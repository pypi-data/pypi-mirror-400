#!/bin/bash
# 清理 phone-toolkit 仓库中不需要的文档和冗余代码

echo "开始清理 phone-toolkit 仓库..."

# 删除开发过程中的临时文档
echo "删除临时文档..."
rm -f DELIVERABLES.md
rm -f PROJECT_OVERVIEW.md
rm -f UV_GUIDE.md
rm -f UV_INTEGRATION.md
rm -f QUICKSTART.md

# 删除开发脚本
echo "删除开发脚本..."
rm -f verify_uv.sh
rm -f demo_performance.sh

# 删除构建产物和缓存
echo "删除构建产物和缓存..."
rm -rf htmlcov/
rm -rf dist/
rm -rf .pytest_cache/
rm -rf __pycache__/
rm -rf src/phone_parser/__pycache__/
rm -rf tests/__pycache__/
rm -f .coverage
rm -f uv.lock

echo "清理完成！"
echo ""
echo "保留的文件："
echo "  - README.md (用户文档)"
echo "  - DEVELOPMENT.md (开发指南)"
echo "  - TROUBLESHOOTING.md (问题排查)"
echo "  - LICENSE (许可证)"
echo "  - Makefile (构建工具)"
echo "  - pyproject.toml (项目配置)"
echo "  - uv.toml.example (配置示例)"
echo ""
echo "清理的内容："
echo "  - 5个临时文档文件"
echo "  - 2个开发脚本"
echo "  - 所有构建产物和缓存目录"
