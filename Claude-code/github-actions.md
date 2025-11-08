# Claude Code GitHub Actions

> 了解如何使用 Claude Code GitHub Actions 将 Claude Code 集成到您的开发工作流程中

Claude Code GitHub Actions 为您的 GitHub 工作流程带来 AI 驱动的自动化。只需在任何 PR 或 issue 中简单地提及 `@claude`，Claude 就可以分析您的代码、创建拉取请求、实现功能和修复错误 - 所有这些都遵循您项目的标准。

<Note>
  Claude Code GitHub Actions 基于 [Claude Code
  SDK](/zh-CN/docs/claude-code/sdk) 构建，该 SDK 支持将
  Claude Code 以编程方式集成到您的应用程序中。您可以使用 SDK 构建超越 GitHub Actions 的自定义
  自动化工作流程。
</Note>

## 为什么使用 Claude Code GitHub Actions？

* **即时 PR 创建**：描述您需要什么，Claude 就会创建一个包含所有必要更改的完整 PR
* **自动化代码实现**：通过单个命令将 issue 转换为可工作的代码
* **遵循您的标准**：Claude 尊重您的 `CLAUDE.md` 指南和现有代码模式
* **简单设置**：使用我们的安装程序和 API 密钥在几分钟内开始使用
* **默认安全**：您的代码保留在 Github 的运行器上

## Claude 能做什么？

Claude Code 提供了一个强大的 GitHub Action，可以改变您处理代码的方式：

### Claude Code Action

这个 GitHub Action 允许您在 GitHub Actions 工作流程中运行 Claude Code。您可以使用它在 Claude Code 之上构建任何自定义工作流程。

[查看仓库 →](https://github.com/anthropics/claude-code-action)

## 设置

## 快速设置

设置此 action 的最简单方法是通过终端中的 Claude Code。只需打开 claude 并运行 `/install-github-app`。

此命令将指导您设置 GitHub 应用程序和所需的密钥。

<Note>
  * 您必须是仓库管理员才能安装 GitHub 应用程序和添加密钥
  * GitHub 应用程序将请求对内容、Issues 和拉取请求的读写权限
  * 此快速启动方法仅适用于直接 Claude API 用户。如果
    您使用的是 AWS Bedrock 或 Google Vertex AI，请参阅[与 AWS
    Bedrock 和 Google Vertex AI 一起使用](#using-with-aws-bedrock-%26-google-vertex-ai)
    部分。
</Note>

## 手动设置

如果 `/install-github-app` 命令失败或您更喜欢手动设置，请按照以下手动设置说明操作：

1. **将 Claude GitHub 应用程序安装**到您的仓库：[https://github.com/apps/claude](https://github.com/apps/claude)

   Claude GitHub 应用程序需要以下仓库权限：

   * **内容**：读写（修改仓库文件）
   * **Issues**：读写（响应 issues）
   * **拉取请求**：读写（创建 PR 和推送更改）

   有关安全性和权限的更多详细信息，请参阅[安全文档](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)。
2. **将 ANTHROPIC\_API\_KEY 添加**到您的仓库密钥中（[了解如何在 GitHub Actions 中使用密钥](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)）
3. **复制工作流程文件**从 [examples/claude.yml](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml) 到您仓库的 `.github/workflows/`

<Tip>
  完成快速启动或手动设置后，通过在 issue 或 PR 评论中标记 `@claude` 来测试 action！
</Tip>

## 从 Beta 版升级

<Warning>
  Claude Code GitHub Actions v1.0 引入了破坏性更改，需要更新您的工作流程文件才能从 beta 版本升级到 v1.0。
</Warning>

如果您当前使用的是 Claude Code GitHub Actions 的 beta 版本，我们建议您更新工作流程以使用 GA 版本。新版本简化了配置，同时添加了强大的新功能，如自动模式检测。

### 基本更改

所有 beta 用户必须对其工作流程文件进行以下更改才能升级：

1. **更新 action 版本**：将 `@beta` 更改为 `@v1`
2. **删除模式配置**：删除 `mode: "tag"` 或 `mode: "agent"`（现在自动检测）
3. **更新提示输入**：将 `direct_prompt` 替换为 `prompt`
4. **移动 CLI 选项**：将 `max_turns`、`model`、`custom_instructions` 等转换为 `claude_args`

### 破坏性更改参考

| 旧 Beta 输入             | 新 v1.0 输入                        |
| --------------------- | -------------------------------- |
| `mode`                | *（已删除 - 自动检测）*                   |
| `direct_prompt`       | `prompt`                         |
| `override_prompt`     | 带有 GitHub 变量的 `prompt`           |
| `custom_instructions` | `claude_args: --system-prompt`   |
| `max_turns`           | `claude_args: --max-turns`       |
| `model`               | `claude_args: --model`           |
| `allowed_tools`       | `claude_args: --allowedTools`    |
| `disallowed_tools`    | `claude_args: --disallowedTools` |
| `claude_env`          | JSON 格式的 `settings`              |

### 前后示例

**Beta 版本：**

```yaml  theme={null}
- uses: anthropics/claude-code-action@beta
  with:
    mode: "tag"
    direct_prompt: "Review this PR for security issues"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    custom_instructions: "Follow our coding standards"
    max_turns: "10"
    model: "claude-3-5-sonnet-20241022"
```

**GA 版本（v1.0）：**

```yaml  theme={null}
- uses: anthropics/claude-code-action@v1
  with:
    prompt: "Review this PR for security issues"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    claude_args: |
      --system-prompt "Follow our coding standards"
      --max-turns 10
      --model claude-sonnet-4-5-20250929
```

<Tip>
  该 action 现在根据您的配置自动检测是在交互模式（响应 `@claude` 提及）还是自动化模式（立即使用提示运行）下运行。
</Tip>

## 示例用例

Claude Code GitHub Actions 可以帮助您处理各种任务。[示例目录](https://github.com/anthropics/claude-code-action/tree/main/examples)包含适用于不同场景的即用型工作流程。

### 基本工作流程

```yaml  theme={null}
name: Claude Code
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
jobs:
  claude:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          # 响应评论中的 @claude 提及
```

### 使用斜杠命令

```yaml  theme={null}
name: Code Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "/review"
          claude_args: "--max-turns 5"
```

### 使用提示的自定义自动化

```yaml  theme={null}
name: Daily Report
on:
  schedule:
    - cron: "0 9 * * *"
jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Generate a summary of yesterday's commits and open issues"
          claude_args: "--model claude-opus-4-1-20250805"
```

### 常见用例

在 issue 或 PR 评论中：

```
@claude implement this feature based on the issue description
@claude how should I implement user authentication for this endpoint?
@claude fix the TypeError in the user dashboard component
```

Claude 将自动分析上下文并适当响应。

## 最佳实践

### CLAUDE.md 配置

在您的仓库根目录中创建一个 `CLAUDE.md` 文件来定义代码风格指南、审查标准、项目特定规则和首选模式。此文件指导 Claude 理解您的项目标准。

### 安全考虑

<Warning>永远不要直接将 API 密钥提交到您的仓库！</Warning>

有关包括权限、身份验证和最佳实践在内的全面安全指导，请参阅 [Claude Code Action 安全文档](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)。

始终使用 GitHub Secrets 存储 API 密钥：

* 将您的 API 密钥添加为名为 `ANTHROPIC_API_KEY` 的仓库密钥
* 在工作流程中引用它：`anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`
* 将 action 权限限制为仅必要的权限
* 在合并之前审查 Claude 的建议

始终使用 GitHub Secrets（例如，`${{ secrets.ANTHROPIC_API_KEY }}`）而不是直接在工作流程文件中硬编码 API 密钥。

### 优化性能

使用 issue 模板提供上下文，保持您的 `CLAUDE.md` 简洁和专注，并为您的工作流程配置适当的超时。

### CI 成本

使用 Claude Code GitHub Actions 时，请注意相关成本：

**GitHub Actions 成本：**

* Claude Code 在 GitHub 托管的运行器上运行，这会消耗您的 GitHub Actions 分钟数
* 有关详细定价和分钟数限制，请参阅 [GitHub 的计费文档](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions)

**API 成本：**

* 每次 Claude 交互都会根据提示和响应的长度消耗 API 令牌
* 令牌使用量因任务复杂性和代码库大小而异
* 有关当前令牌费率，请参阅 [Claude 的定价页面](https://claude.com/platform/api)

**成本优化提示：**

* 使用特定的 `@claude` 命令来减少不必要的 API 调用
* 在 `claude_args` 中配置适当的 `--max-turns` 以防止过度迭代
* 设置工作流程级别的超时以避免失控的作业
* 考虑使用 GitHub 的并发控制来限制并行运行

## 配置示例

Claude Code Action v1 通过统一参数简化了配置：

```yaml  theme={null}
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: "Your instructions here" # 可选
    claude_args: "--max-turns 5" # 可选的 CLI 参数
```

主要功能：

* **统一提示接口** - 对所有指令使用 `prompt`
* **斜杠命令** - 预构建的提示，如 `/review` 或 `/fix`
* **CLI 透传** - 通过 `claude_args` 传递任何 Claude Code CLI 参数
* **灵活触发器** - 适用于任何 GitHub 事件

访问[示例目录](https://github.com/anthropics/claude-code-action/tree/main/examples)获取完整的工作流程文件。

<Tip>
  当响应 issue 或 PR 评论时，Claude 自动响应 @claude 提及。对于其他事件，使用 `prompt` 参数提供指令。
</Tip>

## 与 AWS Bedrock 和 Google Vertex AI 一起使用

对于企业环境，您可以将 Claude Code GitHub Actions 与您自己的云基础设施一起使用。这种方法让您控制数据驻留和计费，同时保持相同的功能。

### 先决条件

在使用云提供商设置 Claude Code GitHub Actions 之前，您需要：

#### 对于 Google Cloud Vertex AI：

1. 启用了 Vertex AI 的 Google Cloud 项目
2. 为 GitHub Actions 配置的工作负载身份联合
3. 具有所需权限的服务帐户
4. GitHub 应用程序（推荐）或使用默认的 GITHUB\_TOKEN

#### 对于 AWS Bedrock：

1. 启用了 Amazon Bedrock 的 AWS 账户
2. 在 AWS 中配置的 GitHub OIDC 身份提供商
3. 具有 Bedrock 权限的 IAM 角色
4. GitHub 应用程序（推荐）或使用默认的 GITHUB\_TOKEN

<Steps>
  <Step title="创建自定义 GitHub 应用程序（推荐用于第三方提供商）">
    为了在使用 Vertex AI 或 Bedrock 等第三方提供商时获得最佳控制和安全性，我们建议创建您自己的 GitHub 应用程序：

    1. 转到 [https://github.com/settings/apps/new](https://github.com/settings/apps/new)
    2. 填写基本信息：
       * **GitHub 应用程序名称**：选择一个唯一的名称（例如，"YourOrg Claude Assistant"）
       * **主页 URL**：您组织的网站或仓库 URL
    3. 配置应用程序设置：
       * **Webhooks**：取消选中"Active"（此集成不需要）
    4. 设置所需权限：
       * **仓库权限**：
         * 内容：读写
         * Issues：读写
         * 拉取请求：读写
    5. 点击"创建 GitHub 应用程序"
    6. 创建后，点击"生成私钥"并保存下载的 `.pem` 文件
    7. 从应用程序设置页面记下您的应用程序 ID
    8. 将应用程序安装到您的仓库：
       * 从您应用程序的设置页面，点击左侧边栏中的"安装应用程序"
       * 选择您的账户或组织
       * 选择"仅选择仓库"并选择特定仓库
       * 点击"安装"
    9. 将私钥作为密钥添加到您的仓库：
       * 转到您仓库的设置 → 密钥和变量 → Actions
       * 创建一个名为 `APP_PRIVATE_KEY` 的新密钥，内容为 `.pem` 文件的内容
    10. 将应用程序 ID 作为密钥添加：

    * 创建一个名为 `APP_ID` 的新密钥，值为您的 GitHub 应用程序的 ID

    <Note>
      此应用程序将与 [actions/create-github-app-token](https://github.com/actions/create-github-app-token) action 一起使用，在您的工作流程中生成身份验证令牌。
    </Note>

    **Claude API 的替代方案或如果您不想设置自己的 Github 应用程序**：使用官方 Anthropic 应用程序：

    1. 从以下位置安装：[https://github.com/apps/claude](https://github.com/apps/claude)
    2. 身份验证无需额外配置
  </Step>

  <Step title="配置云提供商身份验证">
    选择您的云提供商并设置安全身份验证：

    <AccordionGroup>
      <Accordion title="AWS Bedrock">
        **配置 AWS 以允许 GitHub Actions 安全地进行身份验证，而无需存储凭据。**

        > **安全注意事项**：使用特定于仓库的配置，并仅授予所需的最小权限。

        **所需设置**：

        1. **启用 Amazon Bedrock**：
           * 在 Amazon Bedrock 中请求访问 Claude 模型
           * 对于跨区域模型，请在所有必需区域中请求访问

        2. **设置 GitHub OIDC 身份提供商**：
           * 提供商 URL：`https://token.actions.githubusercontent.com`
           * 受众：`sts.amazonaws.com`

        3. **为 GitHub Actions 创建 IAM 角色**：
           * 受信任实体类型：Web 身份
           * 身份提供商：`token.actions.githubusercontent.com`
           * 权限：`AmazonBedrockFullAccess` 策略
           * 为您的特定仓库配置信任策略

        **所需值**：

        设置后，您需要：

        * **AWS\_ROLE\_TO\_ASSUME**：您创建的 IAM 角色的 ARN

        <Tip>
          OIDC 比使用静态 AWS 访问密钥更安全，因为凭据是临时的并且会自动轮换。
        </Tip>

        有关详细的 OIDC 设置说明，请参阅 [AWS 文档](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)。
      </Accordion>

      <Accordion title="Google Vertex AI">
        **配置 Google Cloud 以允许 GitHub Actions 安全地进行身份验证，而无需存储凭据。**

        > **安全注意事项**：使用特定于仓库的配置，并仅授予所需的最小权限。

        **所需设置**：

        1. **在您的 Google Cloud 项目中启用 API**：
           * IAM 凭据 API
           * 安全令牌服务 (STS) API
           * Vertex AI API

        2. **创建工作负载身份联合资源**：
           * 创建工作负载身份池
           * 添加 GitHub OIDC 提供商，包含：
             * 发行者：`https://token.actions.githubusercontent.com`
             * 仓库和所有者的属性映射
             * **安全建议**：使用特定于仓库的属性条件

        3. **创建服务帐户**：
           * 仅授予 `Vertex AI User` 角色
           * **安全建议**：为每个仓库创建专用服务帐户

        4. **配置 IAM 绑定**：
           * 允许工作负载身份池模拟服务帐户
           * **安全建议**：使用特定于仓库的主体集

        **所需值**：

        设置后，您需要：

        * **GCP\_WORKLOAD\_IDENTITY\_PROVIDER**：完整的提供商资源名称
        * **GCP\_SERVICE\_ACCOUNT**：服务帐户电子邮件地址

        <Tip>
          工作负载身份联合消除了对可下载服务帐户密钥的需求，提高了安全性。
        </Tip>

        有关详细的设置说明，请参阅 [Google Cloud 工作负载身份联合文档](https://cloud.google.com/iam/docs/workload-identity-federation)。
      </Accordion>
    </AccordionGroup>
  </Step>

  <Step title="添加所需密钥">
    将以下密钥添加到您的仓库（设置 → 密钥和变量 → Actions）：

    #### 对于 Claude API（直接）：

    1. **对于 API 身份验证**：
       * `ANTHROPIC_API_KEY`：您从 [console.anthropic.com](https://console.anthropic.com) 获得的 Claude API 密钥

    2. **对于 GitHub 应用程序（如果使用您自己的应用程序）**：
       * `APP_ID`：您的 GitHub 应用程序的 ID
       * `APP_PRIVATE_KEY`：私钥（.pem）内容

    #### 对于 Google Cloud Vertex AI

    1. **对于 GCP 身份验证**：
       * `GCP_WORKLOAD_IDENTITY_PROVIDER`
       * `GCP_SERVICE_ACCOUNT`

    2. **对于 GitHub 应用程序（如果使用您自己的应用程序）**：
       * `APP_ID`：您的 GitHub 应用程序的 ID
       * `APP_PRIVATE_KEY`：私钥（.pem）内容

    #### 对于 AWS Bedrock

    1. **对于 AWS 身份验证**：
       * `AWS_ROLE_TO_ASSUME`

    2. **对于 GitHub 应用程序（如果使用您自己的应用程序）**：
       * `APP_ID`：您的 GitHub 应用程序的 ID
       * `APP_PRIVATE_KEY`：私钥（.pem）内容
  </Step>

  <Step title="创建工作流程文件">
    创建与您的云提供商集成的 GitHub Actions 工作流程文件。下面的示例显示了 AWS Bedrock 和 Google Vertex AI 的完整配置：

    <AccordionGroup>
      <Accordion title="AWS Bedrock 工作流程">
        **先决条件：**

        * 启用了 AWS Bedrock 访问和 Claude 模型权限
        * 在 AWS 中配置 GitHub 作为 OIDC 身份提供商
        * 具有 Bedrock 权限且信任 GitHub Actions 的 IAM 角色

        **所需的 GitHub 密钥：**

        | 密钥名称                 | 描述                          |
        | -------------------- | --------------------------- |
        | `AWS_ROLE_TO_ASSUME` | 用于 Bedrock 访问的 IAM 角色 ARN   |
        | `APP_ID`             | 您的 GitHub 应用程序 ID（来自应用程序设置） |
        | `APP_PRIVATE_KEY`    | 您为 GitHub 应用程序生成的私钥         |

        ```yaml  theme={null}
        name: Claude PR Action

        permissions:
          contents: write
          pull-requests: write
          issues: write
          id-token: write

        on:
          issue_comment:
            types: [created]
          pull_request_review_comment:
            types: [created]
          issues:
            types: [opened, assigned]

        jobs:
          claude-pr:
            if: |
              (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
              (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
              (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
            runs-on: ubuntu-latest
            env:
              AWS_REGION: us-west-2
            steps:
              - name: Checkout repository
                uses: actions/checkout@v4

              - name: Generate GitHub App token
                id: app-token
                uses: actions/create-github-app-token@v2
                with:
                  app-id: ${{ secrets.APP_ID }}
                  private-key: ${{ secrets.APP_PRIVATE_KEY }}

              - name: Configure AWS Credentials (OIDC)
                uses: aws-actions/configure-aws-credentials@v4
                with:
                  role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
                  aws-region: us-west-2

              - uses: anthropics/claude-code-action@v1
                with:
                  github_token: ${{ steps.app-token.outputs.token }}
                  use_bedrock: "true"
                  claude_args: '--model us.anthropic.claude-sonnet-4-5-20250929-v1:0 --max-turns 10'
        ```

        <Tip>
          Bedrock 的模型 ID 格式包括区域前缀（例如，`us.anthropic.claude...`）和版本后缀。
        </Tip>
      </Accordion>

      <Accordion title="Google Vertex AI 工作流程">
        **先决条件：**

        * 在您的 GCP 项目中启用 Vertex AI API
        * 为 GitHub 配置工作负载身份联合
        * 具有 Vertex AI 权限的服务帐户

        **所需的 GitHub 密钥：**

        | 密钥名称                             | 描述                          |
        | -------------------------------- | --------------------------- |
        | `GCP_WORKLOAD_IDENTITY_PROVIDER` | 工作负载身份提供商资源名称               |
        | `GCP_SERVICE_ACCOUNT`            | 具有 Vertex AI 访问权限的服务帐户电子邮件  |
        | `APP_ID`                         | 您的 GitHub 应用程序 ID（来自应用程序设置） |
        | `APP_PRIVATE_KEY`                | 您为 GitHub 应用程序生成的私钥         |

        ```yaml  theme={null}
        name: Claude PR Action

        permissions:
          contents: write
          pull-requests: write
          issues: write
          id-token: write

        on:
          issue_comment:
            types: [created]
          pull_request_review_comment:
            types: [created]
          issues:
            types: [opened, assigned]

        jobs:
          claude-pr:
            if: |
              (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
              (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
              (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
            runs-on: ubuntu-latest
            steps:
              - name: Checkout repository
                uses: actions/checkout@v4

              - name: Generate GitHub App token
                id: app-token
                uses: actions/create-github-app-token@v2
                with:
                  app-id: ${{ secrets.APP_ID }}
                  private-key: ${{ secrets.APP_PRIVATE_KEY }}

              - name: Authenticate to Google Cloud
                id: auth
                uses: google-github-actions/auth@v2
                with:
                  workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
                  service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}

              - uses: anthropics/claude-code-action@v1
                with:
                  github_token: ${{ steps.app-token.outputs.token }}
                  trigger_phrase: "@claude"
                  use_vertex: "true"
                  claude_args: '--model claude-sonnet-4@20250514 --max-turns 10'
                env:
                  ANTHROPIC_VERTEX_PROJECT_ID: ${{ steps.auth.outputs.project_id }}
                  CLOUD_ML_REGION: us-east5
                  VERTEX_REGION_CLAUDE_3_7_SONNET: us-east5
        ```

        <Tip>
          项目 ID 会自动从 Google Cloud 身份验证步骤中检索，因此您无需硬编码它。
        </Tip>
      </Accordion>
    </AccordionGroup>
  </Step>
</Steps>

## 故障排除

### Claude 不响应 @claude 命令

验证 GitHub 应用程序是否正确安装，检查工作流程是否已启用，确保 API 密钥在仓库密钥中设置，并确认评论包含 `@claude`（不是 `/claude`）。

### CI 不在 Claude 的提交上运行

确保您使用的是 GitHub 应用程序或自定义应用程序（不是 Actions 用户），检查工作流程触发器包括必要的事件，并验证应用程序权限包括 CI 触发器。

### 身份验证错误

确认 API 密钥有效且具有足够的权限。对于 Bedrock/Vertex，检查凭据配置并确保密钥在工作流程中命名正确。

## 高级配置

### Action 参数

Claude Code Action v1 使用简化的配置：

| 参数                  | 描述                                 | 必需    |
| ------------------- | ---------------------------------- | ----- |
| `prompt`            | Claude 的指令（文本或斜杠命令）                | 否\*   |
| `claude_args`       | 传递给 Claude Code 的 CLI 参数           | 否     |
| `anthropic_api_key` | Claude API 密钥                      | 是\*\* |
| `github_token`      | 用于 API 访问的 GitHub 令牌               | 否     |
| `trigger_phrase`    | 自定义触发短语（默认："@claude"）              | 否     |
| `use_bedrock`       | 使用 AWS Bedrock 而不是 Claude API      | 否     |
| `use_vertex`        | 使用 Google Vertex AI 而不是 Claude API | 否     |

\*对于 issue/PR 评论，省略提示时，Claude 响应触发短语\
\*\*对于直接 Claude API 是必需的，对于 Bedrock/Vertex 不是必需的

#### 使用 claude\_args

`claude_args` 参数接受任何 Claude Code CLI 参数：

```yaml  theme={null}
claude_args: "--max-turns 5 --model claude-sonnet-4-5-20250929 --mcp-config /path/to/config.json"
```

常见参数：

* `--max-turns`：最大对话轮数（默认：10）
* `--model`：要使用的模型（例如，`claude-sonnet-4-5-20250929`）
* `--mcp-config`：MCP 配置的路径
* `--allowed-tools`：允许的工具的逗号分隔列表
* `--debug`：启用调试输出

### 替代集成方法

虽然 `/install-github-app` 命令是推荐的方法，但您也可以：

* **自定义 GitHub 应用程序**：对于需要品牌用户名或自定义身份验证流程的组织。创建您自己的具有所需权限（内容、issues、拉取请求）的 GitHub 应用程序，并使用 actions/create-github-app-token action 在您的工作流程中生成令牌。
* **手动 GitHub Actions**：直接工作流程配置以获得最大灵活性
* **MCP 配置**：模型上下文协议服务器的动态加载

有关身份验证、安全性和高级配置的详细指南，请参阅 [Claude Code Action 文档](https://github.com/anthropics/claude-code-action/blob/main/docs)。

### 自定义 Claude 的行为

您可以通过两种方式配置 Claude 的行为：

1. **CLAUDE.md**：在仓库根目录的 `CLAUDE.md` 文件中定义编码标准、审查标准和项目特定规则。Claude 在创建 PR 和响应请求时将遵循这些指南。查看我们的[内存文档](/zh-CN/docs/claude-code/memory)了解更多详细信息。
2. **自定义提示**：在工作流程文件中使用 `prompt` 参数提供特定于工作流程的指令。这允许您为不同的工作流程或任务自定义 Claude 的行为。

Claude 在创建 PR 和响应请求时将遵循这些指南。
