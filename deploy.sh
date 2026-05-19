#!/bin/bash

# Resume Studio 一键部署脚本 (Linux/macOS)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

show_help() {
    echo -e "${CYAN}Resume Studio 一键部署脚本${NC}"
    echo ""
    echo "用法:"
    echo "  ./deploy.sh          # 启动服务"
    echo "  ./deploy.sh build    # 重新构建并启动"
    echo "  ./deploy.sh stop     # 停止所有服务"
    echo "  ./deploy.sh logs     # 查看日志"
    echo ""
    echo "服务地址:"
    echo "  前端: http://localhost"
    echo "  后端: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
    echo ""
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Resume Studio 一键部署${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

if ! command -v docker &> /dev/null; then
    echo -e "${RED}[错误] Docker 未安装${NC}"
    echo -e "${YELLOW}安装文档: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}[错误] Docker Compose 未安装${NC}"
    exit 1
fi

DOCKER_COMPOSE="docker compose"
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
fi

case "$1" in
    stop)
        echo -e "${YELLOW}[1/2] 停止服务...${NC}"
        $DOCKER_COMPOSE down
        echo -e "${GREEN}[2/2] 清理完成${NC}"
        echo -e "${GREEN}服务已停止${NC}"
        exit 0
        ;;
    logs)
        echo -e "${YELLOW}查看日志 (Ctrl+C 退出)...${NC}"
        $DOCKER_COMPOSE logs -f
        exit 0
        ;;
    build)
        echo -e "${YELLOW}[1/3] 停止旧容器...${NC}"
        $DOCKER_COMPOSE down
        echo -e "${YELLOW}[2/3] 构建镜像...${NC}"
        $DOCKER_COMPOSE build --no-cache
        echo -e "${YELLOW}[3/3] 启动服务...${NC}"
        $DOCKER_COMPOSE up -d
        ;;
    *)
        echo -e "${YELLOW}[1/2] 启动服务...${NC}"
        $DOCKER_COMPOSE up -d
        echo -e "${YELLOW}[2/2] 检查服务状态...${NC}"
        ;;
esac

sleep 3

containers=$(docker ps --filter "name=resume-" --format "{{.Names}}: {{.Status}}")
if [ -n "$containers" ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   部署成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${CYAN}服务状态:${NC}"
    echo "$containers" | while read line; do echo "  $line"; done
    echo ""
    echo -e "${CYAN}访问地址:${NC}"
    echo -e "  前端应用: ${YELLOW}http://localhost${NC}"
    echo -e "  API文档:  ${YELLOW}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${CYAN}其他命令:${NC}"
    echo "  查看日志: ./deploy.sh logs"
    echo "  停止服务: ./deploy.sh stop"
    echo "  重新构建: ./deploy.sh build"
    echo ""
else
    echo ""
    echo -e "${YELLOW}[警告] 容器可能未正常启动，请检查日志${NC}"
    echo -e "${YELLOW}运行: ./deploy.sh logs${NC}"
fi
