@echo off
REM Simple startup script - Opens servers in separate windows

echo Starting WebRTC Video Conference App...
echo.

REM Start Backend
echo Starting Backend Server...
start "Backend (Django)" cmd /k "cd /d %~dp0backend && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start Frontend
echo Starting Frontend Server...
start "Frontend (React)" cmd /k "cd /d %~dp0frontend && set BROWSER=none && npm start"

echo.
echo Servers are starting...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Close the server windows to stop them.
echo.

timeout /t 8 /nobreak >nul
start http://localhost:3000
