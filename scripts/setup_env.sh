#!/usr/bin/env bash
set -euo pipefail
# Usage: bash scripts/setup_env.sh
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
: "# Use sqlite by default if DATABASE_URL or SQLALCHEMY_DATABASE_URI not set"
if [ -z "${SQLALCHEMY_DATABASE_URI:-}" ] && [ -z "${DATABASE_URL:-}" ]; then
  export SQLALCHEMY_DATABASE_URI=sqlite:///dev.db
fi
python scripts/init_db.py

echo "Setup complete. Start server: python -m src.server and open http://localhost:5000"
