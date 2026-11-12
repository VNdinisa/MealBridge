"""Vercel Serverless Entrypoint for MealBridge."""

import sys
from pathlib import Path

# Add workspace root to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.web.app import app
