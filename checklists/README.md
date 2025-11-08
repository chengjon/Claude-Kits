# Role-Based Component Checklists

> **最后更新**: 2025-11-07 | **角色清单**: 6 个

本目录包含基于不同开发者角色的组件推荐清单，帮助用户快速选择和安装适合其工作需求的组件套件。

---

## 📋 目录结构

```
checklists/
├── roles/              # 预定义的角色清单
│   ├── backend-developer.yaml
│   ├── frontend-developer.yaml
│   ├── fullstack-developer.yaml
│   ├── devops-engineer.yaml
│   ├── security-engineer.yaml
│   └── test-engineer.yaml
├── custom/             # 用户自定义清单
└── template.yaml       # 创建自定义清单的模板
```

---

## 🎯 预定义角色清单

### Backend Developer
**适用于**: 后端开发、API 设计、数据库管理

**包含组件**:
- Agents: backend-architect, database-optimizer, api-designer, test-writer, debugger
- Skills: sql-optimization-patterns, error-handling-patterns, debugging-strategies, code-review-excellence
- Commands: review, test-generate, smart-debug, refactor-clean

### Frontend Developer
**适用于**: 前端开发、UI/UX、客户端应用

**包含组件**:
- Agents: frontend-developer, api-designer, test-writer, performance-engineer
- Skills: typescript-advanced-types, e2e-testing-patterns, error-handling-patterns, code-review-excellence, debugging-strategies
- Commands: review, test-generate, docs, refactor-clean

### Full-Stack Developer
**适用于**: 全栈开发、端到端解决方案

**包含组件**:
- Agents: backend-architect, frontend-developer, api-designer, database-optimizer, test-writer, architect-review
- Skills: typescript-advanced-types, e2e-testing-patterns, sql-optimization-patterns, error-handling-patterns, code-review-excellence, git-advanced-workflows, debugging-strategies
- Commands: review, test-generate, docs, smart-debug, refactor-clean

### DevOps Engineer
**适用于**: 运维、CI/CD、基础设施管理

**包含组件**:
- Agents: devops-troubleshooter, architect-review, database-optimizer, performance-engineer, security-auditor
- Skills: debugging-strategies, error-handling-patterns, git-advanced-workflows
- Commands: smart-debug, security-sast, review, docs

### Security Engineer
**适用于**: 安全审计、漏洞扫描、合规检查

**包含组件**:
- Agents: security-auditor, architect-review, debugger
- Skills: error-handling-patterns, code-review-excellence, debugging-strategies
- Commands: security-sast, review, smart-debug, tech-debt

### Test Engineer
**适用于**: 测试自动化、质量保证、测试架构

**包含组件**:
- Agents: test-writer, test-automator, debugger
- Skills: e2e-testing-patterns, python-testing-patterns, debugging-strategies, code-review-excellence, error-handling-patterns
- Commands: test-generate, smart-debug, review, refactor-clean

---

## 🚀 使用方法

### 方法 1: 使用 TUI（推荐）

```bash
# 启动 Claude-Kits TUI
python scripts/claude_tui.py

# 在主菜单中选择 "Role Checklists"
# 然后选择所需操作:
# - View Roles: 查看所有可用角色
# - View Checklist: 查看特定清单详情
# - Install from Checklist: 一键安装清单中的所有组件
# - Create Custom: 创建自定义清单
# - Edit Custom: 编辑自定义清单
# - Delete Custom: 删除自定义清单
```

### 方法 2: 手动查看和使用

```bash
# 查看某个角色清单
cat checklists/roles/backend-developer.yaml

# 手动安装清单中的组件
python scripts/subagents_manager.py install backend-architect --scope project
python scripts/skills_manager.py install sql-optimization-patterns --scope project
python scripts/commands_manager.py install review --scope project
```

---

## 📝 清单文件格式

每个清单文件使用 YAML 格式，包含以下字段：

```yaml
name: Role Name
description: Brief description of this role and its needs
role: role-identifier

agents:
  - name: agent-name
    reason: Why this agent is included

skills:
  - name: skill-name
    reason: Why this skill is included

commands:
  - name: command-name
    reason: Why this command is included
```

---

## 🛠️ 创建自定义清单

### 使用 TUI 创建

1. 运行 `python scripts/claude_tui.py`
2. 选择 "Role Checklists" -> "Create Custom"
3. 按提示输入清单信息
4. 清单将保存到 `checklists/custom/`

### 手动创建

1. 复制模板文件:
   ```bash
   cp checklists/template.yaml checklists/custom/my-checklist.yaml
   ```

2. 编辑文件，添加所需组件:
   ```yaml
   name: My Custom Setup
   description: My personalized component setup
   role: custom

   agents:
     - name: debugger
       reason: Essential for troubleshooting
     - name: test-writer
       reason: Generate comprehensive tests

   skills:
     - name: debugging-strategies
       reason: Systematic debugging approaches

   commands:
     - name: review
       reason: Quick code review
   ```

3. 保存并使用 TUI 安装

---

## 💡 最佳实践

### 选择合适的清单

- **明确角色**: 根据主要工作职责选择最匹配的角色清单
- **组合使用**: 可以安装多个角色清单，组件不会重复安装
- **渐进添加**: 先从核心清单开始，根据需要逐步添加其他组件

### 自定义清单建议

- **项目特定**: 为特定项目创建自定义清单
- **团队标准**: 为团队创建统一的组件清单
- **个人偏好**: 根据个人工作流创建优化清单

---

## 📚 相关文档

- [组件目录](../COMPONENTS_CATALOG.md) - 查看所有可用组件
- [Claude-Kits README](../README.md) - 项目总览
- [TUI 使用指南](../scripts/README.md) - TUI 详细文档

---

## 🔄 更新清单

角色清单会随着组件库的更新而更新。建议定期检查：

```bash
# 查看最新的清单
python scripts/claude_tui.py
# 选择 "Role Checklists" -> "View Roles"
```

---

**维护**: Claude-Kits Team | **许可**: MIT
