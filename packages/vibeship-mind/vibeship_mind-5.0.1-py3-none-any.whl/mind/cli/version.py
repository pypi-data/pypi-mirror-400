"""Mind version command - Show version information.

Displays Mind version and system information.

Usage:
    mind version
"""

import platform
import sys


def version_command() -> None:
    """Show version information."""
    # Get Mind version
    try:
        from importlib.metadata import version
        mind_version = version("mind")
    except Exception:
        mind_version = "5.0.0"  # Default fallback

    print()
    print(f"  Mind v{mind_version}")
    print()
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Platform: {platform.system()} {platform.machine()}")
    print()

    # Show dependency versions
    print("  Dependencies:")
    deps = [
        "fastapi",
        "uvicorn",
        "asyncpg",
        "sqlalchemy",
        "pydantic",
        "structlog",
    ]

    for dep in deps:
        try:
            from importlib.metadata import version
            v = version(dep)
            print(f"    {dep}: {v}")
        except Exception:
            print(f"    {dep}: not installed")

    print()
