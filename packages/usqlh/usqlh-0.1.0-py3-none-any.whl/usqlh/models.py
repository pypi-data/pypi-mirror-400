"""
Data models and type definitions for usqlh.

This module contains the core data structures used throughout the application.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class DatabaseType(str, Enum):
    """Supported database types."""

    POSTGRES = "postgres"
    MYSQL = "mysql"
    MSSQL = "sqlserver"
    ORACLE = "oracle"
    SQLITE = "sqlite"
    COCKROACHDB = "cockroachdb"
    REDIS = "redis"
    MONGODB = "mongodb"


# Database type configuration
DATABASE_TYPES: Dict[str, dict] = {
    "postgres": {"default_port": 5432, "scheme": "postgres"},
    "postgresql": {"default_port": 5432, "scheme": "postgres"},
    "mysql": {"default_port": 3306, "scheme": "mysql"},
    "mysql2": {"default_port": 3306, "scheme": "mysql"},
    "mssql": {"default_port": 1433, "scheme": "sqlserver"},
    "sqlserver": {"default_port": 1433, "scheme": "sqlserver"},
    "oracle": {"default_port": 1521, "scheme": "oracle"},
    "sqlite": {"default_port": None, "scheme": "sqlite"},
    "sqlite3": {"default_port": None, "scheme": "sqlite"},
    "cockroachdb": {"default_port": 26257, "scheme": "cockroachdb"},
    "redis": {"default_port": 6379, "scheme": "redis"},
    "mongodb": {"default_port": 27017, "scheme": "mongodb"},
}


@dataclass
class Connection:
    """Represents a database connection."""

    alias: str
    url: str

    def __post_init__(self):
        """Validate connection after initialization."""
        if not self.alias:
            raise ValueError("Alias cannot be empty")
        if not self.url:
            raise ValueError("URL cannot be empty")


@dataclass
class ParsedConnection:
    """Represents a parsed database connection URL."""

    type: str = "unknown"
    user: str = ""
    password: str = ""
    host: str = ""
    port: str = ""
    database: str = ""
    path: str = ""
    options: str = ""

    def __str__(self) -> str:
        """Return a human-readable representation."""
        if self.type == "sqlite":
            return f"{self.type}: {self.path}"
        return f"{self.type}://{self.user}@{self.host}:{self.port}/{self.database}"


@dataclass
class ConnectionTestResult:
    """Result of a connection test."""

    success: bool
    message: str

    def __bool__(self) -> bool:
        """Return True if the connection test was successful."""
        return self.success
