"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import sys
import subprocess
from flask import Blueprint, jsonify, current_app

from qalita.internal.utils import logger, validate_token
from qalita.internal.request import send_request
from .helpers import (
    worker_status_payload,
    read_selected_env,
    parse_env_file,
    worker_log_file_path,
    worker_pid_file_path,
    open_path_in_file_explorer,
    compute_worker_summary,
)


bp = Blueprint("workers", __name__)


@bp.get("/worker/status")
def worker_status():
    return jsonify(worker_status_payload())


@bp.post("/worker/start")
def worker_start():
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    worker_name = None

    st = worker_status_payload()
    if st.get("running"):
        return jsonify({"ok": True, "already_running": True, **st})

    try:
        sel_path = read_selected_env()
        if sel_path and os.path.isfile(sel_path):
            logger.info(f"worker_start: applying selected env at [{sel_path}]")
            _login_with_env(sel_path)
    except Exception as exc:
        logger.error(f"worker_start: failed applying selected env: {exc}")
        return (
            jsonify({"ok": False, "error": "Failed to apply selected context"}),
            400,
        )

    try:
        sel_path = read_selected_env()
        if sel_path and os.path.isfile(sel_path):
            data = parse_env_file(sel_path)
            worker_name = (
                data.get("QALITA_WORKER_NAME")
                or data.get("AGENT_NAME")
                or data.get("NAME")
                or None
            )
    except Exception:
        worker_name = None
    if not worker_name:
        try:
            worker_name = getattr(cfg, "name", None) or None
        except Exception:
            worker_name = None
    if not worker_name:
        try:
            raw = cfg.load_worker_config()
            if isinstance(raw, dict) and raw:
                worker_name = (
                    (raw.get("context", {}).get("remote", {}) or {}).get("name")
                    or raw.get("name")
                    or None
                )
        except Exception:
            worker_name = None
    if not worker_name:
        worker_name = "agent"

    # Ensure we have minimum credentials before preflight
    if not getattr(cfg, "token", None) or not getattr(cfg, "url", None):
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "Missing TOKEN or URL. Select a context or login first.",
                }
            ),
            400,
        )
    try:
        validated = validate_token(cfg.token)
        user_id = validated.get("user_id") if isinstance(validated, dict) else None
        if not user_id:
            return (
                jsonify(
                    {
                        "ok": False,
                        "error": "Invalid or missing TOKEN in current context",
                    }
                ),
                400,
            )
        try:
            r = send_request.__wrapped__(cfg, request=f"{cfg.url}/api/v1/version", mode="get")  # type: ignore[attr-defined]
        except Exception:
            r = None
        if r is None or getattr(r, "status_code", None) != 200:
            logger.error("Preflight failed: /api/v1/version not reachable or not 200")
            return (
                jsonify(
                    {
                        "ok": False,
                        "error": "Backend unreachable or /api/v1/version not 200",
                    }
                ),
                400,
            )
        try:
            r2 = send_request.__wrapped__(cfg, request=f"{cfg.url}/api/v2/users/{user_id}", mode="get")  # type: ignore[attr-defined]
        except Exception:
            r2 = None
        if r2 is None or getattr(r2, "status_code", None) != 200:
            logger.error(
                "Preflight failed: /api/v2/users/{user_id} not 200 (invalid token?)"
            )
            return (
                jsonify({"ok": False, "error": "Token invalid or user not accessible"}),
                400,
            )
    except Exception as exc:
        logger.error(f"Preflight login check failed: {exc}")
        return (
            jsonify({"ok": False, "error": "Preflight login check failed"}),
            400,
        )

    try:
        env = dict(os.environ)
        try:
            env["QALITA_HOME"] = cfg.qalita_home  # type: ignore[attr-defined]
        except Exception:
            env["QALITA_HOME"] = os.path.expanduser("~/.qalita")
        logger.info(f"worker_start: QALITA_HOME resolved to [{env.get('QALITA_HOME')}]")
        try:
            sel_path = read_selected_env()
            if sel_path and os.path.isfile(sel_path):
                with open(sel_path, "r", encoding="utf-8") as ef:
                    for line in ef.readlines():
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and v:
                            env[k] = v
        except Exception:
            pass
        try:
            if not any(env.get(k) for k in ("QALITA_WORKER_MODE", "AGENT_MODE", "MODE")):
                env["QALITA_WORKER_MODE"] = "worker"
        except Exception:
            env["QALITA_WORKER_MODE"] = "worker"
        logger.info(
            f"worker_start: effective agent mode is [{env.get('QALITA_WORKER_MODE') or env.get('AGENT_MODE') or env.get('MODE')}]"
        )
        if os.name == "nt":
            python_bin = sys.executable or "python"
            cmd = [
                python_bin,
                "-m",
                "qalita",
                "worker",
                "-n",
                str(worker_name),
                "-m",
                "worker",
                "run",
            ]
            logger.info(f"worker_start: using python interpreter [{python_bin}]")
        else:
            cmd = ["qalita", "worker", "-n", str(worker_name), "-m", "worker", "run"]
        logger.info(f"worker_start: executing command: {' '.join(cmd)}")
        log_path = worker_log_file_path()
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
        except Exception:
            pass
        logger.info(f"worker_start: logging to [{log_path}]")
        log_file = open(log_path, "a", encoding="utf-8", buffering=1)
        popen_kwargs = {"stdout": log_file, "stderr": log_file, "env": env}
        if os.name == "nt":
            try:
                DETACHED_PROCESS = 0x00000008
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                CREATE_NO_WINDOW = 0x08000000
                popen_kwargs["creationflags"] = (
                    DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
                )
                logger.info(
                    "worker_start: using Windows creation flags DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW"
                )
            except Exception:
                pass
        else:
            popen_kwargs["start_new_session"] = True
            logger.info("worker_start: using POSIX start_new_session=True")
        proc = subprocess.Popen(cmd, **popen_kwargs)
        try:
            with open(worker_pid_file_path(), "w", encoding="utf-8") as f:
                f.write(str(proc.pid))
        except Exception:
            pass
        logger.info(f"worker_start: started process with PID [{proc.pid}]")
        return jsonify({"ok": True, "pid": proc.pid, "login_ok": True})
    except Exception as exc:
        logger.error(f"worker_start: primary launch failed: {exc}")
        try:
            env = dict(os.environ)
            try:
                env["QALITA_HOME"] = cfg.qalita_home  # type: ignore[attr-defined]
            except Exception:
                env["QALITA_HOME"] = os.path.expanduser("~/.qalita")
            logger.info(
                f"worker_start(fallback): QALITA_HOME resolved to [{env.get('QALITA_HOME')}]"
            )
            sel_path = read_selected_env()
            if sel_path and os.path.isfile(sel_path):
                with open(sel_path, "r", encoding="utf-8") as ef:
                    for line in ef.readlines():
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and v:
                            env[k] = v
            try:
                if not any(
                    env.get(k) for k in ("QALITA_WORKER_MODE", "AGENT_MODE", "MODE")
                ):
                    env["QALITA_WORKER_MODE"] = "worker"
            except Exception:
                env["QALITA_WORKER_MODE"] = "worker"
            logger.info(
                f"worker_start(fallback): effective agent mode is [{env.get('QALITA_WORKER_MODE') or env.get('AGENT_MODE') or env.get('MODE')}]"
            )
            python_bin = sys.executable or "python3"
            cmd = [
                python_bin,
                "-m",
                "qalita",
                "worker",
                "-n",
                str(worker_name),
                "-m",
                "worker",
                "run",
            ]
            logger.info(f"worker_start(fallback): executing command: {' '.join(cmd)}")
            log_path = worker_log_file_path()
            try:
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
            except Exception:
                pass
            logger.info(f"worker_start(fallback): logging to [{log_path}]")
            log_file = open(log_path, "a", encoding="utf-8", buffering=1)
            popen_kwargs = {"stdout": log_file, "stderr": log_file, "env": env}
            if os.name == "nt":
                try:
                    DETACHED_PROCESS = 0x00000008
                    CREATE_NEW_PROCESS_GROUP = 0x00000200
                    CREATE_NO_WINDOW = 0x08000000
                    popen_kwargs["creationflags"] = (
                        DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
                    )
                    logger.info(
                        "worker_start(fallback): using Windows creation flags DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW"
                    )
                except Exception:
                    pass
            else:
                popen_kwargs["start_new_session"] = True
                logger.info("worker_start(fallback): using POSIX start_new_session=True")
            proc = subprocess.Popen(cmd, **popen_kwargs)
            with open(worker_pid_file_path(), "w", encoding="utf-8") as f:
                f.write(str(proc.pid))
            logger.info(f"worker_start(fallback): started process with PID [{proc.pid}]")
            return jsonify(
                {"ok": True, "pid": proc.pid, "fallback": True, "login_ok": True}
            )
        except Exception as exc2:
            logger.error(f"worker_start(fallback): launch failed: {exc2}")
            return (
                jsonify({"ok": False, "error": "Worker launch failed", "fallback_error": "Fallback also failed"}),
                500,
            )


@bp.post("/worker/stop")
def worker_stop():
    pid = _read_worker_pid()
    if not pid:
        return jsonify({"ok": True, "already_stopped": True})
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(int(pid)), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            pass
    else:
        try:
            import signal

            os.killpg(int(pid), signal.SIGTERM)
        except Exception:
            try:
                os.kill(int(pid), signal.SIGTERM)
            except Exception:
                pass
    try:
        p = worker_pid_file_path()
        if os.path.exists(p):
            os.remove(p)
    except Exception:
        pass
    return jsonify({"ok": True})


@bp.get("/worker/summary")
def worker_summary():
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    worker_conf, worker_runs = compute_worker_summary(cfg)
    return jsonify({"worker_conf": worker_conf or {}, "worker_runs": worker_runs})


@bp.get("/worker/run/<run_name>")
def open_worker_run(run_name: str):
    import re
    
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    run_root = cfg.get_worker_run_path()
    
    # Validate run_name format to prevent path traversal attempts
    # Expected format: YYYYMMDDHHMMSS_XXXXX (timestamp_randomseed)
    if not run_name or not re.match(r'^[\w\-]+$', run_name):
        return jsonify({
            "ok": False,
            "error": "Invalid run name format",
            "message": "Run name contains invalid characters.",
        }), 400
    
    # Use realpath to resolve symlinks and get canonical paths
    run_root_real = os.path.realpath(os.path.abspath(run_root))
    candidate = os.path.realpath(os.path.abspath(os.path.join(run_root, run_name)))
    
    # Ensure the resolved path is within the run_root directory
    if not candidate.startswith(run_root_real + os.sep) and candidate != run_root_real:
        return jsonify({
            "ok": False,
            "error": "Invalid path",
            "message": "If the path is invalid it means: Your local agent is not the one that ran the analysis you are trying to get files from, or the job failed or was cancelled.",
        }), 400

    if not os.path.isdir(candidate):
        return jsonify({
            "ok": False,
            "error": "Run folder not found",
            "path": candidate,
            "message": "If the run folder does not exist it means: Your local agent is not the one that ran the analysis you are trying to get files from, or the job failed or was cancelled.",
        }), 404

    ok, method_used = open_path_in_file_explorer(candidate)
    status = "Opened" if ok else "Could not open automatically"

    # Build instructions for manual navigation
    instructions = []
    if sys.platform == "darwin":
        instructions.append("macOS: open Finder and Go to Folder…")
    elif sys.platform.startswith("linux"):
        instructions.append(f"Linux: use your file manager or run: xdg-open {candidate}")
    elif sys.platform.startswith("win") or "WSL" in os.environ:
        wsl_distro = os.environ.get('WSL_DISTRO_NAME', '<distro>')
        instructions.append(f"Windows/WSL: use Explorer at \\\\wsl$\\{wsl_distro}\\{candidate}")

    return jsonify({
        "ok": True,
        "status": status,
        "path": candidate,
        "method": method_used,
        "instructions": instructions,
        "message": f"{status} file explorer. If the explorer did not open, you can navigate to this folder manually.",
    })


def _read_worker_pid():
    try:
        with open(worker_pid_file_path(), "r", encoding="utf-8") as f:
            raw = f.read().strip()
            return int(raw) if raw else None
    except Exception:
        return None


def _login_with_env(env_path: str) -> None:
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    data = parse_env_file(env_path)

    def pick(*names: str, default: str | None = None) -> str | None:
        for n in names:
            if n in data and data[n]:
                return data[n]
        return default

    name = (
        pick("QALITA_WORKER_NAME", "AGENT_NAME", "NAME")
        or getattr(cfg, "name", None)
        or "agent"
    )
    mode = (
        pick("QALITA_WORKER_MODE", "AGENT_MODE", "MODE")
        or getattr(cfg, "mode", None)
        or "job"
    )
    token = pick("QALITA_WORKER_TOKEN", "QALITA_TOKEN", "TOKEN") or getattr(
        cfg, "token", None
    )
    url = pick("QALITA_WORKER_ENDPOINT", "QALITA_URL", "URL") or getattr(
        cfg, "url", None
    )

    if not token or not url:
        raise RuntimeError("Missing TOKEN or URL in context .env")

    cfg.name = name
    cfg.mode = mode
    cfg.token = token
    cfg.url = url
