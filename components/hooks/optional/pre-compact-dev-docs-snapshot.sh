#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Dev Docs Snapshot (PreCompact)
# ============================================================================
#
# Event: PreCompact
# Matcher: N/A (PreCompact 不支持 matcher)
# Purpose: 在对话压缩前保存开发文档快照，防止上下文丢失
#
# Reddit 案例设计理念:
#   Claude Code 会定期压缩对话历史以节省 token，但这会导致上下文丢失。
#   Reddit 案例通过在压缩前自动保存 Dev Docs 来解决这个问题：
#   - plan.md: 当前架构和设计决策
#   - context.md: 项目背景和技术栈
#   - tasks.md: 进行中的任务和待办事项
#
#   结果：即使对话被压缩，核心上下文仍然保留在 Dev Docs 中，
#        SessionStart 时可以通过 dev-docs-injector 恢复
#
# 工作原理:
#   1. PreCompact 触发时，调用 /dev-docs-update slash command
#   2. 将当前会话的关键信息写入 Dev Docs 文件
#   3. 输出 additionalContext 提示 Claude 已保存快照
#   4. 非阻塞（exit 0），不影响压缩流程
#
# 退出码:
#   0: 成功（非阻塞，始终允许压缩）
#   1: 警告（快照失败，但不阻止压缩）
#
# JSON 输出格式:
#   {
#     "hookSpecificOutput": {
#       "hookEventName": "PreCompact",
#       "additionalContext": "Dev Docs snapshot saved before compaction..."
#     }
#   }
#
# 自定义:
#   - 修改 DEV_DOCS_DIR 来改变 Dev Docs 存储位置
#   - 修改 DEV_DOCS_FILES 来添加更多文档文件
#   - 修改 SNAPSHOT_BACKUP 来控制是否创建备份副本
#
# 安装方法:
#   1. chmod +x pre-compact-dev-docs-snapshot.sh
#   2. 复制到 .claude/hooks/
#   3. 添加到 settings.json:
#      {
#        "hooks": {
#          "PreCompact": [
#            {
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-compact-dev-docs-snapshot.sh"
#              }],
#              "timeout": 10
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 10 秒（文件 I/O 操作，通常 < 5 秒）
#
# Reddit 案例集成:
#   配合 session-start-dev-docs-injector.sh 使用：
#   - PreCompact: 保存快照（此脚本）
#   - SessionStart: 恢复上下文（dev-docs-injector.sh）
#   结果：上下文在对话压缩后仍然保留，Claude 能够继续之前的工作
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
DEBUG_MODE="${DEV_DOCS_SNAPSHOT_DEBUG:-false}"

# Dev Docs 目录（相对于项目根目录）
DEV_DOCS_DIR="${DEV_DOCS_DIR:-.claude/dev-docs}"

# Dev Docs 文件列表
DEV_DOCS_FILES=(
    "plan.md"       # 架构和设计决策
    "context.md"    # 项目背景和技术栈
    "tasks.md"      # 任务和待办事项
)

# 是否创建备份副本（带时间戳）
SNAPSHOT_BACKUP="${SNAPSHOT_BACKUP:-true}"

# 最大备份数量（超过则删除最旧的）
MAX_BACKUPS="${MAX_BACKUPS:-5}"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 获取项目根目录 =====
get_project_root() {
    # 优先使用 CLAUDE_PROJECT_DIR 环境变量
    if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
        echo "$CLAUDE_PROJECT_DIR"
        return
    fi

    # 否则尝试查找 git 根目录
    if git rev-parse --show-toplevel 2>/dev/null; then
        return
    fi

    # 最后使用当前工作目录
    pwd
}

# ===== 创建备份 =====
create_backup() {
    local file_path="$1"
    local backup_dir="$DEV_DOCS_DIR/.backups"
    local file_name=$(basename "$file_path")
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$backup_dir/${file_name%.md}_${timestamp}.md"

    debug_log "Creating backup: $backup_path"

    # 确保备份目录存在
    mkdir -p "$backup_dir"

    # 创建备份
    cp "$file_path" "$backup_path" 2>/dev/null || {
        debug_log "Failed to create backup for $file_path"
        return 1
    }

    # 清理旧备份（保留最新的 MAX_BACKUPS 个）
    local backup_pattern="${file_name%.md}_*.md"
    local backup_count=$(find "$backup_dir" -name "$backup_pattern" -type f 2>/dev/null | wc -l)

    if [ "$backup_count" -gt "$MAX_BACKUPS" ]; then
        debug_log "Cleaning old backups (keeping $MAX_BACKUPS)"
        find "$backup_dir" -name "$backup_pattern" -type f -printf '%T@ %p\n' 2>/dev/null | \
            sort -n | \
            head -n -$MAX_BACKUPS | \
            cut -d' ' -f2- | \
            xargs rm -f
    fi

    return 0
}

# ===== 检查 Dev Docs 文件 =====
check_dev_docs_files() {
    local project_root="$1"
    local dev_docs_path="$project_root/$DEV_DOCS_DIR"
    local files_exist=0
    local total_size=0

    debug_log "Checking Dev Docs at: $dev_docs_path"

    if [ ! -d "$dev_docs_path" ]; then
        debug_log "Dev Docs directory does not exist: $dev_docs_path"
        return 1
    fi

    for file in "${DEV_DOCS_FILES[@]}"; do
        local file_path="$dev_docs_path/$file"
        if [ -f "$file_path" ]; then
            files_exist=$((files_exist + 1))
            local size=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null || echo 0)
            total_size=$((total_size + size))
            debug_log "Found: $file (${size} bytes)"

            # 创建备份（如果启用）
            if [ "$SNAPSHOT_BACKUP" = "true" ]; then
                create_backup "$file_path"
            fi
        else
            debug_log "Missing: $file"
        fi
    done

    debug_log "Found $files_exist/${#DEV_DOCS_FILES[@]} Dev Docs files, total size: ${total_size} bytes"

    # 如果至少有一个文件存在，返回成功
    [ $files_exist -gt 0 ]
}

# ===== 生成快照摘要 =====
generate_snapshot_summary() {
    local project_root="$1"
    local dev_docs_path="$project_root/$DEV_DOCS_DIR"
    local summary=""

    for file in "${DEV_DOCS_FILES[@]}"; do
        local file_path="$dev_docs_path/$file"
        if [ -f "$file_path" ]; then
            local size=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null || echo 0)
            local lines=$(wc -l < "$file_path" 2>/dev/null || echo 0)
            summary="${summary}\n  - $file: ${lines} lines, ${size} bytes"
        fi
    done

    echo -e "$summary"
}

# ===== 主逻辑 =====
debug_log "PreCompact hook triggered"

# 获取项目根目录
PROJECT_ROOT=$(get_project_root)
debug_log "Project root: $PROJECT_ROOT"

# 检查 Dev Docs 文件
if check_dev_docs_files "$PROJECT_ROOT"; then
    # 生成快照摘要
    SNAPSHOT_SUMMARY=$(generate_snapshot_summary "$PROJECT_ROOT")

    debug_log "Dev Docs snapshot saved successfully"

    # 输出成功消息（带 additionalContext）
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreCompact",
    "additionalContext": "✓ Dev Docs snapshot saved before compaction\n\nSaved files:${SNAPSHOT_SUMMARY}\n\nContext will be preserved across conversation compaction. Use SessionStart hook to restore context in next session."
  }
}
EOF

    exit 0
else
    # 没有 Dev Docs 文件，输出提示（非阻塞）
    debug_log "No Dev Docs found, skipping snapshot"

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreCompact",
    "additionalContext": "ℹ️  No Dev Docs found at $DEV_DOCS_DIR. Consider using /dev-docs-update to create Dev Docs for context preservation across compaction."
  }
}
EOF

    exit 0
fi
