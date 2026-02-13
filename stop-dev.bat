@echo off
REM WebRTC Video Conference App - Stop Development Servers Script (Windows)

echo.
echo ========================================
echo   Stopping Development Servers...
echo ========================================
echo.

REM Django Backend (Port 8000) を停止
echo [1/2] Stopping Django Backend Server (Port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo    Backend server stopped

echo.
echo [2/2] Stopping React Frontend Server (Port 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo    Frontend server stopped

echo.
echo ========================================
echo   All servers stopped successfully!
echo ========================================
echo.

pause
