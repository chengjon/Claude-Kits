# 进度跟踪模式

> TodoWrite 状态管理和更新最佳实践

## 🎯 核心原则

### 原则 1: 实时更新 (Real-time Updates)

```markdown
用户看到的进度 = 你当前的状态

❌ 错误：延迟更新
[执行任务1]
[执行任务2]
[执行任务3]
[批量更新所有状态]    ← 用户看不到中间进度

✅ 正确：实时更新
[标记任务1 → in_progress]
[执行任务1]
[标记任务1 → completed]  ← 立即反馈
[标记任务2 → in_progress]
[执行任务2]
[标记任务2 → completed]
```

### 原则 2: 单一焦点 (Single Focus)

```markdown
规则：同时只能有 1 个 in_progress 任务

为什么？
- 避免混淆（用户不知道你在做什么）
- 强制顺序执行（避免并行冲突）
- 清晰的进度指示

✅ 正确状态:
- [completed] 任务A
- [in_progress] 任务B    ← 唯一的 in_progress
- [pending] 任务C
- [pending] 任务D

❌ 错误状态:
- [in_progress] 任务A
- [in_progress] 任务B    ← 两个 in_progress！
- [pending] 任务C
```

### 原则 3: 完整才完成 (Complete Before Marking)

```markdown
何时标记为 completed？

✅ 必须满足所有条件:
1. 代码已写完
2. 测试已通过
3. 无编译/运行错误
4. 达到预期目标

❌ 不能标记为 completed:
- 部分完成
- 测试失败
- 遇到阻塞问题
- 需要返工

遇到问题时的正确做法:
1. 保持当前任务为 in_progress
2. 创建新任务解决问题
3. 问题解决后，再标记原任务为 completed
```

---

## 📊 状态转换详解

### 完整状态机

```
                 pending
                    ↓
          [开始工作]
                    ↓
              in_progress
                    ↓
         [完成所有工作]
                    ↓
               completed
```

### 转换时机

#### pending → in_progress

**触发时机**:
- 准备开始执行该任务
- 已读取必要的文件/信息
- 明确了下一步具体操作

**示例**:
```markdown
情况 1: 创建新文件
- 已确定文件路径和内容
→ 标记 "创建 User model" 为 in_progress
→ 使用 Write 工具创建文件

情况 2: 修复 bug
- 已定位到问题代码（src/utils.ts:45）
- 已分析出根本原因
→ 标记 "修复空指针错误" 为 in_progress
→ 使用 Edit 工具修改代码

情况 3: 运行测试
- 代码修改已完成
- 准备验证修复
→ 标记 "运行单元测试" 为 in_progress
→ 使用 Bash 工具运行 npm test
```

#### in_progress → completed

**触发时机**:
- 任务完全完成（100%）
- 所有验证通过
- 无遗留问题

**检查清单**:
```markdown
代码任务:
  ✓ 代码已写完
  ✓ 语法正确
  ✓ 逻辑符合需求
  ✓ 测试通过

测试任务:
  ✓ 所有测试用例已运行
  ✓ 测试通过率 100%
  ✓ 无错误输出

文档任务:
  ✓ 内容完整
  ✓ 格式正确
  ✓ 链接有效
```

---

## 🔄 常见场景处理

### 场景 1: 执行中发现新问题

**问题**: 任务执行到一半，发现依赖缺失

```markdown
初始状态:
- [completed] 创建 API 路由
- [in_progress] 编写 API 测试
- [pending] 更新 API 文档

发现问题: 测试需要 supertest 库，但未安装

❌ 错误做法:
[放弃当前任务，去安装依赖]
[标记测试任务为 completed]    ← 实际未完成

✅ 正确做法:
[调整任务列表]
- [completed] 创建 API 路由
- [completed] 编写 API 测试（发现依赖缺失）
- [in_progress] 安装 supertest 依赖    ← 新增
- [pending] 重新运行 API 测试          ← 新增
- [pending] 更新 API 文档
```

### 场景 2: 任务失败需要返工

**问题**: 测试运行后发现代码有bug

```markdown
当前状态:
- [completed] 实现登录功能
- [in_progress] 运行登录测试

结果: 测试失败（token 验证逻辑错误）

❌ 错误做法:
[标记测试为 completed]    ← 测试失败不能标记完成
[返回修改代码]

✅ 正确做法:
[更新任务列表]
- [completed] 实现登录功能（发现 bug）
- [completed] 运行登录测试（测试失败，定位问题）
- [in_progress] 修复 token 验证逻辑    ← 新增
- [pending] 重新运行登录测试           ← 新增
```

### 场景 3: 并行任务完成

**问题**: 多个独立任务可以并行

```markdown
任务:
- [pending] 搜索所有 API 文件
- [pending] 搜索所有路由配置
- [pending] 搜索所有中间件

✅ 正确做法（分步标记）:
Step 1:
[标记任务1 → in_progress]
[并行执行 Glob 工具调用]
[标记任务1 → completed]

Step 2:
[标记任务2 → in_progress]
[结果已从并行调用获得]
[标记任务2 → completed]

Step 3:
[标记任务3 → in_progress]
[结果已从并行调用获得]
[标记任务3 → completed]

说明: 虽然工具并行执行，但状态更新仍然按顺序进行
```

---

## 🎯 更新频率指导

### 推荐更新频率

```markdown
小任务（1-2分钟）:
  pending → in_progress → completed
  ↑              ↑               ↑
  开始          执行中           完成后立即

中任务（3-5分钟）:
  pending → in_progress → completed
  ↑              ↑               ↑
  开始          执行中           完成后立即

大任务（5+分钟）:
  pending → in_progress → completed
  ↑              ↑               ↑
  开始          执行中           完成后立即

关键: 无论任务大小，完成后立即更新
```

### 批量操作的处理

```markdown
场景: 需要编辑 5 个文件

❌ 粗粒度（不推荐）:
- [in_progress] 更新所有配置文件

✅ 细粒度（推荐）:
- [in_progress] 更新 config1.json
- [pending] 更新 config2.json
- [pending] 更新 config3.json
- [pending] 更新 config4.json
- [pending] 更新 config5.json

优点: 用户可以看到精确的进度（1/5, 2/5, 3/5...）
```

---

## 📝 状态描述最佳实践

### content vs activeForm

```yaml
content: 命令式（做什么）
  - 用于任务列表展示
  - 简洁明了
  - 动词 + 对象

activeForm: 进行时（正在做什么）
  - 用于进度指示
  - 让用户知道当前操作
  - "正在" + 动词 + 对象
```

### 优秀示例

```yaml
✅ 清晰具体:
content: "创建 User 数据模型（src/models/user.ts）"
activeForm: "正在创建 User 数据模型"

content: "实现登录 API（POST /auth/login）"
activeForm: "正在实现登录 API"

content: "运行完整测试套件（Jest）"
activeForm: "正在运行测试套件"

content: "修复 Safari 浏览器样式问题（header.css:45-67）"
activeForm: "正在修复 Safari 样式问题"

❌ 模糊不清:
content: "处理用户"
activeForm: "正在处理"

content: "修复bug"
activeForm: "正在修复"

content: "更新代码"
activeForm: "正在更新"
```

---

## 🚨 常见错误

### 错误 1: 批量更新状态

```markdown
症状:
[完成了 3 个任务]
[一次性更新所有状态]

问题:
- 用户看不到实时进度
- 缺少反馈
- 像是"冻住"了

解决:
每完成一个任务，立即更新其状态
```

### 错误 2: 忘记标记 completed

```markdown
症状:
- [completed] 任务A
- [in_progress] 任务B    ← 实际已完成，但忘记更新
- [in_progress] 任务C    ← 当前正在做

问题:
- 有两个 in_progress（违反规则）
- 用户不知道任务B已完成

解决:
完成任务后，立即检查并更新状态
```

### 错误 3: 过早标记 completed

```markdown
症状:
[代码写完]
[标记为 completed]
[运行测试 → 失败]    ← 实际未完成！

问题:
- 误导用户以为已完成
- 需要返工

解决:
确保所有验证通过后再标记 completed
```

---

## 💡 高级技巧

### 技巧 1: 使用明确的阶段标识

```yaml
TodoWrite([
  // 阶段1: 准备
  { content: "【准备】分析需求", status: "completed", ... },
  { content: "【准备】设计方案", status: "completed", ... },

  // 阶段2: 实施
  { content: "【实施】编写代码", status: "in_progress", ... },
  { content: "【实施】编写测试", status: "pending", ... },

  // 阶段3: 验证
  { content: "【验证】运行测试", status: "pending", ... },
  { content: "【验证】代码审查", status: "pending", ... }
])

优点: 用户可以看到整体进展（当前在哪个阶段）
```

### 技巧 2: 动态调整计划

```markdown
执行中可以:
- 添加新任务（发现遗漏）
- 删除任务（不再需要）
- 修改任务描述（澄清细节）

示例:
初始:
- [pending] 实现用户注册
- [pending] 添加邮箱验证

执行中发现需要密码强度检查:
- [completed] 实现用户注册
- [in_progress] 添加密码强度检查    ← 新增
- [pending] 添加邮箱验证
```

### 技巧 3: 保持任务列表整洁

```markdown
完成所有任务后:
- 可以清空任务列表（开始新任务组）
- 或保留历史记录（供用户参考）

推荐: 大型任务完成后保留历史，小任务完成后清空
```

---

## 📊 性能指标

### 好的进度跟踪的特征

```markdown
✓ 用户能看到实时进度
✓ 每个任务状态准确
✓ 完成比例清晰（3/5, 4/5）
✓ 当前操作明确
✓ 无意外的状态变化

测量方法:
- 状态更新延迟 < 5秒
- in_progress 任务数量 = 1
- completed 任务准确率 = 100%
```

---

**版本**: v1.0
**最后更新**: 2025-11-10
