# Complete Python 3.12 + Requirements Setup

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Complete Setup: Python 3.12 + Requirements        " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python 3.12 exists
if (Test-Path "D:\Python312\python.exe") {
    Write-Host "[OK] Python 3.12 found at D:\Python312" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Python 3.12 not found. Run install_python312_standard.ps1 first." -ForegroundColor Red
    exit 1
}

$PY312 = "D:\Python312\python.exe"

# Verify version
$ver = & $PY312 --version
Write-Host "      Version: $ver" -ForegroundColor Green

# Upgrade pip
Write-Host ""
Write-Host "[1/3] Upgrading pip..." -ForegroundColor Yellow
& $PY312 -m pip install --upgrade pip setuptools wheel -q 2>&1 | Out-Null
Write-Host "[1/3] pip upgraded" -ForegroundColor Green

# Install requirements
Write-Host "[2/3] Installing requirements.txt..." -ForegroundColor Yellow
Set-Location "D:\mewar_erp"
& $PY312 -m pip install -r requirements.txt 2>&1 | Select-String -Pattern "Successfully|ERROR|error" -ErrorAction SilentlyContinue
Write-Host "[2/3] requirements installed" -ForegroundColor Green

# Test imports
Write-Host "[3/3] Testing v2 module imports..." -ForegroundColor Yellow
$testCmd = @"
try:
    from app.services.v2_ollama_engine import ask_local_llm, health_check
    from app.routers.v2_chatbot import v2_chatbot
    print('SUCCESS: All v2 modules imported')
except Exception as e:
    print(f'FAIL: {e}')
    exit(1)
"@

$output = & $PY312 -c $testCmd 2>&1
Write-Host "      $output" -ForegroundColor Green

if ($output -match "SUCCESS") {
    Write-Host "[3/3] Import test passed" -ForegroundColor Green
} else {
    Write-Host "[3/3] Import test FAILED" -ForegroundColor Red
    Write-Host $output -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  All Setup Complete!                               " -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Update app/main.py to include v2_chatbot router:" -ForegroundColor White
Write-Host "   from app.routers.v2_chatbot import router as v2_chatbot_router" -ForegroundColor Gray
Write-Host "   app.include_router(v2_chatbot_router)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start Ollama server (in a separate terminal):" -ForegroundColor White
Write-Host "   D:\Ollama\ollama.exe serve" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Run setup_ollama_d.ps1 to download qwen2.5:7b (~4.7GB):" -ForegroundColor White
Write-Host "   powershell -ExecutionPolicy Bypass -File setup_ollama_d.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Start FastAPI server:" -ForegroundColor White
Write-Host "   D:\Python312\python.exe -m uvicorn app.main:app --reload --port 8000" -ForegroundColor Gray
Write-Host ""
