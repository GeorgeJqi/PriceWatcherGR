#!/usr/bin/env bash
# Script εκκίνησης PriceWatcher GR
cd "$(dirname "$0")"
echo "🚀 Εκκίνηση του PriceWatcher GR στο http://localhost:8000 ..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
