"""Vercel Serverless Entrypoint for MealBridge."""

import os
import sys
from pathlib import Path

# Mark serverless environment
os.environ["VERCEL"] = "1"

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.web.app import app
