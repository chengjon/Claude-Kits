#!/usr/bin/env bash
# Claude TUI - tmux 启动脚本
# 功能：在 tmux 会话中运行 TUI，支持持久化和滚动查看历史

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_NAME="claude-tui"
TUI_SCRIPT="$SCRIPT_DIR/claude_tui.py"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 检查 tmux 是否已安装
if ! command -v tmux &> /dev/null; then
    print_error "tmux 未安装"
    echo ""
    echo "请先安装 tmux："
    echo "  Ubuntu/Debian: sudo apt install tmux"
    echo "  CentOS/RHEL:   sudo yum install tmux"
    echo "  macOS:         brew install tmux"
    echo ""
    exit 1
fi

# 检查 TUI 脚本是否存在
if [ ! -f "$TUI_SCRIPT" ]; then
    print_error "TUI 脚本未找到: $TUI_SCRIPT"
    exit 1
fi

# 检查 Python 脚本是否可执行
if ! python3 "$TUI_SCRIPT" --version &> /dev/null; then
    if ! python3 -c "import sys; sys.exit(0)" &> /dev/null; then
        print_error "Python3 未安装或不可用"
        exit 1
    fi
fi

# 显示帮助信息
show_help() {
    cat << EOF
Claude TUI - tmux 启动脚本

用法:
  $0 [选项]

选项:
  -h, --help          显示此帮助信息
  -a, --attach        连接到现有会话（如果存在）
  -k, --kill          终止现有会话
  -l, --list          列出所有会话
  -n, --new           强制创建新会话（即使已存在）
  -s, --session NAME  指定会话名称（默认: claude-tui）
  --log               启用会话日志记录

示例:
  # 启动或连接到 TUI
  $0

  # 启动并记录日志
  $0 --log

  # 连接到现有会话
  $0 --attach

  # 终止会话
  $0 --kill

  # 创建新会话（使用自定义名称）
  $0 --new --session my-tui

tmux 快捷键:
  Ctrl+B, D           断开会话（TUI 继续运行）
  Ctrl+B, [           进入滚动模式（查看历史输出）
  Ctrl+B, "           水平分屏
  Ctrl+B, %           垂直分屏
  Ctrl+B, 方向键      切换面板

会话管理:
  查看所有会话:       tmux list-sessions
  重连会话:           tmux attach -t $SESSION_NAME
  终止会话:           tmux kill-session -t $SESSION_NAME
EOF
}

# 检查会话是否存在
session_exists() {
    tmux has-session -t "$SESSION_NAME" 2>/dev/null
}

# 创建新会话
create_session() {
    local log_enabled=$1

    if session_exists; then
        print_warning "会话 '$SESSION_NAME' 已存在"
        read -p "是否连接到现有会话？[Y/n] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            attach_session
            return
        else
            print_info "已取消"
            exit 0
        fi
    fi

    print_info "创建 tmux 会话: $SESSION_NAME"

    if [ "$log_enabled" = true ]; then
        # 启用日志记录
        LOG_DIR="$HOME/.claude-tui-logs"
        mkdir -p "$LOG_DIR"
        TIMESTAMP=$(date +%Y%m%d-%H%M%S)
        LOG_FILE="$LOG_DIR/session-$TIMESTAMP.log"

        print_info "日志文件: $LOG_FILE"

        tmux new-session -s "$SESSION_NAME" \
            "echo -e '${GREEN}Claude TUI 已启动（日志记录已启用）${NC}'; \
             echo -e '${BLUE}日志文件: $LOG_FILE${NC}'; \
             echo ''; \
             script -f -c 'python3 $TUI_SCRIPT' '$LOG_FILE'; \
             echo ''; \
             echo -e '${YELLOW}会话已结束，按 Enter 关闭${NC}'; \
             read"
    else
        tmux new-session -s "$SESSION_NAME" \
            "echo -e '${GREEN}Claude TUI 已启动${NC}'; \
             echo ''; \
             python3 '$TUI_SCRIPT'; \
             echo ''; \
             echo -e '${YELLOW}会话已结束，按 Enter 关闭${NC}'; \
             read"
    fi
}

# 连接到现有会话
attach_session() {
    if ! session_exists; then
        print_error "会话 '$SESSION_NAME' 不存在"
        print_info "使用 '$0 --new' 创建新会话"
        exit 1
    fi

    print_success "连接到会话: $SESSION_NAME"
    tmux attach -t "$SESSION_NAME"
}

# 终止会话
kill_session() {
    if ! session_exists; then
        print_warning "会话 '$SESSION_NAME' 不存在"
        exit 0
    fi

    read -p "确定要终止会话 '$SESSION_NAME'？[y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        tmux kill-session -t "$SESSION_NAME"
        print_success "会话 '$SESSION_NAME' 已终止"
    else
        print_info "已取消"
    fi
}

# 列出所有会话
list_sessions() {
    print_info "所有 tmux 会话:"
    tmux list-sessions 2>/dev/null || print_warning "没有活动的 tmux 会话"
}

# 主逻辑
main() {
    local action="auto"  # auto, new, attach, kill, list
    local log_enabled=false

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -a|--attach)
                action="attach"
                shift
                ;;
            -k|--kill)
                action="kill"
                shift
                ;;
            -l|--list)
                action="list"
                shift
                ;;
            -n|--new)
                action="new"
                shift
                ;;
            -s|--session)
                SESSION_NAME="$2"
                shift 2
                ;;
            --log)
                log_enabled=true
                shift
                ;;
            *)
                print_error "未知选项: $1"
                echo "使用 '$0 --help' 查看帮助"
                exit 1
                ;;
        esac
    done

    # 执行操作
    case $action in
        auto)
            if session_exists; then
                print_info "会话 '$SESSION_NAME' 已存在"
                attach_session
            else
                create_session "$log_enabled"
            fi
            ;;
        new)
            if session_exists; then
                kill_session
            fi
            create_session "$log_enabled"
            ;;
        attach)
            attach_session
            ;;
        kill)
            kill_session
            ;;
        list)
            list_sessions
            ;;
    esac
}

# 捕获 Ctrl+C
trap 'echo ""; print_warning "已取消"; exit 130' INT

main "$@"
