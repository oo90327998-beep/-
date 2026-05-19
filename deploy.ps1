<#
.SYNOPSIS
    Resume Studio 一键部署脚本 (Windows PowerShell)

.DESCRIPTION
    自动构建并启动 Resume Studio 的所有服务

.EXAMPLE
    .\deploy.ps1
    .\deploy.ps1 -Build
    .\deploy.ps1 -Stop
#>

param(
    [switch]$Build,
    [switch]$Stop,
    [switch]$Logs,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host @"
Resume Studio 一键部署脚本

用法:
    .\deploy.ps1          # 启动服务（如已存在则直接启动）
    .\deploy.ps1 -Build   # 重新构建并启动
    .\deploy.ps1 -Stop    # 停止所有服务
    .\deploy.ps1 -Logs    # 查看日志

服务地址:
    前端: http://localhost
    后端: http://localhost:8000
    API文档: http://localhost:8000/docs

"@
}

if ($Help) {
    Show-Help
    exit 0
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Resume Studio 一键部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[错误] Docker 未安装，请先安装 Docker Desktop" -ForegroundColor Red
    Write-Host "下载地址: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue) -and 
    -not (docker compose version 2>$null)) {
    Write-Host "[错误] Docker Compose 未安装" -ForegroundColor Red
    exit 1
}

$dockerCompose = "docker compose"
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    $dockerCompose = "docker-compose"
}

if ($Stop) {
    Write-Host "[1/2] 停止服务..." -ForegroundColor Yellow
    Invoke-Expression "$dockerCompose down"
    Write-Host "[2/2] 清理完成" -ForegroundColor Green
    Write-Host ""
    Write-Host "服务已停止" -ForegroundColor Green
    exit 0
}

if ($Logs) {
    Write-Host "查看日志 (Ctrl+C 退出)..." -ForegroundColor Yellow
    Invoke-Expression "$dockerCompose logs -f"
    exit 0
}

if ($Build) {
    Write-Host "[1/3] 停止旧容器..." -ForegroundColor Yellow
    Invoke-Expression "$dockerCompose down"
    
    Write-Host "[2/3] 构建镜像..." -ForegroundColor Yellow
    Invoke-Expression "$dockerCompose build --no-cache"
    
    Write-Host "[3/3] 启动服务..." -ForegroundColor Yellow
    Invoke-Expression "$dockerCompose up -d"
} else {
    Write-Host "[1/2] 启动服务..." -ForegroundColor Yellow
    Invoke-Expression "$dockerCompose up -d"
    
    Write-Host "[2/2] 检查服务状态..." -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

$containers = docker ps --filter "name=resume-" --format "{{.Names}}: {{.Status}}"
if ($containers) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   部署成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "服务状态:" -ForegroundColor Cyan
    $containers | ForEach-Object { Write-Host "  $_" }
    Write-Host ""
    Write-Host "访问地址:" -ForegroundColor Cyan
    Write-Host "  前端应用: " -NoNewline; Write-Host "http://localhost" -ForegroundColor Yellow
    Write-Host "  API文档:  " -NoNewline; Write-Host "http://localhost:8000/docs" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "其他命令:" -ForegroundColor Cyan
    Write-Host "  查看日志: .\deploy.ps1 -Logs"
    Write-Host "  停止服务: .\deploy.ps1 -Stop"
    Write-Host "  重新构建: .\deploy.ps1 -Build"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[警告] 容器可能未正常启动，请检查日志" -ForegroundColor Yellow
    Write-Host "运行: .\deploy.ps1 -Logs" -ForegroundColor Yellow
}
