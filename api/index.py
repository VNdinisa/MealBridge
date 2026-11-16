"""Vercel Serverless Entrypoint for MealBridge."""

import os
import sys
import traceback
from pathlib import Path

# Mark serverless environment
os.environ["VERCEL"] = "1"

# Add project root and src to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
CWD = Path.cwd()

for p in [CWD, ROOT_DIR, SRC_DIR, Path(__file__).resolve().parent]:
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

try:
    from src.web.app import app
except BaseException:
    startup_error = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    app = FastAPI(title="MealBridge Startup Debugger")

    @app.get("/{catchall:path}", response_class=HTMLResponse)
    async def startup_debugger(catchall: str = ""):
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>MealBridge Startup Error</title></head>
        <body style="font-family: monospace; padding: 24px; background: #0f172a; color: #f87171;">
            <h1 style="color: #ef4444;">MealBridge Serverless Startup Error</h1>
            <p style="color: #94a3b8;">Python exception caught during application import:</p>
            <pre style="background: #1e293b; color: #f1f5f9; padding: 16px; border-radius: 8px; border: 1px solid #334155; overflow-x: auto;">{startup_error}</pre>
        </body>
        </html>
        """
