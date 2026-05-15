$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ollamaExe  = "$projectDir\ollama\ollama.exe"
$modelsDir  = "$projectDir\models"
$MODEL      = if ($env:LOCAL_MODEL) { $env:LOCAL_MODEL } else { "qwen2.5:32b" }

Write-Host "Mewar ERP - Model Download" -ForegroundColor Cyan
Write-Host "Model   : $MODEL" -ForegroundColor Yellow
Write-Host "Storage : $modelsDir" -ForegroundColor White
Write-Host ""

if (-not (Test-Path $ollamaExe)) {
    Write-Host "ERROR: Ollama not found. Run setup_ollama_d.ps1 first." -ForegroundColor Red
    exit 1
}

$running = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if (-not $running) {
    Write-Host "Starting Ollama server..." -ForegroundColor Yellow
    $env:OLLAMA_MODELS = $modelsDir
    Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Minimized -WorkingDirectory "$projectDir\ollama"
    Start-Sleep -Seconds 6
    Write-Host "Ollama running at http://localhost:11434" -ForegroundColor Green
}

$env:OLLAMA_MODELS = $modelsDir
Write-Host "Pulling $MODEL -- progress shown below." -ForegroundColor Cyan
Write-Host "30-90 min on fast internet. Ctrl+C to pause." -ForegroundColor Gray
Write-Host ""

& $ollamaExe pull $MODEL

Write-Host ""
Write-Host "Model downloaded! Run: .\start_prod.ps1" -ForegroundColor Green
