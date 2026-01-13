#!/bin/bash

# PaperTrail-Py 快速启动脚本
# 用法: ./scripts/setup.sh

set -e

echo "🚀 PaperTrail-Py 项目初始化"
echo "================================"

# 检查 uv
echo "📦 检查 uv 安装..."
if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "✅ uv 已安装"
fi

# 创建虚拟环境
echo ""
echo "🔧 创建虚拟环境..."
uv venv

# 激活虚拟环境
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# 安装依赖
echo ""
echo "📥 安装开发依赖..."
uv pip install -e ".[dev,async,postgresql]"

# 安装 pre-commit hooks
echo ""
echo "🪝 安装 pre-commit hooks..."
pre-commit install

# 运行测试
echo ""
echo "🧪 运行测试..."
uv run pytest --cov=paper_trail

# 代码质量检查
echo ""
echo "🎨 运行代码质量检查..."
uv run ruff check src/ tests/ || true
uv run mypy src/paper_trail || true

echo ""
echo "================================"
echo "✅ 项目初始化完成！"
echo ""
echo "📚 下一步："
echo "  1. 查看 README.md 了解项目"
echo "  2. 运行 'make test' 执行测试"
echo "  3. 运行 'cd examples && uv run python complete_example.py' 查看示例"
echo ""
echo "🛠️ 常用命令："
echo "  make dev-install  - 安装开发依赖"
echo "  make test         - 运行测试"
echo "  make lint         - 代码检查"
echo "  make format       - 格式化代码"
echo ""
