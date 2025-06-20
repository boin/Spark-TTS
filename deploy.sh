#!/bin/bash

# Spark-TTS 部署脚本
# 用法: ./deploy.sh [部署类型]
# 部署类型: stage (Gradio应用) 或 api (API服务器)

DEPLOY_TYPE=${1}

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

# 根据部署类型设置目标主机和标签
case "$DEPLOY_TYPE" in
    "stage")
        TARGET_HOST="ttd-stage"
        TAGS="stage"
        echo -e "${GREEN}开始部署 Spark-TTS Gradio 应用到 $TARGET_HOST${NC}"
        ;;
    "api")
        TARGET_HOST="ttd-edge"
        TAGS="api"
        echo -e "${GREEN}开始部署 Spark-TTS API 服务器到 $TARGET_HOST${NC}"
        ;;
    *)
        echo -e "${RED}错误: 无效的部署类型 '$DEPLOY_TYPE'。请使用 'stage' 或 'api'${NC}"
        exit 1
        ;;
esac

# 执行ansible playbook
ANSIBLE_STDOUT_CALLBACK=debug echo -e "${YELLOW}执行命令: ansible-playbook -i $INVENTORY_FILE ./deploy/spark-tts-deploy.yml -l $TARGET_HOST --tags $TAGS -v${NC}"
ANSIBLE_STDOUT_CALLBACK=debug ansible-playbook -i $INVENTORY_FILE ./deploy/spark-tts-deploy.yml -l $TARGET_HOST --tags $TAGS -v

# 检查部署结果
DEPLOY_RESULT=$?
if [ $DEPLOY_RESULT -eq 0 ]; then
    echo -e "${GREEN}部署成功!${NC}"
else
    echo -e "${RED}部署失败，返回代码: $DEPLOY_RESULT${NC}"
    exit $DEPLOY_RESULT
fi
