"""
Thread Detail Screen - View thread with messages.
"""

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Rule, Static

from ..api_client import ApiClient

# Try to import pyperclip, but make it optional
try:
    import pyperclip

    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False


class ThreadDetailScreen(Screen):
    """Screen for viewing thread details and messages."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("c", "copy", "Copy Message"),
        Binding("y", "copy_all", "Copy All"),
        Binding("d", "distill", "Distill"),
        Binding("x", "delete", "Delete"),
        Binding("j", "scroll_down", "Down", show=False),
        Binding("k", "scroll_up", "Up", show=False),
    ]

    DEFAULT_CSS = """
    ThreadDetailScreen {
        background: $surface;
    }

    ThreadDetailScreen > Vertical {
        padding: 1 2;
    }

    ThreadDetailScreen .title {
        text-style: bold;
        color: $primary;
    }

    ThreadDetailScreen .section {
        text-style: bold;
        color: $secondary;
        margin-top: 1;
    }

    ThreadDetailScreen .meta {
        color: $text-muted;
        padding-left: 2;
    }

    ThreadDetailScreen #messages-scroll {
        height: 1fr;
        border: round $boost;
        background: $panel;
        padding: 1;
        margin-top: 1;
    }

    ThreadDetailScreen #messages-scroll:focus {
        border: round $primary;
    }

    ThreadDetailScreen .user-msg {
        background: $primary-darken-3;
        padding: 1;
        margin-bottom: 1;
        border-left: thick $primary;
    }

    ThreadDetailScreen .assistant-msg {
        background: $boost;
        padding: 1;
        margin-bottom: 1;
        border-left: thick $secondary;
    }

    ThreadDetailScreen .hint {
        color: $text-muted;
        text-align: center;
        padding: 1;
        background: $panel;
    }
    """

    def __init__(self, thread_id: str, api_client: ApiClient, **kwargs) -> None:
        super().__init__(**kwargs)
        self.thread_id = thread_id
        self.api_client = api_client
        self.thread: dict[str, Any] = {}
        self.messages: list[dict[str, Any]] = []
        self._all_content: str = ""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Loading thread...", id="loading")
        yield Footer()

    def on_mount(self) -> None:
        """Load thread data when mounted."""
        self.run_worker(self._load_thread(), exclusive=True, thread=False)

    async def _load_thread(self) -> None:
        """Load thread details from API."""
        try:
            data = await self.api_client.get_thread(self.thread_id)
            self.thread = data.get("thread", data)  # Handle both wrapped and unwrapped
            self.messages = data.get("messages", [])

            container = self.query_one(Vertical)
            await container.remove_children()

            # Title
            title = str(self.thread.get("title", "Untitled Thread"))
            await container.mount(Static(title, classes="title"))
            await container.mount(Rule())

            # Metadata
            msg_count = len(self.messages)
            source = str(self.thread.get("source", "Unknown"))
            status = str(self.thread.get("distillation_status", "pending"))
            status_icon = "◆" if status == "completed" else "◇"
            thread_id = str(self.thread_id)[:20]

            await container.mount(Static("◇ METADATA", classes="section"))
            await container.mount(Static(f"  ID: {thread_id}...", classes="meta"))
            await container.mount(Static(f"  Messages: {msg_count}", classes="meta"))
            await container.mount(Static(f"  Source: {source}", classes="meta"))
            await container.mount(
                Static(f"  Status: {status_icon} {status}", classes="meta")
            )

            # Messages
            await container.mount(Static("◇ MESSAGES", classes="section"))
            scroll = VerticalScroll(id="messages-scroll")
            await container.mount(scroll)

            # Build full content for copying
            all_content_parts = []

            for msg in self.messages:
                role = str(msg.get("role", "unknown")).upper()
                content = str(msg.get("content", ""))
                display_content = content[:500]
                if len(content) > 500:
                    display_content += "..."

                all_content_parts.append(f"[{role}]\n{content}")

                css_class = "user-msg" if role.lower() == "user" else "assistant-msg"
                await scroll.mount(
                    Static(
                        f"─── {role} ───\n{display_content}",
                        classes=css_class,
                        markup=False,
                    )
                )

            self._all_content = "\n\n".join(all_content_parts)

            # Hint
            await container.mount(
                Static("c:Copy  y:Copy all  d:Distill  Esc:Back", classes="hint")
            )

        except Exception as e:
            container = self.query_one(Vertical)
            await container.remove_children()
            await container.mount(Static(f"Error loading thread: {e}"))

    def action_copy(self) -> None:
        """Copy last message to clipboard."""
        if not HAS_CLIPBOARD:
            self.notify("Clipboard not available", severity="warning")
            return
        if self.messages:
            try:
                content = str(self.messages[-1].get("content", ""))
                pyperclip.copy(content)
                self.notify("Message copied!", severity="information")
            except Exception:
                self.notify("Copy failed", severity="warning")

    def action_copy_all(self) -> None:
        """Copy all messages to clipboard."""
        if not HAS_CLIPBOARD:
            self.notify("Clipboard not available", severity="warning")
            return
        if self._all_content:
            try:
                pyperclip.copy(self._all_content)
                self.notify("All messages copied!", severity="information")
            except Exception:
                self.notify("Copy failed", severity="warning")

    def action_distill(self) -> None:
        self.notify("Distill not yet implemented", severity="warning")

    def action_delete(self) -> None:
        self.notify("Delete not yet implemented", severity="warning")

    def action_scroll_down(self) -> None:
        try:
            self.query_one("#messages-scroll", VerticalScroll).scroll_down()
        except Exception:
            pass

    def action_scroll_up(self) -> None:
        try:
            self.query_one("#messages-scroll", VerticalScroll).scroll_up()
        except Exception:
            pass
