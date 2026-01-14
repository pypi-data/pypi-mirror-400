"""Module for SFTP credentials management."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SQLCredentials:
    """Data class for SQL connection credentials."""
    hostname: str
    database: str
    username: str
    password: str
