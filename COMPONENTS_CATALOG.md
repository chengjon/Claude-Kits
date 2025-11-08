# Claude-Kits 组件库目录

> **最后更新**: 2025-11-07
> **组件总数**: 29 个 (10 Agents + 8 Commands + 11 Skills)
> **状态**: ✅ 所有组件符合 Claude Code 官方规范

---

## 📋 目录概览

- [Agents](#agents) - 专业 AI 代理，处理复杂多步骤任务
- [Commands](#commands) - 斜杠命令，快速执行特定操作
- [Skills](#skills) - 技能模块，增强 Claude 的专业能力
- [使用指南](#使用指南)
- [安装方法](#安装方法)

---

## 🤖 Agents

专业 AI 代理，用于处理复杂任务和多步骤工作流。

### 开发与调试类

| Agent | 描述 | 使用场景 |
|-------|------|---------|
| **debugger** | 调试专家，使用现代调试工具和可观测性平台进行根因分析 | 修复 bug、错误追踪、性能问题诊断 |
| **test-writer** | 测试编写专家，生成全面的单元测试、集成测试和 E2E 测试 | 提高测试覆盖率、TDD、测试重构 |
| **test-automator** | 测试自动化专家，生成可维护的测试代码 | 自动化测试、测试策略、质量保证 |

### 架构与设计类

| Agent | 描述 | 使用场景 |
|-------|------|---------|
| **architect-review** | 软件架构大师，专注于现代架构模式和分布式系统设计 | 架构审查、系统设计、技术选型 |
| **backend-architect** | 后端架构专家，精通微服务、API 设计和数据库架构 | 后端系统设计、API 架构、数据建模 |
| **api-designer** | API 设计专家，精通 RESTful、GraphQL 和 API 文档 | API 设计、OpenAPI 规范、接口文档 |
| **frontend-developer** | 前端开发专家，精通现代前端框架和最佳实践 | 前端开发、组件设计、性能优化 |

### 性能与优化类

| Agent | 描述 | 使用场景 |
|-------|------|---------|
| **performance-engineer** | 性能工程师，专注于应用性能优化和监控 | 性能分析、瓶颈诊断、优化建议 |
| **database-optimizer** | 数据库优化专家，精通查询优化和索引设计 | 数据库性能调优、查询优化、架构设计 |

### 安全与合规类

| Agent | 描述 | 使用场景 |
|-------|------|---------|
| **security-auditor** | 安全审计专家，检测漏洞和安全隐患 | 安全审计、漏洞扫描、合规检查 |

### 运维与部署类

| Agent | 描述 | 使用场景 |
|-------|------|---------|
| **devops-troubleshooter** | DevOps 故障排查专家，解决部署和运维问题 | 故障排查、日志分析、系统诊断 |

---

## ⚡ Commands

快速执行的斜杠命令，用于特定任务。

### 开发工具类

| Command | 描述 | 用法示例 |
|---------|------|---------|
| **/review** | 对最近的代码更改进行全面代码审查 | `/review` - 审查 git diff |
| **/docs** | 生成全面的代码文档和 README | `/docs` - 为当前项目生成文档 |
| **/smart-debug** | AI 辅助的智能调试，根因分析 | `/smart-debug [issue描述]` |
| **/test-generate** | 自动生成单元测试 | `/test-generate path/to/file.js` |

### 代码质量类

| Command | 描述 | 用法示例 |
|---------|------|---------|
| **/refactor-clean** | 代码重构和清理，消除技术债务 | `/refactor-clean` |
| **/tech-debt** | 识别和跟踪技术债务 | `/tech-debt analyze` |

### 安全类

| Command | 描述 | 用法示例 |
|---------|------|---------|
| **/security-sast** | 静态应用安全测试（SAST） | `/security-sast scan` |

### 模板（参考）

| Command | 描述 | 用法示例 |
|---------|------|---------|
| **/command-template** | 创建新命令的模板 | 仅供参考 |

---

## 🎯 Skills

增强 Claude 专业能力的技能模块，自动激活。

### 开发最佳实践类

| Skill | 描述 | 自动激活场景 |
|-------|------|------------|
| **code-review-excellence** | 代码审查最佳实践，提供建设性反馈 | 审查 PR、代码质量讨论 |
| **debugging-strategies** | 系统化调试策略和工具使用 | 调试问题、错误追踪 |
| **error-handling-patterns** | 错误处理模式和最佳实践 | 异常处理、错误设计 |
| **git-advanced-workflows** | Git 高级工作流和团队协作 | Git 操作、版本管理 |

### 测试类

| Skill | 描述 | 自动激活场景 |
|-------|------|------------|
| **e2e-testing-patterns** | 端到端测试模式和策略 | E2E 测试、集成测试 |
| **python-testing-patterns** | Python 测试模式（pytest, unittest） | Python 测试开发 |

### 性能与数据库类

| Skill | 描述 | 自动激活场景 |
|-------|------|------------|
| **sql-optimization-patterns** | SQL 查询优化和数据库性能 | 数据库优化、查询调优 |

### 语言特定类

| Skill | 描述 | 自动激活场景 |
|-------|------|------------|
| **typescript-advanced-types** | TypeScript 高级类型系统 | TypeScript 开发、类型设计 |

### 示例（参考）

| Skill | 描述 | 用途 |
|-------|------|-----|
| **code-reviewer** | 完整的代码审查技能示例 | 展示 500 行规则和渐进式披露 |
| **skill-template** | 创建新技能的模板 | 开发者参考 |

---

## 📦 使用指南

### Agents 使用

Agents 通过 Task 工具调用或自然语言激活：

```
"Use the debugger agent to analyze this error"
"Help me design an API for this feature"
"Review the architecture of this system"
```

### Commands 使用

Commands 通过斜杠命令调用：

```
/review
/smart-debug "Login timeout errors"
/test-generate src/utils/validator.js
/security-sast scan
```

### Skills 使用

Skills 通过自然语言**自动激活**，无需显式调用：

- 当你讨论代码审查时，`code-review-excellence` 自动激活
- 当你处理错误时，`error-handling-patterns` 自动激活
- 当你优化 SQL 时，`sql-optimization-patterns` 自动激活

---

## 🚀 安装方法

### 方法 1：使用管理脚本（推荐）

```bash
# 安装单个 Agent
python scripts/subagents_manager.py install debugger --scope project

# 安装单个 Command
python scripts/commands_manager.py install review --scope project

# 安装单个 Skill
python scripts/skills_manager.py install code-review-excellence --scope project
```

### 方法 2：手动安装

#### 安装 Agent
```bash
cp components/agents/debugger.md ~/.claude/agents/
# 或项目级别
cp components/agents/debugger.md .claude/agents/
```

#### 安装 Command
```bash
cp components/commands/review.md ~/.claude/commands/
# 或项目级别
cp components/commands/review.md .claude/commands/
```

#### 安装 Skill
```bash
cp -r components/skills/code-review-excellence ~/.claude/skills/
# 或项目级别
cp -r components/skills/code-review-excellence .claude/skills/
```

### 方法 3：批量安装

```bash
# 安装所有 Agents
for agent in components/agents/*.md; do
  cp "$agent" .claude/agents/
done

# 安装所有 Commands
for cmd in components/commands/*.md; do
  cp "$cmd" .claude/commands/
done

# 安装所有 Skills
for skill in components/skills/*/; do
  cp -r "$skill" .claude/skills/
done
```

---

## 📊 组件统计

| 类型 | 已部署 | 可用参考 | 总计 |
|------|--------|----------|------|
| Agents | 10 | 147 | 157 |
| Commands | 8 | 70 | 78 |
| Skills | 11 | 58 | 69 |
| **总计** | **29** | **275** | **304** |

---

## 🎯 推荐组合

### 全栈开发套件
- Agents: `backend-architect`, `frontend-developer`, `api-designer`
- Commands: `/review`, `/docs`, `/test-generate`
- Skills: `code-review-excellence`, `error-handling-patterns`

### 性能优化套件
- Agents: `performance-engineer`, `database-optimizer`
- Commands: `/refactor-clean`, `/smart-debug`
- Skills: `sql-optimization-patterns`, `debugging-strategies`

### 安全审计套件
- Agents: `security-auditor`
- Commands: `/security-sast`, `/review`
- Skills: `code-review-excellence`, `error-handling-patterns`

### 测试自动化套件
- Agents: `test-writer`, `test-automator`
- Commands: `/test-generate`
- Skills: `e2e-testing-patterns`, `python-testing-patterns`

---

## 🔄 更新日志

### 2025-11-07 - 初始版本
- ✅ 部署 10 个核心 Agents
- ✅ 部署 8 个实用 Commands
- ✅ 部署 11 个重要 Skills
- ✅ 所有组件符合官方规范
- ✅ 提供完整的使用文档

### 计划中
- [ ] 添加更多语言特定的 Agents（Go, Rust, Java）
- [ ] 创建完整的 Plugin 示例
- [ ] 添加 Hooks 示例
- [ ] 扩展数据库和云架构组件

---

## 📚 相关文档

- [CLAUDE.md](CLAUDE.md) - Claude Code 工作指南
- [ARCHITECTURE_DESIGN.md](docs/ARCHITECTURE_DESIGN.md) - 架构设计文档
- [COMPLIANCE_AUDIT_REPORT.md](docs/COMPLIANCE_AUDIT_REPORT.md) - 合规性审核报告
- [Claude Code 官方文档](https://docs.claude.com/claude-code)

---

## 🤝 贡献

欢迎贡献更多实用组件！请确保：
1. 遵循官方 Claude Code 规范
2. 包含完整的 YAML Frontmatter
3. Skills 主文件 < 500 行
4. 提供清晰的使用说明和示例

---

**Happy Coding with Claude!** 🚀
