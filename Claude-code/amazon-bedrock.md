# Amazon Bedrock 上的 Claude Code

> 了解如何通过 Amazon Bedrock 配置 Claude Code，包括设置、IAM 配置和故障排除。

## 先决条件

在使用 Bedrock 配置 Claude Code 之前，请确保您具备：

* 启用了 Bedrock 访问权限的 AWS 账户
* 在 Bedrock 中访问所需的 Claude 模型（例如，Claude Sonnet 4.5）
* 已安装并配置的 AWS CLI（可选 - 仅在您没有其他获取凭证机制时需要）
* 适当的 IAM 权限

## 设置

### 1. 启用模型访问

首先，确保您在 AWS 账户中可以访问所需的 Claude 模型：

1. 导航到 [Amazon Bedrock 控制台](https://console.aws.amazon.com/bedrock/)
2. 在左侧导航中转到**模型访问**
3. 请求访问所需的 Claude 模型（例如，Claude Sonnet 4.5）
4. 等待批准（大多数地区通常是即时的）

### 2. 配置 AWS 凭证

Claude Code 使用默认的 AWS SDK 凭证链。使用以下方法之一设置您的凭证：

**选项 A：AWS CLI 配置**

```bash  theme={null}
aws configure
```

**选项 B：环境变量（访问密钥）**

```bash  theme={null}
export AWS_ACCESS_KEY_ID=your-access-key-id
export AWS_SECRET_ACCESS_KEY=your-secret-access-key
export AWS_SESSION_TOKEN=your-session-token
```

**选项 C：环境变量（SSO 配置文件）**

```bash  theme={null}
aws sso login --profile=<your-profile-name>

export AWS_PROFILE=your-profile-name
```

**选项 D：Bedrock API 密钥**

```bash  theme={null}
export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
```

Bedrock API 密钥提供了一种更简单的身份验证方法，无需完整的 AWS 凭证。[了解更多关于 Bedrock API 密钥的信息](https://aws.amazon.com/blogs/machine-learning/accelerate-ai-development-with-amazon-bedrock-api-keys/)。

#### 高级凭证配置

Claude Code 支持 AWS SSO 和企业身份提供商的自动凭证刷新。将这些设置添加到您的 Claude Code 设置文件中（有关文件位置，请参阅[设置](/zh-CN/docs/claude-code/settings)）。

当 Claude Code 检测到您的 AWS 凭证已过期（基于本地时间戳或当 Bedrock 返回凭证错误时），它将自动运行您配置的 `awsAuthRefresh` 和/或 `awsCredentialExport` 命令以获取新凭证，然后重试请求。

##### 示例配置

```json  theme={null}
{
  "awsAuthRefresh": "aws sso login --profile myprofile",
  "env": {
    "AWS_PROFILE": "myprofile"
  }
}
```

##### 配置设置说明

**`awsAuthRefresh`**：用于修改 `.aws` 目录的命令（例如，更新凭证、SSO 缓存或配置文件）。输出显示给用户（但不支持用户输入），适用于基于浏览器的身份验证流程，其中 CLI 显示要在浏览器中输入的代码。

**`awsCredentialExport`**：仅在无法修改 `.aws` 且必须直接返回凭证时使用。输出被静默捕获（不显示给用户）。命令必须输出以下格式的 JSON：

```json  theme={null}
{
  "Credentials": {
    "AccessKeyId": "value",
    "SecretAccessKey": "value",
    "SessionToken": "value"
  }
}
```

### 3. 配置 Claude Code

设置以下环境变量以启用 Bedrock：

```bash  theme={null}
# 启用 Bedrock 集成
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1  # 或您首选的地区

# 可选：覆盖小型/快速模型（Haiku）的地区
export ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION=us-west-2
```

为 Claude Code 启用 Bedrock 时，请记住以下几点：

* `AWS_REGION` 是必需的环境变量。Claude Code 不会从 `.aws` 配置文件中读取此设置。
* 使用 Bedrock 时，`/login` 和 `/logout` 命令被禁用，因为身份验证通过 AWS 凭证处理。
* 您可以使用设置文件来设置不希望泄露给其他进程的环境变量，如 `AWS_PROFILE`。有关更多信息，请参阅[设置](/zh-CN/docs/claude-code/settings)。

### 4. 模型配置

Claude Code 为 Bedrock 使用这些默认模型：

| 模型类型    | 默认值                                                |
| :------ | :------------------------------------------------- |
| 主要模型    | `global.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| 小型/快速模型 | `us.anthropic.claude-haiku-4-5-20251001-v1:0`      |

<Note>
  对于 Bedrock 用户，Claude Code 不会自动从 Haiku 3.5 升级到 Haiku 4.5。要手动切换到较新的 Haiku 模型，请将 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 环境变量设置为完整的模型名称（例如，`us.anthropic.claude-haiku-4-5-20251001-v1:0`）。
</Note>

要自定义模型，请使用以下方法之一：

```bash  theme={null}
# 使用推理配置文件 ID
export ANTHROPIC_MODEL='global.anthropic.claude-sonnet-4-5-20250929-v1:0'
export ANTHROPIC_SMALL_FAST_MODEL='us.anthropic.claude-haiku-4-5-20251001-v1:0'

# 使用应用程序推理配置文件 ARN
export ANTHROPIC_MODEL='arn:aws:bedrock:us-east-2:your-account-id:application-inference-profile/your-model-id'

# 可选：如果需要，禁用提示缓存
export DISABLE_PROMPT_CACHING=1
```

<Note>
  [提示缓存](/zh-CN/docs/build-with-claude/prompt-caching)可能在所有地区都不可用
</Note>

### 5. 输出令牌配置

在 Amazon Bedrock 上使用 Claude Code 时，我们建议以下令牌设置：

```bash  theme={null}
# Bedrock 推荐的输出令牌设置
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096
export MAX_THINKING_TOKENS=1024
```

**为什么使用这些值：**

* **`CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096`**：Bedrock 的递减限流逻辑将最少 4096 个令牌设置为 max\_token 惩罚。设置得更低不会降低成本，但可能会截断长工具使用，导致 Claude Code 代理循环持续失败。Claude Code 通常在没有扩展思考的情况下使用少于 4096 个输出令牌，但对于涉及大量文件创建或写入工具使用的任务可能需要这个余量。

* **`MAX_THINKING_TOKENS=1024`**：这为扩展思考提供了空间，而不会截断工具使用响应，同时仍保持专注的推理链。这种平衡有助于防止对编码任务特别不总是有帮助的轨迹变化。

## IAM 配置

为 Claude Code 创建具有所需权限的 IAM 策略：

```json  theme={null}
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListInferenceProfiles"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:inference-profile/*",
        "arn:aws:bedrock:*:*:application-inference-profile/*"
      ]
    }
  ]
}
```

为了更严格的权限，您可以将资源限制为特定的推理配置文件 ARN。

有关详细信息，请参阅 [Bedrock IAM 文档](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html)。

<Note>
  我们建议为 Claude Code 创建专用的 AWS 账户，以简化成本跟踪和访问控制。
</Note>

## 故障排除

如果您遇到地区问题：

* 检查模型可用性：`aws bedrock list-inference-profiles --region your-region`
* 切换到支持的地区：`export AWS_REGION=us-east-1`
* 考虑使用推理配置文件进行跨地区访问

如果您收到错误"不支持按需吞吐量"：

* 将模型指定为[推理配置文件](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) ID

Claude Code 使用 Bedrock [调用 API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModelWithResponseStream.html)，不支持对话 API。

## 其他资源

* [Bedrock 文档](https://docs.aws.amazon.com/bedrock/)
* [Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)
* [Bedrock 推理配置文件](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html)
* [Amazon Bedrock 上的 Claude Code：快速设置指南](https://community.aws/content/2tXkZKrZzlrlu0KfH8gST5Dkppq/claude-code-on-amazon-bedrock-quick-setup-guide)
* [Claude Code 监控实现（Bedrock）](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/blob/main/assets/docs/MONITORING.md)
