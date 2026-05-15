$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ollamaDir  = "$projectDir\ollama"
$modelsDir  = "$projectDir\models"
$ollamaExe  = "$ollamaDir\ollama.exe"
$venvDir    = "$projectDir\.venv"
$MODEL      = "qwen2.5:32b"

Write-Host "Mewar ERP - Setup (Steps 1-4 only)" -ForegroundColor Cyan
Write-Host "Project : $projectDir"               -ForegroundColor White
Write-Host ""

New-Item -ItemType Directory -Force -Path $ollamaDir | Out-Null
New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null

# Step 1: env vars
[System.Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $modelsDir, "User")
[System.Environment]::SetEnvironmentVariable("LOCAL_MODEL",   $MODEL,     "User")
[System.Environment]::SetEnvironmentVariable("OLLAMA_HOME",   $ollamaDir, "User")
$env:OLLAMA_MODELS = $modelsDir
$env:LOCAL_MODEL   = $MODEL
$env:OLLAMA_HOME   = $ollamaDir
Write-Host "[1/4] Env set." -ForegroundColor Green

# Step 2: Ollama binary
if (Test-Path $ollamaExe) {
    Write-Host "[2/4] Ollama binary already at $ollamaExe" -ForegroundColor Green
} else {
    Write-Host "[2/4] Downloading Ollama binary (~1 GB)..." -ForegroundColor Yellow
    $zipPath = "$ollamaDir\ollama_temp.zip"
    Invoke-WebRequest -Uri "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip" -OutFile $zipPath -UseBasicParsing
    Expand-Archive -Path $zipPath -DestinationPath $ollamaDir -Force
    Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
    Write-Host "[2/4] Ollama ready." -ForegroundColor Green
}

# Step 3: Python venv + pip
if (Test-Path "$venvDir\Scripts\python.exe") {
    Write-Host "[3/4] Python venv already exists." -ForegroundColor Green
} else {
    Write-Host "[3/4] Creating Python venv at $venvDir..." -ForegroundColor Yellow
    python -m venv $venvDir
    Write-Host "[3/4] Venv created." -ForegroundColor Green
}
Write-Host "[3/4] Installing Python dependencies..." -ForegroundColor Yellow
& "$venvDir\Scripts\pip.exe" install -r "$projectDir\requirements.txt" --quiet
Write-Host "[3/4] Dependencies installed." -ForegroundColor Green

# Step 4: Start Ollama server
$running = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if ($running) {
    Write-Host "[4/4] Ollama already running." -ForegroundColor Green
} else {
    Write-Host "[4/4] Starting Ollama server..." -ForegroundColor Yellow
    $env:OLLAMA_MODELS = $modelsDir
    Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Minimized -WorkingDirectory $ollamaDir
    Start-Sleep -Seconds 5
    Write-Host "[4/4] Ollama running at http://localhost:11434" -ForegroundColor Green
}

Write-Host ""
Write-Host "Infrastructure ready!" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEP: Switch to your fast internet connection, then run:" -ForegroundColor Yellow
Write-Host "  .\pull_model.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "That will download qwen2.5:32b (~20 GB)." -ForegroundColor Gray
