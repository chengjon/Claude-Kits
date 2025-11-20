#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Skills Auto-Activation System
# ============================================================================
#
# Event: UserPromptSubmit
# Purpose: 强制激活相关 Skills 在 Claude 处理用户提示之前
#
# Reddit 案例核心发现:
#   Claude 不会自动加载/采用所有 Skill 文档！
#   必须通过 UserPromptSubmit Hook + skill-rules.json 强制激活。
#
# 工作原理:
#   1. 从 stdin 读取用户提示（prompt 字段）
#   2. 读取 .claude/skill-rules.json 配置
#   3. 匹配规则：关键词、文件模式、意图正则、内容触发器
#   4. 输出 JSON additionalContext 注入 Claude
#   5. Claude 收到上下文后会加载对应的 Skills
#
# 退出码:
#   0: 成功（stdout 会被注入到 Claude 上下文！特例！）
#   1: 警告（显示 stderr 但继续）
#   2: 阻止提示处理（清除原始提示）
#
# JSON 输出格式:
#   {
#     "hookSpecificOutput": {
#       "hookEventName": "UserPromptSubmit",
#       "additionalContext": "SKILL ACTIVATION CHECK: using backend-dev-guidelines..."
#     }
#   }
#
# skill-rules.json 格式 (基于 claude-code-infrastructure-showcase):
#   {
#     "version": "1.0",
#     "skills": {
#       "backend-dev-guidelines": {
#         "type": "domain",
#         "enforcement": "suggest",
#         "priority": "high",
#         "description": "Backend development patterns",
#         "promptTriggers": {
#           "keywords": ["route", "controller", "API"],
#           "intentPatterns": ["(create|add).*API"]
#         },
#         "fileTriggers": {
#           "pathPatterns": ["src/**/*.ts"],
#           "contentPatterns": ["router\\."]
#         }
#       }
#     }
#   }
#
# 安装方法:
#   1. chmod +x user-prompt-submit-skill-activation.sh
#   2. 复制到 .claude/hooks/
#   3. 创建 .claude/skill-rules.json（使用模板）
#   4. 添加到 settings.json:
#      {
#        "hooks": {
#          "UserPromptSubmit": [
#            {
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/user-prompt-submit-skill-activation.sh"
#              }]
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 5 秒（快速匹配，不应该超时）
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
SKILL_RULES_FILE=".claude/skill-rules.json"
DEBUG_MODE="${SKILL_ACTIVATION_DEBUG:-false}"  # 设置环境变量 SKILL_ACTIVATION_DEBUG=true 启用调试

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 读取 stdin JSON =====
INPUT_JSON=$(cat)
debug_log "Received input JSON"

# ===== 提取用户提示 =====
PROMPT=$(echo "$INPUT_JSON" | jq -r '.prompt // empty')

if [ -z "$PROMPT" ]; then
    debug_log "No prompt field found, skipping skill activation"
    exit 0
fi

debug_log "User prompt: ${PROMPT:0:100}..."  # 只显示前100字符

# ===== 检查 skill-rules.json 是否存在 =====
if [ ! -f "$SKILL_RULES_FILE" ]; then
    debug_log "skill-rules.json not found at $SKILL_RULES_FILE, skipping activation"
    # 不报错，静默跳过（用户可能不想使用此功能）
    exit 0
fi

# ===== 读取 skill-rules.json =====
if ! SKILL_RULES=$(cat "$SKILL_RULES_FILE" 2>/dev/null); then
    echo "Error: Cannot read $SKILL_RULES_FILE" >&2
    exit 1
fi

# ===== 验证 JSON 格式 =====
if ! echo "$SKILL_RULES" | jq empty 2>/dev/null; then
    echo "Error: $SKILL_RULES_FILE contains invalid JSON" >&2
    exit 1
fi

# ===== 匹配规则并收集激活的技能 =====
ACTIVATED_SKILLS=()

# 获取所有技能名称
SKILL_NAMES=$(echo "$SKILL_RULES" | jq -r '.skills | keys[]')
RULE_COUNT=$(echo "$SKILL_NAMES" | wc -l)

debug_log "Found $RULE_COUNT skills in skill-rules.json"

while IFS= read -r SKILL_NAME; do
    if [ -z "$SKILL_NAME" ]; then
        continue
    fi

    SKILL_CONFIG=$(echo "$SKILL_RULES" | jq -c ".skills[\"$SKILL_NAME\"]")
    PRIORITY=$(echo "$SKILL_CONFIG" | jq -r '.priority // "medium"')
    ENFORCEMENT=$(echo "$SKILL_CONFIG" | jq -r '.enforcement // "suggest"')

    # 转换 priority 字符串为数字（用于排序）
    case "$PRIORITY" in
        critical) PRIORITY_NUM=1 ;;
        high) PRIORITY_NUM=2 ;;
        medium) PRIORITY_NUM=3 ;;
        low) PRIORITY_NUM=4 ;;
        *) PRIORITY_NUM=999 ;;
    esac

    debug_log "Checking skill: $SKILL_NAME (priority: $PRIORITY, enforcement: $ENFORCEMENT)"

    MATCHED=false

    # ----- 检查关键词匹配 -----
    KEYWORDS=$(echo "$SKILL_CONFIG" | jq -r '.promptTriggers.keywords[]? // empty')
    if [ -n "$KEYWORDS" ]; then
        while IFS= read -r keyword; do
            if [ -z "$keyword" ]; then continue; fi
            if echo "$PROMPT" | grep -qi "$keyword"; then
                debug_log "  ✓ Keyword matched: $keyword"
                MATCHED=true
                break
            fi
        done <<< "$KEYWORDS"
    fi

    # ----- 检查意图正则匹配 -----
    if [ "$MATCHED" = "false" ]; then
        INTENT_PATTERNS=$(echo "$SKILL_CONFIG" | jq -r '.promptTriggers.intentPatterns[]? // empty')
        if [ -n "$INTENT_PATTERNS" ]; then
            while IFS= read -r pattern; do
                if [ -z "$pattern" ]; then continue; fi
                if echo "$PROMPT" | grep -Eq "$pattern"; then
                    debug_log "  ✓ Intent pattern matched: $pattern"
                    MATCHED=true
                    break
                fi
            done <<< "$INTENT_PATTERNS"
        fi
    fi

    # ----- 检查文件模式匹配（如果用户提到了文件路径）-----
    if [ "$MATCHED" = "false" ]; then
        PATH_PATTERNS=$(echo "$SKILL_CONFIG" | jq -r '.fileTriggers.pathPatterns[]? // empty')
        if [ -n "$PATH_PATTERNS" ]; then
            while IFS= read -r pattern; do
                if [ -z "$pattern" ]; then continue; fi
                # 提取提示中可能的文件路径（简单实现）
                if echo "$PROMPT" | grep -Eq "$pattern"; then
                    debug_log "  ✓ File path pattern matched: $pattern"
                    MATCHED=true
                    break
                fi
            done <<< "$PATH_PATTERNS"
        fi
    fi

    # ----- 如果匹配，添加到激活列表 -----
    if [ "$MATCHED" = "true" ]; then
        ACTIVATED_SKILLS+=("$SKILL_NAME:$PRIORITY_NUM:$ENFORCEMENT")
        debug_log "  → Skill activated: $SKILL_NAME"
    else
        debug_log "  ✗ No match for $SKILL_NAME"
    fi
done <<< "$SKILL_NAMES"

# ===== 如果没有匹配的技能，退出 =====
if [ ${#ACTIVATED_SKILLS[@]} -eq 0 ]; then
    debug_log "No skills matched, skipping activation"
    exit 0
fi

# ===== 按优先级排序（数字越小优先级越高）=====
IFS=$'\n' SORTED_SKILLS=($(sort -t: -k2 -n <<< "${ACTIVATED_SKILLS[*]}"))
unset IFS

# ===== 构建技能列表和检查是否有 block enforcement =====
SKILL_LIST=""
HAS_BLOCKING_SKILL=false

for skill_data in "${SORTED_SKILLS[@]}"; do
    # skill_data 格式: "skill-name:priority_num:enforcement"
    skill_name=$(echo "$skill_data" | cut -d: -f1)
    enforcement=$(echo "$skill_data" | cut -d: -f3)

    if [ -z "$SKILL_LIST" ]; then
        SKILL_LIST="$skill_name"
    else
        SKILL_LIST="$SKILL_LIST, $skill_name"
    fi

    # 检查是否有阻塞型技能
    if [ "$enforcement" = "block" ]; then
        HAS_BLOCKING_SKILL=true
    fi
done

debug_log "Activating skills (in priority order): $SKILL_LIST"

# ===== 生成技能文件路径列表（用于 Claude 参考）=====
SKILL_FILES=""
for skill_data in "${SORTED_SKILLS[@]}"; do
    skill_name=$(echo "$skill_data" | cut -d: -f1)
    skill_file=".claude/skills/$skill_name/SKILL.md"

    if [ -f "$skill_file" ]; then
        if [ -z "$SKILL_FILES" ]; then
            SKILL_FILES="$skill_file"
        else
            SKILL_FILES="$SKILL_FILES, $skill_file"
        fi
    fi
done

# ===== 构建激活消息 =====
if [ "$HAS_BLOCKING_SKILL" = "true" ]; then
    ACTIVATION_MESSAGE="⚠️ SKILL ACTIVATION REQUIRED: The following skills are relevant and should be reviewed before proceeding: $SKILL_LIST. Please consult: $SKILL_FILES"
else
    ACTIVATION_MESSAGE="💡 SKILL ACTIVATION SUGGESTED: The following skills may be helpful for this request: $SKILL_LIST. Consider reviewing: $SKILL_FILES"
fi

# ===== 输出 JSON（使用 jq 确保正确转义）=====
jq -n \
    --arg context "$ACTIVATION_MESSAGE" \
    '{
        hookSpecificOutput: {
            hookEventName: "UserPromptSubmit",
            additionalContext: $context
        }
    }'

exit 0
