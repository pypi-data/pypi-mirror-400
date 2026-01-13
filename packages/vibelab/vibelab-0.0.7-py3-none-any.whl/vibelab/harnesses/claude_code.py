"""Claude Code harness."""

import os
import shutil
import subprocess
import threading
from pathlib import Path

from ..models.executor import ModelInfo
from .base import HarnessOutput, PricingInfo, StreamCallback


class ClaudeCodeHarness:
    """Harness for Claude Code CLI."""

    id = "claude-code"
    name = "Claude Code"
    supported_providers = ["anthropic"]
    preferred_driver = None

    def get_models(self, provider: str) -> list[ModelInfo]:
        """Get available models."""
        if provider != "anthropic":
            return []
        # Dynamically fetch versioned models from LiteLLM for reproducibility
        from ..models_registry import get_anthropic_models

        registry_models = get_anthropic_models()
        return [ModelInfo(id=m.id, name=m.name) for m in registry_models]

    def get_pricing(self, provider: str, model: str) -> PricingInfo | None:
        """Get pricing information for Anthropic models.

        Note: Primary pricing comes from LiteLLM in pricing.py.
        This method returns None to defer to LiteLLM for all explicit model IDs.
        """
        # All explicit model IDs are handled by LiteLLM
        return None

    def check_available(self) -> tuple[bool, str | None]:
        """Check if Claude Code CLI is available."""
        if shutil.which("claude") is None:
            return (
                False,
                "Claude Code CLI not found. Install: npm install -g @anthropic-ai/claude-code",
            )
        return True, None

    def run(
        self,
        workdir: Path,
        prompt: str,
        provider: str,
        model: str,
        timeout_seconds: int,
        on_stdout: StreamCallback | None = None,
        on_stderr: StreamCallback | None = None,
    ) -> HarnessOutput:
        """Execute Claude Code CLI with optional streaming."""
        cmd = [
            "claude",
            "--print",
            "--verbose",
            "--output-format",
            "stream-json",
            "--dangerously-skip-permissions",  # Skip permission prompts in isolated worktrees
            "--model",
            model,
            "-p",
            prompt,
        ]

        # If streaming callbacks provided, use Popen for real-time output
        if on_stdout or on_stderr:
            return self._run_streaming(cmd, workdir, timeout_seconds, on_stdout, on_stderr)

        # Otherwise use simple subprocess.run
        try:
            result = subprocess.run(
                cmd,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return HarnessOutput(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )
        except subprocess.TimeoutExpired:
            return HarnessOutput(
                exit_code=124,
                stdout="",
                stderr="Command timed out",
            )

    def _run_streaming(
        self,
        cmd: list[str],
        workdir: Path,
        timeout_seconds: int,
        on_stdout: StreamCallback | None,
        on_stderr: StreamCallback | None,
    ) -> HarnessOutput:
        """Run command with streaming output via callbacks."""
        stdout_chunks: list[str] = []
        stderr_chunks: list[str] = []

        def read_stream(stream, chunks: list[str], callback: StreamCallback | None):
            """Read stream line by line and call callback."""
            try:
                for line in iter(stream.readline, ""):
                    if line:
                        chunks.append(line)
                        if callback:
                            callback(line)
            except Exception:
                pass
            finally:
                stream.close()

        try:
            process = subprocess.Popen(
                cmd,
                cwd=workdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
            )

            # Start threads to read stdout and stderr
            stdout_thread = threading.Thread(
                target=read_stream,
                args=(process.stdout, stdout_chunks, on_stdout),
            )
            stderr_thread = threading.Thread(
                target=read_stream,
                args=(process.stderr, stderr_chunks, on_stderr),
            )

            stdout_thread.start()
            stderr_thread.start()

            # Wait for process with timeout
            try:
                exit_code = process.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)
                return HarnessOutput(
                    exit_code=124,
                    stdout="".join(stdout_chunks),
                    stderr="".join(stderr_chunks) + "\nCommand timed out",
                )

            # Wait for threads to finish reading
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)

            return HarnessOutput(
                exit_code=exit_code,
                stdout="".join(stdout_chunks),
                stderr="".join(stderr_chunks),
            )

        except Exception as e:
            return HarnessOutput(
                exit_code=1,
                stdout="".join(stdout_chunks),
                stderr=f"Error running command: {e}",
            )

    def get_container_image(self) -> str | None:
        """Return container image if available."""
        # Default to vibelab image, can be overridden via environment
        return os.getenv("VIBELAB_CLAUDE_CODE_IMAGE", "vibelab/claude-code:latest")
