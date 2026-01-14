"""
Threads Screen - List, search, and manage conversation threads.
"""

from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Label, ListItem, ListView, Static

from ..api_client import ApiClient


class ThreadItem(ListItem):
    """A styled thread item in the list."""

    DEFAULT_CSS = """
    ThreadItem {
        padding: 1 2;
        height: auto;
        border-bottom: solid $boost;
    }

    ThreadItem:hover {
        background: $boost;
    }

    ThreadItem.-highlight {
        background: $primary-darken-2;
    }

    ThreadItem > Horizontal {
        height: auto;
    }

    ThreadItem .status {
        width: 3;
        color: $success;
    }

    ThreadItem .status-pending {
        color: $warning;
    }

    ThreadItem .msgs {
        width: 10;
        color: $secondary;
    }

    ThreadItem .date {
        width: 12;
        color: $text-muted;
    }

    ThreadItem .title {
        width: 1fr;
        color: $primary;
        text-style: bold;
    }

    ThreadItem .source {
        color: $text-muted;
        padding-left: 25;
    }
    """

    def __init__(self, thread: dict[str, Any]) -> None:
        super().__init__()
        self.thread = thread
        self.thread_id = str(thread.get("id", thread.get("thread_id", "")))

    def compose(self) -> ComposeResult:
        title = str(self.thread.get("title", "Untitled Thread"))[:50]
        msgs = self.thread.get("messages", self.thread.get("message_count", 0))
        if not isinstance(msgs, int):
            msgs = 0
        date = str(self.thread.get("date", self.thread.get("created_at", "")))[:10]
        source = str(self.thread.get("source", ""))[:20]
        status = str(self.thread.get("distillation_status", "pending"))

        # Modern status indicators
        status_icon = "◆" if status == "completed" else "◇"
        status_class = "status" if status == "completed" else "status status-pending"

        with Horizontal():
            yield Label(status_icon, classes=status_class)
            yield Label(f"{msgs:>3} msgs", classes="msgs")
            yield Label(date, classes="date")
            yield Label(title, classes="title")
        if source:
            yield Label(source, classes="source")


class ThreadsScreen(Vertical):
    """Screen for browsing and searching threads."""

    DEFAULT_CSS = """
    ThreadsScreen {
        padding: 1 2;
    }

    ThreadsScreen > #header {
        height: 1;
        color: $secondary;
        margin-bottom: 1;
    }

    ThreadsScreen > #search-input {
        margin-bottom: 1;
        border: round $boost;
        background: $panel;
    }

    ThreadsScreen > #search-input:focus {
        border: round $primary;
    }

    ThreadsScreen > #thread-list {
        height: 1fr;
        border: round $boost;
        background: $panel;
    }

    ThreadsScreen > #thread-list:focus {
        border: round $primary;
    }

    ThreadsScreen > #status-bar {
        height: 1;
        color: $text-muted;
        background: $panel;
        padding: 0 1;
        border: round $boost;
    }
    """

    BINDINGS = [
        Binding("d", "distill", "Distill"),
        Binding("x", "delete", "Delete"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, api_client: ApiClient, **kwargs) -> None:
        super().__init__(**kwargs)
        self.api_client = api_client
        self.threads: list[dict[str, Any]] = []
        self._loading = False

    def compose(self) -> ComposeResult:
        yield Static("◈ THREADS │ d:distill  x:delete  r:refresh", id="header")
        yield Input(
            placeholder="Search threads (press / to focus)...", id="search-input"
        )
        yield ListView(id="thread-list")
        yield Static("Loading...", id="status-bar")

    def on_mount(self) -> None:
        self.run_worker(self._load(), exclusive=True, thread=False)

    async def _load(self) -> None:
        if self._loading:
            return
        self._loading = True

        try:
            status = self.query_one("#status-bar", Static)
            thread_list = self.query_one("#thread-list", ListView)

            status.update("Fetching threads...")
            data = await self.api_client.list_threads(limit=50)
            threads = data.get("threads", [])
            total = data.get("pagination", {}).get("total", len(threads))

            self.threads = threads
            thread_list.clear()

            if threads:
                for t in threads:
                    thread_list.append(ThreadItem(t))
                status.update(
                    f"{len(threads)} of {total} threads | Enter:view  /:search"
                )
            else:
                status.update("No threads found")
        except Exception as e:
            self.query_one("#status-bar", Static).update(f"Error: {e}")
        finally:
            self._loading = False

    @on(Input.Submitted, "#search-input")
    def on_search(self, event: Input.Submitted) -> None:
        self.run_worker(self._search(event.value), exclusive=True, thread=False)

    async def _search(self, query: str) -> None:
        if self._loading:
            return
        self._loading = True

        try:
            status = self.query_one("#status-bar", Static)
            thread_list = self.query_one("#thread-list", ListView)

            status.update("Searching...")

            if query:
                data = await self.api_client.search_threads(query, limit=50)
            else:
                data = await self.api_client.list_threads(limit=50)

            threads = data.get("threads", [])
            self.threads = threads
            thread_list.clear()

            for t in threads:
                thread_list.append(ThreadItem(t))

            status.update(f"Found {len(threads)} threads")
        except Exception as e:
            self.query_one("#status-bar", Static).update(f"Error: {e}")
        finally:
            self._loading = False

    @on(ListView.Selected, "#thread-list")
    def on_select(self, event: ListView.Selected) -> None:
        if isinstance(event.item, ThreadItem) and event.item.thread_id:
            from .thread_detail import ThreadDetailScreen

            self.app.push_screen(
                ThreadDetailScreen(
                    thread_id=event.item.thread_id,
                    api_client=self.api_client,
                )
            )

    def action_distill(self) -> None:
        self.notify("Distill not yet implemented", severity="warning")

    def action_delete(self) -> None:
        self.notify("Delete not yet implemented", severity="warning")

    def action_refresh(self) -> None:
        self.run_worker(self._load(), exclusive=True, thread=False)

    def focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()
