"""Embedded PostgreSQL server management.

Provides a fully managed PostgreSQL instance for local development.
Handles initialization, startup, shutdown, and extension management.

Usage:
    async with EmbeddedPostgres() as pg:
        print(f"PostgreSQL running at: {pg.connection_url}")
        # Use with SQLAlchemy, asyncpg, etc.
"""

import asyncio
import os
import shutil
import signal
import socket
import subprocess
import tempfile
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator, Optional

import structlog

from mind.infrastructure.embedded.downloader import PostgresBinaryManager, detect_platform

logger = structlog.get_logger()


def find_free_port(start_port: int = 5432, max_attempts: int = 10) -> int:
    """Find a free port starting from start_port.

    Args:
        start_port: Port to start searching from
        max_attempts: Maximum number of ports to try

    Returns:
        A free port number

    Raises:
        RuntimeError: If no free port found
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()
            if result != 0:  # Port is not in use
                return port
        except Exception:
            pass
    raise RuntimeError(f"Could not find free port in range {start_port}-{start_port + max_attempts}")


@dataclass
class PostgresConfig:
    """Configuration for embedded PostgreSQL."""

    # Server settings
    port: int = 0  # 0 means auto-detect a free port
    host: str = "127.0.0.1"
    database: str = "mind"
    user: str = "mind"
    password: str = "mind"

    # Data directory (where PostgreSQL stores its files)
    data_dir: Optional[Path] = None

    # If True, delete data_dir on shutdown (for testing)
    ephemeral: bool = False

    # Connection timeout in seconds
    startup_timeout: int = 30

    # Extensions to install
    extensions: tuple[str, ...] = ("uuid-ossp", "vector")

    def __post_init__(self):
        """Auto-detect port if set to 0."""
        if self.port == 0:
            self.port = find_free_port()


class EmbeddedPostgres:
    """Embedded PostgreSQL server for zero-config development.

    Downloads PostgreSQL binaries on first use, initializes a database
    cluster, starts the server, and manages the lifecycle.

    Features:
    - Automatic binary download for current platform
    - Database cluster initialization with initdb
    - pgvector extension support
    - Graceful shutdown
    - Data persistence (or ephemeral mode for testing)

    Example:
        # Start with default config
        async with EmbeddedPostgres() as pg:
            url = pg.connection_url
            # url = "postgresql://mind:mind@127.0.0.1:5432/mind"

        # Custom config
        config = PostgresConfig(
            port=5433,
            database="test",
            ephemeral=True,  # Auto-delete on shutdown
        )
        async with EmbeddedPostgres(config) as pg:
            ...
    """

    def __init__(self, config: Optional[PostgresConfig] = None):
        """Initialize embedded PostgreSQL.

        Args:
            config: Server configuration. Uses defaults if not provided.
        """
        self.config = config or PostgresConfig()
        self._binary_manager = PostgresBinaryManager()
        self._process: Optional[subprocess.Popen] = None
        self._started = False

        # Default data directory
        if self.config.data_dir is None:
            self.config.data_dir = Path.home() / ".mind" / "data" / "postgres"

        self._log = logger.bind(
            port=self.config.port,
            data_dir=str(self.config.data_dir),
            database=self.config.database,
        )

    @property
    def connection_url(self) -> str:
        """PostgreSQL connection URL for asyncpg/SQLAlchemy."""
        c = self.config
        return f"postgresql+asyncpg://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}"

    @property
    def sync_connection_url(self) -> str:
        """Synchronous connection URL (for psycopg2)."""
        c = self.config
        return f"postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}"

    @property
    def is_running(self) -> bool:
        """Check if PostgreSQL is running."""
        return self._process is not None and self._process.poll() is None

    async def start(self) -> None:
        """Start the embedded PostgreSQL server.

        Downloads binaries if needed, initializes the database cluster,
        and starts the server.

        Raises:
            RuntimeError: If startup fails or times out
        """
        if self._started:
            self._log.warning("postgres_already_started")
            return

        self._log.info("starting_embedded_postgres")

        # Ensure binaries are available
        self._binary_manager.ensure_installed()

        # Initialize database cluster if needed
        await self._ensure_initialized()

        # Start PostgreSQL server
        await self._start_server()

        # Wait for server to accept connections
        await self._wait_for_startup()

        # Ensure user and database exist
        await self._ensure_database()

        # Install extensions
        await self._install_extensions()

        self._started = True
        self._log.info(
            "embedded_postgres_started",
            url=self.connection_url.replace(self.config.password, "***"),
        )

    async def stop(self) -> None:
        """Stop the embedded PostgreSQL server gracefully."""
        if not self.is_running:
            self._log.debug("postgres_not_running")
            return

        self._log.info("stopping_embedded_postgres")

        # Use pg_ctl stop for graceful shutdown
        pg_ctl = self._binary_manager.pg_ctl_binary()

        try:
            result = subprocess.run(
                [
                    str(pg_ctl),
                    "stop",
                    "-D", str(self.config.data_dir),
                    "-m", "fast",  # Fast shutdown (rollback transactions)
                    "-w",  # Wait for shutdown
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                self._log.warning(
                    "pg_ctl_stop_failed",
                    returncode=result.returncode,
                    stderr=result.stderr,
                )
                # Fall back to terminating the process
                self._force_stop()
        except subprocess.TimeoutExpired:
            self._log.warning("pg_ctl_stop_timeout")
            self._force_stop()

        self._process = None
        self._started = False

        # Clean up ephemeral data
        if self.config.ephemeral and self.config.data_dir.exists():
            self._log.debug("cleaning_ephemeral_data")
            shutil.rmtree(self.config.data_dir)

        self._log.info("embedded_postgres_stopped")

    def _force_stop(self) -> None:
        """Force stop the PostgreSQL process."""
        if self._process is None:
            return

        self._log.warning("force_stopping_postgres")

        try:
            if os.name == 'nt':  # Windows
                self._process.terminate()
            else:
                self._process.send_signal(signal.SIGTERM)

            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._log.warning("force_killing_postgres")
                self._process.kill()
                self._process.wait(timeout=5)
        except Exception as e:
            self._log.error("stop_failed", error=str(e))

    async def _ensure_initialized(self) -> None:
        """Initialize database cluster if not already done."""
        pg_version_file = self.config.data_dir / "PG_VERSION"

        if pg_version_file.exists():
            self._log.debug("database_cluster_exists")
            return

        self._log.info("initializing_database_cluster")

        # Create data directory
        self.config.data_dir.mkdir(parents=True, exist_ok=True)

        initdb = self._binary_manager.initdb_binary()

        # Set library path for initdb
        env = self._get_pg_env()

        # On Windows, set environment variables to fix hardcoded paths
        # (embedded PostgreSQL has hardcoded Unix paths like /share/timezone)
        platform_info = detect_platform()
        if platform_info.os == "windows":
            share_dir = str(self._binary_manager.share_dir)
            env["TZ"] = "UTC"
            env["PGTZ"] = "UTC"
            env["PGSHAREDIR"] = share_dir
            env["PGLOCALEDIR"] = str(self._binary_manager.install_dir / "locale")

        # Build initdb command
        cmd = [
            str(initdb),
            "-D", str(self.config.data_dir),
            "-U", "postgres",  # Superuser name
            "-E", "UTF8",
            "--locale=C",  # Use C locale for consistency
            "--no-sync",  # Faster initialization
            "-L", str(self._binary_manager.share_dir),  # Share files location
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"initdb failed (exit {result.returncode}): {result.stderr}"
            )

        # Configure PostgreSQL for local development
        await self._configure_postgres()

        self._log.info("database_cluster_initialized")

    async def _configure_postgres(self) -> None:
        """Configure PostgreSQL for local development."""
        # Determine platform-specific settings
        platform_info = detect_platform()
        dsm_type = "windows" if platform_info.os == "windows" else "posix"

        # Update postgresql.conf
        conf_file = self.config.data_dir / "postgresql.conf"
        conf_additions = f"""
# Mind embedded PostgreSQL configuration
listen_addresses = '{self.config.host}'
port = {self.config.port}
max_connections = 100
shared_buffers = 128MB
dynamic_shared_memory_type = {dsm_type}

# Logging
log_destination = 'stderr'
logging_collector = off

# Performance (development settings)
fsync = off
synchronous_commit = off
full_page_writes = off

# Extensions
shared_preload_libraries = ''
"""
        with open(conf_file, "a") as f:
            f.write(conf_additions)

        # Update pg_hba.conf for local development (trust all local connections)
        hba_file = self.config.data_dir / "pg_hba.conf"
        hba_content = """
# Mind embedded PostgreSQL authentication (local development)
# TYPE  DATABASE    USER        ADDRESS         METHOD
local   all         all                         trust
host    all         all         127.0.0.1/32    trust
host    all         all         ::1/128         trust
"""
        with open(hba_file, "w") as f:
            f.write(hba_content)

    async def _start_server(self) -> None:
        """Start the PostgreSQL server process."""
        postgres = self._binary_manager.postgres_binary()

        env = self._get_pg_env()

        self._log.debug("starting_postgres_process")

        # Start postgres directly (not as daemon)
        self._process = subprocess.Popen(
            [
                str(postgres),
                "-D", str(self.config.data_dir),
                "-k", "",  # Disable Unix socket (Windows compatibility)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

        # Start log reader tasks
        asyncio.create_task(self._read_logs(self._process.stdout, "stdout"))
        asyncio.create_task(self._read_logs(self._process.stderr, "stderr"))

    async def _read_logs(self, pipe, name: str) -> None:
        """Read and log PostgreSQL output."""
        try:
            while True:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, pipe.readline
                )
                if not line:
                    break
                self._log.debug(f"postgres_{name}", message=line.decode().strip())
        except Exception:
            pass

    async def _wait_for_startup(self) -> None:
        """Wait for PostgreSQL to accept connections."""
        self._log.debug("waiting_for_postgres_startup")

        start_time = asyncio.get_event_loop().time()
        timeout = self.config.startup_timeout

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise RuntimeError(
                    f"PostgreSQL failed to start within {timeout}s"
                )

            # Check if process is still running
            if self._process.poll() is not None:
                raise RuntimeError(
                    f"PostgreSQL process exited with code {self._process.returncode}"
                )

            # Try to connect
            if await self._check_connection():
                self._log.debug("postgres_accepting_connections", elapsed_s=elapsed)
                return

            await asyncio.sleep(0.2)

    async def _check_connection(self) -> bool:
        """Check if PostgreSQL is accepting connections."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.config.host, self.config.port))
            sock.close()
            return result == 0
        except Exception:
            return False

    async def _ensure_database(self) -> None:
        """Ensure the user and database exist."""
        psql = self._binary_manager.psql_binary()
        env = self._get_pg_env()

        # Create user
        self._log.debug("creating_user", user=self.config.user)
        await self._run_sql(
            f"CREATE USER {self.config.user} WITH PASSWORD '{self.config.password}' CREATEDB;",
            check=False,  # Ignore if exists
        )

        # Create database
        self._log.debug("creating_database", database=self.config.database)
        await self._run_sql(
            f"CREATE DATABASE {self.config.database} OWNER {self.config.user};",
            check=False,  # Ignore if exists
        )

    async def _install_extensions(self) -> None:
        """Install required PostgreSQL extensions."""
        for ext in self.config.extensions:
            self._log.debug("installing_extension", extension=ext)
            try:
                await self._run_sql(
                    f"CREATE EXTENSION IF NOT EXISTS \"{ext}\";",
                    database=self.config.database,
                )
            except RuntimeError as e:
                # Extension might not be available in embedded distribution
                if "not available" in str(e) or "does not exist" in str(e):
                    self._log.warning(
                        "extension_not_available",
                        extension=ext,
                        message="Extension not available in embedded PostgreSQL, skipping"
                    )
                else:
                    raise

    async def _run_sql(
        self,
        sql: str,
        database: str = "postgres",
        check: bool = True,
    ) -> str:
        """Run SQL command using psql or Python fallback.

        On Windows, psql is not included in embedded binaries,
        so we use psycopg2 as a fallback.
        """
        psql = self._binary_manager.psql_binary()

        # Use psql if available, otherwise fall back to Python
        if psql.exists():
            return await self._run_sql_psql(sql, database, check)
        else:
            return await self._run_sql_python(sql, database, check)

    async def _run_sql_psql(
        self,
        sql: str,
        database: str,
        check: bool,
    ) -> str:
        """Run SQL using psql binary."""
        psql = self._binary_manager.psql_binary()
        env = self._get_pg_env()

        result = subprocess.run(
            [
                str(psql),
                "-h", self.config.host,
                "-p", str(self.config.port),
                "-U", "postgres",  # Use superuser for admin tasks
                "-d", database,
                "-c", sql,
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        if check and result.returncode != 0:
            # Check for "already exists" errors which are OK
            if "already exists" not in result.stderr.lower():
                raise RuntimeError(f"SQL failed: {result.stderr}")

        return result.stdout

    async def _run_sql_python(
        self,
        sql: str,
        database: str,
        check: bool,
    ) -> str:
        """Run SQL using asyncpg (fallback for Windows where psql is missing)."""
        import asyncpg

        conn = None
        try:
            # Connect as superuser (trust auth for local connections)
            conn = await asyncpg.connect(
                host=self.config.host,
                port=self.config.port,
                user="postgres",
                database=database,
            )

            # Execute the SQL
            result = await conn.execute(sql)
            return result or ""

        except asyncpg.PostgresError as e:
            error_msg = str(e).lower()
            if check:
                # Check for "already exists" errors which are OK
                if "already exists" not in error_msg:
                    raise RuntimeError(f"SQL failed: {e}")
            return ""
        finally:
            if conn:
                await conn.close()

    def _get_pg_env(self) -> dict:
        """Get environment variables for PostgreSQL commands."""
        env = os.environ.copy()

        # Set library path so PostgreSQL can find its libraries
        lib_dir = self._binary_manager.lib_dir
        platform_info = detect_platform()

        if platform_info.os == "darwin":
            env["DYLD_LIBRARY_PATH"] = str(lib_dir)
        elif platform_info.os == "linux":
            env["LD_LIBRARY_PATH"] = str(lib_dir)
        # Windows doesn't need this - DLLs are in bin/

        return env

    async def __aenter__(self) -> "EmbeddedPostgres":
        """Context manager entry - start PostgreSQL."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - stop PostgreSQL."""
        await self.stop()


@asynccontextmanager
async def embedded_postgres(
    config: Optional[PostgresConfig] = None,
) -> AsyncGenerator[EmbeddedPostgres, None]:
    """Async context manager for embedded PostgreSQL.

    Example:
        async with embedded_postgres() as pg:
            url = pg.connection_url
            # Use url with your application
    """
    pg = EmbeddedPostgres(config)
    try:
        await pg.start()
        yield pg
    finally:
        await pg.stop()
