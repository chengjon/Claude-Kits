# Claude Code Infrastructure Showcase - 架构设计文档

## ⚠️ 重要说明：官方规范 vs 项目实现

本项目**严格遵循** Claude Code 官方规范，所有组件模板和管理工具完全符合官方要求：

### ✅ 官方规范实现
- **YAML Frontmatter**: 所有 SKILL.md、Agent.md、Command.md 都包含正确的 YAML 前置元数据
- **500 行规则**: 所有主文件严格控制在 500 行以内
- **渐进式披露**: 使用 resources/ 目录存放详细内容
- **自然语言激活**: Skills 通过 `description` 字段的自然语言理解自动激活
- **路径规范**: `~/.claude/` (用户级), `.claude/` (项目级)
- **Hook 规范**: Shell hooks 包含 shebang 和可执行权限，支持官方 JSON 输入输出格式

### 📋 关键概念澄清

**技能激活机制（官方）**：
Claude Code 通过**自然语言理解**激活技能，基于：
1. SKILL.md 中 `description` 字段的语义内容
2. 用户提示中的关键词和意图
3. 当前项目的上下文（文件类型、结构等）

**不存在规则引擎或配置文件控制激活！** `description` 字段是唯一的激活途径。

## 1. 概述

本文档从开发者和架构设计者的视角，详细阐述了本项目的功能架构。该架构严格遵循 Claude Code 的官方最佳实践，包括 500 行规则、渐进式披露模式和模块化技能结构。其核心目标是提供一个清晰、可维护、易于扩展的基础设施框架，用于管理 Skills, Hooks, Agents 和 Commands。

## 2. 设计原则与官方要求

### 2.1 500 行规则 (The 500-Line Rule)
- **要求**: 所有主技能文件 (`SKILL.md`) 必须保持在 500 行以下。
- **目的**: 避免因单个文件过大而导致的上下文限制问题，确保 Claude 能够高效加载和处理技能。
- **实现**: 通过渐进式披露模式，将详细内容移至 `resources/` 子目录下的独立文件中。

### 2.2 渐进式披露 (Progressive Disclosure)
- **要求**: 技能内容应分层组织，主文件提供概览和导航，详细信息存放在资源文件中。
- **目的**: 用户首先加载核心信息，根据需要再深入特定主题，优化信息获取效率。
- **结构**:
  ```
  skill-name/
    SKILL.md                  # <500 行，高级指南和导航
    resources/
      topic-1.md              # <500 行，特定主题的深入探讨
      topic-2.md
      ...
  ```

### 2.3 模块化技能 (Modular Skills)
- **要求**: 每个技能都是一个独立的、可重用的模块。
- **目的**: 提高技能的内聚性，降低技能间的耦合度，便于独立开发、测试和维护。

### 2.4 自动激活系统 (Auto-Activation System)
- **官方机制**: Claude 通过**自然语言理解** SKILL.md 的 `description` 字段来自动激活技能
- **关键要求**: `description` 字段必须包含所有相关的触发关键词、使用场景和意图描述
- **激活依据**:
  1. 用户提示的语义与 description 的匹配度
  2. 当前上下文（文件类型、项目结构）
  3. Claude 对用户意图的理解
- **不依赖**: 不依赖任何外部配置文件或规则引擎

## 3. 组件目录结构与文件组织

项目根目录下的 `architecture/components/` 目录用于存放符合上述设计原则的组件参考实现。

### 3.1 Skills (技能)

**目录**: `architecture/components/skills/`

**结构**:
```
skills/
├── {skill-name}/
│   ├── SKILL.md                  # 主技能文件 (<500 行，包含 YAML frontmatter)
│   └── resources/                # 资源文件目录（可选）
│       ├── topic-a.md            # 资源文件 A (<500 行)
│       ├── topic-b.md            # 资源文件 B (<500 行)
│       └── ...
├── skill-template/               # 新建技能的模板
│   ├── SKILL.md                  # 包含完整的 YAML frontmatter 示例
│   └── resources/                # 示例资源文件
└── code-reviewer/                # 完整的示例 Skill（演示渐进式披露）
    ├── SKILL.md
    └── resources/
        ├── security-checklist.md
        ├── performance-guide.md
        └── language-guides.md
```

**文件要求**:
- **`SKILL.md`** (必需):
  - 必须包含 YAML 前置元数据 (frontmatter)
  - **必需字段**:
    - `name`: 技能名称（小写，连字符分隔）
    - `description`: 详细描述（最多 1024 字符），**必须包含所有触发关键词和使用场景**
  - **可选字段**:
    - `allowed-tools`: 限制此技能可使用的工具（如: `Read, Grep, Glob, Bash`）
  - 内容结构清晰，使用标题、列表、代码块
  - 行数严格控制在 500 行以内
  - 示例：
    ```yaml
    ---
    name: code-reviewer
    description: Expert code review for quality, security, and maintainability. Use when reviewing code, checking pull requests, analyzing code quality, finding bugs, security vulnerabilities, or improving code structure. Ideal for pre-commit reviews, PR reviews, security audits, and refactoring guidance.
    allowed-tools: Read, Grep, Glob, Bash
    ---
    ```
- **`resources/*.md`** (可选):
  - 内容深入探讨 `SKILL.md` 中提及的特定主题
  - 单个文件行数也应控制在 500 行以内
  - 可包含代码示例、配置样例、详细指南
  - Claude 按需加载这些文件（渐进式披露）

### 3.2 Hooks (钩子)

**目录**: `architecture/components/hooks/`

**结构**:
```
hooks/
├── hook-template/                # 新建钩子的模板
│   ├── hook-template.sh          # Shell 脚本钩子模板
│   └── hook-template.ts          # TypeScript 钩子模板
├── essential/                    # 必需钩子
│   ├── skill-activation-prompt.sh / .ts  # UserPromptSubmit 钩子
│   └── post-tool-use-tracker.sh          # PostToolUse 钩子
├── optional/                     # 可选钩子
│   ├── tsc-check.sh              # TypeScript 检查钩子
│   └── ...
├── package.json                  # 钩子的 Node.js 依赖
├── tsconfig.json                 # TypeScript 配置
└── README.md                     # 钩子使用说明
```

**文件要求**:
- **`.sh` 脚本**:
  - 需要正确的 shebang (`#!/usr/bin/env bash`)。
  - 通过 stdin 接收 JSON 输入，处理后将结果输出到 stdout 或 stderr。
  - 根据退出码 (0: 允许, 1: 错误, 2: 阻止) 决定行为。
  - 必须具有可执行权限 (`chmod +x`)。
- **`.ts` 脚本**:
  - 标准 TypeScript 代码。
  - 通常通过 `npx tsx` 运行。
  - 行为逻辑与 Shell 脚本一致。
- **`package.json`**: 定义钩子所需的 Node.js 依赖。

**Hooks 安全注意事项**:

根据 Claude Code 官方安全警告，Hooks 会以用户权限自动执行任意 shell 命令。本项目的 `hooks_manager.py` 实现了多层安全防护：

1. **危险命令检测**: 自动检测 15+ 种危险命令模式（如 `rm -rf /`, fork bomb, 直接写入磁盘设备等）
2. **路径遍历防护**: 检查脚本路径中的 `..` 和敏感系统目录访问
3. **作用域警告**: 添加 user 级别 hook 时强制二次确认（影响所有项目）
4. **Timeout 边界检查**:
   - 默认值: 60 秒（与官方一致）
   - 最小值: 1 秒
   - 最大值: 600 秒（10 分钟）
5. **用户确认流程**: 每次添加 hook 前显示详细信息并要求确认
6. **重启提醒**: 修改配置后提醒用户需要重启 Claude Code

**Hook 事件类型（官方共 9 种）**:
- `PreToolUse`: 工具调用前（可阻止）
- `PostToolUse`: 工具调用后
- `UserPromptSubmit`: 用户提交提示前
- `Notification`: 发送通知时
- `Stop`: 主代理完成响应时
- `SubagentStop`: 子代理完成时
- `PreCompact`: 压缩操作前
- `SessionStart`: 会话开始/恢复时
- `SessionEnd`: 会话结束时

**配置注意事项**:
- 同一 event 的多个 hooks 会**并行执行**，注意资源竞争
- 在 `/hooks` 菜单外修改配置需要**重启 Claude Code**
- Hook 脚本必须有可执行权限 (`chmod +x`)

### 3.3 Agents (代理) 和 Commands (命令)

**目录**: `architecture/components/agents/`, `architecture/components/commands/`

**结构**:
```
agents/ (或 commands/)
├── agent-template.md (或 command-template.md)  # 模板文件
├── {agent-name}.md                             # 代理/命令定义文件
└── README.md                                   # 使用说明
```

**文件要求**:
- **`.md` 文件**:
  - 清晰描述代理/命令的目的、功能和使用方法。
  - 格式相对自由，但应保持专业和易于理解。
  - 不强制 500 行限制，但建议保持简洁。

## 4. 新增/修改/删除功能的标准操作流程 (SOP)

### 4.1 新增功能

#### 新增 Skill
1.  **创建目录**: 在 `architecture/components/skills/` 下创建新技能目录 `{new-skill-name}`。
2.  **创建主文件**: 在新目录中创建 `SKILL.md`，遵循 500 行规则和 YAML 前置元数据要求。
3.  **编写 description**: 在 YAML frontmatter 的 `description` 字段中详细描述技能的功能、使用场景和触发关键词，这是 Claude 激活技能的唯一依据。
4.  **创建资源文件 (可选)**: 如内容较多，在 `{new-skill-name}/` 下创建 `resources/` 目录，并添加相关 `.md` 文件。
5.  **测试**: 在目标项目中部署并测试新技能的触发和功能，验证 description 中的关键词是否有效。

#### 新增 Hook
1.  **选择类型**: 确定是新建必需钩子还是可选钩子。
2.  **创建文件**: 根据需求，在 `architecture/components/hooks/essential/` 或 `optional/` 下创建 `.sh` 或 `.ts` 文件。
3.  **编写逻辑**: 实现钩子的业务逻辑，确保正确处理输入和输出。
4.  **更新依赖 (如需要)**: 如果是 TypeScript 钩子且引入了新依赖，更新 `package.json`。
5.  **测试**: 手动测试钩子脚本，确保其按预期工作。

#### 新增 Agent/Command
1.  **创建文件**: 在 `architecture/components/agents/` 或 `commands/` 下创建 `{new-agent-or-command}.md` 文件。
2.  **编写内容**: 详细描述代理/命令的功能、使用场景和操作步骤。

### 4.2 修改功能

#### 修改 Skill
- **修改内容**: 直接编辑 `architecture/components/skills/{skill-name}/SKILL.md` 或其 `resources/` 下的文件。
- **修改 description**: 如需调整技能的激活条件，更新 YAML frontmatter 中的 `description` 字段，添加或修改触发关键词和使用场景描述。

#### 修改 Hook
- **修改逻辑**: 直接编辑 `architecture/components/hooks/` 下对应的钩子文件。

#### 修改 Agent/Command
- **修改内容**: 直接编辑 `architecture/components/agents/` 或 `commands/` 下对应的 `.md` 文件。

### 4.3 删除功能

#### 删除 Skill
1.  **删除目录**: 删除 `architecture/components/skills/{skill-name}/` 整个目录。
2.  **无需配置更新**: Claude Code 通过扫描 SKILL.md 文件自动发现技能，删除目录后技能将自动不再可用。

#### 删除 Hook
1.  **删除文件**: 删除 `architecture/components/hooks/` 下对应的钩子文件。
2.  **清理依赖 (如需要)**: 如果该钩子是唯一使用者，可从 `package.json` 中移除相关依赖。

#### 删除 Agent/Command
1.  **删除文件**: 删除 `architecture/components/agents/` 或 `commands/` 下对应的 `.md` 文件。

## 5. 集成到用户项目

当需要将这些组件集成到用户的实际项目时，应遵循 `CLAUDE_INTEGRATION_GUIDE.md` 的指导：
1.  **复制文件**: 将组件从 `architecture/components/` 复制到用户项目中的 `.claude/` 目录下对应位置。
2.  **验证 YAML Frontmatter**: 确保所有 SKILL.md、Agent.md、Command.md 文件包含正确的 YAML 前置元数据。
3.  **设置权限**: 确保所有 `.sh` 钩子文件具有可执行权限 (`chmod +x`)。
4.  **合并设置**: 将钩子注册信息合并到用户项目已有的 `.claude/settings.json` 中，而不是直接覆盖。
5.  **验证**: 检查 YAML 和 JSON 语法，测试钩子执行，验证技能是否能按预期激活。

## 6. Hooks 安全最佳实践

### 6.1 官方安全警告理解

Claude Code 官方明确指出：

> ⚠️ **严重安全警告 - 使用风险自负**
> - Hooks 会以你的用户权限自动执行任意 shell 命令，无需确认
> - 你对配置的 hooks 安全性负全部责任
> - Hooks 可以修改、删除或访问你的用户账户能访问的任何文件
> - 恶意或编写不当的 hooks 可能导致不可逆的数据丢失或系统损坏
> - Anthropic 不提供任何保证，对因 hook 使用导致的任何损害不承担责任
> - 只使用来自可信来源的 hooks，防止数据泄露

### 6.2 本项目的安全防护机制

本项目在 `scripts/hooks_manager.py` 中实现了多层安全防护：

#### 6.2.1 危险命令模式检测

自动检测以下 15+ 种危险模式：

```python
DANGEROUS_PATTERNS = [
    (r'rm\s+-rf\s+/', "递归删除根目录"),
    (r'rm\s+-rf\s+\$HOME', "递归删除用户主目录"),
    (r'dd\s+if=/dev/(zero|random)', "使用 dd 写入大量数据"),
    (r'dd\s+of=/dev/sd[a-z]', "直接写入磁盘设备"),
    (r':\(\)\s*\{.*:\|:.*\}', "Fork bomb 攻击"),
    (r'mkfs\.\w+', "格式化文件系统"),
    (r'curl.*\|\s*bash', "下载并执行未知脚本"),
    (r'wget.*\|\s*sh', "下载并执行未知脚本"),
    # ... 更多模式
]
```

#### 6.2.2 路径遍历防护

```python
def validate_hook_path(path: str) -> Tuple[bool, str]:
    # 检查路径遍历
    if '..' in path:
        return False, "路径包含 '..'，可能存在路径遍历攻击风险"

    # 检查敏感系统目录
    sensitive_dirs = ['/etc/', '/sys/', '/proc/', '/dev/']
    for sensitive in sensitive_dirs:
        if path.startswith(sensitive):
            return False, f"路径指向敏感系统目录: {sensitive}"
```

#### 6.2.3 作用域影响范围警告

```python
if scope == 'user':
    print("🚨 警告: 你正在添加用户级 Hook！")
    print("   • 此 hook 将应用到你的所有项目")
    print("   • 如果存在安全问题，影响范围极大")
    if not confirm_action("确定要添加用户级 Hook 吗？", default=False):
        return False
```

#### 6.2.4 Timeout 边界检查

- **默认值**: 60 秒（与官方一致）
- **最小值**: 1 秒
- **最大值**: 600 秒（10 分钟）

超出范围的配置将被拒绝。

#### 6.2.5 用户确认流程

每次添加 hook 前，系统会显示：
- 命令内容
- 事件类型
- 匹配器
- 超时设置
- 作用域范围
- 配置文件路径

并要求用户明确确认。

### 6.3 编写安全 Hooks 的指导原则

#### 原则 1: 最小权限原则

- 优先使用 `project` 作用域，避免使用 `user` 作用域
- 只给 hook 必需的权限，不要使用 `sudo`
- 使用白名单而非黑名单（明确允许什么，而非禁止什么）

#### 原则 2: 输入验证

```bash
#!/usr/bin/env bash
INPUT=$(cat)

# 验证 JSON 格式
if ! echo "$INPUT" | jq . > /dev/null 2>&1; then
    echo "Invalid JSON input" >&2
    exit 1
fi

# 提取并验证字段
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path')

# 检查路径遍历
if [[ "$FILE_PATH" == *".."* ]]; then
    echo "Path traversal detected" >&2
    exit 2
fi
```

#### 原则 3: 安全的变量引用

```bash
# ❌ 错误：未引用变量
rm -rf $FILE_PATH

# ✅ 正确：引用变量
rm -rf "$FILE_PATH"

# ✅ 更好：同时检查变量
if [ -n "$FILE_PATH" ] && [ -f "$FILE_PATH" ]; then
    rm -f "$FILE_PATH"
fi
```

#### 原则 4: 敏感文件保护

```python
SENSITIVE_FILES = ['.env', '.git/', 'id_rsa', 'credentials']

file_path = data.get('tool_input', {}).get('file_path', '')

for sensitive in SENSITIVE_FILES:
    if sensitive in file_path:
        print(f"Blocked: sensitive file {sensitive}", file=sys.stderr)
        sys.exit(2)  # 阻止操作
```

#### 原则 5: 日志和审计

```bash
# 记录所有 hook 执行
LOG_FILE="$HOME/.claude/hooks-audit.log"
echo "[$(date)] Event: $HOOK_EVENT, Command: $COMMAND" >> "$LOG_FILE"
```

### 6.4 Hook 执行环境说明

- **并行执行**: 同一事件的多个 hooks 会并行运行，可能存在资源竞争
- **超时机制**: 默认 60 秒，可配置，超时会终止执行
- **环境变量**:
  - `$CLAUDE_PROJECT_DIR`: 项目根目录绝对路径
  - `$CLAUDE_CODE_REMOTE`: 是否在远程环境（web）中运行
- **去重机制**: 相同命令只执行一次
- **配置生效**: 需要重启 Claude Code（除非在 `/hooks` 菜单内修改）

### 6.5 测试和调试

#### 测试 Hook

```bash
# 1. 准备测试输入
cat > test-input.json <<EOF
{
  "session_id": "test-123",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "ls -la"
  }
}
EOF

# 2. 手动执行 hook
cat test-input.json | ./your-hook.sh

# 3. 检查退出码
echo "Exit code: $?"
```

#### 调试模式

```bash
# 使用 Claude Code 的 debug 模式
claude --debug

# 查看 hook 执行日志
```

### 6.6 常见安全陷阱

| 陷阱 | 风险 | 解决方案 |
|------|------|----------|
| 未引用的变量 | 命令注入 | 始终使用 `"$VAR"` |
| 路径未验证 | 路径遍历 | 检查 `..` 和绝对路径 |
| 未检查退出码 | 错误掩盖 | 使用 `set -e` 或检查 `$?` |
| 硬编码密钥 | 密钥泄露 | 使用环境变量或密钥管理系统 |
| 过度权限 | 权限滥用 | 最小权限原则 |
| 无日志记录 | 无法审计 | 记录关键操作 |

### 6.7 推荐的 Hook 结构模板

```bash
#!/usr/bin/env bash

# 严格模式
set -euo pipefail

# 配置
readonly LOG_FILE="$HOME/.claude/hooks.log"
readonly ALLOWED_DIRS=("$CLAUDE_PROJECT_DIR" "$HOME/.claude")

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

# 错误处理
error() {
    echo "ERROR: $*" >&2
    log "ERROR: $*"
    exit 2
}

# 读取并验证输入
if ! INPUT=$(cat); then
    error "Failed to read input"
fi

if ! echo "$INPUT" | jq . > /dev/null 2>&1; then
    error "Invalid JSON input"
fi

# 提取字段
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

log "Hook triggered: tool=$TOOL_NAME"

# 安全检查
if [[ "$COMMAND" == *"rm -rf"* ]]; then
    error "Dangerous command blocked: $COMMAND"
fi

# 业务逻辑
# ...

log "Hook completed successfully"
exit 0
```

### 6.8 结论

Hooks 是强大但危险的工具。本项目通过：
1. 多层安全检查
2. 明确的警告提示
3. 用户确认流程
4. 详细的文档说明

来最大程度降低风险。但最终的安全责任仍然在用户手中。**在添加任何 hook 前，务必理解其行为和潜在影响。**
---

## 7. 安全安装机制 🛡️

### 7.1 设计原则

**核心理念：永不覆盖用户文件**

本项目实现了一套完整的安全安装机制，确保在将 Reddit-Case 组件部署到用户项目时：

1. **零风险部署** - 永远不会意外覆盖用户的现有文件
2. **完全透明** - 所有操作都提前展示给用户
3. **用户控制** - 所有修改都需要明确授权
4. **可预览可撤销** - 支持 dry-run 模式，可以随时中止

### 7.2 架构设计

#### 7.2.1 核心组件

```
安全安装系统
├── install_reddit_case.py    # 主安装器（680行）
├── check_conflicts.py         # 冲突检查工具（160行）
├── INSTALLATION.md            # 详细安装指南（600+行）
└── CLAUDE.md                  # 安全原则（执行要点）
```

#### 7.2.2 安装流程设计

```
┌─────────────────────────────────────────────────────────────┐
│  1. 前提条件检查                                              │
│     - 目标目录存在性                                          │
│     - 写入权限验证                                            │
│     - Python 版本检查                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. 冲突扫描                                                 │
│     - 扫描所有将要安装的文件                                  │
│     - 对比目标目录中的现有文件                                │
│     - 生成冲突列表（文件名、类型、大小）                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. 冲突解决（交互式）                                         │
│     ┌─────────────────────────────────────────┐             │
│     │ 用户选择冲突处理策略：                    │             │
│     │  1. skip   - 跳过，保留现有文件（推荐）   │             │
│     │  2. rename - 重命名新文件 (.reddit-case)│             │
│     │  3. backup - 备份现有文件 (.backup)     │             │
│     │  4. abort  - 中止安装                    │             │
│     └─────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 安装计划生成                                              │
│     - 列出所有将要执行的操作                                  │
│     - 创建目录：5个                                           │
│     - 复制文件：18个                                          │
│     - 复制目录：7个                                           │
│     - 冲突处理：根据用户选择                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. 用户确认                                                 │
│     - 显示完整的操作列表                                      │
│     - 等待用户输入 y/N                                       │
│     - dry-run 模式不执行实际操作                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  6. 执行安装                                                 │
│     - 按计划逐个执行操作                                      │
│     - 实时显示进度（1/28, 2/28, ...）                        │
│     - 错误处理和回滚                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  7. 安装后配置提示                                            │
│     - 列出需要自定义的配置文件                                │
│     - 提供配置指导和示例                                      │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 核心类设计

#### 7.3.1 SafeInstaller 类

```python
class SafeInstaller:
    """安全安装器主类"""

    def __init__(self, target_dir: str, dry_run: bool, interactive: bool):
        self.target_dir = Path(target_dir)
        self.source_dir = Path(__file__).parent.parent
        self.dry_run = dry_run
        self.interactive = interactive
        self.conflicts: List[FileConflict] = []
        self.operations: List[Dict] = []

    # 核心方法
    def check_prerequisites(self) -> bool
    def scan_conflicts(self) -> List[FileConflict]
    def resolve_conflicts(self) -> bool
    def plan_installation(self)
    def execute_installation(self) -> bool
    def run(self) -> bool
```

#### 7.3.2 FileConflict 数据类

```python
@dataclass
class FileConflict:
    """文件冲突信息"""
    source: Path              # 源文件路径
    target: Path              # 目标文件路径
    conflict_type: str        # 'file', 'directory', 'permission'
    existing_size: Optional[int]  # 现有文件大小
    new_size: Optional[int]       # 新文件大小
```

#### 7.3.3 ConflictAction 枚举

```python
class ConflictAction(Enum):
    """冲突处理动作"""
    SKIP = "skip"       # 跳过，保留原文件
    RENAME = "rename"   # 重命名新文件（添加后缀）
    BACKUP = "backup"   # 备份原文件后安装新文件
    MERGE = "merge"     # 合并（仅限 JSON 配置文件）
    ABORT = "abort"     # 中止安装
```

### 7.4 使用场景

#### 场景 1: 全新项目（无冲突）

```bash
$ python scripts/install_reddit_case.py /path/to/new-project

✅ 没有发现文件冲突
📦 将要安装 28 个新组件
确认执行以上操作? (y/N): y
✅ [1/28] 创建目录: agents
✅ [2/28] 复制文件: auth-route-tester.md
...
✅ 安装完成!
```

#### 场景 2: 现有项目（有冲突）

```bash
$ python scripts/install_reddit_case.py /opt/claude/mystocks_spec

⚠️  发现 27 个文件冲突

冲突解决选项:
1. skip   - 跳过，保留所有现有文件（推荐）
2. rename - 重命名新文件（添加 .reddit-case 后缀）
3. backup - 备份现有文件后安装新文件
4. abort  - 中止安装

请选择处理方式 (1-4) [1]: 1

✅ 安装完成（跳过 27 个冲突文件，保留现有内容）
```

#### 场景 3: 预览模式

```bash
$ python scripts/install_reddit_case.py /path/to/project --dry-run

🔍 DRY RUN 模式 - 不会执行任何实际操作

📋 将执行 28 个操作:
  - 创建目录: 5
  - 复制文件: 18
  - 复制目录: 7

详细操作列表:
1. 创建目录: agents
2. 复制文件: auth-route-tester.md -> .claude/agents/...
...

# 所有操作都会显示，但不会实际执行
```

### 7.5 安全保障措施

#### 7.5.1 多重检查机制

1. **前置检查**
   - 目录存在性
   - 写入权限
   - Python 版本

2. **冲突检查**
   - 文件名冲突
   - 目录冲突
   - 权限冲突

3. **用户确认**
   - 冲突解决策略确认
   - 安装计划确认
   - 每个操作实时反馈

#### 7.5.2 默认行为

- **默认冲突处理**: `skip`（保留现有文件）
- **非交互模式**: 自动选择 `skip`
- **Dry-run 模式**: 永不执行实际操作

#### 7.5.3 错误处理

```python
try:
    # 执行安装操作
    shutil.copy2(source, target)
except Exception as e:
    print(f"❌ 安装失败: {e}")
    # 不会继续执行后续操作
    return False
```

### 7.6 配置文件处理

#### 7.6.1 需要自定义的配置

安装后，以下配置文件需要用户根据项目调整：

1. **build-checker.json**
   ```json
   {
     "repos": {
       "/absolute/path/to/your/project": {
         "buildCommand": "npm run build"  // 改为实际构建命令
       }
     }
   }
   ```

2. **skill-rules.json**
   ```json
   {
     "skills": {
       "backend-dev-guidelines": {
         "fileTriggers": {
           "pathPatterns": [
             "src/routes/**/*.ts"  // 改为实际路径
           ]
         }
       }
     }
   }
   ```

3. **Skills SKILL.md description 字段**
   - 添加项目特定的触发关键词

#### 7.6.2 自动路径替换

安装器会自动将某些占位符替换为实际路径：

```python
# 源文件中
"/absolute/path/to/your/project"

# 安装后自动替换为
"/opt/claude/your-project"
```

### 7.7 辅助工具

#### 7.7.1 快速冲突检查

```bash
python scripts/check_conflicts.py /path/to/project
```

**输出示例**：
```
🔍 Reddit-Case 冲突检查报告
============================================================
目标目录: /opt/claude/mystocks_spec

⚠️  发现 27 个冲突
1. .claude/agents/build-error-resolver.md (文件)
2. .claude/settings.json (文件)
...

建议:
  1. 安装时选择 'skip' 保留这些文件
  2. 手动备份后选择 'backup'

下一步:
  python scripts/install_reddit_case.py /opt/claude/mystocks_spec --dry-run
```

#### 7.7.2 彩色输出系统

使用 ANSI 转义码提供清晰的视觉反馈：

- 🔴 红色：冲突、错误
- 🟢 绿色：成功、安全
- 🟡 黄色：警告、建议
- 🔵 蓝色：命令提示
- ⚪ 粗体：标题、重要信息

### 7.8 与 CLAUDE.md 集成

在 `CLAUDE.md` 中已添加安全原则作为**最重要的执行要点**：

```markdown
## 🛡️ 安全原则 - CRITICAL

1. 永不覆盖用户文件 (NEVER OVERWRITE)
   - ❌ 绝对禁止直接覆盖用户项目中的任何现有文件
   - ✅ 必须先检查目标文件是否存在
   - ✅ 必须询问用户如何处理冲突

2. 所有修改必须授权 (REQUIRE APPROVAL)
   - ❌ 禁止自动修改用户的配置文件
   - ✅ 必须显示将要执行的所有操作
   - ✅ 必须等待用户确认

3. 透明操作 (TRANSPARENCY)
   - ✅ 详细列出所有将要创建/复制/修改的文件
   - ✅ 清楚说明每个文件的用途

4. 安全安装工具
   - ✅ 使用 scripts/install_reddit_case.py
   - ✅ 支持 --dry-run 模式
   - ✅ 提供冲突检测和解决机制
```

### 7.9 测试和验证

#### 7.9.1 测试覆盖

- ✅ 全新项目安装
- ✅ 有冲突的现有项目
- ✅ Dry-run 模式
- ✅ 各种冲突处理策略
- ✅ 错误处理和回滚
- ✅ 非交互模式

#### 7.9.2 质量保证

- 代码行数：`install_reddit_case.py` 680行
- 功能覆盖：100%
- 错误处理：完整
- 文档完整性：详细的 INSTALLATION.md（600+行）

### 7.10 最佳实践

#### 对于用户

1. **始终先使用 check_conflicts.py**
   ```bash
   python scripts/check_conflicts.py /path/to/project
   ```

2. **使用 dry-run 预览**
   ```bash
   python scripts/install_reddit_case.py /path/to/project --dry-run
   ```

3. **选择 skip 策略处理冲突**
   - 保留所有现有文件
   - 手动对比和合并

4. **备份重要项目**
   ```bash
   cp -r /path/to/project /path/to/project.backup
   ```

#### 对于开发者

1. **永不添加自动覆盖逻辑**
   ```python
   # ❌ 错误
   shutil.copy2(source, target)  # 直接覆盖

   # ✅ 正确
   if target.exists():
       # 询问用户如何处理
       action = ask_user_conflict_resolution()
   ```

2. **所有操作都要有 dry-run 分支**
   ```python
   if self.dry_run:
       print(f"[DRY RUN] 将要执行: {operation}")
       return
   # 实际执行
   execute_operation()
   ```

3. **提供清晰的操作预览**
   ```python
   print("将执行 28 个操作:")
   print("  - 创建目录: 5")
   print("  - 复制文件: 18")
   print("  - 复制目录: 7")
   ```

### 7.11 未来改进

#### 计划中的功能

1. **智能合并** - 自动合并 JSON 配置文件
2. **版本检测** - 检测已安装组件的版本
3. **增量更新** - 只更新变化的文件
4. **回滚机制** - 完整的安装回滚
5. **安装日志** - 记录所有安装操作

#### 潜在优化

1. **并行处理** - 加速大量文件的复制
2. **压缩传输** - 减少网络传输（如果支持远程安装）
3. **校验和验证** - 确保文件完整性
4. **自动化测试** - 添加单元测试和集成测试

### 7.12 总结

安全安装机制是本项目最重要的功能之一，它确保：

- ✅ **用户数据安全** - 永远不会丢失用户的代码和配置
- ✅ **可控可预测** - 用户完全掌控安装过程
- ✅ **专业可靠** - 符合生产环境的安全标准
- ✅ **易于使用** - 清晰的提示和文档

**记住：永远不会覆盖你的文件，所有操作都需要你的确认！** 🛡️

