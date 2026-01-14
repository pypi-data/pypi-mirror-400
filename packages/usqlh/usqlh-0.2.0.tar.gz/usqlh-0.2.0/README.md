# usqlh

A CLI tool for managing [usql](https://github.com/xo/usql) database connections with alias management and Tab auto-completion.

## Why usqlh?

[usql](https://github.com/xo/usql) is a universal command-line interface for SQL databases, but it requires you to remember or type full connection URLs every time. **usqlh** solves this by:

- Storing connections with memorable aliases
- Providing Tab auto-completion for alias names
- Offering interactive connection setup with validation

## Installation

```bash
# Install from PyPI
pip install usqlh

# Or install from source
git clone https://github.com/aki-colt/usqlh.git
cd usqlh
pip install -e .
```

### Prerequisites

- Python 3.8+
- [usql](https://github.com/xo/usql) installed and available in PATH

## Quick Start

```bash
# Add a new connection
usqlh add mydb
# Follow the interactive prompts to configure

# Connect to database
usqlh connect  # Tab to select from saved connections
# Or directly:
usqlh mydb

# List all saved connections
usqlh list
```

## Usage

| Command | Description |
|---------|-------------|
| `usqlh add [alias]` | Add/update a connection (interactive) |
| `usqlh edit [alias]` | Edit existing connection (Tab to complete) |
| `usqlh remove [alias]` | Remove a connection (Tab to complete) |
| `usqlh rename <old> <new>` | Rename an alias |
| `usqlh list [pattern]` | List connections (optional filter) |
| `usqlh connect [alias]` | Connect with Tab completion |
| `usqlh c [alias]` | Short alias for connect |
| `usqlh <alias> [args]` | Connect directly, pass extra args to usql |

### Auto-completion

Press `Tab` when prompted for an alias to:
- Show all available aliases (empty input)
- Complete partial input (e.g., `my` → `mydb`)

Works in all shells (bash, zsh, sh) without additional configuration.

## Supported Databases

All databases supported by [usql](https://github.com/xo/usql):

| Database | Schemes |
|----------|---------|
| PostgreSQL | `postgres`, `postgresql`, `pg` |
| MySQL | `mysql`, `mysql2` |
| SQLite | `sqlite`, `sqlite3` |
| SQL Server | `mssql`, `sqlserver` |
| Oracle | `oracle` |
| CockroachDB | `cockroachdb` |
| Redis | `redis` |
| MongoDB | `mongodb` |

## Configuration

Connections are stored in `~/.usqldb`:

```
mydb:postgres://user:pass@localhost:5432/mydb
prod:mysql://admin:secret@db.example.com:3306/app
local:sqlite3:///path/to/db.sqlite
```

## Architecture

```
usqlh/
├── __init__.py     # Entry point
├── cli.py          # Command routing and argument parsing
├── core.py         # Connection URL building/parsing, usql execution
├── config.py       # ~/.usqldb file management
├── completer.py    # readline-based Tab completion
└── models.py       # Database type definitions
```

### Key Design Decisions

1. **Zero runtime dependencies** - Uses only Python standard library (readline, argparse, urllib)
2. **readline for completion** - Works across all terminal emulators without shell-specific config
3. **Simple file format** - Plain text `alias:url` for easy manual editing and version control
4. **Thin wrapper** - Delegates actual database operations to usql via `execvp`

## Development

```bash
# Create virtual environment with uv
uv venv
source .venv/bin/activate

# Install with dev dependencies
uv pip install -e ".[dev]"

# Run linter
ruff check usqlh/

# Format code
ruff format usqlh/

# Type check
mypy usqlh/
```

## License

MIT
