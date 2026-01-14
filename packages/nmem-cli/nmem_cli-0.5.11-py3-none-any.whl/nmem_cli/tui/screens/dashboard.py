"""
Dashboard Screen - Overview and statistics with animated logo.
"""

from rich.style import Style
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from ..api_client import ApiClient

# Gradient color palette for animation (teal -> cyan -> purple -> back)
GRADIENT_COLORS = [
    "#06B6D4",  # Cyan-500
    "#22D3EE",  # Cyan-400
    "#67E8F9",  # Cyan-300
    "#A5F3FC",  # Cyan-200
    "#C4B5FD",  # Violet-300
    "#A78BFA",  # Violet-400
    "#8B5CF6",  # Violet-500
    "#A78BFA",  # Violet-400
    "#C4B5FD",  # Violet-300
    "#A5F3FC",  # Cyan-200
    "#67E8F9",  # Cyan-300
    "#22D3EE",  # Cyan-400
]

# Logo ASCII art lines (for per-line gradient coloring)
LOGO_LINES = [
    "         ▄▄▄▄████████████████▄▄▄▄",
    "        ▄█▀░░░░░░░░░░░░░░░░░░░░░░▀█▄",
    "      ▄█░░░░▄████████████████▄░░░░░█▄",
    "      █░░░██░  ✦     ✦     ✦  ░██░░░█",
    "      █░░██░    ╭─────────╮    ░██░░█",
    "      █░░██░  ✦ │  ∿∿∿∿∿  │ ✦  ░██░░█",
    "      █░░██░    ╰─────────╯    ░██░░█",
    "      █░░░██░  ✦     ✦     ✦  ░██░░░█",
    "      ▀█░░░▀████████████████▀░░░░█▀",
    "        ▀█▄░░░░░░░░░░░░░░░░░░░▄█▀",
    "          ▀▀████████████████▀▀",
    "                ████████",
]


class AnimatedLogo(Static):
    """Logo with animated gradient color cycling."""

    DEFAULT_CSS = """
    AnimatedLogo {
        text-align: center;
        height: 14;
        content-align: center middle;
    }
"""

    def __init__(self) -> None:
        super().__init__("")
        self._frame = 0

    def on_mount(self) -> None:
        self._render_logo()
        self.set_interval(0.15, self._animate)

    def _animate(self) -> None:
        self._frame = (self._frame + 1) % len(GRADIENT_COLORS)
        self._render_logo()

    def _render_logo(self) -> None:
        """Render logo with gradient colors per line."""
        text = Text()
        for i, line in enumerate(LOGO_LINES):
            # Offset color index for each line to create wave effect
            color_idx = (self._frame + i) % len(GRADIENT_COLORS)
            color = GRADIENT_COLORS[color_idx]
            text.append(line + "\n", style=Style(color=color))
        self.update(text)


class AnimatedTitle(Static):
    """Title with subtle glow animation."""

    DEFAULT_CSS = """
    AnimatedTitle {
        text-align: center;
        text-style: bold;
        height: 1;
    }
"""

    TITLE_TEXT = "N O W L E D G E   M E M"

    def __init__(self) -> None:
        super().__init__("")
        self._frame = 0

    def on_mount(self) -> None:
        self._render_title()
        self.set_interval(0.1, self._animate)

    def _animate(self) -> None:
        self._frame = (self._frame + 1) % len(GRADIENT_COLORS)
        self._render_title()

    def _render_title(self) -> None:
        """Render title with gradient effect across characters."""
        text = Text()
        chars = list(self.TITLE_TEXT)
        for i, char in enumerate(chars):
            color_idx = (self._frame + i) % len(GRADIENT_COLORS)
            color = GRADIENT_COLORS[color_idx]
            text.append(char, style=Style(color=color, bold=True))
        self.update(text)


class StatCard(Vertical):
    """A styled stat card with rounded aesthetic."""

    DEFAULT_CSS = """
    StatCard {
        width: 1fr;
        height: 7;
        background: $panel;
        border: round $boost;
        margin: 0 1;
        padding: 1;
    }

    StatCard:first-child {
        margin-left: 0;
    }

    StatCard:last-child {
        margin-right: 0;
    }

    StatCard > .value {
        text-style: bold;
        text-align: center;
        width: 100%;
        color: $primary;
    }

    StatCard > .label {
        text-align: center;
        width: 100%;
        color: $text-muted;
    }
"""

    def __init__(self, label: str, value: str = "--", **kwargs) -> None:
        super().__init__(**kwargs)
        self._label = label
        self._value = value

    def compose(self) -> ComposeResult:
        yield Static(self._value, classes="value", id=f"val-{self._label}")
        yield Static(self._label, classes="label")

    def set_value(self, value: str) -> None:
        try:
            self.query_one(f"#val-{self._label}", Static).update(value)
        except Exception:
            pass


class DashboardScreen(Vertical):
    """Dashboard screen showing overview and statistics."""

    DEFAULT_CSS = """
    DashboardScreen {
        padding: 1 2;
    }

    DashboardScreen > #tagline {
        text-align: center;
        color: $secondary;
        margin-bottom: 1;
    }

    DashboardScreen > #status {
        color: $text-muted;
        text-align: center;
    }

    DashboardScreen > #stats-row {
        height: 9;
        margin: 1 0;
    }

    DashboardScreen > #recent-title {
        text-style: bold;
        color: $secondary;
        margin-top: 1;
    }

    DashboardScreen > #recent-section {
        height: 1fr;
        border: round $boost;
        background: $panel;
        padding: 1;
    }

    DashboardScreen > #shortcuts {
        color: $text-muted;
        text-align: center;
        padding: 1;
        background: $panel;
        border: round $boost;
    }
"""

    def __init__(self, api_client: ApiClient, **kwargs) -> None:
        super().__init__(**kwargs)
        self.api_client = api_client
        self._loaded = False

    def compose(self) -> ComposeResult:
        yield AnimatedLogo()
        yield AnimatedTitle()
        yield Static("AI that remembers your world", id="tagline")
        yield Static("Connecting...", id="status")
        yield Horizontal(
            StatCard("Memories", "--"),
            StatCard("Entities", "--"),
            StatCard("Threads", "--"),
            StatCard("Status", "--"),
            id="stats-row",
        )
        yield Static("◈ Recent Activity", id="recent-title")
        yield Static("Loading...", id="recent-section")
        yield Static(
            "1:Dashboard  2:Memories  3:Threads  4:Graph  5:Settings  ?:Help  q:Quit",
            id="shortcuts",
        )

    def on_mount(self) -> None:
        if not self._loaded:
            self.run_worker(self._load(), exclusive=True, thread=False)

    async def _load(self) -> None:
        status = self.query_one("#status", Static)

        try:
            status.update("● Connecting to server...")
            health = await self.api_client.get_health()

            if health.get("status") == "offline" or health.get("error"):
                status.update(f"○ Offline: {health.get('error', 'Cannot connect')}")
                return

            status.update("● Loading statistics...")
            stats = await self.api_client.get_stats()

            # Update stat cards
            cards = list(self.query(StatCard))
            if len(cards) >= 4:
                cards[0].set_value(str(stats.get("memory_count", 0)))
                cards[1].set_value(str(stats.get("entity_count", 0)))
                cards[2].set_value(str(stats.get("thread_count", 0)))
                cards[3].set_value("● Online")

            # Load recent memories
            status.update("● Loading recent activity...")
            data = await self.api_client.list_memories(limit=8)
            memories = data.get("memories", [])

            recent = self.query_one("#recent-section", Static)
            if memories:
                lines = []
                for m in memories:
                    title = str(m.get("title", "Untitled"))[:40]
                    imp = m.get("importance", 0.5)
                    if not isinstance(imp, int | float):
                        imp = 0.5
                    date = str(m.get("created_at", ""))[:10]
                    # Modern bar indicator for importance
                    filled = int(imp * 5)
                    bar = "▰" * filled + "▱" * (5 - filled)
                    lines.append(f"  {bar}  {date}  {title}")
                recent.update("\n".join(lines))
            else:
                recent.update(
                    "  No memories yet.\n\n  Press 2 to go to Memories and create some!"
                )

            status.update("● Ready")
            self._loaded = True

        except Exception as e:
            status.update(f"✗ Error: {e}")
