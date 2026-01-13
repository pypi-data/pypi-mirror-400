"""Streaming log infrastructure for real-time output."""

import logging
import threading
import time
from collections.abc import Generator
from dataclasses import dataclass, field
from pathlib import Path

from ..db.connection import get_results_dir

logger = logging.getLogger(__name__)


def _get_result_dir(project_id: int, result_id: int) -> Path:
    """Get the result directory for a specific result."""
    result_dir = get_results_dir(project_id) / str(result_id)
    result_dir.mkdir(parents=True, exist_ok=True)
    return result_dir


@dataclass
class StreamingLog:
    """Manages streaming log files for a result."""

    result_id: int
    project_id: int
    _stdout_path: Path = field(init=False)
    _stderr_path: Path = field(init=False)
    _combined_path: Path = field(init=False)
    _status_path: Path = field(init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        result_dir = _get_result_dir(self.project_id, self.result_id)

        self._stdout_path = result_dir / "stdout.stream"
        self._stderr_path = result_dir / "stderr.stream"
        self._combined_path = result_dir / "combined.stream"
        self._status_path = result_dir / "stream.status"

        # Initialize files
        self._stdout_path.write_text("")
        self._stderr_path.write_text("")
        self._combined_path.write_text("")
        self._set_status("starting")

    def _set_status(self, status: str) -> None:
        """Set the streaming status."""
        self._status_path.write_text(status)

    def set_status(self, status: str) -> None:
        """Update the streaming status (public method)."""
        self._set_status(status)

    def get_status(self) -> str:
        """Get the streaming status."""
        if self._status_path.exists():
            return self._status_path.read_text().strip()
        return "unknown"

    def append_stdout(self, data: str) -> None:
        """Append data to stdout stream."""
        if not data:
            return
        with self._lock:
            with open(self._stdout_path, "a") as f:
                f.write(data)
            with open(self._combined_path, "a") as f:
                f.write(data)

    def append_stderr(self, data: str) -> None:
        """Append data to stderr stream."""
        if not data:
            return
        with self._lock:
            with open(self._stderr_path, "a") as f:
                f.write(data)
            with open(self._combined_path, "a") as f:
                f.write(data)

    def finalize(self, final_stdout: str | None = None, final_stderr: str | None = None) -> None:
        """Finalize the stream and save final logs."""
        result_dir = _get_result_dir(self.project_id, self.result_id)

        # Save final logs (either from provided strings or from stream files)
        if final_stdout is not None:
            (result_dir / "stdout.log").write_text(final_stdout)
        elif self._stdout_path.exists():
            (result_dir / "stdout.log").write_text(self._stdout_path.read_text())

        if final_stderr is not None:
            (result_dir / "stderr.log").write_text(final_stderr)
        elif self._stderr_path.exists():
            (result_dir / "stderr.log").write_text(self._stderr_path.read_text())

        self._set_status("completed")

    def mark_failed(self) -> None:
        """Mark the stream as failed."""
        self._set_status("failed")

    def get_stdout(self) -> str:
        """Get current stdout content."""
        if self._stdout_path.exists():
            return self._stdout_path.read_text()
        return ""

    def get_stderr(self) -> str:
        """Get current stderr content."""
        if self._stderr_path.exists():
            return self._stderr_path.read_text()
        return ""

    def get_combined(self) -> str:
        """Get current combined content."""
        if self._combined_path.exists():
            return self._combined_path.read_text()
        return ""


def get_streaming_log(project_id: int, result_id: int) -> StreamingLog | None:
    """Get or create a streaming log for a result.

    Args:
        project_id: The project ID (for blob storage path).
        result_id: The result ID.

    Returns:
        StreamingLog if the stream exists, None otherwise.
    """
    results_dir = get_results_dir(project_id)
    status_path = results_dir / str(result_id) / "stream.status"
    if status_path.exists():
        log = object.__new__(StreamingLog)
        log.result_id = result_id
        log.project_id = project_id
        log._stdout_path = results_dir / str(result_id) / "stdout.stream"
        log._stderr_path = results_dir / str(result_id) / "stderr.stream"
        log._combined_path = results_dir / str(result_id) / "combined.stream"
        log._status_path = status_path
        log._lock = threading.Lock()
        return log
    return None


def stream_log_file(
    project_id: int, result_id: int, poll_interval: float = 0.5
) -> Generator[dict[str, object], None, None]:
    """
    Generator that yields log updates for a result.

    Args:
        project_id: The project ID (for blob storage path).
        result_id: The result ID.
        poll_interval: How often to poll for updates (seconds).

    Yields dicts with:
    - type: "stdout" | "stderr" | "combined" | "status" | "patch"
    - data: the content
    - offset: byte offset (for incremental updates)
    """
    result_dir = get_results_dir(project_id) / str(result_id)

    combined_path = result_dir / "combined.stream"
    status_path = result_dir / "stream.status"
    patch_path = result_dir / "patch.diff"

    last_combined_size = 0
    last_patch_content = ""

    # Initial status
    if status_path.exists():
        status = status_path.read_text().strip()
        yield {"type": "status", "data": status}
    else:
        yield {"type": "status", "data": "waiting"}
        # Wait for stream to start
        for _ in range(60):  # Wait up to 30 seconds
            if status_path.exists():
                break
            time.sleep(0.5)
        if not status_path.exists():
            yield {"type": "status", "data": "timeout"}
            return

    while True:
        # Check status
        status = status_path.read_text().strip() if status_path.exists() else "unknown"

        # Read new combined output
        if combined_path.exists():
            current_size = combined_path.stat().st_size
            if current_size > last_combined_size:
                with open(combined_path) as f:
                    f.seek(last_combined_size)
                    new_content = f.read()
                    if new_content:
                        yield {
                            "type": "output",
                            "data": new_content,
                            "offset": last_combined_size,
                        }
                last_combined_size = current_size

        # Check for patch updates
        if patch_path.exists():
            try:
                patch_content = patch_path.read_text()
                if patch_content != last_patch_content:
                    yield {"type": "patch", "data": patch_content}
                    last_patch_content = patch_content
            except Exception:
                pass

        # If completed or failed, send final status and exit
        if status in ("completed", "failed"):
            yield {"type": "status", "data": status}
            # Send any remaining output
            if combined_path.exists():
                current_size = combined_path.stat().st_size
                if current_size > last_combined_size:
                    with open(combined_path) as f:
                        f.seek(last_combined_size)
                        new_content = f.read()
                        if new_content:
                            yield {"type": "output", "data": new_content}
            # Final patch
            if patch_path.exists():
                yield {"type": "patch", "data": patch_path.read_text()}
            break

        time.sleep(poll_interval)


def cleanup_stream_files(project_id: int, result_id: int) -> None:
    """Clean up streaming files after completion.

    Args:
        project_id: The project ID (for blob storage path).
        result_id: The result ID.
    """
    result_dir = get_results_dir(project_id) / str(result_id)

    for suffix in [".stream"]:
        for path in result_dir.glob(f"*{suffix}"):
            try:
                path.unlink()
            except Exception:
                pass
