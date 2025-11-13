#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Documentation Update Reminder
# ============================================================================
#
# Event: PostToolUse
# Matcher: .*  (所有工具)
# Purpose: 当检测到任务完成、新增文件等关键操作时，提醒 AI 更新相关文档
#
# 设计理念:
#   在开发过程中，AI 经常会完成任务、创建新文件、实现新功能，
#   但可能忘记同步更新 README.md、CHANGELOG.md、文档等。
#
#   此 Hook 通过关键词检测，自动提醒 AI 考虑更新相关文档，
#   确保文档始终与代码保持同步。
#
# 工作原理:
#   1. 从 stdin 读取工具输出内容（tool_response）
#   2. 检测关键触发词，如：
#      - "任务完成"、"已完成"、"完成实施"
#      - "新增文件"、"创建文件"、"新建"
#      - "实现功能"、"新功能"
#      - "修改"、"更新"
#   3. 如果匹配，输出提醒消息到 stderr（显示给用户但不阻塞）
#   4. 提醒 AI 检查并更新以下文档：
#      - README.md
#      - CHANGELOG.md
#      - docs/ 目录下的相关文档
#      - 项目特定的文档文件
#
# 退出码:
#   0: 成功（非阻塞）
#   1: 警告（显示 stderr 但继续）
#   2: 阻止（不使用，因为这只是提醒）
#
# 配置文件 (.claude/doc-update-rules.json):
#   {
#     "enabled": true,
#     "triggerPatterns": [
#       "任务.*完成",
#       "已完成",
#       "新增.*文件",
#       "创建.*文件",
#       "实现.*功能",
#       "添加.*功能"
#     ],
#     "documentsToCheck": [
#       "README.md",
#       "CHANGELOG.md",
#       "IFLOW.md",
#       "docs/**/*.md",
#       "QUICK_INSTALL_GUIDE.md"
#     ],
#     "reminderTemplate": "📝 文档更新提醒：检测到 {trigger}，请考虑更新以下文档：{docs}",
#     "cooldownMinutes": 10
#   }
#
# 安装方法:
#   1. chmod +x post-tool-use-doc-update-reminder.sh
#   2. 复制到 .claude/hooks/
#   3. (可选) 创建 .claude/doc-update-rules.json 自定义规则
#   4. 添加到 settings.json:
#      {
#        "hooks": {
#          "PostToolUse": [
#            {
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-doc-update-reminder.sh"
#              }],
#              "timeout": 3
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 3 秒（只是检查和提醒，应该很快）
#
# 配合使用:
#   - 可以与 TodoWrite 工具集成，自动添加文档更新任务
#   - 可以与 git hooks 配合，commit 前检查文档是否更新
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
CONFIG_FILE=".claude/doc-update-rules.json"
DEBUG_MODE="${DOC_UPDATE_DEBUG:-false}"
COOLDOWN_FILE="$HOME/.claude/doc_update_reminder_last.txt"

# 默认触发模式（如果没有配置文件）
DEFAULT_TRIGGERS=(
    "任务.*完成"
    "已完成"
    "完成实施"
    "新增.*文件"
    "创建.*文件"
    "新建.*文件"
    "实现.*功能"
    "添加.*功能"
    "新功能"
    "修改完成"
    "更新完成"
    "集成完成"
    "开发完成"
    "构建完成"
    "测试通过"
    "部署完成"
    "发布.*版本"
)

# 默认需要检查的文档
DEFAULT_DOCS=(
    "README.md"
    "CHANGELOG.md"
    "IFLOW.md"
    "QUICK_INSTALL_GUIDE.md"
    "docs/INSTALLATION.md"
    "docs/"
)

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 检查冷却时间（避免短时间内重复提醒）=====
check_cooldown() {
    local cooldown_minutes=${1:-10}

    if [ -f "$COOLDOWN_FILE" ]; then
        local last_reminder=$(cat "$COOLDOWN_FILE")
        local current_time=$(date +%s)
        local time_diff=$((current_time - last_reminder))
        local cooldown_seconds=$((cooldown_minutes * 60))

        if [ $time_diff -lt $cooldown_seconds ]; then
            debug_log "Cooldown active: $time_diff seconds since last reminder (cooldown: $cooldown_seconds)"
            return 1  # 在冷却期内
        fi
    fi

    return 0  # 不在冷却期
}

# ===== 记录提醒时间 =====
record_reminder_time() {
    mkdir -p "$(dirname "$COOLDOWN_FILE")"
    date +%s > "$COOLDOWN_FILE"
}

# ===== 读取 stdin JSON =====
INPUT_JSON=$(cat)
debug_log "Received input JSON"

# ===== 提取工具名称和响应 =====
TOOL_NAME=$(echo "$INPUT_JSON" | jq -r '.tool_name // "Unknown"')
TOOL_RESPONSE=$(echo "$INPUT_JSON" | jq -r '.tool_response // empty')

debug_log "Tool: $TOOL_NAME"

# ===== 如果没有工具响应，跳过 =====
if [ -z "$TOOL_RESPONSE" ]; then
    debug_log "No tool_response found, skipping"
    exit 0
fi

# ===== 检查工具是否成功 =====
SUCCESS=$(echo "$INPUT_JSON" | jq -r '.tool_response.success // true')
if [ "$SUCCESS" != "true" ]; then
    debug_log "Tool execution failed, skipping reminder"
    exit 0
fi

# ===== 读取配置文件（如果存在）=====
ENABLED=true
COOLDOWN_MINUTES=10
TRIGGERS=("${DEFAULT_TRIGGERS[@]}")
DOCS_TO_CHECK=("${DEFAULT_DOCS[@]}")

if [ -f "$CONFIG_FILE" ]; then
    debug_log "Loading config from $CONFIG_FILE"

    # 读取 enabled 状态
    if ENABLED_VALUE=$(jq -r '.enabled // true' "$CONFIG_FILE" 2>/dev/null); then
        ENABLED=$ENABLED_VALUE
    fi

    # 如果禁用，直接退出
    if [ "$ENABLED" != "true" ]; then
        debug_log "Doc update reminder is disabled"
        exit 0
    fi

    # 读取冷却时间
    if COOLDOWN_VALUE=$(jq -r '.cooldownMinutes // 10' "$CONFIG_FILE" 2>/dev/null); then
        COOLDOWN_MINUTES=$COOLDOWN_VALUE
    fi

    # 读取自定义触发模式
    if CUSTOM_TRIGGERS=$(jq -r '.triggerPatterns[]? // empty' "$CONFIG_FILE" 2>/dev/null); then
        if [ -n "$CUSTOM_TRIGGERS" ]; then
            TRIGGERS=()
            while IFS= read -r pattern; do
                if [ -n "$pattern" ]; then
                    TRIGGERS+=("$pattern")
                fi
            done <<< "$CUSTOM_TRIGGERS"
        fi
    fi

    # 读取自定义文档列表
    if CUSTOM_DOCS=$(jq -r '.documentsToCheck[]? // empty' "$CONFIG_FILE" 2>/dev/null); then
        if [ -n "$CUSTOM_DOCS" ]; then
            DOCS_TO_CHECK=()
            while IFS= read -r doc; do
                if [ -n "$doc" ]; then
                    DOCS_TO_CHECK+=("$doc")
                fi
            done <<< "$CUSTOM_DOCS"
        fi
    fi
fi

debug_log "Enabled: $ENABLED, Cooldown: $COOLDOWN_MINUTES minutes"
debug_log "Checking ${#TRIGGERS[@]} trigger patterns"

# ===== 检查冷却时间 =====
if ! check_cooldown "$COOLDOWN_MINUTES"; then
    debug_log "Skipping reminder due to cooldown"
    exit 0
fi

# ===== 将 JSON 转换为纯文本进行匹配 =====
# 提取所有可能包含文本的字段
RESPONSE_TEXT=$(echo "$TOOL_RESPONSE" | jq -r '.. | strings' 2>/dev/null | tr '\n' ' ')

if [ -z "$RESPONSE_TEXT" ]; then
    debug_log "Could not extract text from tool_response"
    exit 0
fi

debug_log "Response text: ${RESPONSE_TEXT:0:200}..."  # 只显示前200字符

# ===== 检测触发模式 =====
MATCHED=false
MATCHED_PATTERN=""

for pattern in "${TRIGGERS[@]}"; do
    if echo "$RESPONSE_TEXT" | grep -Eq "$pattern"; then
        MATCHED=true
        MATCHED_PATTERN="$pattern"
        debug_log "✓ Matched pattern: $pattern"
        break
    fi
done

# ===== 如果没有匹配，退出 =====
if [ "$MATCHED" != "true" ]; then
    debug_log "No trigger patterns matched"
    exit 0
fi

# ===== 记录此次提醒时间 =====
record_reminder_time

# ===== 构建文档列表字符串 =====
DOCS_STRING=""
for doc in "${DOCS_TO_CHECK[@]}"; do
    if [ -z "$DOCS_STRING" ]; then
        DOCS_STRING="$doc"
    else
        DOCS_STRING="$DOCS_STRING, $doc"
    fi
done

# ===== 输出提醒消息（stderr，非阻塞）=====
cat >&2 <<EOF

📝 ============================================================
   文档更新提醒
============================================================

检测到触发关键词: "$MATCHED_PATTERN"

建议检查并更新以下文档：
$(for doc in "${DOCS_TO_CHECK[@]}"; do echo "  • $doc"; done)

更新要点：
  ✓ 新增功能是否已记录到 README.md？
  ✓ 安装步骤是否需要更新？
  ✓ CHANGELOG.md 是否记录了变更？
  ✓ 技术文档是否与实现保持同步？
  ✓ 示例代码是否需要更新？

💡 提示：可以使用以下命令快速检查：
   git status docs/ README.md CHANGELOG.md
   git diff docs/ README.md CHANGELOG.md

⏭️  如果文档已是最新，可以忽略此提醒。
============================================================

EOF

debug_log "Reminder sent successfully"

# 非阻塞成功退出
exit 0
