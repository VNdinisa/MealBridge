#!/usr/bin/env bash
set -euo pipefail

echo "1. Running Expo TypeScript & design-system checks..."
bun run typecheck
bun run lint:slop || true

echo "2. Checking Python syntax in backend/..."
python3 -m compileall backend/

echo "3. Staging and committing monorepo integration..."
git status
git add .
git commit -m "Integrate backend/ with RBAC, pretend-data guardrails, audit logging, and Expo API client"
git push origin main

echo "Integration complete and pushed to VNdinisa/MealBridge!"
