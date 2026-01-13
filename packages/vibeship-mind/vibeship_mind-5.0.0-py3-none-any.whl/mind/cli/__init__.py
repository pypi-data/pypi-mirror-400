"""Mind CLI - Command-line interface for Mind v5.

Commands:
    mind up      - One-command start: setup + serve
    mind setup   - Download PostgreSQL, pgvector, initialize database
    mind serve   - Start the Mind API server
    mind migrate - Run database migrations
    mind demo    - Interactive learning loop demo
    mind health  - Check service health
    mind worker  - Manage background jobs

Quick Start:
    $ pip install mind-v5
    $ mind up                       # Downloads everything and starts Mind

Usage:
    $ mind setup                    # Setup PostgreSQL and pgvector
    $ mind serve                    # Start with embedded PostgreSQL
    $ mind serve --port 8080        # Custom port
    $ mind migrate                  # Apply migrations
    $ mind demo                     # Interactive demo
    $ mind worker status            # Check scheduled jobs
    $ mind worker run consolidation # Run a job manually
"""

import argparse
import asyncio
import sys
from typing import Optional


def cli() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="mind",
        description="Mind v5 - Decision intelligence for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mind serve              Start the API server (auto-starts embedded PostgreSQL)
  mind serve --port 8080  Start on a custom port
  mind migrate            Apply database migrations
  mind demo               Run an interactive learning loop demo
  mind health             Check if the server is healthy
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # serve command
    serve_parser = subparsers.add_parser(
        "serve",
        help="Start the Mind API server",
    )
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen on (default: 8000)",
    )
    serve_parser.add_argument(
        "--database-url",
        dest="database_url",
        help="PostgreSQL connection URL (uses embedded PG if not set)",
    )
    serve_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    serve_parser.add_argument(
        "--tier",
        choices=["standard", "enterprise"],
        default="standard",
        help="Deployment tier (default: standard)",
    )

    # migrate command
    migrate_parser = subparsers.add_parser(
        "migrate",
        help="Run database migrations",
    )
    migrate_parser.add_argument(
        "--database-url",
        dest="database_url",
        help="PostgreSQL connection URL",
    )
    migrate_parser.add_argument(
        "--revision",
        default="head",
        help="Target revision (default: head)",
    )

    # demo command
    subparsers.add_parser(
        "demo",
        help="Run an interactive learning loop demo",
    )

    # health command
    health_parser = subparsers.add_parser(
        "health",
        help="Check service health",
    )
    health_parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000",
        help="Mind API base URL (default: http://127.0.0.1:8000)",
    )

    # version command
    subparsers.add_parser(
        "version",
        help="Show version information",
    )

    # setup command - one-command install
    setup_parser = subparsers.add_parser(
        "setup",
        help="Download PostgreSQL, pgvector, and initialize database",
    )
    setup_parser.add_argument(
        "--skip-postgres",
        action="store_true",
        help="Skip PostgreSQL download (use existing installation)",
    )
    setup_parser.add_argument(
        "--skip-pgvector",
        action="store_true",
        help="Skip pgvector download",
    )
    setup_parser.add_argument(
        "--skip-db-init",
        action="store_true",
        help="Skip database initialization",
    )

    # up command - setup + serve
    up_parser = subparsers.add_parser(
        "up",
        help="Setup everything and start the server (one-command start)",
    )
    up_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    up_parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to listen on (default: 8001)",
    )
    up_parser.add_argument(
        "--skip-setup",
        action="store_true",
        help="Skip setup step (assume already configured)",
    )

    # worker command
    worker_parser = subparsers.add_parser(
        "worker",
        help="Manage background jobs",
    )
    worker_parser.add_argument(
        "action",
        choices=["status", "run"],
        default="status",
        nargs="?",
        help="Action: status (show jobs) or run (execute job)",
    )
    worker_parser.add_argument(
        "--job",
        dest="job_name",
        help="Job name to run (consolidation, expiration, promotion, pattern_detection, cleanup)",
    )
    worker_parser.add_argument(
        "--all",
        dest="run_all",
        action="store_true",
        help="Run all jobs",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # Dispatch to command handlers
    if args.command == "serve":
        from mind.cli.serve import serve_command
        serve_command(
            host=args.host,
            port=args.port,
            database_url=args.database_url,
            reload=args.reload,
            tier=args.tier,
        )
    elif args.command == "migrate":
        from mind.cli.migrate import migrate_command
        migrate_command(
            database_url=args.database_url,
            revision=args.revision,
        )
    elif args.command == "demo":
        from mind.cli.demo import demo_command
        asyncio.run(demo_command())
    elif args.command == "health":
        from mind.cli.health import health_command
        health_command(url=args.url)
    elif args.command == "version":
        from mind.cli.version import version_command
        version_command()
    elif args.command == "setup":
        from mind.cli.setup import setup_command
        asyncio.run(setup_command(
            skip_postgres=args.skip_postgres,
            skip_pgvector=args.skip_pgvector,
            skip_db_init=args.skip_db_init,
        ))
    elif args.command == "up":
        from mind.cli.setup import up_command
        asyncio.run(up_command(
            host=args.host,
            port=args.port,
            skip_setup=args.skip_setup,
        ))
    elif args.command == "worker":
        from mind.cli.worker import worker_command
        worker_command(
            action=args.action or "status",
            job_name=args.job_name,
            run_all=args.run_all,
        )
    else:
        parser.print_help()
        sys.exit(1)
