#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Desktop Notifier (Notification)
# ============================================================================
#
# Event: Notification
# Matcher: N/A (Notification 不支持 matcher)
# Purpose: 将 Claude Code 的通知事件转发到操作系统的桌面通知系统
#
# Reddit 案例设计理念:
#   "Awareness without interruption" - 提供关键事件的即时反馈：
#   - 长时间运行的任务完成时通知用户
#   - 错误或警告发生时提醒用户
#   - 构建/测试结果的即时反馈
#
#   使用系统原生通知，无需额外工具：
#   - macOS: osascript (内置)
#   - Linux: notify-send (libnotify)
#   - Windows WSL: powershell.exe (调用 Windows 通知)
#
# 工作原理:
#   1. 从 stdin JSON 读取通知内容和级别
#   2. 检测操作系统类型
#   3. 使用对应的系统通知 API 发送通知
#   4. 根据通知级别设置图标和紧急程度
#   5. 非阻塞（exit 0），通知是异步的
#
# 退出码:
#   0: 成功（通知已发送或已跳过）
#
# JSON 输出格式:
#   {
#     "hookSpecificOutput": {
#       "hookEventName": "Notification",
#       "additionalContext": "Desktop notification sent"
#     }
#   }
#
# 自定义:
#   - 修改 NOTIFICATION_ENABLED 来全局启用/禁用通知
#   - 修改 MIN_LEVEL 来过滤低级别通知（只显示 warning 和 error）
#   - 修改 CUSTOM_SOUND 来使用自定义通知声音
#   - 修改 NOTIFICATION_DURATION 来调整通知显示时长
#
# 安装方法:
#   1. chmod +x notification-desktop-notifier.sh
#   2. 复制到 .claude/hooks/
#   3. Linux 用户需要安装 notify-send:
#      - Ubuntu/Debian: sudo apt-get install libnotify-bin
#      - Fedora/RHEL: sudo dnf install libnotify
#      - Arch: sudo pacman -S libnotify
#   4. 添加到 settings.json:
#      {
#        "hooks": {
#          "Notification": [
#            {
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/notification-desktop-notifier.sh"
#              }],
#              "timeout": 5
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 5 秒（发送通知很快，但系统可能有延迟）
#
# 通知级别:
#   - info: 一般信息（绿色/低优先级）
#   - warning: 警告（黄色/中优先级）
#   - error: 错误（红色/高优先级）
#   - success: 成功（绿色/低优先级）
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
DEBUG_MODE="${DESKTOP_NOTIFIER_DEBUG:-false}"

# 是否启用桌面通知
NOTIFICATION_ENABLED="${NOTIFICATION_ENABLED:-true}"

# 最小通知级别（info, warning, error）
# 设置为 "warning" 则只显示 warning 和 error 通知
MIN_LEVEL="${MIN_LEVEL:-info}"

# 通知显示时长（秒，仅 Linux）
NOTIFICATION_DURATION="${NOTIFICATION_DURATION:-5}"

# 自定义通知声音（可选，仅 macOS）
CUSTOM_SOUND="${CUSTOM_SOUND:-}"

# 通知图标（仅 Linux）
ICON_INFO="${ICON_INFO:-dialog-information}"
ICON_WARNING="${ICON_WARNING:-dialog-warning}"
ICON_ERROR="${ICON_ERROR:-dialog-error}"
ICON_SUCCESS="${ICON_SUCCESS:-emblem-default}"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 检查通知级别是否满足最小级别 =====
check_level_threshold() {
    local level="$1"
    local min_level="$2"

    # 级别优先级: error > warning > info
    case "$min_level" in
        "error")
            [ "$level" = "error" ]
            ;;
        "warning")
            [ "$level" = "error" ] || [ "$level" = "warning" ]
            ;;
        "info")
            true  # 所有级别都显示
            ;;
        *)
            true
            ;;
    esac
}

# ===== 检测操作系统 =====
detect_os() {
    local os_type=""

    if [[ "$OSTYPE" == "darwin"* ]]; then
        os_type="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # 检查是否是 WSL
        if grep -qEi "(Microsoft|WSL)" /proc/version &>/dev/null; then
            os_type="wsl"
        else
            os_type="linux"
        fi
    else
        os_type="unknown"
    fi

    echo "$os_type"
}

# ===== macOS 通知 (osascript) =====
send_notification_macos() {
    local title="$1"
    local message="$2"
    local level="$3"

    debug_log "Sending macOS notification: $title - $message"

    # 构建 osascript 命令
    local script="display notification \"$message\" with title \"$title\""

    # 添加声音（如果配置了）
    if [ -n "$CUSTOM_SOUND" ]; then
        script="$script sound name \"$CUSTOM_SOUND\""
    elif [ "$level" = "error" ]; then
        script="$script sound name \"Basso\""
    fi

    # 发送通知
    osascript -e "$script" 2>/dev/null || {
        debug_log "Failed to send macOS notification"
        return 1
    }

    return 0
}

# ===== Linux 通知 (notify-send) =====
send_notification_linux() {
    local title="$1"
    local message="$2"
    local level="$3"

    debug_log "Sending Linux notification: $title - $message"

    # 检查 notify-send 是否安装
    if ! command -v notify-send &>/dev/null; then
        debug_log "notify-send not found, skipping notification"
        return 1
    fi

    # 根据级别选择图标和紧急程度
    local icon="$ICON_INFO"
    local urgency="normal"

    case "$level" in
        "error")
            icon="$ICON_ERROR"
            urgency="critical"
            ;;
        "warning")
            icon="$ICON_WARNING"
            urgency="normal"
            ;;
        "success")
            icon="$ICON_SUCCESS"
            urgency="low"
            ;;
        *)
            icon="$ICON_INFO"
            urgency="low"
            ;;
    esac

    # 发送通知
    notify-send \
        --icon="$icon" \
        --urgency="$urgency" \
        --expire-time=$((NOTIFICATION_DURATION * 1000)) \
        "$title" \
        "$message" 2>/dev/null || {
        debug_log "Failed to send Linux notification"
        return 1
    }

    return 0
}

# ===== WSL 通知 (powershell.exe) =====
send_notification_wsl() {
    local title="$1"
    local message="$2"
    local level="$3"

    debug_log "Sending WSL (Windows) notification: $title - $message"

    # 检查 powershell.exe 是否可用
    if ! command -v powershell.exe &>/dev/null; then
        debug_log "powershell.exe not found, skipping notification"
        return 1
    fi

    # 转义特殊字符
    title=$(echo "$title" | sed "s/'/\\\'/g")
    message=$(echo "$message" | sed "s/'/\\\'/g")

    # 构建 PowerShell 命令（使用 Windows Toast Notification）
    local ps_script="
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > \$null
        \$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        \$toastXml = [xml] \$template.GetXml()
        \$toastXml.GetElementsByTagName('text')[0].AppendChild(\$toastXml.CreateTextNode('$title')) > \$null
        \$toastXml.GetElementsByTagName('text')[1].AppendChild(\$toastXml.CreateTextNode('$message')) > \$null
        \$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        \$xml.LoadXml(\$toastXml.OuterXml)
        \$toast = [Windows.UI.Notifications.ToastNotification]::new(\$xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Claude Code').Show(\$toast)
    "

    # 发送通知
    powershell.exe -NoProfile -Command "$ps_script" 2>/dev/null || {
        debug_log "Failed to send WSL notification"
        return 1
    }

    return 0
}

# ===== 主逻辑 =====
debug_log "Notification desktop-notifier hook triggered"

# 检查是否启用通知
if [ "$NOTIFICATION_ENABLED" != "true" ]; then
    debug_log "Desktop notifications are disabled"
    exit 0
fi

# 读取 stdin JSON
INPUT_JSON=$(cat)

# 提取通知信息
NOTIFICATION_TITLE=$(echo "$INPUT_JSON" | jq -r '.notification_title // "Claude Code"')
NOTIFICATION_MESSAGE=$(echo "$INPUT_JSON" | jq -r '.notification_message // "Notification"')
NOTIFICATION_LEVEL=$(echo "$INPUT_JSON" | jq -r '.notification_level // "info"')

debug_log "Title: $NOTIFICATION_TITLE"
debug_log "Message: $NOTIFICATION_MESSAGE"
debug_log "Level: $NOTIFICATION_LEVEL"

# 检查是否满足最小级别要求
if ! check_level_threshold "$NOTIFICATION_LEVEL" "$MIN_LEVEL"; then
    debug_log "Notification level ($NOTIFICATION_LEVEL) below minimum threshold ($MIN_LEVEL), skipping"
    exit 0
fi

# 检测操作系统
OS_TYPE=$(detect_os)
debug_log "Detected OS: $OS_TYPE"

# 根据操作系统发送通知
case "$OS_TYPE" in
    "macos")
        send_notification_macos "$NOTIFICATION_TITLE" "$NOTIFICATION_MESSAGE" "$NOTIFICATION_LEVEL"
        ;;
    "linux")
        send_notification_linux "$NOTIFICATION_TITLE" "$NOTIFICATION_MESSAGE" "$NOTIFICATION_LEVEL"
        ;;
    "wsl")
        send_notification_wsl "$NOTIFICATION_TITLE" "$NOTIFICATION_MESSAGE" "$NOTIFICATION_LEVEL"
        ;;
    *)
        debug_log "Unknown OS type, cannot send notification"
        cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "Notification",
    "additionalContext": "⚠️  Desktop notifications not supported on this platform"
  }
}
EOF
        exit 0
        ;;
esac

# 输出成功消息
if [ $? -eq 0 ]; then
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "Notification",
    "additionalContext": "✓ Desktop notification sent: $NOTIFICATION_TITLE"
  }
}
EOF
else
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "Notification",
    "additionalContext": "⚠️  Failed to send desktop notification (check system notification settings)"
  }
}
EOF
fi

exit 0
