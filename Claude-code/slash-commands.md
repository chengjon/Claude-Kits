# 斜杠命令

> 在交互式会话中使用斜杠命令控制Claude的行为。

## 内置斜杠命令

| 命令                        | 用途                                                                                   |
| :------------------------ | :----------------------------------------------------------------------------------- |
| `/add-dir`                | 添加额外的工作目录                                                                            |
| `/agents`                 | 管理用于专门任务的自定义AI子代理                                                                    |
| `/bug`                    | 报告错误（将对话发送给Anthropic）                                                                |
| `/clear`                  | 清除对话历史                                                                               |
| `/compact [instructions]` | 压缩对话，可选的焦点说明                                                                         |
| `/config`                 | 打开设置界面（配置选项卡）                                                                        |
| `/cost`                   | 显示令牌使用统计（有关订阅特定详情，请参阅[成本跟踪指南](/zh-CN/docs/claude-code/costs#using-the-cost-command)） |
| `/doctor`                 | 检查Claude Code安装的健康状态                                                                 |
| `/help`                   | 获取使用帮助                                                                               |
| `/init`                   | 使用CLAUDE.md指南初始化项目                                                                   |
| `/login`                  | 切换Anthropic账户                                                                        |
| `/logout`                 | 从Anthropic账户登出                                                                       |
| `/mcp`                    | 管理MCP服务器连接和OAuth身份验证                                                                 |
| `/memory`                 | 编辑CLAUDE.md内存文件                                                                      |
| `/model`                  | 选择或更改AI模型                                                                            |
| `/permissions`            | 查看或更新[权限](/zh-CN/docs/claude-code/iam#configuring-permissions)                       |
| `/pr_comments`            | 查看拉取请求评论                                                                             |
| `/review`                 | 请求代码审查                                                                               |
| `/sandbox`                | 启用沙箱bash工具，具有文件系统和网络隔离，以实现更安全、更自主的执行                                                 |
| `/rewind`                 | 回退对话和/或代码                                                                            |
| `/status`                 | 打开设置界面（状态选项卡），显示版本、模型、账户和连接性                                                         |
| `/terminal-setup`         | 安装Shift+Enter键绑定以实现换行（仅限iTerm2和VSCode）                                               |
| `/usage`                  | 显示计划使用限制和速率限制状态（仅限订阅计划）                                                              |
| `/vim`                    | 进入vim模式以交替插入和命令模式                                                                    |

## 自定义斜杠命令

自定义斜杠命令允许您将经常使用的提示定义为Markdown文件，Claude Code可以执行这些文件。命令按范围（项目特定或个人）组织，并通过目录结构支持命名空间。

### 语法

```
/<command-name> [arguments]
```

#### 参数

| 参数               | 描述                             |
| :--------------- | :----------------------------- |
| `<command-name>` | 从Markdown文件名派生的名称（不包括`.md`扩展名） |
| `[arguments]`    | 传递给命令的可选参数                     |

### 命令类型

#### 项目命令

存储在您的存储库中并与您的团队共享的命令。在`/help`中列出时，这些命令在其描述后显示"(project)"。

**位置**：`.claude/commands/`

在以下示例中，我们创建`/optimize`命令：

```bash  theme={null}
# 创建项目命令
mkdir -p .claude/commands
echo "Analyze this code for performance issues and suggest optimizations:" > .claude/commands/optimize.md
```

#### 个人命令

在所有项目中可用的命令。在`/help`中列出时，这些命令在其描述后显示"(user)"。

**位置**：`~/.claude/commands/`

在以下示例中，我们创建`/security-review`命令：

```bash  theme={null}
# 创建个人命令
mkdir -p ~/.claude/commands
echo "Review this code for security vulnerabilities:" > ~/.claude/commands/security-review.md
```

### 功能

#### 命名空间

在子目录中组织命令。子目录用于组织，并在命令描述中显示，但它们不影响命令名称本身。描述将显示命令来自项目目录（`.claude/commands`）还是用户级目录（`~/.claude/commands`），以及子目录名称。

不支持用户级和项目级命令之间的冲突。否则，多个具有相同基本文件名的命令可以共存。

例如，位于`.claude/commands/frontend/component.md`的文件创建命令`/component`，描述显示"(project:frontend)"。
同时，位于`~/.claude/commands/component.md`的文件创建命令`/component`，描述显示"(user)"。

#### 参数

使用参数占位符将动态值传递给命令：

##### 使用`$ARGUMENTS`的所有参数

`$ARGUMENTS`占位符捕获传递给命令的所有参数：

```bash  theme={null}
# 命令定义
echo 'Fix issue #$ARGUMENTS following our coding standards' > .claude/commands/fix-issue.md

# 使用
> /fix-issue 123 high-priority
# $ARGUMENTS变为："123 high-priority"
```

##### 使用`$1`、`$2`等的单个参数

使用位置参数（类似于shell脚本）单独访问特定参数：

```bash  theme={null}
# 命令定义  
echo 'Review PR #$1 with priority $2 and assign to $3' > .claude/commands/review-pr.md

# 使用
> /review-pr 456 high alice
# $1变为"456"，$2变为"high"，$3变为"alice"
```

在以下情况下使用位置参数：

* 在命令的不同部分单独访问参数
* 为缺失的参数提供默认值
* 使用特定参数角色构建更结构化的命令

#### Bash命令执行

使用`!`前缀在斜杠命令运行之前执行bash命令。输出包含在命令上下文中。您\_必须\_使用Bash工具包含`allowed-tools`，但您可以选择允许的特定bash命令。

例如：

```markdown  theme={null}
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
description: Create a git commit
---

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Your task

Based on the above changes, create a single git commit.
```

#### 文件引用

使用`@`前缀在命令中包含文件内容以[引用文件](/zh-CN/docs/claude-code/common-workflows#reference-files-and-directories)。

例如：

```markdown  theme={null}
# 引用特定文件

Review the implementation in @src/utils/helpers.js

# 引用多个文件

Compare @src/old-version.js with @src/new-version.js
```

#### 思考模式

斜杠命令可以通过包含[扩展思考关键字](/zh-CN/docs/claude-code/common-workflows#use-extended-thinking)来触发扩展思考。

### 前置事项

命令文件支持前置事项，用于指定有关命令的元数据：

| 前置事项                       | 用途                                                                                      | 默认值       |
| :------------------------- | :-------------------------------------------------------------------------------------- | :-------- |
| `allowed-tools`            | 命令可以使用的工具列表                                                                             | 从对话继承     |
| `argument-hint`            | 斜杠命令期望的参数。示例：`argument-hint: add [tagId] \| remove [tagId] \| list`。此提示在自动完成斜杠命令时显示给用户。 | 无         |
| `description`              | 命令的简要描述                                                                                 | 使用提示中的第一行 |
| `model`                    | 特定模型字符串（请参阅[模型概述](/zh-CN/docs/about-claude/models/overview)）                            | 从对话继承     |
| `disable-model-invocation` | 是否防止`SlashCommand`工具调用此命令                                                               | false     |

例如：

```markdown  theme={null}
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
argument-hint: [message]
description: Create a git commit
model: claude-3-5-haiku-20241022
---

Create a git commit with message: $ARGUMENTS
```

使用位置参数的示例：

```markdown  theme={null}
---
argument-hint: [pr-number] [priority] [assignee]
description: Review pull request
---

Review PR #$1 with priority $2 and assign to $3.
Focus on security, performance, and code style.
```

## 插件命令

[插件](/zh-CN/docs/claude-code/plugins)可以提供与Claude Code无缝集成的自定义斜杠命令。插件命令的工作方式与用户定义的命令完全相同，但通过[插件市场](/zh-CN/docs/claude-code/plugin-marketplaces)分发。

### 插件命令如何工作

插件命令：

* **命名空间**：命令可以使用格式`/plugin-name:command-name`来避免冲突（除非存在名称冲突，否则插件前缀是可选的）
* **自动可用**：安装并启用插件后，其命令出现在`/help`中
* **完全集成**：支持所有命令功能（参数、前置事项、bash执行、文件引用）

### 插件命令结构

**位置**：插件根目录中的`commands/`目录

**文件格式**：带前置事项的Markdown文件

**基本命令结构**：

```markdown  theme={null}
---
description: Brief description of what the command does
---

# Command Name

Detailed instructions for Claude on how to execute this command.
Include specific guidance on parameters, expected outcomes, and any special considerations.
```

**高级命令功能**：

* **参数**：在命令描述中使用`{arg1}`等占位符
* **子目录**：在子目录中组织命令以实现命名空间
* **Bash集成**：命令可以执行shell脚本和程序
* **文件引用**：命令可以引用和修改项目文件

### 调用模式

```shell 直接命令（无冲突时） theme={null}
/command-name
```

```shell 插件前缀（需要消除歧义时） theme={null}
/plugin-name:command-name
```

```shell 带参数（如果命令支持） theme={null}
/command-name arg1 arg2
```

## MCP斜杠命令

MCP服务器可以将提示公开为斜杠命令，这些命令在Claude Code中变得可用。这些命令从连接的MCP服务器动态发现。

### 命令格式

MCP命令遵循以下模式：

```
/mcp__<server-name>__<prompt-name> [arguments]
```

### 功能

#### 动态发现

MCP命令在以下情况下自动可用：

* MCP服务器已连接并处于活动状态
* 服务器通过MCP协议公开提示
* 在连接期间成功检索提示

#### 参数

MCP提示可以接受服务器定义的参数：

```
# 无参数
> /mcp__github__list_prs

# 带参数
> /mcp__github__pr_review 456
> /mcp__jira__create_issue "Bug title" high
```

#### 命名约定

* 服务器和提示名称已规范化
* 空格和特殊字符变为下划线
* 名称为小写以保持一致性

### 管理MCP连接

使用`/mcp`命令来：

* 查看所有配置的MCP服务器
* 检查连接状态
* 使用启用OAuth的服务器进行身份验证
* 清除身份验证令牌
* 查看来自每个服务器的可用工具和提示

### MCP权限和通配符

配置[MCP工具权限](/zh-CN/docs/claude-code/iam#tool-specific-permission-rules)时，请注意**不支持通配符**：

* ✅ **正确**：`mcp__github`（批准来自github服务器的所有工具）
* ✅ **正确**：`mcp__github__get_issue`（批准特定工具）
* ❌ **不正确**：`mcp__github__*`（不支持通配符）

要批准来自MCP服务器的所有工具，只需使用服务器名称：`mcp__servername`。要仅批准特定工具，请单独列出每个工具。

## `SlashCommand`工具

`SlashCommand`工具允许Claude在对话期间以编程方式执行[自定义斜杠命令](/zh-CN/docs/claude-code/slash-commands#custom-slash-commands)。这使Claude能够在适当时代表您调用自定义命令。

为了鼓励Claude触发`SlashCommand`工具，您的说明（提示、CLAUDE.md等）通常需要使用其斜杠引用命令。

示例：

```
> Run /write-unit-test when you are about to start writing tests.
```

此工具将每个可用自定义斜杠命令的元数据放入上下文，直到达到字符预算限制。您可以使用`/context`来监视令牌使用情况，并按照以下操作来管理上下文。

### `SlashCommand`工具支持的命令

`SlashCommand`工具仅支持以下自定义斜杠命令：

* 是用户定义的。内置命令如`/compact`和`/init`\_不\_受支持。
* 已填充`description`前置事项字段。我们在上下文中使用`description`。

对于Claude Code版本>= 1.0.124，您可以通过运行`claude --debug`并触发查询来查看`SlashCommand`工具可以调用的自定义斜杠命令。

### 禁用`SlashCommand`工具

要防止Claude通过工具执行任何斜杠命令：

```bash  theme={null}
/permissions
# 添加到拒绝规则：SlashCommand
```

这也将从上下文中删除SlashCommand工具（和斜杠命令描述）。

### 仅禁用特定命令

要防止特定斜杠命令变得可用，请在斜杠命令的前置事项中添加`disable-model-invocation: true`。

这也将从上下文中删除命令的元数据。

### `SlashCommand`权限规则

权限规则支持：

* **精确匹配**：`SlashCommand:/commit`（仅允许`/commit`，无参数）
* **前缀匹配**：`SlashCommand:/review-pr:*`（允许`/review-pr`带任何参数）

### 字符预算限制

`SlashCommand`工具包括字符预算以限制显示给Claude的命令描述的大小。这可以防止在有许多命令可用时令牌溢出。

预算包括每个自定义斜杠命令的名称、参数和描述。

* **默认限制**：15,000个字符
* **自定义限制**：通过`SLASH_COMMAND_TOOL_CHAR_BUDGET`环境变量设置

当超过字符预算时，Claude将仅看到可用命令的子集。在`/context`中，警告将显示"M of N commands"。

## 技能与斜杠命令

**斜杠命令**和**代理技能**在Claude Code中服务于不同的目的：

### 使用斜杠命令

**快速、经常使用的提示**：

* 您经常使用的简单提示片段
* 快速提醒或模板
* 适合一个文件的经常使用的说明

**示例**：

* `/review` → "Review this code for bugs and suggest improvements"
* `/explain` → "Explain this code in simple terms"
* `/optimize` → "Analyze this code for performance issues"

### 使用技能

**具有结构的综合功能**：

* 具有多个步骤的复杂工作流
* 需要脚本或实用程序的功能
* 跨多个文件组织的知识
* 您想要标准化的团队工作流

**示例**：

* 带有表单填充脚本和验证的PDF处理技能
* 带有不同数据类型参考文档的数据分析技能
* 带有风格指南和模板的文档技能

### 关键差异

| 方面      | 斜杠命令             | 代理技能             |
| ------- | ---------------- | ---------------- |
| **复杂性** | 简单提示             | 复杂功能             |
| **结构**  | 单个.md文件          | 带SKILL.md +资源的目录 |
| **发现**  | 显式调用（`/command`） | 自动（基于上下文）        |
| **文件**  | 仅一个文件            | 多个文件、脚本、模板       |
| **范围**  | 项目或个人            | 项目或个人            |
| **共享**  | 通过git            | 通过git            |

### 示例比较

**作为斜杠命令**：

```markdown  theme={null}
# .claude/commands/review.md
Review this code for:
- Security vulnerabilities
- Performance issues
- Code style violations
```

使用：`/review`（手动调用）

**作为技能**：

```
.claude/skills/code-review/
├── SKILL.md (overview and workflows)
├── SECURITY.md (security checklist)
├── PERFORMANCE.md (performance patterns)
├── STYLE.md (style guide reference)
└── scripts/
    └── run-linters.sh
```

使用："Can you review this code?"（自动发现）

技能提供更丰富的上下文、验证脚本和组织的参考资料。

### 何时使用每一个

**使用斜杠命令**：

* 您重复调用相同的提示
* 提示适合单个文件
* 您想要对何时运行进行显式控制

**使用技能**：

* Claude应该自动发现功能
* 需要多个文件或脚本
* 具有验证步骤的复杂工作流
* 团队需要标准化、详细的指导

斜杠命令和技能可以共存。使用适合您需求的方法。

了解更多关于[代理技能](/zh-CN/docs/claude-code/skills)。

## 另请参阅

* [插件](/zh-CN/docs/claude-code/plugins) - 通过插件使用自定义命令扩展Claude Code
* [身份和访问管理](/zh-CN/docs/claude-code/iam) - 权限完整指南，包括MCP工具权限
* [交互模式](/zh-CN/docs/claude-code/interactive-mode) - 快捷键、输入模式和交互功能
* [CLI参考](/zh-CN/docs/claude-code/cli-reference) - 命令行标志和选项
* [设置](/zh-CN/docs/claude-code/settings) - 配置选项
* [内存管理](/zh-CN/docs/claude-code/memory) - 跨会话管理Claude的内存
