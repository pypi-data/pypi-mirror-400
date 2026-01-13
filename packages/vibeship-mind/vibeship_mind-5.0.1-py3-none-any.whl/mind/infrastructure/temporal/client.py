"""Temporal client management."""

import structlog
from temporalio.client import Client

from mind.config import get_settings

logger = structlog.get_logger()


# Global client instance
_temporal_client: Client | None = None


async def get_temporal_client() -> Client:
    """Get or create Temporal client instance.

    Returns a connected Temporal client. The client is cached
    for reuse across requests.
    """
    global _temporal_client

    if _temporal_client is None:
        settings = get_settings()
        logger.info("temporal_connecting", host=settings.temporal_host)

        _temporal_client = await Client.connect(
            f"{settings.temporal_host}:{settings.temporal_port}",
            namespace=settings.temporal_namespace,
        )

        logger.info("temporal_connected")

    return _temporal_client


async def close_temporal_client() -> None:
    """Close Temporal client connection."""
    global _temporal_client

    if _temporal_client is not None:
        # Note: Temporal client doesn't have an explicit close method
        # but we clear the reference for cleanup
        _temporal_client = None
        logger.info("temporal_disconnected")


async def check_temporal_health() -> tuple[bool, str]:
    """Check Temporal health by verifying connection and namespace.

    Returns:
        Tuple of (is_healthy, status_message)
    """
    global _temporal_client

    try:
        # Try to connect if not already connected
        if _temporal_client is None:
            settings = get_settings()
            if not settings.temporal_host:
                return False, "not_configured"

            _temporal_client = await Client.connect(
                f"{settings.temporal_host}:{settings.temporal_port}",
                namespace=settings.temporal_namespace,
            )
            logger.info("temporal_connected_via_health_check")

        # Verify the namespace exists and is accessible
        settings = get_settings()
        namespace_info = await _temporal_client.service_client.operator_service.list_namespaces(
            request={}
        )
        # Check if our namespace is in the list
        namespace_names = [ns.namespace_info.name for ns in namespace_info.namespaces]
        if settings.temporal_namespace in namespace_names:
            return True, "connected"
        return False, f"namespace '{settings.temporal_namespace}' not found"
    except Exception as e:
        # Fallback: if we can't list namespaces, try a simpler check
        try:
            if _temporal_client is not None:
                # Just verify the connection is still valid
                await _temporal_client.service_client.check_health()
                return True, "connected"
        except Exception:
            pass
        logger.warning("temporal_health_check_failed", error=str(e))
        return False, f"error: {str(e)}"
