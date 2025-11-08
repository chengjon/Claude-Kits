# 迁移到 Claude Agent SDK

> 从 Claude Code TypeScript 和 Python SDK 迁移到 Claude Agent SDK 的指南

## 概述

Claude Code SDK 已重命名为 **Claude Agent SDK**，其文档也已重新组织。这一变化反映了 SDK 在构建 AI 代理方面的更广泛能力，不仅限于编码任务。

## 变化内容

| 方面             | 旧版                          | 新版                               |
| :------------- | :-------------------------- | :------------------------------- |
| **包名 (TS/JS)** | `@anthropic-ai/claude-code` | `@anthropic-ai/claude-agent-sdk` |
| **Python 包**   | `claude-code-sdk`           | `claude-agent-sdk`               |
| **文档位置**       | Claude Code 文档 → SDK 部分     | API 指南 → Agent SDK 部分            |

<Note>
  **文档变化：** Agent SDK 文档已从 Claude Code 文档移至 API 指南下的专门 [Agent SDK](/zh-CN/api/agent-sdk/overview) 部分。Claude Code 文档现在专注于 CLI 工具和自动化功能。
</Note>

## 迁移步骤

### 对于 TypeScript/JavaScript 项目

**1. 卸载旧包：**

```bash  theme={null}
npm uninstall @anthropic-ai/claude-code
```

**2. 安装新包：**

```bash  theme={null}
npm install @anthropic-ai/claude-agent-sdk
```

**3. 更新导入：**

将所有从 `@anthropic-ai/claude-code` 的导入更改为 `@anthropic-ai/claude-agent-sdk`：

```typescript  theme={null}
// 之前
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-code";

// 之后
import {
  query,
  tool,
  createSdkMcpServer,
} from "@anthropic-ai/claude-agent-sdk";
```

**4. 更新 package.json 依赖：**

如果您在 `package.json` 中列出了该包，请更新它：

```json  theme={null}
// 之前
{
  "dependencies": {
    "@anthropic-ai/claude-code": "^1.0.0"
  }
}

// 之后
{
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^0.1.0"
  }
}
```

就是这样！不需要其他代码更改。

### 对于 Python 项目

**1. 卸载旧包：**

```bash  theme={null}
pip uninstall claude-code-sdk
```

**2. 安装新包：**

```bash  theme={null}
pip install claude-agent-sdk
```

**3. 更新导入：**

将所有从 `claude_code_sdk` 的导入更改为 `claude_agent_sdk`：

```python  theme={null}
# 之前
from claude_code_sdk import query, ClaudeCodeOptions

# 之后
from claude_agent_sdk import query, ClaudeAgentOptions
```

**4. 更新类型名称：**

将 `ClaudeCodeOptions` 更改为 `ClaudeAgentOptions`：

```python  theme={null}
# 之前
from claude_agent_sdk import query, ClaudeCodeOptions

options = ClaudeCodeOptions(
    model="claude-sonnet-4-5"
)

# 之后
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    model="claude-sonnet-4-5"
)
```

**5. 查看[破坏性变化](#breaking-changes)**

进行完成迁移所需的任何代码更改。

## 破坏性变化

<Warning>
  为了改善隔离性和显式配置，Claude Agent SDK v0.1.0 为从 Claude Code SDK 迁移的用户引入了破坏性变化。在迁移前请仔细查看本节。
</Warning>

### Python：ClaudeCodeOptions 重命名为 ClaudeAgentOptions

**变化内容：** Python SDK 类型 `ClaudeCodeOptions` 已重命名为 `ClaudeAgentOptions`。

**迁移：**

```python  theme={null}
# 之前 (v0.0.x)
from claude_agent_sdk import query, ClaudeCodeOptions

options = ClaudeCodeOptions(
    model="claude-sonnet-4-5",
    permission_mode="acceptEdits"
)

# 之后 (v0.1.0)
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    permission_mode="acceptEdits"
)
```

**变化原因：** 类型名称现在与"Claude Agent SDK"品牌匹配，并在 SDK 的命名约定中提供一致性。

### 系统提示不再默认

**变化内容：** SDK 不再默认使用 Claude Code 的系统提示。

**迁移：**

<CodeGroup>
  ```typescript TypeScript theme={null}
  // 之前 (v0.0.x) - 默认使用 Claude Code 的系统提示
  const result = query({ prompt: "Hello" });

  // 之后 (v0.1.0) - 默认使用空系统提示
  // 要获得旧行为，显式请求 Claude Code 的预设：
  const result = query({
    prompt: "Hello",
    options: {
      systemPrompt: { type: "preset", preset: "claude_code" }
    }
  });

  // 或使用自定义系统提示：
  const result = query({
    prompt: "Hello",
    options: {
      systemPrompt: "You are a helpful coding assistant"
    }
  });
  ```

  ```python Python theme={null}
  # 之前 (v0.0.x) - 默认使用 Claude Code 的系统提示
  async for message in query(prompt="Hello"):
      print(message)

  # 之后 (v0.1.0) - 默认使用空系统提示
  # 要获得旧行为，显式请求 Claude Code 的预设：
  from claude_agent_sdk import query, ClaudeAgentOptions

  async for message in query(
      prompt="Hello",
      options=ClaudeAgentOptions(
          system_prompt={"type": "preset", "preset": "claude_code"}  # 使用预设
      )
  ):
      print(message)

  # 或使用自定义系统提示：
  async for message in query(
      prompt="Hello",
      options=ClaudeAgentOptions(
          system_prompt="You are a helpful coding assistant"
      )
  ):
      print(message)
  ```
</CodeGroup>

**变化原因：** 为 SDK 应用程序提供更好的控制和隔离。您现在可以构建具有自定义行为的代理，而不会继承 Claude Code 的 CLI 专用指令。

### 设置源不再默认加载

**变化内容：** SDK 不再默认从文件系统设置（CLAUDE.md、settings.json、斜杠命令等）读取。

**迁移：**

<CodeGroup>
  ```typescript TypeScript theme={null}
  // 之前 (v0.0.x) - 自动加载所有设置
  const result = query({ prompt: "Hello" });
  // 会从以下位置读取：
  // - ~/.claude/settings.json (用户)
  // - .claude/settings.json (项目)
  // - .claude/settings.local.json (本地)
  // - CLAUDE.md 文件
  // - 自定义斜杠命令

  // 之后 (v0.1.0) - 默认不加载设置
  // 要获得旧行为：
  const result = query({
    prompt: "Hello",
    options: {
      settingSources: ["user", "project", "local"]
    }
  });

  // 或只加载特定源：
  const result = query({
    prompt: "Hello",
    options: {
      settingSources: ["project"]  // 只加载项目设置
    }
  });
  ```

  ```python Python theme={null}
  # 之前 (v0.0.x) - 自动加载所有设置
  async for message in query(prompt="Hello"):
      print(message)
  # 会从以下位置读取：
  # - ~/.claude/settings.json (用户)
  # - .claude/settings.json (项目)
  # - .claude/settings.local.json (本地)
  # - CLAUDE.md 文件
  # - 自定义斜杠命令

  # 之后 (v0.1.0) - 默认不加载设置
  # 要获得旧行为：
  from claude_agent_sdk import query, ClaudeAgentOptions

  async for message in query(
      prompt="Hello",
      options=ClaudeAgentOptions(
          setting_sources=["user", "project", "local"]
      )
  ):
      print(message)

  # 或只加载特定源：
  async for message in query(
      prompt="Hello",
      options=ClaudeAgentOptions(
          setting_sources=["project"]  # 只加载项目设置
      )
  ):
      print(message)
  ```
</CodeGroup>

**变化原因：** 确保 SDK 应用程序具有独立于本地文件系统配置的可预测行为。这对以下情况特别重要：

* **CI/CD 环境** - 无本地自定义的一致行为
* **部署的应用程序** - 不依赖文件系统设置
* **测试** - 隔离的测试环境
* **多租户系统** - 防止用户之间的设置泄漏

<Note>
  **向后兼容性：** 如果您的应用程序依赖文件系统设置（自定义斜杠命令、CLAUDE.md 指令等），请在选项中添加 `settingSources: ['user', 'project', 'local']`。
</Note>

## 为什么重命名？

Claude Code SDK 最初是为编码任务设计的，但它已发展成为构建所有类型 AI 代理的强大框架。新名称"Claude Agent SDK"更好地反映了其能力：

* 构建业务代理（法律助手、财务顾问、客户支持）
* 创建专门的编码代理（SRE 机器人、安全审查员、代码审查代理）
* 为任何领域开发自定义代理，具有工具使用、MCP 集成等功能

## 获取帮助

如果您在迁移过程中遇到任何问题：

**对于 TypeScript/JavaScript：**

1. 检查所有导入是否已更新为使用 `@anthropic-ai/claude-agent-sdk`
2. 验证您的 package.json 具有新的包名
3. 运行 `npm install` 以确保依赖项已更新

**对于 Python：**

1. 检查所有导入是否已更新为使用 `claude_agent_sdk`
2. 验证您的 requirements.txt 或 pyproject.toml 具有新的包名
3. 运行 `pip install claude-agent-sdk` 以确保包已安装

查看[故障排除](/zh-CN/docs/claude-code/troubleshooting)指南了解常见问题。

## 下一步

* 探索 [Agent SDK 概述](/zh-CN/api/agent-sdk/overview)了解可用功能
* 查看 [TypeScript SDK 参考](/zh-CN/api/agent-sdk/typescript)获取详细的 API 文档
* 查看 [Python SDK 参考](/zh-CN/api/agent-sdk/python)获取 Python 特定文档
* 了解[自定义工具](/zh-CN/api/agent-sdk/custom-tools)和 [MCP 集成](/zh-CN/api/agent-sdk/mcp)
