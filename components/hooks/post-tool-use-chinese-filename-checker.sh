#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Chinese Filename Checker
# ============================================================================
#
# Event: PostToolUse
# Matcher: Write
# Purpose: 检测新创建文件的文件名是否包含中文字符，确保文件名仅使用ASCII字符
#
# 设计理念:
#   在创建新文件后立即检查文件名，防止中文文件名带来的跨平台兼容性问题
#
# 工作原理:
#   1. 从 stdin 读取 tool_input.file_path
#   2. 检查文件名（basename）是否包含非ASCII字符
#   3. 如果发现中文字符，输出警告或阻止
#   4. 输出清晰的错误消息（纯文本，符合官方规范）
#
# 退出码:
#   0: 文件名合规（仅ASCII字符）
#   1: 警告（包含非ASCII字符但继续）
#   2: 阻止（包含非ASCII字符，需要修复）- 可通过环境变量配置
#
# 环境变量:
#   CHINESE_FILENAME_CHECKER_MODE: "blocking"（阻止模式）或 "warning"（警告模式，默认）
#   CHINESE_FILENAME_CHECKER_EXCLUDE: 排除的目录（用|分隔，如 "temp/|archive/"）
#
# 安装方法:
#   1. chmod +x post-tool-use-chinese-filename-checker.sh
#   2. 复制到 .claude/hooks/
#   3. 添加到 settings.json (见下方配置示例)
#
# Settings.json 配置:
#   {
#     "hooks": {
#       "PostToolUse": [
#         {
#           "matcher": "Write",
#           "hooks": [{
#             "type": "command",
#             "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-chinese-filename-checker.sh"
#           }],
#           "timeout": 3
#         }
#       ]
#     }
#   }
#
# Timeout 建议: 3 秒
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
CHECKER_MODE="${CHINESE_FILENAME_CHECKER_MODE:-warning}"  # "blocking" 或 "warning"
EXCLUDE_PATTERN="${CHINESE_FILENAME_CHECKER_EXCLUDE:-^temp/|^archive/}"
DEBUG_MODE="${CHINESE_FILENAME_CHECKER_DEBUG:-false}"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 检查文件名是否包含非ASCII字符 =====
has_non_ascii() {
    local filename="$1"
    # 使用 LC_ALL=C grep 检测非ASCII字符
    if echo "$filename" | LC_ALL=C grep -q '[^[:print:][:space:]]'; then
        return 0  # 包含非ASCII
    fi
    # 额外检查：使用 perl 检测多字节字符
    if echo "$filename" | perl -ne 'exit 1 if /[^\x00-\x7F]/'; then
        return 1  # 纯ASCII
    else
        return 0  # 包含非ASCII
    fi
}

# ===== 主逻辑 =====

# 读取 stdin JSON
INPUT_JSON=$(cat)
debug_log "Received input: $INPUT_JSON"

# 提取文件路径
FILE_PATH=$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
    debug_log "No file_path in tool_input, skipping"
    exit 0
fi

debug_log "File path: $FILE_PATH"

# 检查是否在排除列表中
if [ -n "$EXCLUDE_PATTERN" ] && echo "$FILE_PATH" | grep -qE "$EXCLUDE_PATTERN"; then
    debug_log "File matches exclude pattern, skipping"
    exit 0
fi

# 提取文件名（basename）
FILENAME=$(basename "$FILE_PATH")
debug_log "Filename: $FILENAME"

# 检查文件名是否包含非ASCII字符
if has_non_ascii "$FILENAME"; then
    # 包含非ASCII字符（可能是中文） - 输出清晰的错误消息到 stderr
    {
        echo ""
        echo "❌ 文件名包含中文或特殊字符"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "文件名: \"$FILENAME\""
        echo "路径: $FILE_PATH"
        echo ""
        echo "⚠️  为什么要避免中文文件名？"
        echo "  • 跨平台兼容性问题（Windows/Linux/macOS编码差异）"
        echo "  • Git仓库在不同系统间克隆可能出现乱码"
        echo "  • 部分构建工具和脚本无法正确处理"
        echo ""
        echo "✅ 推荐的文件命名规范:"
        echo "  • user_authentication.py"
        echo "  • api-config-2025.json"
        echo "  • database_schema_v2.sql"
        echo "  • README.md"
        echo ""
        echo "❌ 避免:"
        echo "  • 用户认证.py"
        echo "  • 配置文件-2025.json"
        echo "  • 数据库架构.sql"
        echo ""
        echo "💡 建议: 使用英文字母、数字、下划线和连字符"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    } >&2

    if [ "$CHECKER_MODE" = "blocking" ]; then
        debug_log "Blocking mode: exit 2"
        exit 2
    else
        debug_log "Warning mode: exit 1"
        exit 1
    fi
else
    # 文件名合规
    debug_log "Filename validation passed"
    echo "✅ 文件名合规 (仅ASCII字符): $FILENAME"
    exit 0
fi
