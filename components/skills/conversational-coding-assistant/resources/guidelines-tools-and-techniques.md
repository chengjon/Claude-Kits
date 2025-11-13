## 工具使用策略

### AskUserQuestion 工具

#### 何时使用

✅ **应该使用**:
- 需求有多种合理解释
- 需要技术决策（框架、工具、方法）
- 缺少关键实施细节

❌ **不应该使用**:
- 显而易见的问题
- 可以通过读取代码得出答案
- 只有一种合理方案

#### 好的问题设计

```yaml
✅ 优秀设计:
questions:
  - question: "使用哪种认证方式？"
    header: "认证"
    multiSelect: false
    options:
      - label: "JWT"
        description: "无状态，适合 API，需要前端存储 token"
      - label: "Session"
        description: "有状态，服务器存储，适合传统 Web 应用"
      - label: "OAuth2"
        description: "第三方登录，实施复杂但用户体验好"

❌ 不足设计:
questions:
  - question: "用什么？"
    options:
      - label: "A"
      - label: "B"
```

### Read 工具策略

#### 并行读取

```markdown
✅ 正确：并行
[
  Read('package.json'),
  Read('tsconfig.json'),
  Read('README.md')
]

❌ 错误：顺序
Read('package.json')
Read('tsconfig.json')
Read('README.md')
```

#### 有目的性读取

```markdown
✅ 正确：明确目的
Q: 这个项目使用什么测试框架？
[
  Read('package.json'),        # 检查 devDependencies
  Read('jest.config.js'),       # 检查配置
  Glob('**/*.test.{ts,js}')    # 检查测试文件
]

❌ 错误：盲目读取
[读取所有文件]
```

---

## 高级技巧

### 技巧 1: 渐进式详细

```markdown
策略：
第 1 层（默认）: 一句话回答
    ↓
[用户追问]
    ↓
第 2 层: 简要步骤
    ↓
[用户深入]
    ↓
第 3 层: 详细指导

实例：

第 1 层:
Q: 如何优化查询？
A: 添加索引

第 2 层:
Q: 具体怎么做？
A: 1. 分析慢查询
   2. 识别常用字段
   3. CREATE INDEX

第 3 层:
Q: 给个完整示例
A: [完整 SQL + 解释 + 性能对比]
```

### 技巧 2: 上下文记忆

```markdown
✅ 好的上下文使用:

轮次 1:
Q: 这个项目用什么数据库？
A: [检查配置] PostgreSQL 13.4

轮次 2:
Q: 如何备份？
A: [记住是 PostgreSQL，直接给答案]
   pg_dump dbname > backup.sql

❌ 差的上下文使用:

轮次 1:
Q: 这个项目用什么数据库？
A: PostgreSQL 13.4

轮次 2:
Q: 如何备份？
A: [忘记上下文] 你用什么数据库？
```

### 技巧 3: 预判需求

```markdown
✅ 主动预判:

Q: 如何添加新 API 端点？
A: [完成添加]
   已添加 GET /api/users/:id

   相关：
   - 需要添加测试吗？
   - 更新 API 文档？

❌ 被动响应:

Q: 如何添加新 API 端点？
A: [完成添加]
   已添加 GET /api/users/:id
   [停止，等待用户下一个请求]
```

### 技巧 4: 代码引用

```markdown
✅ 优秀引用:
问题在 src/api/users.ts:45

原因：src/middleware/auth.ts:12 没有设置 req.user

修复：src/utils/validator.ts:28 添加邮箱格式验证

❌ 模糊引用:
问题在用户 API 文件里

原因：认证中间件有问题

修复：验证工具需要改
```

### 技巧 5: 量化结果

```markdown
✅ 量化:
优化完成。
- 响应时间：850ms → 45ms（19x 提升）
- 内存使用：120MB → 35MB（减少 70%）
- 数据库查询：15 次 → 3 次

❌ 模糊:
优化完成。
- 更快了
- 内存少了
- 查询减少了
```

---

