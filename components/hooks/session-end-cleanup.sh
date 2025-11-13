#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Session End Cleanup
# ============================================================================
#
# Event: SessionEnd
# Purpose: 会话结束时清理临时文件和日志
#
# 清理策略:
#   1. 清理当前会话的编辑日志（从 edit_log.jsonl 中移除）
#   2. 保留最近 5000 条编辑记录（防止日志文件过大）
#   3. 不删除任何业务数据或代码
#
# 工作原理:
#   1. 从 stdin 读取 session_id
#   2. 从 .claude/edit_log.jsonl 中删除当前会话的记录
#   3. 如果日志文件过大，截断到最后 5000 行
#   4. 清理超过 7 天的旧编辑日志
#
# 退出码（符合 Claude 官方规范）:
#   0: 成功
#   1: 警告（显示 stderr 但继续）
#   2: 一般不用于 SessionEnd
#
# SessionEnd 特点:
#   - 不支持 stdout 注入（不会显示给用户）
#   - 适合清理、归档等后台操作
#   - 应该快速完成（避免延迟关闭）
#
# 安装方法:
#   1. chmod +x session-end-cleanup.sh
#   2. 复制到 .claude/hooks/
#   3. 添加到 settings.json:
#      {
#        "hooks": {
#          "SessionEnd": [
#            {
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-end-cleanup.sh"
#              }],
#              "timeout": 5
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 5 秒（快速清理）
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
EDIT_LOG_FILE="${CLAUDE_EDIT_LOG:-.claude/edit_log.jsonl}"
MAX_LOG_LINES=5000  # 保留最后 5000 条记录
DEBUG_MODE="${SESSION_CLEANUP_DEBUG:-false}"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 读取 stdin JSON =====
INPUT_JSON=$(cat)
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"')

debug_log "Session end cleanup started for session: $SESSION_ID"

# ===== 如果编辑日志不存在，跳过 =====
if [ ! -f "$EDIT_LOG_FILE" ]; then
    debug_log "No edit log found, skipping cleanup"
    exit 0
fi

# ===== 清理当前会话的编辑记录 =====
debug_log "Removing edit records for session $SESSION_ID"

# 使用 jq 过滤掉当前会话的记录
if TMP_FILE=$(mktemp); then
    jq --arg sid "$SESSION_ID" 'select(.session_id != $sid)' "$EDIT_LOG_FILE" > "$TMP_FILE" 2>/dev/null || true

    # 检查临时文件是否有内容
    if [ -s "$TMP_FILE" ]; then
        mv "$TMP_FILE" "$EDIT_LOG_FILE"
        debug_log "Edit log updated, current session records removed"
    else
        debug_log "No records found for other sessions, keeping original log"
        rm -f "$TMP_FILE"
    fi
else
    debug_log "Failed to create temporary file, skipping cleanup"
fi

# ===== 截断日志文件（如果过大）=====
if [ -f "$EDIT_LOG_FILE" ]; then
    LINE_COUNT=$(wc -l < "$EDIT_LOG_FILE")

    if [ "$LINE_COUNT" -gt "$MAX_LOG_LINES" ]; then
        debug_log "Log file has $LINE_COUNT lines, truncating to last $MAX_LOG_LINES"

        if TMP_FILE=$(mktemp); then
            tail -n "$MAX_LOG_LINES" "$EDIT_LOG_FILE" > "$TMP_FILE"
            mv "$TMP_FILE" "$EDIT_LOG_FILE"
            debug_log "Log file truncated successfully"
        fi
    else
        debug_log "Log file size OK ($LINE_COUNT lines)"
    fi
fi

debug_log "Session end cleanup completed"

exit 0
