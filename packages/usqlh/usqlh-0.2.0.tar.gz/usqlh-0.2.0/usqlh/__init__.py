"""
usqlh: Enhanced Python version for managing usql database connections

A modern CLI and TUI tool for managing database connections with usql.
"""

__version__ = "0.2.0"
__author__ = "usqlh team"

from usqlh.config import Config
from usqlh.core import (
    build_connection_url,
    load_connections,
    parse_connection_url,
    save_connections,
    test_connection,
)
from usqlh.models import Connection, DatabaseType

__all__ = [
    "Config",
    "Connection",
    "DatabaseType",
    "build_connection_url",
    "load_connections",
    "parse_connection_url",
    "save_connections",
    "test_connection",
]


def main():
    """Entry point for CLI."""
    from usqlh.cli import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
