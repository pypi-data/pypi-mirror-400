"""
Memory Detail Screen - View and edit a single memory.
"""

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Footer, Input, Rule, Static, TextArea

from ..api_client import ApiClient

# Try to import pyperclip, but make it optional
try:
    import pyperclip

    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False


class EditMemoryModal(ModalScreen):
    """Modal screen for editing a memory."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    DEFAULT_CSS = """
    EditMemoryModal {
        align: center middle;
    }

    EditMemoryModal > Vertical {
        width: 80%;
        height: 80%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    EditMemoryModal .modal-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 1;
    }

    EditMemoryModal .field-label {
        margin-top: 1;
        color: $secondary;
    }

    EditMemoryModal #title-input {
        margin-bottom: 1;
        border: solid $boost;
    }

    EditMemoryModal #title-input:focus {
        border: solid $primary;
    }

    EditMemoryModal #content-area {
        height: 1fr;
        border: solid $boost;
    }

    EditMemoryModal #content-area:focus {
        border: solid $primary;
    }

    EditMemoryModal .hint {
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
            yield Rule()
            yield Static("Title:", classes="field-label")
            yield Input(value=self.memory.get("title", ""), id="title-input")
            yield Static("Content:", classes="field-label")
            yield TextArea(self.memory.get("content", ""), id="content-area")
            yield Static("Ctrl+S: Save  |  Esc: Cancel", classes="hint")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_save(self) -> None:
        title = self.query_one("#title-input", Input).value
        content = self.query_one("#content-area", TextArea).text
        self.dismiss({"title": title, "content": content})


class MemoryDetailScreen(Screen):
    """Screen for viewing memory details."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("e", "edit", "Edit"),
        Binding("c", "copy", "Copy Content"),
        Binding("y", "copy_id", "Copy ID"),
        Binding("d", "delete", "Delete"),
    ]

    DEFAULT_CSS = """
    MemoryDetailScreen {
        background: $surface;
    }

    MemoryDetailScreen > Vertical {
        padding: 1 2;
    }

    MemoryDetailScreen .title {
        text-style: bold;
        color: $primary;
    }

    MemoryDetailScreen .section {
        text-style: bold;
        color: $secondary;
        margin-top: 1;
    }

    MemoryDetailScreen .meta {
        color: $text-muted;
        padding-left: 2;
    }

    MemoryDetailScreen #content-scroll {
        height: 1fr;
        border: round $boost;
        background: $panel;
        padding: 1;
    }

    MemoryDetailScreen #content-scroll:focus {
        border: round $primary;
    }

    MemoryDetailScreen .hint {
        color: $text-muted;
        text-align: center;
        padding: 1;
        background: $panel;
    }
    """

    def __init__(self, memory_id: str, api_client: ApiClient, **kwargs) -> None:
        super().__init__(**kwargs)
        self.memory_id = memory_id
        self.api_client = api_client
        self.memory: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Loading memory...", id="loading")
        yield Footer()

    def on_mount(self) -> None:
        """Load memory data when mounted."""
        self.run_worker(self._load_memory(), exclusive=True, thread=False)

    async def _load_memory(self) -> None:
        """Load memory details from API."""
        try:
            self.memory = await self.api_client.get_memory(self.memory_id)

            container = self.query_one(Vertical)
            await container.remove_children()

            # Title
            title = self.memory.get("title", "Untitled Memory")
            await container.mount(Static(title, classes="title"))
            await container.mount(Rule())

            # Metadata section
            await container.mount(Static("◇ METADATA", classes="section"))

            memory_id = self.memory.get("id", "")
            await container.mount(Static(f"  ID: {memory_id[:30]}...", classes="meta"))

            importance = self.memory.get("importance", 0.5)
            if not isinstance(importance, int | float):
                importance = 0.5
            bar = "▰" * int(importance * 10) + "▱" * (10 - int(importance * 10))
            await container.mount(
                Static(f"  Importance: {bar} {importance:.0%}", classes="meta")
            )

            created = self.memory.get("created_at", "Unknown")[:19]
            await container.mount(Static(f"  Created: {created}", classes="meta"))

            source = self.memory.get("source", "Unknown")
            await container.mount(Static(f"  Source: {source}", classes="meta"))

            labels = self.memory.get("labels", [])
            if labels:
                label_names = []
                for label in labels[:5]:
                    if isinstance(label, dict):
                        label_names.append(f"#{label.get('name', 'tag')}")
                    else:
                        label_names.append(f"#{label}")
                await container.mount(
                    Static(f"  Labels: {' '.join(label_names)}", classes="meta")
                )

            # Content section
            await container.mount(Static("◇ CONTENT", classes="section"))
            content = self.memory.get("content", "No content")
            scroll = VerticalScroll(id="content-scroll")
            await container.mount(scroll)
            await scroll.mount(Static(content, markup=False))

            # Entities if available
            entities = self.memory.get("entities", [])
            if entities:
                entity_names = []
                for e in entities[:10]:
                    if isinstance(e, dict):
                        entity_names.append(e.get("name", "?"))
                    else:
                        entity_names.append(str(e))
                await container.mount(Static("◇ ENTITIES", classes="section"))
                await container.mount(
                    Static(f"  {', '.join(entity_names)}", classes="meta")
                )

            # Hint
            await container.mount(
                Static("e:Edit  c:Copy  y:Copy ID  Esc:Back", classes="hint")
            )

        except Exception as e:
            container = self.query_one(Vertical)
            await container.remove_children()
            await container.mount(Static(f"Error loading memory: {e}"))

    def action_edit(self) -> None:
        """Open edit modal."""
        if self.memory:
            self.app.push_screen(
                EditMemoryModal(self.memory, self.api_client),
                callback=self._on_edit_complete,
            )

    def _on_edit_complete(self, result: dict | None) -> None:
        """Handle edit completion."""
        if result:
            self.run_worker(self._save_edit(result), exclusive=True, thread=False)

    async def _save_edit(self, result: dict) -> None:
        """Save the edited memory."""
        try:
            await self.api_client.update_memory(
                self.memory_id,
                title=result.get("title"),
                content=result.get("content"),
            )
            self.notify("Memory updated!", severity="information")
            await self._load_memory()
        except Exception as e:
            self.notify(f"Failed to save: {e}", severity="error")

    def action_copy(self) -> None:
        """Copy memory content to clipboard."""
        content = self.memory.get("content", "")
        if content and HAS_CLIPBOARD:
            try:
                pyperclip.copy(content)
                self.notify("Content copied!", severity="information")
            except Exception:
                self.notify("Copy failed", severity="warning")
        elif not HAS_CLIPBOARD:
            self.notify("Clipboard not available", severity="warning")

    def action_copy_id(self) -> None:
        """Copy memory ID to clipboard."""
        memory_id = self.memory.get("id", "")
        if memory_id and HAS_CLIPBOARD:
            try:
                pyperclip.copy(memory_id)
                self.notify("ID copied!", severity="information")
            except Exception:
                self.notify("Copy failed", severity="warning")
        elif not HAS_CLIPBOARD:
            self.notify("Clipboard not available", severity="warning")

    def action_delete(self) -> None:
        self.notify("Delete not yet implemented", severity="warning")
