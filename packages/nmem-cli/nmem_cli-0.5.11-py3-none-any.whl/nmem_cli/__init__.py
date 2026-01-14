"""
nmem-cli - CLI and TUI for Nowledge Mem

A lightweight command-line interface and terminal UI for interacting
with the Nowledge Mem server.

Usage:
    nmem status          Check server connection
    nmem stats           Show database statistics
    nmem tui             Launch interactive TUI
    nmem m               List memories (alias for 'memories')
    nmem m search "q"    Search memories
    nmem t               List threads (alias for 'threads')

Environment:
    NMEM_API_URL         Override API URL (default: http://127.0.0.1:14242)
"""

__version__ = "0.5.11"
__author__ = "Nowledge Labs"

from .cli import main

__all__ = ["__version__", "main"]
