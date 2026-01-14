#!/usr/bin/env python3
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -

import os
import click

from qalita.internal.utils import logger, get_version
from qalita.internal.config import Config


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group(
    context_settings=dict(help_option_names=["-h", "--help"]),
    invoke_without_command=True,
)
@click.option(
    "--ui",
    is_flag=True,
    default=os.environ.get("QALITA_WORKER_UI", False),
    help="Open the local web UI dashboard",
)
@click.option(
    "--port",
    default=os.environ.get("QALITA_WORKER_UI_PORT", 7070),
    show_default=True,
    type=int,
    help="Port for the local web UI",
)
@click.option(
    "--host",
    default=os.environ.get("QALITA_WORKER_UI_HOST", "localhost"),
    show_default=True,
    help="Host interface to bind the local web UI",
)
@click.pass_context
def cli(ctx, ui=False, port=7070, host="localhost"):
    """
    ------------------ QALITA Platform Command Line Interface ------------------\n\r
    Hello and thanks for using QALITA Platform to monitor and ensure the quality of your data. \n\r
    ----------------------------------------------------------------------------\n\r
    Please, Help us improve our service by reporting any bug by filing a bug report, Thanks ! \n\r
    mail : contact@qalita.io \n\r
    ----------------------------------------------------------------------------"""
    if ui:
        try:
            import subprocess
            import sys
            import threading
            import time
            from qalita.web.app import run_dashboard_ui

            # Instantiate a Config to pass into the UI
            cfg = Config()
            cfg.load_source_config(verbose=False)

            # Flask API runs on port + 1 (e.g., 7071 if UI is 7070)
            flask_port = port + 1
            flask_host = host

            # Start Flask API in a separate thread
            def run_flask():
                run_dashboard_ui(cfg, host=flask_host, port=flask_port)

            flask_thread = threading.Thread(target=run_flask, daemon=True)
            flask_thread.start()

            # Wait a bit for Flask to start
            time.sleep(1)

            # Start Next.js frontend
            # Check for embedded frontend first (pip installed package)
            embedded_frontend = os.path.join(os.path.dirname(__file__), "_frontend")
            dev_frontend = os.path.join(os.path.dirname(__file__), "..", "frontend")

            if os.path.isdir(embedded_frontend) and os.path.exists(os.path.join(embedded_frontend, "server.js")):
                # Use embedded standalone frontend (from pip package)
                frontend_dir = embedded_frontend
                use_standalone_server = True
                logger.info("Using embedded frontend from package")
            elif os.path.isdir(dev_frontend):
                # Development mode - use local frontend directory
                frontend_dir = dev_frontend
                use_standalone_server = False
            else:
                logger.error("Frontend not found. If installed via pip, please reinstall the package.")
                logger.error("If developing locally, run 'npm install' and 'npm run build' in the frontend directory first")
                raise SystemExit(1)

            # Check Node.js version (Next.js 16 requires >= 20.9.0)
            # Try to use nvm's node if available, otherwise use system node
            node_cmd = "node"
            nvm_node_path = None

            # Check for nvm in common locations
            nvm_paths = [
                os.path.expanduser("~/.nvm/versions/node"),
                os.path.expanduser("~/.config/nvm/versions/node"),
            ]

            # Try to find Node.js 20+ in nvm directories
            for nvm_base in nvm_paths:
                if os.path.isdir(nvm_base):
                    try:
                        # List directories and find the highest v20+ version
                        versions = []
                        for item in os.listdir(nvm_base):
                            if item.startswith("v20.") or item.startswith("v21.") or item.startswith("v22."):
                                versions.append(item)
                        if versions:
                            # Sort and get the highest version
                            versions.sort(reverse=True)
                            nvm_node_path = os.path.join(nvm_base, versions[0], "bin", "node")
                            if os.path.exists(nvm_node_path):
                                node_cmd = nvm_node_path
                                logger.info(f"Using Node.js from nvm: {nvm_node_path}")
                                break
                    except Exception:
                        pass

            try:
                node_version_result = subprocess.run(
                    [node_cmd, "--version"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                node_version = node_version_result.stdout.strip()
                # Extract major and minor version numbers
                version_parts = node_version.lstrip("v").split(".")
                major_version = int(version_parts[0])
                minor_version = int(version_parts[1]) if len(version_parts) > 1 else 0

                if major_version < 20 or (major_version == 20 and minor_version < 9):
                    logger.error(f"Node.js version {node_version} is installed, but Next.js 16 requires Node.js >= 20.9.0")
                    logger.error("Please upgrade Node.js to version 20.9.0 or higher")
                    if not nvm_node_path:
                        logger.error("If you're using nvm, make sure to run: nvm use 20")
                    logger.error("You can install Node.js from https://nodejs.org/ or use nvm: nvm install 20")
                    raise SystemExit(1)
                logger.info(f"Node.js version: {node_version}")

            except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
                logger.error("Node.js is not installed or not found in PATH")
                logger.error("Please install Node.js >= 20.9.0 from https://nodejs.org/")
                logger.error("Or use nvm: nvm install 20 && nvm use 20")
                raise SystemExit(1)

            # Set environment variable for Flask API URL and configure PATH for Node.js
            env = os.environ.copy()
            env["FLASK_API_URL"] = f"http://{flask_host}:{flask_port}"
            env["PORT"] = str(port)
            env["HOSTNAME"] = host

            # Determine which node/npm to use and ensure they're in PATH
            import platform
            if nvm_node_path:
                node_bin = nvm_node_path
                node_bin_dir = os.path.dirname(nvm_node_path)
                npm_cmd = os.path.join(node_bin_dir, "npm")
                if not os.path.exists(npm_cmd):
                    npm_cmd = "npm"  # Fallback
                # Ensure nvm's bin directory is FIRST in PATH so npm uses the right node
                current_path = env.get("PATH", "")
                path_parts = current_path.split(":") if current_path else []
                # Remove node_bin_dir if it's already there
                path_parts = [p for p in path_parts if p != node_bin_dir]
                # Put nvm's bin directory first
                env["PATH"] = f"{node_bin_dir}:{':'.join(path_parts)}"
            else:
                node_bin = "node.exe" if platform.system() == "Windows" else "node"
                npm_cmd = "npm"

            # For development mode, check if node_modules exists
            if not use_standalone_server:
                node_modules_path = os.path.join(frontend_dir, "node_modules")
                if not os.path.exists(node_modules_path):
                    logger.info("Installing Next.js dependencies...")
                    install_result = subprocess.run(
                        [npm_cmd, "install"],
                        cwd=frontend_dir,
                        capture_output=True,
                        env=env,
                    )
                    if install_result.returncode != 0:
                        logger.error("Failed to install Next.js dependencies")
                        logger.error(install_result.stderr.decode() if install_result.stderr else "Unknown error")
                        raise SystemExit(1)

            logger.info(f"Starting Flask API on http://{flask_host}:{flask_port}")
            logger.info(f"Starting Next.js frontend on http://{host}:{port}")
            logger.info(f"QALITA CLI UI is running. Open http://{host}:{port}")

            # Check if using embedded standalone server (from pip package)
            if use_standalone_server:
                # Use embedded standalone server directly with node
                logger.info("Running Next.js standalone server (embedded)...")
                server_js = os.path.join(frontend_dir, "server.js")
                subprocess.run(
                    [node_bin, server_js],
                    cwd=frontend_dir,
                    env=env,
                )
            # Check for production build (standalone mode) in development frontend
            elif os.path.exists(os.path.join(frontend_dir, ".next", "standalone")):
                # Use next start from frontend directory instead of standalone
                # This ensures static files are served correctly
                logger.info("Running Next.js in production mode (standalone build detected)...")
                next_bin = os.path.join(frontend_dir, "node_modules", ".bin", "next")
                if os.path.exists(next_bin):
                    subprocess.run(
                        [node_bin, next_bin, "start", "-p", str(port), "-H", host],
                        cwd=frontend_dir,
                        env=env,
                    )
                else:
                    subprocess.run(
                        [npm_cmd, "start"],
                        cwd=frontend_dir,
                        env=env,
                    )
            elif os.path.exists(os.path.join(frontend_dir, ".next", "server")):
                # Production build exists but not standalone, use next start directly with args
                logger.info("Running Next.js in production mode...")
                next_bin = os.path.join(frontend_dir, "node_modules", ".bin", "next")
                if not os.path.exists(next_bin):
                    # Fallback to npm start
                    subprocess.run(
                        [npm_cmd, "start"],
                        cwd=frontend_dir,
                        env=env,
                    )
                else:
                    subprocess.run(
                        [node_bin, next_bin, "start", "-p", str(port), "-H", host],
                        cwd=frontend_dir,
                        env=env,
                    )
            else:
                # Development mode - use next directly with node from nvm
                logger.info("Running Next.js in development mode...")
                next_cli = os.path.join(frontend_dir, "node_modules", "next", "dist", "bin", "next")
                next_bin = os.path.join(frontend_dir, "node_modules", ".bin", "next")

                # Try to use the actual Next.js CLI file directly (no shebang issues)
                if os.path.exists(next_cli):
                    logger.info(f"Using Node.js: {node_bin} to run Next.js")
                    subprocess.run(
                        [node_bin, next_cli, "dev", "-p", str(port), "-H", host],
                        cwd=frontend_dir,
                        env=env,
                    )
                elif os.path.exists(next_bin):
                    # Use node to execute next script (node ignores shebang when called directly)
                    logger.info(f"Using Node.js: {node_bin} to run Next.js")
                    subprocess.run(
                        [node_bin, next_bin, "dev", "-p", str(port), "-H", host],
                        cwd=frontend_dir,
                        env=env,
                    )
                else:
                    # Fallback: use npm but ensure PATH is set correctly
                    logger.warning("next binary not found, trying npm with PATH override...")
                    # Verify node version in env before running
                    verify_result = subprocess.run(
                        [node_bin, "--version"],
                        capture_output=True,
                        text=True,
                        env=env,
                    )
                    if verify_result.returncode == 0:
                        logger.info(f"Node.js version in env: {verify_result.stdout.strip()}")
                    subprocess.run(
                        [npm_cmd, "run", "dev", "--", "-p", str(port), "-H", host],
                        cwd=frontend_dir,
                        env=env,
                    )
        except Exception as exc:
            logger.error(f"Unable to start web UI: {exc}")
            import traceback
            traceback.print_exc()
        raise SystemExit(0)
    # If invoked without a subcommand and without --ui, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        raise SystemExit(0)


@cli.command(context_settings=dict(help_option_names=["-h", "--help"]))
def version():
    """
    Display the version of the cli
    """
    print("--- QALITA CLI Version ---")
    print(f"Version : {get_version()}")


def add_commands_to_cli():
    from qalita.commands import worker, source, pack

    # Add pack command group to cli
    cli.add_command(pack.pack)
    cli.add_command(worker.worker)
    cli.add_command(source.source)


def main():
    add_commands_to_cli()
    cli()


if __name__ == "__main__":
    main()
