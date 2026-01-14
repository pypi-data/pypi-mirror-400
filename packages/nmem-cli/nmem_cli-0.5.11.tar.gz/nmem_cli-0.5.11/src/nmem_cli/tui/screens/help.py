"""
Help Screen - Overlay showing keybindings and help.
"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Rule, Static


class HelpScreen(ModalScreen):
    """Modal help screen showing keybindings."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close"),
        Binding("question_mark", "app.pop_screen", "Close"),
    ]

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    HelpScreen > #help-container {
        width: 70;
        height: auto;
        max-height: 85%;
        padding: 2;
        background: $surface;
        border: round $primary;
    }

    HelpScreen .help-title {
        text-style: bold;
        text-align: center;
        color: $primary;
    }

    HelpScreen .section {
        text-style: bold;
        color: $secondary;
        margin-top: 1;
    }

    HelpScreen .key-row {
        color: $text;
    }

    HelpScreen .key {
        color: $accent;
        text-style: bold;
    }

    HelpScreen .hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }

    HelpScreen Rule {
        color: $boost;
    }
"""

    def compose(self) -> ComposeResult:
        with Container(id="help-container"):
            with Vertical():
                yield Static("◈ NOWLEDGE MEM TUI ◈", classes="help-title")
                yield Static("AI that remembers your world", classes="hint")
                yield Rule()

                yield Static("◇ Global Navigation", classes="section")
                yield Static("  1-5       Switch between tabs", classes="key-row")
                yield Static("  /         Focus search input", classes="key-row")
                yield Static("  ?         Toggle this help", classes="key-row")
                yield Static("  q         Quit application", classes="key-row")

                yield Static("◇ List Navigation", classes="section")
                yield Static("  j / ↓     Move down in list", classes="key-row")
                yield Static("  k / ↑     Move up in list", classes="key-row")
                yield Static("  Enter     Select / View details", classes="key-row")
                yield Static("  Esc       Go back / Cancel", classes="key-row")

                yield Static("◇ Memory Actions", classes="section")
                yield Static("  a         Add new memory", classes="key-row")
                yield Static("  e         Edit memory", classes="key-row")
                yield Static("  c         Copy content", classes="key-row")
                yield Static("  d         Delete memory", classes="key-row")
                yield Static("  r         Refresh list", classes="key-row")

                yield Static("◇ Detail View", classes="section")
                yield Static("  c         Copy content to clipboard", classes="key-row")
                yield Static("  y         Copy ID to clipboard", classes="key-row")
                yield Static("  e         Edit item", classes="key-row")

                yield Static("◇ Thread Actions", classes="section")
                yield Static("  d         Distill to memories", classes="key-row")
                yield Static("  x         Delete thread", classes="key-row")
                yield Static("  r         Refresh list", classes="key-row")

                yield Static("◇ Graph View", classes="section")
                yield Static("  e         Expand all nodes", classes="key-row")
                yield Static("  c         Collapse all nodes", classes="key-row")
                yield Static("  r         Refresh graph", classes="key-row")

                yield Rule()
                yield Static("Press ? or Esc to close", classes="hint")
