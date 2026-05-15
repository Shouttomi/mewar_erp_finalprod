# ============================================================
#  Setup Python 3.12 Portable (embeddable)
#  No installation needed — just extract and use
# ============================================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Python 3.12 Portable Setup (D:)      " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PYTHON_URL    = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip"
$ZIP_PATH      = "D:\python-3.12.8-embed-amd64.zip"
$PYTHON_DIR    = "D:\Python312"

# ── Step 1: Download ───────────────────────────────────────
if (Test-Path $PYTHON_DIR) {
    Write-Host "[1/5] Python 3.12 portable already at $PYTHON_DIR" -ForegroundColor Green
} else {
    Write-Host "[1/5] Downloading Python 3.12.8 embeddable (~28 MB)..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $PYTHON_URL -OutFile $ZIP_PATH -UseBasicParsing
        Write-Host "[1/5] Downloaded to $ZIP_PATH" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Download failed. Check internet." -ForegroundColor Red
        exit 1
    }

    # ── Step 2: Extract ────────────────────────────────────
    Write-Host "[2/5] Extracting to $PYTHON_DIR..." -ForegroundColor Yellow
    Expand-Archive -Path $ZIP_PATH -DestinationPath $PYTHON_DIR -Force
    Remove-Item $ZIP_PATH -Force

    if (-not (Test-Path "$PYTHON_DIR\python.exe")) {
        Write-Host "ERROR: Extraction failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "[2/5] Extracted successfully" -ForegroundColor Green
}

# ── Step 3: Setup pip ──────────────────────────────────────
Write-Host "[3/5] Setting up pip..." -ForegroundColor Yellow
$PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
$GET_PIP = "$PYTHON_DIR\get-pip.py"

if (-not (Test-Path "$PYTHON_DIR\Scripts\pip.exe")) {
    Invoke-WebRequest -Uri $PIP_URL -OutFile $GET_PIP -UseBasicParsing
    & $PYTHON_DIR\python.exe $GET_PIP --quiet
    Remove-Item $GET_PIP -Force

    if (Test-Path "$PYTHON_DIR\Scripts\pip.exe") {
        Write-Host "[3/5] pip installed" -ForegroundColor Green
    } else {
        Write-Host "ERROR: pip setup failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[3/5] pip already configured" -ForegroundColor Green
}

# ── Step 4: Install requirements ───────────────────────────
Write-Host "[4/5] Installing dependencies..." -ForegroundColor Yellow
Set-Location "d:\mewar_erp"

& $PYTHON_DIR\python.exe -m pip install --upgrade pip setuptools wheel --quiet
& $PYTHON_DIR\python.exe -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Installation failed" -ForegroundColor Red
    exit 1
}
Write-Host "[4/5] Dependencies installed" -ForegroundColor Green

# ── Step 5: Test imports ───────────────────────────────────
Write-Host "[5/5] Testing v2 module imports..." -ForegroundColor Yellow
$testResult = & $PYTHON_DIR\python.exe -c "from app.services.v2_ollama_engine import ask_local_llm; from app.routers.v2_chatbot import v2_chatbot; print('SUCCESS')" 2>&1

if ($testResult -match "SUCCESS") {
    Write-Host "[5/5] All v2 modules import successfully" -ForegroundColor Green
} else {
    Write-Host "ERROR: Import test failed:" -ForegroundColor Red
    Write-Host $testResult -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!                       " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Python 3.12: $PYTHON_DIR" -ForegroundColor White
Write-Host ""
Write-Host "Verify installation:" -ForegroundColor Yellow
Write-Host "  $PYTHON_DIR\python.exe --version" -ForegroundColor White
Write-Host ""
