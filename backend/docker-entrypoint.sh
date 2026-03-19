#!/bin/sh
# Backend Docker entrypoint
# 1. Waits for MongoDB to be ready
# 2. Auto-trains ML models if .pkl files are missing
# 3. Starts uvicorn

set -e

echo "[ENTRYPOINT] Waiting for MongoDB..."
until python -c "import pymongo; pymongo.MongoClient('${MONGO_URI:-mongodb://mongo:27017}', serverSelectionTimeoutMS=2000).admin.command('ping')" 2>/dev/null; do
  echo "[ENTRYPOINT] MongoDB not ready -- retrying in 2s"
  sleep 2
done
echo "[ENTRYPOINT] MongoDB is up"

# Train models if not already present
MODEL_DIR="models/saved"
if [ ! -f "$MODEL_DIR/isolation_forest.pkl" ] || [ ! -f "$MODEL_DIR/random_forest.pkl" ]; then
  echo "[ENTRYPOINT] ML models not found -- training now (30-60 seconds)..."
  python models/train_models.py
  echo "[ENTRYPOINT] ML models trained successfully"
else
  echo "[ENTRYPOINT] ML models found -- skipping training"
fi

echo "[ENTRYPOINT] Starting FastAPI backend..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
