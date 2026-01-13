"""FalkorDB client management.

FalkorDB is a graph database built on Redis that provides:
- Property graph model for causal relationships
- Cypher query language for graph traversal
- High performance for causal path analysis
"""

import structlog
from falkordb import FalkorDB

from mind.config import get_settings

logger = structlog.get_logger()

# Global client instance
_falkordb_client: FalkorDB | None = None
_graph_name = "mind_causal"


async def get_falkordb_client() -> FalkorDB:
    """Get or create FalkorDB client instance.

    Returns a connected FalkorDB client. The client is cached
    for reuse across requests.

    Raises:
        ValueError: If FalkorDB is not configured
    """
    global _falkordb_client

    if _falkordb_client is None:
        settings = get_settings()

        if not settings.falkordb_host:
            raise ValueError(
                "FalkorDB not configured. Set MIND_FALKORDB_HOST environment variable."
            )

        logger.info(
            "falkordb_connecting",
            host=settings.falkordb_host,
            port=settings.falkordb_port,
        )

        password = None
        if settings.falkordb_password:
            password = settings.falkordb_password.get_secret_value()

        _falkordb_client = FalkorDB(
            host=settings.falkordb_host,
            port=settings.falkordb_port,
            password=password,
        )

        logger.info("falkordb_connected")

    return _falkordb_client


async def close_falkordb_client() -> None:
    """Close FalkorDB client connection."""
    global _falkordb_client

    if _falkordb_client is not None:
        try:
            # FalkorDB uses Redis connection underneath
            if hasattr(_falkordb_client, "connection") and _falkordb_client.connection:
                _falkordb_client.connection.close()
            elif hasattr(_falkordb_client, "close"):
                _falkordb_client.close()
        except Exception as e:
            logger.warning("falkordb_close_error", error=str(e))
        finally:
            _falkordb_client = None
            logger.info("falkordb_disconnected")


async def check_falkordb_health() -> tuple[bool, str]:
    """Check FalkorDB health by executing a ping.

    Returns:
        Tuple of (is_healthy, status_message)
    """
    global _falkordb_client

    if _falkordb_client is None:
        return False, "not_configured"

    try:
        # FalkorDB is built on Redis, so we can use PING
        # The underlying connection object supports Redis commands
        connection = _falkordb_client.connection
        response = connection.ping()
        if response:
            return True, "connected"
        return False, "ping_failed"
    except Exception as e:
        logger.warning("falkordb_health_check_failed", error=str(e))
        return False, f"error: {str(e)}"


async def ensure_schema(client: FalkorDB, graph_name: str = _graph_name) -> None:
    """Ensure graph schema exists with proper indexes.

    Creates indexes for efficient causal graph queries.

    Args:
        client: FalkorDB client
        graph_name: Name of the graph (default: mind_causal)
    """
    graph = client.select_graph(graph_name)

    # Create indexes for common query patterns
    try:
        # Index on Memory nodes for fast lookup by memory_id
        graph.query("CREATE INDEX FOR (m:Memory) ON (m.memory_id)")
        logger.info("falkordb_index_created", index="Memory.memory_id")
    except Exception:
        # Index may already exist
        pass

    try:
        # Index on Decision nodes
        graph.query("CREATE INDEX FOR (d:Decision) ON (d.trace_id)")
        logger.info("falkordb_index_created", index="Decision.trace_id")
    except Exception:
        pass

    try:
        # Index on Outcome nodes
        graph.query("CREATE INDEX FOR (o:Outcome) ON (o.trace_id)")
        logger.info("falkordb_index_created", index="Outcome.trace_id")
    except Exception:
        pass

    try:
        # Index for user filtering
        graph.query("CREATE INDEX FOR (m:Memory) ON (m.user_id)")
        logger.info("falkordb_index_created", index="Memory.user_id")
    except Exception:
        pass

    logger.info("falkordb_schema_ensured", graph=graph_name)
