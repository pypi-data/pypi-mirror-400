"""
Memories Screen - List, search, and manage memories.
"""

from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListItem, ListView, Static, TextArea

from ..api_client import ApiClient

# Try to import pyperclip, but make it optional
try:
    import pyperclip

    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False


class MemoryItem(ListItem):
    """A styled memory item in the list."""

    DEFAULT_CSS = """
    MemoryItem {
        padding: 1 2;
        height: auto;
        border-bottom: solid $boost;
    }

    MemoryItem:hover {
        background: $boost;
    }

    MemoryItem.-highlight {
        background: $primary-darken-2;
    }

    MemoryItem > Horizontal {
        height: auto;
    }

    MemoryItem .importance {
        width: 8;
        color: $secondary;
    }

    MemoryItem .date {
        width: 12;
        color: $text-muted;
    }

    MemoryItem .title {
        width: 1fr;
        color: $primary;
        text-style: bold;
    }

    MemoryItem .preview {
        color: $text-muted;
        padding-left: 20;
    }
"""

    def __init__(self, memory: dict[str, Any]) -> None:
        super().__init__()
        self.memory = memory
        self.memory_id = str(memory.get("id", ""))

    def compose(self) -> ComposeResult:
        title = str(self.memory.get("title", "Untitled"))[:50]
        importance = self.memory.get("importance", 0.5)
        if not isinstance(importance, int | float):
            importance = 0.5
        date = str(self.memory.get("created_at", ""))[:10]
        content = str(self.memory.get("content", ""))
        preview = content[:60].replace("\n", " ") if content else ""

        # Importance as modern bar indicator
        filled = int(importance * 5)
        stars = "▰" * filled + "▱" * (5 - filled)

        with Horizontal():
            yield Label(stars, classes="importance")
            yield Label(date, classes="date")
            yield Label(title, classes="title")
        if preview:
            yield Label(f"{preview}...", classes="preview")


class EditMemoryScreen(ModalScreen):
    """Modal screen for editing a memory."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    DEFAULT_CSS = """
    EditMemoryScreen {
        align: center middle;
    }

    EditMemoryScreen > Vertical {
        width: 80%;
        height: 80%;
        background: $surface;
        border: round $primary;
        padding: 1 2;
    }

    EditMemoryScreen .modal-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 1;
    }

    EditMemoryScreen .field-label {
        margin-top: 1;
        color: $secondary;
    }

    EditMemoryScreen #title-input {
        margin-bottom: 1;
        border: round $boost;
    }

    EditMemoryScreen #title-input:focus {
        border: round $primary;
    }

    EditMemoryScreen #content-area {
        height: 1fr;
        border: round $boost;
    }

    EditMemoryScreen #content-area:focus {
        border: round $primary;
    }

    EditMemoryScreen .hint {
        color: $text-muted;
        text-align: center;
        margin-top: 1;
    }
"""

    def __init__(self, memory: dict[str, Any], api_client: ApiClient) -> None:
        super().__init__()
        self.memory = memory
        self.api_client = api_client

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("EDIT MEMORY", classes="modal-title")
            yield Static("Title:", classes="field-label")
            yield Input(value=str(self.memory.get("title", "")), id="title-input")
            yield Static("Content:", classes="field-label")
            yield TextArea(str(self.memory.get("content", "")), id="content-area")
            yield Static("Ctrl+S: Save  |  Esc: Cancel", classes="hint")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_save(self) -> None:
        title = self.query_one("#title-input", Input).value
        content = self.query_one("#content-area", TextArea).text
        self.dismiss({"title": title, "content": content})


class MemoriesScreen(Vertical):
    """Screen for browsing and searching memories."""

    DEFAULT_CSS = """
    MemoriesScreen {
        padding: 1 2;
    }

    MemoriesScreen > #header {
        height: 1;
        color: $secondary;
        margin-bottom: 1;
    }

    MemoriesScreen > #search-input {
        margin-bottom: 1;
        border: round $boost;
        background: $panel;
    }

    MemoriesScreen > #search-input:focus {
        border: round $primary;
    }

    MemoriesScreen > #memory-list {
        height: 1fr;
        border: round $boost;
        background: $panel;
    }

    MemoriesScreen > #memory-list:focus {
        border: round $primary;
    }

    MemoriesScreen > #status-bar {
        height: 1;
        color: $text-muted;
        background: $panel;
        padding: 0 1;
        border: round $boost;
    }
"""

    BINDINGS = [
        Binding("a", "add", "Add"),
        Binding("e", "edit", "Edit"),
        Binding("c", "copy", "Copy"),
        Binding("d", "delete", "Delete"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, api_client: ApiClient, **kwargs) -> None:
        super().__init__(**kwargs)
        self.api_client = api_client
        self.memories: list[dict[str, Any]] = []
        self._loading = False

    def compose(self) -> ComposeResult:
        yield Static(
            "◈ MEMORIES │ a:add  e:edit  c:copy  d:delete  r:refresh", id="header"
        )
        yield Input(
            placeholder="Search memories (press / to focus)...", id="search-input"
        )
        yield ListView(id="memory-list")
        yield Static("Loading...", id="status-bar")

    def on_mount(self) -> None:
        self.run_worker(self._load(), exclusive=True, thread=False)

    async def _load(self) -> None:
        if self._loading:
            return
        self._loading = True

        try:
            status = self.query_one("#status-bar", Static)
            memory_list = self.query_one("#memory-list", ListView)

            status.update("Fetching memories...")
            data = await self.api_client.list_memories(limit=50, offset=0)
            memories = data.get("memories", [])
            total = data.get("pagination", {}).get("total", len(memories))

            self.memories = memories
            memory_list.clear()

            if memories:
                for mem in memories:
                    memory_list.append(MemoryItem(mem))
                status.update(
                    f"{len(memories)} of {total} memories | Enter:view  c:copy  /:search"
                )
            else:
                status.update("No memories found")
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
            memory_list = self.query_one("#memory-list", ListView)

            status.update("Searching...")

            if query:
                data = await self.api_client.search_memories(query, limit=50)
            else:
                data = await self.api_client.list_memories(limit=50)

            memories = data.get("memories", [])
            self.memories = memories
            memory_list.clear()

            for mem in memories:
                memory_list.append(MemoryItem(mem))

            status.update(f"Found {len(memories)} memories")
        except Exception as e:
            self.query_one("#status-bar", Static).update(f"Error: {e}")
        finally:
            self._loading = False

    @on(ListView.Selected, "#memory-list")
    def on_select(self, event: ListView.Selected) -> None:
        if isinstance(event.item, MemoryItem) and event.item.memory_id:
            from .memory_detail import MemoryDetailScreen

            self.app.push_screen(
                MemoryDetailScreen(
                    memory_id=event.item.memory_id,
                    api_client=self.api_client,
                )
            )

    def action_add(self) -> None:
        self.notify("Add memory not yet implemented", severity="warning")

    def action_edit(self) -> None:
        memory_list = self.query_one("#memory-list", ListView)
        if memory_list.highlighted_child and isinstance(
            memory_list.highlighted_child, MemoryItem
        ):
            memory = memory_list.highlighted_child.memory
            self.app.push_screen(
                EditMemoryScreen(memory, self.api_client),
                callback=self._on_edit_complete,
            )
        else:
            self.notify("Select a memory first", severity="warning")

    def action_copy(self) -> None:
        """Copy selected memory content to clipboard."""
        if not HAS_CLIPBOARD:
            self.notify("Clipboard not available", severity="warning")
            return
        memory_list = self.query_one("#memory-list", ListView)
        if memory_list.highlighted_child and isinstance(
            memory_list.highlighted_child, MemoryItem
        ):
            content = str(memory_list.highlighted_child.memory.get("content", ""))
            if content:
                try:
                    pyperclip.copy(content)
                    self.notify("Content copied!", severity="information")
                except Exception:
                    self.notify("Copy failed", severity="warning")
        else:
            self.notify("Select a memory first", severity="warning")

    def _on_edit_complete(self, result: dict | None) -> None:
        if result:
            self.run_worker(self._save_edit(result), exclusive=True, thread=False)

    async def _save_edit(self, result: dict) -> None:
        try:
            memory_list = self.query_one("#memory-list", ListView)
            if memory_list.highlighted_child and isinstance(
                memory_list.highlighted_child, MemoryItem
            ):
                memory_id = memory_list.highlighted_child.memory_id
                await self.api_client.update_memory(
                    memory_id,
                    title=result.get("title"),
                    content=result.get("content"),
                )
                self.notify("Memory updated!", severity="information")
                await self._load()
        except Exception as e:
            self.notify(f"Failed to save: {e}", severity="error")

    def action_delete(self) -> None:
        self.notify("Delete not yet implemented", severity="warning")

    def action_refresh(self) -> None:
        self.run_worker(self._load(), exclusive=True, thread=False)

    def focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()
