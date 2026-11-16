"""Vercel Diagnostic Entrypoint for MealBridge."""

import os
import sys
from pathlib import Path
from fastapi import FastAPI

# Mark serverless environment
os.environ["VERCEL"] = "1"

# Add project root and src to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

for p in [str(ROOT_DIR), str(SRC_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

app = FastAPI()


@app.get("/")
async def root():
    try:
        from src.web.app import dashboard
        from fastapi import Request
        return {"status": "ok", "message": "MealBridge diagnostic probe alive"}
    except Exception:
        import traceback
        return {"status": "error", "traceback": traceback.format_exc()}


@app.get("/test")
async def test():
    return {"status": "ok", "python_version": sys.version}


handler = app
