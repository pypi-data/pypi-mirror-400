"""Mind migrate command - Run database migrations.

Applies database schema migrations to PostgreSQL.
Uses Alembic for migration management.

Usage:
    mind migrate                              # Apply all migrations
    mind migrate --database-url postgresql://... # Use specific database
    mind migrate --revision head              # Apply to specific revision
"""

import os
import sys
from typing import Optional


def migrate_command(
    database_url: Optional[str] = None,
    revision: str = "head",
) -> None:
    """Run database migrations.

    Args:
        database_url: PostgreSQL connection URL
        revision: Target revision (default: head)
    """
    import structlog

    logger = structlog.get_logger()

    # Determine database URL
    if database_url is None:
        database_url = os.environ.get("MIND_DATABASE_URL")

    if database_url is None:
        print("Error: No database URL provided.")
        print()
        print("Options:")
        print("  1. Set MIND_DATABASE_URL environment variable")
        print("  2. Pass --database-url argument")
        print("  3. For local development, use 'mind serve' which auto-creates the database")
        print()
        print("Example:")
        print("  mind migrate --database-url postgresql://user:pass@localhost:5432/mind")
        sys.exit(1)

    # Normalize URL for psycopg2 (Alembic uses sync driver)
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    sync_url = sync_url.replace("postgresql://", "postgresql+psycopg2://")

    print(f"Migrating database...")
    print(f"  Target: {_mask_password(database_url)}")
    print(f"  Revision: {revision}")
    print()

    try:
        from alembic import command
        from alembic.config import Config

        # Find alembic.ini in the package
        import mind
        package_dir = os.path.dirname(mind.__file__)
        alembic_ini = os.path.join(package_dir, "..", "..", "alembic.ini")

        if not os.path.exists(alembic_ini):
            # Try alternate location
            alembic_ini = os.path.join(os.getcwd(), "alembic.ini")

        if not os.path.exists(alembic_ini):
            # Fall back to direct SQL application
            print("  Using direct SQL migration (alembic.ini not found)")
            _apply_sql_migrations(database_url)
            return

        # Configure Alembic
        alembic_cfg = Config(alembic_ini)
        alembic_cfg.set_main_option("sqlalchemy.url", sync_url)

        # Run migrations
        command.upgrade(alembic_cfg, revision)

        print()
        print("  Migration complete!")

    except ImportError:
        print("Warning: Alembic not installed, using direct SQL migration")
        _apply_sql_migrations(database_url)
    except Exception as e:
        logger.error("migration_failed", error=str(e))
        print(f"\nError: {e}")
        sys.exit(1)


def _apply_sql_migrations(database_url: str) -> None:
    """Apply SQL migrations directly (fallback when Alembic not available)."""
    import asyncio

    async def run():
        import asyncpg

        # Normalize URL for asyncpg
        asyncpg_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        asyncpg_url = asyncpg_url.replace("postgresql+psycopg2://", "postgresql://")

        conn = await asyncpg.connect(asyncpg_url)

        try:
            # Find and apply migration files
            import mind
            package_dir = os.path.dirname(mind.__file__)
            migrations_dir = os.path.join(package_dir, "..", "..", "migrations")

            if not os.path.exists(migrations_dir):
                # Try docker/init.sql
                init_sql = os.path.join(package_dir, "..", "..", "docker", "init.sql")
                if os.path.exists(init_sql):
                    print(f"  Applying {init_sql}")
                    with open(init_sql) as f:
                        sql = f.read()
                    await conn.execute(sql)
                    print("  Applied init.sql")
                else:
                    print("  No migration files found")
                return

            # Apply migrations in order
            migration_files = sorted([
                f for f in os.listdir(migrations_dir)
                if f.endswith(".sql")
            ])

            for filename in migration_files:
                filepath = os.path.join(migrations_dir, filename)
                print(f"  Applying {filename}...")
                with open(filepath) as f:
                    sql = f.read()
                await conn.execute(sql)

            print(f"  Applied {len(migration_files)} migration(s)")

        finally:
            await conn.close()

    asyncio.run(run())
    print()
    print("  Migration complete!")


def _mask_password(url: str) -> str:
    """Mask password in database URL for logging."""
    import re
    return re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", url)
