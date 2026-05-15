# Standard Python 3.12.8 installer (not embeddable)
$ErrorActionPreference = "SilentlyContinue"

Write-Host ""
Write-Host "Downloading Python 3.12.8 installer..." -ForegroundColor Cyan

$url       = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
$installer = "D:\python-3.12.8-amd64.exe"

Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
Write-Host "Downloaded. Starting installation..." -ForegroundColor Green

# Install to D:\Python312, add to PATH
& $installer /quiet InstallAllUsers=0 PrependPath=0 TargetPath="D:\Python312" | Out-Null

Start-Sleep -Seconds 5

if (Test-Path "D:\Python312\python.exe") {
    Write-Host "Installation successful!" -ForegroundColor Green
    & "D:\Python312\python.exe" --version
    Remove-Item $installer -Force
} else {
    Write-Host "Installation failed or Python 3.12 not found at D:\Python312" -ForegroundColor Red
}
