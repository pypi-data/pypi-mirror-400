"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import re
import sys
import shutil
import subprocess
import threading
from datetime import datetime
from flask import current_app

from qalita.internal.utils import logger

# Lock for .current_env file operations
_current_env_lock = threading.Lock()


def write_selected_env_atomic(pointer_path: str, env_path: str) -> bool:
    """Atomically write the selected env pointer file. Uses locking to prevent race conditions.

    Args:
        pointer_path: Path to the .current_env pointer file
        env_path: Path to the env file to write in the pointer

    Returns:
        True if successful, False otherwise
    """
    with _current_env_lock:
        try:
            # Use atomic write: write to temp file then rename
            temp_path = pointer_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as pf:
                pf.write(env_path)
            os.replace(temp_path, pointer_path)
            return True
        except Exception as exc:
            logger.warning(f"Failed to write selected env pointer: {exc}")
            return False


def qalita_home() -> str:
    try:
        cfg = current_app.config.get("QALITA_CONFIG_OBJ")
        return os.path.normpath(cfg.qalita_home)  # type: ignore[attr-defined]
    except Exception:
        return os.path.normpath(os.path.expanduser("~/.qalita"))


def selected_env_file_path() -> str:
    return os.path.normpath(os.path.join(qalita_home(), ".current_env"))


def parse_env_file(env_path: str) -> dict:
    vars: dict[str, str] = {}
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for raw in f.readlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip().lstrip("\ufeff")
                v = v.strip().strip('"').strip("'")
                vars[k] = v
    except Exception:
        logger.error(f"Failed reading env file: [{env_path}]")
        pass
    return vars


def materialize_env_from_process_env(target_path: str) -> None:
    """Update specific keys in an env file from process environment variables.

    This function preserves ALL existing keys in the file and only updates
    specific keys (NAME, MODE, TOKEN, URL) from the process environment.
    It should only be called when creating a NEW file, not on existing files
    that may contain important configuration.
    """
    try:
        existing: dict[str, str] = {}
        if os.path.isfile(target_path):
            existing = parse_env_file(target_path) or {}
        env = os.environ
        key_groups = [
            ("QALITA_WORKER_NAME", ["QALITA_WORKER_NAME", "QALITA_AGENT_NAME", "AGENT_NAME", "NAME"]),
            ("QALITA_WORKER_MODE", ["QALITA_WORKER_MODE", "QALITA_AGENT_MODE", "AGENT_MODE", "MODE"]),
            ("QALITA_WORKER_TOKEN", ["QALITA_WORKER_TOKEN", "QALITA_AGENT_TOKEN", "QALITA_TOKEN", "TOKEN"]),
            (
                "QALITA_WORKER_ENDPOINT",
                ["QALITA_WORKER_ENDPOINT", "QALITA_AGENT_ENDPOINT", "AGENT_ENDPOINT", "QALITA_URL", "URL"],
            ),
        ]
        # Start with existing keys to preserve everything
        merged = dict(existing)

        # Only update specific keys from environment if they exist
        # Map environment variable names to their canonical key names (use WORKER as canonical)
        canonical_keys = {
            "QALITA_WORKER_NAME": "QALITA_WORKER_NAME",
            "QALITA_AGENT_NAME": "QALITA_WORKER_NAME",
            "AGENT_NAME": "QALITA_WORKER_NAME",
            "NAME": "QALITA_WORKER_NAME",
            "QALITA_WORKER_MODE": "QALITA_WORKER_MODE",
            "QALITA_AGENT_MODE": "QALITA_WORKER_MODE",
            "AGENT_MODE": "QALITA_WORKER_MODE",
            "MODE": "QALITA_WORKER_MODE",
            "QALITA_WORKER_TOKEN": "QALITA_WORKER_TOKEN",
            "QALITA_AGENT_TOKEN": "QALITA_WORKER_TOKEN",
            "QALITA_TOKEN": "QALITA_WORKER_TOKEN",
            "TOKEN": "QALITA_WORKER_TOKEN",
            "QALITA_WORKER_ENDPOINT": "QALITA_WORKER_ENDPOINT",
            "QALITA_AGENT_ENDPOINT": "QALITA_WORKER_ENDPOINT",
            "AGENT_ENDPOINT": "QALITA_WORKER_ENDPOINT",
            "QALITA_URL": "QALITA_WORKER_ENDPOINT",
            "URL": "QALITA_WORKER_ENDPOINT",
        }

        # Update only the canonical keys from environment
        for env_key, canonical_key in canonical_keys.items():
            if env_key in env and env.get(env_key):
                merged[canonical_key] = env.get(env_key)

        # Write all keys (existing + updated)
        lines = []
        for k in sorted(merged.keys()):
            v = merged[k]
            if v is None:
                continue
            if any(ch.isspace() for ch in str(v)):
                escaped = str(v).replace('"', '\\"')
                lines.append(f'{k}="{escaped}"')
            else:
                lines.append(f"{k}={v}")
        content = "\n".join(lines) + ("\n" if lines else "")
        os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as wf:
            wf.write(content)
    except Exception:
        pass


def ensure_default_env_selected(pointer_path: str):
    """Ensure a default env is selected. Uses locking to prevent race conditions."""
    # Double-check: if file was created by another thread, use it
    try:
        if os.path.isfile(pointer_path):
            with open(pointer_path, "r", encoding="utf-8") as f:
                existing_path = f.read().strip()
                if existing_path and os.path.isfile(existing_path):
                    return existing_path
    except Exception:
        pass

    try:
        base = qalita_home()
        env = os.environ
        cfg = current_app.config.get("QALITA_CONFIG_OBJ")
        name = env.get("QALITA_AGENT_NAME") or env.get("AGENT_NAME") or env.get("NAME")
        if not name:
            try:
                name = getattr(cfg, "name", None)
            except Exception:
                name = None
        if not name:
            name = "agent"
        safe = re.sub(r"[^A-Za-z0-9._-]+", "-", str(name)).strip("-_.") or "agent"
        target = os.path.normpath(os.path.join(base, f".env-{safe}"))
        os.makedirs(base, exist_ok=True)
        materialize_env_from_process_env(target)
        # Use atomic write function (which handles locking)
        write_selected_env_atomic(pointer_path, target)
        return target
    except Exception:
        return None


def read_selected_env():
    """Read the selected env file path. Uses locking to prevent race conditions when creating default.

    NOTE: Does NOT call materialize_env_from_process_env() to avoid overwriting existing .env files.
    The materialization should only happen when explicitly creating a new file, not on every read.
    """
    p = selected_env_file_path()
    try:
        # Try to read the file first (read-only, no lock needed)
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                path = os.path.normpath(raw) if raw else None
                if path and os.path.isfile(path):
                    # DO NOT call materialize_env_from_process_env() here - it would overwrite the file!
                    # Only return the path without modifying the file
                    return path
                # Path exists but file doesn't - try to find it
                try:
                    base = qalita_home()
                    if path:
                        candidate = os.path.normpath(
                            os.path.join(base, os.path.basename(path))
                        )
                        if os.path.isfile(candidate):
                            logger.warning(
                                f"Selected env pointer [{path}] not found. Using [{candidate}] under current QALITA_HOME."
                            )
                            # DO NOT call materialize_env_from_process_env() - preserve existing file content
                            # Use atomic write function (which handles locking)
                            # Double-check: if file was updated by another thread, use it
                            try:
                                if os.path.isfile(p):
                                    with open(p, "r", encoding="utf-8") as f2:
                                        existing = f2.read().strip()
                                        if existing and os.path.isfile(existing):
                                            return existing
                            except Exception:
                                pass
                            write_selected_env_atomic(p, candidate)
                            return candidate
                        try:
                            os.makedirs(base, exist_ok=True)
                            # Only call materialize_env_from_process_env when creating a NEW file
                            # This is safe because the file doesn't exist yet
                            materialize_env_from_process_env(candidate)
                            logger.warning(
                                f"Selected env pointer [{path}] not found. Created [{candidate}] under current QALITA_HOME from environment."
                            )
                            # Use atomic write function (which handles locking)
                            # Double-check: if file was updated by another thread, use it
                            try:
                                if os.path.isfile(p):
                                    with open(p, "r", encoding="utf-8") as f2:
                                        existing = f2.read().strip()
                                        if existing and os.path.isfile(existing):
                                            return existing
                            except Exception:
                                pass
                            write_selected_env_atomic(p, candidate)
                            return candidate
                        except Exception:
                            pass
                except Exception:
                    pass
        # File doesn't exist or is invalid - create default (with lock)
        return ensure_default_env_selected(p)
    except Exception:
        logger.warning(f"No selected env pointer found at [{p}] or failed to read it")
        return ensure_default_env_selected(p)


def list_env_files():
    root = qalita_home()
    files = []
    try:
        for name in os.listdir(root):
            lower = name.lower()
            if lower.startswith(".env") or lower.endswith(".env"):
                files.append(
                    {"name": name, "path": os.path.normpath(os.path.join(root, name))}
                )
    except Exception:
        files = []
    files.sort(key=lambda x: x["name"])  # stable order
    return files


def agent_pid_file_path():
    return os.path.join(qalita_home(), "agent_run.pid")


def read_agent_pid():
    p = agent_pid_file_path()
    try:
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                return int(raw) if raw else None
    except Exception:
        return None
    return None


def agent_log_file_path():
    return os.path.join(qalita_home(), "agent_run.log")


def is_pid_running(pid: int) -> bool:
    try:
        if os.name == "nt":
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {int(pid)}"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    return False
                return str(int(pid)) in result.stdout
            except Exception:
                return False
        else:
            os.kill(int(pid), 0)
            return True
    except Exception:
        return False


def agent_status_payload() -> dict:
    pid = read_agent_pid()
    running = bool(pid) and is_pid_running(int(pid))
    return {"running": running, "pid": int(pid) if running else None}


def open_path_in_file_explorer(target_path: str) -> tuple[bool, str]:
    try:
        target_path = os.path.normpath(target_path)
        if sys.platform == "darwin":
            if shutil.which("open"):
                subprocess.Popen(["open", target_path])
                return True, "open"
        if os.name == "nt":
            if shutil.which("explorer"):
                subprocess.Popen(["explorer", target_path])
                return True, "explorer"
        if os.environ.get("WSL_DISTRO_NAME"):
            try:
                if shutil.which("wslpath") and shutil.which("explorer.exe"):
                    win_path = subprocess.check_output(
                        ["wslpath", "-w", target_path], text=True
                    ).strip()
                    subprocess.Popen(["explorer.exe", win_path])
                    return True, "explorer.exe(wslpath)"
            except Exception:
                pass
            if shutil.which("wslview"):
                subprocess.Popen(["wslview", target_path])
                return True, "wslview"
        if shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", target_path])
            return True, "xdg-open"
        if shutil.which("open"):
            subprocess.Popen(["open", target_path])
            return True, "open"
    except Exception as exc:
        logger.warning(f"Failed opening explorer for [{target_path}]: {exc}")
        return False, "error"
    return False, "none"


def compute_agent_summary(cfg):
    agent_conf = None
    try:
        raw = cfg.load_agent_config()
        if isinstance(raw, dict) and raw:

            def pick(obj, *path):
                cur = obj
                for key in path:
                    if not isinstance(cur, dict) or key not in cur:
                        return ""
                    cur = cur[key]
                return cur

            agent_conf = {
                "name": pick(raw, "context", "remote", "name") or raw.get("name", ""),
                "mode": pick(raw, "context", "local", "mode") or raw.get("mode", ""),
                "url": pick(raw, "context", "local", "url") or raw.get("url", ""),
                "agent_id": pick(raw, "context", "remote", "id")
                or raw.get("agent_id", ""),
            }
        else:
            agent_conf = None
    except SystemExit:
        # Gracefully handle missing/invalid .agent in web requests
        agent_conf = None
    except Exception:
        agent_conf = None
    # Overlay with selected context values
    try:
        env_path = read_selected_env()
        if env_path:
            data = parse_env_file(env_path)
            if agent_conf is None:
                agent_conf = {}
            agent_conf["name"] = (
                data.get("QALITA_WORKER_NAME")
                or data.get("QALITA_AGENT_NAME")
                or data.get("AGENT_NAME")
                or data.get("NAME")
                or agent_conf.get("name", "")
            )
            agent_conf["mode"] = (
                data.get("QALITA_WORKER_MODE")
                or data.get("QALITA_AGENT_MODE")
                or data.get("AGENT_MODE")
                or data.get("MODE")
                or agent_conf.get("mode", "")
            )
            agent_conf["url"] = (
                data.get("QALITA_WORKER_ENDPOINT")
                or data.get("QALITA_AGENT_ENDPOINT")
                or data.get("QALITA_URL")
                or data.get("URL")
                or agent_conf.get("url", "")
            )
    except Exception:
        pass
    # Final overlay from live cfg values
    try:
        if agent_conf is None:
            agent_conf = {}
        if not agent_conf.get("name"):
            agent_conf["name"] = getattr(cfg, "name", "") or agent_conf.get("name", "")
        if not agent_conf.get("mode"):
            agent_conf["mode"] = getattr(cfg, "mode", "") or agent_conf.get("mode", "")
        if not agent_conf.get("url"):
            agent_conf["url"] = getattr(cfg, "url", "") or agent_conf.get("url", "")
    except Exception:
        pass
    # Build agent runs
    agent_runs = []
    try:
        run_root = cfg.get_agent_run_path()
        if os.path.isdir(run_root):
            pattern = re.compile(r"^\d{14}_[a-z0-9]{5}$")
            for entry in sorted(os.listdir(run_root), reverse=True):
                if pattern.match(entry) and os.path.isdir(
                    os.path.join(run_root, entry)
                ):
                    ts = entry.split("_")[0]
                    try:
                        when = datetime.strptime(ts, "%Y%m%d%H%M%S").strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    except Exception:
                        when = ts
                    agent_runs.append(
                        {
                            "name": entry,
                            "path": os.path.join(run_root, entry),
                            "timestamp": ts,
                            "when": when,
                        }
                    )
    except Exception:
        agent_runs = []
    return agent_conf, agent_runs


# Aliases for backward compatibility (agent -> worker refactoring)
worker_pid_file_path = agent_pid_file_path
worker_log_file_path = agent_log_file_path
worker_status_payload = agent_status_payload
compute_worker_summary = compute_agent_summary
