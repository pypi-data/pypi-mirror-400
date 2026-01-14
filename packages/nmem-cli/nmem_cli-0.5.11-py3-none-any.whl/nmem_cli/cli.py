"""
Nowledge Mem CLI - AI agent-friendly memory management.

Aliases:
  m  = memories
  t  = threads
"""

import argparse
import json as json_module
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table

from . import __version__

DEFAULT_API_URL = "http://127.0.0.1:14242"

console = Console()
_json_mode = False


def set_json_mode(enabled: bool) -> None:
    global _json_mode
    _json_mode = enabled


def is_json_mode() -> bool:
    return _json_mode


def output_json(data: Any) -> None:
    print(json_module.dumps(data, indent=2, default=str, ensure_ascii=False))


def get_api_url() -> str:
    return os.environ.get("NMEM_API_URL", DEFAULT_API_URL)


def print_error(title: str, message: str, hint: str | None = None) -> None:
    if is_json_mode():
        return
    console.print(f"[bold red]x[/bold red] [bold]{title}[/bold]")
    console.print(f"  [dim]{message}[/dim]")
    if hint:
        console.print(f"  [dim cyan]Hint: {hint}[/dim cyan]")


def print_success(message: str, detail: str | None = None) -> None:
    if is_json_mode():
        return
    if detail:
        console.print(f"[green]ok[/green] {message}: [cyan]{detail}[/cyan]")
    else:
        console.print(f"[green]ok[/green] {message}")


# ═══════════════════════════════════════════════════════════════════════════════
# API Client
# ═══════════════════════════════════════════════════════════════════════════════


def api_get(endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{get_api_url()}{endpoint}"
    try:
        response = httpx.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        error = {
            "error": "connection_failed",
            "message": f"Cannot connect to {get_api_url()}",
        }
        if is_json_mode():
            output_json(error)
        else:
            print_error(
                "Connection Failed",
                f"Cannot reach {get_api_url()}",
                "Make sure Nowledge Mem is running",
            )
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        error = {"error": "api_error", "status_code": e.response.status_code}
        try:
            error["detail"] = e.response.json().get("detail", "")
        except Exception:
            pass
        if is_json_mode():
            output_json(error)
        else:
            status = e.response.status_code
            if status == 404:
                print_error("Not Found", "Resource doesn't exist", "Check the ID")
            else:
                print_error(
                    f"API Error ({status})", error.get("detail", "Request failed")
                )
        sys.exit(1)


def api_post(endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
    url = f"{get_api_url()}{endpoint}"
    try:
        response = httpx.post(url, json=data, timeout=60.0)
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        error = {
            "error": "connection_failed",
            "message": f"Cannot connect to {get_api_url()}",
        }
        if is_json_mode():
            output_json(error)
        else:
            print_error("Connection Failed", f"Cannot reach {get_api_url()}")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        error = {"error": "api_error", "status_code": e.response.status_code}
        try:
            error["detail"] = e.response.json().get("detail", "")
        except Exception:
            pass
        if is_json_mode():
            output_json(error)
        else:
            print_error(
                f"API Error ({e.response.status_code})",
                error.get("detail", "Request failed"),
            )
        sys.exit(1)


def api_delete(
    endpoint: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    url = f"{get_api_url()}{endpoint}"
    try:
        response = httpx.delete(url, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        error = {"error": "connection_failed", "message": "Cannot connect"}
        if is_json_mode():
            output_json(error)
        else:
            print_error("Connection Failed", "Cannot reach server")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        error = {"error": "api_error", "status_code": e.response.status_code}
        if is_json_mode():
            output_json(error)
        else:
            if e.response.status_code == 404:
                print_error("Not Found", "Already deleted or invalid ID")
            else:
                print_error(
                    f"Delete Failed ({e.response.status_code})", "Could not delete"
                )
        sys.exit(1)


def api_patch(endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
    url = f"{get_api_url()}{endpoint}"
    try:
        response = httpx.patch(url, json=data, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        error = {"error": "connection_failed", "message": "Cannot connect"}
        if is_json_mode():
            output_json(error)
        else:
            print_error("Connection Failed", "Cannot reach server")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        error = {"error": "api_error", "status_code": e.response.status_code}
        if is_json_mode():
            output_json(error)
        else:
            print_error(f"Update Failed ({e.response.status_code})", "Could not update")
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# Utilities
# ═══════════════════════════════════════════════════════════════════════════════


def format_date(date_str: str | None) -> str:
    if not date_str:
        return "-"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        return date_str[:10] if date_str else "-"


def truncate(text: str, max_len: int = 50) -> str:
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "..."


def format_score(score: float) -> str:
    if score >= 0.8:
        return f"[bold green]{score:.2f}[/bold green]"
    elif score >= 0.5:
        return f"[green]{score:.2f}[/green]"
    elif score >= 0.3:
        return f"[yellow]{score:.2f}[/yellow]"
    else:
        return f"[dim]{score:.2f}[/dim]"


def format_importance(imp: float) -> str:
    if imp >= 0.7:
        return f"[green]{imp:.1f}[/green]"
    elif imp >= 0.4:
        return f"[yellow]{imp:.1f}[/yellow]"
    else:
        return f"[dim]{imp:.1f}[/dim]"


def parse_time_filter(time_str: str) -> str | None:
    now = datetime.now()
    time_map = {
        "today": now - timedelta(days=1),
        "yesterday": now - timedelta(days=2),
        "week": now - timedelta(weeks=1),
        "month": now - timedelta(days=30),
        "year": now - timedelta(days=365),
    }
    if time_str in time_map:
        return time_map[time_str].strftime("%Y-%m-%d")
    return time_str


# ═══════════════════════════════════════════════════════════════════════════════
# Commands: Status & Stats
# ═══════════════════════════════════════════════════════════════════════════════


def cmd_status() -> None:
    if not is_json_mode():
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Connecting...[/cyan]"),
            console=console,
            transient=True,
        ) as p:
            p.add_task("", total=None)
            data = api_get("/health")
    else:
        data = api_get("/health")

    result = {
        "status": data.get("status", "ok"),
        "version": data.get("version", __version__),
        "api_url": get_api_url(),
        "database": data.get("database_connected", True),
    }

    if is_json_mode():
        output_json(result)
    else:
        status_color = "green" if result["status"] == "ok" else "yellow"
        console.print()
        console.print(f"[bold]nmem[/bold] v{result['version']}")
        console.print(f"  status   [{status_color}]{result['status']}[/{status_color}]")
        console.print(f"  api      {result['api_url']}")
        console.print(
            f"  database {'connected' if result['database'] else 'disconnected'}"
        )
        console.print()


def cmd_stats() -> None:
    if not is_json_mode():
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Loading...[/cyan]"),
            console=console,
            transient=True,
        ) as p:
            p.add_task("", total=None)
            data = api_get("/stats")
    else:
        data = api_get("/stats")

    result = {
        "memories": data.get("memory_count", data.get("memories", 0)),
        "threads": data.get("thread_count", data.get("threads", 0)),
        "entities": data.get("entity_count", data.get("entities", 0)),
        "labels": data.get("label_count", data.get("labels", 0)),
        "communities": data.get("community_count", 0),
    }

    if is_json_mode():
        output_json(result)
    else:
        console.print()
        console.print("[bold]Database Statistics[/bold]")
        console.print(f"  memories    [cyan]{result['memories']:,}[/cyan]")
        console.print(f"  threads     [cyan]{result['threads']:,}[/cyan]")
        console.print(f"  entities    [magenta]{result['entities']:,}[/magenta]")
        console.print(f"  labels      [yellow]{result['labels']:,}[/yellow]")
        console.print(f"  communities [green]{result['communities']:,}[/green]")
        console.print()


# ═══════════════════════════════════════════════════════════════════════════════
# Memory Commands
# ═══════════════════════════════════════════════════════════════════════════════


def cmd_memories_list(limit: int = 10, importance_min: float | None = None) -> None:
    """List memories. Only importance filter is supported by the /memories API."""
    params: dict[str, Any] = {"limit": limit, "offset": 0}
    if importance_min is not None and importance_min > 0:
        params["importance_min"] = importance_min

    if not is_json_mode():
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Loading...[/cyan]"),
            console=console,
            transient=True,
        ) as p:
            p.add_task("", total=None)
            data = api_get("/memories", params=params)
    else:
        data = api_get("/memories", params=params)

    memories = data.get("memories", [])
    pagination = data.get("pagination", {})

    result = {
        "memories": [
            {
                "id": m.get("id", ""),
                "title": m.get("title", ""),
                "content": m.get("content", ""),
                "importance": m.get("importance", 0),
                "source": m.get("source", ""),
                "created_at": m.get("created_at", ""),
            }
            for m in memories
        ],
        "total": pagination.get("total", len(memories)),
    }

    if is_json_mode():
        output_json(result)
    else:
        if not memories:
            if importance_min and importance_min > 0:
                console.print(
                    f"[dim]No memories found with importance >= {importance_min}[/dim]"
                )
            else:
                console.print("[dim]No memories found.[/dim]")
            return
        console.print()
        if importance_min and importance_min > 0:
            console.print(f"[dim]Filter: importance >= {importance_min}[/dim]")
            console.print()
        table = Table(box=box.SIMPLE, header_style="bold", show_edge=False)
        table.add_column("ID", style="dim cyan", no_wrap=True)
        table.add_column("Title", min_width=30)
        table.add_column("Imp", justify="right", width=4)
        table.add_column("Source", style="yellow", width=10)
        table.add_column("Date", style="dim", width=10)
        for m in result["memories"]:
            table.add_row(
                m["id"],
                truncate(m["title"], 35),
                format_importance(m["importance"]),
                truncate(m["source"], 10),
                format_date(m["created_at"]),
            )
        console.print(table)
        if result["total"] > len(result["memories"]):
            console.print(
                f"[dim]Showing {len(result['memories'])} of {result['total']}[/dim]"
            )
        console.print()


def cmd_memories_search(
    query: str,
    limit: int = 10,
    labels: list[str] | None = None,
    time_range: str | None = None,
    importance_min: float | None = None,
) -> None:
    params: dict[str, Any] = {"q": query, "limit": limit}
    if labels:
        # Pass labels as repeated query params (labels=x&labels=y)
        params["labels"] = labels
    if time_range:
        # Use time_range directly - backend handles conversion
        params["time_range"] = time_range
    if importance_min is not None and importance_min > 0:
        params["importance_min"] = importance_min

    if not is_json_mode():
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[cyan]Searching '{query}'...[/cyan]"),
            console=console,
            transient=True,
        ) as p:
            p.add_task("", total=None)
            data = api_get("/memories/search", params=params)
    else:
        data = api_get("/memories/search", params=params)

    memories = data.get("memories", [])
    meta = data.get("search_metadata", {})

    result = {
        "query": query,
        "total": meta.get("total_found", len(memories)),
        "memories": [
            {
                "id": m.get("id", ""),
                "title": m.get("title", ""),
                "content": m.get("content", ""),
                "score": m.get("confidence", m.get("similarity_score", 0)),
                "source": m.get("source", ""),
                "source_thread": m.get("source_thread"),  # Include thread info
            }
            for m in memories
        ],
    }

    if is_json_mode():
        output_json(result)
    else:
        console.print()
        if not memories:
            filter_info = []
            if labels:
                filter_info.append(f"labels={','.join(labels)}")
            if time_range:
                filter_info.append(f"time={time_range}")
            if importance_min:
                filter_info.append(f"importance>={importance_min}")
            if filter_info:
                console.print(
                    f"[dim]No results for '{query}' with filters: {' '.join(filter_info)}[/dim]"
                )
            else:
                console.print(f"[dim]No results for '{query}'[/dim]")
            return

        # Show filter info if any
        filter_parts = []
        if labels:
            filter_parts.append(f"[magenta]{','.join(labels)}[/magenta]")
        if time_range:
            filter_parts.append(f"[cyan]{time_range}[/cyan]")
        if importance_min:
            filter_parts.append(f"[green]imp>={importance_min}[/green]")

        if filter_parts:
            console.print(
                f"[green]Found {result['total']} matches[/green] for [cyan]{query}[/cyan] [dim]({' '.join(filter_parts)})[/dim]"
            )
        else:
            console.print(
                f"[green]Found {result['total']} matches[/green] for [cyan]{query}[/cyan]"
            )
        console.print()
        table = Table(box=box.SIMPLE, header_style="bold", show_edge=False)
        table.add_column("ID", style="dim cyan", no_wrap=True)
        table.add_column("Title", min_width=25)
        table.add_column("Score", justify="right", width=5)
        table.add_column("Source", style="yellow", width=10)
        table.add_column("Thread", style="dim magenta", width=15)
        for m in result["memories"]:
            # Format thread info
            thread_info = ""
            if m.get("source_thread"):
                thread_title = m["source_thread"].get("title", "")
                thread_info = truncate(thread_title, 15) if thread_title else ""
            table.add_row(
                m["id"],
                truncate(m["title"], 30),
                format_score(m["score"]),
                truncate(m["source"], 10),
                thread_info,
            )
        console.print(table)
        console.print()


def cmd_memories_show(memory_id: str, content_limit: int | None = None) -> None:
    if not is_json_mode():
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Loading...[/cyan]"),
            console=console,
            transient=True,
        ) as p:
            p.add_task("", total=None)
            data = api_get(f"/memories/{memory_id}")
    else:
        data = api_get(f"/memories/{memory_id}")

    labels = [
        l.get("name", str(l)) if isinstance(l, dict) else str(l)
        for l in data.get("labels", [])
    ]
    result = {
        "id": data.get("id", memory_id),
        "title": data.get("title", ""),
        "content": data.get("content", ""),
        "importance": data.get("importance", 0),
        "confidence": data.get("confidence", 0),
        "source": data.get("source", ""),
        "created_at": data.get("created_at", ""),
        "labels": labels,
    }

    if is_json_mode():
        output_json(result)
    else:
        console.print()
        console.print(f"[bold]{result['title'] or 'Untitled'}[/bold]")
        console.print(f"[dim]ID:[/dim] [cyan]{result['id']}[/cyan]")
        console.print(
            f"[dim]Importance:[/dim] {format_importance(result['importance'])}  [dim]Source:[/dim] [yellow]{result['source']}[/yellow]"
        )
        if labels:
            console.print(f"[dim]Labels:[/dim] [magenta]{', '.join(labels)}[/magenta]")
        console.print()
        content = result["content"]
        if content_limit and len(content) > content_limit:
            console.print(content[:content_limit])
            console.print(f"[dim]... ({len(result['content'])} chars total)[/dim]")
        else:
            console.print(Markdown(content))
        console.print()


def cmd_memories_add(
    content: str, title: str | None = None, importance: float = 0.5
) -> None:
    payload = {"content": content, "importance": importance, "source": "cli"}
    if title:
        payload["title"] = title

    if not is_json_mode():
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Creating...[/cyan]"),
            console=console,
            transient=True,
        ) as p:
            p.add_task("", total=None)
            data = api_post("/memories", payload)
    else:
        data = api_post("/memories", payload)

    memory_data = data.get("memory", {})
    memory_id = memory_data.get("id", data.get("memory_id", data.get("id", "")))
    result = {
        "success": True,
        "id": memory_id,
        "title": memory_data.get("title", title or ""),
    }

    if is_json_mode():
        output_json(result)
    else:
        print_success("Created", result["id"])


def cmd_memories_update(
    memory_id: str,
    title: str | None = None,
    content: str | None = None,
    importance: float | None = None,
) -> None:
    payload: dict[str, Any] = {"memory_id": memory_id}
    if title is not None:
        payload["title"] = title
    if content is not None:
        payload["content"] = content
    if importance is not None:
        payload["importance"] = importance

    if len(payload) == 1:
        if is_json_mode():
            output_json({"error": "no_updates", "message": "No updates specified"})
        else:
            console.print("[yellow]No updates specified[/yellow]")
        return

    if not is_json_mode():
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Updating...[/cyan]"),
            console=console,
            transient=True,
        ) as p:
            p.add_task("", total=None)
            data = api_patch(f"/memories/{memory_id}", payload)
    else:
        data = api_patch(f"/memories/{memory_id}", payload)

    if is_json_mode():
        output_json({"success": True, "id": data.get("id", memory_id)})
    else:
        print_success("Updated", data.get("id", memory_id))


def cmd_memories_delete(memory_id: str, force: bool = False) -> None:
    if not force and not is_json_mode():
        if not Confirm.ask(f"Delete {memory_id}?"):
            console.print("[dim]Cancelled[/dim]")
            return

    if not is_json_mode():
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Deleting...[/cyan]"),
            console=console,
            transient=True,
        ) as p:
            p.add_task("", total=None)
            api_delete(f"/memories/{memory_id}")
    else:
        api_delete(f"/memories/{memory_id}")

    if is_json_mode():
        output_json({"success": True, "id": memory_id})
    else:
        print_success("Deleted", memory_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Thread Commands
# ═══════════════════════════════════════════════════════════════════════════════


def cmd_threads_list(limit: int = 10) -> None:
    if not is_json_mode():
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Loading...[/cyan]"),
            console=console,
            transient=True,
        ) as p:
            p.add_task("", total=None)
            data = api_get("/threads", params={"limit": limit, "offset": 0})
    else:
        data = api_get("/threads", params={"limit": limit, "offset": 0})

    threads = data.get("threads", [])
    pagination = data.get("pagination", {})

    result = {
        "threads": [
            {
                "id": t.get("id", ""),
                "title": t.get("title", ""),
                "messages": t.get("messages", 0),
                "source": t.get("source", ""),
                "created_at": t.get("date", t.get("created_at", "")),
            }
            for t in threads
        ],
        "total": pagination.get("total", len(threads)),
    }

    if is_json_mode():
        output_json(result)
    else:
        if not threads:
            console.print("[dim]No threads found.[/dim]")
            return
        console.print()
        table = Table(box=box.SIMPLE, header_style="bold", show_edge=False)
        table.add_column("ID", style="dim cyan", no_wrap=True)
        table.add_column("Title", min_width=35)
        table.add_column("Msgs", justify="right", width=4)
        table.add_column("Source", style="yellow", width=10)
        table.add_column("Date", style="dim", width=10)
        for t in result["threads"]:
            table.add_row(
                t["id"],
                truncate(t["title"], 40),
                str(t["messages"]),
                truncate(t["source"], 10),
                t["created_at"][:10] if t["created_at"] else "-",
            )
        console.print(table)
        if result["total"] > len(result["threads"]):
            console.print(
                f"[dim]Showing {len(result['threads'])} of {result['total']}[/dim]"
            )
        console.print()


def cmd_threads_show(
    thread_id: str, messages_limit: int = 10, content_limit: int | None = None
) -> None:
    if not is_json_mode():
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Loading...[/cyan]"),
            console=console,
            transient=True,
        ) as p:
            p.add_task("", total=None)
            data = api_get(f"/threads/{thread_id}")
    else:
        data = api_get(f"/threads/{thread_id}")

    thread = data.get("thread", {})
    messages = data.get("messages", [])

    result = {
        "id": thread.get("thread_id", thread_id),
        "title": thread.get("title", ""),
        "source": thread.get("source", ""),
        "created_at": thread.get("created_at", ""),
        "message_count": len(messages),
        "messages": [
            {
                "index": i,
                "role": m.get("role", "unknown"),
                "content": m.get("content", ""),
            }
            for i, m in enumerate(messages)
        ],
    }

    if is_json_mode():
        if messages_limit and messages_limit < len(result["messages"]):
            result["messages"] = result["messages"][-messages_limit:]
            result["truncated"] = True
        output_json(result)
    else:
        console.print()
        console.print(f"[bold]{result['title'] or 'Untitled'}[/bold]")
        console.print(
            f"[dim]ID:[/dim] [cyan]{result['id']}[/cyan]  [dim]Messages:[/dim] {result['message_count']}  [dim]Source:[/dim] [yellow]{result['source']}[/yellow]"
        )
        console.print()
        display_msgs = messages[-messages_limit:] if messages_limit else messages
        if len(messages) > len(display_msgs):
            console.print(
                f"[dim]... {len(messages) - len(display_msgs)} earlier messages ...[/dim]"
            )
            console.print()
        for m in display_msgs:
            role = m.get("role", "unknown")
            content = m.get("content", "")
            if content_limit and len(content) > content_limit:
                content = (
                    content[:content_limit] + f"... ({len(m.get('content', ''))} chars)"
                )
            role_color = "blue" if role == "user" else "green"
            if len(content) > 300:
                console.print(f"[bold {role_color}]{role.upper()}[/bold {role_color}]")
                console.print(content)
                console.print()
            else:
                console.print(
                    f"[bold {role_color}]{role.upper()}:[/bold {role_color}] {truncate(content, 200)}"
                )
        console.print()


def cmd_threads_search(query: str, limit: int = 10) -> None:
    if not is_json_mode():
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[cyan]Searching '{query}'...[/cyan]"),
            console=console,
            transient=True,
        ) as p:
            p.add_task("", total=None)
            data = api_get("/threads/search", params={"query": query, "limit": limit})
    else:
        data = api_get("/threads/search", params={"query": query, "limit": limit})

    threads = data.get("threads", [])

    # Get matches (message-level) and message count from API response
    result = {
        "query": query,
        "total": data.get("total_found", len(threads)),
        "threads": [
            {
                "id": t.get("thread_id", t.get("id", "")),
                "title": t.get("title", ""),
                "message_count": t.get("message_count", 0),
                "matches": t.get("total_matches", t.get("matched_messages_count", 0)),
                "source": t.get("source", ""),
            }
            for t in threads
        ],
    }

    if is_json_mode():
        output_json(result)
    else:
        console.print()
        if not threads:
            console.print(f"[dim]No results for '{query}'[/dim]")
            return
        console.print(
            f"[green]Found {result['total']} threads[/green] for [cyan]{query}[/cyan]"
        )
        console.print()
        table = Table(box=box.SIMPLE, header_style="bold", show_edge=False)
        table.add_column("ID", style="dim cyan", no_wrap=True)
        table.add_column("Title", min_width=35)
        table.add_column("Msgs", justify="right", width=5)
        table.add_column("Hits", justify="right", width=5)
        table.add_column("Source", style="yellow", width=10)
        for t in result["threads"]:
            table.add_row(
                t["id"],
                truncate(t["title"], 40),
                str(t["message_count"]),
                str(t["matches"]),
                truncate(t["source"], 10),
            )
        console.print(table)
        console.print()


def cmd_threads_create(
    title: str,
    content: str | None = None,
    messages_json: str | None = None,
    file: str | None = None,
    source: str = "cli",
) -> None:
    """Create a new thread from content, messages JSON, or file."""
    import hashlib

    if file:
        # File-based creation
        file_path = Path(file).resolve()
        if not file_path.exists():
            if is_json_mode():
                output_json({"error": "file_not_found", "path": str(file_path)})
            else:
                print_error("File Not Found", str(file_path))
            sys.exit(1)

        payload = {"file_path": str(file_path), "format": "auto"}
        if title:
            payload["title"] = title

        if not is_json_mode():
            with Progress(
                SpinnerColumn(),
                TextColumn("[cyan]Creating from file...[/cyan]"),
                console=console,
                transient=True,
            ) as p:
                p.add_task("", total=None)
                data = api_post("/threads/from-file", payload)
        else:
            data = api_post("/threads/from-file", payload)

        result = {
            "success": data.get("success", True),
            "id": data.get("thread_id", ""),
            "title": data.get("title", title),
            "messages": data.get("message_count", 0),
        }
    else:
        # Content or messages-based creation
        messages: list[dict[str, str]] = []

        if messages_json:
            # Parse JSON messages array
            try:
                messages = json_module.loads(messages_json)
                if not isinstance(messages, list):
                    raise ValueError("Must be a JSON array")
                for i, msg in enumerate(messages):
                    if not isinstance(msg, dict):
                        raise ValueError(f"Message {i} must be an object")
                    if "role" not in msg or "content" not in msg:
                        raise ValueError(f"Message {i} missing 'role' or 'content'")
            except (json_module.JSONDecodeError, ValueError) as e:
                if is_json_mode():
                    output_json({"error": "invalid_messages", "message": str(e)})
                else:
                    print_error(
                        "Invalid Messages JSON",
                        str(e),
                        'Format: [{"role":"user","content":"..."},{"role":"assistant","content":"..."}]',
                    )
                sys.exit(1)
        elif content:
            # Single content becomes a user message
            messages = [{"role": "user", "content": content}]
        else:
            if is_json_mode():
                output_json(
                    {
                        "error": "missing_content",
                        "message": "Provide --content, --messages, or --file",
                    }
                )
            else:
                print_error(
                    "Missing Content", "Provide --content, --messages, or --file"
                )
            sys.exit(1)

        # Generate thread_id from title and timestamp
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        title_hash = hashlib.md5(title.encode()).hexdigest()[:6]
        thread_id = f"cli-{ts}-{title_hash}"

        payload = {
            "thread_id": thread_id,
            "title": title,
            "messages": messages,
            "source": source,
        }

        if not is_json_mode():
            with Progress(
                SpinnerColumn(),
                TextColumn("[cyan]Creating...[/cyan]"),
                console=console,
                transient=True,
            ) as p:
                p.add_task("", total=None)
                data = api_post("/threads", payload)
        else:
            data = api_post("/threads", payload)

        # Response has thread object with thread_id
        thread_data = data.get("thread", {})
        result = {
            "success": True,
            "id": thread_data.get("thread_id", thread_id),
            "title": thread_data.get("title", title),
            "messages": len(data.get("messages", [])),
        }

    if is_json_mode():
        output_json(result)
    else:
        print_success("Created", f"{result['id']} ({result['messages']} messages)")


def cmd_threads_delete(
    thread_id: str, force: bool = False, cascade: bool = False
) -> None:
    if not force and not is_json_mode():
        msg = f"Delete {thread_id}?" + (" (with memories)" if cascade else "")
        if not Confirm.ask(msg):
            console.print("[dim]Cancelled[/dim]")
            return

    if not is_json_mode():
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Deleting...[/cyan]"),
            console=console,
            transient=True,
        ) as p:
            p.add_task("", total=None)
            data = api_delete(
                f"/threads/{thread_id}", params={"cascade_delete_memories": cascade}
            )
    else:
        data = api_delete(
            f"/threads/{thread_id}", params={"cascade_delete_memories": cascade}
        )

    result = {
        "success": True,
        "id": thread_id,
        "deleted_messages": data.get("deleted_messages", 0),
        "deleted_memories": data.get("deleted_memories", 0) if cascade else 0,
    }

    if is_json_mode():
        output_json(result)
    else:
        print_success("Deleted", thread_id)


def cmd_threads_save(
    client: str,
    project_path: str,
    mode: str = "current",
    session_id: str | None = None,
    summary: str | None = None,
    truncate: bool = False,
) -> None:
    """Save coding session(s) as conversation thread(s).

    Supports Claude Code and Codex. Auto-detects sessions from project path.
    """
    # Validate client
    if client not in ["claude-code", "codex"]:
        if is_json_mode():
            output_json(
                {"error": "invalid_client", "message": f"Must be claude-code or codex"}
            )
        else:
            print_error(
                "Invalid Client",
                f"'{client}' is not supported",
                "Use 'claude-code' or 'codex'",
            )
        sys.exit(1)

    # Resolve project path
    resolved_path = Path(project_path).resolve()
    if not resolved_path.exists():
        if is_json_mode():
            output_json({"error": "path_not_found", "path": str(resolved_path)})
        else:
            print_error("Path Not Found", str(resolved_path))
        sys.exit(1)

    payload = {
        "client": client,
        "project_path": str(resolved_path),
        "persist_mode": mode,
        "truncate_large_content": truncate,
    }
    if session_id:
        payload["session_id"] = session_id
    if summary:
        payload["summary"] = summary

    if not is_json_mode():
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[cyan]Saving {client} session...[/cyan]"),
            console=console,
            transient=True,
        ) as p:
            p.add_task("", total=None)
            data = api_post("/threads/sessions/save", payload)
    else:
        data = api_post("/threads/sessions/save", payload)

    if data.get("status") == "error":
        if is_json_mode():
            output_json(data)
        else:
            print_error(
                "Save Failed",
                data.get("error", "Unknown error"),
                data.get("hint"),
            )
        sys.exit(1)

    if is_json_mode():
        output_json(data)
    else:
        results = data.get("results", [])
        if len(results) == 1:
            r = results[0]
            action = r["action"]
            if action == "created":
                print_success(
                    "Created",
                    f"{r['thread_id']} ({r['message_count']} messages)",
                )
            else:
                print_success(
                    "Updated",
                    f"{r['thread_id']} (+{r['messages_added']} messages)",
                )
        else:
            created = sum(1 for r in results if r["action"] == "created")
            appended = sum(1 for r in results if r["action"] == "appended")
            console.print(
                f"[green]ok[/green] Processed {len(results)} sessions: "
                f"{created} created, {appended} updated"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Argument Parser
# ═══════════════════════════════════════════════════════════════════════════════


def create_parser() -> argparse.ArgumentParser:
    epilog = """
EXAMPLES
  nmem status                       Check server
  nmem tui                          Launch interactive TUI
  nmem m                            List memories (alias)
  nmem m search "query"             Search memories
  nmem m add "content"              Add memory
  nmem t                            List threads (alias)
  nmem t create -t "Title" -f x.md  Create from file
  nmem --json m search "x"          JSON output

ALIASES
  m  = memories
  t  = threads

SEARCH FILTERS (for 'm search' only)
  -l, --label LABEL    Filter by label
  -t, --time RANGE     today, week, month, year
  --importance MIN     Minimum importance

ENVIRONMENT
  NMEM_API_URL         Override API URL
"""

    parser = argparse.ArgumentParser(
        prog="nmem",
        description="Nowledge Mem CLI",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"nmem {__version__}"
    )
    parser.add_argument("--api-url", help="API server URL")
    parser.add_argument("-j", "--json", action="store_true", help="JSON output")

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # status
    subparsers.add_parser("status", help="Check server status")

    # stats
    subparsers.add_parser("stats", help="Show statistics")

    # tui - Interactive Terminal UI
    subparsers.add_parser("tui", help="Launch interactive TUI (Textual-based)")

    # memories (with alias 'm')
    for name in ["memories", "m"]:
        mem_parser = subparsers.add_parser(name, help="Memory operations")
        mem_parser.add_argument("-n", "--limit", type=int, default=10)
        mem_parser.add_argument(
            "--importance", type=float, help="Filter by min importance (list only)"
        )
        mem_subs = mem_parser.add_subparsers(dest="action")

        s = mem_subs.add_parser("search", help="Search memories")
        s.add_argument("query", nargs="+")
        s.add_argument("-n", "--limit", type=int, default=10)
        s.add_argument(
            "-l", "--label", action="append", dest="labels", help="Filter by label"
        )
        s.add_argument("-t", "--time", dest="time_range", help="today/week/month/year")
        s.add_argument("--importance", type=float, help="Minimum importance")

        sh = mem_subs.add_parser("show", help="Show details")
        sh.add_argument("id")
        sh.add_argument("--content-limit", type=int)

        a = mem_subs.add_parser("add", help="Add memory")
        a.add_argument("content")
        a.add_argument("-t", "--title")
        a.add_argument("-i", "--importance", type=float, default=0.5)

        u = mem_subs.add_parser("update", help="Update")
        u.add_argument("id")
        u.add_argument("-t", "--title")
        u.add_argument("-c", "--content")
        u.add_argument("-i", "--importance", type=float)

        d = mem_subs.add_parser("delete", help="Delete")
        d.add_argument("id")
        d.add_argument("-f", "--force", action="store_true")

    # threads (with alias 't')
    for name in ["threads", "t"]:
        thr_parser = subparsers.add_parser(name, help="Thread operations")
        thr_parser.add_argument("-n", "--limit", type=int, default=10)
        thr_subs = thr_parser.add_subparsers(dest="action")

        s = thr_subs.add_parser("search", help="Search")
        s.add_argument("query", nargs="+")
        s.add_argument("-n", "--limit", type=int, default=10)

        sh = thr_subs.add_parser("show", help="Show details")
        sh.add_argument("id")
        sh.add_argument("-m", "--messages", type=int, default=10)
        sh.add_argument("--content-limit", type=int)

        c = thr_subs.add_parser("create", help="Create thread from content or file")
        c.add_argument("-t", "--title", required=True, help="Thread title")
        c.add_argument("-c", "--content", help="Text content (creates 1 user message)")
        c.add_argument(
            "-m",
            "--messages",
            help='JSON: [{"role":"user|assistant","content":"..."},...]',
        )
        c.add_argument(
            "-f", "--file", help="Import from file (1 msg unless Cursor format)"
        )
        c.add_argument(
            "-s", "--source", default="cli", help="Source tag (default: cli)"
        )

        d = thr_subs.add_parser("delete", help="Delete")
        d.add_argument("id")
        d.add_argument("-f", "--force", action="store_true")
        d.add_argument("--cascade", action="store_true")

        # save - Save coding session as thread
        sv = thr_subs.add_parser(
            "save", help="Save Claude Code or Codex session as thread"
        )
        sv.add_argument(
            "--from",
            dest="source_app",
            required=True,
            choices=["claude-code", "codex"],
            help="Source app: claude-code or codex",
        )
        sv.add_argument(
            "-p",
            "--project",
            default=".",
            help="Project directory path (default: current dir)",
        )
        sv.add_argument(
            "-m",
            "--mode",
            choices=["current", "all"],
            default="current",
            help="Save mode: current (latest) or all sessions",
        )
        sv.add_argument(
            "--session-id", help="Specific session ID (Codex only)"
        )
        sv.add_argument(
            "-s", "--summary", help="Brief session summary"
        )
        sv.add_argument(
            "--truncate",
            action="store_true",
            help="Truncate large tool results (>10KB)",
        )

    return parser


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()

    if args.api_url:
        os.environ["NMEM_API_URL"] = args.api_url
    if getattr(args, "json", False):
        set_json_mode(True)

    cmd = args.command

    if cmd == "status":
        cmd_status()
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "tui":
        # Launch the interactive TUI
        from .tui import run_tui

        run_tui()
    elif cmd in ("memories", "m"):
        action = args.action
        if action == "search":
            cmd_memories_search(
                " ".join(args.query),
                args.limit,
                getattr(args, "labels", None),
                getattr(args, "time_range", None),
                getattr(args, "importance", None),
            )
        elif action == "show":
            cmd_memories_show(args.id, getattr(args, "content_limit", None))
        elif action == "add":
            cmd_memories_add(args.content, args.title, args.importance)
        elif action == "update":
            cmd_memories_update(args.id, args.title, args.content, args.importance)
        elif action == "delete":
            cmd_memories_delete(args.id, args.force)
        else:
            cmd_memories_list(args.limit, getattr(args, "importance", None))
    elif cmd in ("threads", "t"):
        action = args.action
        if action == "search":
            cmd_threads_search(" ".join(args.query), args.limit)
        elif action == "show":
            cmd_threads_show(
                args.id,
                getattr(args, "messages", 10),
                getattr(args, "content_limit", None),
            )
        elif action == "create":
            cmd_threads_create(
                args.title,
                args.content,
                getattr(args, "messages", None),
                args.file,
                args.source,
            )
        elif action == "delete":
            cmd_threads_delete(args.id, args.force, getattr(args, "cascade", False))
        elif action == "save":
            cmd_threads_save(
                client=args.source_app,
                project_path=args.project,
                mode=args.mode,
                session_id=getattr(args, "session_id", None),
                summary=getattr(args, "summary", None),
                truncate=getattr(args, "truncate", False),
            )
        else:
            cmd_threads_list(args.limit)
    else:
        if is_json_mode():
            output_json(
                {"error": "no_command", "commands": ["status", "stats", "m", "t"]}
            )
        else:
            parser.print_help()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
