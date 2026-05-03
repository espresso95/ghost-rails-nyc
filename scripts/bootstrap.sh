#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

if [ ! -f ".env" ]; then
  cp .env.example .env
fi

cd "$ROOT_DIR/backend"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/build_index.py

cd "$ROOT_DIR/frontend"
npm install
npm run build

echo "Bootstrap complete"

