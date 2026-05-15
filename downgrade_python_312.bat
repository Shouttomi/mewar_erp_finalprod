@echo off
REM ============================================================
REM  Downgrade Python 3.13 → 3.12 and reinstall requirements
REM  Downloads Python 3.12.8 to D:\Python312
REM ============================================================

setlocal enabledelayedexpansion
cls

echo.
echo ========================================
echo  Python 3.12 Setup (D: Drive)
echo ========================================
echo.

REM ── Step 1: Download Python 3.12.8 ────────────────────────
set "PYTHON312_URL=https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
set "INSTALLER=D:\python-3.12.8-amd64.exe"
set "PYTHON312_DIR=D:\Python312"

if exist "%PYTHON312_DIR%" (
    echo [1/4] Python 3.12 already at %PYTHON312_DIR%
) else (
    echo [1/4] Downloading Python 3.12.8 (~25 MB^) to D:\ ...
    powershell -NoProfile -Command "Invoke-WebRequest -Uri '%PYTHON312_URL%' -OutFile '%INSTALLER%' -UseBasicParsing" >nul 2>&1
    if !errorlevel! neq 0 (
        echo ERROR: Failed to download Python 3.12. Check internet connection.
        pause
        exit /b 1
    )
    echo [1/4] Installing Python 3.12 to D:\Python312 ...
    "%INSTALLER%" /quiet InstallAllUsers=0 DefaultJustForMeRegistry=1 TargetPath="%PYTHON312_DIR%" AssociateFiles=0 AssociatePythonFiles=0 >nul 2>&1
    if !errorlevel! neq 0 (
        echo ERROR: Python 3.12 installation failed.
        pause
        exit /b 1
    )
    del "%INSTALLER%" /F /Q >nul 2>&1
    echo [1/4] Python 3.12 installed to %PYTHON312_DIR%
)

REM ── Step 2: Verify Python 3.12 ─────────────────────────────
echo [2/4] Verifying Python 3.12...
"%PYTHON312_DIR%\python.exe" --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Python 3.12 not found or not working.
    pause
    exit /b 1
)
echo [2/4] Python 3.12 verified:
"%PYTHON312_DIR%\python.exe" --version

REM ── Step 3: Kill any running Python processes ──────────────
echo [3/4] Stopping any running Python processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
timeout /T 2 /NOBREAK >nul 2>&1
echo [3/4] Processes stopped.

REM ── Step 4: Upgrade pip and install requirements ───────────
echo [4/4] Installing dependencies with Python 3.12...
cd /d "d:\mewar_erp"
"%PYTHON312_DIR%\python.exe" -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo       Installing from requirements.txt...
"%PYTHON312_DIR%\python.exe" -m pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo ERROR: Dependency installation failed. Check requirements.txt
    pause
    exit /b 1
)
echo [4/4] All dependencies installed.

REM ── Verify v2 modules ─────────────────────────────────────
echo.
echo [5/5] Testing v2 module imports...
"%PYTHON312_DIR%\python.exe" -c "from app.services.v2_ollama_engine import ask_local_llm; from app.routers.v2_chatbot import v2_chatbot; print('OK: All v2 modules import successfully')"
if !errorlevel! neq 0 (
    echo ERROR: Module import test failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo [*] Python 3.12: %PYTHON312_DIR%
echo [*] To use Python 3.12, update your PATH or run:
echo     %PYTHON312_DIR%\python.exe -m uvicorn app.main:app --reload
echo.
echo [*] FastAPI server command:
echo     cd d:\mewar_erp
echo     %PYTHON312_DIR%\python.exe -m uvicorn app.main:app --reload --port 8000
echo.
pause
