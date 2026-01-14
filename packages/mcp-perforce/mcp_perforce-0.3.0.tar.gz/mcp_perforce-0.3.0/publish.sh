#!/bin/bash
# MCP Perforce 一键发布脚本
# 用于发布到 PyPI

set -e  # 遇到错误立即退出

echo "=========================================="
echo "MCP Perforce 发布脚本"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "[1/5] 清理旧的构建文件..."
rm -rf .venv dist build *.egg-info src/*.egg-info 2>/dev/null || true
echo "✓ 清理完成"

echo ""
echo "[2/5] 创建虚拟环境并安装依赖..."
uv sync
echo "✓ 依赖安装完成"

echo ""
echo "[3/5] 安装 twine..."
uv pip install twine
echo "✓ twine 安装完成"

echo ""
echo "[4/5] 构建包..."
uv build
echo "✓ 构建完成"

echo ""
echo "[5/5] 上传到 PyPI..."
echo "请输入 PyPI 凭据（或使用 token）"
uv run twine upload ./dist/*

echo ""
echo "=========================================="
echo "✓ 发布完成！"
echo "=========================================="

# 显示版本信息
VERSION=$(grep -oP 'version = "\K[^"]+' pyproject.toml)
echo ""
echo "已发布版本: $VERSION"
echo "PyPI 地址: https://pypi.org/project/mcp-perforce/$VERSION/"
