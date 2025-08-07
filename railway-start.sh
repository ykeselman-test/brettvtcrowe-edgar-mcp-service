#!/bin/bash
# Railway startup script

# Set default port if not provided by Railway
if [ -z "$PORT" ]; then
    export PORT=8001
fi

echo "Starting Edgar MCP Service on port $PORT"
uvicorn main:app --host 0.0.0.0 --port $PORT