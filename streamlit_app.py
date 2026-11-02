"""Streamlit Cloud entry point for Online Course Completion Prediction.

Routes execution to dashboard/app.py while ensuring proper system path resolution
and environment configuration across both local and cloud deployments.
"""

import os
import sys
from pathlib import Path
import runpy

# Ensure repository root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Execute the dashboard application
if __name__ == "__main__" or True:
    app_path = ROOT_DIR / "dashboard" / "app.py"
    runpy.run_path(str(app_path), run_name="__main__")
