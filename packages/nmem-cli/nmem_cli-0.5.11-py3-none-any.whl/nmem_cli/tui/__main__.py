"""
Entry point for running TUI with Textual dev mode.

Usage:
    python -m textual run --dev nmem_cli.tui

Or directly:
    python -m nmem_cli.tui
"""

from .app import NowledgeMemApp

app = NowledgeMemApp()

if __name__ == "__main__":
    app.run()
