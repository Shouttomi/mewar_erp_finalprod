# ============================================================
#  Downgrade Python 3.13 → 3.12 and reinstall requirements
#  Downloads Python 3.12.8 to D:\Python312
# ============================================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Python 3.12 Setup (D: Drive)         " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PYTHON312_URL = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
$INSTALLER     = "D:\python-3.12.8-amd64.exe"
$PYTHON312_DIR = "D:\Python312"

# ── Step 1: Download Python 3.12.8 ────────────────────────
if (Test-Path $PYTHON312_DIR) {
    Write-Host "[1/5] Python 3.12 already at $PYTHON312_DIR" -ForegroundColor Green
} else {
    Write-Host "[1/5] Downloading Python 3.12.8 (~25 MB) to D:\" -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $PYTHON312_URL -OutFile $INSTALLER -UseBasicParsing
    } catch {
        Write-Host "ERROR: Failed to download Python 3.12" -ForegroundColor Red
        exit 1
    }

    Write-Host "[1/5] Installing Python 3.12 to D:\Python312..." -ForegroundColor Yellow
    & $INSTALLER /quiet InstallAllUsers=0 DefaultJustForMeRegistry=1 TargetPath=$PYTHON312_DIR AssociateFiles=0 AssociatePythonFiles=0 | Out-Null
    Start-Sleep -Seconds 5

    if (Test-Path "$PYTHON312_DIR\python.exe") {
        Write-Host "[1/5] Python 3.12 installed successfully" -ForegroundColor Green
        Remove-Item $INSTALLER -Force -ErrorAction SilentlyContinue | Out-Null
    } else {
        Write-Host "ERROR: Python 3.12 installation failed" -ForegroundColor Red
        exit 1
    }
}

# ── Step 2: Verify Python 3.12 ─────────────────────────────
Write-Host "[2/5] Verifying Python 3.12..." -ForegroundColor Yellow
$pyVer = & $PYTHON312_DIR\python.exe --version 2>&1
Write-Host "      $pyVer" -ForegroundColor Green

# ── Step 3: Kill any running Python processes ──────────────
Write-Host "[3/5] Stopping any running Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process pythonw -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "[3/5] Processes stopped" -ForegroundColor Green

# ── Step 4: Upgrade pip and install requirements ───────────
Write-Host "[4/5] Installing dependencies with Python 3.12..." -ForegroundColor Yellow
Set-Location "d:\mewar_erp"

Write-Host "      Upgrading pip..." -ForegroundColor Gray
& $PYTHON312_DIR\python.exe -m pip install --upgrade pip setuptools wheel --quiet

Write-Host "      Installing from requirements.txt..." -ForegroundColor Gray
& $PYTHON312_DIR\python.exe -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Dependency installation failed" -ForegroundColor Red
    exit 1
}
Write-Host "[4/5] All dependencies installed" -ForegroundColor Green

# ── Step 5: Verify v2 modules ──────────────────────────────
Write-Host "[5/5] Testing v2 module imports..." -ForegroundColor Yellow
$testResult = & $PYTHON312_DIR\python.exe -c "from app.services.v2_ollama_engine import ask_local_llm; from app.routers.v2_chatbot import v2_chatbot; print('OK')" 2>&1

if ($testResult -contains "OK") {
    Write-Host "[5/5] All v2 modules import successfully" -ForegroundColor Green
} else {
    Write-Host "ERROR: Module import test failed" -ForegroundColor Red
    Write-Host $testResult -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!                       " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Python 3.12: $PYTHON312_DIR" -ForegroundColor White
Write-Host ""
Write-Host "Next: Update app/main.py to include v2_chatbot router" -ForegroundColor Yellow
Write-Host ""
