# Reddit-Case 快速开始 ⚡

> 5分钟完成安全安装

## 🛡️ 安全保证

- ✅ **永不覆盖你的文件** - 所有现有文件完全安全
- ✅ **完全透明** - 所有操作提前展示
- ✅ **用户控制** - 所有修改需要你确认

---

## 📋 3步安装流程

### 步骤 1: 检查冲突（30秒）

```bash
# 快速检查将要安装什么，是否有冲突
python scripts/check_conflicts.py /path/to/your/project
```

**输出示例**：
```
✅ 没有冲突 - 可以安全安装
📦 将要安装 27 个新组件
```

或

```
⚠️  发现 27 个冲突
建议: 安装时选择 'skip' 保留这些文件
```

---

### 步骤 2: 预览安装（1分钟）

```bash
# 预览所有操作，不执行实际安装
python scripts/install_reddit_case.py /path/to/your/project --dry-run
```

**会显示**：
- 将要创建的目录
- 将要复制的文件
- 需要自定义的配置

---

### 步骤 3: 执行安装（2分钟）

```bash
# 交互式安装
python scripts/install_reddit_case.py /path/to/your/project
```

**按提示操作**：

1. **如果有冲突** - 选择处理方式：
   ```
   1. skip   - 跳过，保留现有文件（推荐）✅
   2. rename - 重命名新文件 (.reddit-case)
   3. backup - 备份现有文件 (.backup)
   4. abort  - 中止安装

   请选择 (1-4) [1]: 1
   ```

2. **确认安装计划**：
   ```
   将执行 28 个操作
   确认执行? (y/N): y
   ```

3. **等待完成**：
   ```
   ✅ [1/28] 创建目录: agents
   ✅ [2/28] 复制文件: auth-route-tester.md
   ...
   ✅ 安装完成!
   ```

---

## 🎯 安装后配置（5分钟）

安装完成后，需要自定义3个配置文件：

### 1. 构建检查配置

编辑 `.claude/build-checker.json`:

```json
{
  "repos": {
    "/opt/claude/your-project": {              // 👈 改为你的项目路径
      "buildCommand": "npm run build",          // 👈 改为你的构建命令
      "errorThreshold": 5
    }
  }
}
```

**常见构建命令**：
- TypeScript: `"tsc --noEmit"`
- Next.js: `"next build"`
- Python: `"python3 -m py_compile **/*.py"`
- Vue: `"npm run build"`

### 2. Skills 激活规则

编辑 `.claude/skill-rules.json`:

```json
{
  "skills": {
    "backend-dev-guidelines": {
      "fileTriggers": {
        "pathPatterns": [
          "src/routes/**/*.ts",           // 👈 改为你的路径
          "src/controllers/**/*.ts"
        ]
      }
    }
  }
}
```

### 3. Skills 描述（可选）

编辑 `.claude/skills/*/SKILL.md` 的 `description` 字段，添加项目特定关键词。

---

## 💡 使用示例

### 场景 1: 全新项目（推荐）

```bash
# 1. 检查（应该无冲突）
python scripts/check_conflicts.py /path/to/new-project

# 2. 直接安装
python scripts/install_reddit_case.py /path/to/new-project

# 3. 配置文件
nano /path/to/new-project/.claude/build-checker.json
```

### 场景 2: 现有项目（有配置）

```bash
# 1. 检查冲突
python scripts/check_conflicts.py /path/to/existing-project

# 2. 预览
python scripts/install_reddit_case.py /path/to/existing-project --dry-run

# 3. 安装（选择 skip 保留现有文件）
python scripts/install_reddit_case.py /path/to/existing-project
# 选择 1 (skip)

# 4. 手动复制需要的组件
cp -r .claude/agents/build-error-resolver.md /path/to/existing-project/.claude/agents/
```

---

## ⚙️ 命令选项

```bash
# 交互式安装（推荐）
python scripts/install_reddit_case.py /path/to/project

# 预览模式（不执行）
python scripts/install_reddit_case.py /path/to/project --dry-run

# 非交互模式（自动 skip 冲突）
python scripts/install_reddit_case.py /path/to/project --no-interactive

# 查看帮助
python scripts/install_reddit_case.py --help
```

---

## 🔍 冲突处理策略

| 策略 | 说明 | 推荐场景 |
|------|------|---------|
| **skip** ✅ | 跳过，保留现有文件 | 已有配置，想手动合并 |
| **rename** | 新文件添加 `.reddit-case` 后缀 | 想同时保留两个版本对比 |
| **backup** | 备份现有文件为 `.backup` | 想使用新版本但保留旧版 |
| **abort** | 中止安装 | 发现预期外的冲突 |

---

## 🚀 核心功能预览

安装完成后你将获得：

### 🤖 7个专业 Agents
- `build-error-resolver` - 自动修复构建错误
- `code-architecture-reviewer` - 代码架构审查
- `database-verifier` - 数据库验证
- 更多...

### 📚 7个领域 Skills
- `backend-dev-guidelines` - 后端开发指南
- `frontend-dev-guidelines` - 前端开发指南
- `dev-docs-workflow` - Dev Docs 工作流
- 更多...

### 🪝 4个核心 Hooks
- `user-prompt-submit-skill-activation.sh` - **Skills 自动激活**
- `stop-build-checker.sh` - **构建检查门禁**
- `post-tool-use-file-edit-tracker.sh` - 文件编辑追踪
- `session-start-dev-docs-injector.sh` - 上下文恢复

### ⚡ 6个 Slash Commands
- `/dev-docs` - 创建开发文档
- `/code-review` - 代码审查
- `/build-and-fix` - 构建并修复
- 更多...

---

## 📖 详细文档

需要更多信息？查看：

- [完整安装指南](INSTALLATION.md) - 详细步骤和示例
- [架构设计](docs/ARCHITECTURE_DESIGN.md) - 安全机制设计
- [Reddit Case Study](docs/REDDIT_CASE_IMPLEMENTATION_SUMMARY.md) - 30万行代码案例

---

## ❓ 常见问题

### Q: 会覆盖我的文件吗？
**A**: **绝对不会！** 所有现有文件都受保护，只有你明确选择 backup 策略时才会修改。

### Q: 可以撤销安装吗？
**A**: 如果选择了 skip 策略，完全没有修改你的文件。如果选择了其他策略，备份文件都在（.backup 后缀）。

### Q: 安装失败了怎么办？
**A**: 安装器会在第一个错误处停止，不会继续执行后续操作。已经安装的文件可以手动删除。

### Q: 如何只安装部分组件？
**A**:
1. 使用 skip 策略跳过所有冲突
2. 手动复制需要的组件：
   ```bash
   cp -r .claude/agents/build-error-resolver.md /path/to/project/.claude/agents/
   ```

---

## 🎯 下一步

安装完成后：

1. ✅ 测试 Skills 自动激活
   ```
   > "创建一个新的 API 路由"
   # 应该自动激活 backend-dev-guidelines
   ```

2. ✅ 配置构建检查
   ```bash
   # 编辑文件后，Claude 停止时会自动运行构建检查
   ```

3. ✅ 尝试 Slash Commands
   ```
   > /dev-docs
   > /code-review
   ```

4. ✅ 创建 Dev Docs
   ```
   > /dev-docs
   # 创建 plan.md, context.md, tasks.md
   ```

---

**记住：永远不会覆盖你的文件！** 🛡️

有问题？查看 [INSTALLATION.md](INSTALLATION.md) 或提交 Issue。
