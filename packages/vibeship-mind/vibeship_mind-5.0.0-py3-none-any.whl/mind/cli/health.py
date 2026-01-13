"""Mind health command - Check service health.

Checks the health of the Mind API server and its dependencies.

Usage:
    mind health                         # Check default localhost
    mind health --url http://mind:8000  # Check custom URL
"""

import sys


def health_command(url: str = "http://127.0.0.1:8000") -> None:
    """Check service health.

    Args:
        url: Mind API base URL
    """
    import httpx

    print(f"Checking Mind health at {url}")
    print()

    try:
        with httpx.Client(timeout=10.0) as client:
            # Main health check
            resp = client.get(f"{url}/health")

            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status", "unknown")
                tier = data.get("tier", "unknown")

                print(f"  Status: {_status_icon(status)} {status.upper()}")
                print(f"  Tier: {tier}")
                print()

                # Component health
                components = data.get("components", {})
                if components:
                    print("  Components:")
                    for name, healthy in components.items():
                        icon = _status_icon("healthy" if healthy else "unhealthy")
                        print(f"    {icon} {name}: {'healthy' if healthy else 'unhealthy'}")
                    print()

                # Version info
                version = data.get("version", "unknown")
                print(f"  Version: {version}")

                if status == "healthy":
                    print()
                    print("  All systems operational!")
                    sys.exit(0)
                else:
                    print()
                    print("  Some components are unhealthy.")
                    sys.exit(1)
            else:
                print(f"  Error: HTTP {resp.status_code}")
                print(f"  Response: {resp.text[:200]}")
                sys.exit(1)

    except httpx.ConnectError:
        print("  Status: Connection failed")
        print()
        print("  Cannot connect to Mind server.")
        print("  Start the server with: mind serve")
        sys.exit(1)
    except Exception as e:
        print(f"  Error: {e}")
        sys.exit(1)


def _status_icon(status: str) -> str:
    """Get status icon."""
    icons = {
        "healthy": "✓",
        "unhealthy": "✗",
        "unknown": "?",
    }
    return icons.get(status.lower(), "?")
