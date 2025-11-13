# Role Collections Implementation Summary

## 📅 文档更新时间
2025-11-10 (v3.0.0)

## 🎯 文档目标

本文档全面介绍 Claude-Kits 中所有可用的 Role 集合，包括：
1. **Reddit-Case** - Reddit 工程师 30 万行代码最佳实践
2. **6 个通用角色** - 后端/前端/全栈/DevOps/测试/安全工程师

每个 Role 集合都是精心设计的组件包，包含 Skills、Agents、Commands 和 Hooks，为特定开发角色提供完整的工具链。

---

## 📦 可用的 Role 集合

### 快速概览

| Role | 组件数 | Skills | Agents | Commands | Hooks | 适用场景 |
|------|--------|--------|--------|----------|-------|---------|
| reddit-case | 28 | 7 | 7 | 6 | 4 | 高质量零错误项目 |
| backend-developer | 13 | 4 | 5 | 4 | 0 | 后端 API 和数据库开发 |
| frontend-developer | 13 | 5 | 4 | 4 | 0 | 现代前端应用开发 |
| fullstack-developer | 19 | 7 | 6 | 5 | 0 | 全栈 Web 应用开发 |
| devops-engineer | 12 | 3 | 5 | 4 | 0 | DevOps 和基础设施 |
| test-engineer | 13 | 5 | 3 | 4 | 0 | 测试自动化和质量保证 |
| security-engineer | 10 | 3 | 3 | 4 | 0 | 安全审计和漏洞扫描 |

---

## 1️⃣ Reddit-Case - 30 万行代码工程实践

### 概述
基于 Reddit 工程师在 30 万行代码项目中的实践经验，这是最完整的质量保证系统，包含自动化工作流、质量门禁和上下文持久化。

### 核心特性
- ✅ **Skills 自动激活系统** - 确保 Claude 始终使用相关技能
- ✅ **零错误容忍系统** - 构建检查质量门禁（Reddit 团队 6 个月零错误记录）
- ✅ **上下文持久化** - Dev Docs 三文档系统，跨会话工作
- ✅ **完整的自动化管道** - 4 个核心 Hooks 自动化工作流

### 组件清单

#### 🤖 Agents (7 个)
1. **auth-route-tester** - 认证路由测试
   - 自动测试 API 路由的认证和授权
   - 生成测试用例和验证逻辑

2. **build-error-resolver** - 构建错误自动修复
   - 分析构建错误并提供修复方案
   - 自动修复常见的类型错误

3. **code-architecture-reviewer** - 代码架构审查
   - 审查代码架构和设计模式
   - 确保符合项目架构规范

4. **database-verifier** - 数据库验证
   - 验证数据库 schema 和迁移
   - 检查数据一致性

5. **documentation-architect** - 文档架构
   - 设计和维护项目文档结构
   - 确保文档完整性

6. **frontend-error-fixer** - 前端错误修复
   - 修复前端编译和运行时错误
   - 优化前端代码质量

7. **strategic-plan-architect** - 战略规划
   - 制定项目开发计划
   - 任务分解和优先级排序

#### 📚 Skills (7 个)
1. **backend-dev-guidelines** - 后端开发指南
   - Reddit 后端开发最佳实践
   - API 设计和数据库模式

2. **dev-docs-workflow** - Dev Docs 工作流
   - 三文档系统（plan.md + context.md + tasks.md）
   - 上下文持久化和恢复

3. **frontend-dev-guidelines** - 前端开发指南
   - React/TypeScript 最佳实践
   - 组件设计和状态管理

4. **notification-developer** - 通知系统开发
   - 实时通知系统设计
   - WebSocket 和推送通知

5. **progressive-disclosure-pattern** - 渐进式披露模式
   - 复杂功能的渐进式展示
   - 用户体验优化

6. **skill-developer** - Skill 开发元技能
   - 创建自定义 Claude Skills
   - Skills 最佳实践

7. **workflow-developer** - 工作流开发
   - 自动化工作流设计
   - Hooks 和 Commands 集成

#### 🪝 Hooks (4 个)
1. **user-prompt-submit-skill-activation.sh** (UserPromptSubmit)
   - **最重要** - Skills 自动激活系统核心
   - 分析用户提示，强制激活相关 Skills
   - 配合 skill-rules.json 使用

2. **post-tool-use-file-edit-tracker.sh** (PostToolUse)
   - 追踪所有文件编辑操作
   - 记录到 edit_log.jsonl
   - 为构建检查提供数据

3. **stop-build-checker.sh** (Stop)
   - **零错误容忍的秘诀** - 构建检查质量门禁
   - 读取编辑日志，批量运行构建
   - 错误 ≥5 时阻断（exit 2），要求修复

4. **session-start-dev-docs-injector.sh** (SessionStart)
   - 自动注入 Dev Docs 上下文
   - 恢复 plan.md、context.md、tasks.md
   - 实现跨会话连续性

#### ⚡ Commands (6 个)
1. **/dev-docs** - 创建 Dev Docs 系统
2. **/dev-docs-update** - 更新 Dev Docs
3. **/code-review** - 代码审查
4. **/build-and-fix** - 构建并修复错误
5. **/test-route** - API 路由测试
6. **/pm2-status** - PM2 状态查看

#### ⚙️ 配置文件
1. **settings.json** - Hooks 配置
2. **skill-rules.json** - Skills 激活规则
3. **build-checker.json** - 构建检查配置

### 安装方式

```bash
# 方法 1: 使用 Roles Manager（推荐）
python scripts/roles_manager.py install reddit-case --path /path/to/project

# 方法 2: 使用传统安装脚本
python scripts/install_reddit_case.py /path/to/project
```

### 安装后配置

#### 1. 配置构建检查 (`.claude/build-checker.json`)
```json
{
  "repos": {
    "/absolute/path/to/your/project": {
      "buildCommand": "npm run build",
      "errorThreshold": 5
    }
  }
}
```

#### 2. 配置 Skills 激活规则 (`.claude/skill-rules.json`)
```json
{
  "skills": {
    "backend-dev-guidelines": {
      "fileTriggers": {
        "pathPatterns": [
          "src/routes/**/*.ts",
          "src/controllers/**/*.ts"
        ]
      }
    }
  }
}
```

#### 3. 自定义 Skills 描述
编辑每个 `.claude/skills/*/SKILL.md` 的 `description` 字段，添加项目特定关键词。

### 适用场景
- ✅ 需要高质量、零错误容忍的项目
- ✅ 中大型项目（10,000+ 行代码）
- ✅ 需要跨会话上下文持久化
- ✅ 团队协作开发
- ✅ 需要自动化质量门禁

---

## 2️⃣ Backend Developer - 后端开发工具集

### 概述
Essential tools for backend development, API design, and database management

### 组件清单 (13 个组件)

#### 🤖 Agents (5 个)
1. **backend-architect** - 后端架构专家
   - RESTful API 设计、微服务和数据库架构

2. **database-optimizer** - 数据库优化器
   - 查询优化和数据库性能调优

3. **api-designer** - API 设计师
   - API 设计、OpenAPI 规范和文档

4. **test-writer** - 测试编写器
   - 生成全面的单元和集成测试

5. **debugger** - 调试器
   - 调试复杂的后端问题和生产问题

#### 📚 Skills (4 个)
1. **sql-optimization-patterns** - SQL 优化模式
   - 掌握 SQL 查询优化和数据库最佳实践

2. **error-handling-patterns** - 错误处理模式
   - 在后端服务中实现健壮的错误处理

3. **debugging-strategies** - 调试策略
   - 后端系统的系统化调试方法

4. **code-review-excellence** - 代码审查卓越
   - 审查后端代码的质量和安全性

#### ⚡ Commands (4 个)
1. **/review** - 快速代码审查
2. **/test-generate** - 生成测试
3. **/smart-debug** - AI 辅助调试
4. **/refactor-clean** - 重构清理

### 安装方式

```bash
python scripts/roles_manager.py install backend-developer --path /path/to/project
```

### 适用场景
- ✅ 后端 API 和微服务开发
- ✅ 数据库设计和优化
- ✅ RESTful/GraphQL API 设计
- ✅ 后端性能调优

---

## 3️⃣ Frontend Developer - 前端开发工具集

### 概述
Essential tools for modern frontend development with React/Vue/Angular

### 组件清单 (13 个组件)

#### 🤖 Agents (4 个)
1. **frontend-developer** - 前端开发专家
   - React/Vue/Angular、响应式设计和客户端架构

2. **api-designer** - API 设计师
   - 设计前后端 API 契约和集成点

3. **test-writer** - 测试编写器
   - 编写组件测试和 E2E 测试

4. **performance-engineer** - 性能工程师
   - 优化前端性能和打包体积

#### 📚 Skills (5 个)
1. **typescript-advanced-types** - TypeScript 高级类型
   - 掌握 TypeScript 类型系统，实现类型安全的前端代码

2. **e2e-testing-patterns** - E2E 测试模式
   - 使用 Playwright/Cypress 实现全面的 E2E 测试

3. **error-handling-patterns** - 错误处理模式
   - 在前端应用中优雅地处理错误

4. **code-review-excellence** - 代码审查卓越
   - 审查前端代码的质量和最佳实践

5. **debugging-strategies** - 调试策略
   - 跨浏览器调试前端问题

#### ⚡ Commands (4 个)
1. **/review** - 快速代码审查
2. **/test-generate** - 生成组件测试
3. **/docs** - 生成组件文档
4. **/refactor-clean** - 重构清理

### 安装方式

```bash
python scripts/roles_manager.py install frontend-developer --path /path/to/project
```

### 适用场景
- ✅ React/Vue/Angular 应用开发
- ✅ TypeScript 前端项目
- ✅ 组件驱动开发
- ✅ 前端性能优化

---

## 4️⃣ Full-Stack Developer - 全栈开发工具集

### 概述
Comprehensive toolkit for full-stack web development

### 组件清单 (19 个组件)

#### 🤖 Agents (6 个)
1. **backend-architect** - 设计和审查后端架构
2. **frontend-developer** - 构建现代前端应用
3. **api-designer** - 设计连接前后端的 API
4. **database-optimizer** - 优化数据库查询和 schema 设计
5. **test-writer** - 编写跨整个技术栈的测试
6. **architect-review** - 审查整体系统架构

#### 📚 Skills (7 个)
1. **typescript-advanced-types** - 跨技术栈的类型安全开发
2. **e2e-testing-patterns** - 全栈应用的端到端测试
3. **sql-optimization-patterns** - 数据库优化和查询调优
4. **error-handling-patterns** - 一致的错误处理模式
5. **code-review-excellence** - 审查前后端代码
6. **git-advanced-workflows** - 团队协作的高级 Git 工作流
7. **debugging-strategies** - 跨整个技术栈调试问题

#### ⚡ Commands (5 个)
1. **/review** - 全面代码审查
2. **/test-generate** - 为任何层生成测试
3. **/docs** - 生成项目文档
4. **/smart-debug** - 调试复杂的全栈问题
5. **/refactor-clean** - 重构和清理代码库

### 安装方式

```bash
python scripts/roles_manager.py install fullstack-developer --path /path/to/project
```

### 适用场景
- ✅ 全栈 Web 应用开发
- ✅ 单人或小团队项目
- ✅ 需要前后端同时开发
- ✅ Monorepo 项目

---

## 5️⃣ DevOps Engineer - DevOps 工具集

### 概述
Tools for DevOps, CI/CD, deployment, and infrastructure management

### 组件清单 (12 个组件)

#### 🤖 Agents (5 个)
1. **devops-troubleshooter** - DevOps 故障排查专家
   - 生产调试、日志分析和部署问题

2. **architect-review** - 架构审查
   - 审查基础设施和部署架构

3. **database-optimizer** - 数据库优化器
   - 优化生产环境中的数据库性能

4. **performance-engineer** - 性能工程师
   - 监控和优化应用性能

5. **security-auditor** - 安全审计员
   - 安全审计和漏洞扫描

#### 📚 Skills (3 个)
1. **debugging-strategies** - 生产问题的系统化调试
2. **error-handling-patterns** - 实现健壮的错误处理和监控
3. **git-advanced-workflows** - 高级 Git 工作流和 CI/CD 集成

#### ⚡ Commands (4 个)
1. **/smart-debug** - 调试部署和基础设施问题
2. **/security-sast** - 部署前安全扫描
3. **/review** - 审查基础设施即代码变更
4. **/docs** - 生成部署和运维文档

### 安装方式

```bash
python scripts/roles_manager.py install devops-engineer --path /path/to/project
```

### 适用场景
- ✅ CI/CD 管道设计
- ✅ Kubernetes/Docker 部署
- ✅ 基础设施即代码 (Terraform/Ansible)
- ✅ 生产环境监控和故障排查

---

## 6️⃣ Test Engineer - 测试工程师工具集

### 概述
Comprehensive testing tools for unit, integration, and E2E testing

### 组件清单 (13 个组件)

#### 🤖 Agents (3 个)
1. **test-writer** - 测试编写器
   - 生成跨所有测试级别的全面测试套件

2. **test-automator** - 测试自动化器
   - 创建可维护的测试自动化框架

3. **debugger** - 调试器
   - 调试失败的测试并识别根本原因

#### 📚 Skills (5 个)
1. **e2e-testing-patterns** - 使用 Playwright/Cypress 掌握 E2E 测试
2. **python-testing-patterns** - 使用 pytest 和 unittest 进行 Python 测试
3. **debugging-strategies** - 调试测试失败和不稳定的测试
4. **code-review-excellence** - 审查测试代码的质量和可维护性
5. **error-handling-patterns** - 测试代码中的正确错误处理

#### ⚡ Commands (4 个)
1. **/test-generate** - 生成单元和集成测试
2. **/smart-debug** - 调试测试失败
3. **/review** - 审查测试代码质量
4. **/refactor-clean** - 重构和清理测试代码

### 安装方式

```bash
python scripts/roles_manager.py install test-engineer --path /path/to/project
```

### 适用场景
- ✅ 测试自动化框架开发
- ✅ QA 和质量保证
- ✅ TDD/BDD 开发流程
- ✅ 测试覆盖率提升

---

## 7️⃣ Security Engineer - 安全工程师工具集

### 概述
Security auditing, vulnerability scanning, and secure coding practices

### 组件清单 (10 个组件)

#### 🤖 Agents (3 个)
1. **security-auditor** - 安全审计员
   - 检测 OWASP Top 10 漏洞和安全问题的专家

2. **architect-review** - 架构审查
   - 审查架构的安全问题

3. **debugger** - 调试器
   - 调试安全相关问题和漏洞

#### 📚 Skills (3 个)
1. **error-handling-patterns** - 安全的错误处理，不泄露信息
2. **code-review-excellence** - 以安全为重点的代码审查实践
3. **debugging-strategies** - 调试和分析安全漏洞

#### ⚡ Commands (4 个)
1. **/security-sast** - 静态应用安全测试
2. **/review** - 以安全为重点的代码审查
3. **/smart-debug** - 调试安全问题和漏洞利用
4. **/tech-debt** - 识别安全相关的技术债务

### 安装方式

```bash
python scripts/roles_manager.py install security-engineer --path /path/to/project
```

### 适用场景
- ✅ 安全审计和渗透测试
- ✅ OWASP 漏洞扫描
- ✅ 安全编码实践
- ✅ 合规性审查（GDPR/HIPAA）

---

## 🎯 Role 选择指南

### 根据项目类型选择

| 项目类型 | 推荐 Role | 原因 |
|---------|----------|------|
| 纯后端 API | backend-developer | 专注后端开发和数据库 |
| 纯前端 SPA | frontend-developer | 专注前端组件和性能 |
| 全栈 Web 应用 | fullstack-developer | 涵盖前后端所有需求 |
| 高质量项目 | reddit-case | 完整的质量保证系统 |
| 微服务部署 | devops-engineer | CI/CD 和容器化 |
| QA 测试 | test-engineer | 全面的测试工具 |
| 安全审计 | security-engineer | 安全扫描和漏洞检测 |

### 根据团队规模选择

| 团队规模 | 推荐策略 | 说明 |
|---------|---------|------|
| 1 人 | fullstack-developer | 一个人需要前后端都会 |
| 2-3 人 | 按角色分配（backend/frontend） | 每人安装自己的角色 |
| 4-10 人 | 所有角色 + reddit-case | 完整的工具链和质量保证 |
| 10+ 人 | 专业角色 + DevOps + Security | 专业分工，加强基础设施和安全 |

### 组合安装建议

#### 小团队（2-3 人）
```bash
# 后端开发者
python scripts/roles_manager.py install backend-developer --path /project

# 前端开发者
python scripts/roles_manager.py install frontend-developer --path /project
```

#### 中型团队（4-10 人）
```bash
# 安装 Reddit-Case（团队共享）
python scripts/roles_manager.py install reddit-case --path /project

# 各自安装专业 Role
python scripts/roles_manager.py install backend-developer --path /project
python scripts/roles_manager.py install frontend-developer --path /project
python scripts/roles_manager.py install devops-engineer --path /project
```

#### 企业团队（10+ 人）
```bash
# 完整工具链
python scripts/roles_manager.py install reddit-case --path /project
python scripts/roles_manager.py install backend-developer --path /project
python scripts/roles_manager.py install frontend-developer --path /project
python scripts/roles_manager.py install devops-engineer --path /project
python scripts/roles_manager.py install test-engineer --path /project
python scripts/roles_manager.py install security-engineer --path /project
```

---

## 📚 Reddit-Case 核心知识点

### 🚨 最重要的发现：Skills 不会自动激活！

**错误认知**：之前以为 Claude 会自动读取 `.claude/skills/` 下的所有 SKILL.md 文件。

**真相**：Claude **不会**自动加载/采用所有 Skill 文档！Reddit 工程师在 30 万行代码中发现 Claude 经常忽略技能。

**解决方案**：UserPromptSubmit Hook + skill-rules.json 强制激活

```
用户输入 → UserPromptSubmit Hook → 分析提示词 → 匹配 skill-rules.json
→ 输出 JSON additionalContext → 强制 Claude 加载技能 → Claude 处理请求
```

### 📚 9 大核心知识点

#### 1. stdout 注入只在两个事件中有效 ⭐

**只有这两个事件的 stdout 会注入到 Claude**：
- `UserPromptSubmit` - 在 Claude 处理用户提示前注入
- `SessionStart` - 在会话启动时注入（恢复上下文）

**其他 7 个事件的 stdout 不会注入**，需要用 JSON `hookSpecificOutput.additionalContext`

#### 2. 温和提醒哲学（Exit Code 策略）⭐

**Exit Code 0** - 成功，继续
- stdout 在某些事件会被注入（UserPromptSubmit, SessionStart）

**Exit Code 1** - 警告但不阻止（温和提醒）
- stderr 显示给用户
- 操作继续执行
- **适用**：代码风格建议、性能优化提示、最佳实践提醒

**Exit Code 2** - 阻断操作（强制门禁）
- PreToolUse: 阻止工具调用，stderr 给 Claude
- Stop: 阻止停止，要求 Claude 继续工作
- UserPromptSubmit: 阻止提示处理，清除原始提示
- **适用**：安全风险、编译错误 ≥5、敏感文件修改

**Reddit 实践**：大多数检查用 exit 1（非阻塞），只有质量门禁用 exit 2

#### 3. 构建检查管道的先记录后检查模式 ⭐

**反模式**（会导致噪声）：
```bash
PostToolUse (Edit) → 立即运行 tsc → 报告错误
# 问题：临时破坏代码时频繁触发，干扰工作流
```

**正确模式**（Reddit 实践）：
```bash
PostToolUse (Edit|Write) → 记录到 edit_log.jsonl（非阻塞）
Stop → 读取日志 → 批量运行构建 → 若错误 ≥5 则阻断（exit 2）
```

**优点**：
- 允许临时代码破坏
- 减少构建次数
- 只在完成时做质量门禁

**结果**：Reddit 团队 6 个月零错误记录

#### 4. JSON 输出控制的新旧字段 ⭐

**新字段**（推荐）：
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "原因说明",
    "additionalContext": "注入到 Claude 的上下文"
  }
}
```

**旧字段**（仍支持但不推荐）：
```json
{
  "decision": "block",
  "reason": "原因"
}
```

#### 5. Dev Docs 三文档系统 ⭐

**三个核心文档**：
1. **plan.md** - 项目整体规划和架构设计
2. **context.md** - 关键上下文和决策记录（< 200 行）
3. **tasks.md** - 任务清单和进度追踪

**自动恢复机制**：
- SessionStart Hook 自动注入这三个文档
- 实现跨会话连续性
- 压缩后仍能继续工作

#### 6. Hooks 最佳实践

**命名规范**：
- `{event}-{功能描述}.{sh|ts}`
- 例如：`post-tool-use-file-edit-tracker.sh`

**脚本要求**：
- Shell 脚本必须有 shebang：`#!/usr/bin/env bash`
- 必须有可执行权限：`chmod +x`
- TypeScript 通过 `npx tsx` 运行

**错误处理**：
- 始终处理 stdin JSON 解析错误
- 提供清晰的错误信息
- 记录日志以便调试

#### 7. skill-rules.json 配置

**文件触发器**：
```json
{
  "skills": {
    "backend-dev-guidelines": {
      "fileTriggers": {
        "pathPatterns": [
          "src/routes/**/*.ts",
          "src/controllers/**/*.ts"
        ]
      }
    }
  }
}
```

**关键词触发器**：
```json
{
  "skills": {
    "backend-dev-guidelines": {
      "keywordTriggers": {
        "keywords": ["api", "backend", "route", "controller"]
      }
    }
  }
}
```

#### 8. build-checker.json 配置

```json
{
  "repos": {
    "/absolute/path/to/your/project": {
      "buildCommand": "npm run build",
      "errorThreshold": 5,
      "timeout": 60000
    }
  }
}
```

**常见构建命令**：
- TypeScript: `"tsc --noEmit"`
- Next.js: `"next build"`
- Python: `"python3 -m py_compile **/*.py"`
- Vite: `"vite build"`

#### 9. 质量门禁策略

**门禁时机**：
- Stop Hook - 当 Claude 想要停止时
- 不是 PostToolUse - 避免频繁触发

**门禁条件**：
- 编译错误数量 ≥ 阈值（默认 5）
- 安全漏洞检测
- 测试覆盖率下降

**门禁行为**：
- Exit Code 2 - 阻断停止
- 清晰的错误报告
- 提供修复建议

---

## 🔧 安装和使用

### 通用安装命令

```bash
# 查看所有 Role
python scripts/roles_manager.py list

# 查看 Role 详情
python scripts/roles_manager.py info <role-name>

# 安装完整 Role
python scripts/roles_manager.py install <role-name> --path /path/to/project

# 选择性安装（只安装 Skills 和 Agents）
python scripts/roles_manager.py install <role-name> \
    --path /path/to/project \
    --components skills,agents

# 预览安装（不执行）
python scripts/roles_manager.py install <role-name> \
    --path /path/to/project \
    --dry-run

# 非交互模式
python scripts/roles_manager.py install <role-name> \
    --path /path/to/project \
    --non-interactive
```

### 安装后步骤

1. **重启 Claude Code** - 加载新组件
2. **配置项目特定设置** - 编辑 build-checker.json、skill-rules.json
3. **自定义 Skills 描述** - 添加项目关键词
4. **测试激活** - 验证 Skills 和 Agents 能正常工作

---

## 📖 相关文档

- **[README.md](../README.md)** - 项目概览和快速开始
- **[QUICK_INSTALL_GUIDE.md](../QUICK_INSTALL_GUIDE.md)** - 详细安装指南
- **[CLAUDE.md](../CLAUDE.md)** - Claude Code 使用指南
- **[ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md)** - 架构设计文档
- **[INSTALLATION_SYSTEM_IMPLEMENTATION.md](INSTALLATION_SYSTEM_IMPLEMENTATION.md)** - 安装系统实施文档

---

## 🤝 贡献

欢迎贡献新的 Role 定义！要添加新 Role：

1. 在 `checklists/roles/` 创建新的 YAML 文件
2. 定义 agents、skills、commands、hooks
3. 更新本文档添加 Role 说明
4. 测试安装流程
5. 提交 Pull Request

---

**版本**: v3.0.0 (2025-11-10)

**更新内容**:
- ✅ 重命名为 CASE_IMPLEMENTATION_SUMMARY.md
- ✅ 新增 6 个通用 Role 的完整文档
- ✅ 保留 Reddit-Case 核心知识点
- ✅ 新增 Role 选择指南和组合安装建议
- ✅ 统一文档结构和格式

**记住：选择适合你团队角色的 Role 集合，快速开始高效开发！** 🚀
