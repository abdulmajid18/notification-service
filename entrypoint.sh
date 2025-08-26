#!/bin/sh

# Wait for PostgreSQL to be fully ready
sleep 2

echo "Starting FastAPI server..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload