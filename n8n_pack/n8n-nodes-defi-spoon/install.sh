#!/bin/bash

# Installation script for n8n-nodes-defi-spoon
# This script installs the custom nodes package into ~/.n8n/nodes (correct location for custom nodes)

N8N_NODES_DIR="$HOME/.n8n/nodes"
PACKAGE_PATH="$(cd "$(dirname "$0")" && pwd)"
TGZ_FILE="$PACKAGE_PATH/n8n-nodes-defi-spoon-1.0.0.tgz"

echo "Installing n8n-nodes-defi-spoon..."
echo "Package: $TGZ_FILE"
echo "Target: $N8N_NODES_DIR"
echo ""

# Create .n8n/nodes directory if it doesn't exist
if [ ! -d "$N8N_NODES_DIR" ]; then
    echo "Creating $N8N_NODES_DIR..."
    mkdir -p "$N8N_NODES_DIR"
fi

# Check if package file exists
if [ ! -f "$TGZ_FILE" ]; then
    echo "Error: Package file not found: $TGZ_FILE"
    echo "Please build the package first: npm run build && npm pack"
    exit 1
fi

# Remove old installation if exists
OLD_INSTALL="$N8N_NODES_DIR/node_modules/n8n-nodes-defi-spoon"
if [ -d "$OLD_INSTALL" ]; then
    echo "Removing old installation..."
    rm -rf "$OLD_INSTALL"
fi

# Install the package
echo "Installing package to ~/.n8n/nodes..."
npm install "$TGZ_FILE" \
    --prefix "$N8N_NODES_DIR" \
    --legacy-peer-deps

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Installation successful!"
    echo ""
    echo "Next steps:"
    echo "1. Stop n8n if it's running (Ctrl+C)"
    echo "2. Restart n8n: n8n start"
    echo "3. The new nodes will appear in the node list:"
    echo "   - DeFi: Get Balance"
    echo "   - DeFi: Get Transaction"
    echo "   - DeFi: Get Wallet Transactions"
    echo "   - DeFi: Monitor Wallet Transactions"
    echo "   - Python Script (SpoonOS)"
else
    echo ""
    echo "✗ Installation failed!"
    exit 1
fi

