## 模式 3: 故障排查对话

### 对话流程

```
收集症状
    ↓
定位问题
    ↓
解释原因
    ↓
提供修复方案
    ↓
征求修复许可
```

### 示例 1: API 错误排查

```markdown
用户: 我的 API 不工作

助手: 什么错误信息？

用户: 500 Internal Server Error

助手: [读取日志]
[Read('logs/error.log')]

助手: 看到错误：`TypeError: Cannot read property 'id' of undefined`

      位置：src/api/users.ts:45

      问题：`user` 对象为 undefined

      可能原因：
      1. 认证中间件未设置 req.user
      2. 数据库查询返回 null

      检查认证中间件？

用户: 认证中间件可能有问题

助手: [检查代码]
[Read('src/middleware/auth.ts')]

助手: 发现问题：src/middleware/auth.ts:12

      JWT 验证失败时没有返回错误响应，导致：
      - `req.user` 未设置
      - 继续执行后续中间件
      - users.ts:45 访问 undefined.id 报错

      修复方法：
      ```typescript
      if (!decoded) {
        return res.status(401).json({ error: 'Unauthorized' });
      }
      ```

      要我修复吗？
```

### 示例 2: 性能问题排查

```markdown
用户: 网站加载很慢

助手: [测量]
[Bash("curl -w '@curl-format.txt' -o /dev/null -s https://your-site.com")]

助手: 响应时间：3.2秒

      细分：
      - DNS: 80ms
      - 连接: 120ms
      - 首字节时间: 2.8s ← 瓶颈
      - 传输: 200ms

      问题在服务器端。

      检查：
      1. 数据库查询？
      2. 外部API调用？

用户: 可能是数据库

助手: [分析慢查询]
[Bash("mysql -e 'SHOW FULL PROCESSLIST'")]

助手: 发现慢查询：
      ```sql
      SELECT * FROM products
      WHERE category_id IN (...)
      AND price BETWEEN ...
      ORDER BY created_at DESC
      ```

      耗时：2.5秒
      扫描行数：850,000 行

      原因：缺少复合索引

      建议添加：
      ```sql
      CREATE INDEX idx_category_price_created
      ON products(category_id, price, created_at)
      ```

      预计提升：2.5s → 50ms（50x）

      要我添加索引吗？
```

### 示例 3: 逻辑错误排查

```markdown
用户: 用户积分计算不对

助手: 预期结果 vs 实际结果？

用户: 应该是 150 分，显示 100 分

助手: [检查积分计算逻辑]
[
  Grep("calculatePoints|addPoints", type="ts"),
  Read('src/services/points.service.ts')
]

助手: 找到问题：src/services/points.service.ts:34

      ```typescript
      function calculatePoints(order) {
        let points = order.amount * 0.1;  // 基础积分

        if (order.isVip) {
          points = points * 1.5;  // VIP 加成
        }

        return Math.floor(points);
      }
      ```

      你的订单：
      - 金额: 1000 元
      - VIP: 是
      - 预期: (1000 * 0.1) * 1.5 = 150
      - 实际: 100

      问题：第 8 行 `Math.floor(points)` 应该在 VIP 加成之后执行

      但代码逻辑是对的...

      [继续检查]

      发现：src/controllers/order.controller.ts:67

      ```typescript
      const points = calculatePoints({
        amount: order.amount,
        // isVip: order.user.isVip  ← 这行被注释了！
      });
      ```

      根本原因：调用时没有传递 VIP 状态

      要我修复吗？
```

### 故障排查技巧

#### 1. 系统化收集信息

```markdown
✅ 好的流程:
1. 错误信息/症状
2. 复现步骤
3. 预期 vs 实际
4. 相关日志
5. 最近的代码变更

❌ 低效流程:
随机猜测，没有数据支持
```

#### 2. 缩小范围

```
全系统
   ↓
定位到子系统（前端 vs 后端 vs 数据库）
   ↓
定位到模块
   ↓
定位到文件
   ↓
定位到行
```

#### 3. 假设验证

```markdown
提出假设 → 设计验证方法 → 执行验证 → 确认/排除
```

---

