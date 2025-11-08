# 通过 MCP 将 Claude Code 连接到工具

> 了解如何使用 Model Context Protocol 将 Claude Code 连接到您的工具。

export const MCPServersTable = ({platform = "all"}) => {
  const generateClaudeCodeCommand = server => {
    if (server.customCommands && server.customCommands.claudeCode) {
      return server.customCommands.claudeCode;
    }
    if (server.urls.http) {
      return `claude mcp add --transport http ${server.name.toLowerCase().replace(/[^a-z0-9]/g, '-')} ${server.urls.http}`;
    }
    if (server.urls.sse) {
      return `claude mcp add --transport sse ${server.name.toLowerCase().replace(/[^a-z0-9]/g, '-')} ${server.urls.sse}`;
    }
    if (server.urls.stdio) {
      const envFlags = server.authentication && server.authentication.envVars ? server.authentication.envVars.map(v => `--env ${v}=YOUR_${v.split('_').pop()}`).join(' ') : '';
      const baseCommand = `claude mcp add --transport stdio ${server.name.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;
      return envFlags ? `${baseCommand} ${envFlags} -- ${server.urls.stdio}` : `${baseCommand} -- ${server.urls.stdio}`;
    }
    return null;
  };
  const servers = [{
    name: "Airtable",
    category: "Databases & Data Management",
    description: "Read/write records, manage bases and tables",
    documentation: "https://github.com/domdomegg/airtable-mcp-server",
    urls: {
      stdio: "npx -y airtable-mcp-server"
    },
    authentication: {
      type: "api_key",
      envVars: ["AIRTABLE_API_KEY"]
    },
    availability: {
      claudeCode: true,
      mcpConnector: false,
      claudeDesktop: true
    }
  }, {
    name: "Figma",
    category: "Design & Media",
    description: "Generate better code by bringing in full Figma context",
    documentation: "https://developers.figma.com",
    urls: {
      http: "https://mcp.figma.com/mcp"
    },
    customCommands: {
      claudeCode: "claude mcp add --transport http figma-remote-mcp https://mcp.figma.com/mcp"
    },
    availability: {
      claudeCode: true,
      mcpConnector: false,
      claudeDesktop: false
    },
    notes: "Visit developers.figma.com for local server setup."
  }, {
    name: "Asana",
    category: "Project Management & Documentation",
    description: "Interact with your Asana workspace to keep projects on track",
    documentation: "https://developers.asana.com/docs/using-asanas-model-control-protocol-mcp-server",
    urls: {
      sse: "https://mcp.asana.com/sse"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Atlassian",
    category: "Project Management & Documentation",
    description: "Manage your Jira tickets and Confluence docs",
    documentation: "https://www.atlassian.com/platform/remote-mcp-server",
    urls: {
      sse: "https://mcp.atlassian.com/v1/sse"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "ClickUp",
    category: "Project Management & Documentation",
    description: "Task management, project tracking",
    documentation: "https://github.com/hauptsacheNet/clickup-mcp",
    urls: {
      stdio: "npx -y @hauptsache.net/clickup-mcp"
    },
    authentication: {
      type: "api_key",
      envVars: ["CLICKUP_API_KEY", "CLICKUP_TEAM_ID"]
    },
    availability: {
      claudeCode: true,
      mcpConnector: false,
      claudeDesktop: true
    }
  }, {
    name: "Cloudflare",
    category: "Infrastructure & DevOps",
    description: "Build applications, analyze traffic, monitor performance, and manage security settings through Cloudflare",
    documentation: "https://developers.cloudflare.com/agents/model-context-protocol/mcp-servers-for-cloudflare/",
    urls: {},
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    },
    notes: "Multiple services available. See documentation for specific server URLs. Claude Code can use the Cloudflare CLI if installed."
  }, {
    name: "Cloudinary",
    category: "Design & Media",
    description: "Upload, manage, transform, and analyze your media assets",
    documentation: "https://cloudinary.com/documentation/cloudinary_llm_mcp#mcp_servers",
    urls: {},
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    },
    notes: "Multiple services available. See documentation for specific server URLs."
  }, {
    name: "Intercom",
    category: "Project Management & Documentation",
    description: "Access real-time customer conversations, tickets, and user data",
    documentation: "https://developers.intercom.com/docs/guides/mcp",
    urls: {
      http: "https://mcp.intercom.com/mcp"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "invideo",
    category: "Design & Media",
    description: "Build video creation capabilities into your applications",
    documentation: "https://invideo.io/ai/mcp",
    urls: {
      sse: "https://mcp.invideo.io/sse"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Linear",
    category: "Project Management & Documentation",
    description: "Integrate with Linear's issue tracking and project management",
    documentation: "https://linear.app/docs/mcp",
    urls: {
      http: "https://mcp.linear.app/mcp"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Notion",
    category: "Project Management & Documentation",
    description: "Read docs, update pages, manage tasks",
    documentation: "https://developers.notion.com/docs/mcp",
    urls: {
      http: "https://mcp.notion.com/mcp"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: false,
      claudeDesktop: false
    }
  }, {
    name: "PayPal",
    category: "Payments & Commerce",
    description: "Integrate PayPal commerce capabilities, payment processing, transaction management",
    documentation: "https://www.paypal.ai/",
    urls: {
      http: "https://mcp.paypal.com/mcp"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Plaid",
    category: "Payments & Commerce",
    description: "Analyze, troubleshoot, and optimize Plaid integrations. Banking data, financial account linking",
    documentation: "https://plaid.com/blog/plaid-mcp-ai-assistant-claude/",
    urls: {
      sse: "https://api.dashboard.plaid.com/mcp/sse"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Sentry",
    category: "Development & Testing Tools",
    description: "Monitor errors, debug production issues",
    documentation: "https://docs.sentry.io/product/sentry-mcp/",
    urls: {
      http: "https://mcp.sentry.dev/mcp"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: false,
      claudeDesktop: false
    }
  }, {
    name: "Square",
    category: "Payments & Commerce",
    description: "Use an agent to build on Square APIs. Payments, inventory, orders, and more",
    documentation: "https://developer.squareup.com/docs/mcp",
    urls: {
      sse: "https://mcp.squareup.com/sse"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Socket",
    category: "Development & Testing Tools",
    description: "Security analysis for dependencies",
    documentation: "https://github.com/SocketDev/socket-mcp",
    urls: {
      http: "https://mcp.socket.dev/"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: false,
      claudeDesktop: false
    }
  }, {
    name: "Stripe",
    category: "Payments & Commerce",
    description: "Payment processing, subscription management, and financial transactions",
    documentation: "https://docs.stripe.com/mcp",
    urls: {
      http: "https://mcp.stripe.com"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Workato",
    category: "Automation & Integration",
    description: "Access any application, workflows or data via Workato, made accessible for AI",
    documentation: "https://docs.workato.com/mcp.html",
    urls: {},
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    },
    notes: "MCP servers are programmatically generated"
  }, {
    name: "Zapier",
    category: "Automation & Integration",
    description: "Connect to nearly 8,000 apps through Zapier's automation platform",
    documentation: "https://help.zapier.com/hc/en-us/articles/36265392843917",
    urls: {},
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    },
    notes: "Generate a user-specific URL at mcp.zapier.com"
  }, {
    name: "Box",
    category: "Project Management & Documentation",
    description: "Ask questions about your enterprise content, get insights from unstructured data, automate content workflows",
    documentation: "https://box.dev/guides/box-mcp/remote/",
    urls: {
      http: "https://mcp.box.com/"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Canva",
    category: "Design & Media",
    description: "Browse, summarize, autofill, and even generate new Canva designs directly from Claude",
    documentation: "https://www.canva.dev/docs/connect/canva-mcp-server-setup/",
    urls: {
      http: "https://mcp.canva.com/mcp"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Daloopa",
    category: "Databases & Data Management",
    description: "Supplies high quality fundamental financial data sourced from SEC Filings, investor presentations",
    documentation: "https://docs.daloopa.com/docs/daloopa-mcp",
    urls: {
      http: "https://mcp.daloopa.com/server/mcp"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Fireflies",
    category: "Project Management & Documentation",
    description: "Extract valuable insights from meeting transcripts and summaries",
    documentation: "https://guide.fireflies.ai/articles/8272956938-learn-about-the-fireflies-mcp-server-model-context-protocol",
    urls: {
      http: "https://api.fireflies.ai/mcp"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "HubSpot",
    category: "Databases & Data Management",
    description: "Access and manage HubSpot CRM data by fetching contacts, companies, and deals, and creating and updating records",
    documentation: "https://developers.hubspot.com/mcp",
    urls: {
      http: "https://mcp.hubspot.com/anthropic"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Hugging Face",
    category: "Development & Testing Tools",
    description: "Provides access to Hugging Face Hub information and Gradio AI Applications",
    documentation: "https://huggingface.co/settings/mcp",
    urls: {
      http: "https://huggingface.co/mcp"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Jam",
    category: "Development & Testing Tools",
    description: "Debug faster with AI agents that can access Jam recordings like video, console logs, network requests, and errors",
    documentation: "https://jam.dev/docs/debug-a-jam/mcp",
    urls: {
      http: "https://mcp.jam.dev/mcp"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Monday",
    category: "Project Management & Documentation",
    description: "Manage monday.com boards by creating items, updating columns, assigning owners, setting timelines, adding CRM activities, and writing summaries",
    documentation: "https://developer.monday.com/apps/docs/mondaycom-mcp-integration",
    urls: {
      sse: "https://mcp.monday.com/sse"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Netlify",
    category: "Infrastructure & DevOps",
    description: "Create, deploy, and manage websites on Netlify. Control all aspects of your site from creating secrets to enforcing access controls to aggregating form submissions",
    documentation: "https://docs.netlify.com/build/build-with-ai/netlify-mcp-server/",
    urls: {
      http: "https://netlify-mcp.netlify.app/mcp"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Stytch",
    category: "Infrastructure & DevOps",
    description: "Configure and manage Stytch authentication services, redirect URLs, email templates, and workspace settings",
    documentation: "https://stytch.com/docs/workspace-management/stytch-mcp",
    urls: {
      http: "http://mcp.stytch.dev/mcp"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }, {
    name: "Vercel",
    category: "Infrastructure & DevOps",
    description: "Vercel's official MCP server, allowing you to search and navigate documentation, manage projects and deployments, and analyze deployment logs—all in one place",
    documentation: "https://vercel.com/docs/mcp/vercel-mcp",
    urls: {
      http: "https://mcp.vercel.com/"
    },
    authentication: {
      type: "oauth"
    },
    availability: {
      claudeCode: true,
      mcpConnector: true,
      claudeDesktop: false
    }
  }];
  const filteredServers = servers.filter(server => {
    if (platform === "claudeCode") {
      return server.availability.claudeCode;
    } else if (platform === "mcpConnector") {
      return server.availability.mcpConnector;
    } else if (platform === "claudeDesktop") {
      return server.availability.claudeDesktop;
    } else if (platform === "all") {
      return true;
    } else {
      throw new Error(`Unknown platform: ${platform}`);
    }
  });
  const serversByCategory = filteredServers.reduce((acc, server) => {
    if (!acc[server.category]) {
      acc[server.category] = [];
    }
    acc[server.category].push(server);
    return acc;
  }, {});
  const categoryOrder = ["Development & Testing Tools", "Project Management & Documentation", "Databases & Data Management", "Payments & Commerce", "Design & Media", "Infrastructure & DevOps", "Automation & Integration"];
  return <>
      <style jsx>{`
        .cards-container {
          display: grid;
          gap: 1rem;
          margin-bottom: 2rem;
        }
        .server-card {
          border: 1px solid var(--border-color, #e5e7eb);
          border-radius: 6px;
          padding: 1rem;
        }
        .command-row {
          display: flex;
          align-items: center;
          gap: 0.25rem;
        }
        .command-row code {
          font-size: 0.75rem;
          overflow-x: auto;
        }
      `}</style>
      
      {categoryOrder.map(category => {
    if (!serversByCategory[category]) return null;
    return <div key={category}>
            <h3>{category}</h3>
            <div className="cards-container">
              {serversByCategory[category].map(server => {
      const claudeCodeCommand = generateClaudeCodeCommand(server);
      const mcpUrl = server.urls.http || server.urls.sse;
      const commandToShow = platform === "claudeCode" ? claudeCodeCommand : mcpUrl;
      return <div key={server.name} className="server-card">
                    <div>
                      {server.documentation ? <a href={server.documentation}>
                          <strong>{server.name}</strong>
                        </a> : <strong>{server.name}</strong>}
                    </div>
                    
                    <p style={{
        margin: '0.5rem 0',
        fontSize: '0.9rem'
      }}>
                      {server.description}
                      {server.notes && <span style={{
        display: 'block',
        marginTop: '0.25rem',
        fontSize: '0.8rem',
        fontStyle: 'italic',
        opacity: 0.7
      }}>
                          {server.notes}
                        </span>}
                    </p>
                    
                    {commandToShow && <>
                      <p style={{
        display: 'block',
        fontSize: '0.75rem',
        fontWeight: 500,
        minWidth: 'fit-content',
        marginTop: '0.5rem',
        marginBottom: 0
      }}>
                        {platform === "claudeCode" ? "Command" : "URL"}
                      </p>
                      <div className="command-row">
                        <code>
                          {commandToShow}
                        </code>
                      </div>
                    </>}
                  </div>;
    })}
            </div>
          </div>;
  })}
    </>;
};

Claude Code 可以通过 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction)（一个用于 AI 工具集成的开源标准）连接到数百个外部工具和数据源。MCP 服务器为 Claude Code 提供对您的工具、数据库和 API 的访问权限。

## 使用 MCP 可以做什么

连接 MCP 服务器后，您可以要求 Claude Code 执行以下操作：

* **从问题跟踪器实现功能**："添加 JIRA 问题 ENG-4521 中描述的功能，并在 GitHub 上创建 PR。"
* **分析监控数据**："检查 Sentry 和 Statsig 以检查 ENG-4521 中描述的功能的使用情况。"
* **查询数据库**："根据我们的 Postgres 数据库，查找使用功能 ENG-4521 的 10 个随机用户的电子邮件。"
* **集成设计**："根据在 Slack 中发布的新 Figma 设计更新我们的标准电子邮件模板"
* **自动化工作流**："创建 Gmail 草稿，邀请这 10 个用户参加关于新功能的反馈会议。"

## 流行的 MCP 服务器

以下是一些您可以连接到 Claude Code 的常用 MCP 服务器：

<Warning>
  使用第三方 MCP 服务器需自担风险 - Anthropic 尚未验证所有这些服务器的正确性或安全性。
  确保您信任要安装的 MCP 服务器。
  使用可能获取不受信任内容的 MCP 服务器时要特别小心，因为这些可能会使您面临提示注入风险。
</Warning>

<MCPServersTable platform="claudeCode" />

<Note>
  **需要特定的集成？** [在 GitHub 上查找数百个更多 MCP 服务器](https://github.com/modelcontextprotocol/servers)，或使用 [MCP SDK](https://modelcontextprotocol.io/quickstart/server) 构建您自己的服务器。
</Note>

## 安装 MCP 服务器

MCP 服务器可以根据您的需求以三种不同的方式进行配置：

### 选项 1：添加远程 HTTP 服务器

HTTP 服务器是连接到远程 MCP 服务器的推荐选项。这是云服务最广泛支持的传输方式。

```bash  theme={null}
# 基本语法
claude mcp add --transport http <name> <url>

# 真实示例：连接到 Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# 带有 Bearer 令牌的示例
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"
```

### 选项 2：添加远程 SSE 服务器

<Warning>
  SSE（Server-Sent Events）传输已弃用。请在可用的地方使用 HTTP 服务器。
</Warning>

```bash  theme={null}
# 基本语法
claude mcp add --transport sse <name> <url>

# 真实示例：连接到 Asana
claude mcp add --transport sse asana https://mcp.asana.com/sse

# 带有身份验证标头的示例
claude mcp add --transport sse private-api https://api.company.com/sse \
  --header "X-API-Key: your-key-here"
```

### 选项 3：添加本地 stdio 服务器

Stdio 服务器作为本地进程在您的计算机上运行。它们非常适合需要直接系统访问或自定义脚本的工具。

```bash  theme={null}
# 基本语法
claude mcp add --transport stdio <name> <command> [args...]

# 真实示例：添加 Airtable 服务器
claude mcp add --transport stdio airtable --env AIRTABLE_API_KEY=YOUR_KEY \
  -- npx -y airtable-mcp-server
```

<Note>
  **理解"--"参数：**
  `--`（双破折号）将 Claude 自己的 CLI 标志与传递给 MCP 服务器的命令和参数分开。`--` 之前的所有内容都是 Claude 的选项（如 `--env`、`--scope`），`--` 之后的所有内容都是运行 MCP 服务器的实际命令。

  例如：

  * `claude mcp add --transport stdio myserver -- npx server` → 运行 `npx server`
  * `claude mcp add --transport stdio myserver --env KEY=value -- python server.py --port 8080` → 在环境中使用 `KEY=value` 运行 `python server.py --port 8080`

  这可以防止 Claude 的标志与服务器标志之间的冲突。
</Note>

### 管理您的服务器

配置后，您可以使用以下命令管理您的 MCP 服务器：

```bash  theme={null}
# 列出所有配置的服务器
claude mcp list

# 获取特定服务器的详细信息
claude mcp get github

# 删除服务器
claude mcp remove github

# （在 Claude Code 中）检查服务器状态
/mcp
```

<Tip>
  提示：

  * 使用 `--scope` 标志指定配置的存储位置：
    * `local`（默认）：仅在当前项目中对您可用（在较旧版本中称为 `project`）
    * `project`：通过 `.mcp.json` 文件与项目中的每个人共享
    * `user`：在所有项目中对您可用（在较旧版本中称为 `global`）
  * 使用 `--env` 标志设置环境变量（例如，`--env KEY=value`）
  * 使用 MCP\_TIMEOUT 环境变量配置 MCP 服务器启动超时（例如，`MCP_TIMEOUT=10000 claude` 设置 10 秒超时）
  * 当 MCP 工具输出超过 10,000 个令牌时，Claude Code 将显示警告。要增加此限制，请设置 `MAX_MCP_OUTPUT_TOKENS` 环境变量（例如，`MAX_MCP_OUTPUT_TOKENS=50000`）
  * 使用 `/mcp` 对需要 OAuth 2.0 身份验证的远程服务器进行身份验证
</Tip>

<Warning>
  **Windows 用户**：在本机 Windows（不是 WSL）上，使用 `npx` 的本地 MCP 服务器需要 `cmd /c` 包装器以确保正确执行。

  ```bash  theme={null}
  # 这创建了 Windows 可以执行的 command="cmd"
  claude mcp add --transport stdio my-server -- cmd /c npx -y @some/package
  ```

  如果没有 `cmd /c` 包装器，您将遇到"连接已关闭"错误，因为 Windows 无法直接执行 `npx`。（有关 `--` 参数的说明，请参阅上面的注释。）
</Warning>

### 插件提供的 MCP 服务器

[插件](/zh-CN/docs/claude-code/plugins)可以捆绑 MCP 服务器，在启用插件时自动提供工具和集成。插件 MCP 服务器的工作方式与用户配置的服务器相同。

**插件 MCP 服务器的工作原理**：

* 插件在插件根目录的 `.mcp.json` 中或在 `plugin.json` 中内联定义 MCP 服务器
* 启用插件时，其 MCP 服务器会自动启动
* 插件 MCP 工具与手动配置的 MCP 工具一起出现
* 插件服务器通过插件安装进行管理（不是 `/mcp` 命令）

**示例插件 MCP 配置**：

在插件根目录的 `.mcp.json` 中：

```json  theme={null}
{
  "database-tools": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
    "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
    "env": {
      "DB_URL": "${DB_URL}"
    }
  }
}
```

或在 `plugin.json` 中内联：

```json  theme={null}
{
  "name": "my-plugin",
  "mcpServers": {
    "plugin-api": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/api-server",
      "args": ["--port", "8080"]
    }
  }
}
```

**插件 MCP 功能**：

* **自动生命周期**：服务器在插件启用时启动，但您必须重新启动 Claude Code 以应用 MCP 服务器更改（启用或禁用）
* **环境变量**：使用 `${CLAUDE_PLUGIN_ROOT}` 表示插件相对路径
* **用户环境访问**：访问与手动配置的服务器相同的环境变量
* **多种传输类型**：支持 stdio、SSE 和 HTTP 传输（传输支持可能因服务器而异）

**查看插件 MCP 服务器**：

```bash  theme={null}
# 在 Claude Code 中，查看所有 MCP 服务器，包括插件服务器
/mcp
```

插件服务器出现在列表中，并带有指示它们来自插件的指示符。

**插件 MCP 服务器的优势**：

* **捆绑分发**：工具和服务器打包在一起
* **自动设置**：无需手动 MCP 配置
* **团队一致性**：安装插件时每个人都获得相同的工具

有关使用插件捆绑 MCP 服务器的详细信息，请参阅[插件组件参考](/zh-CN/docs/claude-code/plugins-reference#mcp-servers)。

## MCP 安装范围

MCP 服务器可以在三个不同的范围级别进行配置，每个级别都用于管理服务器可访问性和共享的不同目的。了解这些范围可以帮助您确定为特定需求配置服务器的最佳方式。

### 本地范围

本地范围的服务器代表默认配置级别，存储在您的项目特定用户设置中。这些服务器对您保持私密，仅在当前项目目录中工作时才可访问。此范围非常适合个人开发服务器、实验配置或包含不应共享的敏感凭据的服务器。

```bash  theme={null}
# 添加本地范围的服务器（默认）
claude mcp add --transport http stripe https://mcp.stripe.com

# 显式指定本地范围
claude mcp add --transport http stripe --scope local https://mcp.stripe.com
```

### 项目范围

项目范围的服务器通过在项目根目录中存储配置到 `.mcp.json` 文件来启用团队协作。此文件设计为检入版本控制，确保所有团队成员都可以访问相同的 MCP 工具和服务。添加项目范围的服务器时，Claude Code 会自动创建或更新此文件，使用适当的配置结构。

```bash  theme={null}
# 添加项目范围的服务器
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp
```

生成的 `.mcp.json` 文件遵循标准化格式：

```json  theme={null}
{
  "mcpServers": {
    "shared-server": {
      "command": "/path/to/server",
      "args": [],
      "env": {}
    }
  }
}
```

出于安全原因，Claude Code 在使用来自 `.mcp.json` 文件的项目范围服务器之前会提示批准。如果您需要重置这些批准选择，请使用 `claude mcp reset-project-choices` 命令。

### 用户范围

用户范围的服务器提供跨项目可访问性，使其在您计算机上的所有项目中可用，同时对您的用户帐户保持私密。此范围适用于个人实用程序服务器、开发工具或您在不同项目中经常使用的服务。

```bash  theme={null}
# 添加用户服务器
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

### 选择正确的范围

根据以下条件选择您的范围：

* **本地范围**：个人服务器、实验配置或特定于一个项目的敏感凭据
* **项目范围**：团队共享的服务器、项目特定的工具或协作所需的服务
* **用户范围**：跨多个项目需要的个人实用程序、开发工具或经常使用的服务

### 范围层次结构和优先级

MCP 服务器配置遵循明确的优先级层次结构。当具有相同名称的服务器存在于多个范围时，系统通过首先优先考虑本地范围的服务器、其次是项目范围的服务器，最后是用户范围的服务器来解决冲突。此设计确保个人配置可以在需要时覆盖共享配置。

### `.mcp.json` 中的环境变量扩展

Claude Code 支持 `.mcp.json` 文件中的环境变量扩展，允许团队共享配置，同时为特定于机器的路径和 API 密钥等敏感值保持灵活性。

**支持的语法：**

* `${VAR}` - 扩展为环境变量 `VAR` 的值
* `${VAR:-default}` - 如果设置了 `VAR`，则扩展为 `VAR`，否则使用 `default`

**扩展位置：**
环境变量可以在以下位置扩展：

* `command` - 服务器可执行文件路径
* `args` - 命令行参数
* `env` - 传递给服务器的环境变量
* `url` - 对于 HTTP 服务器类型
* `headers` - 对于 HTTP 服务器身份验证

**带有变量扩展的示例：**

```json  theme={null}
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

如果未设置所需的环境变量且没有默认值，Claude Code 将无法解析配置。

## 实际示例

{/* ### 示例：使用 Playwright 自动化浏览器测试

  ```bash
  # 1. 添加 Playwright MCP 服务器
  claude mcp add --transport stdio playwright -- npx -y @playwright/mcp@latest

  # 2. 编写并运行浏览器测试
  > "Test if the login flow works with test@example.com"
  > "Take a screenshot of the checkout page on mobile"
  > "Verify that the search feature returns results"
  ``` */}

### 示例：使用 Sentry 监控错误

```bash  theme={null}
# 1. 添加 Sentry MCP 服务器
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# 2. 使用 /mcp 对您的 Sentry 帐户进行身份验证
> /mcp

# 3. 调试生产问题
> "过去 24 小时内最常见的错误是什么？"
> "显示错误 ID abc123 的堆栈跟踪"
> "哪个部署引入了这些新错误？"
```

### 示例：连接到 GitHub 进行代码审查

```bash  theme={null}
# 1. 添加 GitHub MCP 服务器
claude mcp add --transport http github https://api.githubcopilot.com/mcp/

# 2. 在 Claude Code 中，如果需要进行身份验证
> /mcp
# 为 GitHub 选择"身份验证"

# 3. 现在您可以要求 Claude 使用 GitHub
> "审查 PR #456 并提出改进建议"
> "为我们刚发现的错误创建新问题"
> "显示分配给我的所有开放 PR"
```

### 示例：查询您的 PostgreSQL 数据库

```bash  theme={null}
# 1. 使用您的连接字符串添加数据库服务器
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://readonly:pass@prod.db.com:5432/analytics"

# 2. 自然地查询您的数据库
> "本月我们的总收入是多少？"
> "显示订单表的架构"
> "查找 90 天内未进行购买的客户"
```

## 使用远程 MCP 服务器进行身份验证

许多基于云的 MCP 服务器需要身份验证。Claude Code 支持 OAuth 2.0 以实现安全连接。

<Steps>
  <Step title="添加需要身份验证的服务器">
    例如：

    ```bash  theme={null}
    claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
    ```
  </Step>

  <Step title="在 Claude Code 中使用 /mcp 命令">
    在 Claude Code 中，使用命令：

    ```
    > /mcp
    ```

    然后按照浏览器中的步骤登录。
  </Step>
</Steps>

<Tip>
  提示：

  * 身份验证令牌存储安全且自动刷新
  * 在 `/mcp` 菜单中使用"清除身份验证"来撤销访问权限
  * 如果您的浏览器没有自动打开，请复制提供的 URL
  * OAuth 身份验证适用于 HTTP 服务器
</Tip>

## 从 JSON 配置添加 MCP 服务器

如果您有 MCP 服务器的 JSON 配置，可以直接添加它：

<Steps>
  <Step title="从 JSON 添加 MCP 服务器">
    ```bash  theme={null}
    # 基本语法
    claude mcp add-json <name> '<json>'

    # 示例：添加带有 JSON 配置的 HTTP 服务器
    claude mcp add-json weather-api '{"type":"http","url":"https://api.weather.com/mcp","headers":{"Authorization":"Bearer token"}}'

    # 示例：添加带有 JSON 配置的 stdio 服务器
    claude mcp add-json local-weather '{"type":"stdio","command":"/path/to/weather-cli","args":["--api-key","abc123"],"env":{"CACHE_DIR":"/tmp"}}'
    ```
  </Step>

  <Step title="验证服务器已添加">
    ```bash  theme={null}
    claude mcp get weather-api
    ```
  </Step>
</Steps>

<Tip>
  提示：

  * 确保 JSON 在您的 shell 中正确转义
  * JSON 必须符合 MCP 服务器配置架构
  * 您可以使用 `--scope user` 将服务器添加到您的用户配置而不是项目特定的配置
</Tip>

## 从 Claude Desktop 导入 MCP 服务器

如果您已在 Claude Desktop 中配置了 MCP 服务器，可以导入它们：

<Steps>
  <Step title="从 Claude Desktop 导入服务器">
    ```bash  theme={null}
    # 基本语法 
    claude mcp add-from-claude-desktop 
    ```
  </Step>

  <Step title="选择要导入的服务器">
    运行命令后，您将看到一个交互式对话框，允许您选择要导入的服务器。
  </Step>

  <Step title="验证服务器已导入">
    ```bash  theme={null}
    claude mcp list 
    ```
  </Step>
</Steps>

<Tip>
  提示：

  * 此功能仅在 macOS 和 Windows Subsystem for Linux (WSL) 上有效
  * 它从这些平台上的标准位置读取 Claude Desktop 配置文件
  * 使用 `--scope user` 标志将服务器添加到您的用户配置
  * 导入的服务器将具有与 Claude Desktop 中相同的名称
  * 如果已存在具有相同名称的服务器，它们将获得数字后缀（例如，`server_1`）
</Tip>

## 将 Claude Code 用作 MCP 服务器

您可以将 Claude Code 本身用作 MCP 服务器，其他应用程序可以连接到该服务器：

```bash  theme={null}
# 启动 Claude 作为 stdio MCP 服务器
claude mcp serve
```

您可以通过将此配置添加到 claude\_desktop\_config.json 在 Claude Desktop 中使用它：

```json  theme={null}
{
  "mcpServers": {
    "claude-code": {
      "type": "stdio",
      "command": "claude",
      "args": ["mcp", "serve"],
      "env": {}
    }
  }
}
```

<Tip>
  提示：

  * 服务器提供对 Claude 工具（如 View、Edit、LS 等）的访问权限。
  * 在 Claude Desktop 中，尝试要求 Claude 读取目录中的文件、进行编辑等。
  * 请注意，此 MCP 服务器只是将 Claude Code 的工具暴露给您的 MCP 客户端，因此您自己的客户端负责为各个工具调用实现用户确认。
</Tip>

## MCP 输出限制和警告

当 MCP 工具产生大量输出时，Claude Code 有助于管理令牌使用，以防止压倒您的对话上下文：

* **输出警告阈值**：当任何 MCP 工具输出超过 10,000 个令牌时，Claude Code 显示警告
* **可配置限制**：您可以使用 `MAX_MCP_OUTPUT_TOKENS` 环境变量调整最大允许的 MCP 输出令牌
* **默认限制**：默认最大值为 25,000 个令牌

要为产生大量输出的工具增加限制：

```bash  theme={null}
# 为 MCP 工具输出设置更高的限制
export MAX_MCP_OUTPUT_TOKENS=50000
claude
```

这在使用以下 MCP 服务器时特别有用：

* 查询大型数据集或数据库
* 生成详细的报告或文档
* 处理大量日志文件或调试信息

<Warning>
  如果您经常遇到特定 MCP 服务器的输出警告，请考虑增加限制或配置服务器以分页或过滤其响应。
</Warning>

## 使用 MCP 资源

MCP 服务器可以暴露资源，您可以使用 @ 提及来引用这些资源，类似于引用文件的方式。

### 引用 MCP 资源

<Steps>
  <Step title="列出可用资源">
    在您的提示中键入 `@` 以查看来自所有连接的 MCP 服务器的可用资源。资源与文件一起出现在自动完成菜单中。
  </Step>

  <Step title="引用特定资源">
    使用格式 `@server:protocol://resource/path` 来引用资源：

    ```
    > 您能分析 @github:issue://123 并建议修复吗？
    ```

    ```
    > 请查看位于 @docs:file://api/authentication 的 API 文档
    ```
  </Step>

  <Step title="多个资源引用">
    您可以在单个提示中引用多个资源：

    ```
    > 比较 @postgres:schema://users 与 @docs:file://database/user-model
    ```
  </Step>
</Steps>

<Tip>
  提示：

  * 引用时自动获取资源并作为附件包含
  * 资源路径在 @ 提及自动完成中可模糊搜索
  * Claude Code 在服务器支持时自动提供列出和读取 MCP 资源的工具
  * 资源可以包含 MCP 服务器提供的任何类型的内容（文本、JSON、结构化数据等）
</Tip>

## 将 MCP 提示用作斜杠命令

MCP 服务器可以暴露提示，这些提示在 Claude Code 中作为斜杠命令变得可用。

### 执行 MCP 提示

<Steps>
  <Step title="发现可用的提示">
    键入 `/` 以查看所有可用的命令，包括来自 MCP 服务器的命令。MCP 提示以 `/mcp__servername__promptname` 格式出现。
  </Step>

  <Step title="执行不带参数的提示">
    ```
    > /mcp__github__list_prs
    ```
  </Step>

  <Step title="执行带参数的提示">
    许多提示接受参数。在命令后面用空格分隔传递它们：

    ```
    > /mcp__github__pr_review 456
    ```

    ```
    > /mcp__jira__create_issue "登录流中的错误" high
    ```
  </Step>
</Steps>

<Tip>
  提示：

  * MCP 提示从连接的服务器动态发现
  * 参数根据提示的定义参数进行解析
  * 提示结果直接注入到对话中
  * 服务器和提示名称被规范化（空格变为下划线）
</Tip>

## 企业 MCP 配置

对于需要对 MCP 服务器进行集中控制的组织，Claude Code 支持企业管理的 MCP 配置。这允许 IT 管理员：

* **控制员工可以访问哪些 MCP 服务器**：在整个组织中部署一组标准化的已批准 MCP 服务器
* **防止未授权的 MCP 服务器**：可选择限制用户添加自己的 MCP 服务器
* **完全禁用 MCP**：如果需要，完全删除 MCP 功能

### 设置企业 MCP 配置

系统管理员可以在托管设置文件旁边部署企业 MCP 配置文件：

* **macOS**：`/Library/Application Support/ClaudeCode/managed-mcp.json`
* **Windows**：`C:\ProgramData\ClaudeCode\managed-mcp.json`
* **Linux**：`/etc/claude-code/managed-mcp.json`

`managed-mcp.json` 文件使用与标准 `.mcp.json` 文件相同的格式：

```json  theme={null}
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    },
    "sentry": {
      "type": "http",
      "url": "https://mcp.sentry.dev/mcp"
    },
    "company-internal": {
      "type": "stdio",
      "command": "/usr/local/bin/company-mcp-server",
      "args": ["--config", "/etc/company/mcp-config.json"],
      "env": {
        "COMPANY_API_URL": "https://internal.company.com"
      }
    }
  }
}
```

### 使用允许列表和拒绝列表限制 MCP 服务器

除了提供企业管理的服务器外，管理员还可以使用 `managed-settings.json` 文件中的 `allowedMcpServers` 和 `deniedMcpServers` 控制用户允许配置哪些 MCP 服务器：

* **macOS**：`/Library/Application Support/ClaudeCode/managed-settings.json`
* **Windows**：`C:\ProgramData\ClaudeCode\managed-settings.json`
* **Linux**：`/etc/claude-code/managed-settings.json`

```json  theme={null}
{
  "allowedMcpServers": [
    { "serverName": "github" },
    { "serverName": "sentry" },
    { "serverName": "company-internal" }
  ],
  "deniedMcpServers": [
    { "serverName": "filesystem" }
  ]
}
```

**允许列表行为 (`allowedMcpServers`)**：

* `undefined`（默认）：无限制 - 用户可以配置任何 MCP 服务器
* 空数组 `[]`：完全锁定 - 用户无法配置任何 MCP 服务器
* 服务器名称列表：用户只能配置指定的服务器

**拒绝列表行为 (`deniedMcpServers`)**：

* `undefined`（默认）：没有服务器被阻止
* 空数组 `[]`：没有服务器被阻止
* 服务器名称列表：指定的服务器在所有范围内被明确阻止

**重要说明**：

* 这些限制适用于所有范围：用户、项目、本地，甚至来自 `managed-mcp.json` 的企业服务器
* **拒绝列表具有绝对优先级**：如果服务器同时出现在两个列表中，它将被阻止

<Note>
  **企业配置优先级**：企业 MCP 配置具有最高优先级，当启用 `useEnterpriseMcpConfigOnly` 时无法被用户、本地或项目配置覆盖。
</Note>
