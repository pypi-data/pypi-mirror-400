"""
Settings Screen - Configuration and preferences.
"""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Rule, Static

from ..api_client import ApiClient


class SettingsScreen(VerticalScroll):
    """Screen for managing settings and configuration."""

    DEFAULT_CSS = """
    SettingsScreen {
        padding: 1 2;
    }

    SettingsScreen > .section-title {
        text-style: bold;
        color: $primary;
        margin-top: 1;
        padding: 0 1;
    }

    SettingsScreen > .setting {
        padding: 0 2;
        color: $text;
    }

    SettingsScreen > .setting-muted {
        padding: 0 2;
        color: $text-muted;
    }

    SettingsScreen > .key-group {
        margin-top: 1;
        padding: 0 2;
        color: $secondary;
    }

    SettingsScreen > .about-text {
        padding: 0 2;
        color: $primary;
    }

    SettingsScreen Rule {
        margin: 1 0;
        color: $boost;
    }
    """

    def __init__(self, api_client: ApiClient, **kwargs) -> None:
        super().__init__(**kwargs)
        self.api_client = api_client

    def compose(self) -> ComposeResult:
        yield Static("◈ SETTINGS", classes="section-title")
        yield Rule()

        yield Static("◇ CONNECTION", classes="section-title")
        yield Static(f"API URL: {self.api_client.base_url}", classes="setting")
        yield Static("Status: ◌ checking...", id="server-status", classes="setting")

        yield Rule()
        yield Static("◇ KEYBOARD SHORTCUTS", classes="section-title")

        yield Static("◇ Navigation", classes="key-group")
        yield Static("  1-5       Switch between tabs", classes="setting-muted")
        yield Static("  /         Focus search input", classes="setting-muted")
        yield Static("  ?         Show help overlay", classes="setting-muted")
        yield Static("  q         Quit application", classes="setting-muted")

        yield Static("◇ Lists", classes="key-group")
        yield Static("  j / Down  Move down in list", classes="setting-muted")
        yield Static("  k / Up    Move up in list", classes="setting-muted")
        yield Static("  Enter     Select / Open item", classes="setting-muted")
        yield Static("  Esc       Go back / Close", classes="setting-muted")

        yield Static("◇ Memories", classes="key-group")
        yield Static("  a         Add new memory", classes="setting-muted")
        yield Static("  e         Edit selected memory", classes="setting-muted")
        yield Static("  c         Copy memory content", classes="setting-muted")
        yield Static("  d         Delete selected memory", classes="setting-muted")
        yield Static("  r         Refresh list", classes="setting-muted")

        yield Static("◇ Detail Views", classes="key-group")
        yield Static("  c         Copy content to clipboard", classes="setting-muted")
        yield Static("  y         Copy ID to clipboard", classes="setting-muted")

        yield Static("◇ Threads", classes="key-group")
        yield Static("  d         Distill to memories", classes="setting-muted")
        yield Static("  x         Delete thread", classes="setting-muted")
        yield Static("  r         Refresh list", classes="setting-muted")

        yield Static("◇ Graph", classes="key-group")
        yield Static("  e         Expand all nodes", classes="setting-muted")
        yield Static("  c         Collapse all nodes", classes="setting-muted")
        yield Static("  r         Refresh graph", classes="setting-muted")

        yield Rule()
        yield Static("◇ ABOUT", classes="section-title")
        yield Static("◈ Nowledge Mem", classes="about-text")
        yield Static("  AI that remembers your world", classes="setting-muted")
        yield Static(
            "  TUI built with Textual (textual.textualize.io)", classes="setting-muted"
        )
        yield Static("  Your data stays only on your device.", classes="setting-muted")

    def on_mount(self) -> None:
        self.run_worker(self._check_status(), exclusive=True, thread=False)

    async def _check_status(self) -> None:
        try:
            health = await self.api_client.get_health()
            status = health.get("status", "unknown")
            version = health.get("version", "unknown")

            status_widget = self.query_one("#server-status", Static)
            if status == "ok":
                status_widget.update(f"Status: ● Online (v{version})")
            else:
                status_widget.update(f"Status: ○ {status}")
        except Exception as e:
            self.query_one("#server-status", Static).update(f"Status: ✗ Error - {e}")
