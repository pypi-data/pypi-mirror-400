"""
Graph Screen - Knowledge graph visualization.
"""

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Input, Static, Tree

from ..api_client import ApiClient

# Node type icons
NODE_ICONS = {
    "PERSON": "👤",
    "ORGANIZATION": "🏢",
    "LOCATION": "📍",
    "EVENT": "📅",
    "CONCEPT": "💡",
    "ENTITY": "◆",
    "MEMORY": "📝",
    "THREAD": "💬",
}


class GraphScreen(Vertical):
    """Screen for viewing the knowledge graph."""

    DEFAULT_CSS = """
    GraphScreen {
        padding: 1 2;
    }

    GraphScreen > #header {
        height: 1;
        color: $secondary;
        margin-bottom: 1;
    }

    GraphScreen > #search-input {
        margin-bottom: 1;
        border: round $boost;
        background: $panel;
    }

    GraphScreen > #search-input:focus {
        border: round $primary;
    }

    GraphScreen > #stats {
        height: 1;
        color: $secondary;
        background: $panel;
        padding: 0 1;
        margin-bottom: 1;
        border: round $boost;
    }

    GraphScreen > #graph-tree {
        height: 1fr;
        border: round $boost;
        background: $panel;
        padding: 1;
    }

    GraphScreen > #graph-tree:focus {
        border: round $primary;
    }

    GraphScreen > #status-bar {
        height: 1;
        color: $text-muted;
        background: $panel;
        padding: 0 1;
        border: round $boost;
    }

    GraphScreen Tree {
        background: transparent;
    }
    """

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("e", "expand_all", "Expand All"),
        Binding("c", "collapse_all", "Collapse All"),
    ]

    def __init__(self, api_client: ApiClient, **kwargs) -> None:
        super().__init__(**kwargs)
        self.api_client = api_client
        self._loading = False

    def compose(self) -> ComposeResult:
        yield Static("◈ KNOWLEDGE GRAPH │ r:refresh  e:expand  c:collapse", id="header")
        yield Input(placeholder="◎ Search entities...", id="search-input")
        yield Static("◎ Loading graph...", id="stats")
        yield Tree("◆ Knowledge Graph", id="graph-tree")
        yield Static("Loading...", id="status-bar")

    def on_mount(self) -> None:
        self.run_worker(self._load(), exclusive=True, thread=False)

    async def _load(self, query: str = "") -> None:
        if self._loading:
            return
        self._loading = True

        try:
            status = self.query_one("#status-bar", Static)
            stats = self.query_one("#stats", Static)
            tree = self.query_one("#graph-tree", Tree)

            status.update("● Fetching graph data...")

            if query:
                data = await self.api_client.search_graph(query)
            else:
                data = await self.api_client.get_graph_sample(limit=100)

            nodes = data.get("nodes", [])
            edges = data.get("edges", [])
            communities = data.get("communities", [])

            stats.update(
                f"◎ {len(nodes)} entities │ {len(edges)} relationships │ {len(communities)} communities"
            )

            # Clear and rebuild tree
            tree.clear()
            tree.root.expand()

            if nodes:
                # Group nodes by type
                by_type: dict[str, list[dict]] = {}
                for n in nodes:
                    ntype = str(n.get("node_type", "entity")).upper()
                    if ntype not in by_type:
                        by_type[ntype] = []
                    by_type[ntype].append(n)

                # Build tree structure
                for ntype in sorted(by_type.keys()):
                    type_nodes = by_type[ntype]
                    icon = NODE_ICONS.get(ntype, "◆")
                    type_branch = tree.root.add(
                        f"{icon} {ntype} ({len(type_nodes)})", expand=True
                    )

                    for n in type_nodes[:20]:
                        label = str(n.get("label", "?"))
                        node_id = n.get("id", "")

                        # Find connections for this node
                        connections = []
                        for e in edges:
                            if e.get("source") == node_id:
                                target_label = next(
                                    (
                                        nd.get("label", "?")
                                        for nd in nodes
                                        if nd.get("id") == e.get("target")
                                    ),
                                    "?",
                                )
                                rel = e.get("relationship", "relates_to")
                                connections.append(f"─▶ {rel} ─▶ {target_label}")
                            elif e.get("target") == node_id:
                                source_label = next(
                                    (
                                        nd.get("label", "?")
                                        for nd in nodes
                                        if nd.get("id") == e.get("source")
                                    ),
                                    "?",
                                )
                                rel = e.get("relationship", "relates_to")
                                connections.append(f"◀── {rel} ◀── {source_label}")

                        # Add node with connections
                        if connections:
                            node_branch = type_branch.add(f"● {label}", expand=False)
                            for conn in connections[:5]:
                                node_branch.add_leaf(f"  {conn}")
                            if len(connections) > 5:
                                node_branch.add_leaf(
                                    f"  ... +{len(connections) - 5} more"
                                )
                        else:
                            type_branch.add_leaf(f"○ {label}")

                    if len(type_nodes) > 20:
                        type_branch.add_leaf(f"... +{len(type_nodes) - 20} more")

                status.update(
                    f"● Loaded {len(nodes)} entities │ /:search  Enter:expand/collapse"
                )
            else:
                tree.root.add_leaf("No entities found")
                status.update("○ No graph data")

        except Exception as e:
            self.query_one("#status-bar", Static).update(f"✗ Error: {e}")
        finally:
            self._loading = False

    @on(Input.Submitted, "#search-input")
    def on_search(self, event: Input.Submitted) -> None:
        self.run_worker(self._load(event.value), exclusive=True, thread=False)

    def action_refresh(self) -> None:
        self.run_worker(self._load(), exclusive=True, thread=False)

    def action_expand_all(self) -> None:
        tree = self.query_one("#graph-tree", Tree)
        for node in tree.root.children:
            node.expand()

    def action_collapse_all(self) -> None:
        tree = self.query_one("#graph-tree", Tree)
        for node in tree.root.children:
            node.collapse()

    def focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()
