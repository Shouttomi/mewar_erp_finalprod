$ErrorActionPreference = "SilentlyContinue"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ollamaExe  = "$projectDir\ollama\ollama.exe"
$modelsDir  = "$projectDir\models"
$venvPython = "$projectDir\.venv\Scripts\python.exe"
$venvUvi    = "$projectDir\.venv\Scripts\uvicorn.exe"
$model      = "qwen2.5:32b"

Write-Host "Mewar ERP - Production Start" -ForegroundColor Cyan
Write-Host "Model : $model"               -ForegroundColor Yellow
Write-Host ""

# Verify setup was done
if (-not (Test-Path $ollamaExe)) {
    Write-Host "ERROR: Run setup_ollama_d.ps1 first!" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: Python venv missing. Run setup_ollama_d.ps1 first!" -ForegroundColor Red
    exit 1
}

# Start Ollama
$env:OLLAMA_MODELS = $modelsDir
$ollamaProc = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if ($ollamaProc) {
    Write-Host "[1/2] Ollama already running (PID $($ollamaProc.Id))" -ForegroundColor Green
} else {
    Write-Host "[1/2] Starting Ollama server..." -ForegroundColor Yellow
    Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Minimized -WorkingDirectory "$projectDir\ollama"
    Start-Sleep -Seconds 8
    Write-Host "[1/2] Ollama up at http://localhost:11434" -ForegroundColor Green
}

# Start FastAPI
Write-Host "[2/2] Starting FastAPI..." -ForegroundColor Yellow
Write-Host "  API  : http://localhost:8000"             -ForegroundColor White
Write-Host "  Docs : http://localhost:8000/docs"        -ForegroundColor White
Write-Host "  Chat : POST /v2-chatbot/"                 -ForegroundColor White
Write-Host "  Health: GET /v2-chatbot/status"           -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:LOCAL_MODEL     = $model
$env:OLLAMA_MODELS   = $modelsDir

Set-Location $projectDir
& $venvUvi app.main:app --host 0.0.0.0 --port 8000 --log-level info
