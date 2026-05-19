@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Resume Studio AI 简历优化助手
echo ========================================
echo.

:menu
echo 请选择部署方式：
echo 1. 使用 Docker 部署（需要安装 Docker）
echo 2. 本地部署（无需 Docker）
echo 3. 查看帮助
echo 4. 退出
echo.

set /p choice="请选择 (1-4): "

if "%choice%"=="1" goto docker_deploy
if "%choice%"=="2" goto local_deploy
if "%choice%"=="3" goto show_help
if "%choice%"=="4" goto exit_program

echo 选择无效，请重新输入
goto menu

:docker_deploy
echo.
echo 正在检查 Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未安装！
    echo 请先安装 Docker Desktop：https://www.docker.com/products/docker-desktop
    echo.
    pause
    goto menu
)

echo Docker 已安装，正在启动服务...
powershell -ExecutionPolicy Bypass -File "%~dp0deploy.ps1"
pause
goto menu

:local_deploy
echo.
echo 正在检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python 未安装！
    echo 请先安装 Python：https://www.python.org/downloads/
    echo.
    pause
    goto menu
)

echo 正在检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Node.js 未安装！
    echo 请先安装 Node.js：https://nodejs.org/
    echo.
    pause
    goto menu
)

echo 环境检查通过，正在启动服务...
powershell -ExecutionPolicy Bypass -File "%~dp0deploy-local.ps1"
pause
goto menu

:show_help
echo.
echo =============== 帮助信息 ===============
echo.
echo 快速启动：
echo   启动 Docker 服务：双击 deploy.ps1
echo   启动本地服务：双击 deploy-local.ps1
echo.
echo 访问地址：
echo   前端应用：http://localhost (Docker) 或 http://localhost:5173 (本地)
echo   API文档：http://localhost:8000/docs
echo.
echo 停止服务：
echo   Docker 部署：双击 deploy.ps1 -Stop
echo   本地部署：双击 deploy-local.ps1 -Stop
echo.
pause
goto menu

:exit_program
echo.
echo 感谢使用 Resume Studio AI 简历优化助手！
echo.
pause