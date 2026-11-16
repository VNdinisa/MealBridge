"""Vercel Serverless Entrypoint for MealBridge."""

import os
import sys
from pathlib import Path

# Mark serverless environment
os.environ["VERCEL"] = "1"

# Add project root and src to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

for p in [str(ROOT_DIR), str(SRC_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.web.app import app

# Expose app and handler for Vercel ASGI runtime
handler = app
