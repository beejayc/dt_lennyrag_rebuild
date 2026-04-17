#!/bin/bash

# Check Qdrant service status

echo "Checking Qdrant status..."
if curl -s http://localhost:6333/ > /dev/null; then
    echo "✓ Qdrant is running at http://localhost:6333"

    # Get version info
    VERSION=$(curl -s http://localhost:6333/ | grep -o '"version":"[^"]*' | cut -d'"' -f4)
    echo "  Version: $VERSION"

    # Check collections
    COLLECTIONS=$(curl -s http://localhost:6333/collections | grep -o '"name":"[^"]*' | cut -d'"' -f4)
    if [ -n "$COLLECTIONS" ]; then
        echo "  Collections:"
        echo "$COLLECTIONS" | sed 's/^/    - /'
    else
        echo "  No collections yet"
    fi
else
    echo "✗ Qdrant is not running"
    echo "  Start it with: ./start_qdrant.sh"
    exit 1
fi
