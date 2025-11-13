# .claude/ 目录说明

⚠️ **重要提示**: 本目录仅作为**使用示例**，不是模板库。

## 目录用途

此目录展示了 Claude Code 项目配置的完整示例，包括：

- `agents/` - Subagent 配置示例
- `commands/` - Slash Command 示例
- `hooks/` - Hook 脚本示例
- `dev/` - Dev Docs 工作流示例
- `settings.json` - Hooks 配置示例
- `skill-rules.json` - Skills 激活规则示例
- `build-checker.json` - 构建检查配置示例

## ~~不要直接复制此目录~~

**正确做法**：使用管理工具安装组件

### 安装单个组件

```bash
# 使用 skills_manager.py 安装 Skill
python scripts/skills_manager.py install task-planning-pro --scope project --path /path/to/your/project

# 使用 TUI 交互式安装
python scripts/claude_tui.py
# 然后选择: Skills Manager → View Details → 选择 Skill → Install
```

### 安装 Role 集合

```bash
# 安装 Reddit Case 的所有组件
python scripts/roles_manager.py install reddit-case --path /path/to/your/project

# 只安装特定类型的组件
python scripts/roles_manager.py install reddit-case --path /path/to/your/project --components skills,agents
```

## 组件模板库位置

所有可用的组件模板位于：

- **Skills**: `components/skills/` (72 个模板)
- **Agents**: `components/agents/`
- **Hooks**: `components/hooks/`
- **Commands**: `components/commands/`

## Role 配置文件

预定义的 Role 集合位于：

- `checklists/roles/reddit-case.yaml` - Reddit 工程师 30万行代码实践
- `checklists/roles/backend-developer.yaml` - 后端开发工具集
- `checklists/roles/frontend-developer.yaml` - 前端开发工具集
- `checklists/roles/devops-engineer.yaml` - DevOps 工具集
- ... 更多

## 相关文档

- `CLAUDE.md` - 项目指导和安全原则
- `docs/UNIVERSAL_INSTALLER_DESIGN.md` - 安装系统设计文档
- `INSTALLATION.md` - 详细安装指南

---

**版本**: 1.0.0
**更新日期**: 2025-11-10
