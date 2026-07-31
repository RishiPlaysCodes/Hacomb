@echo off
REM ============================================================
REM   VIGIL LABS - One-Command Launcher (Windows)
REM   Double-click this file OR run: START.bat
REM ============================================================
title VIGIL LABS Launcher
color 0b

echo.
echo  ============================================================
echo    VIGIL LABS - Starting up...
echo  ============================================================
echo.

cd /d "%~dp0"

REM ---- Backend setup ----
cd backend

if not exist "venv\" (
    echo  [1/4] Creating Python virtual environment...
    python -m venv venv
)

echo  [2/4] Activating environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

if not exist ".env" (
    echo  [*] Creating .env file...
    copy .env.example .env >nul
    echo  [!] IMPORTANT: Open backend\.env and set your SECRET_KEY and GEMINI_API_KEY
)

echo  [3/4] Starting backend server (new window)...
start "VIGIL LABS - Backend" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate.bat && python start.py"

cd ..

REM ---- Frontend setup ----
cd frontend

if not exist "node_modules\" (
    echo  [*] Installing frontend dependencies (first run, please wait)...
    call npm install
)

echo  [4/4] Starting frontend (new window)...
start "VIGIL LABS - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

cd ..

echo.
echo  ============================================================
echo    VIGIL LABS is starting!
echo.
echo    Backend:  http://localhost:8000
echo    Frontend: http://localhost:5173
echo.
echo    Open http://localhost:5173 in your browser.
echo    (Two new windows opened - keep them running)
echo  ============================================================
echo.
echo  Waiting 8 seconds then opening browser...
timeout /t 8 /nobreak >nul
start http://localhost:5173

echo.
echo  Done! You can close THIS window. Keep the other two open.
pause
