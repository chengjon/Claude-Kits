## 模式 5: 迭代开发对话

### 迭代模式

```
用户请求 v1
    ↓
实现基础功能
    ↓
简短确认
    ↓
用户请求 v2（增强）
    ↓
迭代改进
    ↓
简短确认
    ↓
[循环]
```

### 示例 1: 功能迭代

```markdown
轮次 1: 基础功能
用户: 添加用户搜索功能

助手: [实现基础搜索]
[
  Edit('src/api/users.ts', ...),
  Edit('src/controllers/users.controller.ts', ...)
]

助手: 完成。支持按用户名搜索。
      API: GET /api/users/search?name=xxx

---

轮次 2: 功能增强
用户: 需要支持邮箱搜索

助手: [更新代码]
[Edit('src/controllers/users.controller.ts', ...)]

助手: 已添加邮箱搜索。
      现在支持：
      - 用户名: ?name=xxx
      - 邮箱: ?email=xxx
      - 或两者: ?name=xxx&email=yyy

---

轮次 3: 性能优化
用户: 搜索太慢了

助手: [检查性能]
[
  Bash("EXPLAIN SELECT * FROM users WHERE username LIKE '%xxx%'")
]

助手: 问题：没有索引，全表扫描。
      扫描 50,000 行，耗时 850ms

      [添加索引]
      [Bash("CREATE INDEX idx_username ON users(username)")]
      [Bash("CREATE INDEX idx_email ON users(email)")]

      优化结果：
      - 搜索时间：850ms → 12ms（70x 提升）
      - 使用索引：idx_username, idx_email

---

轮次 4: 用户体验改进
用户: 能否支持模糊匹配？

助手: 已支持模糊匹配。

      示例：
      - 搜索 "john" → 匹配 "john", "johnny", "johnson"
      - 搜索 "gmail" → 匹配所有 gmail.com 邮箱

      实现：使用 LIKE '%xxx%'
```

### 示例 2: Bug修复迭代

```markdown
轮次 1: 发现问题
用户: 注册后没有发送验证邮件

助手: [检查代码]
[Read('src/services/email.service.ts')]

助手: 发现问题：src/controllers/auth.controller.ts:56

      ```typescript
      await createUser(userData);
      // TODO: 发送验证邮件
      ```

      [修复]
      [Edit(...)]

      已修复。现在注册后会自动发送验证邮件。

---

轮次 2: 新问题
用户: 邮件发送失败了

助手: [查看错误]
[Read('logs/email.log')]

助手: 错误：SMTP 连接超时

      原因：.env 中缺少 SMTP 配置

      需要添加：
      ```
      SMTP_HOST=smtp.gmail.com
      SMTP_PORT=587
      SMTP_USER=your-email@gmail.com
      SMTP_PASS=your-app-password
      ```

      要我帮你配置吗？

---

轮次 3: 配置完成
用户: 配置好了，但还是不行

助手: [测试连接]
[Bash("npm run test:email")]

助手: 测试结果：
      ✅ SMTP 连接成功
      ❌ 邮件发送失败：535 Authentication failed

      问题：Gmail 需要"应用专用密码"，不能使用普通密码

      步骤：
      1. 访问 https://myaccount.google.com/apppasswords
      2. 生成新的应用密码
      3. 更新 SMTP_PASS 为该密码

      [提供详细指南链接]
```

### 迭代开发原则

#### 1. 每轮简短确认

```markdown
✅ 好的确认:
完成。支持按用户名搜索。

❌ 冗长确认:
好的，我已经成功完成了用户搜索功能的实现。
现在你可以使用这个功能来搜索用户了。
这个功能非常有用...
```

#### 2. 主动发现问题

```markdown
✅ 主动:
完成。但发现性能问题（850ms），要优化吗？

❌ 被动:
完成。[等待用户发现性能问题]
```

#### 3. 保持上下文

```markdown
轮次 1: 实现功能 X
轮次 2: [记住 X] 基于 X 添加 Y
轮次 3: [记住 X+Y] 优化 X 和 Y 的性能
```

#### 4. 渐进式改进

```markdown
V1: 基础功能（核心价值）
  ↓
V2: 增强功能（更多用例）
  ↓
V3: 性能优化（更快）
  ↓
V4: 用户体验（更好）
```

---

## 🎯 模式选择决策树

```
用户消息
    ↓
【决策点 1】
请求是否明确？
    ↙        ↘
  否          是
   ↓           ↓
模式 1     【决策点 2】
需求澄清    是问题还是任务？
           ↙              ↘
         问题              任务
          ↓                 ↓
     【决策点 3】      【决策点 4】
    问什么类型？       首次还是迭代？
      ↙    ↘            ↙        ↘
    代码  故障         首次      迭代
     ↓     ↓            ↓         ↓
   模式2  模式3       模式4     模式5
   代码   故障        方案      迭代
   解释   排查        建议      开发
```

---

**版本**: v1.0
**最后更新**: 2025-11-09
