# 可选 Hooks (Optional Hooks)

本目录包含基于 Reddit 案例研究开发的可选 Hook 脚本。这些脚本提供额外的功能，可以根据项目需求选择性启用。

## 📋 目录

- [脚本列表](#脚本列表)
- [快速开始](#快速开始)
- [使用场景](#使用场景)
- [安装指南](#安装指南)
- [配置示例](#配置示例)
- [常见问题](#常见问题)

---

## 脚本列表

### 1. PM2 Permission Gatekeeper

**文件**: `pre-tool-use-pm2-permission-gatekeeper.sh`
**事件**: PreToolUse
**Matcher**: `Bash`
**用途**: 控制 PM2 命令权限，让 Claude 安全地管理后端服务

**功能**:
- ✅ **自动批准** 只读命令（logs, monit, status, list, show）
- ⚠️ **询问确认** 变更命令（restart, stop, reload, delete, start）
- ❌ **阻止执行** 危险命令（delete all, kill, flush all）

**使用场景**:
- 后端开发，需要 Claude 帮助调试 Node.js 服务
- 允许查看日志和状态，但需要确认重启操作
- 防止误删除所有 PM2 进程

---

### 2. Sensitive File Guard

**文件**: `pre-tool-use-sensitive-file-guard.sh`
**事件**: PreToolUse
**Matcher**: `Edit|Write`
**用途**: 阻止 Claude 修改敏感文件（credentials, keys, configs）

**保护的文件类型**:
- 🔑 环境变量：`.env`, `.env.*`, `credentials.json`
- 🔐 SSH 密钥：`.ssh/id_rsa`, `.ssh/id_ed25519`, `.ssh/*.pem`
- ☁️ 云凭证：`.aws/credentials`, `.azure/credentials`, `.kube/config`
- 🗄️ 数据库配置：`database.yml`, `.my.cnf`, `.pgpass`
- 🎟️ API 密钥：`.npmrc`, `.pypirc`, `auth.json`, `token.json`
- 🔏 私钥：`.pem`, `.key`, `.p12`, `.pfx`
- 🐙 Git 凭证：`.git-credentials`, `.gitconfig`
- 🐳 Docker 配置：`.docker/config.json`

**使用场景**:
- 所有项目的基础安全守卫
- 防止意外泄露敏感信息
- 符合安全合规要求

---

### 3. Dev Docs Snapshot

**文件**: `pre-compact-dev-docs-snapshot.sh`
**事件**: PreCompact
**Matcher**: N/A
**用途**: 在对话压缩前保存 Dev Docs 快照，防止上下文丢失

**保存的文件**:
- 📝 `plan.md` - 当前架构和设计决策
- 📖 `context.md` - 项目背景和技术栈
- ✅ `tasks.md` - 进行中的任务和待办事项

**功能**:
- 💾 创建带时间戳的备份副本
- 🧹 自动清理旧备份（保留最新 5 个）
- 📊 提供快照摘要（文件大小、行数）

**使用场景**:
- 长期项目，需要保持上下文连续性
- 配合 SessionStart 的 dev-docs-injector.sh 使用
- Reddit 案例的核心模式：**上下文保存与恢复**

---

### 4. Batch Prettier

**文件**: `session-end-batch-prettier.sh`
**事件**: SessionEnd
**Matcher**: N/A
**用途**: 会话结束时自动格式化所有修改过的代码文件

**支持的文件类型**:
- JavaScript: `js`, `jsx`
- TypeScript: `ts`, `tsx`
- 样式: `css`, `scss`, `less`
- 标记: `html`, `vue`, `md`
- 配置: `json`, `yaml`, `yml`

**功能**:
- 🔍 从 git status 或 file-edit-tracker 检测修改文件
- 🎨 批量格式化（限制 100 个文件）
- 💬 友好提示：Prettier 未安装时不阻塞
- 📊 提供格式化摘要

**使用场景**:
- 前端开发，确保代码风格一致
- 减少 PR review 中的格式问题
- Reddit 案例的 "Clean Exit" 模式

**前置要求**:
```bash
npm install -D prettier
```

---

### 5. Desktop Notifier

**文件**: `notification-desktop-notifier.sh`
**事件**: Notification
**Matcher**: N/A
**用途**: 将 Claude Code 的通知转发到操作系统桌面通知

**平台支持**:
- 🍎 macOS: 使用 `osascript`（内置）
- 🐧 Linux: 使用 `notify-send`（需要安装）
- 🪟 Windows WSL: 使用 `powershell.exe`（内置）

**通知级别**:
- ℹ️ `info`: 一般信息（绿色/低优先级）
- ⚠️ `warning`: 警告（黄色/中优先级）
- ❌ `error`: 错误（红色/高优先级）
- ✅ `success`: 成功（绿色/低优先级）

**功能**:
- 🎨 根据级别设置图标和紧急程度
- 🔕 可配置的最小级别过滤（只显示 warning 和 error）
- 🔔 自定义通知声音（macOS）
- ⏱️ 可配置的显示时长（Linux）

**使用场景**:
- 长时间运行的构建任务完成时通知
- 测试套件运行结果
- 错误或警告发生时提醒
- Reddit 案例的 "Awareness Without Interruption" 模式

**Linux 安装依赖**:
```bash
# Ubuntu/Debian
sudo apt-get install libnotify-bin

# Fedora/RHEL
sudo dnf install libnotify

# Arch Linux
sudo pacman -S libnotify
```

---

## 快速开始

### 1. 安装脚本

```bash
# 创建 hooks 目录
mkdir -p .claude/hooks

# 复制你需要的脚本（选择性复制）
cp components/hooks/optional/pre-tool-use-pm2-permission-gatekeeper.sh .claude/hooks/
cp components/hooks/optional/pre-tool-use-sensitive-file-guard.sh .claude/hooks/
cp components/hooks/optional/pre-compact-dev-docs-snapshot.sh .claude/hooks/
cp components/hooks/optional/session-end-batch-prettier.sh .claude/hooks/
cp components/hooks/optional/notification-desktop-notifier.sh .claude/hooks/

# 设置可执行权限
chmod +x .claude/hooks/*.sh
```

### 2. 配置 settings.json

使用 hooks_manager.py 添加 hooks：

```bash
# PM2 Permission Gatekeeper
python scripts/hooks_manager.py add PreToolUse \
    --matcher "Bash" \
    --command ".claude/hooks/pre-tool-use-pm2-permission-gatekeeper.sh" \
    --scope project \
    --timeout 2

# Sensitive File Guard
python scripts/hooks_manager.py add PreToolUse \
    --matcher "Edit|Write" \
    --command ".claude/hooks/pre-tool-use-sensitive-file-guard.sh" \
    --scope project \
    --timeout 2

# Dev Docs Snapshot
python scripts/hooks_manager.py add PreCompact \
    --command ".claude/hooks/pre-compact-dev-docs-snapshot.sh" \
    --scope project \
    --timeout 10

# Batch Prettier
python scripts/hooks_manager.py add SessionEnd \
    --command ".claude/hooks/session-end-batch-prettier.sh" \
    --scope project \
    --timeout 60

# Desktop Notifier
python scripts/hooks_manager.py add Notification \
    --command ".claude/hooks/notification-desktop-notifier.sh" \
    --scope project \
    --timeout 5
```

### 3. 验证安装

```bash
# 查看已安装的 hooks
python scripts/hooks_manager.py list --scope project

# 验证脚本权限
ls -l .claude/hooks/*.sh
```

---

## 使用场景

### 场景 1: 后端开发

**需求**: 开发 Node.js API，使用 PM2 管理服务，需要 Claude 帮助调试

**推荐 Hooks**:
- ✅ PM2 Permission Gatekeeper（自动批准日志查看，询问确认重启）
- ✅ Sensitive File Guard（保护 .env 和数据库配置）
- ✅ Dev Docs Snapshot（保持项目上下文）

**配置**:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": ".claude/hooks/pre-tool-use-pm2-permission-gatekeeper.sh"}],
        "timeout": 2
      },
      {
        "matcher": "Edit|Write",
        "hooks": [{"type": "command", "command": ".claude/hooks/pre-tool-use-sensitive-file-guard.sh"}],
        "timeout": 2
      }
    ],
    "PreCompact": [
      {"hooks": [{"type": "command", "command": ".claude/hooks/pre-compact-dev-docs-snapshot.sh"}], "timeout": 10}
    ]
  }
}
```

---

### 场景 2: 前端开发

**需求**: 开发 React 应用，需要确保代码风格一致，及时收到构建通知

**推荐 Hooks**:
- ✅ Sensitive File Guard（保护 API keys 和配置文件）
- ✅ Batch Prettier（自动格式化代码）
- ✅ Desktop Notifier（构建完成通知）

**配置**:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{"type": "command", "command": ".claude/hooks/pre-tool-use-sensitive-file-guard.sh"}],
        "timeout": 2
      }
    ],
    "SessionEnd": [
      {"hooks": [{"type": "command", "command": ".claude/hooks/session-end-batch-prettier.sh"}], "timeout": 60}
    ],
    "Notification": [
      {"hooks": [{"type": "command", "command": ".claude/hooks/notification-desktop-notifier.sh"}], "timeout": 5}
    ]
  }
}
```

**前置准备**:
```bash
# 安装 Prettier
npm install -D prettier

# 创建 .prettierrc
echo '{"semi": true, "singleQuote": true, "tabWidth": 2}' > .prettierrc
```

---

### 场景 3: 全栈开发（Monorepo）

**需求**: 大型项目，前后端都有，需要全面的 Hook 支持

**推荐 Hooks**:
- ✅ 所有可选 Hooks

**配置**:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": ".claude/hooks/pre-tool-use-pm2-permission-gatekeeper.sh"}],
        "timeout": 2
      },
      {
        "matcher": "Edit|Write",
        "hooks": [{"type": "command", "command": ".claude/hooks/pre-tool-use-sensitive-file-guard.sh"}],
        "timeout": 2
      }
    ],
    "PreCompact": [
      {"hooks": [{"type": "command", "command": ".claude/hooks/pre-compact-dev-docs-snapshot.sh"}], "timeout": 10}
    ],
    "SessionEnd": [
      {"hooks": [{"type": "command", "command": ".claude/hooks/session-end-batch-prettier.sh"}], "timeout": 60}
    ],
    "Notification": [
      {"hooks": [{"type": "command", "command": ".claude/hooks/notification-desktop-notifier.sh"}], "timeout": 5}
    ]
  }
}
```

---

## 安装指南

### 方法 1: 使用 hooks_manager.py（推荐）

```bash
# 添加 PM2 Permission Gatekeeper
python scripts/hooks_manager.py add PreToolUse \
    --matcher "Bash" \
    --command "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-pm2-permission-gatekeeper.sh" \
    --scope project \
    --timeout 2

# 添加 Sensitive File Guard
python scripts/hooks_manager.py add PreToolUse \
    --matcher "Edit|Write" \
    --command "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-sensitive-file-guard.sh" \
    --scope project \
    --timeout 2

# 其他脚本类似...
```

### 方法 2: 手动编辑 settings.json

1. 打开 `.claude/settings.json`
2. 添加 hooks 配置（参考上面的配置示例）
3. 保存文件
4. 验证 JSON 语法：`python scripts/hooks_manager.py list --scope project`

---

## 配置示例

### PreToolUse Hooks 配置

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-pm2-permission-gatekeeper.sh"
          }
        ],
        "timeout": 2
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-sensitive-file-guard.sh"
          }
        ],
        "timeout": 2
      }
    ]
  }
}
```

**注意**:
- `matcher` 参数只支持 PreToolUse 和 PostToolUse 事件
- 工具名称区分大小写（`Edit` 不是 `edit`）
- 可以使用 `|` 连接多个工具（如 `Edit|Write`）

### PreCompact Hook 配置

```json
{
  "hooks": {
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-compact-dev-docs-snapshot.sh"
          }
        ],
        "timeout": 10
      }
    ]
  }
}
```

**环境变量配置**:
```bash
# 在 .bashrc 或 .zshrc 中添加
export DEV_DOCS_DIR=".claude/dev-docs"
export SNAPSHOT_BACKUP="true"
export MAX_BACKUPS="5"
```

### SessionEnd Hook 配置

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-end-batch-prettier.sh"
          }
        ],
        "timeout": 60
      }
    ]
  }
}
```

**环境变量配置**:
```bash
export MAX_FILES="100"
export USE_GIT_STATUS="true"
export PRETTIER_OPTIONS="--write"
```

### Notification Hook 配置

```json
{
  "hooks": {
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/notification-desktop-notifier.sh"
          }
        ],
        "timeout": 5
      }
    ]
  }
}
```

**环境变量配置**:
```bash
export NOTIFICATION_ENABLED="true"
export MIN_LEVEL="warning"  # 只显示 warning 和 error
export NOTIFICATION_DURATION="5"
```

---

## 常见问题

### Q1: 为什么我的 hooks 没有被触发？

**A1**: 检查以下几点：
1. ✅ 脚本是否有可执行权限？`ls -l .claude/hooks/*.sh`
2. ✅ settings.json 语法是否正确？`python scripts/hooks_manager.py list --scope project`
3. ✅ 脚本路径是否正确？使用绝对路径或 `$CLAUDE_PROJECT_DIR/`
4. ✅ matcher 参数是否正确？（工具名称区分大小写）

### Q2: PM2 Permission Gatekeeper 总是阻止我的命令

**A2**: 检查以下几点：
1. 是否是危险命令？（delete all, kill, flush all）
   - 这些命令会被阻止，改用具体的服务名称：`pm2 delete api` 而不是 `pm2 delete all`
2. 查看调试日志：`export PM2_GATEKEEPER_DEBUG="true"`
3. 自定义命令模式：修改脚本中的正则表达式

### Q3: Sensitive File Guard 阻止了我的测试文件

**A3**: 测试文件应该被自动排除，检查：
1. 文件名是否包含 `.test.`, `.spec.`, `.example.`, `.sample.`？
2. 文件路径是否在 `test/`, `example/`, `sample/` 目录下？
3. 如果不是，修改脚本添加你的排除模式

### Q4: Dev Docs Snapshot 说找不到 Dev Docs 文件

**A4**: 首先创建 Dev Docs：
```bash
mkdir -p .claude/dev-docs
touch .claude/dev-docs/plan.md
touch .claude/dev-docs/context.md
touch .claude/dev-docs/tasks.md
```

然后在 SessionStart 时，使用 dev-docs-injector.sh 恢复上下文。

### Q5: Batch Prettier 说 Prettier 未安装

**A5**: 安装 Prettier：
```bash
npm install -D prettier

# 验证安装
npx prettier --version
```

### Q6: Desktop Notifier 在 Linux 上不工作

**A6**: 安装 libnotify：
```bash
# Ubuntu/Debian
sudo apt-get install libnotify-bin

# 验证安装
notify-send "Test" "This is a test"
```

### Q7: 如何禁用某个 hook？

**A7**: 两种方法：
1. **临时禁用**：设置环境变量
   ```bash
   export NOTIFICATION_ENABLED="false"
   ```
2. **永久禁用**：从 settings.json 中删除该 hook 配置
   ```bash
   python scripts/hooks_manager.py delete PreToolUse --scope project
   ```

### Q8: Hook 执行超时怎么办？

**A8**: 增加 timeout 值：
```bash
python scripts/hooks_manager.py add PreToolUse \
    --matcher "Bash" \
    --command ".claude/hooks/pre-tool-use-pm2-permission-gatekeeper.sh" \
    --scope project \
    --timeout 10  # 增加到 10 秒
```

或者在 settings.json 中修改：
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [...],
      "timeout": 10
    }]
  }
}
```

### Q9: 如何调试 hook 脚本？

**A9**: 启用调试模式：
```bash
export PM2_GATEKEEPER_DEBUG="true"
export SENSITIVE_GUARD_DEBUG="true"
export DEV_DOCS_SNAPSHOT_DEBUG="true"
export BATCH_PRETTIER_DEBUG="true"
export DESKTOP_NOTIFIER_DEBUG="true"
```

调试信息会输出到 stderr，你可以在终端看到详细的执行日志。

### Q10: 可以同时使用多个 PreToolUse hooks 吗？

**A10**: 可以！Claude Code 支持同一事件的多个 hooks：
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"command": ".claude/hooks/pre-tool-use-pm2-permission-gatekeeper.sh"}],
        "timeout": 2
      },
      {
        "matcher": "Edit|Write",
        "hooks": [{"command": ".claude/hooks/pre-tool-use-sensitive-file-guard.sh"}],
        "timeout": 2
      }
    ]
  }
}
```

**重要**: 不同的 matcher 会匹配不同的工具调用，不会冲突。

---

## 🎓 学习资源

- **完整文档**: 查看 `docs/IMPLEMENTATION_COMPLETION_REPORT.md`
- **Reddit 案例研究**: 查看 `docs/REDDIT_CASE_IMPLEMENTATION_SUMMARY.md`
- **代码审查**: 查看 `docs/CODE_REVIEW_FINDINGS.md`
- **Essential Hooks**: 查看 `components/hooks/essential/`

---

## 📞 支持

遇到问题？

1. 📖 查看脚本头部的详细文档（每个脚本都有 60-80 行注释）
2. 🐛 检查 GitHub Issues
3. 💬 加入社区讨论

---

**最后更新**: 2025-11-07
**版本**: v1.0
