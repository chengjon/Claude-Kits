## 模式 2: 代码解释

### 何时使用

- 用户询问代码功能、目的、实现方式
- 需要解释架构、设计模式
- 回答"这段代码做什么"类型的问题

### 分层解释策略

```
第一层: 一句话概述（默认）
    ↓
[如果用户需要更多]
    ↓
第二层: 关键步骤（2-4行）
    ↓
[如果用户需要更多]
    ↓
第三层: 逐行详解
```

### 示例 1: 简单解释

```typescript
// 代码
function filterActiveUsers(users) {
  return users
    .filter(u => u.isActive)
    .sort((a, b) => b.createdAt - a.createdAt)
    .slice(0, 10);
}
```

**第一层回答（默认）**:
```markdown
用户: 这段代码做什么？
助手: 过滤活跃用户，按创建时间倒序排列，取前 10 个。
```

**第二层回答（用户追问）**:
```markdown
用户: 为什么要过滤？
助手: 只显示 `isActive=true` 的用户，排除已禁用账户。
```

**第三层回答（用户深入）**:
```markdown
用户: 详细解释每一步
助手:
1. `.filter(u => u.isActive)`: 保留 isActive 为 true 的用户
2. `.sort((a, b) => b.createdAt - a.createdAt)`: 按创建时间降序
3. `.slice(0, 10)`: 取前 10 个结果
```

### 示例 2: 架构解释

```markdown
用户: 这个项目的认证流程是怎样的？

助手: [先读取相关文件]
[
  Read('src/middleware/auth.ts'),
  Read('src/services/jwt.service.ts'),
  Read('src/controllers/auth.controller.ts')
]

助手:
1. 用户登录 → AuthController.login()
2. 验证密码 → bcrypt 哈希比对
3. 生成 JWT → JwtService.sign()
4. 返回 token

后续请求：
- 前端在 header 中携带 token
- AuthMiddleware 验证 token
- 解析出 userId，注入 req.user

关键文件：
- src/middleware/auth.ts:15 - Token 验证
- src/services/jwt.service.ts:28 - Token 生成
- src/controllers/auth.controller.ts:42 - 登录逻辑
```

### 示例 3: 设计模式解释

```markdown
用户: 为什么使用 Factory 模式？

助手: [检查代码]

这里使用 Factory 是因为需要根据不同的支付方式创建不同的处理器：

- 信用卡 → CreditCardProcessor
- PayPal → PayPalProcessor
- 支付宝 → AlipayProcessor

Factory 模式优点：
1. 客户端代码不需要知道具体类
2. 添加新支付方式无需修改现有代码
3. 集中管理对象创建逻辑

位置：src/payment/PaymentProcessorFactory.ts:12
```

### 最佳实践

#### 使用代码引用

```markdown
✅ 好的引用:
问题在 src/api/users.ts:45

❌ 模糊引用:
问题在用户 API 文件里
```

#### 匹配详细程度

| 问题类型 | 回答详细度 | 示例 |
|---------|-----------|------|
| 简单功能查询 | 1行概述 | "验证用户输入" |
| 函数实现 | 2-4行步骤 | "1. 检查格式 2. 哈希密码 3. 保存" |
| 架构设计 | 流程图 + 关键文件 | [流程] + 文件引用 |
| 设计模式 | 原因 + 优点 + 示例 | "使用X因为Y，优点是..." |

#### 渐进式详细

```markdown
默认: 简短回答
   ↓
用户追问 → 提供更多细节
   ↓
用户深入 → 完整解释
```

---

