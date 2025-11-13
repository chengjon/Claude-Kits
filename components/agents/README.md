---
description: 文档管理专家，专注项目文档创建、API文档生成和知识库维护。为开发团队提供清晰的结构化文档和技术说明。
model: sonnet
name: README
---

# Agents 组件库

> **最后更新**: 2025-11-07 | **组件数量**: 10

本目录包含所有可用的专业 AI 代理（Agents），用于处理复杂的多步骤任务。

---

## 📋 组件列表

### 架构与设计类

| Agent | 模型 | 功能描述 | 引用来源 |
|-------|------|---------|---------|
| **architect-review** | sonnet | 软件架构大师，专注于现代架构模式、微服务、事件驱动、DDD。进行架构审查和设计指导 | [code-review-ai](../../reference/agents/plugins/code-review-ai/agents/architect-review.md) |
| **backend-architect** | sonnet | 后端架构专家，精通 RESTful API、微服务、数据库架构设计 | [backend-development](../../reference/agents/plugins/backend-development/agents/backend-architect.md) |
| **frontend-developer** | sonnet | 前端开发专家，精通 React/Vue/Angular、响应式设计、客户端状态管理 | [frontend-mobile-development](../../reference/agents/plugins/frontend-mobile-development/agents/frontend-developer.md) |
| **api-designer** | sonnet | API 设计专家，精通 RESTful、GraphQL、OpenAPI 规范编写 | 本项目原创 |

### 开发与测试类

| Agent | 模型 | 功能描述 | 引用来源 |
|-------|------|---------|---------|
| **test-writer** | sonnet | 测试编写专家，生成全面的单元测试、集成测试、E2E 测试 | 本项目原创 |
| **test-automator** | sonnet | 测试自动化专家，创建可维护的测试代码，最大化测试覆盖率 | [unit-testing](../../reference/agents/plugins/unit-testing/agents/test-automator.md) |
| **debugger** | sonnet | 调试专家，使用现代调试工具和可观测性平台进行根因分析 | [debugging-toolkit](../../reference/agents/plugins/debugging-toolkit/agents/debugger.md) |

### 性能与优化类

| Agent | 模型 | 功能描述 | 引用来源 |
|-------|------|---------|---------|
| **performance-engineer** | sonnet | 性能工程师，专注于应用性能优化、监控、APM 集成 | [application-performance](../../reference/agents/plugins/application-performance/agents/performance-engineer.md) |
| **database-optimizer** | sonnet | 数据库优化专家，精通查询优化、索引设计、迁移策略 | [database-cloud-optimization](../../reference/agents/plugins/database-cloud-optimization/agents/database-optimizer.md) |

### 安全与合规类

| Agent | 模型 | 功能描述 | 引用来源 |
|-------|------|---------|---------|
| **security-auditor** | sonnet | 安全审计专家，检测 OWASP Top 10 漏洞和安全隐患 | [comprehensive-review](../../reference/agents/plugins/comprehensive-review/agents/security-auditor.md) |

### 运维与故障排查类

| Agent | 模型 | 功能描述 | 引用来源 |
|-------|------|---------|---------|
| **devops-troubleshooter** | sonnet | DevOps 故障排查专家，生产环境调试、日志分析、部署故障诊断 | [cicd-automation](../../reference/agents/plugins/cicd-automation/agents/devops-troubleshooter.md) |

---

## 🎯 使用场景

### 开发阶段
- **架构设计**: architect-review, backend-architect, api-designer
- **前端开发**: frontend-developer
- **代码质量**: test-writer, test-automator

### 测试阶段
- **单元测试**: test-writer, test-automator
- **调试**: debugger, devops-troubleshooter

### 优化阶段
- **性能优化**: performance-engineer, database-optimizer
- **安全审计**: security-auditor

### 运维阶段
- **故障排查**: devops-troubleshooter, debugger
- **数据库维护**: database-optimizer

---

## 📖 使用方法

### 安装 Agent

```bash
# 安装到项目级别
python scripts/subagents_manager.py install <agent-name> --scope project

# 安装到用户级别
python scripts/subagents_manager.py install <agent-name> --scope user
```

### 使用 Agent

```bash
# 启动 Claude Code
claude

# 自然语言激活
> "Use the debugger agent to analyze this error"
> "Help me design an API with the api-designer agent"
> "Review the architecture using architect-review agent"
```

### 查看已安装 Agents

```bash
python scripts/subagents_manager.py list
```

---

## 🏷️ 模型说明

| 模型 | 特点 | 推荐场景 |
|------|------|---------|
| **sonnet** | 快速、高效、成本优 | 大多数开发任务 |
| **opus** | 最强能力、深度分析 | 复杂架构决策（未来支持） |
| **haiku** | 超快速、简单任务 | 快速查询（未来支持） |

*注：当前所有 agents 默认使用 sonnet 模型*

---

## 🔗 相关文档

- [组件目录总览](../../COMPONENTS_CATALOG.md)
- [架构设计文档](../../docs/ARCHITECTURE_DESIGN.md)
- [Claude 工作指南](../../CLAUDE.md)

---

## 📝 添加新 Agent

1. 参考 `agent-template.md` 创建新的 agent 文件
2. 确保包含正确的 YAML frontmatter
3. 更新本 README.md 添加新 agent 信息
4. 测试 agent 功能正常

---

**维护**: Claude-Kits Team | **许可**: MIT
