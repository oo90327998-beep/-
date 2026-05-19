#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

show_menu() {
    clear
    echo -e "${CYAN}========================================"
    echo -e "   Resume Studio AI 简历优化助手"
    echo -e "========================================${NC}"
    echo ""
    echo "请选择部署方式："
    echo "1. 使用 Docker 部署（需要安装 Docker）"
    echo "2. 本地部署（无需 Docker）"
    echo "3. 查看帮助"
    echo "4. 退出"
    echo ""
}

show_help() {
    echo ""
    echo -e "${CYAN}=============== 帮助信息 ===============${NC}"
    echo ""
    echo "快速启动："
    echo "   启动 Docker 服务：./deploy.sh"
    echo "   启动本地服务：./deploy-local.sh"
    echo ""
    echo "访问地址："
    echo "   前端应用：http://localhost (Docker) 或 http://localhost:5173 (本地)"
    echo "   API文档：http://localhost:8000/docs"
    echo ""
    echo "停止服务："
    echo "   Docker 部署：./deploy.sh stop"
    echo "   本地部署：./deploy-local.sh stop"
    echo ""
    echo -e "${YELLOW}注意：首次运行需要给脚本添加执行权限${NC}"
    echo "    chmod +x deploy.sh deploy-local.sh start.sh"
    echo ""
}

docker_deploy() {
    echo ""
    echo -e "${YELLOW}[1/2] 检查 Docker...${NC}"
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}[错误] Docker 未安装${NC}"
        echo -e "${YELLOW}安装文档：https://docs.docker.com/get-docker/${NC}"
        echo ""
        read -p "按回车键返回主菜单..."
        return
    fi
    
    echo -e "${GREEN}✓ Docker 已安装${NC}"
    
    echo -e "${YELLOW}[2/2] 启动 Docker 服务...${NC}"
    chmod +x deploy.sh 2>/dev/null
    ./deploy.sh
    
    echo ""
    read -p "按回车键返回主菜单..."
}

local_deploy() {
    echo ""
    echo -e "${YELLOW}[1/3] 检查 Python...${NC}"
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        echo -e "${RED}[错误] Python 未安装${NC}"
        echo -e "${YELLOW}安装文档：https://www.python.org/downloads/${NC}"
        echo ""
        read -p "按回车键返回主菜单..."
        return
    fi
    echo -e "${GREEN}✓ Python 已安装${NC}"
    
    echo -e "${YELLOW}[2/3] 检查 Node.js...${NC}"
    if ! command -v node &> /dev/null; then
        echo -e "${RED}[错误] Node.js 未安装${NC}"
        echo -e "${YELLOW}安装文档：https://nodejs.org/${NC}"
        echo ""
        read -p "按回车键返回主菜单..."
        return
    fi
    echo -e "${GREEN}✓ Node.js 已安装${NC}"
    
    echo -e "${YELLOW}[3/3] 启动本地服务...${NC}"
    chmod +x deploy-local.sh 2>/dev/null
    ./deploy-local.sh
    
    echo ""
    read -p "按回车键返回主菜单..."
}

while true; do
    show_menu
    read -p "请选择 (1-4): " choice
    
    case $choice in
        1)
            docker_deploy
            ;;
        2)
            local_deploy
            ;;
        3)
            show_help
            read -p "按回车键返回主菜单..."
            ;;
        4)
            echo ""
            echo -e "${GREEN}感谢使用 Resume Studio AI 简历优化助手！${NC}"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}选择无效，请重新输入${NC}"
            sleep 1
            ;;
    esac
done