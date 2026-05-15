# Remove and reinstall Python 3.12 with pip included

$ErrorActionPreference = "SilentlyContinue"

Write-Host "Removing old Python 3.12 installation..." -ForegroundColor Yellow
Remove-Item -Path "D:\Python312" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Downloading Python 3.12.8 installer (with pip)..." -ForegroundColor Cyan
$url       = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
$installer = "D:\python-3.12.8-amd64.exe"

Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing

Write-Host "Installing to D:\Python312 (includes pip, setuptools)..." -ForegroundColor Green
$installArgs = @(
    "/quiet",
    "InstallAllUsers=0",
    "PrependPath=0",
    "TargetPath=D:\Python312",
    "Include_pip=1",
    "Include_dev=1",
    "Include_launcher=0",
    "AssociateFiles=0"
)
& $installer $installArgs | Out-Null

Start-Sleep -Seconds 5

if (Test-Path "D:\Python312\python.exe") {
    Write-Host "Installation successful!" -ForegroundColor Green
    & "D:\Python312\python.exe" --version

    # Check pip
    & "D:\Python312\python.exe" -m pip --version

    Remove-Item $installer -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "Installation failed!" -ForegroundColor Red
}
