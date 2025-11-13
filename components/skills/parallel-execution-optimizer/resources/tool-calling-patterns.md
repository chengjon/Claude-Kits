# 工具调用模式详解

> 并行执行的具体实现模式和示例

## 目录

- [Read 工具模式](#read-工具模式)
- [Grep 工具模式](#grep-工具模式)
- [Codebase Search 模式](#codebase-search-模式)
- [混合工具模式](#混合工具模式)
- [Bash 工具模式](#bash-工具模式)

---

## Read 工具模式

### 模式 1: 模块完整读取

**场景**: 理解一个完整的功能模块

```typescript
// 用户: "分析用户管理模块的实现"

// ✅ 并行读取所有相关文件
[
  Read('src/modules/user/user.controller.ts'),
  Read('src/modules/user/user.service.ts'),
  Read('src/modules/user/user.repository.ts'),
  Read('src/modules/user/user.entity.ts'),
  Read('src/modules/user/dto/create-user.dto.ts'),
  Read('src/modules/user/dto/update-user.dto.ts')
]

// 一次性获取完整上下文，无需等待
```

### 模式 2: 跨层读取

**场景**: 追踪请求从前端到后端的完整流程

```python
# 用户: "用户登录请求是如何处理的？"

[
    # 前端层
    Read('src/components/LoginForm.tsx'),
    Read('src/services/auth.service.ts'),

    # API层
    Read('src/api/routes/auth.routes.ts'),
    Read('src/api/controllers/auth.controller.ts'),

    # 业务层
    Read('src/services/auth.service.ts'),
    Read('src/middleware/jwt.middleware.ts'),

    # 数据层
    Read('src/repositories/user.repository.ts')
]
```

### 模式 3: 配置文件批量读取

```javascript
// 用户: "检查项目配置"

[
  Read('package.json'),
  Read('tsconfig.json'),
  Read('.eslintrc.js'),
  Read('.prettierrc'),
  Read('jest.config.js'),
  Read('.env.example')
]
```

---

## Grep 工具模式

### 模式 1: 三角定位（定义-使用-导入）

**策略**: 从三个维度全面了解一个符号

```python
# 用户: "UserService 在项目中如何使用？"

[
    # 1. 找定义
    grep("class UserService|interface UserService", type="ts"),

    # 2. 找导入
    grep("import.*UserService", type="ts"),

    # 3. 找使用
    grep("UserService\.|new UserService", type="ts")
]

# 一次性获得完整图景
```

### 模式 2: 多模式匹配

**场景**: 查找一个功能的不同实现方式

```typescript
// 用户: "如何处理异步错误？"

[
  // 不同的错误处理方式
  grep("try.*catch", type="ts", output_mode="files_with_matches"),
  grep("\.catch\(", type="ts", output_mode="files_with_matches"),
  grep("Promise.*reject", type="ts", output_mode="files_with_matches"),
  grep("throw new.*Error", type="ts", output_mode="files_with_matches")
]
```

### 模式 3: 分层搜索

**场景**: 在不同层次查找相关代码

```python
[
    # 控制器层
    grep("@Controller|@Get|@Post", path="src/controllers"),

    # 服务层
    grep("@Injectable|@Service", path="src/services"),

    # 数据层
    grep("@Entity|@Repository", path="src/entities")
]
```

---

## Codebase Search 模式

### 模式 1: 问题分解

**策略**: 将大问题分解为多个小问题，并行搜索

```markdown
# 用户: "这个项目的数据库架构是什么？"

# ❌ 单个笼统查询
codebase_search("What is the database architecture?")

# ✅ 分解为具体问题
[
  codebase_search("What database is being used?"),
  codebase_search("How are database entities defined?"),
  codebase_search("How are database migrations handled?"),
  codebase_search("Where are database queries executed?")
]
```

### 模式 2: 多措辞搜索

**策略**: 同一问题用不同表述方式，避免遗漏

```typescript
// 用户: "认证中间件在哪里？"

[
  codebase_search("Where is authentication middleware?"),
  codebase_search("How to verify user tokens?"),
  codebase_search("Request authentication handling"),
  codebase_search("JWT validation code")
]

// 不同措辞可能匹配不同代码片段
```

### 模式 3: 深度 + 广度

**策略**: 结合高层概念和具体实现

```python
[
    # 高层概念
    codebase_search("How does the payment system work?"),

    # 具体实现
    codebase_search("Where is payment processing code?"),
    codebase_search("How to create payment intent?"),
    codebase_search("Payment webhook handling")
]
```

---

## 混合工具模式

### 模式 1: 三工具组合

**策略**: codebase_search + grep + glob 全方位覆盖

```javascript
// 用户: "分析测试覆盖情况"

[
  // 语义搜索: 找测试策略
  codebase_search("How are tests organized?"),

  // 精确匹配: 找测试文件
  grep("describe\(|it\(|test\(", type="ts", output_mode="files_with_matches"),

  // 模式匹配: 找所有测试文件
  glob("**/*.{test,spec}.{ts,js}")
]
```

### 模式 2: 先广后精

**策略**: 先用 glob 找文件，再用 grep 找内容

```python
[
    # 第一层: 找到所有可能的文件
    glob("**/auth*.{ts,js}"),
    glob("**/login*.{ts,js}"),

    # 第二层: 在这些文件中找具体实现
    grep("login|authenticate|verify", path="src/auth"),
    grep("jwt|token|session", path="src/auth")
]
```

### 模式 3: 精确 + 模糊

**策略**: grep 精确匹配 + codebase_search 语义理解

```typescript
[
  // 精确: 找到所有 API 端点定义
  grep("@Get|@Post|@Put|@Delete", type="ts"),

  // 模糊: 理解 API 如何组织
  codebase_search("How are API routes structured?"),
  codebase_search("What is the API naming convention?")
]
```

---

## Bash 工具模式

### 模式 1: Git 信息收集

```bash
# 用户: "查看项目状态"

[
  Bash("git status"),
  Bash("git log -5 --oneline"),
  Bash("git diff --stat"),
  Bash("git branch -a")
]

# 所有命令互相独立，可以并行
```

### 模式 2: 依赖和构建检查

```bash
[
  Bash("npm list --depth=0"),
  Bash("npm outdated"),
  Bash("npm run | grep -E '^  '"),  # 列出所有scripts
  Bash("du -sh node_modules")        # 检查大小
]
```

### 模式 3: 环境检查

```bash
[
  Bash("node --version"),
  Bash("npm --version"),
  Bash("git --version"),
  Bash("python --version")
]
```

⚠️ **注意**: 涉及状态改变或依赖关系的命令必须顺序执行：

```bash
# ❌ 不能并行（有依赖）
Bash("cd backend && npm install")

# ✅ 必须顺序或使用 &&
Bash("cd backend && npm install && npm test")
```

---

## 高级模式

### 模式 1: 分批并行

**场景**: 需要读取 20+ 个文件

```python
# 策略: 分为多批，每批 5-10 个并行

# 第一批: 核心文件
batch1 = [
    Read('file1.ts'),
    Read('file2.ts'),
    ...
    Read('file8.ts')
]

# 基于第一批结果，决定第二批
batch2 = [
    Read('related1.ts'),
    Read('related2.ts'),
    ...
]
```

### 模式 2: 条件并行

**策略**: 部分并行 + 部分顺序

```typescript
// 步骤 1: 并行收集元信息
[
  Read('package.json'),
  Read('tsconfig.json')
]

// 步骤 2: 基于元信息，决定读取哪些源文件（并行）
if (usesReact) {
  [
    Read('src/App.tsx'),
    Read('src/components/**'),
    ...
  ]
}
```

### 模式 3: 瀑布式并行

**策略**: 每一层内部并行，层与层之间顺序

```markdown
层1 (并行): 读取配置文件
   ↓
层2 (并行): 基于配置，读取源文件
   ↓
层3 (并行): 基于源文件，搜索依赖
```

---

## 性能优化技巧

### 1. 合理批次大小

```python
# ❌ 过小批次（浪费并行机会）
Read('file1.ts')
Read('file2.ts')
Read('file3.ts')

# ❌ 过大批次（超出上下文）
[Read(f) for f in all_50_files]  # 一次性 50 个

# ✅ 合理批次（5-10 个）
[
  Read('file1.ts'),
  Read('file2.ts'),
  ...
  Read('file8.ts')
]
```

### 2. 避免重复读取

```typescript
// ❌ 重复读取
Read('user.service.ts')
// ... 一些操作
Read('user.service.ts')  // 再次读取

// ✅ 一次读取，保存在上下文中
Read('user.service.ts')
// 后续直接引用，无需再次读取
```

### 3. 精确匹配优先

```python
# 如果知道精确符号，优先使用 grep
# ✅ 快速
grep("class UserService", type="ts")

# ⚠️ 较慢（当精确符号已知时）
codebase_search("UserService class definition")
```

---

## 常见反模式

### 反模式 1: 过度谨慎

```markdown
# ❌ 错误思维
"我先搜索一下，看看结果再决定下一步"

# ✅ 正确思维
"我需要A、B、C三个信息，现在就全部获取"
```

### 反模式 2: 忘记并行机会

```python
# ❌ 顺序执行明显独立的操作
grep("import.*React")
# 等待...
grep("export.*Component")
# 等待...
grep("useState|useEffect")

# ✅ 并行执行
[
  grep("import.*React"),
  grep("export.*Component"),
  grep("useState|useEffect")
]
```

### 反模式 3: 错误的依赖假设

```typescript
// ❌ 错误假设: 认为需要顺序
Read('package.json')
Read('tsconfig.json')
Read('README.md')

// ✅ 实际: 三者完全独立，应该并行
[
  Read('package.json'),
  Read('tsconfig.json'),
  Read('README.md')
]
```

---

## 检查清单

### 执行工具调用前，确认：

- [ ] 我是否有 2+ 个独立操作？
- [ ] 这些操作真的有依赖关系吗？
- [ ] 我能否提前规划所有需要的信息？
- [ ] 是否可以用多个 grep 代替单个 codebase_search？
- [ ] 读取文件时，是否可以批量并行？

---

**更新日期**: 2025-11-09
**版本**: v1.0
