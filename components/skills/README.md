# Skills 组件库

> **最后更新**: 2025-11-07 | **组件数量**: 11

本目录包含所有可用的技能模块（Skills），通过自然语言自动激活，增强 Claude 的专业能力。

---

## 📋 组件列表

### 开发最佳实践类

| Skill | 主题覆盖 | 触发关键词 | 引用来源 |
|-------|---------|-----------|---------|
| **code-review-excellence** | 代码审查最佳实践、反馈技巧、审查流程 | code review, PR review, feedback | [developer-essentials](../../reference/agents/plugins/developer-essentials/skills/code-review-excellence/) |
| **debugging-strategies** | 系统化调试方法、工具使用、根因分析 | debugging, troubleshooting, bug fix | [developer-essentials](../../reference/agents/plugins/developer-essentials/skills/debugging-strategies/) |
| **error-handling-patterns** | 错误处理模式、异常设计、容错机制 | error handling, exception, try-catch | [developer-essentials](../../reference/agents/plugins/developer-essentials/skills/error-handling-patterns/) |
| **git-advanced-workflows** | Git 高级工作流、分支策略、团队协作 | git workflow, branch strategy, merge | [developer-essentials](../../reference/agents/plugins/developer-essentials/skills/git-advanced-workflows/) |

### 测试类

| Skill | 主题覆盖 | 触发关键词 | 引用来源 |
|-------|---------|-----------|---------|
| **e2e-testing-patterns** | 端到端测试策略、Playwright/Cypress、测试架构 | e2e test, integration test, end-to-end | [developer-essentials](../../reference/agents/plugins/developer-essentials/skills/e2e-testing-patterns/) |
| **python-testing-patterns** | Python 测试模式（pytest/unittest）、fixtures、mocking | python test, pytest, unittest | [python-development](../../reference/agents/plugins/python-development/skills/python-testing-patterns/) |

### 性能与数据库类

| Skill | 主题覆盖 | 触发关键词 | 引用来源 |
|-------|---------|-----------|---------|
| **sql-optimization-patterns** | SQL 查询优化、索引设计、执行计划分析 | sql optimization, query performance, database | [developer-essentials](../../reference/agents/plugins/developer-essentials/skills/sql-optimization-patterns/) |

### 语言特定类

| Skill | 主题覆盖 | 触发关键词 | 引用来源 |
|-------|---------|-----------|---------|
| **typescript-advanced-types** | TypeScript 高级类型系统、泛型、类型推断 | typescript types, generics, type system | [javascript-typescript](../../reference/agents/plugins/javascript-typescript/skills/typescript-advanced-types/) |

### 示例与模板

| Skill | 主题覆盖 | 用途 | 引用来源 |
|-------|---------|------|---------|
| **code-reviewer** | 完整的代码审查流程（含安全、性能、语言指南） | 展示 500 行规则和渐进式披露 | 本项目原创 |
| **skill-template** | 创建新技能的模板 | 开发者参考 | 本项目原创 |

---

## 🎯 自动激活机制

### Skills 如何工作

Skills 通过 **自然语言理解** 自动激活，基于：
1. **YAML Frontmatter 中的 `description` 字段**
2. **用户对话中的关键词和意图**
3. **当前项目的上下文**

### 激活示例

```bash
# 启动 Claude Code
claude

# 自然对话，无需显式调用

> "How should I handle errors in this async function?"
→ error-handling-patterns 自动激活

> "Help me review this pull request"
→ code-review-excellence 自动激活

> "This SQL query is slow, how to optimize it?"
→ sql-optimization-patterns 自动激活

> "I need to write E2E tests for the checkout flow"
→ e2e-testing-patterns 自动激活
```

---

## 📖 使用方法

### 安装 Skill

```bash
# 安装到项目级别（推荐）
python scripts/skills_manager.py install <skill-name> --scope project

# 安装到用户级别（所有项目可用）
python scripts/skills_manager.py install <skill-name> --scope user
```

### Skills 自动激活

Skills 安装后**无需手动调用**，Claude 会根据对话内容自动激活：

```bash
# 无需 "/skill-name" 或 "use skill"
# 直接描述你的需求即可

> "What's the best way to handle database connection errors?"
→ error-handling-patterns + sql-optimization-patterns 可能同时激活

> "Help me write tests for this Python function"
→ python-testing-patterns 自动激活
```

### 查看已安装 Skills

```bash
python scripts/skills_manager.py list
```

---

## 🏗️ Skill 结构

### 标准 Skill 结构

```
skill-name/
├── SKILL.md                 # 主文件（<500 行）
│   ├── YAML Frontmatter     # name, description
│   ├── 概览与快速参考
│   └── 链接到 resources/
└── resources/               # 详细内容（可选）
    ├── topic-1.md          # 深入主题 1
    ├── topic-2.md          # 深入主题 2
    └── ...
```

### 500 行规则

- **主文件** `SKILL.md` 必须 **< 500 行**
- 详细内容放在 `resources/` 目录
- Claude 按需加载资源文件（渐进式披露）

---

## 📝 YAML Frontmatter

每个 Skill 必须包含 YAML frontmatter：

```yaml
---
name: skill-name
description: Detailed description with trigger keywords and use cases...
allowed-tools: Read, Grep, Glob, Bash  # Optional
---
```

### 关键字段说明

| 字段 | 说明 | 必需 |
|------|------|------|
| `name` | 技能名称（小写，连字符分隔） | ✅ 必需 |
| `description` | 详细描述，**必须包含所有触发关键词** | ✅ 必需 |
| `allowed-tools` | 限制可用工具 | 可选 |

### Description 最佳实践

```yaml
# ❌ 不好：太简短
description: Code review skill

# ✅ 好：包含触发场景和关键词
description: Master effective code review practices to provide constructive
  feedback, catch bugs early, and foster knowledge sharing while maintaining
  team morale. Use when reviewing pull requests, establishing review standards,
  or mentoring developers.
```

---

## 🔗 Skills vs Commands vs Agents

| 特性 | Skills | Commands | Agents |
|------|--------|----------|--------|
| **调用方式** | 自动激活 | `/command` | 自然语言/Task |
| **触发条件** | 关键词匹配 | 手动调用 | 显式请求 |
| **持续性** | 持续可用 | 一次性 | 多步对话 |
| **知识深度** | 专业领域知识 | 执行逻辑 | 复杂推理 |

### 何时使用 Skills

- ✅ 需要专业领域知识
- ✅ 希望在对话中自动获得帮助
- ✅ 知识需要在多个任务中复用
- ✅ 有大量参考资料和最佳实践

---

## 🚀 创建自定义 Skill

### 步骤

1. **复制模板**
   ```bash
   cp -r skill-template/ my-skill/
   ```

2. **编辑 SKILL.md**
   - 添加 YAML frontmatter
   - 编写核心内容（< 500 行）
   - 链接到 resources 文件

3. **添加资源文件**（可选）
   ```bash
   mkdir my-skill/resources
   # 创建详细主题文件
   ```

4. **安装测试**
   ```bash
   python scripts/skills_manager.py install my-skill --scope project
   ```

5. **验证激活**
   - 在对话中使用触发关键词
   - 确认 Skill 被正确激活

---

## 📚 Skill 主题分类

### 按难度

| 级别 | Skills |
|------|--------|
| **基础** | error-handling-patterns, git-advanced-workflows |
| **中级** | code-review-excellence, debugging-strategies, python-testing-patterns |
| **高级** | e2e-testing-patterns, sql-optimization-patterns, typescript-advanced-types |

### 按角色

| 角色 | 推荐 Skills |
|------|------------|
| **后端开发** | error-handling-patterns, sql-optimization-patterns, python-testing-patterns |
| **前端开发** | typescript-advanced-types, e2e-testing-patterns, error-handling-patterns |
| **全栈开发** | code-review-excellence, debugging-strategies, git-advanced-workflows |
| **测试工程师** | e2e-testing-patterns, python-testing-patterns, debugging-strategies |
| **架构师** | code-review-excellence, sql-optimization-patterns |

---

## 🔗 相关文档

- [组件目录总览](../../COMPONENTS_CATALOG.md)
- [Skills 官方文档](https://docs.claude.com/claude-code/skills)
- [架构设计文档](../../docs/ARCHITECTURE_DESIGN.md)
- [Claude 工作指南](../../CLAUDE.md)

---

## 📊 统计信息

| 类别 | 数量 |
|------|------|
| 开发最佳实践 | 4 |
| 测试相关 | 2 |
| 性能优化 | 1 |
| 语言特定 | 1 |
| 示例模板 | 3 |
| **总计** | **11** |

### 行数统计

- 平均主文件大小: ~350 行
- 符合 500 行规则: 100%
- 使用渐进式披露: 9/11 (82%)

---

**维护**: Claude-Kits Team | **许可**: MIT
