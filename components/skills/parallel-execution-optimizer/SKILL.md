---
name: parallel-execution-optimizer
description: |
  Expert optimizer for maximizing parallel tool execution to achieve 3-5x faster performance.
  Use when multiple tool calls are needed, gathering information from different sources, reading
  multiple files, running multiple searches, or executing independent operations. Automatically
  detects parallelization opportunities and prevents unnecessary sequential execution. Essential
  for information gathering, batch file operations, multiple grep/search tasks, and any scenario
  where operations don't have dependencies.
allowed-tools: Read, Grep, Glob, Bash
---

# Parallel Execution Optimizer

> 并行工具调用优化专家 - 提升 3-5x 性能

**来源**: 整合自 Cursor Agent v1.0 的并行执行策略 + Claude Code 最佳实践

## 🎯 核心功能

### 何时使用此技能

- ✅ **信息收集**：需要从多个文件/目录收集数据
- ✅ **批量操作**：读取多个文件、运行多个搜索
- ✅ **独立任务**：多个操作之间无依赖关系
- ✅ **探索阶段**：需要同时查看多个代码路径
- ✅ **性能优化**：减少等待时间，提升用户体验

### 不适用场景

- ❌ 操作有严格顺序依赖（A 的输出是 B 的输入）
- ❌ 需要基于前一个结果决定下一步行动
- ❌ 修改操作可能相互冲突（如同时编辑同一文件）

---

## 📋 核心原则

### 1️⃣ 默认并行（Default to Parallel）

**黄金法则**: 除非操作**必须**按顺序执行（A 的输出是 B 的必需输入），否则总是并行执行。

```typescript
// ❌ 错误：顺序执行（慢）
await readFile('user.ts');
// 等待...
await readFile('auth.ts');
// 等待...
await readFile('types.ts');

// ✅ 正确：并行执行（快 3x）
[
  readFile('user.ts'),
  readFile('auth.ts'),
  readFile('types.ts')
]
```

**性能对比**:
- 顺序执行: 3 秒 (1秒 × 3)
- 并行执行: 1 秒 (max(1秒, 1秒, 1秒))
- **提升**: 3x 速度

---

### 2️⃣ 提前规划（Plan Upfront）

**策略**: 在执行前先思考需要哪些信息，然后一次性发起所有工具调用。

```markdown
## 错误模式（反应式）
1. 读取 package.json → 看到 "react"
2. 搜索 React 组件 → 找到 Button.tsx
3. 读取 Button.tsx → 看到样式
4. 搜索样式文件 → ...

⏱️ 总时间: 4+ 轮次 = 4+ 秒

## 正确模式（规划式）
思考: 我需要了解前端架构
→ 需要: package.json, 组件结构, 样式系统, 路由配置

并行执行:
- Read package.json
- Grep "export.*Component"
- Glob "**/*.css"
- Codebase_search "routing configuration"

⏱️ 总时间: 1 轮次 = 1 秒
```

---

### 3️⃣ 识别并行机会

#### ✅ 必须并行的场景

| 场景 | 示例 | 并行工具数 |
|------|------|-----------|
| **读取多个文件** | 理解模块关系 | 3-10 |
| **多模式搜索** | 查找导入、使用、定义 | 3-5 |
| **目录遍历** | 不同子目录的结构 | 2-5 |
| **混合搜索** | grep + codebase_search | 2-4 |
| **批量验证** | 检查多个配置文件 | 5-10 |

#### ❌ 不能并行的场景

```python
# 场景1: 输出依赖
result = search("UserService")
# 必须等待，因为需要result来决定下一步
if "auth" in result:
    read_file(extract_path(result))

# 场景2: 条件分支
config = read_config()
# 必须等待，因为后续操作取决于config内容
if config.use_typescript:
    grep("*.ts")
else:
    grep("*.js")

# 场景3: 累积状态
for file in files:
    content = read(file)
    # 每次循环依赖上次结果
    summary += analyze(content)
```

---

## 🔍 实战模式

### 模式 1: 信息收集（Information Gathering）

**场景**: 用户问"这个项目的认证是如何工作的？"

```markdown
## ❌ 顺序方法（慢）
1. Search "authentication"
2. 等待结果...
3. 基于结果，Read auth.ts
4. 等待...
5. 基于内容，Search "login handler"
6. 等待...

⏱️ 6+ 秒（3 轮次）

## ✅ 并行方法（快）
思考: 认证通常涉及 login、session、token、middleware

并行执行所有搜索:
[
  codebase_search("How does user authentication work?"),
  codebase_search("Where is login handled?"),
  grep("session|token|jwt", type="ts"),
  grep("middleware.*auth", type="ts"),
  glob("**/*auth*.ts")
]

⏱️ 2 秒（1 轮次）
```

---

### 模式 2: 多文件读取（Batch File Reading）

**场景**: 需要理解多个相关模块

```typescript
// ❌ 错误：一个接一个
await Read('src/user/user.service.ts');
await Read('src/user/user.controller.ts');
await Read('src/user/user.dto.ts');
await Read('src/user/user.entity.ts');

// ✅ 正确：一次性全部读取
[
  Read('src/user/user.service.ts'),
  Read('src/user/user.controller.ts'),
  Read('src/user/user.dto.ts'),
  Read('src/user/user.entity.ts')
]
```

**最佳实践**:
- 单次并行读取: 5-10 个文件（平衡性能和上下文）
- 文件过多时: 分批并行（每批 5-10 个）

---

### 模式 3: 混合搜索（Hybrid Search）

**场景**: 需要精确匹配 + 语义搜索

```python
# ✅ 同时使用多种搜索工具
[
    # 语义搜索：找到概念和流程
    codebase_search("How does error handling work?"),

    # 精确搜索：找到具体实现
    grep("class.*Error|throw new", output_mode="files_with_matches"),

    # 模式匹配：找到错误处理器
    grep("catch.*error|handleError", type="ts"),

    # 文件模式：找到错误相关文件
    glob("**/*error*.{ts,js}")
]
```

---

### 模式 4: 探索式搜索（Exploratory Search）

**策略**: 使用不同措辞进行多次搜索

```markdown
## 问题: "数据库连接在哪里配置？"

## ✅ 多角度并行搜索
[
  codebase_search("Where is database connection configured?"),
  codebase_search("How to setup database connection?"),
  codebase_search("Database initialization code"),
  grep("createConnection|connect.*database", type="ts"),
  glob("**/database.config.{ts,js}")
]

**原因**:
- 不同开发者使用不同术语（connection vs pool vs client）
- 配置可能在多个文件中（config, env, bootstrap）
- 一次性覆盖所有可能性
```

---

## ⚖️ 顺序 vs 并行决策树

```
需要执行多个操作？
        ↓
    【决策点1】
操作之间有依赖吗？
    ↙        ↘
  有          无
   ↓           ↓
【决策点2】   ✅ 并行执行
是否必须知道
A的结果才能
执行B？
  ↙    ↘
 是     否
  ↓      ↓
顺序    ✅ 并行
执行    执行
```

### 决策示例

| 操作组合 | 是否并行？ | 原因 |
|---------|----------|------|
| 读取 user.ts + auth.ts | ✅ 是 | 无依赖 |
| 搜索 "API" + 读取搜索结果文件 | ❌ 否 | 需要搜索结果的文件路径 |
| grep 导入 + grep 使用 + grep 定义 | ✅ 是 | 三者独立 |
| 读取配置 + 基于配置决定操作 | ❌ 否 | 后续依赖配置内容 |
| 5 个不同目录的 list_dir | ✅ 是 | 目录之间独立 |

---

## 🛠️ 工具特定优化

### Read 工具

```bash
# ✅ 批量并行读取
[
  Read('src/components/Header.tsx'),
  Read('src/components/Footer.tsx'),
  Read('src/components/Sidebar.tsx'),
  Read('src/styles/theme.ts'),
  Read('src/config/app.config.ts')
]

# 推荐批次大小: 5-10 个文件
```

---

### Grep 工具

```python
# ✅ 多模式并行搜索
[
    # 搜索导入语句
    grep("import.*UserService", type="ts"),

    # 搜索类定义
    grep("class UserService", type="ts"),

    # 搜索使用位置
    grep("new UserService|UserService\.", type="ts")
]

# 注意: 每个 grep 是独立的正则表达式匹配
```

---

### Codebase Search 工具

```typescript
// ✅ 分解复杂问题为多个简单查询
[
  codebase_search("What is UserService?"),
  codebase_search("How does UserService work?"),
  codebase_search("Where is UserService used?")
]

// ❌ 避免: 单个查询包含多个问题
codebase_search("What is UserService? How does it work? Where is it used?")
```

---

### Bash 工具

```bash
# ✅ 独立命令并行执行
[
  Bash("git status"),
  Bash("git diff"),
  Bash("git log -5 --oneline")
]

# ❌ 有依赖关系的命令必须顺序执行
Bash("cd backend && npm install")  # cd 影响后续命令，必须用 &&
```

---

## 📊 性能对比

### 真实案例 1: 理解认证流程

```
任务: 分析项目的认证实现

顺序执行:
1. Search "authentication"     → 1.0s
2. Read auth.service.ts        → 0.8s
3. Search "JWT"                → 1.0s
4. Read jwt.util.ts            → 0.8s
5. Grep middleware             → 1.0s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总计: 4.6 秒

并行执行:
[
  Search "authentication",
  Search "JWT token handling",
  Grep "middleware.*auth",
  Glob "**/*auth*.ts"
]                              → 1.2s
基于结果读取 3 个文件并行        → 0.8s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总计: 2.0 秒

提升: 2.3x (节省 2.6 秒)
```

### 真实案例 2: 批量文件分析

```
任务: 读取和分析 8 个相关组件

顺序执行:
8 个文件 × 0.7秒 = 5.6 秒

并行执行:
8 个文件并行 = 0.9 秒

提升: 6.2x (节省 4.7 秒)
```

---

## ⚡ 最佳实践总结

### DO（推荐）

1. **默认并行**: 没有明确依赖就并行
2. **提前规划**: 思考清楚需要什么，一次性发起
3. **批量操作**: 5-10 个文件为一批
4. **多角度搜索**: 同一问题用不同措辞搜索
5. **混合工具**: grep + codebase_search + glob 组合

### DON'T（避免）

1. **反应式执行**: 看到一个结果再决定下一步
2. **过度谨慎**: "也许我需要先看看结果再说"
3. **单次单操作**: 一次只执行一个工具
4. **忽视机会**: 明明可以并行却顺序执行
5. **过度并行**: 超过 10 个工具调用（分批）

---

## 🎓 训练检查清单

### 在执行工具调用前，问自己：

- [ ] 我需要执行多个操作吗？
- [ ] 这些操作之间有依赖关系吗？
- [ ] 我能提前规划所有需要的操作吗？
- [ ] 是否可以使用不同措辞进行多次搜索？
- [ ] 是否可以混合使用多种搜索工具？

### 执行后自我评估：

- [ ] 是否有本可并行但顺序执行的操作？
- [ ] 是否遗漏了可以同时收集的信息？
- [ ] 下次如何改进并行策略？

---

## 🔗 相关资源

### 内部资源
- [工具调用模式](resources/tool-calling-patterns.md) - 详细的工具调用示例
- [性能基准测试](resources/performance-benchmarks.md) - 各种场景的性能数据

### 外部参考
- Cursor Agent v1.0: `<maximize_parallel_tool_calls>`
- Claude Code 文档: Tool calling best practices

---

## 📝 实施指南

### 步骤 1: 识别机会

```markdown
用户请求 → 分析需要什么信息 → 列出所有工具调用
```

### 步骤 2: 检查依赖

```markdown
工具调用列表 → 标记依赖关系 → 分组（独立/依赖）
```

### 步骤 3: 并行执行

```markdown
独立组 → 单次并行执行
依赖组 → 按批次顺序执行，每批内部并行
```

---

**技能版本**: v1.0
**最后更新**: 2025-11-09
**作者**: Claude Code Prompt Engineer
**基于**: Cursor Agent v1.0 并行执行策略
