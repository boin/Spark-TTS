#!/bin/bash

# Spark-TTS 部署脚本
# 用法: ./deploy.sh [环境名称]

# 默认值
ENV=${1:-"stage"}

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 显示横幅
echo -e "${GREEN}"
echo "====================================="
echo "     Spark-TTS 部署工具"
echo "====================================="
echo -e "${NC}"

# 检查ansible是否安装
if ! command -v ansible &> /dev/null; then
    echo -e "${RED}错误: 未安装ansible。请先安装ansible:${NC}"
    echo "sudo apt update && sudo apt install -y ansible"
    exit 1
fi

# 检查inventory文件是否存在
INVENTORY_FILE="./deploy/inventory.ini"
if [ ! -f "$INVENTORY_FILE" ]; then
    echo -e "${RED}错误: inventory.ini文件不存在${NC}"
    exit 1
fi

echo -e "${GREEN}开始部署 Spark-TTS 到 $ENV 环境${NC}"

# 执行ansible playbook
ansible-playbook -i $INVENTORY_FILE ./deploy/spark-tts-deploy.yml -l $ENV -v

# 检查部署结果
DEPLOY_RESULT=$?

# 显示部署结果
if [ $DEPLOY_RESULT -eq 0 ]; then
    echo -e "${GREEN}"
    echo "====================================="
    echo "     部署成功完成!"
    echo "====================================="
    echo -e "${NC}"
else
    echo -e "${RED}"
    echo "====================================="
    echo "     部署失败，请检查日志"
    echo "====================================="
    echo -e "${NC}"
    exit 1
fi
