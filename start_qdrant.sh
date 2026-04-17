#!/bin/bash

# Start Qdrant as a background service

QDRANT_BIN="${HOME}/.qdrant/qdrant"
QDRANT_CONFIG="$(cd "$(dirname "$0")" && pwd)/qdrant_config.yaml"
QDRANT_STORAGE="$(cd "$(dirname "$0")" && pwd)/qdrant_storage"

if [ ! -f "$QDRANT_BIN" ]; then
    echo "Qdrant not found at $QDRANT_BIN"
    echo "Run './install_qdrant_local.sh' first"
    exit 1
fi

mkdir -p "$QDRANT_STORAGE"

echo "Starting Qdrant..."
"$QDRANT_BIN" --config-path "$QDRANT_CONFIG" > /dev/null 2>&1 &
QDRANT_PID=$!
echo $QDRANT_PID > .qdrant.pid

# Wait for Qdrant to be ready
echo "Waiting for Qdrant to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:6333/ > /dev/null; then
        echo "✓ Qdrant started successfully at http://localhost:6333"
        echo "  Dashboard: http://localhost:6333/dashboard"
        exit 0
    fi
    sleep 1
done

echo "✗ Qdrant failed to start"
exit 1
