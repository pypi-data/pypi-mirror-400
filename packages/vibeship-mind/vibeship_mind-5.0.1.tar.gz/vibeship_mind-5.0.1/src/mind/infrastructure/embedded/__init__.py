"""Embedded PostgreSQL for zero-config local development.

This module enables `pip install mind-sdk && mind serve` without
requiring users to install PostgreSQL separately.

Features:
- Lazy binary download (not bundled in pip package)
- Cross-platform support (Windows, macOS, Linux)
- pgvector extension support
- Data persistence across restarts
- Graceful startup/shutdown

Usage:
    from mind.infrastructure.embedded import EmbeddedPostgres

    async with EmbeddedPostgres() as pg:
        url = pg.connection_url
        # Use url with SQLAlchemy, asyncpg, etc.
"""

from mind.infrastructure.embedded.postgres import EmbeddedPostgres
from mind.infrastructure.embedded.downloader import PostgresBinaryManager
from mind.infrastructure.embedded.schema import init_standard_schema, check_schema_health

__all__ = [
    "EmbeddedPostgres",
    "PostgresBinaryManager",
    "init_standard_schema",
    "check_schema_health",
]
