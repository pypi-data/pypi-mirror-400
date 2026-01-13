"""Setup commands for Mind v5.

Provides one-command installation and startup:
- mind setup: Download PostgreSQL, pgvector, initialize database
- mind up: Setup + serve (one-command start) with embedded PostgreSQL
"""

import os
import re
import sys
from typing import Optional

import structlog

logger = structlog.get_logger()

# Global reference to keep embedded postgres alive
_embedded_pg = None


async def setup_command(
    skip_postgres: bool = False,
    skip_pgvector: bool = False,
    skip_db_init: bool = False,
) -> None:
    """One-command setup: download PostgreSQL, pgvector, initialize database.

    This command handles everything needed to get Mind running:
    1. Downloads PostgreSQL binaries (embedded, no system install needed)
    2. Downloads and installs pgvector extension
    3. Initializes the database with required tables and extensions
    """
    print("\n" + "=" * 60)
    print("  Mind v5 Setup")
    print("=" * 60 + "\n")

    steps_completed = 0
    total_steps = 3

    # Step 1: PostgreSQL binaries
    if not skip_postgres:
        print(f"[{steps_completed + 1}/{total_steps}] Setting up PostgreSQL binaries...")

        try:
            from mind.infrastructure.embedded.downloader import PostgresBinaryManager

            manager = PostgresBinaryManager()

            if manager.is_installed():
                print("  [OK] PostgreSQL binaries already downloaded")
            else:
                print("  -> Downloading PostgreSQL (this may take a few minutes)...")
                manager.ensure_installed()
                print(f"  [OK] PostgreSQL {manager.version} downloaded")

            print(f"  -> Location: {manager.install_dir}")

        except Exception as e:
            print(f"  [ERROR] {e}")
            logger.error("setup_postgres_failed", error=str(e))
            sys.exit(1)

        steps_completed += 1
    else:
        print(f"[1/{total_steps}] PostgreSQL: skipped (--skip-postgres)")
        steps_completed += 1

    # Step 2: pgvector extension
    if not skip_pgvector:
        print(f"\n[{steps_completed + 1}/{total_steps}] Setting up pgvector extension...")

        try:
            from mind.infrastructure.embedded.downloader import PostgresBinaryManager

            manager = PostgresBinaryManager()

            if manager.is_pgvector_installed():
                print("  [OK] pgvector already installed")
            else:
                print("  -> Downloading pgvector...")
                success = manager.ensure_pgvector_installed()
                if success:
                    print("  [OK] pgvector installed")
                else:
                    print("  [!] pgvector not available for auto-install on this platform")
                    print("      Install manually:")
                    print("      - macOS: brew install pgvector")
                    print("      - Linux: apt install postgresql-16-pgvector")

        except Exception as e:
            print(f"  [ERROR] {e}")
            logger.error("setup_pgvector_failed", error=str(e))
            # Don't exit - pgvector is optional

        steps_completed += 1
    else:
        print(f"\n[2/{total_steps}] pgvector: skipped (--skip-pgvector)")
        steps_completed += 1

    # Step 3: Database initialization info
    if not skip_db_init:
        print(f"\n[{steps_completed + 1}/{total_steps}] Database setup...")

        database_url = os.environ.get("MIND_DATABASE_URL")

        if database_url:
            # External database configured
            print(f"  -> External database: {_mask_password(database_url)}")
            print("  -> Tables will be created on first connection")
        else:
            # Will use embedded PostgreSQL
            print("  -> Will use embedded PostgreSQL (no external database configured)")
            print("  -> Database will be initialized when 'mind up' starts")

        steps_completed += 1
    else:
        print(f"\n[3/{total_steps}] Database: skipped (--skip-db-init)")
        steps_completed += 1

    # Summary
    print("\n" + "=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  Run 'mind up' to start Mind with embedded PostgreSQL")
    print("  Or set MIND_DATABASE_URL to use an external database")
    print()


async def up_command(
    host: str = "127.0.0.1",
    port: int = 8001,
    skip_setup: bool = False,
) -> None:
    """One-command start: setup + serve with embedded PostgreSQL.

    This is the simplest way to get Mind running:
    - Downloads PostgreSQL binaries if needed
    - Starts embedded PostgreSQL server
    - Initializes the database with tables and extensions
    - Starts the Mind API server

    Everything is automatic - no external database needed!
    """
    global _embedded_pg

    # Run setup first (unless skipped)
    if not skip_setup:
        await setup_command(
            skip_postgres=False,
            skip_pgvector=False,
            skip_db_init=True,  # We'll init as part of embedded PG startup
        )

    # Check if external database is configured
    external_db = os.environ.get("MIND_DATABASE_URL")

    if external_db:
        # Use external database
        print("\n" + "=" * 60)
        print("  Using External PostgreSQL")
        print("=" * 60)
        print(f"\n  Database: {_mask_password(external_db)}")

        # Initialize tables
        await _init_external_database()

    else:
        # Start embedded PostgreSQL
        print("\n" + "=" * 60)
        print("  Starting Embedded PostgreSQL")
        print("=" * 60 + "\n")

        from mind.infrastructure.embedded.postgres import EmbeddedPostgres, PostgresConfig

        config = PostgresConfig(
            port=5432,  # Try default port first
            database="mind",
            user="mind",
            password="mind",
        )

        _embedded_pg = EmbeddedPostgres(config)

        print("  -> Starting PostgreSQL server...")
        await _embedded_pg.start()

        print(f"  [OK] PostgreSQL running on port {_embedded_pg.config.port}")
        print(f"  [OK] Database: {_embedded_pg.config.database}")
        print(f"  [OK] Extensions: uuid-ossp, vector")

        # Set environment variable for the API server
        os.environ["MIND_DATABASE_URL"] = _embedded_pg.connection_url

        # Initialize Mind tables
        await _init_mind_tables()

    # Now start the API server
    print("\n" + "=" * 60)
    print("  Starting Mind API Server")
    print("=" * 60)
    print(f"\n  -> http://{host}:{port}")
    print("  -> Press Ctrl+C to stop\n")

    import uvicorn

    try:
        # Run uvicorn (this blocks)
        uvicorn.run(
            "mind.api.app:app",
            host=host,
            port=port,
            log_level="info",
        )
    finally:
        # Cleanup embedded postgres on shutdown
        if _embedded_pg:
            print("\n  -> Stopping embedded PostgreSQL...")
            await _embedded_pg.stop()
            print("  [OK] PostgreSQL stopped")


async def _init_external_database() -> None:
    """Initialize tables in external database."""
    try:
        from sqlalchemy import text
        from mind.infrastructure.postgres.database import get_database
        from mind.infrastructure.postgres.models import Base

        print("\n  -> Initializing database tables...")

        db = get_database()

        async with db.engine.begin() as conn:
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))

            try:
                await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "vector"'))
            except Exception:
                print("  [!] pgvector extension not available")

            await conn.run_sync(Base.metadata.create_all)

        print("  [OK] Database tables ready")

    except Exception as e:
        print(f"  [ERROR] Database init failed: {e}")
        raise


async def _init_mind_tables() -> None:
    """Initialize Mind tables in embedded database."""
    try:
        from sqlalchemy import text
        from mind.infrastructure.postgres.database import get_database
        from mind.infrastructure.postgres.models import Base

        print("\n  -> Creating Mind tables...")

        db = get_database()

        async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("  [OK] Mind tables created")

    except Exception as e:
        print(f"  [ERROR] Table creation failed: {e}")
        raise


def _mask_password(url: str) -> str:
    """Mask password in database URL for display."""
    return re.sub(r'(://[^:]+:)[^@]+(@)', r'\1****\2', url)
