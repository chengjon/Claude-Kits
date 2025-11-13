## 🎓 实战场景

### 场景 1: 新功能开发

**用户请求**: "添加用户注册功能"

**Step 1: 澄清需求**
```markdown
需要确认：
1. 注册方式：邮箱/用户名？
2. 验证：需要邮箱验证吗？
3. 字段：除了邮箱和密码还需要什么？
```

**Step 2: 创建任务列表**
```markdown
TodoWrite([
  {
    content: "创建 User 数据模型",
    status: "pending",
    activeForm: "正在创建 User 数据模型"
  },
  {
    content: "实现注册 API 端点（POST /auth/register）",
    status: "pending",
    activeForm: "正在实现注册 API 端点"
  },
  {
    content: "添加密码哈希处理",
    status: "pending",
    activeForm: "正在添加密码哈希处理"
  },
  {
    content: "创建注册表单组件",
    status: "pending",
    activeForm: "正在创建注册表单组件"
  },
  {
    content: "编写注册功能测试",
    status: "pending",
    activeForm: "正在编写注册功能测试"
  }
])
```

**Step 3: 逐步执行**
```markdown
[标记任务1为 in_progress]
[创建 src/models/User.ts]
[标记任务1为 completed]

[标记任务2为 in_progress]
[创建 src/routes/auth.ts]
[标记任务2为 completed]

...
```

### 场景 2: Bug 修复

**用户报告**: "登录页面在移动端显示错位"

**分析 → 规划 → 执行**:
```markdown
TodoWrite([
  {
    content: "复现问题：检查移动端显示",
    status: "in_progress",
    activeForm: "正在复现问题"
  },
  {
    content: "定位根本原因：检查 CSS 和响应式布局",
    status: "pending",
    activeForm: "正在定位根本原因"
  },
  {
    content: "修复样式问题",
    status: "pending",
    activeForm: "正在修复样式问题"
  },
  {
    content: "在多种设备上验证修复",
    status: "pending",
    activeForm: "正在验证修复"
  }
])
```

### 场景 3: 大型重构

**任务**: "重构 API 层使用 async/await"

**并行 + 顺序混合策略**:
```markdown
TodoWrite([
  // 阶段1: 调研（并行）
  {
    content: "搜索所有 API 路由文件",
    status: "pending",
    activeForm: "正在搜索 API 路由文件"
  },
  {
    content: "搜索所有回调函数模式",
    status: "pending",
    activeForm: "正在搜索回调函数"
  },

  // 阶段2: 分析（顺序，依赖阶段1）
  {
    content: "分析依赖关系和影响范围",
    status: "pending",
    activeForm: "正在分析依赖关系"
  },

  // 阶段3: 执行（顺序，逐文件处理）
  {
    content: "重构 users.js（5个端点）",
    status: "pending",
    activeForm: "正在重构 users.js"
  },
  {
    content: "重构 auth.js（3个端点）",
    status: "pending",
    activeForm: "正在重构 auth.js"
  },

  // 阶段4: 验证（顺序）
  {
    content: "运行完整测试套件",
    status: "pending",
    activeForm: "正在运行测试套件"
  }
])
```

---

