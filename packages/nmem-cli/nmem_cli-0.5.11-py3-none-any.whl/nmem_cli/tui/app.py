"""
Nowledge Mem TUI - Main Application.
Elegant terminal interface with rounded aesthetics and gradient-inspired colors.
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.theme import Theme
from textual.widgets import Footer, Header, TabbedContent, TabPane

from .api_client import ApiClient
from .screens.dashboard import DashboardScreen
from .screens.graph import GraphScreen
from .screens.memories import MemoriesScreen
from .screens.settings import SettingsScreen
from .screens.threads import ThreadsScreen

# Elegant gradient-inspired theme with teal-cyan-purple spectrum
NOWLEDGE_THEME = Theme(
    name="nowledge",
    primary="#06B6D4",  # Cyan-500 (vibrant teal)
    secondary="#22D3EE",  # Cyan-400 (light cyan glow)
    accent="#A78BFA",  # Violet-400 (purple accent)
    warning="#FCD34D",  # Amber-300
    error="#FB7185",  # Rose-400
    success="#4ADE80",  # Green-400
    surface="#0C1222",  # Deep navy (almost black)
    panel="#162032",  # Slightly lighter navy
    boost="#1E3A5F",  # Blue-tinted hover
)


class NowledgeMemApp(App):
    """Nowledge Mem Terminal User Interface."""

    TITLE = "Nowledge Mem"
    SUB_TITLE = "AI that remembers your world"

    CSS = """
    /* ═══════════════════════════════════════════════════════════════
       ELEGANT HACKER AESTHETIC - Rounded corners & gradient vibes
       ═══════════════════════════════════════════════════════════════ */

    Screen {
        background: $surface;
    }

    /* Header with glow effect */
    Header {
        background: $primary;
        text-style: bold;
    }

    Footer {
        background: $panel;
    }

    TabbedContent > ContentSwitcher {
        background: $surface;
    }

    /* ═══ Tab styling with rounded feel ═══ */
    Tabs {
        background: $panel;
        dock: top;
    }

    Tab {
        background: $panel;
        color: $text-muted;
        padding: 0 3;
        margin: 0 1;
    }

    Tab:hover {
        background: $boost;
        color: $secondary;
        text-style: bold;
    }

    Tab.-active {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    /* ═══ Rounded input fields ═══ */
    Input {
        background: $panel;
        border: round $boost;
        padding: 0 1;
    }

    Input:focus {
        border: round $primary;
    }

    /* ═══ Rounded list views ═══ */
    ListView {
        background: $panel;
        border: round $boost;
    }

    ListView:focus {
        border: round $primary;
    }

    /* ═══ Rounded containers ═══ */
    VerticalScroll {
        border: round $boost;
    }

    VerticalScroll:focus {
        border: round $primary;
    }

    /* ═══ Elegant scrollbars ═══ */
    Scrollbar {
        background: $panel;
    }

    ScrollbarGripper {
        background: $boost;
    }

    ScrollbarGripper:hover {
        background: $primary;
    }

    /* ═══ Tree widget styling ═══ */
    Tree {
        background: $panel;
        border: round $boost;
    }

    Tree:focus {
        border: round $primary;
    }

    /* ═══ Text Area styling ═══ */
    TextArea {
        background: $panel;
        border: round $boost;
    }

    TextArea:focus {
        border: round $primary;
    }

    /* ═══ Rule/Divider styling ═══ */
    Rule {
        color: $boost;
        margin: 1 0;
    }

    /* ═══ Modal screens ═══ */
    ModalScreen {
        background: rgba(12, 18, 34, 0.85);
    }
"""

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("question_mark", "show_help", "Help"),
        Binding("slash", "focus_search", "Search"),
        Binding("1", "switch_tab('dashboard')", "Dashboard", show=False),
        Binding("2", "switch_tab('memories')", "Memories", show=False),
        Binding("3", "switch_tab('threads')", "Threads", show=False),
        Binding("4", "switch_tab('graph')", "Graph", show=False),
        Binding("5", "switch_tab('settings')", "Settings", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.api_client = ApiClient()
        self.register_theme(NOWLEDGE_THEME)
        self.theme = "nowledge"

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="dashboard"):
            with TabPane("◈ Dashboard", id="dashboard"):
                yield DashboardScreen(api_client=self.api_client)
            with TabPane("◇ Memories", id="memories"):
                yield MemoriesScreen(api_client=self.api_client)
            with TabPane("◇ Threads", id="threads"):
                yield ThreadsScreen(api_client=self.api_client)
            with TabPane("◇ Graph", id="graph"):
                yield GraphScreen(api_client=self.api_client)
            with TabPane("◇ Settings", id="settings"):
                yield SettingsScreen(api_client=self.api_client)
        yield Footer()

    async def on_unmount(self) -> None:
        await self.api_client.close()

    def action_switch_tab(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id

    def action_show_help(self) -> None:
        from .screens.help import HelpScreen

        self.push_screen(HelpScreen())

    def action_focus_search(self) -> None:
        try:
            active = self.query_one(TabbedContent).active
            if active == "memories":
                self.query_one(MemoriesScreen).focus_search()
            elif active == "threads":
                self.query_one(ThreadsScreen).focus_search()
            elif active == "graph":
                self.query_one(GraphScreen).focus_search()
            else:
                self.action_switch_tab("memories")
                self.call_after_refresh(
                    lambda: self.query_one(MemoriesScreen).focus_search()
                )
        except Exception:
            pass


def main() -> None:
    app = NowledgeMemApp()
    app.run()


if __name__ == "__main__":
    main()
