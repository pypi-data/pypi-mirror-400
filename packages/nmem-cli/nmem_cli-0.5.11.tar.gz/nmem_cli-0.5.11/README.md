# nmem-cli

A lightweight CLI and TUI for [Nowledge Mem](https://mem.nowledge.co/) - AI memory management that works with any AI agent.

## Installation Options

### Option 1: Standalone PyPI Package (Recommended for CLI-only users)

```bash
pip install nmem-cli
```

Or with uv:

```bash
uv pip install nmem-cli
```

### Option 2: Nowledge Mem Desktop App

If you're using the [Nowledge Mem desktop app](https://mem.nowledge.co/), the `nmem` CLI is bundled and can be installed via:

- **macOS**: Settings → Install CLI (creates `/usr/local/bin/nmem`)
- **Linux**: Automatically installed via package postinstall
- **Windows**: Automatically added to PATH during installation

The desktop app includes a bundled Python environment, so no separate Python installation is required.

## Requirements

- Python 3.11+ (for PyPI package)
- A running Nowledge Mem server (default: `http://127.0.0.1:14242`)

## Quick Start

```bash
# Check server status
nmem status

# Launch interactive TUI
nmem tui

# List memories
nmem m

# Search memories
nmem m search "python programming"

# List threads
nmem t
```

## Commands

### Core Commands

| Command | Description |
| ------- | ----------- |
| `nmem status` | Check server connection status |
| `nmem stats` | Show database statistics |
| `nmem tui` | Launch interactive terminal UI |

### Memory Commands

| Command | Description |
| ------- | ----------- |
| `nmem m` / `nmem memories` | List recent memories |
| `nmem m search "query"` | Search memories |
| `nmem m show <id>` | Show memory details |
| `nmem m add "content"` | Add a new memory |
| `nmem m update <id>` | Update a memory |
| `nmem m delete <id>` | Delete a memory |

### Thread Commands

| Command | Description |
| ------- | ----------- |
| `nmem t` / `nmem threads` | List threads |
| `nmem t search "query"` | Search threads |
| `nmem t show <id>` | Show thread with messages |
| `nmem t create -t "Title" -c "content"` | Create a thread |
| `nmem t delete <id>` | Delete a thread |

## Options

### Global Options

```bash
nmem --json <command>     # Output in JSON format (for scripting)
nmem --api-url <url>      # Override API URL
nmem --version            # Show version
```

### Search Filters (memories)

```bash
nmem m search "query" -l label1 -l label2   # Filter by labels
nmem m search "query" -t week               # Time range: today/week/month/year
nmem m search "query" --importance 0.7      # Minimum importance
```

## Environment Variables

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `NMEM_API_URL` | API server URL | `http://127.0.0.1:14242` |

## TUI Features

The interactive TUI provides:

- **Dashboard**: Overview with statistics and recent activity
- **Memories**: Browse, search, and manage memories
- **Threads**: View conversation threads
- **Graph**: Explore the knowledge graph
- **Settings**: Configure the application

### TUI Keybindings

| Key | Action |
| --- | ------ |
| `1-5` | Switch tabs |
| `/` | Focus search |
| `?` | Show help |
| `q` | Quit |

## Examples

### Script Integration (JSON mode)

```bash
# Get memories as JSON
nmem --json m search "meeting notes" | jq '.memories[].title'

# Check if server is running
if nmem --json status | jq -e '.status == "ok"' > /dev/null; then
    echo "Server is running"
fi
```

### Adding Memories

```bash
# Simple memory
nmem m add "Remember to review the PR tomorrow"

# With title and importance
nmem m add "The deployment process requires SSH access" \
    -t "Deployment Notes" \
    -i 0.8
```

### Creating Threads

```bash
# From content
nmem t create -t "Debug Session" -c "Started investigating the memory leak"

# From file
nmem t create -t "Code Review" -f review-notes.md
```

## Related

- [Nowledge Mem](https://mem.nowledge.co/) - The full Nowledge Mem application
- This CLI is also bundled with the main Nowledge Mem desktop app

## Author

[Nowledge Labs](https://github.com/nowledge-co)
