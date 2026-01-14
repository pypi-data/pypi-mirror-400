"""
Core functionality for database connection management.

This module contains functions for parsing and building connection URLs,
testing connections, and managing interactive input.
"""

import subprocess
from urllib.parse import unquote, urlparse

from usqlh.config import Config
from usqlh.models import DATABASE_TYPES, ConnectionTestResult


# Legacy compatibility functions (backward compatibility)
def load_connections() -> dict:
    """Load all connections from config file (legacy function)."""
    config = Config()
    return config.load_connections()


def save_connections(connections: dict) -> None:
    """Save all connections to config file (legacy function)."""
    config = Config()
    config.save_connections(connections)


def parse_connection_url(url: str) -> dict:
    """
    Parse a database connection URL into components.

    Args:
        url: Database connection URL

    Returns:
        Dictionary with connection components (type, user, password, host, port, database, path, options)
    """
    result = {
        "type": "unknown",
        "user": "",
        "password": "",
        "host": "",
        "port": "",
        "database": "",
        "path": "",
        "options": "",
    }

    # Handle SQLite separately
    if url.startswith(("sqlite:", "sqlite3:")):
        result["type"] = "sqlite"
        # Extract path from sqlite3:/path/to/db or sqlite3://path/to/db
        path = url.split(":", 1)[1]
        if path.startswith("//"):
            path = path[2:]
        elif path.startswith("/"):
            path = path[1:]
        result["path"] = path
        return result

    # Parse standard URL format
    try:
        parsed = urlparse(url)
    except Exception:
        return result

    # Determine database type from scheme
    scheme = parsed.scheme or ""
    if scheme in DATABASE_TYPES:
        result["type"] = DATABASE_TYPES[scheme]["scheme"]
    else:
        result["type"] = scheme

    # Extract user and password
    if parsed.username:
        result["user"] = unquote(parsed.username)
    if parsed.password:
        result["password"] = unquote(parsed.password)

    # Extract host and port
    if parsed.hostname:
        result["host"] = parsed.hostname

    try:
        if parsed.port:
            result["port"] = str(parsed.port)
    except ValueError:
        # Port is not a valid integer, skip it
        pass

    # Extract database name from path
    if parsed.path and parsed.path.startswith("/"):
        path_parts = parsed.path[1:].split("/")
        if path_parts and path_parts[0]:
            result["database"] = path_parts[0]

    # Extract options
    if parsed.query:
        result["options"] = parsed.query

    return result


def build_connection_url(
    db_type: str,
    user: str,
    password: str,
    host: str,
    port: str,
    database: str,
    path: str = "",
    options: str = "",
) -> str:
    """
    Build a database connection URL from components.

    Args:
        db_type: Database type (postgres, mysql, etc.)
        user: Username
        password: Password
        host: Hostname or IP
        port: Port number
        database: Database name
        path: Path for file-based databases
        options: Query parameters

    Returns:
        Database connection URL
    """
    # Normalize database type
    if db_type.lower() in DATABASE_TYPES:
        scheme = DATABASE_TYPES[db_type.lower()]["scheme"]
    else:
        scheme = db_type.lower()

    # Handle SQLite
    if scheme == "sqlite":
        if path:
            return f"sqlite3://{path}"
        else:
            return f"sqlite3:{database}"

    # Build standard URL
    auth = ""
    if user:
        auth = user
        if password:
            auth += f":{password}"
        auth += "@"

    netloc = host
    if port:
        netloc += f":{port}"

    path_part = ""
    if database:
        path_part = f"/{database}"

    query = ""
    if options:
        query = f"?{options}"

    return f"{scheme}://{auth}{netloc}{path_part}{query}"


def test_connection(url: str) -> ConnectionTestResult:
    """
    Test if the database connection is valid.

    Args:
        url: Database connection URL to test

    Returns:
        ConnectionTestResult with success status and message
    """
    try:
        # Use usql with a simple query to test connection
        result = subprocess.run(
            ["usql", "-c", "SELECT 1", url],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return ConnectionTestResult(True, "Connection successful")
        else:
            return ConnectionTestResult(False, result.stderr.strip() or result.stdout.strip())
    except subprocess.TimeoutExpired:
        return ConnectionTestResult(False, "Connection timeout")
    except FileNotFoundError:
        return ConnectionTestResult(False, "usql command not found")
    except Exception as e:
        return ConnectionTestResult(False, str(e))


def interactive_input(prompt: str, default: str = "", secret: bool = False) -> str:
    """
    Get input from user with optional default and secret mode.

    Args:
        prompt: Prompt text
        default: Default value
        secret: Whether input should be hidden (passwords)

    Returns:
        User input or default value
    """
    if default:
        prompt_text = f"{prompt} [{default}]: "
    else:
        prompt_text = f"{prompt}: "

    if secret:
        import getpass

        value = getpass.getpass(prompt_text)
    else:
        value = input(prompt_text)

    return value if value else default


def select_database_type() -> str:
    """
    Interactive database type selection.

    Returns:
        Selected database type
    """
    print("\nSelect database type:")
    types = sorted(DATABASE_TYPES.keys())
    for i, db_type in enumerate(types, 1):
        print(f"  {i}. {db_type}")

    while True:
        choice = interactive_input(f"Enter choice (1-{len(types)})")
        try:
            index = int(choice) - 1
            if 0 <= index < len(types):
                return types[index]
        except ValueError:
            pass

        print("Invalid choice. Please try again.")


def list_connections(pattern: str = "") -> None:
    """
    List all connections with optional search.

    Args:
        pattern: Optional search pattern to filter connections
    """
    config = Config()
    connections = config.list_connections(pattern)

    if not connections:
        if pattern:
            print(f"No connections matching '{pattern}' found.")
        else:
            print("No connections found.")
        return

    # Calculate column widths
    aliases = connections.keys()
    max_alias_len = max(len(alias) for alias in aliases) if aliases else 10

    # Parse all URLs to find max widths
    all_parsed = {alias: parse_connection_url(url) for alias, url in connections.items()}
    max_type_len = max(len(p["type"]) for p in all_parsed.values()) if all_parsed else 10
    max_user_len = max(len(p["user"]) for p in all_parsed.values()) if all_parsed else 10
    max_host_len = max(len(p["host"]) for p in all_parsed.values()) if all_parsed else 10

    # Print header
    print()
    header = f"{'Alias':<{max_alias_len}}  {'Type':<{max_type_len}}  {'User':<{max_user_len}}  {'Host':<{max_host_len}}  {'Port':<6}  {'Database'}"
    print(header)
    print("-" * len(header))

    # Print connections
    for alias in sorted(connections.keys()):
        parsed = all_parsed[alias]
        if parsed["type"] == "sqlite":
            # Special display for SQLite
            print(
                f"{alias:<{max_alias_len}}  {parsed['type']:<{max_type_len}}  {'N/A':<{max_user_len}}  {parsed['path']:<{max_host_len}}  {'N/A':<6}  {parsed['path']}"
            )
        else:
            print(
                f"{alias:<{max_alias_len}}  {parsed['type']:<{max_type_len}}  {parsed['user']:<{max_user_len}}  {parsed['host']:<{max_host_len}}  {parsed['port']:<6}  {parsed['database']}"
            )
    print()


def edit_connection(alias: str) -> None:
    """
    Edit an existing connection.

    Args:
        alias: Alias of the connection to edit
    """
    config = Config()
    url = config.get_connection(alias)

    if url is None:
        print(f"Error: Alias '{alias}' not found.")
        return

    print(f"\nEditing connection: {alias}")
    print(f"Current URL: {url}")
    interactive_add(alias)


def rename_connection(old_alias: str, new_alias: str) -> None:
    """
    Rename an alias.

    Args:
        old_alias: Current alias
        new_alias: New alias
    """
    config = Config()

    if config.get_connection(old_alias) is None:
        print(f"Error: Alias '{old_alias}' not found.")
        return

    if config.get_connection(new_alias) is not None:
        print(f"Error: New alias '{new_alias}' already exists.")
        return

    if config.rename_connection(old_alias, new_alias):
        print(f"✓ Renamed alias '{old_alias}' to '{new_alias}'")
    else:
        print("Error: Failed to rename alias")


def remove_connection(alias: str) -> None:
    """
    Remove a connection.

    Args:
        alias: Alias of the connection to remove
    """
    config = Config()

    if config.get_connection(alias) is None:
        print(f"Error: Alias '{alias}' not found.")
        return

    confirm = input(f"Remove connection '{alias}'? (yes/no): ")
    if confirm.lower().startswith("y"):
        config.remove_connection(alias)
        print(f"✓ Removed connection for alias '{alias}'")
    else:
        print("Operation cancelled.")


def run_usql(alias: str, args: list) -> None:
    """
    Run usql with the specified alias.

    Args:
        alias: Connection alias
        args: Additional arguments to pass to usql
    """
    import os
    import sys

    config = Config()
    url = config.get_connection(alias)

    if url is None:
        print(f"Error: Alias '{alias}' not found.")
        sys.exit(1)

    cmd = ["usql", url, *args]
    os.execvp("usql", cmd)


def interactive_add(alias: str = "") -> None:
    """
    Interactive add/edit connection.

    Args:
        alias: Optional alias to pre-fill
    """
    from usqlh.completer import input_with_completion

    if not alias:
        config = Config()
        existing_aliases = list(config.load_connections().keys())
        alias = input_with_completion("Enter alias (Tab to see existing)", existing_aliases)
    if not alias:
        print("Error: Alias is required.")
        return

    config = Config()
    existing_url = config.get_connection(alias) or ""

    # Select database type
    db_type = None
    if existing_url:
        parsed = parse_connection_url(existing_url)
        db_type = parsed["type"]
        print(f"\nCurrent connection type: {db_type}")
        keep = interactive_input("Keep current type?", "yes").lower()
        if not keep.startswith("y"):
            db_type = None

    if not db_type:
        db_type = select_database_type()

    # Get connection details based on database type
    user = ""
    password = ""
    host = ""
    port = ""
    database = ""
    path = ""

    if db_type == "sqlite":
        if existing_url:
            parsed = parse_connection_url(existing_url)
            path = parsed["path"]
        path = interactive_input("Enter database path", path)
    else:
        # Get default port
        default_port = ""
        if db_type in DATABASE_TYPES:
            default_port = str(DATABASE_TYPES[db_type]["default_port"])

        # Get existing values if editing
        if existing_url:
            parsed = parse_connection_url(existing_url)
            user = parsed["user"]
            password = parsed["password"]
            host = parsed["host"]
            port = parsed["port"]
            database = parsed["database"]

        user = interactive_input("Enter username", user)
        if not user:
            print("Warning: Username is empty")

        password = interactive_input("Enter password", password, secret=True)

        host = interactive_input("Enter host", host or "localhost")

        port = interactive_input("Enter port", port or default_port)

        database = interactive_input("Enter database name", database)

    # Get options
    options = ""
    keep_options = (
        interactive_input("Add connection options (e.g., sslmode=require)?", "no")
        .lower()
        .startswith("y")
    )
    if keep_options:
        options = interactive_input("Enter options")

    # Build URL
    url = build_connection_url(db_type, user, password, host, port, database, path, options)

    print(f"\nGenerated URL: {url}")

    # Test connection
    test = interactive_input("Test connection?", "yes").lower().startswith("y")
    if test:
        print("\nTesting connection...")
        result = test_connection(url)
        if result.success:
            print(f"✓ {result.message}")
        else:
            print(f"✗ Connection failed: {result.message}")
            save_anyway = interactive_input("Save anyway?", "no").lower().startswith("y")
            if not save_anyway:
                print("Connection not saved.")
                return

    # Save connection
    config.add_connection(alias, url)
    print(f"\n✓ Connection saved for alias '{alias}'")
