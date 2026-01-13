#!/usr/bin/env python3
"""Release script for VibeLab.

Prepares a release by bumping the version, building, committing, and tagging.
After running this script, trigger the release workflow in GitHub Actions UI.

Usage:
    python scripts/release.py patch    # 0.0.2 -> 0.0.3
    python scripts/release.py minor    # 0.0.2 -> 0.1.0
    python scripts/release.py major    # 0.0.2 -> 1.0.0
    python scripts/release.py 1.2.3    # Set explicit version
    
    # Options:
    --dry-run    Show what would happen without making changes
    --no-push    Commit and tag locally but don't push

After pushing:
    1. Go to GitHub Actions > Release workflow
    2. Click "Run workflow"
    3. Select pypi or testpypi
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
VERSION_FILE = PROJECT_ROOT / "src" / "vibelab" / "__init__.py"
VERSION_PATTERN = re.compile(r'^__version__\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)


def get_current_version() -> str:
    """Read current version from __init__.py."""
    content = VERSION_FILE.read_text()
    match = VERSION_PATTERN.search(content)
    if not match:
        raise ValueError(f"Could not find __version__ in {VERSION_FILE}")
    return match.group(1)


def bump_version(current: str, bump_type: str) -> str:
    """Calculate new version based on bump type."""
    # Check if it's an explicit version
    if re.match(r"^\d+\.\d+\.\d+$", bump_type):
        return bump_type

    parts = current.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {current}")

    major, minor, patch = map(int, parts)

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Unknown bump type: {bump_type}. Use major, minor, patch, or X.Y.Z")


def update_version_file(new_version: str) -> None:
    """Update version in __init__.py."""
    content = VERSION_FILE.read_text()
    new_content = VERSION_PATTERN.sub(f'__version__ = "{new_version}"', content)
    VERSION_FILE.write_text(new_content)


def run(
    cmd: list[str], check: bool = True, capture: bool = False, cwd: Path | None = None
) -> subprocess.CompletedProcess:
    """Run a command, printing it first."""
    work_dir = cwd or PROJECT_ROOT
    if cwd:
        print(f"  $ cd {cwd.relative_to(PROJECT_ROOT)} && {' '.join(cmd)}")
    else:
        print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=capture, text=True, cwd=work_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description="Release a new version of VibeLab")
    parser.add_argument(
        "version",
        help="Version bump type (major, minor, patch) or explicit version (X.Y.Z)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Commit and tag locally but don't push",
    )
    args = parser.parse_args()

    # Get current version
    current_version = get_current_version()
    new_version = bump_version(current_version, args.version)
    tag_name = f"v{new_version}"

    print(f"\n{'=' * 50}")
    print(f"VibeLab Release")
    print(f"{'=' * 50}")
    print(f"  Current version: {current_version}")
    print(f"  New version:     {new_version}")
    print(f"  Git tag:         {tag_name}")
    print(f"{'=' * 50}\n")

    if args.dry_run:
        print("[DRY RUN] Would perform the following steps:\n")
        print(f"1. Update {VERSION_FILE.relative_to(PROJECT_ROOT)}")
        print("2. Run: uv sync")
        print("3. Run: cd web && bun run build")
        print(f"4. Run: git add -A")
        print(f"5. Run: git commit -m 'Release {tag_name}'")
        print(f"6. Run: git tag -a {tag_name} -m 'Release {tag_name}'")
        if not args.no_push:
            print(f"7. Run: git push && git push origin {tag_name}")
        print("\n[DRY RUN] No changes made.")
        return 0

    # Check for uncommitted changes (except the ones we'll make)
    result = run(["git", "status", "--porcelain"], capture=True)
    if result.stdout.strip():
        print("Warning: You have uncommitted changes. They will be included in the release commit.")
        response = input("Continue? [y/N] ")
        if response.lower() != "y":
            print("Aborted.")
            return 1

    print("Step 1: Updating version...")
    update_version_file(new_version)
    print(f"  Updated {VERSION_FILE.relative_to(PROJECT_ROOT)}")

    print("\nStep 2: Syncing dependencies...")
    run(["uv", "sync"])

    print("\nStep 3: Building frontend...")
    run(["bun", "run", "build"], cwd=PROJECT_ROOT / "web")

    print("\nStep 4: Committing changes...")
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", f"Release {tag_name}"])

    print("\nStep 5: Creating git tag...")
    run(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"])

    if args.no_push:
        print("\n[--no-push] Skipping push. To push manually:")
        print(f"  git push && git push origin {tag_name}")
    else:
        print("\nStep 6: Pushing to remote...")
        run(["git", "push"])
        run(["git", "push", "origin", tag_name])

    print(f"\n{'=' * 50}")
    print(f"Release {tag_name} ready!")
    print(f"{'=' * 50}")
    print("\nNext steps:")
    print("  1. Go to: https://github.com/<owner>/<repo>/actions/workflows/release.yml")
    print("  2. Click 'Run workflow'")
    print("  3. Select 'pypi' to publish, or 'testpypi' to test first")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())

