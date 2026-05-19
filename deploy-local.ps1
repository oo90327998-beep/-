param(
    [switch]$Stop
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Resume Studio Deploy Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $scriptDir "backend"
$frontendDir = Join-Path $scriptDir "frontend"

if ($Stop) {
    Write-Host "Stopping all services..." -ForegroundColor Yellow
    Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "Services stopped" -ForegroundColor Green
    exit 0
}

Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    Write-Host "[Error] Python not found" -ForegroundColor Red
    exit 1
}
Write-Host "  Using: $pythonCmd" -ForegroundColor Green

Write-Host "[2/4] Checking Node.js..." -ForegroundColor Yellow
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "[Error] Node.js not found" -ForegroundColor Red
    exit 1
}
$nodeVersion = node -v
Write-Host "  Version: $nodeVersion" -ForegroundColor Green

Write-Host "[3/4] Installing dependencies..." -ForegroundColor Yellow
Write-Host "  Backend..." -ForegroundColor Cyan
Push-Location $backendDir
try { & $pythonCmd -m pip install -r requirements.txt --quiet } catch {}
Pop-Location

Write-Host "  Frontend..." -ForegroundColor Cyan
Push-Location $frontendDir
if (-not (Test-Path "node_modules")) {
    try { npm install --silent } catch {}
} else {
    Write-Host "    node_modules exists, skip" -ForegroundColor DarkGray
}
Pop-Location

Write-Host "[4/4] Starting services..." -ForegroundColor Yellow

Start-Process -FilePath $pythonCmd -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory $backendDir -WindowStyle Hidden
Start-Process -FilePath "npm" -ArgumentList "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173" -WorkingDirectory $frontendDir -WindowStyle Hidden

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Deploy Success!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Stop: .\deploy-local.ps1 -Stop" -ForegroundColor Cyan
Write-Host ""
