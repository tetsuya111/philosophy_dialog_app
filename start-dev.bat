@echo off
REM WebRTC Video Conference App - Development Server Startup Script (Windows)
REM このスクリプトは、バックエンド(Django)とフロントエンド(React)の両方の開発サーバーを起動します

echo.
echo ========================================
echo   WebRTC Video Conference App
echo   Development Server Startup
echo ========================================
echo.

REM 現在のディレクトリを保存
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)
echo    Python: OK

echo.
echo [2/4] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo    Node.js: OK

echo.
echo [3/4] Starting Django Backend Server (Port 8000)...
cd "%SCRIPT_DIR%backend"

REM データベースマイグレーション実行
python manage.py migrate --noinput

REM バックエンドをバックグラウンドで起動
start "Django Backend" cmd /k "python manage.py runserver 0.0.0.0:8000"
timeout /t 3 /nobreak >nul
echo    Backend server started on http://localhost:8000

echo.
echo [4/4] Starting React Frontend Server (Port 3000)...
cd "%SCRIPT_DIR%frontend"

REM フロントエンドをバックグラウンドで起動
start "React Frontend" cmd /k "set BROWSER=none && set PORT=3000 && npm start"
timeout /t 5 /nobreak >nul
echo    Frontend server started on http://localhost:3000

echo.
echo ========================================
echo   All servers started successfully!
echo ========================================
echo.
echo Server Information:
echo   Backend API:  http://localhost:8000
echo   Frontend App: http://localhost:3000
echo.
echo To stop servers:
echo   - Close the Django Backend window
echo   - Close the React Frontend window
echo   - Or run: stop-dev.bat
echo.
echo Press any key to open the application in your browser...
pause >nul

REM ブラウザで開く
start http://localhost:3000

echo.
echo Application opened in browser!
echo.
