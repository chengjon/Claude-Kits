---
name: code-style-enforcer
description: |
  Expert code style and quality enforcer based on Clean Code principles.
  Use when reviewing code quality, checking naming conventions, analyzing
  control flow, or enforcing code style standards. Ideal for pre-commit
  reviews, refactoring guidance, code quality audits, and ensuring team
  coding standards. Specializes in identifying unclear variable names,
  deep nesting, missing error handling, and code smell detection.
allowed-tools: Read, Grep, Glob, Bash
---

# Code Style Enforcer

> 基于 Clean Code 原则的代码风格和质量执行专家

**来源**: 整合自 Cursor Agent 的代码风格指南 + 多工具最佳实践

## 🎯 核心功能

### 何时使用此技能

- ✅ **代码审查**：评估代码质量和可维护性
- ✅ **重构指导**：识别需要改进的代码模式
- ✅ **团队规范**：确保代码符合团队标准
- ✅ **预提交检查**：在提交前发现潜在问题
- ✅ **代码清理**：系统化改善代码库质量

### 不适用场景

- ❌ 算法优化（使用 `performance-optimizer`）
- ❌ 安全漏洞扫描（使用 `security-auditor`）
- ❌ 架构设计评审（使用 `architecture-reviewer`）

---

## 📋 检查清单

### 1️⃣ 命名规范

#### ✅ 必须遵守

```python
# ❌ 错误示例
def genYmdStr():
    n = 0
    for key, value in map:
        pass

# ✅ 正确示例
def generateDateString():
    numSuccessfulRequests = 0
    for userId, user in userIdToUser.items():
        pass
```

**规则**：
- 避免 1-2 字符的变量名
- 函数用动词/动词短语
- 变量用名词/名词短语
- 优先使用完整单词而非缩写
- 变量名应足够描述性，通常不需要注释

**更多细节**: 参见 [resources/naming-conventions.md](resources/naming-conventions.md)

---

### 2️⃣ 控制流

#### ✅ 推荐模式

```typescript
// ❌ 深度嵌套
function processUser(user) {
    if (user) {
        if (user.isActive) {
            if (user.hasPermission) {
                // 业务逻辑
            }
        }
    }
}

// ✅ Guard Clauses（早返回）
function processUser(user) {
    if (!user) return;
    if (!user.isActive) return;
    if (!user.hasPermission) return;

    // 业务逻辑
}
```

**规则**：
- 使用 guard clauses 和早返回
- 优先处理错误和边界情况
- 避免嵌套超过 2-3 层
- 复杂条件提取为变量

---

### 3️⃣ 错误处理

#### ❌ 禁止的模式

```javascript
// ❌ 空catch块
try {
    riskyOperation();
} catch (error) {
    // 什么都不做
}

// ❌ 捕获但不处理
try {
    riskyOperation();
} catch (error) {
    console.log(error); // 仅打印
}
```

#### ✅ 正确的处理

```javascript
// ✅ 有意义的错误处理
try {
    riskyOperation();
} catch (error) {
    logger.error('Failed to process user data', { error, userId });
    throw new ProcessingError('User data processing failed', { cause: error });
}
```

**规则**：
- 不要捕获错误却不处理
- 避免过度使用 try/catch
- 错误信息应包含上下文
- 考虑使用 Result 类型（函数式语言）

---

### 4️⃣ 类型注解（静态类型语言）

#### ✅ 何时添加类型

```typescript
// ✅ 函数签名必须注解
function fetchUserData(userId: string): Promise<User> {
    // ...
}

// ✅ 公共API必须注解
export interface UserService {
    getUser(id: string): Promise<User>;
    updateUser(id: string, data: Partial<User>): Promise<void>;
}

// ❌ 不要注解显而易见的类型
const count = 10; // 不需要: const count: number = 10
const users = ['Alice', 'Bob']; // 类型自动推断
```

**规则**：
- 函数签名和公共API明确注解
- 避免注解能轻易推断的变量
- 不使用 `any`，考虑 `unknown`
- 避免不安全的类型转换

**TypeScript专题**: 参见 [resources/typescript-patterns.md](resources/typescript-patterns.md)

---

### 5️⃣ 注释规范

#### ✅ 何时添加注释

```python
# ✅ 解释复杂的业务逻辑
# 我们使用指数退避策略是因为API有速率限制
# 基础延迟 = 2^(重试次数) * 100ms
def retry_with_backoff(func, max_retries=3):
    pass

# ✅ 说明"为什么"而非"是什么"
# 需要深拷贝以避免修改原始数据结构
data_copy = copy.deepcopy(data)
```

#### ❌ 避免的注释

```python
# ❌ 琐碎的注释
i = 0  # 初始化计数器

# ❌ TODO注释（应该直接实现或创建Issue）
# TODO: 优化这个循环

# ❌ 内联注释（使用代码上方的注释或文档字符串）
result = process_data(input)  # 处理数据
```

**规则**：
- 不添加琐碎或显而易见的注释
- 解释"为什么"而非"如何"
- 避免内联注释，使用上方注释或文档字符串
- 不要留TODO注释，直接实现或开Issue
- 复杂逻辑必须注释

---

### 6️⃣ 代码格式

#### ✅ 格式规范

```javascript
// ✅ 匹配现有代码风格
// 如果项目使用2空格缩进，就用2空格
// 如果使用分号，就加分号

// ✅ 多行优于复杂的单行
const userPermissions = userRoles
    .filter(role => role.isActive)
    .map(role => role.permissions)
    .flat();

// ❌ 避免复杂的三元运算符
const result = condition1 ? value1 : condition2 ? value2 : condition3 ? value3 : default;

// ✅ 改为if-else或对象映射
```

**规则**：
- 匹配现有代码风格和格式
- 优先多行而非复杂单行
- 长行要换行
- 不要重新格式化无关代码

---

## 🔍 审查流程

### 标准审查步骤

```markdown
1. 快速扫描（30秒）
   - 文件结构是否清晰？
   - 函数/类是否过长？
   - 是否有明显的代码异味？

2. 命名检查（1分钟）
   - 变量名是否有意义？
   - 是否有1-2字符的变量？
   - 函数名是否是动词短语？

3. 控制流分析（2分钟）
   - 嵌套深度是否合理？
   - 是否使用了早返回？
   - 错误处理是否完善？

4. 类型和注释（1分钟）
   - 类型注解是否完整？
   - 注释是否有价值？
   - 是否有TODO注释？

5. 整体评估（1分钟）
   - 代码是否易于理解？
   - 是否易于测试？
   - 是否遵循DRY原则？
```

---

## 📊 评分标准

### 代码质量评分

| 维度 | 优秀 (9-10分) | 良好 (7-8分) | 需改进 (4-6分) | 差 (1-3分) |
|------|------------|-----------|-------------|----------|
| **命名** | 所有命名清晰有意义 | 大部分命名良好 | 部分命名不清 | 大量缩写和无意义名称 |
| **控制流** | Guard clauses，最多2层嵌套 | 最多3层嵌套 | 嵌套4-5层 | 嵌套5层以上 |
| **错误处理** | 完善的错误处理和日志 | 基本错误处理 | 部分错误未处理 | 无错误处理或空catch |
| **注释** | 仅解释复杂逻辑 | 有用的注释 | 部分琐碎注释 | 过多或无用注释 |
| **格式** | 统一风格 | 基本统一 | 部分不一致 | 格式混乱 |

**总分计算**: 各维度平均分

---

## 🛠️ 工具集成

### 推荐使用的工具

1. **Linter**: ESLint, Pylint, RuboCop
   ```bash
   # JavaScript/TypeScript
   npm run lint

   # Python
   pylint src/

   # 自动修复
   eslint --fix src/
   ```

2. **Formatter**: Prettier, Black, rustfmt
   ```bash
   # Prettier
   npx prettier --write .

   # Black
   black .
   ```

3. **Type Checker**: TypeScript, mypy, Flow
   ```bash
   # TypeScript
   npx tsc --noEmit

   # Python
   mypy src/
   ```

---

## 🎓 最佳实践

### 代码审查原则

1. **专注重要问题**
   - 优先指出逻辑错误和安全问题
   - 其次关注可维护性和可读性
   - 格式问题用自动化工具解决

2. **建设性反馈**
   - 解释"为什么"需要改进
   - 提供具体的改进建议
   - 认可好的代码

3. **一致性优先**
   - 遵循项目现有风格
   - 不要为了个人偏好而要求修改
   - 在团队内达成共识

---

## 📝 输出格式

### 审查报告模板

```markdown
## 代码审查报告

**文件**: src/services/user-service.ts
**总体评分**: 7.5/10

### ✅ 优点
- 函数分解合理，单一职责原则
- 错误处理完善
- TypeScript类型定义清晰

### ⚠️ 需要改进

#### 1. 命名不清晰 (行 42)
问题: 变量 `n` 含义不明
建议: 改为 `notificationCount` 或 `unreadMessagesCount`

#### 2. 嵌套过深 (行 78-95)
问题: 4层if嵌套，难以理解
建议: 使用早返回模式重构

#### 3. 空catch块 (行 123)
问题: 捕获错误但未处理
建议: 添加日志或向上抛出

### 📋 行动项
- [ ] 重命名变量 `n`
- [ ] 重构 `processUserData` 函数，减少嵌套
- [ ] 添加错误处理逻辑
```

---

## 🔗 相关资源

### 内部资源
- [命名规范详解](resources/naming-conventions.md)
- [TypeScript模式](resources/typescript-patterns.md)
- [重构技巧](resources/refactoring-patterns.md)

### 外部资源
- 《Clean Code》by Robert C. Martin
- 《Refactoring》by Martin Fowler
- [Google Style Guides](https://google.github.io/styleguide/)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)

---

## 🚀 快速开始

### 使用示例

```markdown
用户: "审查这个文件的代码质量"

助手:
1. [读取文件内容]
2. [应用 code-style-enforcer 检查清单]
3. [生成审查报告]

报告内容:
- 总体评分
- 具体问题列表（带行号）
- 改进建议
- 优点总结
```

---

**技能版本**: v1.0
**最后更新**: 2025-11-09
**作者**: Claude Code Prompt Engineer
**基于**: Cursor Agent代码风格指南 + Clean Code原则
