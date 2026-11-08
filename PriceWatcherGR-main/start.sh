#!/usr/bin/env bash
# Script εκκίνησης PriceWatcher GR
cd "$(dirname "$0")"
if [[ -x ".venv/bin/python" ]]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi
echo "🚀 Εκκίνηση του PriceWatcher GR στο http://localhost:8000 ..."
exec "$PYTHON" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
