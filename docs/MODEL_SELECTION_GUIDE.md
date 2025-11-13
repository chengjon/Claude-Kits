# Claude Model Selection Guide

> 基于 Claude-Kits 中 165 个 Agent 的 model 配置分析

## 📊 统计概览

在 Claude-Kits 的 Agent 配置中：

- **Sonnet**: 134 个 agents (81.2%)
- **Haiku**: 30 个 agents (18.2%)
- **Opus**: 1 个 agent (0.6%)

## 🎯 Model 选择模式

### 1. Opus - 复杂编排和战略规划

**使用场景**:
- 高度复杂的多步骤任务分析
- 需要深度推理和战略决策
- 多代理协调和任务编排

**示例**:
- `tech-lead-orchestrator` - 技术主管编排器
  - 分析复杂项目需求
  - 将任务分解并分配给子代理
  - 需要深度理解项目架构和任务依赖

**特点**:
- 最强的推理能力
- 最适合复杂的架构决策
- 成本最高，仅用于最复杂的场景

---

### 2. Sonnet - 平衡性能和成本 (默认选择)

**使用场景** (81% 的 agents):
- 代码生成和重构
- API 设计和实现
- 安全代码审查
- 架构设计
- 测试编写
- 文档生成
- 大多数开发任务

**示例**:
- `backend-architect` - 后端架构师
- `api-designer` - API 设计专家
- `code-reviewer` - 代码审查
- `frontend-security-coder` - 前端安全编码
- `django-pro` - Django 专家
- `fastapi-pro` - FastAPI 专家
- `kubernetes-architect` - K8s 架构师

**特点**:
- 优秀的代码生成能力
- 良好的上下文理解
- 性价比最佳
- 适合绝大多数开发场景

---

### 3. Haiku - 快速响应和简单任务

**使用场景** (18% 的 agents):
- 配置管理和运维
- 文档生成
- 内容创作
- 数据分析
- 简单的调试任务
- 客户支持
- 业务分析

**示例**:

#### 运维和基础设施
- `network-engineer` - 网络工程师
- `deployment-engineer` - 部署工程师
- `database-admin` - 数据库管理员
- `devops-troubleshooter` - DevOps 故障排查

#### 文档和内容
- `api-documenter` - API 文档专家
- `content-marketer` - 内容营销
- `customer-support` - 客户支持

#### 分析和优化
- `business-analyst` - 业务分析师
- `database-optimizer` - 数据库优化
- `performance-optimizer` - 性能优化

#### 调试和维护
- `debugger` - 调试专家
- `error-detective` - 错误侦探

**特点**:
- 响应速度最快
- 成本最低
- 适合结构化、明确的任务
- 不需要深度推理的场景

---

## 🔍 选择建议

### 何时使用 Opus
```yaml
model: opus
```
- ✅ 多步骤项目规划和编排
- ✅ 复杂的架构决策需要深度推理
- ✅ 跨多个领域的战略分析
- ✅ 任务分解和代理协调
- ❌ 成本敏感的场景
- ❌ 简单重复性任务

### 何时使用 Sonnet (默认)
```yaml
model: sonnet
# 或不指定，使用默认
```
- ✅ 代码编写和重构
- ✅ API 设计和实现
- ✅ 安全审查和分析
- ✅ 复杂的技术实现
- ✅ 需要深度上下文理解
- ✅ 大多数开发任务

### 何时使用 Haiku
```yaml
model: haiku
```
- ✅ 快速响应需求（如实时支持）
- ✅ 配置文件生成
- ✅ 简单的 CRUD 操作
- ✅ 文档和内容生成
- ✅ 结构化数据处理
- ✅ 成本敏感的场景
- ❌ 需要复杂推理
- ❌ 复杂的架构设计

---

## 📈 性能对比

| 特性 | Opus | Sonnet | Haiku |
|------|------|--------|-------|
| 推理能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ | ⭐⭐⭐☆☆ |
| 代码质量 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐☆☆ |
| 响应速度 | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐⭐ |
| 成本效益 | ⭐⭐☆☆☆ | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐⭐ |
| 上下文理解 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ | ⭐⭐⭐☆☆ |

---

## 💡 最佳实践

### 1. 分层策略
```
Opus → 顶层编排和规划
  ↓
Sonnet → 核心开发和实现
  ↓
Haiku → 快速任务和支持
```

### 2. 任务类型匹配

**复杂任务** (使用 Sonnet/Opus):
- 设计新的系统架构
- 实现复杂的业务逻辑
- 安全审计和漏洞分析
- 性能优化和重构

**简单任务** (使用 Haiku):
- 生成配置文件
- 编写标准化文档
- 执行常规维护任务
- 回答客户问题

### 3. 成本优化

如果预算有限：
1. 默认使用 Sonnet（不指定 model）
2. 仅在明确需要快速响应时使用 Haiku
3. 避免使用 Opus，除非确实需要深度推理

如果追求最佳质量：
1. 编排和规划使用 Opus
2. 核心开发使用 Sonnet
3. 辅助任务使用 Haiku

---

## 🛠️ 实际应用示例

### 场景 1: 构建 RESTful API

```yaml
# 规划阶段 - 使用 Opus（可选）
tech-lead-orchestrator:
  model: opus
  task: 分析需求，制定实施计划

# API 设计 - 使用 Sonnet
api-designer:
  model: sonnet
  task: 设计 API 端点和数据模型

# 后端实现 - 使用 Sonnet
backend-architect:
  model: sonnet
  task: 实现业务逻辑和数据库层

# 文档生成 - 使用 Haiku
api-documenter:
  model: haiku
  task: 生成 OpenAPI 规范和 README
```

### 场景 2: 数据库优化

```yaml
# 分析性能瓶颈 - 使用 Sonnet
database-optimizer:
  model: sonnet  # Haiku 也可以，但建议 Sonnet
  task: 分析慢查询，优化索引

# 配置调优 - 使用 Haiku
database-admin:
  model: haiku
  task: 生成优化后的配置文件
```

### 场景 3: 前端开发

```yaml
# 组件设计 - 使用 Sonnet
react-component-architect:
  model: sonnet
  task: 设计复杂的 React 组件

# 样式实现 - 使用 Haiku
tailwind-css-expert:
  model: haiku
  task: 实现 Tailwind CSS 样式
```

---

## 🔄 迁移指南

### 从无指定到 Haiku

如果你的 agent 执行简单、结构化的任务，考虑添加：

```yaml
---
name: my-agent
description: ...
model: haiku  # 新增
---
```

**适用场景**:
- 生成配置文件
- 简单的 CRUD 操作
- 文档生成
- 数据格式转换

### 从 Sonnet 到 Opus

如果你的 agent 需要深度推理，考虑升级：

```yaml
---
name: my-orchestrator
description: ...
model: opus  # 从 sonnet 升级
---
```

**适用场景**:
- 多代理任务编排
- 复杂的战略规划
- 跨领域的综合分析

---

## 📚 参考资源

- **Claude Models 官方文档**: https://docs.anthropic.com/claude/docs/models-overview
- **Claude-Kits Agents**: `/opt/claude/Claude-Kits/components/agents/`
- **实际使用统计**: 本文档基于 165 个实际生产环境 agents 的配置

---

## 🎓 总结

1. **默认使用 Sonnet** - 81% 的场景适用
2. **Haiku 用于简单快速任务** - 18% 的场景
3. **Opus 仅用于复杂编排** - 非常少见 (< 1%)
4. **权衡成本和质量** - 根据实际需求选择
5. **可以不指定 model** - 系统会使用默认 (通常是 Sonnet)

**记住**: 在 Claude Code 中，不指定 `model` 字段时，系统会使用合理的默认值。只在有明确需求时才指定 model。
