"""
Configuration management for usqlh.

This module handles loading and saving configuration, including database connections.
"""

from pathlib import Path
from typing import Dict, Optional


class Config:
    """Configuration manager for usqlh."""

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_file: Path to configuration file. Defaults to ~/.usqldb
        """
        if config_file is None:
            config_file = Path.home() / ".usqldb"
        self.config_file = config_file

    def load_connections(self) -> Dict[str, str]:
        """
        Load all connections from config file.

        Returns:
            Dictionary mapping aliases to connection URLs
        """
        connections = {}
        if self.config_file.exists():
            with open(self.config_file) as f:
                for line in f:
                    line = line.strip()
                    if line and ":" in line:
                        # Split only on first colon to allow colons in URL
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            alias, url = parts
                            connections[alias] = url
        return connections

    def save_connections(self, connections: Dict[str, str]) -> None:
        """
        Save all connections to config file.

        Args:
            connections: Dictionary mapping aliases to connection URLs
        """
        with open(self.config_file, "w") as f:
            for alias, url in sorted(connections.items()):
                f.write(f"{alias}:{url}\n")

    def add_connection(self, alias: str, url: str) -> None:
        """
        Add or update a connection.

        Args:
            alias: Connection alias
            url: Connection URL
        """
        connections = self.load_connections()
        connections[alias] = url
        self.save_connections(connections)

    def remove_connection(self, alias: str) -> bool:
        """
        Remove a connection.

        Args:
            alias: Connection alias to remove

        Returns:
            True if connection was removed, False if not found
        """
        connections = self.load_connections()
        if alias in connections:
            del connections[alias]
            self.save_connections(connections)
            return True
        return False

    def rename_connection(self, old_alias: str, new_alias: str) -> bool:
        """
        Rename a connection.

        Args:
            old_alias: Current alias
            new_alias: New alias

        Returns:
            True if renamed, False if old_alias not found or new_alias exists
        """
        connections = self.load_connections()
        if old_alias not in connections:
            return False
        if new_alias in connections:
            return False

        connections[new_alias] = connections.pop(old_alias)
        self.save_connections(connections)
        return True

    def get_connection(self, alias: str) -> str | None:
        """
        Get connection URL by alias.

        Args:
            alias: Connection alias

        Returns:
            Connection URL or None if not found
        """
        connections = self.load_connections()
        return connections.get(alias)

    def list_connections(self, pattern: str = "") -> Dict[str, str]:
        """
        List connections with optional filtering.

        Args:
            pattern: Optional search pattern to filter aliases

        Returns:
            Dictionary of filtered connections
        """
        connections = self.load_connections()
        if pattern:
            return {
                alias: url for alias, url in connections.items() if pattern.lower() in alias.lower()
            }
        return connections
