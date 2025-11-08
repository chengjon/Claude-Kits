# Claude Code 三层级架构实现

本文档说明 Claude-Kits 项目中 Agents、Hooks 和 Skills 的**标准三层级架构**实现。

## 📊 三层级架构概述

Claude Code 支持三个层级的组件管理，按优先级从高到低：

1. **项目级（Project-level）** - 最高优先级 🥇
2. **插件级（Plugin-level）** - 中等优先级 🥈
3. **用户级（User-level）** - 最低优先级 🥉

**优先级规则**：当同名组件存在于多个层级时，高优先级的组件会覆盖低优先级的组件。

---

## 🗂️ 各组件类型的存储位置

### 1. Agents（Subagents）

| 层级 | 存储路径 | 作用域 | 说明 |
|-----|---------|--------|------|
| **用户级** | `~/.claude/agents/` | 所有项目 | 个人通用的 agents |
| **插件级** | `~/.claude/plugins/*/agents/` | 所有项目（通过插件） | 插件提供的 agents |
| **项目级** | `.claude/agents/` | 当前项目 | 项目特定的 agents，可与团队共享 |

**优先级顺序**：项目级 > 插件级 > 用户级

### 2. Skills

| 层级 | 存储路径 | 作用域 | 说明 |
|-----|---------|--------|------|
| **用户级** | `~/.claude/skills/` | 所有项目 | 个人通用的技能 |
| **插件级** | `~/.claude/plugins/*/skills/` | 所有项目（通过插件） | 插件提供的技能 |
| **项目级** | `.claude/skills/` | 当前项目 | 项目特定的技能，可与团队共享 |

**优先级顺序**：项目级 > 插件级 > 用户级

### 3. Hooks

| 层级 | 配置文件路径 | 作用域 | 说明 |
|-----|------------|--------|------|
| **用户级** | `~/.claude/settings.json` | 所有项目 | 用户全局 hooks 配置 |
| **插件级** | `~/.claude/plugins/*/hooks/hooks.json` | 所有项目（通过插件） | 插件提供的 hooks |
| **项目级** | `.claude/settings.json` <br> `.claude/settings.local.json` | 当前项目 | 项目 hooks 配置<br>（local 文件用于机密配置） |

**优先级顺序**：项目级 > 插件级 > 用户级

**特殊说明**：
- Hooks 的项目级包含两个文件：
  - `settings.json` - 团队共享配置，提交到 Git
  - `settings.local.json` - 本地机密配置，添加到 `.gitignore`
- 使用 `--scope project` 时会自动加载这两个文件
- `settings.local.json` 中的配置会追加到 `settings.json` 之后
- Hooks 通过配置文件管理，而不是目录结构

---

## 🛠️ 管理工具的层级支持

### skills_manager.py

```bash
# 支持的 scope 选项（三层级架构）
python scripts/skills_manager.py list --scope user       # 用户级
python scripts/skills_manager.py list --scope project    # 项目级
python scripts/skills_manager.py list --scope plugin     # 插件级
python scripts/skills_manager.py list --scope all        # 所有层级
```

**安装限制**：
- ✅ 可以安装到 `user` 和 `project` 层级
- ❌ 不能直接安装到 `plugin` 层级（由插件管理）

### subagents_manager.py

```bash
# 支持的 scope 选项（三层级架构）
python scripts/subagents_manager.py list --scope user       # 用户级
python scripts/subagents_manager.py list --scope project    # 项目级
python scripts/subagents_manager.py list --scope plugin     # 插件级
python scripts/subagents_manager.py list --scope all        # 所有层级
```

**安装限制**：
- ✅ 可以安装到 `user` 和 `project` 层级
- ❌ 不能直接安装到 `plugin` 层级（由插件管理）

### hooks_manager.py

```bash
# 支持的 scope 选项（三层级架构）
python scripts/hooks_manager.py list --scope user       # 用户级
python scripts/hooks_manager.py list --scope project    # 项目级（自动包含 settings.json + settings.local.json）
python scripts/hooks_manager.py list --scope plugin     # 插件级
python scripts/hooks_manager.py list --scope all        # 所有层级
```

**配置说明**：
- ✅ 可以添加到 `user` 和 `project` 层级
- ❌ 不能直接添加到 `plugin` 层级（由插件提供）
- 💡 `project` 层级会自动加载 `settings.json` 和 `settings.local.json`

---

## 🖥️ TUI 界面的层级支持

### claude_tui.py 的三层级实现

```python
def get_common_params(component_type="general"):
    # 所有组件类型使用相同的三层级选项
    scope_choices = ["user", "project", "plugin", "all"]

    scope = Prompt.ask("Select scope",
                      choices=scope_choices,
                      default="project")
```

**功能特性**：
- ✅ 统一的三层级架构（user, project, plugin）
- ✅ 根据组件类型（skills, agents, hooks, commands）显示不同的帮助信息
- ✅ 自动显示每个选项对应的路径

### 示例输出

当选择 Skills 时：
```
Scope options:
  user: ~/.claude/skills/ | project: .claude/skills/ | plugin: from plugins | all: all scopes

Select scope [project]:
```

当选择 Hooks 时：
```
Scope options:
  user: ~/.claude/settings.json | project: .claude/settings.json + settings.local.json | plugin: from plugins | all: all scopes

Select scope [project]:
```

**注意**：Hooks 的提示明确显示项目级包含两个文件。

---

## 🔧 项目级的特殊实现：settings.local.json

### 问题场景

在团队项目中，`.claude/settings.json` 应该：
- ✅ 提交到 Git
- ✅ 与团队共享
- ✅ 包含通用的 hooks 配置

但某些配置**不应该共享**：
- ❌ API 密钥
- ❌ 数据库凭证
- ❌ 个人调试 hooks
- ❌ 本地路径配置

### 解决方案

项目级 Hooks 支持两个配置文件：

```json
// .claude/settings.json (提交到 Git)
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": ".claude/hooks/team-guard.sh"
      }
    ]
  }
}

// .claude/settings.local.json (添加到 .gitignore)
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "echo 'My secret token: $MY_SECRET_TOKEN'"
      }
    ]
  }
}
```

### 自动加载机制

当使用 `--scope project` 时，系统会：

1. 加载 `.claude/settings.json`
2. 加载 `.claude/settings.local.json`（如果存在）
3. Local 配置会追加到同一事件的 hooks 列表中
4. 所有 hooks 按加载顺序执行

**示例**：

```bash
# 查看项目级所有 hooks（包含 local）
python scripts/hooks_manager.py list --scope project

# 输出：
# Event: PreToolUse
#   [0] Command: .claude/hooks/team-guard.sh (Scope: project, File: .claude/settings.json)
# Event: SessionStart
#   [0] Command: echo 'My secret token: $MY_SECRET_TOKEN' (Scope: project:local, File: .claude/settings.local.json)
```

### .gitignore 配置

```gitignore
# 项目级机密配置
.claude/settings.local.json
```

---

## 🔄 插件级组件的加载机制

### Skills 和 Agents

插件级组件存储在 `~/.claude/plugins/<plugin-name>/skills/` 或 `~/.claude/plugins/<plugin-name>/agents/` 目录下。

**扫描逻辑**：
```python
plugins_dir = Path.home() / '.claude' / 'plugins'
if plugins_dir.exists():
    for plugin_dir in plugins_dir.iterdir():
        if plugin_dir.is_dir():
            plugin_skills_dir = plugin_dir / 'skills'
            if plugin_skills_dir.exists():
                # 加载插件技能
                # scope 标记为 'plugin:<plugin-name>'
```

### Hooks

插件级 hooks 存储在 `~/.claude/plugins/<plugin-name>/hooks/hooks.json` 文件中。

**扫描逻辑**：
```python
plugins_dir = Path.home() / '.claude' / 'plugins'
if plugins_dir.exists():
    for plugin_dir in plugins_dir.iterdir():
        if plugin_dir.is_dir():
            plugin_hooks_file = plugin_dir / 'hooks' / 'hooks.json'
            if plugin_hooks_file.exists():
                # 加载插件 hooks
                # scope 标记为 'plugin:<plugin-name>'
```

---

## 📝 使用示例

### 示例 1: 查看所有层级的 Skills

```bash
python scripts/skills_manager.py list --scope all

# 输出示例：
# Found 5 skill(s):
#   - backend-dev-guidelines: Backend development patterns (user)
#   - code-reviewer: Code review assistant (plugin:reddit-case)
#   - frontend-dev-guidelines: Frontend development patterns (project)
```

### 示例 2: 在项目级安装 Agent

```bash
python scripts/subagents_manager.py install my-debugger --scope project
```

### 示例 3: 在用户级添加 Hook

```bash
python scripts/hooks_manager.py add \
  --event PreToolUse \
  --matcher "Edit|Write" \
  --command "echo 'File operation detected'" \
  --scope user
```

### 示例 4: 查看项目级 Hooks（包含 local）

```bash
python scripts/hooks_manager.py list --scope project

# 输出会包含：
# - .claude/settings.json 中的 hooks (Scope: project)
# - .claude/settings.local.json 中的 hooks (Scope: project:local)
```

### 示例 5: 使用 TUI 管理组件

```bash
python scripts/claude_tui.py

# 在 TUI 中：
# 1. 选择 "Agent Skills"
# 2. 选择 "Install"
# 3. 输入技能名称
# 4. 选择 scope：user / project / plugin / all
```

---

## ⚠️ 重要注意事项

### 1. 标准三层级架构

本项目完全遵循 Claude Code 官方的三层级架构：
- ✅ User-level（用户级）
- ✅ Plugin-level（插件级）
- ✅ Project-level（项目级）

**没有第四层级**！`settings.local.json` 是项目级的**实现细节**，不是独立层级。

### 2. 插件级组件不可直接安装

插件级的 Skills、Agents 和 Hooks 由插件系统管理，不能通过管理器直接安装：

```bash
# ❌ 会报错
python scripts/skills_manager.py install my-skill --scope plugin

# 错误信息：
# Error: Cannot directly install skills at plugin scope. Use plugin manager instead.
```

### 3. 术语统一

所有管理器和 TUI 统一使用 `user` 而不是 `personal`：

- ✅ 推荐：`--scope user`
- ⚠️ 兼容：`--scope personal` （仅 skills_manager.py 和 subagents_manager.py 为向后兼容保留）

### 4. 项目级的双文件支持（仅 Hooks）

Hooks 的项目级支持两个配置文件：

| 文件 | 用途 | Git 提交 | 优先级 |
|------|------|---------|--------|
| `settings.json` | 团队共享配置 | ✅ 提交 | 先加载 |
| `settings.local.json` | 本地机密配置 | ❌ 不提交 | 后加载（追加） |

**关键点**：
- 两个文件都属于**项目级**（不是独立层级）
- `settings.local.json` 的配置会**追加**，不会覆盖
- 同一事件的 hooks 会按加载顺序执行
- 使用 `--scope project` 会自动加载两个文件

### 5. 优先级的实际应用

**场景**：如果用户级、插件级和项目级都有名为 `code-reviewer` 的 Skill：

1. Claude Code 会优先使用**项目级**的 `code-reviewer`
2. 如果项目级不存在，使用**插件级**的
3. 如果插件级也不存在，使用**用户级**的

这种设计允许：
- **用户级**：设置通用的默认值
- **插件级**：通过插件分享社区最佳实践
- **项目级**：为特定项目定制，覆盖默认值

---

## 🔍 验证三层级架构实现

可以通过以下命令验证优先级实现是否正确：

```bash
# 检查 Skills 的优先级顺序注释
grep "优先级顺序" scripts/skills_manager.py
# 应输出：优先级顺序：项目级 > 插件级 > 用户级

# 检查 Agents 的优先级顺序注释
grep "优先级顺序" scripts/subagents_manager.py
# 应输出：优先级顺序：项目级 > 插件级 > 用户级

# 检查 Hooks 的优先级顺序注释
grep "优先级顺序" scripts/hooks_manager.py
# 应输出：优先级顺序：项目级 > 插件级 > 用户级
```

**所有组件类型都应该输出相同的优先级顺序**。

---

## 📊 架构对比图

### 标准三层级架构

```
┌─────────────────────────────────────────────┐
│         Claude Code 三层级架构              │
├─────────────────────────────────────────────┤
│                                             │
│  🥇 Project-level (最高优先级)              │
│     ├─ Agents: .claude/agents/              │
│     ├─ Skills: .claude/skills/              │
│     └─ Hooks: .claude/settings.json         │
│              .claude/settings.local.json    │
│                                             │
│  🥈 Plugin-level (中等优先级)               │
│     ├─ Agents: ~/.claude/plugins/*/agents/  │
│     ├─ Skills: ~/.claude/plugins/*/skills/  │
│     └─ Hooks: ~/.claude/plugins/*/hooks/    │
│                                             │
│  🥉 User-level (最低优先级)                 │
│     ├─ Agents: ~/.claude/agents/            │
│     ├─ Skills: ~/.claude/skills/            │
│     └─ Hooks: ~/.claude/settings.json       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📚 相关文档

- [Claude Code 官方文档](https://docs.claude.com/en/docs/claude-code)
- [CLAUDE.md](../CLAUDE.md) - 项目总体说明
- [ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md) - 架构设计文档
- [INSTALLATION.md](../INSTALLATION.md) - 安装指南

---

## 🎯 总结

本项目的三层级架构实现：

✅ **完整性**：所有组件类型（Agents、Skills、Hooks）都支持三层级

✅ **一致性**：所有管理器使用统一的术语和优先级顺序

✅ **可用性**：TUI 提供友好的选择菜单，自动显示路径说明

✅ **可扩展性**：插件系统可无缝集成，不影响现有组件

✅ **实用性**：项目级 Hooks 支持 `settings.local.json` 用于机密配置

**优先级顺序完全符合 Claude Code 官方规范**：**项目级 > 插件级 > 用户级** ✨

**`settings.local.json` 是项目级的实现细节**，不是第四层级，确保架构简洁清晰。
