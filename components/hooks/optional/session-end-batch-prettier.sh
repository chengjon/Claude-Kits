#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Batch Prettier (SessionEnd)
# ============================================================================
#
# Event: SessionEnd
# Matcher: N/A (SessionEnd 不支持 matcher)
# Purpose: 在会话结束时自动格式化所有修改过的文件，确保代码风格一致
#
# Reddit 案例设计理念:
#   "Clean exit" - 在离开前自动整理工作空间：
#   - 格式化所有修改过的代码文件
#   - 确保符合项目的代码风格规范
#   - 减少 PR review 中的格式问题
#
#   使用 gentle reminder 策略：
#   - 如果 Prettier 未安装，友好提示而不阻塞
#   - 如果格式化失败，报告但不影响会话结束
#   - 提供格式化摘要供用户查看
#
# 工作原理:
#   1. 检测 Prettier 是否安装（npx prettier --version）
#   2. 查找修改过的文件（通过 git status 或 file-edit-tracker）
#   3. 对支持的文件类型运行 Prettier
#   4. 输出格式化摘要到 additionalContext
#   5. 非阻塞（exit 0），不影响会话结束
#
# 退出码:
#   0: 成功（格式化完成或跳过）
#   1: 警告（格式化部分失败，但不阻止会话结束）
#
# JSON 输出格式:
#   {
#     "hookSpecificOutput": {
#       "hookEventName": "SessionEnd",
#       "additionalContext": "✓ Formatted 12 files with Prettier..."
#     }
#   }
#
# 自定义:
#   - 修改 SUPPORTED_EXTENSIONS 来添加更多文件类型
#   - 修改 PRETTIER_OPTIONS 来调整格式化选项
#   - 修改 MAX_FILES 来限制批量格式化的文件数量
#   - 修改 USE_GIT_STATUS 来改变文件检测方式
#
# 安装方法:
#   1. chmod +x session-end-batch-prettier.sh
#   2. 复制到 .claude/hooks/
#   3. 确保项目安装了 Prettier: npm install -D prettier
#   4. 添加到 settings.json:
#      {
#        "hooks": {
#          "SessionEnd": [
#            {
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-end-batch-prettier.sh"
#              }],
#              "timeout": 60
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 60 秒（格式化操作，取决于文件数量）
#
# 依赖:
#   - Prettier (npm install -D prettier)
#   - 可选: .prettierrc 配置文件
#   - 可选: .prettierignore 忽略文件
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
DEBUG_MODE="${BATCH_PRETTIER_DEBUG:-false}"

# 支持的文件扩展名（Prettier 可以格式化的）
SUPPORTED_EXTENSIONS=(
    "js"
    "jsx"
    "ts"
    "tsx"
    "json"
    "css"
    "scss"
    "less"
    "html"
    "vue"
    "md"
    "yaml"
    "yml"
)

# Prettier 选项（可以留空使用项目的 .prettierrc）
PRETTIER_OPTIONS="${PRETTIER_OPTIONS:---write}"

# 最大格式化文件数（防止意外格式化整个项目）
MAX_FILES="${MAX_FILES:-100}"

# 使用 git status 检测修改的文件（推荐）
USE_GIT_STATUS="${USE_GIT_STATUS:-true}"

# file-edit-tracker 日志路径（如果使用 PostToolUse hook）
EDIT_TRACKER_LOG="${EDIT_TRACKER_LOG:-.claude/logs/file-edit-tracker.log}"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 检查 Prettier 是否安装 =====
check_prettier_installed() {
    debug_log "Checking if Prettier is installed..."

    if npx prettier --version >/dev/null 2>&1; then
        local version=$(npx prettier --version 2>/dev/null || echo "unknown")
        debug_log "Prettier found: $version"
        return 0
    else
        debug_log "Prettier not found"
        return 1
    fi
}

# ===== 获取项目根目录 =====
get_project_root() {
    if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
        echo "$CLAUDE_PROJECT_DIR"
        return
    fi

    if git rev-parse --show-toplevel 2>/dev/null; then
        return
    fi

    pwd
}

# ===== 从 git status 获取修改的文件 =====
get_modified_files_from_git() {
    local project_root="$1"
    debug_log "Getting modified files from git status..."

    cd "$project_root" || return 1

    # 获取所有修改、添加、未跟踪的文件
    git status --porcelain 2>/dev/null | \
        grep -E '^\s*[MARCU?]' | \
        awk '{print $NF}' || true
}

# ===== 从 file-edit-tracker 日志获取修改的文件 =====
get_modified_files_from_tracker() {
    local project_root="$1"
    local tracker_log="$project_root/$EDIT_TRACKER_LOG"

    debug_log "Getting modified files from edit tracker: $tracker_log"

    if [ ! -f "$tracker_log" ]; then
        debug_log "Edit tracker log not found"
        return 1
    fi

    # 提取今天修改的文件（从 file-edit-tracker.sh 日志）
    local today=$(date +%Y-%m-%d)
    grep "^$today" "$tracker_log" 2>/dev/null | \
        awk '{print $NF}' | \
        sort -u || true
}

# ===== 过滤支持的文件类型 =====
filter_supported_files() {
    local files=("$@")
    local filtered=()

    for file in "${files[@]}"; do
        # 跳过不存在的文件
        [ -f "$file" ] || continue

        # 检查扩展名
        local ext="${file##*.}"
        for supported_ext in "${SUPPORTED_EXTENSIONS[@]}"; do
            if [ "$ext" = "$supported_ext" ]; then
                filtered+=("$file")
                break
            fi
        done
    done

    printf '%s\n' "${filtered[@]}"
}

# ===== 运行 Prettier =====
run_prettier() {
    local files=("$@")
    local success_count=0
    local failure_count=0
    local failed_files=()

    debug_log "Formatting ${#files[@]} files with Prettier..."

    for file in "${files[@]}"; do
        debug_log "Formatting: $file"

        if npx prettier $PRETTIER_OPTIONS "$file" >/dev/null 2>&1; then
            success_count=$((success_count + 1))
        else
            failure_count=$((failure_count + 1))
            failed_files+=("$file")
            debug_log "Failed to format: $file"
        fi
    done

    # 返回结果统计
    echo "$success_count"
    echo "$failure_count"
    printf '%s\n' "${failed_files[@]}"
}

# ===== 主逻辑 =====
debug_log "SessionEnd batch-prettier hook triggered"

# 检查 Prettier 是否安装
if ! check_prettier_installed; then
    # Prettier 未安装，友好提示
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionEnd",
    "additionalContext": "ℹ️  Prettier not found. To enable automatic code formatting on session end:\n\n  npm install -D prettier\n\nOptional: Add .prettierrc for custom formatting rules."
  }
}
EOF
    exit 0
fi

# 获取项目根目录
PROJECT_ROOT=$(get_project_root)
debug_log "Project root: $PROJECT_ROOT"

# 获取修改的文件列表
MODIFIED_FILES=()

if [ "$USE_GIT_STATUS" = "true" ]; then
    # 优先使用 git status
    mapfile -t MODIFIED_FILES < <(get_modified_files_from_git "$PROJECT_ROOT")
fi

# 如果 git 方法失败或没有找到文件，尝试 edit tracker
if [ ${#MODIFIED_FILES[@]} -eq 0 ]; then
    mapfile -t MODIFIED_FILES < <(get_modified_files_from_tracker "$PROJECT_ROOT")
fi

# 如果没有找到任何修改的文件
if [ ${#MODIFIED_FILES[@]} -eq 0 ]; then
    debug_log "No modified files found"

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionEnd",
    "additionalContext": "ℹ️  No modified files found for formatting."
  }
}
EOF
    exit 0
fi

debug_log "Found ${#MODIFIED_FILES[@]} modified files"

# 过滤支持的文件类型
cd "$PROJECT_ROOT" || exit 0
mapfile -t FORMATTABLE_FILES < <(filter_supported_files "${MODIFIED_FILES[@]}")

if [ ${#FORMATTABLE_FILES[@]} -eq 0 ]; then
    debug_log "No formattable files found"

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionEnd",
    "additionalContext": "ℹ️  No formattable files found (checked ${#MODIFIED_FILES[@]} modified files)."
  }
}
EOF
    exit 0
fi

debug_log "Found ${#FORMATTABLE_FILES[@]} formattable files"

# 检查是否超过最大文件数限制
if [ ${#FORMATTABLE_FILES[@]} -gt $MAX_FILES ]; then
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionEnd",
    "additionalContext": "⚠️  Found ${#FORMATTABLE_FILES[@]} files to format, which exceeds the limit ($MAX_FILES).\n\nSkipping automatic formatting. To format manually:\n\n  npx prettier --write ."
  }
}
EOF
    exit 1
fi

# 运行 Prettier
PRETTIER_OUTPUT=$(run_prettier "${FORMATTABLE_FILES[@]}")
SUCCESS_COUNT=$(echo "$PRETTIER_OUTPUT" | head -n 1)
FAILURE_COUNT=$(echo "$PRETTIER_OUTPUT" | head -n 2 | tail -n 1)

# 生成输出消息
if [ "$FAILURE_COUNT" -eq 0 ]; then
    # 全部成功
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionEnd",
    "additionalContext": "✓ Formatted $SUCCESS_COUNT files with Prettier\n\nAll modified code files have been formatted according to project style guidelines."
  }
}
EOF
    exit 0
else
    # 部分失败
    FAILED_FILES=$(echo "$PRETTIER_OUTPUT" | tail -n +3)

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionEnd",
    "additionalContext": "⚠️  Formatted $SUCCESS_COUNT files, but $FAILURE_COUNT files failed:\n\n$FAILED_FILES\n\nCheck Prettier configuration or file syntax errors."
  }
}
EOF
    exit 1
fi
