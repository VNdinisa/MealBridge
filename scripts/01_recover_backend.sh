#!/usr/bin/env bash
set -euo pipefail

echo "1. Fetching latest upstream history..."
git fetch upstream

# Find the last commit from sadeeqdahuwa/mealbridge before the replacement merge
UPSTREAM_BASE=$(git rev-list --parents -n 1 upstream/main | awk '{print $3}')
if [ -z "$UPSTREAM_BASE" ]; then
  UPSTREAM_BASE="upstream/main"
fi

echo "2. Inspecting files in commit: $UPSTREAM_BASE"
git ls-tree -r --name-only "$UPSTREAM_BASE"

echo "3. Extracting original Python backend into ./backend/..."
mkdir -p backend
git archive "$UPSTREAM_BASE" | tar -x -C backend/

# Remove duplicate lockfile if standardizing on bun
if [ -f "package-lock.json" ] && [ -f "bun.lock" ]; then
  echo "4. Removing duplicate package-lock.json (keeping bun.lock)..."
  rm -f package-lock.json
fi

echo "Done! Contents of ./backend/:"
ls -la backend/
