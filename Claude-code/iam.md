# 身份和访问管理

> 了解如何为您的组织配置Claude Code的用户身份验证、授权和访问控制。

## 身份验证方法

设置Claude Code需要访问Anthropic模型。对于团队，您可以通过以下三种方式之一设置Claude Code访问：

* 通过Claude控制台使用Claude API
* Amazon Bedrock
* Google Vertex AI

### Claude API身份验证

**通过Claude API为您的团队设置Claude Code访问：**

1. 使用您现有的Claude控制台账户或创建新的Claude控制台账户
2. 您可以通过以下任一方法添加用户：
   * 从控制台内批量邀请用户（控制台 -> 设置 -> 成员 -> 邀请）
   * [设置SSO](https://support.claude.com/en/articles/10280258-setting-up-single-sign-on-on-the-api-console)
3. 邀请用户时，他们需要以下角色之一：
   * "Claude Code"角色意味着用户只能创建Claude Code API密钥
   * "开发者"角色意味着用户可以创建任何类型的API密钥
4. 每个受邀用户需要完成以下步骤：
   * 接受控制台邀请
   * [检查系统要求](/zh-CN/docs/claude-code/setup#system-requirements)
   * [安装Claude Code](/zh-CN/docs/claude-code/setup#installation)
   * 使用控制台账户凭据登录

### 云提供商身份验证

**通过Bedrock或Vertex为您的团队设置Claude Code访问：**

1. 遵循[Bedrock文档](/zh-CN/docs/claude-code/amazon-bedrock)或[Vertex文档](/zh-CN/docs/claude-code/google-vertex-ai)
2. 向您的用户分发环境变量和生成云凭据的说明。了解更多关于如何[在此处管理配置](/zh-CN/docs/claude-code/settings)。
3. 用户可以[安装Claude Code](/zh-CN/docs/claude-code/setup#installation)

## 访问控制和权限

我们支持细粒度权限，以便您能够精确指定代理被允许做什么（例如运行测试、运行linter）以及不被允许做什么（例如更新云基础设施）。这些权限设置可以检入版本控制并分发给组织中的所有开发者，也可以由个别开发者自定义。

### 权限系统

Claude Code使用分层权限系统来平衡功能和安全性：

| 工具类型   | 示例           | 需要批准 | "是的，不要再问"行为   |
| :----- | :----------- | :--- | :------------ |
| 只读     | 文件读取、LS、Grep | 否    | 不适用           |
| Bash命令 | Shell执行      | 是    | 每个项目目录和命令永久有效 |
| 文件修改   | 编辑/写入文件      | 是    | 直到会话结束        |

### 配置权限

您可以使用`/permissions`查看和管理Claude Code的工具权限。此UI列出所有权限规则及其来源的settings.json文件。

* **允许**规则将允许Claude Code使用指定工具而无需进一步的手动批准。
* **询问**规则将在Claude Code尝试使用指定工具时要求用户确认。询问规则优先于允许规则。
* **拒绝**规则将阻止Claude Code使用指定工具。拒绝规则优先于允许和询问规则。
* **附加目录**将Claude的文件访问扩展到初始工作目录之外的目录。
* **默认模式**控制Claude在遇到新请求时的权限行为。

权限规则使用格式：`Tool`或`Tool(optional-specifier)`

仅为工具名称的规则匹配该工具的任何使用。例如，将`Bash`添加到允许规则列表中将允许Claude Code使用Bash工具而无需用户批准。

#### 权限模式

Claude Code支持几种权限模式，可以在[设置文件](/zh-CN/docs/claude-code/settings#settings-files)中设置为`defaultMode`：

| 模式                  | 描述                            |
| :------------------ | :---------------------------- |
| `default`           | 标准行为 - 在首次使用每个工具时提示权限         |
| `acceptEdits`       | 自动接受会话的文件编辑权限                 |
| `plan`              | 计划模式 - Claude可以分析但不能修改文件或执行命令 |
| `bypassPermissions` | 跳过所有权限提示（需要安全环境 - 请参阅下面的警告）   |

#### 工作目录

默认情况下，Claude可以访问启动它的目录中的文件。您可以扩展此访问权限：

* **启动期间**：使用`--add-dir <path>` CLI参数
* **会话期间**：使用`/add-dir`斜杠命令
* **持久配置**：添加到[设置文件](/zh-CN/docs/claude-code/settings#settings-files)中的`additionalDirectories`

附加目录中的文件遵循与原始工作目录相同的权限规则 - 它们变得可读而无需提示，文件编辑权限遵循当前权限模式。

#### 工具特定权限规则

一些工具支持更细粒度的权限控制：

**Bash**

* `Bash(npm run build)` 匹配确切的Bash命令`npm run build`
* `Bash(npm run test:*)` 匹配以`npm run test`开头的Bash命令
* `Bash(curl http://site.com/:*)` 匹配以确切的`curl http://site.com/`开头的curl命令

<Tip>
  Claude Code了解shell操作符（如`&&`），因此像`Bash(safe-cmd:*)`这样的前缀匹配规则不会给它运行命令`safe-cmd && other-cmd`的权限
</Tip>

<Warning>
  Bash权限模式的重要限制：

  1. 此工具使用**前缀匹配**，而不是正则表达式或glob模式
  2. 通配符`:*`只能在模式末尾使用以匹配任何延续
  3. 像`Bash(curl http://github.com/:*)`这样的模式可以通过多种方式绕过：
     * URL前的选项：`curl -X GET http://github.com/...`不会匹配
     * 不同协议：`curl https://github.com/...`不会匹配
     * 重定向：`curl -L http://bit.ly/xyz`（重定向到github）
     * 变量：`URL=http://github.com && curl $URL`不会匹配
     * 额外空格：`curl  http://github.com`不会匹配

  为了更可靠的URL过滤，请考虑：

  * 使用WebFetch工具与`WebFetch(domain:github.com)`权限
  * 通过CLAUDE.md指示Claude Code您允许的curl模式
  * 使用钩子进行自定义权限验证
</Warning>

**Read & Edit**

`Edit`规则适用于所有编辑文件的内置工具。Claude将尽力将`Read`规则应用于所有读取文件的内置工具，如Grep、Glob和LS。

Read & Edit规则都遵循[gitignore](https://git-scm.com/docs/gitignore)规范，具有四种不同的模式类型：

| 模式              | 含义                | 示例                               | 匹配                                 |
| --------------- | ----------------- | -------------------------------- | ---------------------------------- |
| `//path`        | 从文件系统根目录的**绝对**路径 | `Read(//Users/alice/secrets/**)` | `/Users/alice/secrets/**`          |
| `~/path`        | 从**家**目录的路径       | `Read(~/Documents/*.pdf)`        | `/Users/alice/Documents/*.pdf`     |
| `/path`         | **相对于设置文件**的路径    | `Edit(/src/**/*.ts)`             | `<settings file path>/src/**/*.ts` |
| `path`或`./path` | **相对于当前目录**的路径    | `Read(*.env)`                    | `<cwd>/*.env`                      |

<Warning>
  像`/Users/alice/file`这样的模式不是绝对路径 - 它相对于您的设置文件！使用`//Users/alice/file`表示绝对路径。
</Warning>

* `Edit(/docs/**)` - 在`<project>/docs/`中编辑（不是`/docs/`！）
* `Read(~/.zshrc)` - 读取您家目录的`.zshrc`
* `Edit(//tmp/scratch.txt)` - 编辑绝对路径`/tmp/scratch.txt`
* `Read(src/**)` - 从`<current-directory>/src/`读取

**WebFetch**

* `WebFetch(domain:example.com)` 匹配对example.com的获取请求

**MCP**

* `mcp__puppeteer` 匹配`puppeteer`服务器提供的任何工具（在Claude Code中配置的名称）
* `mcp__puppeteer__puppeteer_navigate` 匹配`puppeteer`服务器提供的`puppeteer_navigate`工具

<Warning>
  与其他权限类型不同，MCP权限不支持通配符（`*`）。

  要批准MCP服务器的所有工具：

  * ✅ 使用：`mcp__github`（批准所有GitHub工具）
  * ❌ 不要使用：`mcp__github__*`（不支持通配符）

  要仅批准特定工具，请列出每一个：

  * ✅ 使用：`mcp__github__get_issue`
  * ✅ 使用：`mcp__github__list_issues`
</Warning>

### 使用钩子进行额外权限控制

[Claude Code钩子](/zh-CN/docs/claude-code/hooks-guide)提供了一种注册自定义shell命令以在运行时执行权限评估的方法。当Claude Code进行工具调用时，PreToolUse钩子在权限系统运行之前运行，钩子输出可以确定是否批准或拒绝工具调用以代替权限系统。

### 企业管理策略设置

对于Claude Code的企业部署，我们支持企业管理策略设置，这些设置优先于用户和项目设置。这允许系统管理员强制执行用户无法覆盖的安全策略。

系统管理员可以将策略部署到：

* macOS：`/Library/Application Support/ClaudeCode/managed-settings.json`
* Linux和WSL：`/etc/claude-code/managed-settings.json`
* Windows：`C:\ProgramData\ClaudeCode\managed-settings.json`

这些策略文件遵循与常规[设置文件](/zh-CN/docs/claude-code/settings#settings-files)相同的格式，但不能被用户或项目设置覆盖。这确保了整个组织的一致安全策略。

### 设置优先级

当存在多个设置源时，它们按以下顺序应用（从最高到最低优先级）：

1. 企业策略
2. 命令行参数
3. 本地项目设置（`.claude/settings.local.json`）
4. 共享项目设置（`.claude/settings.json`）
5. 用户设置（`~/.claude/settings.json`）

此层次结构确保始终执行组织策略，同时在适当的情况下仍允许在项目和用户级别的灵活性。

## 凭据管理

Claude Code安全地管理您的身份验证凭据：

* **存储位置**：在macOS上，API密钥、OAuth令牌和其他凭据存储在加密的macOS钥匙串中。
* **支持的身份验证类型**：Claude.ai凭据、Claude API凭据、Bedrock Auth和Vertex Auth。
* **自定义凭据脚本**：[`apiKeyHelper`](/zh-CN/docs/claude-code/settings#available-settings)设置可以配置为运行返回API密钥的shell脚本。
* **刷新间隔**：默认情况下，`apiKeyHelper`在5分钟后或HTTP 401响应时被调用。设置`CLAUDE_CODE_API_KEY_HELPER_TTL_MS`环境变量以自定义刷新间隔。
