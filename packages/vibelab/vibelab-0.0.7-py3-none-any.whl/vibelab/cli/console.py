"""Console styling utilities for beautiful terminal output."""

from __future__ import annotations

import os
import re
import sys
from typing import TextIO

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# Bright colors
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# Check if colors should be enabled
_COLORS_ENABLED: bool | None = None


def _colors_enabled() -> bool:
    """Check if color output should be enabled."""
    global _COLORS_ENABLED
    if _COLORS_ENABLED is None:
        # Disable colors if not a TTY or if NO_COLOR env is set
        if os.environ.get("NO_COLOR"):
            _COLORS_ENABLED = False
        elif not sys.stderr.isatty():
            _COLORS_ENABLED = False
        else:
            _COLORS_ENABLED = True
    return _COLORS_ENABLED


def style(text: str, *codes: str) -> str:
    """Apply ANSI style codes to text."""
    if not _colors_enabled():
        return text
    return "".join(codes) + text + RESET


def echo(
    message: str = "",
    *,
    err: bool = True,
    nl: bool = True,
    file: TextIO | None = None,
) -> None:
    """Print a message to the console."""
    out = file or (sys.stderr if err else sys.stdout)
    out.write(message)
    if nl:
        out.write("\n")
    out.flush()


# Pre-styled helpers
def success(text: str) -> str:
    """Style text as success (green)."""
    return style(text, BRIGHT_GREEN)


def error(text: str) -> str:
    """Style text as error (red)."""
    return style(text, BRIGHT_RED)


def warning(text: str) -> str:
    """Style text as warning (yellow)."""
    return style(text, BRIGHT_YELLOW)


def info(text: str) -> str:
    """Style text as info (cyan)."""
    return style(text, CYAN)


def muted(text: str) -> str:
    """Style text as muted (dim)."""
    return style(text, DIM)


def bold(text: str) -> str:
    """Style text as bold."""
    return style(text, BOLD)


def accent(text: str) -> str:
    """Style text with accent color (magenta)."""
    return style(text, BRIGHT_MAGENTA)


# Box drawing characters
BOX_TL = "╭"
BOX_TR = "╮"
BOX_BL = "╰"
BOX_BR = "╯"
BOX_H = "─"
BOX_V = "│"


def box(content: list[str], width: int = 50) -> str:
    """Draw a box around content."""
    inner_width = width - 2
    lines = [
        f"{BOX_TL}{BOX_H * inner_width}{BOX_TR}",
    ]
    for line in content:
        # Strip ANSI codes for length calculation
        stripped = re.sub(r"\033\[[0-9;]*m", "", line)
        padding = inner_width - len(stripped)
        lines.append(f"{BOX_V}{line}{' ' * max(0, padding)}{BOX_V}")
    lines.append(f"{BOX_BL}{BOX_H * inner_width}{BOX_BR}")
    return "\n".join(lines)


# ASCII art banner
BANNER_ART = r"""
   ██╗   ██╗██╗██████╗ ███████╗██╗      █████╗ ██████╗ 
   ██║   ██║██║██╔══██╗██╔════╝██║     ██╔══██╗██╔══██╗
   ██║   ██║██║██████╔╝█████╗  ██║     ███████║██████╔╝
   ╚██╗ ██╔╝██║██╔══██╗██╔══╝  ██║     ██╔══██║██╔══██╗
    ╚████╔╝ ██║██████╔╝███████╗███████╗██║  ██║██████╔╝
     ╚═══╝  ╚═╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝ 
"""

BANNER_SMALL = r"""
 ╦  ╦┬┌┐ ┌─┐╦  ┌─┐┌┐ 
 ╚╗╔╝│├┴┐├┤ ║  ├─┤├┴┐
  ╚╝ ┴└─┘└─┘╩═╝┴ ┴└─┘
"""


def print_banner(*, small: bool = False) -> None:
    """Print the VibeLab ASCII art banner."""
    art = BANNER_SMALL if small else BANNER_ART
    echo(style(art, BRIGHT_CYAN, BOLD))


def print_alpha_warning() -> None:
    """Print the alpha release warning."""
    echo()
    echo(style("  ⚠️  ALPHA RELEASE", BRIGHT_YELLOW, BOLD))
    echo(muted("  This project is in active development."))
    echo(muted("  Breaking changes may occur."))
    echo()


def print_startup_info(
    *,
    mode: str,
    api_url: str,
    frontend_url: str | None = None,
    workers: int,
    project: str = "default",
    verbose: bool = False,
) -> None:
    """Print formatted startup information."""
    mode_styled = success(mode) if mode == "development" else info(mode)

    # Docs are at /docs (FastAPI default), derive base URL from API URL
    base_url = api_url.replace("/api", "").rstrip("/")
    docs_url = base_url + "/docs"

    echo(f"  {bold('Mode')}       {mode_styled}")
    echo(f"  {bold('Project')}    {muted(project)}")
    if frontend_url:
        echo(f"  {bold('Frontend')}   {accent(frontend_url)}")
    echo(f"  {bold('API')}        {accent(api_url)}")
    echo(f"  {bold('Docs')}       {muted(docs_url)}")
    echo(f"  {bold('Workers')}    {info(str(workers))}")
    echo()


def print_workers_ready(count: int) -> None:
    """Print workers ready message."""
    checkmark = style("✓", BRIGHT_GREEN, BOLD)
    echo(f"  {checkmark} {success(str(count))} worker(s) ready")
    echo()


def print_server_ready() -> None:
    """Print server ready message."""
    echo(style("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", DIM))
    echo(f"  {style('🚀', BRIGHT_GREEN)} {bold('Ready')}")
    echo()


def print_shutdown() -> None:
    """Print shutdown message."""
    echo()
    echo(muted("  Shutting down gracefully..."))


def print_divider() -> None:
    """Print a visual divider."""
    echo(style("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", DIM))
