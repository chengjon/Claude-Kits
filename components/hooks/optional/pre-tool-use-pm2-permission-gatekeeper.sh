#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: PM2 Permission Gatekeeper
# ============================================================================
#
# Event: PreToolUse
# Matcher: Bash
# Purpose: 控制 PM2 命令权限，自动批准只读命令，要求确认变更命令，阻止危险命令
#
# Reddit 案例设计理念:
#   让 Claude 能够安全地管理和调试后端服务：
#   - 自动批准只读命令（logs, monit, status）
#   - 要求确认变更命令（restart, stop, reload）
#   - 阻止危险命令（delete all, kill）
#
#   结果：Claude 可以诊断和修复后端问题，但不会意外破坏服务
#
# 工作原理:
#   1. 检测 tool_input.command 是否包含 pm2 命令
#   2. 根据命令类型返回不同的 permissionDecision
#   3. 使用 JSON hookSpecificOutput 控制权限
#
# 退出码:
#   0: 成功（允许或已处理）
#   2: 阻止（危险命令）
#
# JSON 输出格式:
#   {
#     "hookSpecificOutput": {
#       "hookEventName": "PreToolUse",
#       "permissionDecision": "allow|deny|ask",
#       "permissionDecisionReason": "原因说明"
#     }
#   }
#
# 安装方法:
#   1. chmod +x pre-tool-use-pm2-permission-gatekeeper.sh
#   2. 复制到 .claude/hooks/
#   3. 添加到 settings.json:
#      {
#        "hooks": {
#          "PreToolUse": [
#            {
#              "matcher": "Bash",
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-pm2-permission-gatekeeper.sh"
#              }],
#              "timeout": 2
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 2 秒（只是检查命令，应该很快）
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
DEBUG_MODE="${PM2_GATEKEEPER_DEBUG:-false}"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 读取 stdin JSON =====
INPUT_JSON=$(cat)
TOOL_NAME=$(echo "$INPUT_JSON" | jq -r '.tool_name // "Unknown"')

debug_log "Tool name: $TOOL_NAME"

# ===== 只处理 Bash 工具 =====
if [ "$TOOL_NAME" != "Bash" ]; then
    debug_log "Not a Bash tool, skipping"
    exit 0
fi

# ===== 提取命令 =====
COMMAND=$(echo "$INPUT_JSON" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
    debug_log "No command found, skipping"
    exit 0
fi

debug_log "Command: $COMMAND"

# ===== 检查是否是 PM2 命令 =====
if ! echo "$COMMAND" | grep -qE '\bpm2\b'; then
    debug_log "Not a PM2 command, allowing"
    exit 0
fi

debug_log "PM2 command detected, applying permission gate"

# ===== 只读命令（自动批准）=====
if echo "$COMMAND" | grep -qE 'pm2\s+(logs?|monit|status|list|show|desc|describe|info|env|ls)'; then
    debug_log "Read-only PM2 command, auto-approving"

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "PM2 read-only command (logs/monit/status) auto-approved for backend observability"
  }
}
EOF
    exit 0
fi

# ===== 危险命令（阻止）=====
if echo "$COMMAND" | grep -qE 'pm2\s+(delete\s+all|kill|flush\s+all|reset\s+all)'; then
    debug_log "Dangerous PM2 command, denying"

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "PM2 dangerous command blocked (delete all/kill/flush all). Use specific service names instead."
  }
}
EOF
    exit 2
fi

# ===== 变更命令（要求确认）=====
if echo "$COMMAND" | grep -qE 'pm2\s+(restart|stop|reload|delete|start|save|dump|resurrect|unstartup|update)'; then
    debug_log "PM2 state-changing command, asking for confirmation"

    # 提取服务名称（如果有）
    SERVICE_NAME=$(echo "$COMMAND" | grep -oE 'pm2\s+\w+\s+\S+' | awk '{print $3}' || echo "")

    if [ -n "$SERVICE_NAME" ] && [ "$SERVICE_NAME" != "all" ]; then
        REASON="PM2 state-changing command requires confirmation: affecting service '$SERVICE_NAME'"
    else
        REASON="PM2 state-changing command requires confirmation: may affect multiple services"
    fi

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "$REASON"
  }
}
EOF
    exit 0
fi

# ===== 其他 PM2 命令（要求确认）=====
debug_log "Unknown PM2 command, asking for confirmation"

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "Unknown PM2 command requires user confirmation"
  }
}
EOF

exit 0
