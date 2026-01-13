#!/bin/bash

# HIL Server Direct 模式部署脚本（内网环境）
# 用于部署到 dev 机器

set -e

TARGET_HOST=${1:-dev}
HIL_PORT=${2:-8081}
BOT_KEY=${3:-"0584a72f-e30c-49d3-801e-6f4dceb2ef95"}

echo "=========================================="
echo "HIL Server Direct 模式部署"
echo "=========================================="
echo "目标主机: $TARGET_HOST"
echo "端口: $HIL_PORT"
echo "模式: Direct (内网)"
echo "=========================================="

# 1. 同步代码
echo "📦 同步代码到 $TARGET_HOST..."
rsync -avz --delete \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude 'data' \
    --exclude '.env' \
    --exclude '*.log' \
    --exclude 'venv' \
    --exclude '.venv' \
    --exclude 'devcloud_worker' \
    --exclude 'forward_service' \
    --exclude 'mcp_server' \
    hil_server requirements.txt \
    $TARGET_HOST:~/projects/hil-mcp-direct/

# 2. 远程部署
echo ""
echo "🚀 在 $TARGET_HOST 上部署 HIL Server..."

ssh $TARGET_HOST << REMOTE_SCRIPT
set -e

cd ~/projects/hil-mcp-direct

# 停止旧进程
echo "停止旧进程..."
pkill -f "hil_server.app" 2>/dev/null || true
sleep 2

# 安装依赖
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    export PATH="\$HOME/.local/bin:\$PATH"
    uv venv .venv --python 3.10
fi

echo "安装依赖..."
export PATH="\$HOME/.local/bin:\$PATH"
source .venv/bin/activate
uv pip install -r requirements.txt -i https://mirrors.tencent.com/pypi/simple/
uv pip install fly-pigeon -i https://mirrors.tencent.com/pypi/simple/

# 设置环境变量
export HIL_PORT=$HIL_PORT
export MODE=direct
export BOT_KEY="$BOT_KEY"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="jarvis2026"

# 启动服务
echo "启动 HIL Server (Direct 模式)..."
nohup python -m hil_server.app >> hil.log 2>&1 &
PID=\$!

echo "✅ 服务已启动，PID: \$PID"
sleep 3

# 健康检查
echo "🔍 健康检查..."
curl -s http://localhost:$HIL_PORT/health || echo "健康检查失败"

REMOTE_SCRIPT

echo ""
echo "✅ HIL Server (Direct 模式) 部署完成！"
echo ""
echo "服务地址: http://$TARGET_HOST:$HIL_PORT"
echo "管理台: http://$TARGET_HOST:$HIL_PORT/admin"
echo ""
echo "查看日志: ssh $TARGET_HOST 'tail -f ~/projects/hil-mcp-direct/hil.log'"
