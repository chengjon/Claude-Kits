#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Task Master Context Injector
# ============================================================================
#
# Event: SessionStart
# Purpose: 在新会话启动或恢复时，注入 Task Master 的当前任务上下文
#
# MyStocks 项目设计理念:
#   Claude 的自动压缩会导致上下文丢失，跨会话时"失忆"。
#   解决方案: 利用现有的 Task Master 系统自动注入任务上下文
#   在 SessionStart 时自动读取并注入当前任务信息，使 Claude 能够"继续"之前的工作。
#
# 工作原理:
#   1. 检测会话启动类型（startup, resume, clear, compact）
#   2. 检查 Task Master 是否已初始化（.taskmaster/tasks/tasks.json）
#   3. 读取当前 in-progress 和 pending 任务
#   4. 提取最重要的上下文信息（任务标题、描述、详情）
#   5. 输出摘要到 stdout（SessionStart 的 stdout 会被注入到 Claude！）
#   6. Claude 收到任务上下文后可以继续之前的工作
#
# 退出码（符合 Claude 官方规范）:
#   0: 成功（stdout 会被注入到 Claude 上下文！特例！）
#   1: 警告（显示 stderr 但继续）
#   2: 一般不用于 SessionStart（阻止错误会被忽略）
#
# SessionStart 特有功能:
#   - stdout 会被注入到 Claude 上下文
#   - 可以写入 CLAUDE_ENV_FILE 持久化环境变量
#
# Task Master 文件结构:
#   .taskmaster/
#   ├── tasks/
#   │   ├── tasks.json       # 主任务数据库
#   │   ├── task-1.md       # 单个任务文件
#   │   └── task-2.md
#   └── config.json          # AI 模型配置
#
# 注入策略:
#   - 优先注入 in-progress 任务（当前正在进行的任务）
#   - 其次注入最高优先级的 pending 任务
#   - 限制注入内容在 100 行以内（避免占用过多 tokens）
#
# 安装方法:
#   1. chmod +x session-start-task-master-injector.sh
#   2. 复制到 .claude/hooks/
#   3. 添加到 settings.json:
#      {
#        "hooks": {
#          "SessionStart": [
#            {
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start-task-master-injector.sh"
#              }],
#              "timeout": 5
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 5 秒（快速读取 JSON 文件）
#
# MyStocks 项目特定功能:
#   - 自动检测 Task Master 是否已初始化
#   - 注入当前 in-progress 任务的详细信息
#   - 提醒 Claude 使用 Task Master 命令继续工作
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
TASKMASTER_TASKS_FILE=".taskmaster/tasks/tasks.json"
MAX_INJECTION_LINES=100  # 最多注入 100 行（避免占用太多 tokens）
DEBUG_MODE="${TASKMASTER_INJECT_DEBUG:-false}"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 读取 stdin JSON =====
INPUT_JSON=$(cat)
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"')
SOURCE=$(echo "$INPUT_JSON" | jq -r '.source // "unknown"')

debug_log "Task Master injector started"
debug_log "Session ID: $SESSION_ID"
debug_log "Source: $SOURCE"

# ===== 检查 Task Master 是否已初始化 =====
if [ ! -f "$TASKMASTER_TASKS_FILE" ]; then
    debug_log "Task Master not initialized (no tasks.json found)"
    # 输出简短提示
    cat <<EOF
═══════════════════════════════════════════════════════════════
 Task Master 未初始化
═══════════════════════════════════════════════════════════════

提示: 如需使用 Task Master 管理任务，请运行:
  task-master init

═══════════════════════════════════════════════════════════════
EOF
    exit 0
fi

debug_log "Task Master found at $TASKMASTER_TASKS_FILE"

# ===== 读取 tasks.json =====
if ! TASKS_DATA=$(cat "$TASKMASTER_TASKS_FILE"); then
    debug_log "Failed to read $TASKMASTER_TASKS_FILE"
    exit 0
fi

# ===== 提取 in-progress 和 pending 任务 =====
IN_PROGRESS_TASKS=$(echo "$TASKS_DATA" | jq -r '.tasks[] | select(.status == "in-progress") | "\(.id)|\(.title)"' 2>/dev/null || echo "")
PENDING_TASKS=$(echo "$TASKS_DATA" | jq -r '.tasks[] | select(.status == "pending" and .priority == "high") | "\(.id)|\(.title)"' 2>/dev/null | head -n 3 || echo "")

# ===== 构建注入消息 =====
INJECTION_MESSAGE="
═══════════════════════════════════════════════════════════════
 Task Master 上下文
═══════════════════════════════════════════════════════════════

"

# 如果有 in-progress 任务，优先显示
if [ -n "$IN_PROGRESS_TASKS" ]; then
    INJECTION_MESSAGE="${INJECTION_MESSAGE}## 🔄 当前进行中的任务:\n\n"

    while IFS='|' read -r task_id task_title; do
        if [ -n "$task_id" ]; then
            INJECTION_MESSAGE="${INJECTION_MESSAGE}### Task $task_id: $task_title\n\n"

            # 提取任务详情
            TASK_DESCRIPTION=$(echo "$TASKS_DATA" | jq -r --arg id "$task_id" '.tasks[] | select(.id == $id) | .description' 2>/dev/null || echo "")
            TASK_DETAILS=$(echo "$TASKS_DATA" | jq -r --arg id "$task_id" '.tasks[] | select(.id == $id) | .details' 2>/dev/null || echo "")

            if [ -n "$TASK_DESCRIPTION" ] && [ "$TASK_DESCRIPTION" != "null" ]; then
                INJECTION_MESSAGE="${INJECTION_MESSAGE}**描述**: $TASK_DESCRIPTION\n\n"
            fi

            if [ -n "$TASK_DETAILS" ] && [ "$TASK_DETAILS" != "null" ]; then
                # 限制详情长度（最多30行）
                DETAILS_PREVIEW=$(echo "$TASK_DETAILS" | head -n 30)
                INJECTION_MESSAGE="${INJECTION_MESSAGE}**实现详情**:\n\`\`\`\n$DETAILS_PREVIEW\n\`\`\`\n\n"
            fi
        fi
    done <<< "$IN_PROGRESS_TASKS"

    INJECTION_MESSAGE="${INJECTION_MESSAGE}💡 建议: 使用 \`task-master show $task_id\` 查看完整任务详情\n\n"
fi

# 如果有高优先级的 pending 任务，也显示
if [ -n "$PENDING_TASKS" ]; then
    INJECTION_MESSAGE="${INJECTION_MESSAGE}## 📋 高优先级待办任务:\n\n"

    while IFS='|' read -r task_id task_title; do
        if [ -n "$task_id" ]; then
            INJECTION_MESSAGE="${INJECTION_MESSAGE}- **Task $task_id**: $task_title\n"
        fi
    done <<< "$PENDING_TASKS"

    INJECTION_MESSAGE="${INJECTION_MESSAGE}\n💡 建议: 使用 \`task-master next\` 获取下一个任务\n\n"
fi

# 如果既没有 in-progress 也没有 pending 任务
if [ -z "$IN_PROGRESS_TASKS" ] && [ -z "$PENDING_TASKS" ]; then
    TOTAL_TASKS=$(echo "$TASKS_DATA" | jq '.tasks | length' 2>/dev/null || echo 0)
    COMPLETED_TASKS=$(echo "$TASKS_DATA" | jq '[.tasks[] | select(.status == "done")] | length' 2>/dev/null || echo 0)

    INJECTION_MESSAGE="${INJECTION_MESSAGE}✅ 当前没有进行中的任务\n\n"
    INJECTION_MESSAGE="${INJECTION_MESSAGE}**任务统计**:\n"
    INJECTION_MESSAGE="${INJECTION_MESSAGE}- 总任务数: $TOTAL_TASKS\n"
    INJECTION_MESSAGE="${INJECTION_MESSAGE}- 已完成: $COMPLETED_TASKS\n\n"
    INJECTION_MESSAGE="${INJECTION_MESSAGE}💡 建议: 使用 \`task-master list\` 查看所有任务\n\n"
fi

INJECTION_MESSAGE="${INJECTION_MESSAGE}
═══════════════════════════════════════════════════════════════
"

# ===== 限制注入消息长度 =====
LINE_COUNT=$(echo "$INJECTION_MESSAGE" | wc -l)
if [ "$LINE_COUNT" -gt "$MAX_INJECTION_LINES" ]; then
    debug_log "Injection message too long ($LINE_COUNT lines), truncating to $MAX_INJECTION_LINES"
    INJECTION_MESSAGE=$(echo "$INJECTION_MESSAGE" | head -n "$MAX_INJECTION_LINES")
    INJECTION_MESSAGE="${INJECTION_MESSAGE}\n\n... (内容过长，已截断)\n\n═══════════════════════════════════════════════════════════════\n"
fi

# ===== 输出到 stdout（会被注入到 Claude 上下文）=====
echo -e "$INJECTION_MESSAGE"

debug_log "Task Master context injection completed"

exit 0
