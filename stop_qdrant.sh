#!/bin/bash

# Stop Qdrant service

if [ -f .qdrant.pid ]; then
    PID=$(cat .qdrant.pid)
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping Qdrant (PID: $PID)..."
        kill "$PID"
        rm .qdrant.pid
        echo "✓ Qdrant stopped"
    else
        echo "Qdrant is not running"
        rm -f .qdrant.pid
    fi
else
    echo "No .qdrant.pid file found"
    # Try to kill by process name
    pkill -f "qdrant" && echo "✓ Qdrant stopped" || echo "Qdrant not running"
fi
