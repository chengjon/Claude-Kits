#!/usr/bin/env bash
# 简化的 TUI 测试脚本（不使用 tmux）
# 用于验证 TUI 本身是否工作

echo "========================================="
echo "Claude TUI 简单测试"
echo "========================================="
echo ""

# 检查 TTY
if [ ! -t 0 ] || [ ! -t 1 ]; then
    echo "❌ 错误：没有 TTY（交互式终端）"
    echo ""
    echo "你当前在非交互式环境中运行（如通过 Claude Code）"
    echo ""
    echo "请在真正的终端中手动输入以下命令："
    echo "  cd /opt/claude/Claude-Kits"
    echo "  ./scripts/simple_test_tui.sh"
    echo ""
    exit 1
fi

echo "✅ TTY 检查通过"
echo ""

# 检查依赖
echo "检查依赖..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi
echo "  ✅ Python3: $(python3 --version)"

if ! python3 -c "import rich" 2>/dev/null; then
    echo "  ❌ rich 库未安装"
    echo "  请运行: pip3 install rich"
    exit 1
fi
echo "  ✅ rich 库已安装"

echo ""
echo "准备启动 TUI..."
echo ""
echo "提示："
echo "  - 使用方向键（↑/↓）或数字键（1-8）导航菜单"
echo "  - 按 Enter 选择"
echo "  - 按 'q' 或选择 'Exit' 退出"
echo ""
echo "按 Enter 继续..."
read

# 启动 TUI
python3 scripts/claude_tui.py

echo ""
echo "TUI 已退出"
echo "========================================="
