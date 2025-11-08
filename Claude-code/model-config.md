# 模型配置

> 了解 Claude Code 模型配置，包括像 `opusplan` 这样的模型别名

## 可用模型

对于 Claude Code 中的 `model` 设置，您可以配置：

* 一个**模型别名**
* 一个完整的\*\*[模型名称](/zh-CN/docs/about-claude/models/overview#model-names)\*\*
* 对于 Bedrock，一个 ARN

### 模型别名

模型别名提供了一种便捷的方式来选择模型设置，而无需记住确切的版本号：

| 模型别名             | 行为                                                                                                     |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| **`default`**    | 推荐的模型设置，取决于您的账户类型                                                                                      |
| **`sonnet`**     | 使用最新的 Sonnet 模型（目前是 Sonnet 4.5）进行日常编码任务                                                                |
| **`opus`**       | 使用 Opus 模型（目前是 Opus 4.1）进行专门的复杂推理任务                                                                    |
| **`haiku`**      | 使用快速高效的 Haiku 模型进行简单任务                                                                                 |
| **`sonnet[1m]`** | 使用具有[100万令牌上下文窗口](/zh-CN/docs/build-with-claude/context-windows#1m-token-context-window)的 Sonnet 进行长会话 |
| **`opusplan`**   | 特殊模式，在计划模式下使用 `opus`，然后切换到 `sonnet` 进行执行                                                               |

### 设置您的模型

您可以通过几种方式配置您的模型，按优先级顺序列出：

1. **会话期间** - 使用 `/model <alias|name>` 在会话中切换模型
2. **启动时** - 使用 `claude --model <alias|name>` 启动
3. **环境变量** - 设置 `ANTHROPIC_MODEL=<alias|name>`
4. **设置** - 使用 `model` 字段在您的设置文件中永久配置。

使用示例：

```bash  theme={null}
# 使用 Opus 启动
claude --model opus

# 在会话期间切换到 Sonnet
/model sonnet
```

示例设置文件：

```
{
    "permissions": {
        ...
    },
    "model": "opus"
}
```

## 特殊模型行为

### `default` 模型设置

`default` 的行为取决于您的账户类型。

对于某些 Max 用户，如果您使用 Opus 达到使用阈值，Claude Code 将自动回退到 Sonnet。

### `opusplan` 模型设置

`opusplan` 模型别名提供了一种自动化的混合方法：

* **在计划模式下** - 使用 `opus` 进行复杂推理和架构决策
* **在执行模式下** - 自动切换到 `sonnet` 进行代码生成和实现

这为您提供了两全其美的效果：Opus 在规划方面的卓越推理能力，以及 Sonnet 在执行方面的效率。

### 使用 \[1m] 扩展上下文

对于控制台/API 用户，可以将 `[1m]` 后缀添加到完整模型名称中以启用[100万令牌上下文窗口](/zh-CN/docs/build-with-claude/context-windows#1m-token-context-window)。

```bash  theme={null}
# 使用带有 [1m] 后缀的完整模型名称的示例
/model anthropic.claude-sonnet-4-5-20250929-v1:0[1m]
```

注意：扩展上下文模型有[不同的定价](/zh-CN/docs/about-claude/pricing#long-context-pricing)。

## 检查您当前的模型

您可以通过几种方式查看您当前使用的模型：

1. 在[状态行](/zh-CN/docs/claude-code/statusline)中（如果已配置）
2. 在 `/status` 中，它还会显示您的账户信息。

## 环境变量

您可以使用以下环境变量，它们必须是完整的**模型名称**，来控制别名映射到的模型名称。

| 环境变量                             | 描述                                                                              |
| -------------------------------- | ------------------------------------------------------------------------------- |
| `ANTHROPIC_DEFAULT_OPUS_MODEL`   | 用于 `opus` 的模型，或在计划模式激活时用于 `opusplan` 的模型。                                       |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | 用于 `sonnet` 的模型，或在计划模式未激活时用于 `opusplan` 的模型。                                    |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL`  | 用于 `haiku` 的模型，或[后台功能](/zh-CN/docs/claude-code/costs#background-token-usage)的模型 |
| `CLAUDE_CODE_SUBAGENT_MODEL`     | 用于[子代理](/zh-CN/docs/claude-code/sub-agents)的模型                                  |

注意：`ANTHROPIC_SMALL_FAST_MODEL` 已弃用，改用 `ANTHROPIC_DEFAULT_HAIKU_MODEL`。

### 提示缓存配置

Claude Code 自动使用[提示缓存](/zh-CN/docs/build-with-claude/prompt-caching)来优化性能并降低成本。您可以全局禁用提示缓存或针对特定模型层禁用：

| 环境变量                            | 描述                               |
| ------------------------------- | -------------------------------- |
| `DISABLE_PROMPT_CACHING`        | 设置为 `1` 以禁用所有模型的提示缓存（优先于每个模型的设置） |
| `DISABLE_PROMPT_CACHING_HAIKU`  | 设置为 `1` 以仅禁用 Haiku 模型的提示缓存       |
| `DISABLE_PROMPT_CACHING_SONNET` | 设置为 `1` 以仅禁用 Sonnet 模型的提示缓存      |
| `DISABLE_PROMPT_CACHING_OPUS`   | 设置为 `1` 以仅禁用 Opus 模型的提示缓存        |

这些环境变量为您提供了对提示缓存行为的细粒度控制。全局 `DISABLE_PROMPT_CACHING` 设置优先于特定模型的设置，允许您在需要时快速禁用所有缓存。每个模型的设置对于选择性控制很有用，例如在调试特定模型或使用可能具有不同缓存实现的云提供商时。
