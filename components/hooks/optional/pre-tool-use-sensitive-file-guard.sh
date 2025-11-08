#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Sensitive File Guard
# ============================================================================
#
# Event: PreToolUse
# Matcher: Edit|Write
# Purpose: 阻止修改敏感文件（credentials, keys, configs）
#
# Reddit 案例设计理念:
#   防止 Claude 意外修改或泄露敏感文件：
#   - .env 文件（环境变量、API keys）
#   - SSH 密钥（id_rsa, id_ed25519）
#   - AWS/Cloud credentials
#   - 数据库配置文件
#
#   使用 deny 而非 ask，因为这些文件通常不应该被 AI 修改
#
# 工作原理:
#   1. 检测 tool_input.file_path
#   2. 匹配敏感文件模式（使用正则表达式）
#   3. 如果匹配，返回 deny 并提供清晰的原因
#
# 退出码:
#   0: 非敏感文件，允许
#   2: 敏感文件，阻止
#
# JSON 输出格式:
#   {
#     "hookSpecificOutput": {
#       "hookEventName": "PreToolUse",
#       "permissionDecision": "deny",
#       "permissionDecisionReason": "Security policy: Cannot modify .env files"
#     }
#   }
#
# 自定义:
#   修改 SENSITIVE_PATTERNS 数组来添加你的敏感文件模式
#
# 安装方法:
#   1. chmod +x pre-tool-use-sensitive-file-guard.sh
#   2. 复制到 .claude/hooks/
#   3. 添加到 settings.json:
#      {
#        "hooks": {
#          "PreToolUse": [
#            {
#              "matcher": "Edit|Write",
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-sensitive-file-guard.sh"
#              }],
#              "timeout": 2
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 2 秒（只是检查文件路径）
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
DEBUG_MODE="${SENSITIVE_GUARD_DEBUG:-false}"

# 敏感文件模式（正则表达式）
SENSITIVE_PATTERNS=(
    # 环境变量和配置
    '\.env$'
    '\.env\.'
    'credentials\.json$'
    'config/secrets\.'

    # SSH 密钥
    '\.ssh/id_rsa'
    '\.ssh/id_ed25519'
    '\.ssh/id_ecdsa'
    '\.ssh/id_dsa'
    '\.ssh/.*_rsa$'
    '\.ssh/.*\.pem$'

    # Cloud provider credentials
    '\.aws/credentials$'
    '\.aws/config$'
    '\.azure/credentials$'
    '\.gcloud/credentials\.json$'
    '\.kube/config$'

    # Database configurations
    'database\.yml$'
    'database\.ini$'
    '\.my\.cnf$'
    '\.pgpass$'

    # API keys and tokens
    '\.npmrc$'
    '\.pypirc$'
    '\.netrc$'
    'auth\.json$'
    'token\.json$'

    # Private keys
    '\.pem$'
    '\.key$'
    '\.p12$'
    '\.pfx$'
    'private.*\.key$'

    # Git credentials
    '\.git-credentials$'
    '\.gitconfig$'  # 可能包含 token

    # Docker
    '\.docker/config\.json$'
)

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

# ===== 只处理 Edit 和 Write 工具 =====
if [ "$TOOL_NAME" != "Edit" ] && [ "$TOOL_NAME" != "Write" ]; then
    debug_log "Not Edit or Write tool, skipping"
    exit 0
fi

# ===== 提取文件路径 =====
FILE_PATH=$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
    debug_log "No file_path found, skipping"
    exit 0
fi

debug_log "Checking file: $FILE_PATH"

# ===== 检查敏感文件模式 =====
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if echo "$FILE_PATH" | grep -qE "$pattern"; then
        debug_log "BLOCKED: Matched sensitive pattern: $pattern"

        # 提取匹配的模式类型（用于更好的错误消息）
        PATTERN_DESC="sensitive file"

        if echo "$pattern" | grep -q '\.env'; then
            PATTERN_DESC="environment variable file (.env)"
        elif echo "$pattern" | grep -q '\.ssh'; then
            PATTERN_DESC="SSH key file"
        elif echo "$pattern" | grep -q '\(aws\|azure\|gcloud\|kube\)'; then
            PATTERN_DESC="cloud provider credentials"
        elif echo "$pattern" | grep -q 'database'; then
            PATTERN_DESC="database configuration file"
        elif echo "$pattern" | grep -q '\(key\|pem\|p12\|pfx\)'; then
            PATTERN_DESC="private key file"
        elif echo "$pattern" | grep -q 'credentials'; then
            PATTERN_DESC="credentials file"
        fi

        cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Security policy: Cannot modify $PATTERN_DESC ($FILE_PATH). These files contain sensitive information and should be edited manually."
  }
}
EOF
        exit 2
    fi
done

# ===== 额外检查：文件名包含 secret, password, credential 等词 =====
if echo "$FILE_PATH" | grep -qiE '(secret|password|credential|token|apikey|api_key)'; then
    # 排除测试文件和示例文件
    if ! echo "$FILE_PATH" | grep -qiE '\.(test|spec|example|sample|template)\.' && \
       ! echo "$FILE_PATH" | grep -qiE '/(test|example|sample|template)/'; then

        debug_log "BLOCKED: File name contains sensitive keyword"

        cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Security policy: File name suggests sensitive content ($FILE_PATH). If this is not sensitive, rename the file or add to exception list."
  }
}
EOF
        exit 2
    fi
fi

# ===== 文件安全，允许编辑 =====
debug_log "File is safe to edit"
exit 0
