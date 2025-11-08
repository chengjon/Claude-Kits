# Claude Code GitLab CI/CD

> 了解如何将 Claude Code 集成到您的 GitLab CI/CD 开发工作流程中

<Info>
  Claude Code for GitLab CI/CD 目前处于测试阶段。随着我们不断完善体验，功能和特性可能会发生变化。

  此集成由 GitLab 维护。如需支持，请参阅以下 [GitLab 问题](https://gitlab.com/gitlab-org/gitlab/-/issues/573776)。
</Info>

<Note>
  此集成基于 [Claude Code CLI 和 SDK](/zh-CN/docs/claude-code/sdk) 构建，支持在您的 CI/CD 作业和自定义自动化工作流程中以编程方式使用 Claude。
</Note>

## 为什么在 GitLab 中使用 Claude Code？

* **即时 MR 创建**：描述您的需求，Claude 会提出包含更改和解释的完整 MR
* **自动化实现**：通过单个命令或提及将问题转化为可工作的代码
* **项目感知**：Claude 遵循您的 `CLAUDE.md` 指南和现有代码模式
* **简单设置**：在 `.gitlab-ci.yml` 中添加一个作业和一个掩码 CI/CD 变量
* **企业就绪**：选择 Claude API、AWS Bedrock 或 Google Vertex AI 以满足数据驻留和采购需求
* **默认安全**：在您的 GitLab 运行器中运行，具有分支保护和审批功能

## 工作原理

Claude Code 使用 GitLab CI/CD 在隔离的作业中运行 AI 任务，并通过 MR 将结果提交回来：

1. **事件驱动编排**：GitLab 监听您选择的触发器（例如，在问题、MR 或审查线程中提及 `@claude` 的评论）。作业从线程和存储库收集上下文，根据该输入构建提示，并运行 Claude Code。

2. **提供商抽象**：使用适合您环境的提供商：
   * Claude API（SaaS）
   * AWS Bedrock（基于 IAM 的访问，跨区域选项）
   * Google Vertex AI（GCP 原生，工作负载身份联合）

3. **沙盒执行**：每次交互都在具有严格网络和文件系统规则的容器中运行。Claude Code 强制执行工作区范围的权限以约束写入。每个更改都通过 MR 流转，因此审查者可以看到差异，审批仍然适用。

选择区域端点以减少延迟并满足数据主权要求，同时使用现有的云协议。

## Claude 能做什么？

Claude Code 支持强大的 CI/CD 工作流程，改变您处理代码的方式：

* 从问题描述或评论创建和更新 MR
* 分析性能回归并提出优化建议
* 直接在分支中实现功能，然后打开 MR
* 修复测试或评论识别的错误和回归
* 响应后续评论以迭代请求的更改

## 设置

### 快速设置

开始使用的最快方法是在您的 `.gitlab-ci.yml` 中添加一个最小作业，并将您的 API 密钥设置为掩码变量。

1. **添加掩码 CI/CD 变量**
   * 转到 **设置** → **CI/CD** → **变量**
   * 添加 `ANTHROPIC_API_KEY`（掩码，根据需要保护）

2. **在 `.gitlab-ci.yml` 中添加 Claude 作业**

```yaml  theme={null}
stages:
  - ai

claude:
  stage: ai
  image: node:24-alpine3.21
  # 调整规则以适应您想要触发作业的方式：
  # - 手动运行
  # - 合并请求事件
  # - 当评论包含 '@claude' 时的 web/API 触发器
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  variables:
    GIT_STRATEGY: fetch
  before_script:
    - apk update
    - apk add --no-cache git curl bash
    - npm install -g @anthropic-ai/claude-code
  script:
    # 可选：如果您的设置提供 GitLab MCP 服务器，则启动它
    - /bin/gitlab-mcp-server || true
    # 通过带有上下文负载的 web/API 触发器调用时使用 AI_FLOW_* 变量
    - echo "$AI_FLOW_INPUT for $AI_FLOW_CONTEXT on $AI_FLOW_EVENT"
    - >
      claude
      -p "${AI_FLOW_INPUT:-'Review this MR and implement the requested changes'}"
      --permission-mode acceptEdits
      --allowedTools "Bash(*) Read(*) Edit(*) Write(*) mcp__gitlab"
      --debug
```

添加作业和您的 `ANTHROPIC_API_KEY` 变量后，通过从 **CI/CD** → **流水线** 手动运行作业进行测试，或从 MR 触发它，让 Claude 在分支中提出更新并在需要时打开 MR。

<Note>
  要在 AWS Bedrock 或 Google Vertex AI 而不是 Claude API 上运行，请参阅下面的[与 AWS Bedrock 和 Google Vertex AI 一起使用](#using-with-aws-bedrock--google-vertex-ai)部分了解身份验证和环境设置。
</Note>

### 手动设置（推荐用于生产）

如果您更喜欢更受控的设置或需要企业提供商：

1. **配置提供商访问**：
   * **Claude API**：创建并存储 `ANTHROPIC_API_KEY` 作为掩码 CI/CD 变量
   * **AWS Bedrock**：**配置 GitLab** → **AWS OIDC** 并为 Bedrock 创建 IAM 角色
   * **Google Vertex AI**：**为 GitLab 配置工作负载身份联合** → **GCP**

2. **为 GitLab API 操作添加项目凭据**：
   * 默认使用 `CI_JOB_TOKEN`，或创建具有 `api` 范围的项目访问令牌
   * 如果使用 PAT，则存储为 `GITLAB_ACCESS_TOKEN`（掩码）

3. **在 `.gitlab-ci.yml` 中添加 Claude 作业**（请参阅下面的示例）

4. **（可选）启用提及驱动的触发器**：
   * 为您的事件监听器（如果您使用一个）添加"评论（注释）"的项目 webhook
   * 当评论包含 `@claude` 时，让监听器使用 `AI_FLOW_INPUT` 和 `AI_FLOW_CONTEXT` 等变量调用流水线触发器 API

## 示例用例

### 将问题转化为 MR

在问题评论中：

```
@claude implement this feature based on the issue description
```

Claude 分析问题和代码库，在分支中编写更改，并打开 MR 进行审查。

### 获得实现帮助

在 MR 讨论中：

```
@claude suggest a concrete approach to cache the results of this API call
```

Claude 提出更改，添加适当缓存的代码，并更新 MR。

### 快速修复错误

在问题或 MR 评论中：

```
@claude fix the TypeError in the user dashboard component
```

Claude 定位错误，实现修复，并更新分支或打开新的 MR。

## 与 AWS Bedrock 和 Google Vertex AI 一起使用

对于企业环境，您可以在您的云基础设施上完全运行 Claude Code，具有相同的开发者体验。

<Tabs>
  <Tab title="AWS Bedrock">
    ### 先决条件

    在使用 AWS Bedrock 设置 Claude Code 之前，您需要：

    1. 具有对所需 Claude 模型的 Amazon Bedrock 访问权限的 AWS 账户
    2. 在 AWS IAM 中配置为 OIDC 身份提供商的 GitLab
    3. 具有 Bedrock 权限和限制为您的 GitLab 项目/引用的信任策略的 IAM 角色
    4. 用于角色假设的 GitLab CI/CD 变量：
       * `AWS_ROLE_TO_ASSUME`（角色 ARN）
       * `AWS_REGION`（Bedrock 区域）

    ### 设置说明

    配置 AWS 以允许 GitLab CI 作业通过 OIDC 假设 IAM 角色（无静态密钥）。

    **必需设置：**

    1. 启用 Amazon Bedrock 并请求访问您的目标 Claude 模型
    2. 如果尚未存在，为 GitLab 创建 IAM OIDC 提供商
    3. 创建由 GitLab OIDC 提供商信任的 IAM 角色，限制为您的项目和受保护的引用
    4. 为 Bedrock 调用 API 附加最小权限

    **要在 CI/CD 变量中存储的必需值：**

    * `AWS_ROLE_TO_ASSUME`
    * `AWS_REGION`

    在设置 → CI/CD → 变量中添加变量：

    ```yaml  theme={null}
    # 对于 AWS Bedrock：
    - AWS_ROLE_TO_ASSUME
    - AWS_REGION
    ```

    使用上面的 AWS Bedrock 作业示例在运行时将 GitLab 作业令牌交换为临时 AWS 凭据。
  </Tab>

  <Tab title="Google Vertex AI">
    ### 先决条件

    在使用 Google Vertex AI 设置 Claude Code 之前，您需要：

    1. 具有以下功能的 Google Cloud 项目：
       * 启用 Vertex AI API
       * 配置工作负载身份联合以信任 GitLab OIDC
    2. 仅具有所需 Vertex AI 角色的专用服务账户
    3. 用于 WIF 的 GitLab CI/CD 变量：
       * `GCP_WORKLOAD_IDENTITY_PROVIDER`（完整资源名称）
       * `GCP_SERVICE_ACCOUNT`（服务账户电子邮件）

    ### 设置说明

    配置 Google Cloud 以允许 GitLab CI 作业通过工作负载身份联合模拟服务账户。

    **必需设置：**

    1. 启用 IAM 凭据 API、STS API 和 Vertex AI API
    2. 为 GitLab OIDC 创建工作负载身份池和提供商
    3. 创建具有 Vertex AI 角色的专用服务账户
    4. 授予 WIF 主体模拟服务账户的权限

    **要在 CI/CD 变量中存储的必需值：**

    * `GCP_WORKLOAD_IDENTITY_PROVIDER`
    * `GCP_SERVICE_ACCOUNT`

    在设置 → CI/CD → 变量中添加变量：

    ```yaml  theme={null}
    # 对于 Google Vertex AI：
    - GCP_WORKLOAD_IDENTITY_PROVIDER
    - GCP_SERVICE_ACCOUNT
    - CLOUD_ML_REGION（例如，us-east5）
    ```

    使用上面的 Google Vertex AI 作业示例在不存储密钥的情况下进行身份验证。
  </Tab>
</Tabs>

## 配置示例

以下是您可以适应到您的流水线的即用代码片段。

### 基本 .gitlab-ci.yml（Claude API）

```yaml  theme={null}
stages:
  - ai

claude:
  stage: ai
  image: node:24-alpine3.21
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  variables:
    GIT_STRATEGY: fetch
  before_script:
    - apk update
    - apk add --no-cache git curl bash
    - npm install -g @anthropic-ai/claude-code
  script:
    - /bin/gitlab-mcp-server || true
    - >
      claude
      -p "${AI_FLOW_INPUT:-'Summarize recent changes and suggest improvements'}"
      --permission-mode acceptEdits
      --allowedTools "Bash(*) Read(*) Edit(*) Write(*) mcp__gitlab"
      --debug
  # Claude Code 将使用来自 CI/CD 变量的 ANTHROPIC_API_KEY
```

### AWS Bedrock 作业示例（OIDC）

**先决条件：**

* 启用 Amazon Bedrock 并访问您选择的 Claude 模型
* 在 AWS 中配置 GitLab OIDC，具有信任您的 GitLab 项目和引用的角色
* 具有 Bedrock 权限的 IAM 角色（推荐最小权限）

**必需的 CI/CD 变量：**

* `AWS_ROLE_TO_ASSUME`：用于 Bedrock 访问的 IAM 角色的 ARN
* `AWS_REGION`：Bedrock 区域（例如，`us-west-2`）

```yaml  theme={null}
claude-bedrock:
  stage: ai
  image: node:24-alpine3.21
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
  before_script:
    - apk add --no-cache bash curl jq git python3 py3-pip
    - pip install --no-cache-dir awscli
    - npm install -g @anthropic-ai/claude-code
    # 将 GitLab OIDC 令牌交换为 AWS 凭据
    - export AWS_WEB_IDENTITY_TOKEN_FILE="${CI_JOB_JWT_FILE:-/tmp/oidc_token}"
    - if [ -n "${CI_JOB_JWT_V2}" ]; then printf "%s" "$CI_JOB_JWT_V2" > "$AWS_WEB_IDENTITY_TOKEN_FILE"; fi
    - >
      aws sts assume-role-with-web-identity
      --role-arn "$AWS_ROLE_TO_ASSUME"
      --role-session-name "gitlab-claude-$(date +%s)"
      --web-identity-token "file://$AWS_WEB_IDENTITY_TOKEN_FILE"
      --duration-seconds 3600 > /tmp/aws_creds.json
    - export AWS_ACCESS_KEY_ID="$(jq -r .Credentials.AccessKeyId /tmp/aws_creds.json)"
    - export AWS_SECRET_ACCESS_KEY="$(jq -r .Credentials.SecretAccessKey /tmp/aws_creds.json)"
    - export AWS_SESSION_TOKEN="$(jq -r .Credentials.SessionToken /tmp/aws_creds.json)"
  script:
    - /bin/gitlab-mcp-server || true
    - >
      claude
      -p "${AI_FLOW_INPUT:-'Implement the requested changes and open an MR'}"
      --permission-mode acceptEdits
      --allowedTools "Bash(*) Read(*) Edit(*) Write(*) mcp__gitlab"
      --debug
  variables:
    AWS_REGION: "us-west-2"
```

<Note>
  Bedrock 的模型 ID 包括区域特定的前缀和版本后缀（例如，`us.anthropic.claude-3-7-sonnet-20250219-v1:0`）。如果您的工作流程支持，请通过您的作业配置或提示传递所需的模型。
</Note>

### Google Vertex AI 作业示例（工作负载身份联合）

**先决条件：**

* 在您的 GCP 项目中启用 Vertex AI API
* 配置工作负载身份联合以信任 GitLab OIDC
* 具有 Vertex AI 权限的服务账户

**必需的 CI/CD 变量：**

* `GCP_WORKLOAD_IDENTITY_PROVIDER`：完整提供商资源名称
* `GCP_SERVICE_ACCOUNT`：服务账户电子邮件
* `CLOUD_ML_REGION`：Vertex 区域（例如，`us-east5`）

```yaml  theme={null}
claude-vertex:
  stage: ai
  image: gcr.io/google.com/cloudsdktool/google-cloud-cli:slim
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
  before_script:
    - apt-get update && apt-get install -y git nodejs npm && apt-get clean
    - npm install -g @anthropic-ai/claude-code
    # 通过 WIF 向 Google Cloud 进行身份验证（无下载密钥）
    - >
      gcloud auth login --cred-file=<(cat <<EOF
      {
        "type": "external_account",
        "audience": "${GCP_WORKLOAD_IDENTITY_PROVIDER}",
        "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
        "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/${GCP_SERVICE_ACCOUNT}:generateAccessToken",
        "token_url": "https://sts.googleapis.com/v1/token"
      }
      EOF
      )
    - gcloud config set project "$(gcloud projects list --format='value(projectId)' --filter="name:${CI_PROJECT_NAMESPACE}" | head -n1)" || true
  script:
    - /bin/gitlab-mcp-server || true
    - >
      CLOUD_ML_REGION="${CLOUD_ML_REGION:-us-east5}"
      claude
      -p "${AI_FLOW_INPUT:-'Review and update code as requested'}"
      --permission-mode acceptEdits
      --allowedTools "Bash(*) Read(*) Edit(*) Write(*) mcp__gitlab"
      --debug
  variables:
    CLOUD_ML_REGION: "us-east5"
```

<Note>
  使用工作负载身份联合，您不需要存储服务账户密钥。使用特定于存储库的信任条件和最小权限服务账户。
</Note>

## 最佳实践

### CLAUDE.md 配置

在存储库根目录创建一个 `CLAUDE.md` 文件来定义编码标准、审查标准和项目特定规则。Claude 在运行期间读取此文件，并在提出更改时遵循您的约定。

### 安全考虑

永远不要将 API 密钥或云凭据提交到您的存储库！始终使用 GitLab CI/CD 变量：

* 将 `ANTHROPIC_API_KEY` 添加为掩码变量（如果需要，请保护它）
* 尽可能使用特定于提供商的 OIDC（无长期密钥）
* 限制作业权限和网络出口
* 像审查任何其他贡献者一样审查 Claude 的 MR

### 优化性能

* 保持 `CLAUDE.md` 重点突出且简洁
* 提供清晰的问题/MR 描述以减少迭代
* 配置合理的作业超时以避免失控运行
* 在可能的情况下在运行器中缓存 npm 和包安装

### CI 成本

在 GitLab CI/CD 中使用 Claude Code 时，请注意相关成本：

* **GitLab 运行器时间**：
  * Claude 在您的 GitLab 运行器上运行并消耗计算分钟
  * 有关详细信息，请参阅您的 GitLab 计划的运行器计费

* **API 成本**：
  * 每次 Claude 交互都会根据提示和响应大小消耗令牌
  * 令牌使用量因任务复杂性和代码库大小而异
  * 有关详细信息，请参阅 [Anthropic 定价](/zh-CN/docs/about-claude/pricing)

* **成本优化提示**：
  * 使用特定的 `@claude` 命令以减少不必要的轮次
  * 设置适当的 `max_turns` 和作业超时值
  * 限制并发以控制并行运行

## 安全和治理

* 每个作业都在具有受限网络访问的隔离容器中运行
* Claude 的更改通过 MR 流转，因此审查者可以看到每个差异
* 分支保护和审批规则适用于 AI 生成的代码
* Claude Code 使用工作区范围的权限来约束写入
* 成本仍在您的控制之下，因为您提供自己的提供商凭据

## 故障排除

### Claude 不响应 @claude 命令

* 验证您的流水线正在被触发（手动、MR 事件或通过注释事件监听器/webhook）
* 确保 CI/CD 变量（`ANTHROPIC_API_KEY` 或云提供商设置）存在且未掩码
* 检查评论是否包含 `@claude`（不是 `/claude`）以及您的提及触发器是否已配置

### 作业无法写入评论或打开 MR

* 确保 `CI_JOB_TOKEN` 对项目具有足够的权限，或使用具有 `api` 范围的项目访问令牌
* 检查 `mcp__gitlab` 工具是否在 `--allowedTools` 中启用
* 确认作业在 MR 的上下文中运行或通过 `AI_FLOW_*` 变量具有足够的上下文

### 身份验证错误

* **对于 Claude API**：确认 `ANTHROPIC_API_KEY` 有效且未过期
* **对于 Bedrock/Vertex**：验证 OIDC/WIF 配置、角色模拟和密钥名称；确认区域和模型可用性

## 高级配置

### 常用参数和变量

Claude Code 支持这些常用输入：

* `prompt` / `prompt_file`：内联提供指令（`-p`）或通过文件
* `max_turns`：限制来回迭代的次数
* `timeout_minutes`：限制总执行时间
* `ANTHROPIC_API_KEY`：Claude API 所需（Bedrock/Vertex 不使用）
* 特定于提供商的环境：`AWS_REGION`，Vertex 的项目/区域变量

<Note>
  确切的标志和参数可能因 `@anthropic-ai/claude-code` 的版本而异。在您的作业中运行 `claude --help` 以查看支持的选项。
</Note>

### 自定义 Claude 的行为

您可以通过两种主要方式指导 Claude：

1. **CLAUDE.md**：定义编码标准、安全要求和项目约定。Claude 在运行期间读取此文件并遵循您的规则。
2. **自定义提示**：通过作业中的 `prompt`/`prompt_file` 传递特定于任务的指令。为不同的作业使用不同的提示（例如，审查、实现、重构）。
