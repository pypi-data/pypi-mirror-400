"""Mind serve command - Start the API server.

This command starts the Mind API server with automatic tier detection:

Standard tier (default):
- Uses embedded PostgreSQL if no DATABASE_URL is set
- Uses PostgreSQL for all storage (memory, events, vectors, causal graph)
- Uses APScheduler for background jobs

Enterprise tier (--tier enterprise):
- Requires Docker services (PostgreSQL, NATS, Qdrant, FalkorDB, Temporal)
- Uses dedicated services for each concern

Usage:
    mind serve                          # Start with embedded PostgreSQL
    mind serve --port 8080              # Custom port
    mind serve --database-url postgresql://...  # Use cloud PostgreSQL
    mind serve --tier enterprise        # Start in enterprise mode
"""

import os
import sys
from typing import Optional


def serve_command(
    host: str = "127.0.0.1",
    port: int = 8000,
    database_url: Optional[str] = None,
    reload: bool = False,
    tier: str = "standard",
) -> None:
    """Start the Mind API server.

    Args:
        host: Host to bind to
        port: Port to listen on
        database_url: PostgreSQL connection URL
        reload: Enable auto-reload for development
        tier: Deployment tier (standard or enterprise)
    """
    import structlog

    logger = structlog.get_logger()

    # Display startup banner
    print(_get_banner())
    print()

    # Set environment variables for the API
    if database_url:
        os.environ["MIND_DATABASE_URL"] = database_url

    os.environ["MIND_TIER"] = tier

    # Detect tier automatically if not explicitly set
    if tier == "standard":
        if database_url:
            logger.info(
                "starting_standard_tier",
                mode="cloud",
                database="external PostgreSQL",
            )
        else:
            logger.info(
                "starting_standard_tier",
                mode="local",
                database="embedded PostgreSQL",
            )
            print("  Using embedded PostgreSQL (data stored in ~/.mind/data/postgres)")
            print("  First run may take 1-2 minutes to download PostgreSQL binaries.")
            print()
    else:
        logger.info(
            "starting_enterprise_tier",
            note="Ensure Docker services are running",
        )
        print("  Enterprise tier requires Docker services.")
        print("  Run: docker-compose up -d")
        print()

    # Start the server
    try:
        import uvicorn

        print(f"  Starting server at http://{host}:{port}")
        print(f"  API docs: http://{host}:{port}/docs")
        print(f"  Health check: http://{host}:{port}/health")
        print()
        print("  Press Ctrl+C to stop")
        print()

        uvicorn.run(
            "mind.api.app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
        )
    except KeyboardInterrupt:
        print("\n  Shutting down...")
    except ImportError as e:
        print(f"Error: {e}")
        print("\nMake sure all dependencies are installed:")
        print("  pip install mind[dev]")
        sys.exit(1)


def _get_banner() -> str:
    """Get the Mind startup banner (ASCII-safe for Windows)."""
    return """
  +====================================================================+
  |                                                                    |
  |   M   M  III  N   N  DDD       V   V  555                          |
  |   MM MM   I   NN  N  D  D      V   V  5                            |
  |   M M M   I   N N N  D  D       V V   555                          |
  |   M   M   I   N  NN  D  D       V V     5                          |
  |   M   M  III  N   N  DDD         V    555                          |
  |                                                                    |
  |   Decision Intelligence for AI Agents                             |
  |                                                                    |
  +====================================================================+
"""
