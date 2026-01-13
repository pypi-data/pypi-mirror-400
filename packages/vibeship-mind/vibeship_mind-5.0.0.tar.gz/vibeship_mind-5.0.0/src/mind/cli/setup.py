"""Setup commands for Mind v5.

Provides one-command installation and startup:
- mind setup: Download PostgreSQL, pgvector, initialize database
- mind up: Setup + serve (one-command start)
"""

import re
import sys
from typing import Optional

import structlog

logger = structlog.get_logger()


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
                print("  [OK] PostgreSQL already installed")
            else:
                print("  -> Downloading PostgreSQL (this may take a few minutes)...")
                manager.ensure_installed()
                print(f"  [OK] PostgreSQL {manager.version} installed")

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

    # Step 3: Database initialization
    if not skip_db_init:
        print(f"\n[{steps_completed + 1}/{total_steps}] Initializing database...")

        try:
            # Check if we can connect to PostgreSQL
            import os
            database_url = os.environ.get("MIND_DATABASE_URL")

            if database_url:
                print(f"  -> Using database: {_mask_password(database_url)}")

                from sqlalchemy import text
                from mind.infrastructure.postgres.database import get_database
                from mind.infrastructure.postgres.models import Base

                db = get_database()

                async with db.engine.begin() as conn:
                    # Enable extensions
                    await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
                    print("  [OK] uuid-ossp extension enabled")

                    try:
                        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "vector"'))
                        print("  [OK] vector extension enabled")
                    except Exception as ve:
                        print(f"  [!] Could not enable vector extension: {ve}")

                    # Create tables
                    await conn.run_sync(Base.metadata.create_all)
                    print("  [OK] Database tables created")

            else:
                print("  [!] No database URL configured")
                print("      Set MIND_DATABASE_URL in .env or environment")
                print("      Example: postgresql+asyncpg://user:pass@localhost:5432/mind")

        except Exception as e:
            print(f"  [ERROR] Database error: {e}")
            logger.error("setup_db_failed", error=str(e))
            # Don't exit - user might want to configure DB later

        steps_completed += 1
    else:
        print(f"\n[3/{total_steps}] Database: skipped (--skip-db-init)")
        steps_completed += 1

    # Summary
    print("\n" + "=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Configure .env file with your database settings")
    print("  2. Run 'mind serve' to start the API server")
    print("  3. Or run 'mind up' to start everything at once")
    print()


async def up_command(
    host: str = "127.0.0.1",
    port: int = 8001,
    skip_setup: bool = False,
) -> None:
    """One-command start: setup + serve.

    This is the simplest way to get Mind running:
    - Ensures PostgreSQL and pgvector are available
    - Initializes the database if needed
    - Starts the API server
    """
    # Run setup first (unless skipped)
    if not skip_setup:
        await setup_command(
            skip_postgres=False,
            skip_pgvector=False,
            skip_db_init=False,
        )

    # Now start the server
    print("\n" + "=" * 60)
    print("  Starting Mind Server")
    print("=" * 60 + "\n")

    import uvicorn

    logger.info(
        "starting_server",
        host=host,
        port=port,
    )

    # Run uvicorn (this blocks)
    uvicorn.run(
        "mind.api.app:app",
        host=host,
        port=port,
        log_level="info",
    )


def _mask_password(url: str) -> str:
    """Mask password in database URL for display."""
    # Match pattern: ://user:password@host
    return re.sub(r'(://[^:]+:)[^@]+(@)', r'\1****\2', url)
