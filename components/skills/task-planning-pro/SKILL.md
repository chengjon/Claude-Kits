---
name: task-planning-pro
description: |
  Expert task planning and progress tracking using TodoWrite tool. Use when breaking down complex tasks, managing multi-step implementations, tracking progress, or coordinating parallel workflows. Ideal for feature development, refactoring projects, bug investigations, and complex system changes. Specializes in task decomposition, dependency management, and real-time progress updates.
allowed-tools: TodoWrite, Read, Grep, Glob, Bash
---

# Task Planning Pro

> 专业任务规划与进度跟踪 - TodoWrite 工具完全指南

**来源**: Claude Code + Cursor 任务管理最佳实践

## 🎯 核心功能

### 何时使用此技能

- ✅ **复杂任务分解** - 将大型任务拆分为可执行的原子步骤
- ✅ **进度跟踪** - 实时更新任务状态，给用户可见性
- ✅ **多步骤实施** - 协调需要 3+ 步骤的开发任务
- ✅ **并行工作流** - 管理可并行执行的独立任务
- ✅ **质量门控** - 确保每个步骤完成后再进行下一步
- ✅ **迭代开发** - 在长对话中保持任务上下文

### 不适用场景

- ❌ 单步骤简单任务（如读取一个文件）
- ❌ 纯信息查询（无需执行步骤）
- ❌ 已经在执行中的任务（避免重复创建）

---

## 📋 TodoWrite 工具核心

### 工具结构

```typescript
TodoWrite({
  todos: [
    {
      content: "命令式描述（做什么）",        // 必需
      status: "pending|in_progress|completed",  // 必需
      activeForm: "进行时描述（正在做什么）"   // 必需
    }
  ]
})
```

### 三种任务状态

| 状态 | 含义 | 使用场景 | 规则 |
|------|------|----------|------|
| **pending** | 待执行 | 任务已规划，尚未开始 | 可以有多个 |
| **in_progress** | 执行中 | 正在处理的任务 | **同时只能有 1 个** |
| **completed** | 已完成 | 任务成功完成 | 完成后立即标记 |

### 两种任务描述形式

**关键原则**: 每个任务必须同时提供两种形式

```yaml
✅ 正确示例:
content: "创建用户认证 API"          # 命令式（做什么）
activeForm: "正在创建用户认证 API"   # 进行时（正在做什么）

content: "运行测试套件"
activeForm: "正在运行测试套件"

content: "修复登录页面样式问题"
activeForm: "正在修复登录页面样式"

❌ 错误示例:
content: "认证 API"                  # 不清晰
activeForm: "认证"                   # 不完整

content: "处理用户相关的事情"         # 过于模糊
activeForm: "正在处理"               # 缺少上下文
```

---

## 🔍 任务分解策略

**详细指南**: [任务分解模式](resources/task-breakdown-patterns.md)

### 快速原则

#### SMART 任务定义

每个任务应该是：
- **S**pecific（具体的）- 明确做什么
- **M**easurable（可衡量的）- 能判断是否完成
- **A**chievable（可实现的）- 单次执行可完成
- **R**elevant（相关的）- 与总目标直接相关
- **T**ime-bound（有时限的）- 明确何时完成

#### 分解层次

```
复杂任务
    ↓
【第一层】按功能模块（2-4个模块）
    ↓
【第二层】按实施步骤（每模块 3-5步）
    ↓
【第三层】按文件/函数（可选，精细化）
```

#### 任务粒度指南

```markdown
✅ 合适粒度（1-3分钟完成）:
- "创建 User model（src/models/user.ts）"
- "实现登录 API（POST /auth/login）"
- "添加密码哈希功能（bcrypt）"

❌ 粒度过大:
- "实现整个认证系统"

❌ 粒度过小:
- "导入 bcrypt 库"
- "创建 hashPassword 函数"
- "添加 return 语句"
```

---

## ⚡ 进度跟踪最佳实践

**详细指南**: [进度跟踪模式](resources/progress-tracking-patterns.md)

### 核心规则

#### 规则 1: 立即更新（No Batching）

```markdown
❌ 错误做法（批量更新）:
[完成任务 1]
[完成任务 2]
[完成任务 3]
[一次性标记所有为 completed]

✅ 正确做法（实时更新）:
[标记任务 1 为 in_progress]
[完成任务 1]
[标记任务 1 为 completed]
[标记任务 2 为 in_progress]
...
```

#### 规则 2: 单一 in_progress

```markdown
✅ 正确：只有一个 in_progress
- [completed] 创建 API
- [in_progress] 写测试      ← 只有这个
- [pending] 更新文档

❌ 错误：多个任务同时 in_progress
- [in_progress] 创建 API
- [in_progress] 写测试
- [in_progress] 更新文档
```

#### 规则 3: 完成后才能标记为 completed

```markdown
✅ 完全完成才标记:
✓ 代码写完
✓ 测试通过
✓ 无编译错误
→ 标记为 completed

❌ 不完整不能标记:
✓ 代码写完
✗ 测试失败        ← 有未解决问题
→ 保持 in_progress，创建新任务解决问题
```

### 状态转换流程

```
[创建任务] → pending

[开始工作] → in_progress

[工作完成] → completed
```

---

## 🎓 实战场景

**完整场景集**: [实战场景](resources/practical-scenarios.md)

### 场景概览

#### 场景 1: 新功能开发
**示例**: "添加用户注册功能"

**流程**:
1. 澄清需求（注册方式、验证、字段）
2. 创建任务列表（数据模型 → API → 密码处理 → 前端表单 → 测试）
3. 逐步执行，实时更新状态

#### 场景 2: Bug 修复
**示例**: "登录页面在移动端显示错位"

**流程**:
1. 复现问题
2. 定位根本原因
3. 修复样式
4. 多设备验证

#### 场景 3: 大型重构
**示例**: "重构 API 层使用 async/await"

**策略**: 分阶段（调研 → 分析 → 执行 → 验证），混合并行和顺序任务

---

## 🚨 常见陷阱与解决方案

**完整指南**: [高级技巧与陷阱](resources/advanced-tips.md)

### 快速参考

#### 陷阱 1: 任务粒度不当

```markdown
❌ 过大: "实现整个认证系统"
❌ 过小: "导入 bcrypt 库"
✅ 合适: "实现密码哈希功能（bcrypt）"
```

#### 陷阱 2: 模糊描述

```markdown
❌ 模糊: "处理用户相关的事情"
✅ 清晰: "实现用户注册 API（POST /auth/register）"
```

#### 陷阱 3: 忘记更新状态

```markdown
❌ 延迟更新 → 用户看不到实时进度
✅ 立即更新 → 完成后立刻标记 completed
```

---

## 📊 决策树

### 何时创建 Todo 列表？

```
收到用户请求
    ↓
需要多少步骤？
    ├─ 1步？ → 直接执行，无需 TodoWrite
    ├─ 2步？ → 简单任务，可选 TodoWrite
    └─ 3+步？→ 必须使用 TodoWrite
```

### 任务粒度决策

```
1. 能否在 1-3 分钟内完成？
   ├─ 是 → ✅ 粒度合适
   └─ 否 → ❌ 需要进一步拆分

2. 完成标准是否明确？
   ├─ 是 → ✅ 描述清晰
   └─ 否 → ❌ 需要细化描述

3. 是否是原子操作？
   ├─ 是 → ✅ 不可再分
   └─ 否 → ❌ 继续分解
```

---

## 💡 高级技巧

### 技巧 1: 动态调整任务列表

执行中发现新问题时，立即调整任务列表，添加新任务处理问题。

### 技巧 2: 任务分组

使用描述性前缀标识阶段：
- 【调研】搜索现有代码
- 【设计】设计接口
- 【实施】编写代码
- 【验证】运行测试

### 技巧 3: 依赖标注

在任务描述中明确依赖关系：
- "实现 API 端点（依赖：schema 完成）"

---

## 🔗 相关资源

### 内部资源

- **[任务分解模式](resources/task-breakdown-patterns.md)** (63 行) - 详细的拆分策略
- **[进度跟踪模式](resources/progress-tracking-patterns.md)** - 状态管理最佳实践
- **[实战场景](resources/practical-scenarios.md)** (137 行) - 20+ 真实场景示例
- **[高级技巧与陷阱](resources/advanced-tips.md)** (168 行) - 常见问题和解决方案

### 相关 Skills

- **conversational-coding-assistant** - 对话式交互，与用户澄清需求
- **code-style-enforcer** - 代码质量门控
- **parallel-execution-optimizer** - 识别并行机会

---

## 📝 快速参考

### TodoWrite 模板

```typescript
TodoWrite({
  todos: [
    {
      content: "动词 + 对象 + （位置/细节）",
      status: "pending|in_progress|completed",
      activeForm: "正在 + 动词 + 对象"
    }
  ]
})
```

### 状态更新时机

```markdown
✅ 何时更新为 in_progress:
- 准备开始执行该任务时
- 已读取必要文件/信息后
- 明确下一步操作时

✅ 何时更新为 completed:
- 任务完全完成（代码+测试+无错误）
- 用户确认满意
- 达到预期目标

❌ 不应标记为 completed:
- 测试失败
- 有编译错误
- 部分完成
- 遇到阻塞问题
```

### 任务命名规范

```markdown
格式: 动词 + 对象 + （上下文）

✅ 优秀命名:
- "创建 User 数据模型（users.ts）"
- "实现登录 API（POST /auth/login）"
- "修复 Safari 样式问题（header.css:45-67）"
- "优化数据库查询（添加索引到 email 字段）"

❌ 不清晰命名:
- "用户功能"
- "处理登录"
- "修复 bug"
```

---

**技能版本**: v1.0
**最后更新**: 2025-11-10
**作者**: Claude Code Prompt Engineer
**基于**: Claude Code TodoWrite + Cursor 任务管理
