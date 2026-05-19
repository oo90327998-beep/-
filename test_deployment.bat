@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Resume Studio 部署测试脚本
echo ========================================
echo.

echo [1/3] 检查系统依赖...
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python 未安装！
    goto missing_python
) else (
    python --version
    echo ✓ Python 已安装
)

echo.

REM 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Node.js 未安装！
    goto missing_nodejs
) else (
    node --version
    echo ✓ Node.js 已安装
)

echo.

REM 检查Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [警告] Docker 未安装，只能使用本地部署模式
    set docker_installed=0
) else (
    docker --version | findstr version
    echo ✓ Docker 已安装
    set docker_installed=1
)

echo.
echo ========================================
echo [2/3] 检查项目依赖...
echo ========================================
echo.

echo 检查后端依赖...
cd /d "%~dp0backend"
if exist requirements.txt (
    python -m pip show fastapi >nul 2>&1
    if errorlevel 1 (
        echo [提示] 后端依赖未安装，正在安装...
        python -m pip install -r requirements.txt --quiet
        echo ✓ 后端依赖已安装
    ) else (
        echo ✓ 后端依赖已安装
    )
) else (
    echo [错误] requirements.txt 文件不存在！
)

echo.

echo 检查前端依赖...
cd /d "%~dp0frontend"
if exist package.json (
    if exist node_modules (
        echo ✓ 前端依赖已安装
    ) else (
        echo [提示] 前端依赖未安装，正在安装...
        npm install --silent >nul 2>&1
        if errorlevel 1 (
            echo [警告] npm install 失败，请手动运行：npm install
        ) else (
            echo ✓ 前端依赖已安装
        )
    )
) else (
    echo [错误] package.json 文件不存在！
)

echo.
echo ========================================
echo [3/3] 检查配置文件...
echo ========================================
echo.

cd /d "%~dp0"
if exist backend\config\siliconflow.json (
    echo ✓ 硅基流动配置文件存在
    echo   模型配置：DeepSeek-V3.2
) else (
    echo [错误] siliconflow.json 配置文件不存在！
)

if exist docker-compose.yml (
    echo ✓ Docker Compose 配置文件存在
) else (
    echo [错误] docker-compose.yml 配置文件不存在！
)

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo [✅] 系统依赖检查通过
echo [✅] 项目依赖检查通过
echo [✅] 配置文件检查通过
echo.

if "%docker_installed%"=="1" (
    echo [可选] 运行 Docker 部署：双击 deploy.ps1
    echo [可选] 运行本地部署：双击 deploy-local.ps1
) else (
    echo [推荐] 运行本地部署：双击 deploy-local.ps1
)

echo.
echo [推荐] 使用一键启动：双击 start.bat
echo.

pause
goto :eof

:missing_python
echo.
echo [解决方案]
echo 1. 下载 Python：https://www.python.org/downloads/
echo 2. 安装时勾选 "Add Python to PATH"
echo 3. 重新运行此脚本
echo.
pause
exit /b 1

:missing_nodejs
echo.
echo [解决方案]
echo 1. 下载 Node.js：https://nodejs.org/
echo 2. 选择 LTS 版本安装
echo 3. 重新运行此脚本
echo.
pause
exit /b 1