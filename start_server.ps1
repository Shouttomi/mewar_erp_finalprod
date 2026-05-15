# Start FastAPI server with v2_chatbot
Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Starting Mewar ERP FastAPI Server                 " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

$env:PYTHONIOENCODING = "utf-8"

Set-Location "D:\mewar_erp"

Write-Host "Endpoint         : http://localhost:8000" -ForegroundColor Green
Write-Host "V2 Chatbot       : POST http://localhost:8000/v2-chatbot/" -ForegroundColor Green
Write-Host "V2 Health Check  : GET  http://localhost:8000/v2-chatbot/status" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop server." -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
