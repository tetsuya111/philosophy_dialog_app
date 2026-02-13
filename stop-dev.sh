#!/bin/bash

# WebRTC Video Conference App - Stop Development Servers Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛑 Stopping WebRTC Video Conference Development Servers..."

# バックエンドの停止
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Stopping Backend Server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo "✓ Backend server stopped"
    fi
    rm .backend.pid
fi

# フロントエンドの停止
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping Frontend Server (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo "✓ Frontend server stopped"
    fi
    rm .frontend.pid
fi

# 念のため、ポートを使用しているプロセスを確認して停止
echo ""
echo "Checking for any remaining processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

echo ""
echo "✅ All servers stopped successfully!"
