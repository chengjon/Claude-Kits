#!/usr/bin/env bash
# TTY 环境诊断脚本
# 用于检查当前是否在交互式终端中

echo "========================================="
echo "TTY 环境诊断"
echo "========================================="
echo ""

# 检查是否连接到 TTY
if [ -t 0 ]; then
    echo "✅ stdin (0) 连接到 TTY"
else
    echo "❌ stdin (0) 未连接到 TTY（非交互式环境）"
fi

if [ -t 1 ]; then
    echo "✅ stdout (1) 连接到 TTY"
else
    echo "❌ stdout (1) 未连接到 TTY"
fi

if [ -t 2 ]; then
    echo "✅ stderr (2) 连接到 TTY"
else
    echo "❌ stderr (2) 未连接到 TTY"
fi

echo ""
echo "终端信息："
echo "  TTY 设备: $(tty 2>/dev/null || echo '无')"
echo "  TERM 类型: ${TERM:-未设置}"
echo "  是否交互式 shell: $(if [[ $- == *i* ]]; then echo '是'; else echo '否'; fi)"

echo ""
echo "tmux 可用性："
if command -v tmux &> /dev/null; then
    echo "  tmux 版本: $(tmux -V)"
    if [ -t 0 ] && [ -t 1 ]; then
        echo "  ✅ 可以运行 tmux（有 TTY）"
    else
        echo "  ❌ 无法运行 tmux（缺少 TTY）"
    fi
else
    echo "  ❌ tmux 未安装"
fi

echo ""
echo "TUI 可用性："
if [ -t 0 ] && [ -t 1 ]; then
    echo "  ✅ 可以运行 TUI（有 TTY）"
    echo ""
    echo "建议运行："
    echo "  ./scripts/run_tui_with_tmux.sh --log"
else
    echo "  ❌ 无法运行 TUI（缺少 TTY）"
    echo ""
    echo "⚠️  你当前在非交互式环境中（如 Claude Code 的 Bash 工具）"
    echo ""
    echo "请在真正的终端中手动输入命令："
    echo "  cd /opt/claude/Claude-Kits"
    echo "  ./scripts/run_tui_with_tmux.sh --log"
fi

echo ""
echo "========================================="
