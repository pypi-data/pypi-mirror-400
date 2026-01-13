"""Start command."""

from __future__ import annotations

import collections
import logging
import multiprocessing
import os
import re
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import FrameType

import typer
import uvicorn

from . import console

app = typer.Typer()

# Global reference to frontend process for cleanup
_frontend_process: subprocess.Popen[bytes] | None = None
_worker_processes: list[multiprocessing.Process] = []

_VITE_URL_RE = re.compile(r"http://(?:localhost|127\.0\.0\.1|\[::1\]):(?P<port>\d+)/?")


def _start_worker_process(worker_id: str, quiet: bool = False) -> None:
    """Entry point for worker subprocesses.

    Must be a top-level function so it is pickleable under the `spawn`
    multiprocessing start method (macOS default).
    """
    from ..engine.worker import run_worker

    run_worker(worker_id=worker_id, quiet_startup=quiet)


def _start_frontend_dev_server(
    *,
    web_dir: Path,
    frontend_host: str,
    preferred_port: int,
    api_url: str,
    project: str,
    verbose: bool,
) -> tuple[subprocess.Popen[bytes], str]:
    """Start Vite dev server and return (process, frontend_url).

    Even in non-verbose mode, we capture Vite output so that if it fails to start we can
    show the last lines of output rather than silently printing a dead URL.
    """
    env = os.environ.copy()
    env["PORT"] = str(preferred_port)
    env["VITE_API_URL"] = api_url
    env["VIBELAB_PROJECT"] = project

    # Let Vite auto-bump the port if needed; we'll parse the actual port from its output.
    cmd = [
        "bun",
        "run",
        "dev",
        "--",
        "--host",
        frontend_host,
        "--port",
        str(preferred_port),
    ]

    proc = subprocess.Popen(
        cmd,
        cwd=web_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )

    # Drain output in a background thread to avoid deadlocks if the buffer fills.
    buf: collections.deque[str] = collections.deque(maxlen=200)
    ready = threading.Event()
    discovered_url: list[str] = []

    def _reader() -> None:
        stdout = proc.stdout
        if stdout is None:
            return
        for raw in iter(stdout.readline, b""):
            line = raw.decode(errors="replace").rstrip("\n")
            buf.append(line)
            if verbose and line.strip():
                # Format Vite output consistently with our logs
                time_str = time.strftime("%H:%M:%S")
                if console._colors_enabled():
                    prefix = f"{console.DIM}{time_str}{console.RESET}"
                    level = f"{console.MAGENTA}V{console.RESET}"
                    module = f"{console.DIM}vite{console.RESET}"
                    sys.stderr.write(f"  {prefix} {level} {module}: {line}\n")
                else:
                    sys.stderr.write(f"  {time_str} V vite: {line}\n")
                sys.stderr.flush()
            if not ready.is_set():
                m = _VITE_URL_RE.search(line)
                if m:
                    port = int(m.group("port"))
                    discovered_url.append(f"http://{frontend_host}:{port}/")
                    ready.set()

    threading.Thread(target=_reader, daemon=True).start()

    # Wait briefly for Vite to either print a URL or exit.
    deadline = time.time() + 6.0
    while time.time() < deadline:
        if ready.is_set() and discovered_url:
            return proc, discovered_url[0]
        if proc.poll() is not None:
            break
        time.sleep(0.05)

    if proc.poll() is not None:
        if not verbose:
            typer.echo("Frontend failed to start. Last output:", err=True)
            for line in list(buf)[-30:]:
                typer.echo(f"[vite] {line}", err=True)
        raise RuntimeError(f"frontend dev server exited (exit={proc.returncode})")

    # Still running but we didn't see a URL yet (unexpected). Assume preferred port.
    return proc, f"http://{frontend_host}:{preferred_port}/"


class _ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and cleaner output."""

    LEVEL_COLORS = {
        logging.DEBUG: console.DIM,
        logging.INFO: console.CYAN,
        logging.WARNING: console.BRIGHT_YELLOW,
        logging.ERROR: console.BRIGHT_RED,
        logging.CRITICAL: console.BRIGHT_RED + console.BOLD,
    }

    def format(self, record: logging.LogRecord) -> str:
        # Simplify the logger name
        name = record.name
        if name.startswith("vibelab."):
            name = name[8:]  # Remove "vibelab." prefix

        # Format timestamp
        time_str = time.strftime("%H:%M:%S", time.localtime(record.created))

        # Get level color
        level_color = self.LEVEL_COLORS.get(record.levelno, "")
        level_name = record.levelname[0]  # Just first letter: I, W, E, D

        # Build the message
        if console._colors_enabled():
            prefix = f"{console.DIM}{time_str}{console.RESET}"
            level = f"{level_color}{level_name}{console.RESET}"
            module = f"{console.DIM}{name}{console.RESET}"
            return f"  {prefix} {level} {module}: {record.getMessage()}"
        else:
            return f"  {time_str} {level_name} {name}: {record.getMessage()}"


def _configure_logging(*, verbose: bool) -> None:
    """
    Configure user-friendly logging for `vibelab start`.

    - Normal mode: INFO-level, no per-request access logs from uvicorn.
    - Verbose mode: DEBUG-level, include access logs (uvicorn controls this).
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Remove any existing handlers from root
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Add our custom handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(_ColoredFormatter())
    root.addHandler(handler)
    root.setLevel(level)

    # Configure uvicorn loggers to use our formatter
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(logger_name)
        uv_logger.handlers = []
        uv_logger.propagate = True  # Let root handle it

    # Suppress noisy third-party loggers even in verbose mode
    noisy_loggers = [
        "httpcore",
        "httpcore.connection",
        "httpcore.http11",
        "httpx",
        "hpack",
        "asyncio",
    ]
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # LiteLLM is very chatty - only show INFO and above, not DEBUG
    logging.getLogger("LiteLLM").setLevel(logging.INFO if verbose else logging.WARNING)

    os.environ["VIBELAB_LOG_LEVEL"] = "DEBUG" if verbose else "INFO"
    # Also set LITELLM_LOG to suppress their custom debug output
    if not verbose:
        os.environ["LITELLM_LOG"] = "WARNING"


def _get_uvicorn_log_config(*, verbose: bool) -> dict:
    """Get uvicorn log config that propagates to root (where we control formatting)."""
    # We want uvicorn to:
    # 1. Not print its own startup banner (we print our own)
    # 2. Propagate to root so our formatter handles it
    level = "INFO" if verbose else "WARNING"
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {},  # No handlers - let propagation handle it
        "loggers": {
            "uvicorn": {
                "handlers": [],
                "level": level,
                "propagate": True,
            },
            "uvicorn.error": {
                "handlers": [],
                "level": level,
                "propagate": True,
            },
            "uvicorn.access": {
                "handlers": [],
                "level": level,
                "propagate": True,
            },
        },
    }


def _cleanup_processes():
    """Clean up frontend + worker processes on exit."""
    global _frontend_process, _worker_processes

    for proc in _worker_processes:
        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=5)
            if proc.is_alive():
                proc.kill()
    _worker_processes = []
    if _frontend_process:
        try:
            _frontend_process.terminate()
            _frontend_process.wait(timeout=5)
        except Exception:
            _frontend_process.kill()
        _frontend_process = None


@app.command()
def start_cmd(
    port: int = typer.Option(8000, "--port", help="Port to listen on"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to"),
    frontend_port: int = typer.Option(5173, "--frontend-port", help="Frontend dev server port"),
    dev: bool = typer.Option(
        False, "--dev/--no-dev", help="Start in development mode (with frontend dev server)"
    ),
    project: str = typer.Option(
        "default",
        "--project",
        help="Project name (separate DB and files under VIBELAB_HOME/projects/<project>/)",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", help="Verbose logging (API access logs + frontend logs)"
    ),
    workers: int = typer.Option(1, "--workers", help="Number of worker processes"),
) -> None:
    """Start the web server and frontend."""
    _configure_logging(verbose=verbose)

    # Print banner and warning
    console.print_banner(small=True)
    console.print_alpha_warning()

    # Must be set before importing the FastAPI app module (uvicorn will import it).
    os.environ["VIBELAB_PROJECT"] = project

    from ..db.connection import init_db

    init_db()

    # Start worker(s) (durable queue consumers)
    # In verbose mode, workers should log their activity
    global _worker_processes
    _worker_processes = []
    for i in range(max(1, workers)):
        worker_id = f"worker-{i + 1}"
        proc = multiprocessing.Process(
            target=_start_worker_process,
            args=(worker_id,),
            kwargs={"quiet": not verbose},  # Log in verbose mode
            name=worker_id,
        )
        proc.start()
        _worker_processes.append(proc)

    # Frontend paths:
    # - Production/static: prefer the installed package path (`vibelab/web/dist`) if present.
    # - Dev (Vite): must use a directory that contains `package.json` (source checkout `./web`).
    package_dir = Path(__file__).parent.parent  # .../src/vibelab
    repo_root = Path(__file__).resolve().parents[3]

    package_web_dir = package_dir / "web"
    package_dist_dir = package_web_dir / "dist"
    source_web_dir = repo_root / "web"
    source_dist_dir = source_web_dir / "dist"

    # Default to package dist if present, else source dist.
    web_dir = package_web_dir if package_dist_dir.exists() else source_web_dir
    dist_dir = package_dist_dir if package_dist_dir.exists() else source_dist_dir

    if dev:
        # Dev mode requires the source `web/` directory (or any directory with a package.json).
        dev_web_dir = (
            source_web_dir if (source_web_dir / "package.json").exists() else package_web_dir
        )
        if not (dev_web_dir / "package.json").exists():
            console.echo(console.error("  ✗ Failed to start frontend in --dev mode"))
            console.echo(console.muted("    Could not find package.json for the Vite app."))
            console.echo(console.muted(f"    Looked in: {source_web_dir}"))
            console.echo(console.muted(f"    Looked in: {package_web_dir}"))
            console.echo()
            console.echo(console.info("  Tip: run from a source checkout, or start without --dev"))
            raise typer.Exit(code=1)

        # Use 127.0.0.1 explicitly to avoid any localhost IPv6/IPv4 surprises.
        frontend_host = "127.0.0.1"

        # Set up signal handlers for cleanup
        def signal_handler(sig: int, frame: FrameType | None) -> None:
            console.print_shutdown()
            _cleanup_processes()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start frontend dev server
        frontend_url: str | None = None
        global _frontend_process
        try:
            _frontend_process, frontend_url = _start_frontend_dev_server(
                web_dir=dev_web_dir,
                frontend_host=frontend_host,
                preferred_port=frontend_port,
                api_url=f"http://{host}:{port}",
                project=project,
                verbose=verbose,
            )
        except Exception as e:
            console.echo(console.warning(f"  ⚠ Frontend failed: {e}"))
            console.echo(console.muted("    Continuing with backend only..."))
            console.echo()

        # Print startup info
        console.print_startup_info(
            mode="development",
            api_url=f"http://{host}:{port}",
            frontend_url=frontend_url,
            workers=workers,
            project=project,
            verbose=verbose,
        )

        # In verbose mode, show additional status
        if verbose:
            console.print_workers_ready(workers)
            console.print_server_ready()

        # Start backend server
        try:
            # Configure uvicorn logging to use our formatter
            log_config = _get_uvicorn_log_config(verbose=verbose)
            uvicorn.run(
                "vibelab.api.app:app",
                host=host,
                port=port,
                reload=False,  # Don't use uvicorn reload when managing frontend separately
                log_level="info" if verbose else "warning",
                access_log=verbose,
                log_config=log_config,
            )
        except (KeyboardInterrupt, SystemExit):
            signal_handler(signal.SIGINT, None)
        finally:
            _cleanup_processes()
    else:
        # Production mode: serve static files from backend
        if not dist_dir.exists():
            console.echo(console.warning("  ⚠ Frontend not built"))
            console.echo(console.muted("    Run 'cd web && bun run build' first."))
            console.echo(console.muted("    Starting backend only..."))
            console.echo()

        # Print startup info
        console.print_startup_info(
            mode="production",
            api_url=f"http://{host}:{port}/api",
            frontend_url=f"http://{host}:{port}",
            workers=workers,
            project=project,
            verbose=verbose,
        )

        # In verbose mode, show additional status
        if verbose:
            console.print_workers_ready(workers)
            console.print_server_ready()

        log_config = _get_uvicorn_log_config(verbose=verbose)
        uvicorn.run(
            "vibelab.api.app:app",
            host=host,
            port=port,
            reload=False,
            log_level="info" if verbose else "warning",
            access_log=verbose,
            log_config=log_config,
        )
