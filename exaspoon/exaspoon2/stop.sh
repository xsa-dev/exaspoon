#!/bin/bash

echo "🛑 Stopping all ExaspoonAi processes..."

# Find and terminate processes by name
pkill -f "exaspoon_mcp_gateway.py" 2>/dev/null || true
pkill -f "app.py" 2>/dev/null || true
pkill -f "uvicorn.*app:app" 2>/dev/null || true

# Find and terminate processes by PID
ps aux | grep -E "(app\.py|exaspoon_mcp|uvicorn)" | grep -v grep | while read line; do
    pid=$(echo $line | awk '{print $2}')
    echo "Killing process PID: $pid"
    kill $pid 2>/dev/null || true
done

# Wait 2 seconds
sleep 2

# Force kill remaining processes
ps aux | grep -E "(app\.py|exaspoon_mcp|uvicorn)" | grep -v grep | while read line; do
    pid=$(echo $line | awk '{print $2}')
    echo "Force killing process PID: $pid"
    kill -9 $pid 2>/dev/null || true
done

echo "✅ All ExaspoonAi processes stopped"
