#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Markdown Frontmatter Validator
# ============================================================================
#
# Event: PostToolUse
# Matcher: Edit|Write
# Purpose: 验证Markdown文件的YAML frontmatter，确保包含项目必需字段
#
# 设计理念:
#   在创建或编辑Markdown文件后立即检查YAML frontmatter，确保文档元数据完整
#
# 工作原理:
#   1. 从 stdin 读取 tool_input.file_path
#   2. 检查是否为 .md 文件
#   3. 验证文件是否以 "---" 开头（YAML frontmatter）
#   4. 验证是否包含必需字段（可配置）
#   5. 输出清晰的错误消息（纯文本，符合官方规范）
#
# 退出码:
#   0: 合规或非Markdown文件（允许继续）
#   1: 警告（显示问题但继续）
#   2: 阻止（不合规，需要修复）- 可通过环境变量配置
#
# 环境变量:
#   MD_FRONTMATTER_VALIDATOR_MODE: "blocking"（阻止模式）或 "warning"（警告模式，默认）
#   MD_FRONTMATTER_VALIDATOR_EXCLUDE: 排除的文件（用|分隔，如 "CLAUDE.md|CHANGELOG.md|README.md"）
#   MD_FRONTMATTER_REQUIRED_FIELDS: 自定义必需字段（用|分隔，默认5个标准字段）
#
# 自定义必需字段示例:
#   export MD_FRONTMATTER_REQUIRED_FIELDS="创建人:|版本:|批准日期:"
#
# 安装方法:
#   1. chmod +x post-tool-use-md-frontmatter-validator.sh
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
#             "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-md-frontmatter-validator.sh"
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
#       "MD_FRONTMATTER_REQUIRED_FIELDS": "创建人:|版本:|批准日期:|最后修订:|本次修订内容:"
#     }
#   }
#
# Timeout 建议: 5 秒
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
VALIDATOR_MODE="${MD_FRONTMATTER_VALIDATOR_MODE:-warning}"  # "blocking" 或 "warning"
EXCLUDE_PATTERN="${MD_FRONTMATTER_VALIDATOR_EXCLUDE:-^CLAUDE\.md$|^CHANGELOG\.md$|^README\.md$}"
DEBUG_MODE="${MD_FRONTMATTER_VALIDATOR_DEBUG:-false}"

# 必需的 frontmatter 字段 - 可通过环境变量配置，避免硬编码
DEFAULT_REQUIRED_FIELDS="创建人:|版本:|批准日期:|最后修订:|本次修订内容:"
REQUIRED_FIELDS_STR="${MD_FRONTMATTER_REQUIRED_FIELDS:-$DEFAULT_REQUIRED_FIELDS}"

# 将配置字符串转换为数组
IFS='|' read -ra REQUIRED_FIELDS <<< "$REQUIRED_FIELDS_STR"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
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

# 检查是否为 Markdown 文件
if [[ ! "$FILE_PATH" =~ \.md$ ]]; then
    debug_log "Not a Markdown file, skipping"
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

# 检查第一行是否为 "---"
FIRST_LINE=$(head -n 1 "$FILE_PATH" 2>/dev/null || echo "")
if [ "$FIRST_LINE" != "---" ]; then
    # 缺少 frontmatter
    {
        echo ""
        echo "❌ Markdown frontmatter缺失"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "文件: $FILE_PATH"
        echo ""
        echo "问题: 文件第一行不是 '---'（YAML frontmatter起始标记）"
        echo ""
        echo "📋 标准Markdown frontmatter模板:"
        echo "  ---"
        echo "  创建人: [创建者姓名]"
        echo "  版本: 1.0.0"
        echo "  批准日期: YYYY-MM-DD"
        echo "  最后修订: YYYY-MM-DD"
        echo "  本次修订内容: [修改描述]"
        echo "  ---"
        echo ""
        echo "  # 文档标题"
        echo "  文档内容..."
        echo ""
        echo "💡 建议: 在文件开头添加标准YAML frontmatter"
        echo ""
        echo "🔧 自定义配置："
        echo "  可通过环境变量 MD_FRONTMATTER_REQUIRED_FIELDS 自定义必需字段"
        echo "  当前配置: ${#REQUIRED_FIELDS[@]} 个必需字段"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    } >&2

    if [ "$VALIDATOR_MODE" = "blocking" ]; then
        exit 2
    else
        exit 1
    fi
fi

# 提取 frontmatter（在两个 "---" 之间的内容）
FRONTMATTER=$(awk '/^---$/{f=!f;next}f' "$FILE_PATH" | head -20)

# 检查每个必需字段
MISSING_FIELDS=()
for field in "${REQUIRED_FIELDS[@]}"; do
    if ! echo "$FRONTMATTER" | grep -q "^${field}"; then
        MISSING_FIELDS+=("$field")
    fi
done

# 判断合规性
if [ ${#MISSING_FIELDS[@]} -eq 0 ]; then
    # 完全合规
    debug_log "Markdown frontmatter validation passed"
    echo "✅ Markdown frontmatter合规: $FILE_PATH"
    exit 0
else
    # 不合规 - 输出清晰的错误消息到 stderr
    {
        echo ""
        echo "❌ Markdown frontmatter不合规"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "文件: $FILE_PATH"
        echo ""
        echo "缺少以下必需字段:"
        for missing in "${MISSING_FIELDS[@]}"; do
            echo "  • $missing"
        done
        echo ""
        echo "📋 标准Markdown frontmatter模板:"
        echo "  ---"
        echo "  创建人: [创建者姓名]"
        echo "  版本: 1.0.0"
        echo "  批准日期: YYYY-MM-DD"
        echo "  最后修订: YYYY-MM-DD"
        echo "  本次修订内容: [修改描述]"
        echo "  ---"
        echo ""
        echo "💡 建议: 补充缺失的frontmatter字段"
        echo ""
        echo "🔧 自定义配置："
        echo "  可通过环境变量 MD_FRONTMATTER_REQUIRED_FIELDS 自定义必需字段"
        echo "  当前配置: ${#REQUIRED_FIELDS[@]} 个必需字段"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    } >&2

    if [ "$VALIDATOR_MODE" = "blocking" ]; then
        debug_log "Blocking mode: exit 2"
        exit 2
    else
        debug_log "Warning mode: exit 1"
        exit 1
    fi
fi
