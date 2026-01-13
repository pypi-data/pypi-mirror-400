#!/usr/bin/env python3
"""Launch the Mind v5 Admin Dashboard.

Usage:
    python scripts/run_dashboard.py
    # or
    streamlit run src/mind/dashboard/app.py
"""

import subprocess
import sys
import os

def main():
    # Ensure we're in the right directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    # Add src to path
    sys.path.insert(0, os.path.join(project_root, "src"))

    # Run streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "src/mind/dashboard/app.py",
        "--server.port", "8501",
        "--theme.base", "dark",
        "--theme.primaryColor", "#6366f1",
        "--theme.backgroundColor", "#0a0a0f",
        "--theme.secondaryBackgroundColor", "#12121a",
        "--theme.textColor", "#f8fafc",
    ])

if __name__ == "__main__":
    main()
