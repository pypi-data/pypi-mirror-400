"""Test MCP server with Standard tier.

This script:
1. Starts the API server with embedded PostgreSQL
2. Tests MCP tool imports
3. Tests calling MCP tools against the running API

Usage:
    python scripts/test_mcp_standard.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def test_mcp_imports():
    """Test that MCP server can be imported."""
    print("\n=== Testing MCP Imports ===")

    try:
        from mind.mcp.server import mcp, mind_health, mind_remember, mind_retrieve, mind_decide
        print("[OK] MCP server imported successfully")
        print(f"  - Server name: {mcp.name}")
        print(f"  - Tools: mind_remember, mind_retrieve, mind_decide, mind_health")
        return True
    except ImportError as e:
        print(f"[FAIL] Failed to import MCP server: {e}")
        return False


async def test_mcp_with_api():
    """Test MCP tools with running API."""
    print("\n=== Testing MCP with API ===")

    # Start API server (it creates its own container via lifespan)
    from mind.api.app import create_app
    import uvicorn
    import httpx
    import os

    # Force Standard tier
    os.environ["MIND_TIER"] = "standard"

    print("Starting API server (Standard tier will auto-init)...")

    # Create app - it will create container in lifespan
    app = create_app()

    # Run server in background task
    config = uvicorn.Config(app, host="127.0.0.1", port=8080, log_level="warning")
    server = uvicorn.Server(config)

    # Start server task
    server_task = asyncio.create_task(server.serve())

    # Wait for server to start (need more time for container init)
    await asyncio.sleep(5)

    try:
        # Test health endpoint directly via HTTP
        async with httpx.AsyncClient() as http:
            response = await http.get("http://127.0.0.1:8080/health", timeout=10.0)
            if response.status_code == 200:
                print(f"[OK] API server healthy: {response.json()}")
            else:
                print(f"[FAIL] API health check failed: {response.status_code}")
                return False

        # Test MCP tool by calling it
        from mind.mcp.server import mind_health
        result = await mind_health()
        print(f"[OK] MCP mind_health tool returned: {result}")

        return True

    except Exception as e:
        print(f"[FAIL] MCP test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Shutdown
        print("\nShutting down...")
        server.should_exit = True

        # Cancel server task with timeout
        try:
            await asyncio.wait_for(server_task, timeout=10.0)
        except asyncio.TimeoutError:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

        print("[OK] Shutdown complete")


async def main():
    """Run all MCP tests."""
    print("=" * 50)
    print("Mind MCP Server Test with Standard Tier")
    print("=" * 50)

    # Test imports first
    if not await test_mcp_imports():
        print("\n[FAILED] MCP import test failed")
        return 1

    # Test with API
    if not await test_mcp_with_api():
        print("\n[FAILED] MCP with API test failed")
        return 1

    print("\n" + "=" * 50)
    print("[SUCCESS] All MCP tests passed!")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
