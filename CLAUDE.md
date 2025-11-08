# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🛡️ 安全原则 - CRITICAL

**这是本项目最重要的执行要点：**

### 1. 永不覆盖用户文件 (NEVER OVERWRITE)
- ❌ **绝对禁止**直接覆盖用户项目中的任何现有文件
- ✅ **必须先检查**目标文件是否存在
- ✅ **必须询问**用户如何处理冲突
- ✅ **必须提供选项**: 跳过/重命名/备份/中止

### 2. 所有修改必须授权 (REQUIRE APPROVAL)
- ❌ **禁止**自动修改用户的配置文件
- ✅ **必须显示**将要执行的所有操作
- ✅ **必须等待**用户确认
- ✅ **必须提供** dry-run 预览模式

### 3. 透明操作 (TRANSPARENCY)
- ✅ **详细列出**所有将要创建/复制/修改的文件
- ✅ **清楚说明**每个文件的用途
- ✅ **明确标注**需要用户自定义的配置

### 4. 安全安装工具
- ✅ **使用** `scripts/install_reddit_case.py` 进行安装
- ✅ **支持** `--dry-run` 模式预览
- ✅ **提供** 冲突检测和解决机制

## 仓库概述

Claude-Kits 是一个用于管理 Claude Code 自定义组件的基础设施工具集。它提供基于 Python 的工具（CLI 和 TUI）来管理 Skills（技能）、Subagents（子代理）、Hooks（钩子）、Slash Commands（斜杠命令）、Plugins（插件）和 MCP Servers（MCP 服务器）。该架构严格遵循 Claude Code 的官方最佳实践，包括 500 行规则、渐进式披露模式和模块化技能结构。

## 核心架构

### 组件组织结构

仓库分为三个主要区域：

1. **`components/`** - 所有组件类型的参考模板和结构
   - `skills/` - Agent Skills，带 YAML 前置元数据，遵循 500 行规则
   - `agents/` - Subagent 定义文件
   - `hooks/` - Hook 实现（Shell 和 TypeScript）
   - `commands/` - Slash Command 模板

2. **`scripts/`** - Python 管理工具（全部可执行）
   - `claude_manager.py` - 所有组件类型的统一 CLI 入口
   - `claude_tui.py` - 交互式文本用户界面（需要 `rich` 库）
   - `skills_manager.py` - Agent Skills 管理
   - `subagents_manager.py` - Subagents 管理
   - `hooks_manager.py` - Hooks 配置管理
   - `commands_manager.py` - Slash Commands 管理
   - `plugins_manager.py` - Plugins 管理
   - `mcps_manager.py` - MCP Servers 管理

3. **`docs/`** - 架构文档
   - `ARCHITECTURE_DESIGN.md` - 详细的设计原则和标准操作流程（中文）

### 设计原则

**500 行规则**：所有 `SKILL.md` 文件必须保持在 500 行以内，以避免上下文限制问题。详细内容放在 `resources/` 子目录中。

**渐进式披露**：技能采用层次化组织 - 主文件提供概览和导航，详细信息存放在资源文件中，Claude 按需加载。

**模块化技能**：每个技能都是独立且可重用的，具有高内聚性和低耦合性。

**自动激活系统**：Claude 通过**自然语言理解** SKILL.md 的 `description` 字段来自动激活技能，无需额外配置。

## 常用命令

### 使用统一 CLI 管理器

所有管理操作使用相同的模式：

```bash
# 通用模式
python scripts/claude_manager.py [组件类型] [操作] [名称] [...选项]

# 列出所有项目级别的 Agent Skills
python scripts/claude_manager.py skills list --scope project

# 安装新的个人 Subagent
python scripts/claude_manager.py subagents install my-debugger --scope personal

# 添加新的 Hook
python scripts/claude_manager.py hooks add PreToolUse --matcher "Bash" --command "echo 'Bash executed'" --scope project

# 列出所有 Slash Commands
python scripts/claude_manager.py commands list --scope project
```

### 使用 TUI（交互模式）

```bash
# 启动文本用户界面
python scripts/claude_tui.py

# 导航方式：
# - 方向键（↑/↓）或 W/S 键导航菜单
# - Enter 键选择
# - 'q' 键退出
```

### 使用独立管理脚本

```bash
# Skills 管理
python scripts/skills_manager.py list --scope personal
python scripts/skills_manager.py install my-skill --scope project

# Subagents 管理
python scripts/subagents_manager.py edit my-coder --scope project

# Hooks 管理
python scripts/hooks_manager.py add PostToolUse --matcher "Edit" --command "echo 'File edited'" --scope user
python scripts/hooks_manager.py list --scope project

# Commands 管理
python scripts/commands_manager.py list --scope project

# Plugins 管理
python scripts/plugins_manager.py list

# MCP Servers 管理
python scripts/mcps_manager.py list --scope user
```

## 组件作用域

所有组件都支持基于作用域的组织（三层级架构）：

- **`user` / `personal`**：用户级组件，位于 `~/.claude/`，在所有项目中可用
- **`plugin`**：插件级组件，由已安装的插件提供，在所有项目中可用
- **`project`**：项目级组件，位于 `.claude/`（相对于当前目录），与团队共享

**优先级顺序**：project > plugin > user

**特殊说明**：
- Hooks 的项目级配置包含两个文件：
  - `.claude/settings.json` - 团队共享配置
  - `.claude/settings.local.json` - 本地机密配置（不提交到 git）
- 使用 `--scope project` 时会自动加载这两个文件

## Skill 结构要求

创建或修改技能时：

### SKILL.md 结构
```markdown
---
name: skill-name
description: 详细描述，包含所有触发关键词和短语（最多 1024 字符）
---

# 技能内容（< 500 行）
- 明确的目的说明
- 何时使用此技能
- 关键信息和最佳实践
- 链接到 resources/ 获取详细主题
```

### 目录布局
```
skill-name/
├── SKILL.md                  # 主文件 < 500 行
└── resources/                # 可选的详细内容
    ├── topic-1.md            # 每个 < 500 行
    ├── topic-2.md
    └── ...
```

### 技能激活机制

Claude Code 通过**自然语言理解**激活技能，基于：
- `description` 字段的语义内容和关键词
- 用户提示的意图和上下文
- 当前项目的文件类型和结构

**重要**：确保 `description` 字段包含所有相关的触发关键词和使用场景，这是技能被发现和激活的唯一途径。

**示例**：
```yaml
---
name: code-reviewer
description: Expert code review for quality, security, and maintainability. Use when reviewing code, checking pull requests, analyzing code quality, finding bugs, security vulnerabilities, or improving code structure. Ideal for pre-commit reviews, PR reviews, security audits, and refactoring guidance.
---
```

## Hook 要求

### Shell Hooks (`.sh`)
- 必须包含 shebang：`#!/usr/bin/env bash`
- 通过 stdin 接收 JSON，输出到 stdout/stderr
- 退出码：0（允许）、1（错误）、2（阻止）
- 必须具有可执行权限：`chmod +x hook-file.sh`

### TypeScript Hooks (`.ts`)
- 通过 `npx tsx` 运行
- 与 shell hooks 相同的输入/输出行为
- 依赖项定义在 `components/hooks/package.json`

### Hook 类型
- **必需的钩子**（位于 `components/hooks/essential/`）：
  - 技能激活提示（UserPromptSubmit）
  - 工具使用后跟踪（PostToolUse）

- **可选的钩子**（位于 `components/hooks/optional/`）：
  - TypeScript 检查
  - 自定义验证

## 集成到用户项目

将组件部署到实际项目时：

1. **复制文件**：从 `components/` 复制到用户项目的 `.claude/` 目录
2. **自定义 description**：编辑 SKILL.md 的 description 字段，添加项目特定的触发关键词
3. **设置权限**：为所有 `.sh` 钩子设置可执行权限：`chmod +x .claude/hooks/*.sh`
4. **合并设置**：合并到现有的 `.claude/settings.json`（不要覆盖）
5. **验证**：验证 YAML frontmatter 语法并测试技能激活

## 文件模式

在此代码库中工作时：
- Python 脚本：`scripts/*.py`
- Skill 模板：`components/skills/*/SKILL.md`
- Skill 资源：`components/skills/*/resources/*.md`
- Hook 脚本：`components/hooks/**/*.{sh,ts}`
- 配置文件：`components/hooks/package.json`、`.claude/settings.json`
- 文档：`docs/*.md`、`Claude-code/*.md`

## 重要说明

- 此仓库主要是一个**工具包和参考实现** - 不是可运行的应用程序
- `Claude-code/` 目录包含官方 Claude Code 文档，仅供参考
- 所有管理脚本使用 Python 3.6+ 并需要适当的权限
- TUI 需要 `rich` 库：`pip install rich`
- 修改技能时，始终保持 500 行限制，确保 `description` 字段包含充分的触发关键词
- 所有管理脚本都位于 `scripts/` 目录且具有可执行权限（`chmod +x`）
