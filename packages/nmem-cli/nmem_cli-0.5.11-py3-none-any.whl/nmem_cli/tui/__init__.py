"""
Nowledge Mem TUI - Terminal User Interface for memory management.

Launch with: nmem tui

For Textual dev mode:
    python -m textual run --dev nmem_cli.tui
"""

import logging

from .app import NowledgeMemApp

__all__ = ["NowledgeMemApp", "run_tui"]

# Disable all logging to stdout/stderr - it corrupts the TUI display
# Logs will go to textual.log if using textual run --dev
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def run_tui() -> None:
    """Entry point for the TUI application."""
    app = NowledgeMemApp()
    app.run()


# For textual run --dev compatibility
app = NowledgeMemApp()
