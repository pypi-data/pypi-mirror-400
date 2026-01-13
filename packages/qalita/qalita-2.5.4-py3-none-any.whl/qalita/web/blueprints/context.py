"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

from flask import Blueprint, jsonify, current_app, request
import requests
import os

from .helpers import (
    list_env_files,
    read_selected_env,
    selected_env_file_path,
    qalita_home,
    parse_env_file,
    write_selected_env_atomic,
)
from qalita.internal.utils import logger
from qalita.internal.request import send_request
from qalita.internal.utils import get_version
from qalita.commands.worker import authenticate, send_alive


bp = Blueprint("context", __name__)


@bp.get("/contexts")
def list_contexts():
    files = list_env_files()
    selected = read_selected_env()
    try:
        if selected:
            sel_norm = os.path.normcase(os.path.normpath(selected))
            for it in files:
                if os.path.normcase(os.path.normpath(it.get("path", ""))) == sel_norm:
                    selected = it.get("path")
                    break
    except Exception:
        pass
    return jsonify({"items": files, "selected": selected})


@bp.post("/context/select")
def select_context():
    data = request.get_json(silent=True) or {}
    path = (data.get("path") or "").strip()

    ok = False
    message = ""
    if not path:
        try:
            p = selected_env_file_path()
            # Use lock when removing to avoid race conditions
            from .helpers import _current_env_lock
            with _current_env_lock:
                if os.path.exists(p):
                    os.remove(p)
            ok = True
            message = "Selection cleared"
        except Exception as exc:
            logger.error(f"Failed to clear selection: {exc}")
            ok = False
            message = "Failed to clear selection"
    else:
        try:
            root = qalita_home()
            abs_root = os.path.abspath(root)
            abs_path = os.path.abspath(path)
            if not abs_path.startswith(abs_root + os.sep):
                logger.warning("Invalid context path outside qalita home")
                return jsonify({"ok": False, "message": "Invalid path"}), 400
            if not os.path.isfile(abs_path):
                logger.warning("Context env file not found on disk")
                return jsonify({"ok": False, "message": "Env file not found"}), 404

            # Use atomic write with locking
            p = selected_env_file_path()
            if not write_selected_env_atomic(p, abs_path):
                return jsonify({"ok": False, "message": "Failed to write context selection"}), 500

            # Apply selected context: login and persist
            try:
                _login_with_env(abs_path)
                ok = True
                message = "Context selected and agent logged in"
            except Exception as exc:
                logger.error(f"Context select: login failed: {exc}")
                ok = False
                message = "Selected, but login failed"
        except Exception as exc:
            logger.error(f"Failed to select context: {exc}")
            ok = False
            message = "Failed to select context"

    try:
        cfg = current_app.config["QALITA_CONFIG_OBJ"]
        from .helpers import compute_agent_summary

        agent_conf, agent_runs = compute_agent_summary(cfg)
    except Exception:
        agent_conf, agent_runs = None, []
    return jsonify(
        {
            "ok": ok,
            "message": message,
            "agent_conf": agent_conf or {},
            "agent_runs": agent_runs,
        }
    )


def _login_with_env(env_path: str) -> None:
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    data = parse_env_file(env_path)

    def pick(*names: str, default: str | None = None) -> str | None:
        for n in names:
            if n in data and data[n]:
                return data[n]
        return default

    name = (
        pick("QALITA_AGENT_NAME", "AGENT_NAME", "NAME")
        or getattr(cfg, "name", None)
        or "agent"
    )
    mode = (
        pick("QALITA_AGENT_MODE", "AGENT_MODE", "MODE")
        or getattr(cfg, "mode", None)
        or "job"
    )
    token = pick("QALITA_AGENT_TOKEN", "QALITA_TOKEN", "TOKEN") or getattr(
        cfg, "token", None
    )
    url = pick("QALITA_AGENT_ENDPOINT", "QALITA_URL", "URL") or getattr(
        cfg, "url", None
    )

    if not token or not url:
        raise RuntimeError("Missing TOKEN or URL in context .env")

    cfg.name = name
    cfg.mode = mode
    cfg.token = token
    cfg.url = url

    try:
        r = send_request.__wrapped__(cfg, request=f"{cfg.url}/api/v1/version", mode="get")  # type: ignore[attr-defined]
        if r.status_code == 200:
            v = r.json().get("version")
            if v and v != get_version():
                pass
    except Exception:
        pass
