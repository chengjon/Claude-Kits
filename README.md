# Claude-Kits

Claude Code 自定义组件管理工具集 - Reddit-Case 30万行代码最佳实践

## 🛡️ 安全第一

**本项目最重要的原则：永不覆盖用户文件**

- ✅ 所有安装操作都需要用户授权
- ✅ 完整的冲突检测和解决机制
- ✅ 支持 dry-run 预览模式
- ✅ 透明显示所有将要执行的操作

## 🚀 快速开始

### 安装 Reddit-Case 到你的项目

```bash
# 1. 克隆此仓库
git clone https://github.com/your-repo/Claude-Kits.git
cd Claude-Kits

# 2. 检查冲突（可选但推荐）
python scripts/check_conflicts.py /path/to/your/project

# 3. 预览安装（不执行实际操作）
python scripts/install_reddit_case.py /path/to/your/project --dry-run

# 4. 执行安装
python scripts/install_reddit_case.py /path/to/your/project
```

**详细安装指南**: 查看 [INSTALLATION.md](INSTALLATION.md)

## 📦 包含的组件

Reddit-Case 包含基于 30 万行代码实践的完整工具链：

### 🤖 Agents (7个专业子代理)
- `auth-route-tester` - 认证路由测试
- `build-error-resolver` - 构建错误自动修复
- `code-architecture-reviewer` - 代码架构审查
- `database-verifier` - 数据库验证
- `documentation-architect` - 文档架构
- `frontend-error-fixer` - 前端错误修复
- `strategic-plan-architect` - 战略规划

### 📚 Skills (7个领域专业技能)
- `backend-dev-guidelines` - 后端开发指南
- `dev-docs-workflow` - Dev Docs 工作流
- `frontend-dev-guidelines` - 前端开发指南
- `notification-developer` - 通知系统开发
- `progressive-disclosure-pattern` - 渐进式披露模式
- `skill-developer` - 技能开发元技能
- `workflow-developer` - 工作流开发

### 🪝 Hooks (4个核心自动化管道)
- `user-prompt-submit-skill-activation.sh` - **Skills 自动激活**（最重要）
- `post-tool-use-file-edit-tracker.sh` - 文件编辑追踪
- `stop-build-checker.sh` - **构建检查质量门禁**（零错误秘诀）
- `session-start-dev-docs-injector.sh` - 上下文恢复

### ⚡ Commands (6个 Slash 命令)
- `/dev-docs` - 创建 Dev Docs 系统
- `/dev-docs-update` - 更新 Dev Docs
- `/code-review` - 代码审查
- `/build-and-fix` - 构建并修复错误
- `/test-route` - API 路由测试
- `/pm2-status` - PM2 状态查看

### ⚙️ 配置文件
- `settings.json` - Hooks 配置
- `skill-rules.json` - Skills 激活规则
- `build-checker.json` - 构建检查配置

## 🔥 核心功能

### 1. Skills 自动激活系统 ⭐
**问题**: Claude 不会自动加载 `.claude/skills/` 中的技能

**解决**: UserPromptSubmit hook + skill-rules.json 强制激活

**效果**: 确保 Claude 始终使用相关技能，提高一致性

### 2. 零错误容忍系统 🛡️
**模式**: 先记录（PostToolUse）→ 后检查（Stop）

**优点**: 允许临时破坏，减少构建噪声

**结果**: Reddit 团队 **6个月零错误记录**

### 3. 上下文持久化 🧠
**三文档系统**: plan.md + context.md + tasks.md

**自动恢复**: SessionStart hook 注入上下文

**跨会话**: 压缩后仍能继续工作

## 📖 文档

- [安装指南](INSTALLATION.md) - 详细的安装步骤和示例
- [CLAUDE.md](CLAUDE.md) - Claude Code 使用指南
- [Reddit Case Study](docs/REDDIT_CASE_IMPLEMENTATION_SUMMARY.md) - 30万行代码案例研究
- [架构设计](docs/ARCHITECTURE_DESIGN.md) - 设计原则和标准流程

## 🛠️ 管理工具

### 安全安装器
```bash
# 交互式安装
python scripts/install_reddit_case.py /path/to/project

# 预览模式
python scripts/install_reddit_case.py /path/to/project --dry-run

# 非交互模式
python scripts/install_reddit_case.py /path/to/project --no-interactive
```

### 冲突检查器
```bash
# 快速检查冲突
python scripts/check_conflicts.py /path/to/project
```

### 组件管理器
```bash
# 统一 CLI 管理器
python scripts/claude_manager.py skills list --scope project
python scripts/claude_manager.py agents install my-agent --scope personal

# 交互式 TUI
python scripts/claude_tui.py
```

## ⚠️ 安装前必读

1. **永远先使用 --dry-run** 预览操作
2. **检查冲突** 使用 `check_conflicts.py`
3. **备份重要文件** 在大规模安装前
4. **选择 skip 选项** 对于冲突，然后手动合并

## 🎯 使用场景

Reddit-Case 适用于：

- ✅ 需要高质量、零错误容忍的项目
- ✅ 中大型项目（10,000+ 行代码）
- ✅ 需要跨会话上下文持久化
- ✅ 团队协作开发
- ✅ 需要自动化质量门禁

## 💡 最佳实践

### 1. Skills 自动激活
编辑 `.claude/skill-rules.json`，调整路径模式以匹配你的项目：

```json
{
  "skills": {
    "backend-dev-guidelines": {
      "fileTriggers": {
        "pathPatterns": [
          "src/routes/**/*.ts",      // 改为你的路径
          "src/controllers/**/*.ts"
        ]
      }
    }
  }
}
```

### 2. 构建检查配置
编辑 `.claude/build-checker.json`：

```json
{
  "repos": {
    "/absolute/path/to/your/project": {
      "buildCommand": "npm run build",  // 改为你的构建命令
      "errorThreshold": 5
    }
  }
}
```

### 3. Skills 描述自定义
编辑每个 `.claude/skills/*/SKILL.md` 的 `description` 字段，添加项目特定关键词。

## 🤝 贡献

欢迎贡献！请确保：

1. 遵循安全原则（永不覆盖用户文件）
2. 添加测试
3. 更新文档
4. 遵循 500 行规则

## 📄 许可证

[MIT License](LICENSE)

## 🙏 致谢

本项目基于 Reddit 工程师 30 万行代码实践经验，感谢：
- Reddit 工程团队的最佳实践分享
- Claude Code 官方文档和指南
- 开源社区的贡献

---

**记住：永远不会覆盖你的文件，所有操作都需要你的确认！** 🛡️
