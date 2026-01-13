"""Local driver using git worktrees from shared bare clones."""

import logging
import subprocess
from pathlib import Path

from ..db.connection import get_results_dir, get_worktrees_dir
from ..drivers.base import ExecutionContext, RunOutput

logger = logging.getLogger(__name__)


def _get_project_id_for_result(result_id: int) -> int:
    """Get project_id for a result.

    Raises:
        ValueError: If project_id cannot be determined.
    """
    from ..db import get_db
    from ..db.queries import get_project_id_for_result

    for db in get_db():
        project_id = get_project_id_for_result(db, result_id)
        if project_id is not None:
            return project_id
    raise ValueError(f"Could not determine project_id for result {result_id}")


class LocalDriver:
    """Local execution driver using git worktrees."""

    id = "local"

    def setup(self, ctx: ExecutionContext) -> None:
        """Create git worktree for isolation."""
        if ctx.streaming_log:
            ctx.streaming_log.set_status("cloning")

        worktrees_dir = get_worktrees_dir()

        workdir = worktrees_dir / ctx.result_id
        ctx.workdir = workdir

        # Load code based on scenario type
        if ctx.scenario.code_type.value == "github":
            self._setup_github(ctx, workdir)
        elif ctx.scenario.code_type.value == "local":
            self._setup_local(ctx, workdir)
        elif ctx.scenario.code_type.value == "empty":
            self._setup_empty(workdir)
        else:
            raise ValueError(f"Unknown code type: {ctx.scenario.code_type}")

        if ctx.streaming_log:
            ctx.streaming_log.set_status("running")

    def _setup_github(self, ctx: ExecutionContext, workdir: Path) -> None:
        """Setup GitHub repository using shared bare clone + worktree."""
        from datetime import datetime

        from ..engine.repo_cache import get_repo_cache
        from ..models.scenario import GitHubCodeRef

        code_ref = ctx.scenario.code_ref
        if not isinstance(code_ref, GitHubCodeRef):
            raise ValueError("Expected GitHubCodeRef")

        repo_cache = get_repo_cache()
        host = "github.com"

        ts = datetime.now().strftime("%H:%M:%S")
        if ctx.streaming_log:
            short_sha = code_ref.commit_sha[:8]
            msg = f"[{ts}] Setting up worktree for {code_ref.owner}/{code_ref.repo}@{short_sha}\n"
            ctx.streaming_log.append_stdout(msg)

        # Create worktree from shared bare clone (will clone if needed)
        repo_cache.create_worktree(
            host=host,
            owner=code_ref.owner,
            repo=code_ref.repo,
            commit_sha=code_ref.commit_sha,
            worktree_path=workdir,
        )

        ts = datetime.now().strftime("%H:%M:%S")
        if ctx.streaming_log:
            ctx.streaming_log.append_stdout(
                f"[{ts}] Worktree ready at commit {code_ref.commit_sha[:8]}\n"
            )

    def _setup_local(self, ctx: ExecutionContext, workdir: Path) -> None:
        """Setup local directory by copying."""
        from ..models.scenario import LocalCodeRef

        code_ref = ctx.scenario.code_ref
        if not isinstance(code_ref, LocalCodeRef):
            raise ValueError("Expected LocalCodeRef")

        import shutil

        source = Path(code_ref.path).expanduser()
        if not source.exists():
            raise ValueError(f"Local path does not exist: {source}")

        if ctx.streaming_log:
            ctx.streaming_log.append_stdout(f"Copying local directory: {source}\n")

        shutil.copytree(source, workdir, dirs_exist_ok=True)

    def _setup_empty(self, workdir: Path) -> None:
        """Setup empty directory and initialize git repo."""
        workdir.mkdir(parents=True, exist_ok=True)

        # Initialize git repository for patch generation
        subprocess.run(
            ["git", "init"],
            cwd=workdir,
            check=True,
            capture_output=True,
        )

        # Configure git user (required for commits)
        subprocess.run(
            ["git", "config", "user.name", "VibeLab"],
            cwd=workdir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "vibelab@localhost"],
            cwd=workdir,
            check=True,
            capture_output=True,
        )

        # Create initial commit with empty state for diff comparison
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "Initial empty state"],
            cwd=workdir,
            check=False,  # May fail if no files, that's ok
            capture_output=True,
        )

    def execute(self, ctx: ExecutionContext) -> RunOutput:
        """Execute harness in worktree with streaming output."""
        import threading
        import time
        from datetime import datetime

        if not ctx.workdir:
            raise ValueError("workdir not set")

        result_id_int = int(ctx.result_id)
        project_id = _get_project_id_for_result(result_id_int)

        # Use streaming log from context if available
        streaming_log = ctx.streaming_log
        if not streaming_log:
            # Fallback: create new streaming log if not provided
            from ..engine.streaming import StreamingLog

            streaming_log = StreamingLog(result_id=result_id_int, project_id=project_id)

        start_time = time.time()
        result_dir = get_results_dir(project_id) / ctx.result_id
        result_dir.mkdir(parents=True, exist_ok=True)
        patch_path = result_dir / "patch.diff"

        # Track last patch for change detection
        last_patch = ""
        stop_patch_thread = threading.Event()

        def update_patch_periodically() -> None:
            """Background thread to periodically update the patch file."""
            nonlocal last_patch
            while not stop_patch_thread.is_set():
                try:
                    patch = self._generate_patch(ctx.workdir)
                    if patch and patch != last_patch:
                        patch_path.write_text(patch)
                        last_patch = patch
                except Exception:
                    pass  # Ignore errors during patch generation
                # Wait 2 seconds between updates (or until stopped)
                stop_patch_thread.wait(2.0)

        # Start background patch generation thread
        patch_thread = threading.Thread(target=update_patch_periodically, daemon=True)
        patch_thread.start()

        # Define callbacks for streaming
        def on_stdout(data: str) -> None:
            if streaming_log:
                streaming_log.append_stdout(data)

        def on_stderr(data: str) -> None:
            if streaming_log:
                streaming_log.append_stderr(data)

        try:
            ts = datetime.now().strftime("%H:%M:%S")
            if streaming_log:
                streaming_log.append_stdout(f"[{ts}] Starting execution with {ctx.harness.id}...\n")

            # Run harness with streaming callbacks
            output = ctx.harness.run(
                workdir=ctx.workdir,
                prompt=ctx.scenario.prompt,
                provider=ctx.provider,
                model=ctx.model,
                timeout_seconds=ctx.timeout_seconds,
                on_stdout=on_stdout,
                on_stderr=on_stderr,
            )

            # Stop background patch generation
            stop_patch_thread.set()
            patch_thread.join(timeout=1.0)

            duration_ms = int((time.time() - start_time) * 1000)

            ts = datetime.now().strftime("%H:%M:%S")
            if streaming_log:
                msg = f"\n[{ts}] Execution completed (exit code: {output.exit_code})\n"
                streaming_log.append_stdout(msg)

            # Generate final patch
            patch = self._generate_patch(ctx.workdir)

            # Save final patch
            if patch:
                patch_path.write_text(patch)

            # Note: Don't finalize here - runner will handle finalization
            # This allows runner to set final status based on exit code

            return RunOutput(
                exit_code=output.exit_code,
                stdout=output.stdout,
                stderr=output.stderr,
                duration_ms=duration_ms,
                patch=patch,
            )
        except Exception as e:
            # Stop background thread on error too
            stop_patch_thread.set()
            patch_thread.join(timeout=1.0)
            if streaming_log:
                streaming_log.append_stderr(f"\nExecution failed: {e}\n")
                streaming_log.mark_failed()
            raise

    def _generate_patch(self, workdir: Path) -> str | None:
        """Generate git patch of changes."""
        try:
            # Check if this is a git repository
            git_check = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=workdir,
                capture_output=True,
                check=False,
            )
            if git_check.returncode != 0:
                # Not a git repo, no patch possible
                return None

            # Stage all changes (including untracked files) for proper diff
            subprocess.run(
                ["git", "add", "-A"],
                cwd=workdir,
                check=False,
                capture_output=True,
            )

            # Get diff of staged changes (modified and new files)
            diff_result = subprocess.run(
                ["git", "diff", "--cached", "HEAD"],
                cwd=workdir,
                capture_output=True,
                text=True,
                check=False,
            )

            patches = []
            if diff_result.returncode == 0 and diff_result.stdout:
                patches.append(diff_result.stdout)

            if patches:
                return "".join(patches)
            return None
        except Exception as e:
            logger.warning(f"Failed to generate patch: {e}")
            return None

    def cleanup(self, ctx: ExecutionContext) -> None:
        """Remove work directory (and unregister worktree if applicable)."""
        if not ctx.workdir:
            return

        import shutil

        try:
            # Check if this is a git worktree (indicated by .git being a file, not directory)
            git_path = ctx.workdir / ".git"
            if git_path.is_file():
                # This is a worktree - try to read the gitdir to find the bare clone
                gitdir_ref = git_path.read_text().strip()
                if gitdir_ref.startswith("gitdir: "):
                    gitdir = Path(gitdir_ref[8:])
                    # Navigate up from .../worktrees/<name> to the bare repo
                    bare_path = gitdir.parent.parent
                    if bare_path.exists():
                        # Remove worktree via git (cleaner than just rmtree)
                        result = subprocess.run(
                            ["git", "worktree", "remove", "--force", str(ctx.workdir)],
                            cwd=bare_path,
                            check=False,
                            capture_output=True,
                        )
                        if result.returncode == 0:
                            return  # Successfully removed via git

            # Fallback: remove directory directly
            shutil.rmtree(ctx.workdir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Failed to cleanup workdir: {e}")
            # Last resort: try simple rmtree
            shutil.rmtree(ctx.workdir, ignore_errors=True)
