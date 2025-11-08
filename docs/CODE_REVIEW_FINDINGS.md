# Code Review Findings - hooks_manager.py

## 审查时间
2025-11-07

## 审查范围
基于 Reddit 30万行代码案例研究和 Claude Code 官方 hooks 文档（9个Event要点.md）

## 总体评分
**6.5/10** - 功能完整但缺少现代模式支持

---

## ✅ 优点

### 1. 完整的安全框架
- ✅ 15+ 危险命令模式检测
- ✅ 路径遍历保护
- ✅ Timeout 边界检查 (1-600秒)
- ✅ 作用域警告机制
- ✅ 多步确认流程

### 2. 良好的代码组织
- ✅ 清晰的函数分离
- ✅ 类型提示（Tuple, List）
- ✅ 详细的文档字符串
- ✅ 退出码语义正确

### 3. 用户友好
- ✅ 彩色输出和格式化
- ✅ 详细的错误提示
- ✅ 重启提醒
- ✅ 支持三种作用域（user/project/local）

---

## ⚠️ 严重问题（必须修复）

### 问题 1: 缺少 JSON 输出控制支持 🔴

**影响**：无法实现 Reddit 案例的核心模式

**当前状态**：
```python
# 只支持简单命令字符串
def add_hook(event, matcher, hook_command, ...):
    hook_config = {
        "matcher": matcher,
        "hooks": [{"type": "command", "command": hook_command}]
    }
```

**缺失功能**：
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "原因",
    "additionalContext": "注入到 Claude 的上下文"
  }
}
```

**需要的功能**：
1. `generate_json_template(event, template_type)` - 生成 JSON 模板
2. `add_hook()` 支持 `--json-output` 参数
3. 为每个事件提供预定义模板（skill-activation, permission-control, context-injection 等）

**实现建议**：
```python
HOOK_JSON_TEMPLATES = {
    "PreToolUse": {
        "auto-approve": {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": "Auto-approved based on whitelist"
            }
        },
        "deny": {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Security policy violation"
            }
        }
    },
    "UserPromptSubmit": {
        "skill-activation": {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "SKILL ACTIVATION: <skill-name>"
            }
        }
    },
    # ... 其他事件
}
```

---

### 问题 2: 缺少 skill-rules.json 集成 🔴

**影响**：用户无法实现 Skills 自动激活系统（Reddit 案例的核心创新）

**当前状态**：完全没有任何相关代码或文档

**Reddit 案例的核心发现**：
> Claude 不会自动加载/采用所有 Skill 文档！必须通过 UserPromptSubmit Hook + skill-rules.json 强制激活。

**需要的功能**：
1. `generate_skill_rules()` - 生成 skill-rules.json 模板
2. `add_skill_rule(skill_name, triggers)` - 添加技能激活规则
3. `validate_skill_rules()` - 验证 skill-rules.json 语法
4. 集成到 UserPromptSubmit hook 脚本模板

**skill-rules.json 结构**：
```json
{
  "version": "1.0.0",
  "rules": [
    {
      "skill": "backend-dev-guidelines",
      "priority": 1,
      "triggers": {
        "keywords": ["route", "controller", "service", "repository", "API"],
        "filePatterns": ["src/routes/**", "src/controllers/**"],
        "intentRegex": ".*(添加|创建|实现).*API.*",
        "contentTriggers": ["import.*express", "router\\s*="]
      },
      "resources": {
        "main": ".claude/skills/backend-dev-guidelines/SKILL.md",
        "detailed": [
          ".claude/skills/backend-dev-guidelines/resources/routing.md",
          ".claude/skills/backend-dev-guidelines/resources/error-handling.md"
        ]
      }
    }
  ]
}
```

**实现建议**：
1. 在 `hooks_manager.py` 添加 `manage_skill_rules` 子命令
2. 创建 `.claude/hooks/user-prompt-submit-skill-activation.sh` 模板
3. 模板应该：
   - 从 stdin 读取 `prompt` 字段
   - 读取 `.claude/skill-rules.json`
   - 匹配规则（关键词/文件/正则/内容）
   - 输出 JSON additionalContext 注入技能

---

## ⚠️ 中等问题（强烈推荐修复）

### 问题 3: 缺少所有 9 个事件的脚本模板 🟡

**影响**：用户需要从零开始编写脚本，学习曲线陡峭

**当前状态**：`components/hooks/` 目录下没有任何可用的模板

**需要的模板**：

#### PreToolUse (3个模板)
1. `sensitive-file-guard.sh` - 阻止修改 .env, .ssh, credentials
2. `pm2-permission-gatekeeper.sh` - PM2 命令权限控制（auto-approve logs/monit，ask restart/stop，deny delete）
3. `bash-whitelist.sh` - Bash 命令白名单

#### PostToolUse (3个模板)
1. `file-edit-tracker.sh` - 记录编辑文件到日志（配合 Stop build-checker）
2. `auto-prettier.sh` - 自动格式化（谨慎使用，token 成本高）
3. `static-check.sh` - ESLint/Flake8 等静态检查

#### UserPromptSubmit (2个模板)
1. `skill-activation.sh` - 基于 skill-rules.json 的技能激活（核心！）
2. `sensitive-keyword-filter.sh` - 检测并阻止含 secret/password 的提示

#### Stop (2个模板)
1. `build-checker.sh` - 读取编辑日志，运行构建，错误 ≥5 则阻断（核心！）
2. `dev-docs-updater.sh` - 更新 Dev Docs 的 tasks.md

#### SessionStart (2个模板)
1. `dev-docs-injector.sh` - 注入 context.md 摘要恢复上下文（核心！）
2. `environment-setup.sh` - 写入 CLAUDE_ENV_FILE 设置 PATH/NODE_ENV

#### SessionEnd (1个模板)
1. `batch-prettier.sh` - 批量运行 Prettier（Reddit 建议在会话结束时运行）

#### PreCompact (1个模板)
1. `dev-docs-snapshot.sh` - 压缩前保存 Dev Docs 快照

#### Notification (1个模板)
1. `desktop-notify.sh` - 桌面通知（notify-send）

#### SubagentStop (1个模板)
1. `subagent-result-validator.sh` - 验证子代理输出

**每个模板应包含**：
- Shebang 和安全的输入解析
- 详细的注释说明用途和工作原理
- 错误处理和日志记录
- 符合官方规范的退出码和 JSON 输出
- 使用说明和配置示例

---

### 问题 4: 缺少 Matcher 验证 🟡

**影响**：配置错误直到运行时才被发现

**当前状态**：
```python
def add_hook(event, matcher, hook_command, ...):
    # 直接接受任意 matcher，不验证
    hook_config = {"matcher": matcher, ...}
```

**潜在错误**：
```bash
# 错误 1: 末尾多余的 |
--matcher "Edit|Write|"

# 错误 2: 工具名称大小写错误（应该是 Edit 不是 edit）
--matcher "edit|write"

# 错误 3: 在不支持 matcher 的事件中使用
python hooks_manager.py add Stop --matcher "Edit" ...  # Stop 不支持 matcher

# 错误 4: 无效的正则表达式
--matcher "[unclosed"
```

**需要的功能**：
```python
def validate_matcher(event: str, matcher: str) -> Tuple[bool, str]:
    """
    验证 matcher 是否有效

    检查项：
    1. 事件是否支持 matcher（只有 PreToolUse/PostToolUse 支持）
    2. 正则表达式语法是否正确
    3. 工具名称是否正确（区分大小写）

    返回:
        (is_valid, error_message)
    """
    # 只有这两个事件支持 matcher
    MATCHER_SUPPORTED_EVENTS = ["PreToolUse", "PostToolUse"]

    if matcher and event not in MATCHER_SUPPORTED_EVENTS:
        return False, f"Event '{event}' does not support matcher"

    if not matcher:
        return True, ""

    # 验证正则语法
    try:
        re.compile(matcher)
    except re.error as e:
        return False, f"Invalid regex pattern: {e}"

    # 验证工具名称（常见工具列表）
    KNOWN_TOOLS = ["Read", "Write", "Edit", "Bash", "Glob", "Grep",
                   "Task", "WebFetch", "WebSearch", "NotebookEdit"]

    # 提取工具名称（分割 | 和去除通配符）
    tool_names = re.findall(r'\w+', matcher)
    for tool in tool_names:
        if tool in KNOWN_TOOLS:
            continue
        if tool.lower() in [t.lower() for t in KNOWN_TOOLS]:
            suggestion = next(t for t in KNOWN_TOOLS if t.lower() == tool.lower())
            return False, f"Tool name is case-sensitive. Did you mean '{suggestion}' instead of '{tool}'?"

    return True, ""
```

**实现位置**：
1. 在 `add_hook()` 中调用 `validate_matcher()`
2. 在 `edit_hook()` 中也调用
3. 在 `validate_hooks_config()` 中批量验证

---

### 问题 5: 缺少事件特定字段支持 🟡

**影响**：无法根据事件上下文做精细控制

**当前状态**：hooks 配置只支持 `matcher` 和 `timeout`，不支持事件特定字段

**缺失字段**：

#### PreCompact 的 trigger 过滤
```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "manual",  // ❌ 错误：应该用事件特定字段
        "hooks": [{"type": "command", "command": "..."}]
      }
    ]
  }
}
```

**正确方式**（9个Event要点.md 没有明确说明，需要推断）：
```bash
# Hook 脚本中从 stdin 读取 trigger 字段
import json, sys
data = json.load(sys.stdin)
trigger = data.get('trigger')  # 'manual' 或 'auto'

if trigger == 'manual':
    # 只在手动 /compact 时执行
    print(json.dumps({
        "hookSpecificOutput": {
            "additionalContext": "Manual compact detected, saving snapshot..."
        }
    }))
```

**但是**，9个Event要点.md 的 matcher 字段定义说：
> PreCompact: 没有工具 matcher；但 trigger 有 manual 或 auto 值可区分场景。

这意味着 **matcher 不适用于 PreCompact**，但脚本可以通过 stdin 读取 trigger 字段来区分。

**结论**：
- settings.json 中不需要新字段
- 但需要在文档中说明如何在脚本中使用这些事件特定字段
- 模板脚本应该展示如何读取和使用这些字段

**需要的改进**：
1. 在 `add_hook()` 中添加 `--help` 输出，说明事件特定字段
2. 在每个事件的模板脚本中添加注释，展示如何读取特定字段
3. 创建文档 `docs/HOOKS_EVENT_SPECIFIC_FIELDS.md`

**示例模板注释**：
```bash
#!/usr/bin/env bash
# PreCompact Hook Template
#
# Event-specific fields available in stdin:
#   - trigger: "manual" | "auto"
#   - custom_instructions: string (only present for manual trigger)
#
# Example: Only run for manual compacts
#   trigger=$(echo "$INPUT_JSON" | jq -r '.trigger')
#   if [ "$trigger" != "manual" ]; then
#     exit 0  # Skip for auto compacts
#   fi

INPUT_JSON=$(cat)
# ... 处理逻辑
```

---

## ⚠️ 低优先级问题（可选改进）

### 问题 6: 缺少构建检查管道生成器 🟢

**影响**：降低 Reddit 最佳实践的采用率

**当前状态**：用户需要手动创建和配置两个 hooks

**理想状态**：一键生成完整管道

**需要的功能**：
```bash
# 一键生成构建检查管道
python hooks_manager.py generate-pipeline build-check \
  --build-command "pnpm build" \
  --error-threshold 5 \
  --scope project

# 生成的内容：
# 1. .claude/hooks/file-edit-tracker.sh (PostToolUse)
# 2. .claude/hooks/build-checker.sh (Stop)
# 3. 添加两个 hooks 到 settings.json
# 4. 创建 ~/.claude/edit_log.jsonl
```

**其他可能的管道**：
- `dev-docs-pipeline` - SessionStart injector + PreCompact snapshot + Stop updater
- `pm2-pipeline` - PreToolUse gatekeeper + Notification alert
- `skill-activation-pipeline` - UserPromptSubmit activator + skill-rules.json

---

## 📊 改进优先级总结

### 🔴 P0 - 必须修复（阻塞核心功能）
1. **JSON 输出控制支持** - 无法实现现代 hooks 模式
2. **skill-rules.json 集成** - 无法实现 Skills 自动激活

### 🟡 P1 - 强烈推荐（显著提升用户体验）
3. **9 个事件的脚本模板** - 降低学习曲线
4. **Matcher 验证** - 提前发现配置错误
5. **事件特定字段文档** - 帮助用户正确使用高级功能

### 🟢 P2 - 可选改进（锦上添花）
6. **构建检查管道生成器** - 提高最佳实践采用率

---

## 🎯 建议的改进步骤

### 第1步：添加 JSON 模板支持（1-2小时）
1. 定义 `HOOK_JSON_TEMPLATES` 字典
2. 添加 `generate_json_template()` 函数
3. 修改 `add_hook()` 支持 `--json-template` 参数
4. 添加交互式选择（"Do you want to use a JSON template?"）

### 第2步：创建 skill-rules.json 管理器（2-3小时）
1. 添加 `manage-skill-rules` 子命令
2. 实现 `generate_skill_rules()` - 生成模板
3. 实现 `add_skill_rule()` - 添加规则
4. 实现 `validate_skill_rules()` - 验证语法
5. 创建 UserPromptSubmit hook 模板使用 skill-rules.json

### 第3步：创建所有事件的脚本模板（4-6小时）
1. 在 `components/hooks/essential/` 创建核心模板（4个）
2. 在 `components/hooks/optional/` 创建可选模板（12个）
3. 每个模板包含详细注释和使用说明
4. 确保所有模板可执行且经过测试

### 第4步：添加 Matcher 验证（1小时）
1. 实现 `validate_matcher()` 函数
2. 集成到 `add_hook()` 和 `edit_hook()`
3. 添加工具名称大小写提示

### 第5步：创建事件特定字段文档（1小时）
1. 创建 `docs/HOOKS_EVENT_SPECIFIC_FIELDS.md`
2. 为每个事件列出可用字段
3. 在模板脚本中添加注释示例

### 第6步：（可选）构建管道生成器（2-3小时）
1. 添加 `generate-pipeline` 子命令
2. 实现常用管道的一键生成

**总计时间估算**：11-16 小时（不含第6步），或 13-19 小时（全部）

---

## 📝 代码质量建议

### 1. 添加单元测试
当前没有任何测试。建议添加：
```python
# tests/test_hooks_manager.py
def test_validate_matcher():
    assert validate_matcher("PreToolUse", "Edit|Write")[0] == True
    assert validate_matcher("Stop", "Edit")[0] == False  # Stop 不支持 matcher
    assert validate_matcher("PreToolUse", "edit")[0] == False  # 大小写错误
```

### 2. 使用 dataclasses 或 TypedDict
```python
from dataclasses import dataclass
from typing import Literal, Optional

@dataclass
class HookConfig:
    event: Literal["PreToolUse", "PostToolUse", ...]
    matcher: Optional[str]
    command: str
    timeout: int = DEFAULT_HOOK_TIMEOUT
    scope: Literal["user", "project", "local"] = "project"
```

### 3. 添加 --dry-run 模式
```bash
python hooks_manager.py add PreToolUse --matcher "Edit" --command "..." --dry-run
# 输出：Would add the following hook:
# {配置预览}
# No changes made (dry-run mode)
```

---

## 🎉 结论

hooks_manager.py 的安全框架和基本功能都很完善（6.5/10），但缺少对现代 hooks 模式的支持。

**优先修复 P0 问题**（JSON 输出控制 + skill-rules.json）将使评分提升到 **8.5/10**。

**完成所有 P1 改进**后，评分可达到 **9.5/10**，成为生产级别的工具。

---

## 参考文档
- `/opt/claude/Claude-Kits/reference/hooks/30-逐项整理.md` - Reddit 30万行代码案例
- `/opt/claude/Claude-Kits/reference/hooks/9个Event要点.md` - 9个事件详细规范
- `/opt/claude/Claude-Kits/reference/hooks/claude_hooks_quickref.md` - 快速参考
- `Claude-code/hooks.md` - 官方 hooks 文档
- `Claude-code/hooks-guide.md` - 官方最佳实践指南
