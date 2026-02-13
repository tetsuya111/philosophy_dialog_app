#!/bin/bash

# WebRTC Video Conference App - Development Server Startup Script
# このスクリプトは、バックエンド(Django)とフロントエンド(React)の両方の開発サーバーを起動します

set -e

echo "🚀 Starting WebRTC Video Conference Development Servers..."

# 現在のディレクトリを保存
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# バックエンドの起動
echo ""
echo "📡 Starting Django Backend Server (Port 8000)..."
cd backend
python manage.py migrate --noinput || true
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!
echo "✓ Backend server started (PID: $BACKEND_PID)"

# フロントエンドの起動
cd "$SCRIPT_DIR"
echo ""
echo "🎨 Starting React Frontend Server (Port 3000)..."
cd frontend
BROWSER=none PORT=3000 npm start &
FRONTEND_PID=$!
echo "✓ Frontend server started (PID: $FRONTEND_PID)"

# プロセスIDを保存
cd "$SCRIPT_DIR"
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

echo ""
echo "✅ All servers started successfully!"
echo ""
echo "📋 Server Information:"
echo "   Backend API:  http://localhost:8000"
echo "   Frontend App: http://localhost:3000"
echo ""
echo "🛑 To stop servers, run: ./stop-dev.sh"
echo ""
echo "📝 Press Ctrl+C to view logs or run 'tail -f backend/logs/*.log' in another terminal"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
