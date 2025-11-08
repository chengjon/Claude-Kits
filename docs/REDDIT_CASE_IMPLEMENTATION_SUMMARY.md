# Reddit Case Study Implementation Summary

## 📅 完成时间
2025-11-07

## 🎯 任务目标

基于 Reddit 工程师 30 万行代码经验（reference/hooks/30-逐项整理.md 和 9个Event要点.md），分析学习、审查代码、创建完整的 Hook 脚本、配置模板和文档。

---

## 📊 第一部分：关键发现与学习成果

### 🚨 最重要的发现：Skills 不会自动激活！

**错误认知**：之前以为 Claude 会自动读取 `.claude/skills/` 下的所有 SKILL.md 文件。

**真相**：Claude **不会**自动加载/采用所有 Skill 文档！Reddit 工程师在 30 万行代码中发现 Claude 经常忽略技能。

**解决方案**：UserPromptSubmit Hook + skill-rules.json 强制激活

```
用户输入 → UserPromptSubmit Hook → 分析提示词 → 匹配 skill-rules.json
→ 输出 JSON additionalContext → 强制 Claude 加载技能 → Claude 处理请求
```

### 📚 学到的 9 大核心知识点

#### 1. stdout 注入只在两个事件中有效 ⭐

**只有这两个事件的 stdout 会注入到 Claude**：
- `UserPromptSubmit` - 在 Claude 处理用户提示前注入
- `SessionStart` - 在会话启动时注入（恢复上下文）

**其他 7 个事件的 stdout 不会注入**，需要用 JSON `hookSpecificOutput.additionalContext`

#### 2. 温和提醒哲学（Exit Code 策略）⭐

**Exit Code 0** - 成功，继续
- stdout 在某些事件会被注入（UserPromptSubmit, SessionStart）

**Exit Code 1** - 警告但不阻止（温和提醒）
- stderr 显示给用户
- 操作继续执行
- **适用**：代码风格建议、性能优化提示、最佳实践提醒

**Exit Code 2** - 阻断操作（强制门禁）
- PreToolUse: 阻止工具调用，stderr 给 Claude
- Stop: 阻止停止，要求 Claude 继续工作
- UserPromptSubmit: 阻止提示处理，清除原始提示
- **适用**：安全风险、编译错误 ≥5、敏感文件修改

**Reddit 实践**：大多数检查用 exit 1（非阻塞），只有质量门禁用 exit 2

#### 3. 构建检查管道的先记录后检查模式 ⭐

**反模式**（会导致噪声）：
```bash
PostToolUse (Edit) → 立即运行 tsc → 报告错误
# 问题：临时破坏代码时频繁触发，干扰工作流
```

**正确模式**（Reddit 实践）：
```bash
PostToolUse (Edit|Write) → 记录到 edit_log.jsonl（非阻塞）
Stop → 读取日志 → 批量运行构建 → 若错误 ≥5 则阻断（exit 2）
```

**优点**：
- 允许临时代码破坏
- 减少构建次数
- 只在完成时做质量门禁

**结果**：Reddit 团队 6 个月零错误记录

#### 4. JSON 输出控制的新旧字段 ⭐

**新字段**（推荐）：
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "原因说明",
    "additionalContext": "注入到 Claude 的上下文"
  }
}
```

**旧字段**（仍支持但不推荐）：
```json
{
  "decision": "block",
  "reason": "原因"
}
```

**我们当前的 hooks_manager.py 没有提供生成这些 JSON 的功能！**

#### 5. 事件特定字段 ⭐

**PreCompact**：
- `trigger`: "manual" 或 "auto"（手动 /compact 还是自动压缩）
- `custom_instructions`: 用户在 /compact 时提供的指令

**SessionStart**：
- `source`: "startup" | "resume" | "clear" | "compact"
- `CLAUDE_ENV_FILE`: 环境变量，可写入文件持久化 env

**SessionEnd**：
- `reason`: "clear" | "logout" | "prompt_input_exit" | "other"

#### 6. Dev Docs 三文档系统解决上下文丢失 ⭐

**问题**：Claude 的自动压缩会丢失上下文，导致跨会话时"失忆"。

**Reddit 解决方案**：
```
.claude/dev/active/<task-name>/
├── plan.md          # 战略目标和架构决策
├── context.md       # 关键文件、依赖、注意事项（<200行）
└── tasks.md         # 任务清单（已完成/进行中/待办）
```

**Hooks 集成**：
- SessionStart → 读取 context.md 摘要 → stdout 注入给 Claude
- PreCompact → 运行 /dev-docs-update → 保存当前状态
- Stop → 可选更新 tasks.md

#### 7. PM2 集成的安全策略 ⭐

**PreToolUse hook 对 Bash 命令的权限控制**：

**自动批准**（exit 0 + JSON permissionDecision: "allow"）：
- `pm2 logs <service>`
- `pm2 monit`
- `pm2 status`

**要求确认**（JSON permissionDecision: "ask"）：
- `pm2 restart <service>`
- `pm2 stop <service>`

**阻止**（exit 2 或 JSON permissionDecision: "deny"）：
- `pm2 delete all`
- `pm2 kill`

#### 8. Prettier 的 Token 成本陷阱 ⭐

**Reddit 教训**：在会话内每次编辑后自动运行 Prettier 会导致：
- 大量 diff 出现在会话记录
- 消耗大量 tokens
- 影响模型输出质量

**解决方案**：
- 改为 SessionEnd hook 批量运行
- 或者只对小文件（<100 行）运行
- 或者作为手动 slash 命令

#### 9. skill-rules.json 实际格式（与预期不同）⭐

**实际使用的格式**（基于 claude-code-infrastructure-showcase）：
```json
{
  "version": "1.0",
  "skills": {
    "backend-dev-guidelines": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "...",
      "promptTriggers": {
        "keywords": [...],
        "intentPatterns": [...]
      },
      "fileTriggers": {
        "pathPatterns": [...],
        "pathExclusions": [...],
        "contentPatterns": [...]
      }
    }
  }
}
```

**不是之前假设的 `rules` 数组格式！**

---

## 🔍 第二部分：Code Review 审查结果

### 审查评分：6.5/10

**优点**：
- ✅ 完整的安全框架（15+ 危险命令检测）
- ✅ 路径遍历保护
- ✅ Timeout 边界检查
- ✅ 良好的代码组织

### 发现的 6 大问题

#### 🔴 问题 1: 缺少 JSON 输出控制支持（严重）

**当前状态**：只支持简单命令字符串，无法生成现代 hooks 需要的 JSON 输出。

**缺失功能**：
- `hookSpecificOutput.permissionDecision`
- `hookSpecificOutput.additionalContext`
- `hookSpecificOutput.permissionDecisionReason`
- `continue: false` / `stopReason`

**影响**：无法实现 Reddit 案例中的核心模式

#### 🔴 问题 2: 缺少 skill-rules.json 集成（严重）

**当前状态**：完全没有任何相关代码或文档。

**需要的功能**：
- `generate_skill_rules()` - 生成模板
- `add_skill_rule()` - 添加规则
- `validate_skill_rules()` - 验证语法

#### 🟡 问题 3: 缺少所有 9 个事件的脚本模板（中等）

**当前状态**：`components/hooks/` 目录下没有任何可用的模板。

**影响**：用户需要从零开始编写脚本，学习曲线陡峭。

#### 🟡 问题 4: 缺少 Matcher 验证（中等）

**当前状态**：`add_hook()` 接受任意 matcher 字符串，不验证正则语法。

**潜在问题**：
- 无效的正则表达式
- 错误的工具名称大小写
- 在不支持 matcher 的事件中使用

#### 🟡 问题 5: 缺少事件特定字段支持（中等）

**当前状态**：`add_hook()` 不支持配置事件特定字段。

**缺失字段**：trigger, source, reason

#### 🟢 问题 6: 缺少构建检查管道生成器（低）

**理想状态**：一键生成完整的 PostToolUse + Stop 管道。

### 详细审查报告

完整报告见：`docs/CODE_REVIEW_FINDINGS.md`

---

## ✅ 第三部分：已创建的文件和脚本

### 1. 核心 Hook 脚本（4个）

#### ✅ user-prompt-submit-skill-activation.sh
- **位置**：`components/hooks/essential/`
- **事件**：UserPromptSubmit
- **用途**：Skills 自动激活系统核心（Reddit 案例最重要的创新）
- **功能**：
  - 从 stdin 读取用户提示
  - 读取 skill-rules.json 配置
  - 匹配关键词、文件模式、意图正则
  - 输出 JSON additionalContext 强制 Claude 加载技能
  - 支持 enforcement (suggest/block/warn) 和 priority 排序
- **特点**：
  - 基于 claude-code-infrastructure-showcase 的实际格式
  - 支持 DEBUG 模式（SKILL_ACTIVATION_DEBUG=true）
  - 自动检测 .claude/skills/ 下的技能文件
- **Timeout 建议**：5 秒

#### ✅ post-tool-use-file-edit-tracker.sh
- **位置**：`components/hooks/essential/`
- **事件**：PostToolUse
- **Matcher**：Edit|Write
- **用途**：记录所有文件编辑操作（配合 Stop build-checker）
- **功能**：
  - 记录到 `~/.claude/edit_log.jsonl`（JSONL 格式）
  - 记录时间戳、文件路径、工具名称、会话 ID、仓库路径
  - 非阻塞（exit 0）
  - 自动限制日志大小（保留最后 10000 条）
- **Timeout 建议**：3 秒

#### ✅ stop-build-checker.sh
- **位置**：`components/hooks/essential/`
- **事件**：Stop
- **用途**：质量门禁，批量运行构建，错误 ≥5 则阻断（Reddit 零错误秘诀）
- **功能**：
  - 读取 edit_log.jsonl 找出本会话编辑的文件
  - 按仓库分组，针对每个仓库运行构建
  - 收集错误并统计
  - 错误 ≥ 阈值（默认 5）则阻断 Stop（exit 2）
  - 建议运行 /build-and-fix 调用 build-error-resolver agent
- **配置文件**：`.claude/build-checker.json`
- **Timeout 建议**：120 秒（根据项目大小调整，官方建议 60s）

#### ✅ session-start-dev-docs-injector.sh
- **位置**：`components/hooks/essential/`
- **事件**：SessionStart
- **用途**：恢复 Dev Docs 上下文，解决跨会话"失忆"问题
- **功能**：
  - 查找活动任务目录（`.claude/dev/active/*/context.md`）
  - 读取 context.md 摘要（前 50 行）
  - 输出到 stdout（SessionStart 的 stdout 会注入到 Claude！）
  - 可选：写入 CLAUDE_ENV_FILE 持久化环境变量
- **Timeout 建议**：5 秒

### 2. 配置模板（2个）

#### ✅ skill-rules.json.template
- **位置**：`components/hooks/essential/`
- **用途**：Skills 自动激活系统的配置文件模板
- **内容**：
  - 7 个预定义技能示例（backend-dev-guidelines, frontend-dev-guidelines, skill-developer, dev-docs-workflow, database-verification, notification-developer, progressive-disclosure-pattern）
  - 详细的 promptTriggers（keywords, intentPatterns）
  - 详细的 fileTriggers（pathPatterns, pathExclusions, contentPatterns）
  - enforcement 和 priority 配置
  - 完整的注释和自定义指南
- **特点**：
  - 基于 claude-code-infrastructure-showcase 的实际生产格式
  - 包含 Reddit 案例洞察和测试指南

#### ✅ build-checker.json.template
- **位置**：`components/hooks/essential/`
- **用途**：Stop build-checker hook 的配置文件模板
- **内容**：
  - errorThreshold 配置（默认 5）
  - repos 配置（支持单仓库和 monorepo）
  - buildCommand, testCommand, skipPatterns
  - errorPatterns（自定义错误检测正则）
  - timeout 配置
  - 构建命令示例（TypeScript, Webpack, Vite, Next.js, Turbo, Nx）
  - Reddit 案例洞察和故障排除指南

### 3. 文档（2个）

#### ✅ CODE_REVIEW_FINDINGS.md
- **位置**：`docs/`
- **内容**：
  - 完整的代码审查报告
  - 评分：6.5/10
  - 6 大问题详细分析
  - 改进优先级（P0/P1/P2）
  - 建议的改进步骤（时间估算）
  - 代码质量建议

#### ✅ REDDIT_CASE_IMPLEMENTATION_SUMMARY.md（本文档）
- **位置**：`docs/`
- **内容**：完整的任务总结，包括学习成果、审查结果、创建的文件、使用指南

---

## 📖 第四部分：如何使用

### 步骤 1: 安装核心 Hook 脚本

```bash
# 1. 复制 hook 脚本到项目
cp components/hooks/essential/*.sh /path/to/your/project/.claude/hooks/

# 2. 设置可执行权限
chmod +x /path/to/your/project/.claude/hooks/*.sh

# 3. 验证权限
ls -la /path/to/your/project/.claude/hooks/*.sh
# 应该显示: -rwxr-xr-x
```

### 步骤 2: 创建配置文件

```bash
# 1. 复制配置模板
cp components/hooks/essential/skill-rules.json.template \
   /path/to/your/project/.claude/skills/skill-rules.json

cp components/hooks/essential/build-checker.json.template \
   /path/to/your/project/.claude/build-checker.json

# 2. 自定义 skill-rules.json
# ⚠️ 重要：必须修改 pathPatterns 以匹配你的项目结构！
# 打开 .claude/skills/skill-rules.json，搜索 "pathPatterns"
# 将示例路径（如 "src/routes/**/*.ts"）改为你的实际路径

# 3. 自定义 build-checker.json
# 将 "/absolute/path/to/your/project" 改为你的项目路径（使用 pwd 获取）
# 将 "npm run build" 改为你的实际构建命令
```

### 步骤 3: 配置 settings.json

添加到 `.claude/settings.json`（**不要覆盖整个文件！**）：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/user-prompt-submit-skill-activation.sh"
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-file-edit-tracker.sh"
        }],
        "timeout": 3
      }
    ],
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-build-checker.sh"
        }],
        "timeout": 120
      }
    ],
    "SessionStart": [
      {
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start-dev-docs-injector.sh"
        }],
        "timeout": 5
      }
    ]
  }
}
```

### 步骤 4: 验证安装

```bash
# 1. 验证 JSON 语法
cat .claude/skills/skill-rules.json | jq .
cat .claude/build-checker.json | jq .
cat .claude/settings.json | jq .

# 2. 测试 skill activation（需要 Claude Code 运行）
# 在 Claude Code 中输入：
# "Create a new API endpoint for user login"
# 应该看到 skill activation 提示

# 3. 测试 file tracking
# 编辑任意文件，然后检查：
cat ~/.claude/edit_log.jsonl | tail -1
# 应该看到最新的编辑记录

# 4. 启用 DEBUG 模式（可选）
export SKILL_ACTIVATION_DEBUG=true
export EDIT_TRACKER_DEBUG=true
export BUILD_CHECKER_DEBUG=true
export DEV_DOCS_DEBUG=true
```

### 步骤 5: 测试构建检查

```bash
# 1. 在 Claude Code 中编辑一些代码（引入错误）

# 2. 当 Claude 尝试停止时，build-checker 应该：
#    - 如果错误 < 5：警告但允许停止
#    - 如果错误 >= 5：阻断停止，建议运行 /build-and-fix

# 3. 手动测试构建命令（确保 buildCommand 正确）
cd /your/project && npm run build
```

---

## 🎯 第五部分：核心设计原则（Reddit 实践）

### 1. 零错误容忍
- 通过 Stop hook 构建检查器
- Reddit 团队 6 个月零错误记录

### 2. Skills 强制激活
- UserPromptSubmit hook 确保 Claude 总是使用相关技能
- 解决 Claude 不自动加载技能的核心问题

### 3. 上下文持久化
- Dev Docs 三文档系统解决 context loss 问题
- SessionStart 自动恢复上下文

### 4. 温和提醒哲学
- 大多数检查非阻塞（exit 1）
- 只有安全/质量门禁阻断（exit 2）

### 5. 渐进式披露
- 主文件 <500 行
- 详细内容在 resources/
- 按需加载

### 6. 先记录后检查
- PostToolUse 非阻塞记录
- Stop 批量检查
- 允许临时破坏，减少噪声

---

## ⚠️ 重要注意事项

### 必须自定义的配置

#### 1. skill-rules.json 的 pathPatterns ⚠️⚠️⚠️

**最重要的自定义！**

示例中的路径（如 `"src/routes/**/*.ts"`）是通用示例，**必须**改为你的实际项目结构：

```json
// 如果你的后端代码在 backend/
"pathPatterns": ["backend/**/*.ts"]

// 如果你是 monorepo
"pathPatterns": ["packages/*/src/**/*.ts"]

// 如果你用 JavaScript
"pathPatterns": ["src/**/*.js"]
```

#### 2. build-checker.json 的 repos 路径 ⚠️⚠️

**必须使用绝对路径！**

```bash
# 获取项目路径
cd /your/project
pwd
# 输出：/home/user/projects/my-app

# 在 build-checker.json 中：
{
  "repos": {
    "/home/user/projects/my-app": {
      "buildCommand": "npm run build"
    }
  }
}
```

#### 3. buildCommand 必须匹配你的项目 ⚠️

```json
// 检查 package.json 中的 scripts
{
  "scripts": {
    "build": "tsc",  // 使用这个
    "compile": "webpack"
  }
}

// 在 build-checker.json 中：
"buildCommand": "npm run build"  // 或 "tsc --noEmit"
```

### Timeout 配置建议

根据官方文档，默认 timeout 是 **60 秒**。Reddit 案例的建议：

- skill-activation: **5 秒**（快速匹配）
- file-edit-tracker: **3 秒**（只是记录）
- build-checker: **120 秒**（构建可能较慢，但不超过官方推荐的 600 秒上限）
- dev-docs-injector: **5 秒**（快速读取）

**如果项目很大**：
- 小项目：120 秒够用
- 中型项目：180 秒
- 大型 monorepo：240-300 秒

**注意**：hook timeout 和 build-checker.json 中的 timeout 应该一致！

### 不建议自动运行的功能

#### ❌ 不要在会话内自动运行 Prettier

Reddit 教训：会话内 Prettier 会消耗大量 tokens。

**替代方案**：
- SessionEnd hook 批量运行
- 手动 slash 命令
- Git pre-commit hook

#### ❌ 不要设置过低的 errorThreshold

Reddit 使用 5 作为阈值。如果设置太低（如 1），会导致：
- 频繁阻断
- 工作流中断
- 假阳性

**建议**：
- 小项目：3-5
- 中型项目：5-7
- 大型项目：7-10

---

## 📊 实施优先级

基于 Reddit 案例的经验：

### 🔴 P0 - 必须实施（核心功能）

1. **UserPromptSubmit skill-activation hook + skill-rules.json**
   - 高收益，核心提高一致性
   - 确保 Claude 总是使用相关技能

2. **Stop build-checker + PostToolUse file-tracker**
   - 防止错误遗漏
   - Reddit 6 个月零错误记录的秘诀

### 🟡 P1 - 强烈推荐（提升体验）

3. **Dev Docs workflow + SessionStart injector**
   - 解决 context loss 问题
   - 让会话可恢复

### 🟢 P2 - 可选增强（锦上添花）

4. **PM2 integration + PreToolUse gatekeeper**
   - 后端可观测性
   - 只在需要管理后端服务时使用

5. **专业化 agents**
   - 提高复杂任务执行质量
   - 后续根据需要添加

---

## 🚀 下一步计划

### 已完成 ✅

1. ✅ 分析并总结 30-逐项整理.md 和 9个Event要点.md
2. ✅ 使用 code-reviewer agent 审查代码
3. ✅ 创建 4 个核心 hook 脚本（可执行，完整功能）
4. ✅ 创建 skill-rules.json 模板（基于实际格式）
5. ✅ 创建 build-checker.json 配置模板
6. ✅ 编写详细的代码审查报告
7. ✅ 编写本总结文档

### 待完成（根据需要）

#### 阶段 1：hooks_manager.py 增强

1. **添加 JSON 模板支持**
   - `generate_json_template(event, template_type)`
   - `add_hook()` 支持 `--json-template` 参数

2. **创建 skill-rules.json 管理器**
   - `generate_skill_rules()` - 生成模板
   - `add_skill_rule()` - 添加规则
   - `validate_skill_rules()` - 验证语法

3. **添加 Matcher 验证**
   - `validate_matcher()` 函数
   - 工具名称大小写检查
   - 正则语法验证

#### 阶段 2：创建 Skills 和 Agents

4. **创建核心 Skills**（每个 <500 行）
   - backend-dev-guidelines
   - frontend-dev-guidelines
   - skill-developer
   - dev-docs-workflow
   - progressive-disclosure-pattern

5. **创建核心 Agents**
   - code-architecture-reviewer
   - build-error-resolver
   - strategic-plan-architect
   - frontend-error-fixer
   - documentation-architect

#### 阶段 3：补充 Hook 脚本

6. **创建可选 Hook 脚本**
   - PreToolUse: pm2-permission-gatekeeper.sh, sensitive-file-guard.sh
   - Stop: error-handling-reminder.sh, dev-docs-updater.sh
   - PreCompact: dev-docs-snapshot.sh
   - SessionEnd: batch-prettier.sh
   - Notification: desktop-notifier.sh

7. **创建安装脚本**
   - 一键安装向导
   - 自动检测项目结构
   - 生成自定义配置

---

## 📚 参考文档

- `/opt/claude/Claude-Kits/reference/hooks/30-逐项整理.md` - Reddit 30万行代码案例
- `/opt/claude/Claude-Kits/reference/hooks/9个Event要点.md` - 9个事件详细规范
- `/opt/claude/Claude-Kits/reference/hooks/claude_hooks_quickref.md` - 快速参考
- `/opt/claude/Claude-Kits/reference/claude-code-infrastructure-showcase/` - 生产级示例
- `Claude-code/hooks.md` - 官方 hooks 文档
- `Claude-code/hooks-guide.md` - 官方最佳实践指南
- `/opt/claude/Claude-Kits/docs/CODE_REVIEW_FINDINGS.md` - 详细代码审查报告

---

## 🎉 总结

本次任务完成了：

1. **深入学习**：从 Reddit 30万行代码经验中提炼出 9 大核心知识点
2. **代码审查**：使用 code-reviewer agent 发现 6 大问题并制定改进计划
3. **实际产出**：创建 4 个可用的核心 hook 脚本 + 2 个配置模板 + 2 个文档

**最重要的发现**：Claude 不会自动加载技能！必须通过 UserPromptSubmit Hook + skill-rules.json 强制激活。

**Reddit 案例的核心价值**：
- 零错误容忍（6 个月记录）
- Skills 强制激活（解决忽略问题）
- 先记录后检查（减少噪声）
- 温和提醒哲学（只在关键时刻阻断）

这些脚本和配置模板已经可以直接使用，只需根据自己的项目自定义配置文件即可。

---

**创建时间**：2025-11-07
**版本**：1.0
**基于**：Reddit 30万行代码案例研究 + claude-code-infrastructure-showcase 生产实践
