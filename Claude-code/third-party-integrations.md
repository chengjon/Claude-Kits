# 企业部署概述

> 了解Claude Code如何与各种第三方服务和基础设施集成，以满足企业部署要求。

本页面提供了可用部署选项的概述，并帮助您为组织选择合适的配置。

## 提供商比较

<table>
  <thead>
    <tr>
      <th>功能</th>
      <th>Anthropic</th>
      <th>Amazon Bedrock</th>
      <th>Google Vertex AI</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <td>区域</td>
      <td>支持的[国家](https://www.anthropic.com/supported-countries)</td>
      <td>多个AWS[区域](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)</td>
      <td>多个GCP[区域](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations)</td>
    </tr>

    <tr>
      <td>提示缓存</td>
      <td>默认启用</td>
      <td>默认启用</td>
      <td>默认启用</td>
    </tr>

    <tr>
      <td>身份验证</td>
      <td>API密钥</td>
      <td>AWS凭证(IAM)</td>
      <td>GCP凭证(OAuth/服务账户)</td>
    </tr>

    <tr>
      <td>成本跟踪</td>
      <td>仪表板</td>
      <td>AWS Cost Explorer</td>
      <td>GCP计费</td>
    </tr>

    <tr>
      <td>企业功能</td>
      <td>团队，使用监控</td>
      <td>IAM策略，CloudTrail</td>
      <td>IAM角色，Cloud Audit Logs</td>
    </tr>
  </tbody>
</table>

## 云提供商

<CardGroup cols={2}>
  <Card title="Amazon Bedrock" icon="aws" href="/zh-CN/docs/claude-code/amazon-bedrock">
    通过AWS基础设施使用Claude模型，具有基于IAM的身份验证和AWS原生监控
  </Card>

  <Card title="Google Vertex AI" icon="google" href="/zh-CN/docs/claude-code/google-vertex-ai">
    通过Google Cloud Platform访问Claude模型，具有企业级安全性和合规性
  </Card>
</CardGroup>

## 企业基础设施

<CardGroup cols={2}>
  <Card title="企业网络" icon="shield" href="/zh-CN/docs/claude-code/network-config">
    配置Claude Code以与您组织的代理服务器和SSL/TLS要求配合使用
  </Card>

  <Card title="LLM网关" icon="server" href="/zh-CN/docs/claude-code/llm-gateway">
    部署集中式模型访问，具有使用跟踪、预算和审计日志记录
  </Card>
</CardGroup>

## 配置概述

Claude Code支持灵活的配置选项，允许您组合不同的提供商和基础设施：

<Note>
  了解以下区别：

  * **企业代理**：用于路由流量的HTTP/HTTPS代理（通过`HTTPS_PROXY`或`HTTP_PROXY`设置）
  * **LLM网关**：处理身份验证并提供与提供商兼容的端点的服务（通过`ANTHROPIC_BASE_URL`、`ANTHROPIC_BEDROCK_BASE_URL`或`ANTHROPIC_VERTEX_BASE_URL`设置）

  这两种配置可以同时使用。
</Note>

### 使用Bedrock与企业代理

通过企业HTTP/HTTPS代理路由Bedrock流量：

```bash  theme={null}
# 启用Bedrock
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1

# 配置企业代理
export HTTPS_PROXY='https://proxy.example.com:8080'
```

### 使用Bedrock与LLM网关

使用提供Bedrock兼容端点的网关服务：

```bash  theme={null}
# 启用Bedrock
export CLAUDE_CODE_USE_BEDROCK=1

# 配置LLM网关
export ANTHROPIC_BEDROCK_BASE_URL='https://your-llm-gateway.com/bedrock'
export CLAUDE_CODE_SKIP_BEDROCK_AUTH=1  # 如果网关处理AWS身份验证
```

### 使用Vertex AI与企业代理

通过企业HTTP/HTTPS代理路由Vertex AI流量：

```bash  theme={null}
# 启用Vertex
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5
export ANTHROPIC_VERTEX_PROJECT_ID=your-project-id

# 配置企业代理
export HTTPS_PROXY='https://proxy.example.com:8080'
```

### 使用Vertex AI与LLM网关

将Google Vertex AI模型与LLM网关结合使用以进行集中管理：

```bash  theme={null}
# 启用Vertex
export CLAUDE_CODE_USE_VERTEX=1

# 配置LLM网关
export ANTHROPIC_VERTEX_BASE_URL='https://your-llm-gateway.com/vertex'
export CLAUDE_CODE_SKIP_VERTEX_AUTH=1  # 如果网关处理GCP身份验证
```

### 身份验证配置

Claude Code在需要时使用`ANTHROPIC_AUTH_TOKEN`作为`Authorization`标头。`SKIP_AUTH`标志（`CLAUDE_CODE_SKIP_BEDROCK_AUTH`、`CLAUDE_CODE_SKIP_VERTEX_AUTH`）用于LLM网关场景，其中网关处理提供商身份验证。

## 选择正确的部署配置

在选择部署方法时考虑这些因素：

### 直接提供商访问

最适合以下组织：

* 希望最简单的设置
* 拥有现有的AWS或GCP基础设施
* 需要提供商原生监控和合规性

### 企业代理

最适合以下组织：

* 有现有的企业代理要求
* 需要流量监控和合规性
* 必须通过特定网络路径路由所有流量

### LLM网关

最适合以下组织：

* 需要跨团队的使用跟踪
* 希望在模型之间动态切换
* 需要自定义速率限制或预算
* 需要集中式身份验证管理

## 调试

调试部署时：

* 使用`claude /status`[斜杠命令](/zh-CN/docs/claude-code/slash-commands)。此命令提供对任何应用的身份验证、代理和URL设置的可观察性。
* 设置环境变量`export ANTHROPIC_LOG=debug`来记录请求。

## 组织最佳实践

### 1. 投资于文档和记忆

我们强烈建议投资于文档，以便Claude Code理解您的代码库。组织可以在多个级别部署CLAUDE.md文件：

* **组织范围**：部署到系统目录，如`/Library/Application Support/ClaudeCode/CLAUDE.md`（macOS）以实现公司范围的标准
* **存储库级别**：在存储库根目录中创建包含项目架构、构建命令和贡献指南的`CLAUDE.md`文件。将这些检入源代码控制，以便所有用户受益

  [了解更多](/zh-CN/docs/claude-code/memory)。

### 2. 简化部署

如果您有自定义开发环境，我们发现创建"一键"安装Claude Code的方式是在组织中推广采用的关键。

### 3. 从引导使用开始

鼓励新用户尝试使用Claude Code进行代码库问答，或处理较小的错误修复或功能请求。要求Claude Code制定计划。检查Claude的建议，如果偏离轨道则给出反馈。随着时间的推移，当用户更好地理解这种新范式时，他们将更有效地让Claude Code更自主地运行。

### 4. 配置安全策略

安全团队可以配置Claude Code允许和不允许执行的托管权限，这些权限不能被本地配置覆盖。[了解更多](/zh-CN/docs/claude-code/security)。

### 5. 利用MCP进行集成

MCP是为Claude Code提供更多信息的好方法，例如连接到票务管理系统或错误日志。我们建议一个中央团队配置MCP服务器并将`.mcp.json`配置检入代码库，以便所有用户受益。[了解更多](/zh-CN/docs/claude-code/mcp)。

在Anthropic，我们信任Claude Code为每个Anthropic代码库的开发提供动力。我们希望您像我们一样享受使用Claude Code！

## 下一步

* [设置Amazon Bedrock](/zh-CN/docs/claude-code/amazon-bedrock)进行AWS原生部署
* [配置Google Vertex AI](/zh-CN/docs/claude-code/google-vertex-ai)进行GCP部署
* [配置企业网络](/zh-CN/docs/claude-code/network-config)满足网络要求
* [部署LLM网关](/zh-CN/docs/claude-code/llm-gateway)进行企业管理
* [设置](/zh-CN/docs/claude-code/settings)配置选项和环境变量
