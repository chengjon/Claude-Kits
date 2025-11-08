# 快速入门

> 欢迎使用 Claude Code！

本快速入门指南将在几分钟内让你使用 AI 驱动的编码辅助。完成后，你将了解如何使用 Claude Code 完成常见的开发任务。

## 开始前

确保你拥有：

* 打开的终端或命令提示符
* 一个要处理的代码项目
* 一个 [Claude.ai](https://claude.ai)（推荐）或 [Claude Console](https://console.anthropic.com/) 账户

## 步骤 1：安装 Claude Code

### NPM 安装

如果你已安装 [Node.js 18 或更新版本](https://nodejs.org/en/download/)：

```sh  theme={null}
npm install -g @anthropic-ai/claude-code
```

### 原生安装

<Tip>
  或者，尝试我们新的原生安装，目前处于测试阶段。
</Tip>

**Homebrew (macOS, Linux)：**

```sh  theme={null}
brew install --cask claude-code
```

**macOS, Linux, WSL：**

```bash  theme={null}
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell：**

```powershell  theme={null}
irm https://claude.ai/install.ps1 | iex
```

**Windows CMD：**

```batch  theme={null}
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

## 步骤 2：登录你的账户

Claude Code 需要账户才能使用。当你使用 `claude` 命令启动交互式会话时，你需要登录：

```bash  theme={null}
claude
# 首次使用时系统会提示你登录
```

```bash  theme={null}
/login
# 按照提示使用你的账户登录
```

你可以使用以下任一账户类型登录：

* [Claude.ai](https://claude.ai)（订阅计划 - 推荐）
* [Claude Console](https://console.anthropic.com/)（API 访问，使用预付费额度）

登录后，你的凭证将被保存，你无需再次登录。

<Note>
  当你首次使用 Claude Console 账户对 Claude Code 进行身份验证时，系统会自动为你创建一个名为"Claude Code"的工作区。此工作区为你的组织中所有 Claude Code 使用情况提供集中的成本跟踪和管理。
</Note>

<Note>
  你可以在同一电子邮件地址下拥有两种账户类型。如果你需要再次登录或切换账户，请在 Claude Code 中使用 `/login` 命令。
</Note>

## 步骤 3：启动你的第一个会话

在任何项目目录中打开你的终端并启动 Claude Code：

```bash  theme={null}
cd /path/to/your/project
claude
```

你将看到 Claude Code 欢迎屏幕，其中包含你的会话信息、最近的对话和最新更新。输入 `/help` 查看可用命令，或输入 `/resume` 继续之前的对话。

<Tip>
  登录后（步骤 2），你的凭证将存储在你的系统上。在 [凭证管理](/zh-CN/docs/claude-code/iam#credential-management) 中了解更多信息。
</Tip>

## 步骤 4：提出你的第一个问题

让我们从理解你的代码库开始。尝试以下命令之一：

```
> what does this project do?
```

Claude 将分析你的文件并提供摘要。你也可以提出更具体的问题：

```
> what technologies does this project use?
```

```
> where is the main entry point?
```

```
> explain the folder structure
```

你也可以询问 Claude 关于其自身功能的问题：

```
> what can Claude Code do?
```

```
> how do I use slash commands in Claude Code?
```

```
> can Claude Code work with Docker?
```

<Note>
  Claude Code 根据需要读取你的文件 - 你无需手动添加上下文。Claude 还可以访问其自身的文档，并可以回答关于其功能和能力的问题。
</Note>

## 步骤 5：进行你的第一次代码更改

现在让我们让 Claude Code 进行一些实际的编码。尝试一个简单的任务：

```
> add a hello world function to the main file
```

Claude Code 将：

1. 找到合适的文件
2. 向你展示建议的更改
3. 请求你的批准
4. 进行编辑

<Note>
  Claude Code 在修改文件前始终会请求许可。你可以批准单个更改或为会话启用"全部接受"模式。
</Note>

## 步骤 6：在 Claude Code 中使用 Git

Claude Code 使 Git 操作变得对话式：

```
> what files have I changed?
```

```
> commit my changes with a descriptive message
```

你也可以提示进行更复杂的 Git 操作：

```
> create a new branch called feature/quickstart
```

```
> show me the last 5 commits
```

```
> help me resolve merge conflicts
```

## 步骤 7：修复 bug 或添加功能

Claude 擅长调试和功能实现。

用自然语言描述你想要的内容：

```
> add input validation to the user registration form
```

或修复现有问题：

```
> there's a bug where users can submit empty forms - fix it
```

Claude Code 将：

* 定位相关代码
* 理解上下文
* 实现解决方案
* 如果可用，运行测试

## 步骤 8：尝试其他常见工作流

有许多方式可以与 Claude 合作：

**重构代码**

```
> refactor the authentication module to use async/await instead of callbacks
```

**编写测试**

```
> write unit tests for the calculator functions
```

**更新文档**

```
> update the README with installation instructions
```

**代码审查**

```
> review my changes and suggest improvements
```

<Tip>
  **记住**：Claude Code 是你的 AI 配对程序员。像与有帮助的同事交谈一样与它交谈 - 描述你想要实现的目标，它将帮助你实现。
</Tip>

## 基本命令

以下是日常使用中最重要的命令：

| 命令                  | 功能             | 示例                                  |
| ------------------- | -------------- | ----------------------------------- |
| `claude`            | 启动交互模式         | `claude`                            |
| `claude "task"`     | 运行一次性任务        | `claude "fix the build error"`      |
| `claude -p "query"` | 运行一次性查询，然后退出   | `claude -p "explain this function"` |
| `claude -c`         | 继续最近的对话        | `claude -c`                         |
| `claude -r`         | 恢复之前的对话        | `claude -r`                         |
| `claude commit`     | 创建 Git 提交      | `claude commit`                     |
| `/clear`            | 清除对话历史         | `> /clear`                          |
| `/help`             | 显示可用命令         | `> /help`                           |
| `exit` 或 Ctrl+C     | 退出 Claude Code | `> exit`                            |

查看 [CLI 参考](/zh-CN/docs/claude-code/cli-reference) 获取完整的命令列表。

## 初学者专业提示

<AccordionGroup>
  <Accordion title="对你的请求要具体">
    不要这样说："fix the bug"

    尝试这样说："fix the login bug where users see a blank screen after entering wrong credentials"
  </Accordion>

  <Accordion title="使用分步说明">
    将复杂任务分解为步骤：

    ```
    > 1. create a new database table for user profiles
    ```

    ```
    > 2. create an API endpoint to get and update user profiles
    ```

    ```
    > 3. build a webpage that allows users to see and edit their information
    ```
  </Accordion>

  <Accordion title="让 Claude 先探索">
    在进行更改之前，让 Claude 理解你的代码：

    ```
    > analyze the database schema
    ```

    ```
    > build a dashboard showing products that are most frequently returned by our UK customers
    ```
  </Accordion>

  <Accordion title="使用快捷方式节省时间">
    * 按 `?` 查看所有可用的键盘快捷方式
    * 使用 Tab 进行命令补全
    * 按 ↑ 查看命令历史
    * 输入 `/` 查看所有斜杠命令
  </Accordion>
</AccordionGroup>

## 接下来呢？

现在你已经学习了基础知识，探索更多高级功能：

<CardGroup cols={3}>
  <Card title="常见工作流" icon="graduation-cap" href="/zh-CN/docs/claude-code/common-workflows">
    常见任务的分步指南
  </Card>

  <Card title="CLI 参考" icon="terminal" href="/zh-CN/docs/claude-code/cli-reference">
    掌握所有命令和选项
  </Card>

  <Card title="配置" icon="gear" href="/zh-CN/docs/claude-code/settings">
    为你的工作流自定义 Claude Code
  </Card>

  <Card title="网络上的 Claude Code" icon="cloud" href="/zh-CN/docs/claude-code/claude-code-on-the-web">
    在云中异步运行任务
  </Card>
</CardGroup>

## 获取帮助

* **在 Claude Code 中**：输入 `/help` 或询问"how do I..."
* **文档**：你在这里！浏览其他指南
* **社区**：加入我们的 [Discord](https://www.anthropic.com/discord) 获取提示和支持
