# Google Vertex AI 上的 Claude Code

> 了解如何通过 Google Vertex AI 配置 Claude Code，包括设置、IAM 配置和故障排除。

## 先决条件

在使用 Vertex AI 配置 Claude Code 之前，请确保您具备：

* 已启用计费的 Google Cloud Platform (GCP) 账户
* 已启用 Vertex AI API 的 GCP 项目
* 对所需 Claude 模型的访问权限（例如，Claude Sonnet 4.5）
* 已安装并配置的 Google Cloud SDK (`gcloud`)
* 在所需 GCP 区域中分配的配额

## 区域配置

Claude Code 可以与 Vertex AI [全球](https://cloud.google.com/blog/products/ai-machine-learning/global-endpoint-for-claude-models-generally-available-on-vertex-ai)和区域端点一起使用。

<Note>
  Vertex AI 可能不支持所有区域的 Claude Code 默认模型。您可能需要切换到[支持的区域或模型](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations#genai-partner-models)。
</Note>

<Note>
  Vertex AI 可能不支持全球端点上的 Claude Code 默认模型。您可能需要切换到区域端点或[支持的模型](https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-partner-models#supported_models)。
</Note>

## 设置

### 1. 启用 Vertex AI API

在您的 GCP 项目中启用 Vertex AI API：

```bash  theme={null}
# 设置您的项目 ID
gcloud config set project YOUR-PROJECT-ID

# 启用 Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

### 2. 请求模型访问权限

在 Vertex AI 中请求访问 Claude 模型：

1. 导航到 [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
2. 搜索"Claude"模型
3. 请求访问所需的 Claude 模型（例如，Claude Sonnet 4.5）
4. 等待批准（可能需要 24-48 小时）

### 3. 配置 GCP 凭据

Claude Code 使用标准的 Google Cloud 身份验证。

有关更多信息，请参阅 [Google Cloud 身份验证文档](https://cloud.google.com/docs/authentication)。

<Note>
  在进行身份验证时，Claude Code 将自动使用来自 `ANTHROPIC_VERTEX_PROJECT_ID` 环境变量的项目 ID。要覆盖此设置，请设置以下环境变量之一：`GCLOUD_PROJECT`、`GOOGLE_CLOUD_PROJECT` 或 `GOOGLE_APPLICATION_CREDENTIALS`。
</Note>

### 4. 配置 Claude Code

设置以下环境变量：

```bash  theme={null}
# 启用 Vertex AI 集成
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=global
export ANTHROPIC_VERTEX_PROJECT_ID=YOUR-PROJECT-ID

# 可选：如果需要，禁用提示缓存
export DISABLE_PROMPT_CACHING=1

# 当 CLOUD_ML_REGION=global 时，为不支持的模型覆盖区域
export VERTEX_REGION_CLAUDE_3_5_HAIKU=us-east5

# 可选：为其他特定模型覆盖区域
export VERTEX_REGION_CLAUDE_3_5_SONNET=us-east5
export VERTEX_REGION_CLAUDE_3_7_SONNET=us-east5
export VERTEX_REGION_CLAUDE_4_0_OPUS=europe-west1
export VERTEX_REGION_CLAUDE_4_0_SONNET=us-east5
export VERTEX_REGION_CLAUDE_4_1_OPUS=europe-west1
```

<Note>
  当您指定 `cache_control` 临时标志时，会自动支持[提示缓存](/zh-CN/docs/build-with-claude/prompt-caching)。要禁用它，请设置 `DISABLE_PROMPT_CACHING=1`。对于更高的速率限制，请联系 Google Cloud 支持。
</Note>

<Note>
  使用 Vertex AI 时，`/login` 和 `/logout` 命令被禁用，因为身份验证通过 Google Cloud 凭据处理。
</Note>

### 5. 模型配置

Claude Code 为 Vertex AI 使用这些默认模型：

| 模型类型    | 默认值                          |
| :------ | :--------------------------- |
| 主要模型    | `claude-sonnet-4-5@20250929` |
| 小型/快速模型 | `claude-haiku-4-5@20251001`  |

<Note>
  对于 Vertex AI 用户，Claude Code 不会自动从 Haiku 3.5 升级到 Haiku 4.5。要手动切换到较新的 Haiku 模型，请将 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 环境变量设置为完整的模型名称（例如，`claude-haiku-4-5@20251001`）。
</Note>

要自定义模型：

```bash  theme={null}
export ANTHROPIC_MODEL='claude-opus-4-1@20250805'
export ANTHROPIC_SMALL_FAST_MODEL='claude-haiku-4-5@20251001'
```

## IAM 配置

分配所需的 IAM 权限：

`roles/aiplatform.user` 角色包括所需的权限：

* `aiplatform.endpoints.predict` - 模型调用所需
* `aiplatform.endpoints.computeTokens` - 令牌计数所需

对于更严格的权限，请创建仅具有上述权限的自定义角色。

有关详细信息，请参阅 [Vertex IAM 文档](https://cloud.google.com/vertex-ai/docs/general/access-control)。

<Note>
  我们建议为 Claude Code 创建专用的 GCP 项目，以简化成本跟踪和访问控制。
</Note>

### 1M 令牌上下文窗口

Claude Sonnet 4 和 Sonnet 4.5 在 Vertex AI 上支持 [1M 令牌上下文窗口](/zh-CN/docs/build-with-claude/context-windows#1m-token-context-window)。

<Note>
  1M 令牌上下文窗口目前处于测试阶段。要使用扩展的上下文窗口，请在您的 Vertex AI 请求中包含 `context-1m-2025-08-07` 测试版标头。
</Note>

## 故障排除

如果您遇到配额问题：

* 通过 [Cloud Console](https://cloud.google.com/docs/quotas/view-manage) 检查当前配额或请求增加配额

如果您遇到"模型未找到"404 错误：

* 确认模型在 [Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) 中已启用
* 验证您有权访问指定的区域
* 如果使用 `CLOUD_ML_REGION=global`，请在 [Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) 的"支持的功能"下检查您的模型是否支持全球端点。对于不支持全球端点的模型，请执行以下操作之一：
  * 通过 `ANTHROPIC_MODEL` 或 `ANTHROPIC_SMALL_FAST_MODEL` 指定支持的模型，或
  * 使用 `VERTEX_REGION_<MODEL_NAME>` 环境变量设置区域端点

如果您遇到 429 错误：

* 对于区域端点，请确保主要模型和小型/快速模型在您选择的区域中受支持
* 考虑切换到 `CLOUD_ML_REGION=global` 以获得更好的可用性

## 其他资源

* [Vertex AI 文档](https://cloud.google.com/vertex-ai/docs)
* [Vertex AI 定价](https://cloud.google.com/vertex-ai/pricing)
* [Vertex AI 配额和限制](https://cloud.google.com/vertex-ai/docs/quotas)
