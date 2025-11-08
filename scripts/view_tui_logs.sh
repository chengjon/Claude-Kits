#!/usr/bin/env bash
# Claude TUI - 日志查看脚本
# 功能：方便地查看和管理 TUI 日志文件

set -euo pipefail

LOG_DIR="${CLAUDE_TUI_LOG_DIR:-$HOME/.claude-tui-logs}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

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

print_header() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
}

show_help() {
    cat << EOF
Claude TUI - 日志查看脚本

用法:
  $0 [选项]

选项:
  -h, --help          显示此帮助信息
  -l, --list          列出所有日志文件
  -t, --tail          实时查看最新日志（tail -f）
  -v, --view [N]      查看第 N 个日志文件（默认：最新）
  -c, --clean [DAYS]  清理 N 天前的日志（默认：30 天）
  -s, --size          显示日志目录大小统计
  -d, --dir           显示日志目录路径
  -n, --lnav          使用 lnav 查看日志（如果已安装）

环境变量:
  CLAUDE_TUI_LOG_DIR  日志目录路径（默认: ~/.claude-tui-logs）

示例:
  # 列出所有日志文件
  $0 --list

  # 实时查看最新日志
  $0 --tail

  # 查看最新日志文件（交互式）
  $0 --view

  # 查看第 3 个日志文件
  $0 --view 3

  # 清理 30 天前的日志
  $0 --clean 30

  # 使用 lnav 查看所有日志
  $0 --lnav

  # 查看日志目录大小
  $0 --size
EOF
}

# 检查日志目录
check_log_dir() {
    if [ ! -d "$LOG_DIR" ]; then
        print_warning "日志目录不存在: $LOG_DIR"
        read -p "是否创建日志目录？[Y/n] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            mkdir -p "$LOG_DIR"
            print_success "已创建日志目录: $LOG_DIR"
        else
            exit 1
        fi
    fi
}

# 列出日志文件
list_logs() {
    check_log_dir

    local log_files=($(find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | sort -r))

    if [ ${#log_files[@]} -eq 0 ]; then
        print_warning "没有找到日志文件"
        return
    fi

    print_header "日志文件列表（共 ${#log_files[@]} 个）"
    echo ""

    for i in "${!log_files[@]}"; do
        local file="${log_files[$i]}"
        local filename=$(basename "$file")
        local size=$(du -h "$file" | cut -f1)
        local mtime=$(stat -c %y "$file" 2>/dev/null || stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$file" 2>/dev/null)

        printf "${CYAN}%2d.${NC} %-40s ${GREEN}%8s${NC}  %s\n" \
            $((i+1)) "$filename" "$size" "${mtime:0:19}"
    done
    echo ""
}

# 实时查看最新日志
tail_log() {
    check_log_dir

    local latest_log=$(find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | sort -r | head -1)

    if [ -z "$latest_log" ]; then
        print_error "没有找到日志文件"
        exit 1
    fi

    print_info "实时查看: $(basename "$latest_log")"
    print_info "按 Ctrl+C 退出"
    echo ""

    tail -f "$latest_log"
}

# 查看指定日志文件
view_log() {
    local index=$1
    check_log_dir

    local log_files=($(find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | sort -r))

    if [ ${#log_files[@]} -eq 0 ]; then
        print_error "没有找到日志文件"
        exit 1
    fi

    if [ -z "$index" ]; then
        # 交互式选择
        list_logs
        read -p "请选择要查看的日志文件编号 [1-${#log_files[@]}]: " index
    fi

    if ! [[ "$index" =~ ^[0-9]+$ ]] || [ "$index" -lt 1 ] || [ "$index" -gt ${#log_files[@]} ]; then
        print_error "无效的编号: $index"
        exit 1
    fi

    local selected_log="${log_files[$((index-1))]}"

    print_info "查看日志: $(basename "$selected_log")"
    echo ""

    # 检查是否安装了 lnav
    if command -v lnav &> /dev/null; then
        print_info "使用 lnav 查看（推荐）"
        print_info "或使用 'less' 查看（按 Enter 继续）"
        read -p "选择查看器 [lnav/less]: " viewer
        case "$viewer" in
            less|l)
                less -R "$selected_log"
                ;;
            *)
                lnav "$selected_log"
                ;;
        esac
    else
        # 使用 less
        less -R "$selected_log"
    fi
}

# 清理旧日志
clean_logs() {
    local days=${1:-30}
    check_log_dir

    print_warning "将删除 $days 天前的日志文件"

    local old_logs=$(find "$LOG_DIR" -name "*.log" -type f -mtime +$days 2>/dev/null)
    local count=$(echo "$old_logs" | grep -c "." || echo "0")

    if [ "$count" -eq 0 ]; then
        print_info "没有需要清理的日志文件"
        return
    fi

    echo ""
    echo "将删除以下文件："
    echo "$old_logs" | while read -r file; do
        echo "  - $(basename "$file")"
    done
    echo ""

    read -p "确认删除？[y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        find "$LOG_DIR" -name "*.log" -type f -mtime +$days -delete
        print_success "已删除 $count 个日志文件"
    else
        print_info "已取消"
    fi
}

# 显示日志目录大小
show_size() {
    check_log_dir

    local total_size=$(du -sh "$LOG_DIR" 2>/dev/null | cut -f1)
    local file_count=$(find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | wc -l)

    print_header "日志目录统计"
    echo ""
    echo "  目录路径: $LOG_DIR"
    echo "  文件数量: $file_count"
    echo "  总大小:   $total_size"
    echo ""

    # 显示最大的 5 个日志文件
    if [ "$file_count" -gt 0 ]; then
        echo "  最大的 5 个日志文件:"
        find "$LOG_DIR" -name "*.log" -type f -exec du -h {} + 2>/dev/null | \
            sort -rh | head -5 | while read -r size file; do
            printf "    ${GREEN}%8s${NC}  %s\n" "$size" "$(basename "$file")"
        done
        echo ""
    fi
}

# 使用 lnav 查看所有日志
view_with_lnav() {
    check_log_dir

    if ! command -v lnav &> /dev/null; then
        print_error "lnav 未安装"
        echo ""
        echo "请先安装 lnav："
        echo "  Ubuntu/Debian: sudo apt install lnav"
        echo "  macOS:         brew install lnav"
        echo "  或访问:        https://lnav.org/"
        echo ""
        exit 1
    fi

    local log_count=$(find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | wc -l)

    if [ "$log_count" -eq 0 ]; then
        print_error "没有找到日志文件"
        exit 1
    fi

    print_info "使用 lnav 查看所有日志（共 $log_count 个文件）"
    print_info "lnav 快捷键："
    echo "  /       - 搜索"
    echo "  n/N     - 下一个/上一个搜索结果"
    echo "  q       - 退出"
    echo "  ?       - 帮助"
    echo ""
    sleep 2

    lnav "$LOG_DIR"/*.log
}

# 显示日志目录路径
show_dir() {
    check_log_dir
    echo "$LOG_DIR"
}

# 主逻辑
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -l|--list)
                list_logs
                shift
                ;;
            -t|--tail)
                tail_log
                shift
                ;;
            -v|--view)
                view_log "${2:-}"
                shift
                if [ -n "${2:-}" ] && [[ "$2" =~ ^[0-9]+$ ]]; then
                    shift
                fi
                ;;
            -c|--clean)
                clean_logs "${2:-30}"
                shift
                if [ -n "${2:-}" ] && [[ "$2" =~ ^[0-9]+$ ]]; then
                    shift
                fi
                ;;
            -s|--size)
                show_size
                shift
                ;;
            -d|--dir)
                show_dir
                shift
                ;;
            -n|--lnav)
                view_with_lnav
                shift
                ;;
            *)
                print_error "未知选项: $1"
                echo "使用 '$0 --help' 查看帮助"
                exit 1
                ;;
        esac
    done
}

# 捕获 Ctrl+C
trap 'echo ""; print_warning "已取消"; exit 130' INT

main "$@"
