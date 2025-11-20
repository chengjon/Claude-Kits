#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Python Header Validator
# ============================================================================
#
# Event: PostToolUse
# Matcher: Edit|Write
# Purpose: 验证Python文件的标准头部注释，确保符合项目规范
#
# 设计理念:
#   在创建或编辑Python文件后立即检查头部注释，及时发现不合规问题
#
# 工作原理:
#   1. 从 stdin 读取 tool_input.file_path
#   2. 检查是否为 .py 文件
#   3. 验证文件前 20 行是否包含必需组件（可配置）
#   4. 检查是否有导入语句可能需要调整（可选）
#   5. 输出清晰的错误消息（纯文本，符合官方规范）
#
# 退出码:
#   0: 合规或非Python文件（允许继续）
#   1: 警告（显示问题但继续）
#   2: 阻止（不合规，需要修复）- 可通过环境变量配置
#
# 环境变量:
#   PYTHON_HEADER_VALIDATOR_MODE: "blocking"（阻止模式）或 "warning"（警告模式，默认）
#   PYTHON_HEADER_VALIDATOR_EXCLUDE: 排除的文件模式（用|分隔，如 "__init__|test_"）
#   PYTHON_HEADER_REQUIRED_FIELDS: 自定义必需字段（用|分隔，默认5个标准字段）
#   PYTHON_HEADER_CHECK_IMPORTS: "true" 检查导入语句（默认 "false"）
#
# 自定义必需字段示例:
#   export PYTHON_HEADER_REQUIRED_FIELDS="# -*- coding: utf-8 -*-|# 功能：|# 作者："
#
# 安装方法:
#   1. chmod +x post-tool-use-python-header-validator.sh
#   2. 复制到 .claude/hooks/
#   3. 添加到 settings.json (见下方配置示例)
#
# Settings.json 配置:
#   {
#     "hooks": {
#       "PostToolUse": [
#         {
#           "matcher": "Edit|Write",
#           "hooks": [{
#             "type": "command",
#             "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-python-header-validator.sh"
#           }],
#           "timeout": 5
#         }
#       ]
#     }
#   }
#
# 自定义字段配置（在 settings.local.json 中）:
#   {
#     "env": {
#       "PYTHON_HEADER_REQUIRED_FIELDS": "# -*- coding: utf-8 -*-|# 功能：|# 作者：|# 日期：|# 版本：",
#       "PYTHON_HEADER_CHECK_IMPORTS": "true"
#     }
#   }
#
# Timeout 建议: 5 秒
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
VALIDATOR_MODE="${PYTHON_HEADER_VALIDATOR_MODE:-warning}"  # "blocking" 或 "warning"
EXCLUDE_PATTERN="${PYTHON_HEADER_VALIDATOR_EXCLUDE:-__pycache__|\.pyc$}"
DEBUG_MODE="${PYTHON_HEADER_VALIDATOR_DEBUG:-false}"
CHECK_IMPORTS="${PYTHON_HEADER_CHECK_IMPORTS:-false}"

# 必需的头部组件 - 可通过环境变量配置，避免硬编码
DEFAULT_REQUIRED_FIELDS="# -*- coding: utf-8 -*-|# 功能：|# 作者：|# 日期：|# 版本："
REQUIRED_FIELDS_STR="${PYTHON_HEADER_REQUIRED_FIELDS:-$DEFAULT_REQUIRED_FIELDS}"

# 将配置字符串转换为数组
IFS='|' read -ra REQUIRED_HEADERS <<< "$REQUIRED_FIELDS_STR"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 检查导入路径提醒 =====
check_imports_warning() {
    local file_path="$1"

    # 检查是否有 import 或 from 语句
    if grep -qE '^(import|from)\s+' "$file_path" 2>/dev/null; then
        local imports=$(grep -E '^(import|from)\s+' "$file_path" | head -5)

        cat >&2 <<EOF

⚠️  检测到导入语句
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
文件: $file_path

检测到以下导入语句（前5个）:
$imports

💡 重要提醒:
  如果此文件是从其他位置移动过来的，请检查：
  • 相对导入路径是否需要调整
  • 模块导入路径是否仍然正确
  • 是否需要更新 __init__.py
  • 是否需要更新 PYTHONPATH

  示例：
    - 从 'src/utils.py' 移到 'lib/utils.py'
    - 导入语句可能需要从 'from . import' 改为 'from lib import'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
    fi
}

# ===== 主逻辑 =====

# 读取 stdin JSON
INPUT_JSON=$(cat)
debug_log "Received input: $INPUT_JSON"

# 提取文件路径（从 tool_input.file_path）
FILE_PATH=$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")

# 如果没有提取到文件路径，跳过检查
if [ -z "$FILE_PATH" ]; then
    debug_log "No file_path in tool_input, skipping"
    exit 0
fi

debug_log "File path: $FILE_PATH"

# 检查是否为 Python 文件
if [[ ! "$FILE_PATH" =~ \.py$ ]]; then
    debug_log "Not a Python file, skipping"
    exit 0
fi

# 检查是否在排除列表中
if [ -n "$EXCLUDE_PATTERN" ] && echo "$FILE_PATH" | grep -qE "$EXCLUDE_PATTERN"; then
    debug_log "File matches exclude pattern, skipping"
    exit 0
fi

# 检查文件是否存在
if [ ! -f "$FILE_PATH" ]; then
    debug_log "File does not exist yet, skipping"
    exit 0
fi

# 读取文件前 20 行
HEADER=$(head -n 20 "$FILE_PATH" 2>/dev/null || echo "")

# 检查每个必需组件
MISSING_HEADERS=()
for header in "${REQUIRED_HEADERS[@]}"; do
    # 使用 grep -F 进行字面字符串匹配（无需转义正则）
    if ! echo "$HEADER" | grep -qF "$header"; then
        MISSING_HEADERS+=("$header")
    fi
done

# 判断合规性
if [ ${#MISSING_HEADERS[@]} -eq 0 ]; then
    # 完全合规
    debug_log "Python header validation passed"
    echo "✅ Python头部注释合规: $FILE_PATH"

    # 如果启用了导入检查，显示导入提醒
    if [ "$CHECK_IMPORTS" = "true" ]; then
        check_imports_warning "$FILE_PATH"
    fi

    exit 0
else
    # 不合规 - 输出清晰的错误消息到 stderr
    {
        echo ""
        echo "❌ Python头部注释不合规"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "文件: $FILE_PATH"
        echo ""
        echo "缺少以下必需组件:"
        for missing in "${MISSING_HEADERS[@]}"; do
            echo "  • $missing"
        done
        echo ""
        echo "📋 标准Python头部模板:"
        echo "  # -*- coding: utf-8 -*-"
        echo "  # 功能：[功能描述]"
        echo "  # 作者：[作者姓名 (email)] & Claude"
        echo "  # 日期：YYYY-MM-DD"
        echo "  # 版本：vX.Y.Z"
        echo "  # 依赖：[依赖列表或详见requirements.txt]"
        echo "  # 注意事项：[注意事项]"
        echo "  # 版权：© 2025 [项目名称] Project"
        echo ""
        echo "💡 建议: 在文件开头添加标准头部注释"
        echo ""
        echo "🔧 自定义配置："
        echo "  可通过环境变量 PYTHON_HEADER_REQUIRED_FIELDS 自定义必需字段"
        echo "  当前配置: ${#REQUIRED_HEADERS[@]} 个必需字段"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    } >&2

    # 根据模式决定退出码
    if [ "$VALIDATOR_MODE" = "blocking" ]; then
        debug_log "Blocking mode: exit 2"
        exit 2  # 阻止继续（Claude 会看到 stderr 消息）
    else
        debug_log "Warning mode: exit 1"
        exit 1  # 警告但继续（用户会看到 stderr 消息）
    fi
fi
