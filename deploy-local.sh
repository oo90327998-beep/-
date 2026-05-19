#!/bin/bash

# Resume Studio 本地一键部署脚本 (无需 Docker)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
PID_FILE="$SCRIPT_DIR/.resume-studio.pid"

show_help() {
    echo -e "${CYAN}Resume Studio 本地一键部署脚本${NC}"
    echo ""
    echo "用法:"
    echo "  ./deploy-local.sh          # 启动服务"
    echo "  ./deploy-local.sh stop     # 停止所有服务"
    echo ""
    echo "服务地址:"
    echo "  前端: http://localhost:5173"
    echo "  后端: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
    echo ""
}

stop_services() {
    echo -e "${YELLOW}停止所有服务...${NC}"
    
    if [ -f "$PID_FILE" ]; then
        while read pid; do
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
    
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "vite.*5173" 2>/dev/null || true
    
    echo -e "${GREEN}服务已停止${NC}"
    exit 0
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

if [[ "$1" == "stop" ]]; then
    stop_services
fi

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Resume Studio 本地一键部署${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

echo -e "${YELLOW}[1/4] 检查 Python 环境...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}[错误] Python 未安装${NC}"
    echo -e "${YELLOW}安装文档: https://www.python.org/downloads/${NC}"
    exit 1
fi
echo -e "${GREEN}  使用: $PYTHON_CMD${NC}"

echo -e "${YELLOW}[2/4] 检查 Node.js 环境...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}[错误] Node.js 未安装${NC}"
    echo -e "${YELLOW}安装文档: https://nodejs.org/${NC}"
    exit 1
fi
NODE_VERSION=$(node -v)
echo -e "${GREEN}  Node.js 版本: $NODE_VERSION${NC}"

echo -e "${YELLOW}[3/4] 安装依赖...${NC}"

echo -e "${CYAN}  安装后端依赖...${NC}"
cd "$BACKEND_DIR"
$PYTHON_CMD -m pip install -r requirements.txt --quiet 2>/dev/null || true

echo -e "${CYAN}  安装前端依赖...${NC}"
cd "$FRONTEND_DIR"
if [ -d "node_modules" ]; then
    echo -e "${CYAN}    node_modules 已存在，跳过安装${NC}"
else
    npm install --silent 2>/dev/null || npm install
fi

echo -e "${YELLOW}[4/4] 启动服务...${NC}"

rm -f "$PID_FILE"

cd "$BACKEND_DIR"
$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo $BACKEND_PID >> "$PID_FILE"

cd "$FRONTEND_DIR"
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
echo $FRONTEND_PID >> "$PID_FILE"

sleep 3

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   部署成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}访问地址:${NC}"
echo -e "  前端应用: ${YELLOW}http://localhost:5173${NC}"
echo -e "  API文档:  ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo -e "${CYAN}停止服务: ./deploy-local.sh stop${NC}"
echo ""

wait
