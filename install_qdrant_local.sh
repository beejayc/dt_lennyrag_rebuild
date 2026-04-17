#!/bin/bash

# Install Qdrant locally to ~/.qdrant/qdrant

QDRANT_DIR="${HOME}/.qdrant"
QDRANT_BIN="${QDRANT_DIR}/qdrant"

if [ -f "$QDRANT_BIN" ]; then
    echo "Qdrant already installed at $QDRANT_BIN"
    exit 0
fi

echo "Installing Qdrant to $QDRANT_DIR..."
mkdir -p "$QDRANT_DIR"

# Detect OS
OS=$(uname -s)
ARCH=$(uname -m)

if [ "$OS" = "Darwin" ]; then
    if [ "$ARCH" = "arm64" ]; then
        URL="https://github.com/qdrant/qdrant/releases/download/v1.8.0/qdrant-x86_64-apple-darwin"
    else
        URL="https://github.com/qdrant/qdrant/releases/download/v1.8.0/qdrant-x86_64-apple-darwin"
    fi
elif [ "$OS" = "Linux" ]; then
    if [ "$ARCH" = "aarch64" ]; then
        URL="https://github.com/qdrant/qdrant/releases/download/v1.8.0/qdrant-aarch64-unknown-linux-gnu"
    else
        URL="https://github.com/qdrant/qdrant/releases/download/v1.8.0/qdrant-x86_64-unknown-linux-gnu"
    fi
else
    echo "Unsupported OS: $OS"
    exit 1
fi

echo "Downloading Qdrant from $URL..."
curl -L "$URL" -o "$QDRANT_BIN"
chmod +x "$QDRANT_BIN"

echo "Qdrant installed successfully at $QDRANT_BIN"
echo "Run './start_qdrant.sh' to start the service"
