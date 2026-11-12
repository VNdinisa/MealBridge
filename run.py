"""Entrypoint runner for the MealBridge Dispatcher Hub."""

import uvicorn

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Starting MealBridge Dispatcher Hub on http://127.0.0.1:8000")
    print("=" * 60 + "\n")
    uvicorn.run("src.web.app:app", host="127.0.0.1", port=8000, reload=True)
