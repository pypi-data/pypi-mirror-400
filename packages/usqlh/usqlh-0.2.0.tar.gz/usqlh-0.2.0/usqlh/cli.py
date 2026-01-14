import argparse
import sys

from usqlh.completer import input_with_completion
from usqlh.config import Config
from usqlh.core import (
    edit_connection,
    interactive_add,
    list_connections,
    remove_connection,
    rename_connection,
    run_usql,
    test_connection,
)

HELP_TEXT = """
usqlh: Enhanced CLI for managing usql database connections

Usage:
  usqlh help                Show help message
  usqlh add [alias]         Add or update a database connection (interactive)
  usqlh edit [alias]        Edit an existing connection (Tab to complete alias)
  usqlh rename <old> <new>  Rename an alias
  usqlh list [pattern]      List connections (with optional search)
  usqlh remove [alias]      Remove a connection (Tab to complete alias)
  usqlh connect [alias]     Connect to database (Tab to complete alias)
  usqlh <alias> [args]      Run usql with the alias directly
"""


def get_aliases() -> list:
    config = Config()
    return list(config.load_connections().keys())


def prompt_for_alias(prompt_text: str) -> str:
    aliases = get_aliases()
    if not aliases:
        print("No connections available.")
        sys.exit(1)
    return input_with_completion(prompt_text, aliases)


def main() -> None:
    parser = argparse.ArgumentParser(description="Enhanced usql connection manager", add_help=False)
    parser.add_argument("command", nargs="?", help="Command to execute")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments for command")

    args = parser.parse_args()

    if not args.command or args.command == "help":
        print(HELP_TEXT)
        return

    command = args.command.lower()

    if command == "add":
        alias = args.args[0] if args.args else ""
        interactive_add(alias)
    elif command == "edit":
        alias = args.args[0] if args.args else prompt_for_alias("Enter alias to edit")
        if not alias:
            sys.exit(1)
        edit_connection(alias)
    elif command == "rename":
        old_alias = args.args[0] if args.args else prompt_for_alias("Enter alias to rename")
        if not old_alias:
            sys.exit(1)
        new_alias = args.args[1] if len(args.args) > 1 else input("Enter new alias: ")
        if not new_alias:
            print("Error: New alias is required.")
            sys.exit(1)
        rename_connection(old_alias, new_alias)
    elif command == "list":
        pattern = args.args[0] if args.args else ""
        list_connections(pattern)
    elif command == "remove":
        alias = args.args[0] if args.args else prompt_for_alias("Enter alias to remove")
        if not alias:
            sys.exit(1)
        remove_connection(alias)
    elif command == "test":
        if not args.args:
            print("Error: URL is required for test command.")
            sys.exit(1)
        result = test_connection(args.args[0])
        if result.success:
            print(f"✓ {result.message}")
        else:
            print(f"✗ {result.message}")
        sys.exit(0 if result.success else 1)
    elif command == "connect" or command == "c":
        alias = args.args[0] if args.args else prompt_for_alias("Select connection")
        if not alias:
            sys.exit(1)
        run_usql(alias, args.args[1:] if len(args.args) > 1 else [])
    else:
        run_usql(args.command, args.args)


if __name__ == "__main__":
    main()
