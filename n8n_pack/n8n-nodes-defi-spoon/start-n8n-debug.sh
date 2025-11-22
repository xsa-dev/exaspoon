#!/bin/bash

# Script to start n8n with debug logging enabled
# This will show detailed information about loaded nodes and packages

echo "Starting n8n with debug logging..."
echo ""
echo "Environment variables:"
echo "  N8N_LOG_LEVEL=debug"
echo "  N8N_LOG_OUTPUT=console"
echo ""

# Set debug logging
export N8N_LOG_LEVEL=debug
export N8N_LOG_OUTPUT=console

# Optional: Enable more verbose logging for node loading
export DEBUG=n8n:*

# Start n8n
n8n start

