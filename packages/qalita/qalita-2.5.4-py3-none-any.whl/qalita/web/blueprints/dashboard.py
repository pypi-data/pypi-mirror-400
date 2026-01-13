"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

from flask import Blueprint, current_app, request, jsonify

from qalita.internal.request import send_request
from qalita.internal.utils import logger
from .helpers import (
    compute_agent_summary,
    read_selected_env,
    parse_env_file,
)


bp = Blueprint("dashboard", __name__)


@bp.route("/")
def dashboard():
    """Legacy route - redirects to Next.js frontend"""
    # Next.js will handle the frontend
    # This route is kept for backward compatibility but should not be used
    return _get_dashboard_data_json()


@bp.route("/api/dashboard")
def dashboard_api():
    """API endpoint for dashboard data"""
    return _get_dashboard_data_json()


def _get_dashboard_data_json():
    """Get dashboard data as JSON"""
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    agent_conf, agent_runs = compute_agent_summary(cfg)
    # Load local sources regardless of agent configuration
    try:
        cfg.load_source_config()
        sources = list(reversed(cfg.config.get("sources", [])))
    except Exception:
        sources = []

    # Resolve public platform URL
    platform_url = None
    try:
        backend_url = getattr(cfg, "url", None)
        try:
            env_path = read_selected_env()
            if env_path:
                data = parse_env_file(env_path)
                backend_url = (
                    data.get("QALITA_AGENT_ENDPOINT")
                    or data.get("QALITA_URL")
                    or data.get("URL")
                    or backend_url
                )
        except Exception:
            pass
        if backend_url:
            try:
                r = send_request.__wrapped__(
                    cfg, request=f"{backend_url}/api/v1/info", mode="get"
                )  # type: ignore[attr-defined]
            except Exception:
                r = None
            if r is not None and getattr(r, "status_code", None) == 200:
                try:
                    platform_url = (r.json() or {}).get("public_platform_url")
                except Exception:
                    platform_url = None
    except Exception:
        platform_url = None
    if isinstance(platform_url, str):
        platform_url = platform_url.rstrip("/")

    # Pagination for runs
    try:
        page = int((request.args.get("runs_page") or "1").strip() or "1")
    except Exception:
        page = 1
    try:
        per_page = int((request.args.get("runs_per_page") or "10").strip() or "10")
    except Exception:
        per_page = 10
    if page < 1:
        page = 1
    if per_page <= 0:
        per_page = 10
    total_runs = len(agent_runs)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    agent_runs_page = agent_runs[start_idx:end_idx]
    runs_has_prev = start_idx > 0
    runs_has_next = end_idx < total_runs
    runs_start = (start_idx + 1) if total_runs > 0 and start_idx < total_runs else 0
    runs_end = min(end_idx, total_runs) if total_runs > 0 else 0

    return jsonify({
        "agent_conf": agent_conf or {},
        "sources": sources,
        "agent_runs": agent_runs,
        "agent_runs_page": agent_runs_page,
        "runs_total": total_runs,
        "runs_page": page,
        "runs_per_page": per_page,
        "runs_has_prev": runs_has_prev,
        "runs_has_next": runs_has_next,
        "runs_start": runs_start,
        "runs_end": runs_end,
        "platform_url": platform_url,
    })


def dashboard_with_feedback(feedback_msg=None, feedback_level: str = "info"):
    """Legacy function - kept for backward compatibility"""
    return _get_dashboard_data_json()


@bp.post("/validate")
def validate_sources():
    from qalita.commands.source import validate_source as _validate

    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    # Run validation (graceful if agent not configured)
    try:
        try:
            _validate.__wrapped__(cfg)  # type: ignore[attr-defined]
        except Exception:
            _validate(cfg)  # type: ignore[misc]
    except (SystemExit, Exception):
        pass
    # Build feedback from results
    try:
        cfg.load_source_config()
        sources = cfg.config.get("sources", []) or []
        total = len(sources)
        valid_count = sum(
            1 for s in sources if (s.get("validate") or "").lower() == "valid"
        )
        invalid_count = sum(
            1 for s in sources if (s.get("validate") or "").lower() == "invalid"
        )
        msg = (
            f"Validated {total} source(s): {valid_count} valid, {invalid_count} invalid"
        )
        level = "info" if invalid_count == 0 else "error"
    except Exception:
        msg = "Validation completed."
        level = "info"
    return jsonify({"ok": True, "message": msg, "level": level})


@bp.post("/push")
def push_sources():
    from qalita.commands.source import push_programmatic

    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    # For web, we do not want interactive confirms; public approvals off by default
    try:
        ok, message = push_programmatic(cfg, skip_validate=False, approve_public=False)
    except Exception as exc:
        logger.error(f"Push failed: {exc}")
        ok, message = False, "Push failed due to an internal error"
    level = "info" if ok else "error"
    return jsonify({"ok": ok, "message": message, "level": level})


@bp.post("/pack/push")
def push_pack_from_ui():
    from qalita.commands.pack import push_from_directory

    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    pack_dir = request.form.get("pack_dir", "").strip()
    feedback = None
    feedback_level = "info"
    if pack_dir:
        try:
            ok, message = push_from_directory(cfg, pack_dir)
            # Sanitize message to avoid exposing internal details
            if ok:
                feedback = "Pack pushed successfully."
            else:
                # Log the detailed message but return a generic one to the user
                logger.error(f"Pack push failed: {message}")
                feedback = "Pack push failed. Check the logs for details."
            feedback_level = "info" if ok else "error"
        except Exception:
            logger.exception("Unexpected error during pack push")
            feedback = "An unexpected error occurred during pack push."
            feedback_level = "error"
    else:
        feedback = "Please select a pack folder."
        feedback_level = "error"
    # Return JSON response
    return jsonify({"ok": feedback_level == "info", "message": feedback, "level": feedback_level})
