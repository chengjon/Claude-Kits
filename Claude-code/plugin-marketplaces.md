# 插件市场

> 创建和管理插件市场，在团队和社区中分发 Claude Code 扩展。

插件市场是可用插件的目录，使发现、安装和管理 Claude Code 扩展变得容易。本指南向您展示如何使用现有市场以及为团队分发创建自己的市场。

## 概述

市场是一个 JSON 文件，列出可用的插件并描述在哪里找到它们。市场提供：

* **集中发现**：在一个地方浏览来自多个来源的插件
* **版本管理**：自动跟踪和更新插件版本
* **团队分发**：在您的组织中共享所需的插件
* **灵活来源**：支持 git 仓库、GitHub 仓库、本地路径和包管理器

### 先决条件

* 已安装并运行 Claude Code
* 基本熟悉 JSON 文件格式
* 对于创建市场：Git 仓库或本地开发环境

## 添加和使用市场

使用 `/plugin marketplace` 命令添加市场以访问来自不同来源的插件：

### 添加 GitHub 市场

```shell 添加包含 .claude-plugin/marketplace.json 的 GitHub 仓库 theme={null}
/plugin marketplace add owner/repo
```

### 添加 Git 仓库

```shell 添加任何 git 仓库 theme={null}
/plugin marketplace add https://gitlab.com/company/plugins.git
```

### 添加本地市场进行开发

```shell 添加包含 .claude-plugin/marketplace.json 的本地目录 theme={null}
/plugin marketplace add ./my-marketplace
```

```shell 添加 marketplace.json 文件的直接路径 theme={null}
/plugin marketplace add ./path/to/marketplace.json
```

```shell 通过 URL 添加远程 marketplace.json theme={null}
/plugin marketplace add https://url.of/marketplace.json
```

### 从市场安装插件

添加市场后，直接安装插件：

```shell 从任何已知市场安装 theme={null}
/plugin install plugin-name@marketplace-name
```

```shell 交互式浏览可用插件 theme={null}
/plugin
```

### 验证市场安装

添加市场后：

1. **列出市场**：运行 `/plugin marketplace list` 确认已添加
2. **浏览插件**：使用 `/plugin` 查看来自您市场的可用插件
3. **测试安装**：尝试安装插件以验证市场正常工作

## 配置团队市场

通过在 `.claude/settings.json` 中指定所需市场，为团队项目设置自动市场安装：

```json  theme={null}
{
  "extraKnownMarketplaces": {
    "team-tools": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-plugins"
      }
    },
    "project-specific": {
      "source": {
        "source": "git",
        "url": "https://git.company.com/project-plugins.git"
      }
    }
  }
}
```

当团队成员信任仓库文件夹时，Claude Code 会自动安装这些市场以及在 `enabledPlugins` 字段中指定的任何插件。

***

## 创建您自己的市场

为您的团队或社区构建和分发自定义插件集合。

### 市场创建的先决条件

* Git 仓库（GitHub、GitLab 或其他 git 托管）
* 了解 JSON 文件格式
* 一个或多个要分发的插件

### 创建市场文件

在您的仓库根目录中创建 `.claude-plugin/marketplace.json`：

```json  theme={null}
{
  "name": "company-tools",
  "owner": {
    "name": "DevTools Team",
    "email": "devtools@company.com"
  },
  "plugins": [
    {
      "name": "code-formatter",
      "source": "./plugins/formatter",
      "description": "保存时自动代码格式化",
      "version": "2.1.0",
      "author": {
        "name": "DevTools Team"
      }
    },
    {
      "name": "deployment-tools",
      "source": {
        "source": "github",
        "repo": "company/deploy-plugin"
      },
      "description": "部署自动化工具"
    }
  ]
}
```

### 市场架构

#### 必需字段

| 字段        | 类型     | 描述                    |
| :-------- | :----- | :-------------------- |
| `name`    | string | 市场标识符（kebab-case，无空格） |
| `owner`   | object | 市场维护者信息               |
| `plugins` | array  | 可用插件列表                |

#### 可选元数据

| 字段                     | 类型     | 描述          |
| :--------------------- | :----- | :---------- |
| `metadata.description` | string | 简短市场描述      |
| `metadata.version`     | string | 市场版本        |
| `metadata.pluginRoot`  | string | 相对插件来源的基础路径 |

### 插件条目

<Note>
  插件条目基于*插件清单架构*（所有字段都设为可选）加上市场特定字段（`source`、`category`、`tags`、`strict`），其中 `name` 是必需的。
</Note>

**必需字段：**

| 字段       | 类型             | 描述                    |
| :------- | :------------- | :-------------------- |
| `name`   | string         | 插件标识符（kebab-case，无空格） |
| `source` | string\|object | 从哪里获取插件               |

#### 可选插件字段

**标准元数据字段：**

| 字段            | 类型      | 描述                                         |
| :------------ | :------ | :----------------------------------------- |
| `description` | string  | 简短插件描述                                     |
| `version`     | string  | 插件版本                                       |
| `author`      | object  | 插件作者信息                                     |
| `homepage`    | string  | 插件主页或文档 URL                                |
| `repository`  | string  | 源代码仓库 URL                                  |
| `license`     | string  | SPDX 许可证标识符（例如，MIT、Apache-2.0）             |
| `keywords`    | array   | 用于插件发现和分类的标签                               |
| `category`    | string  | 用于组织的插件类别                                  |
| `tags`        | array   | 用于搜索性的标签                                   |
| `strict`      | boolean | 要求插件文件夹中有 plugin.json（默认：true）<sup>1</sup> |

**组件配置字段：**

| 字段           | 类型             | 描述                  |
| :----------- | :------------- | :------------------ |
| `commands`   | string\|array  | 命令文件或目录的自定义路径       |
| `agents`     | string\|array  | 代理文件的自定义路径          |
| `hooks`      | string\|object | 自定义钩子配置或钩子文件路径      |
| `mcpServers` | string\|object | MCP 服务器配置或 MCP 配置路径 |

*<sup>1 - 当 `strict: true`（默认）时，插件必须包含 `plugin.json` 清单文件，市场字段补充这些值。当 `strict: false` 时，plugin.json 是可选的。如果缺失，市场条目作为完整的插件清单。</sup>*

### 插件来源

#### 相对路径

对于同一仓库中的插件：

```json  theme={null}
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin"
}
```

#### GitHub 仓库

```json  theme={null}
{
  "name": "github-plugin",
  "source": {
    "source": "github",
    "repo": "owner/plugin-repo"
  }
}
```

#### Git 仓库

```json  theme={null}
{
  "name": "git-plugin",
  "source": {
    "source": "url",
    "url": "https://gitlab.com/team/plugin.git"
  }
}
```

#### 高级插件条目

插件条目可以覆盖默认组件位置并提供额外的元数据。注意 `${CLAUDE_PLUGIN_ROOT}` 是一个环境变量，解析为插件的安装目录（详情请参见[环境变量](/zh-CN/docs/claude-code/plugins-reference#environment-variables)）：

```json  theme={null}
{
  "name": "enterprise-tools",
  "source": {
    "source": "github",
    "repo": "company/enterprise-plugin"
  },
  "description": "企业工作流自动化工具",
  "version": "2.1.0",
  "author": {
    "name": "Enterprise Team",
    "email": "enterprise@company.com"
  },
  "homepage": "https://docs.company.com/plugins/enterprise-tools",
  "repository": "https://github.com/company/enterprise-plugin",
  "license": "MIT",
  "keywords": ["enterprise", "workflow", "automation"],
  "category": "productivity",
  "commands": [
    "./commands/core/",
    "./commands/enterprise/",
    "./commands/experimental/preview.md"
  ],
  "agents": [
    "./agents/security-reviewer.md",
    "./agents/compliance-checker.md"
  ],
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"}]
      }
    ]
  },
  "mcpServers": {
    "enterprise-db": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"]
    }
  },
  "strict": false
}
```

<Note>
  **架构关系**：插件条目使用插件清单架构，所有字段都设为可选，加上市场特定字段（`source`、`strict`、`category`、`tags`）。这意味着在 `plugin.json` 文件中有效的任何字段也可以在市场条目中使用。当 `strict: false` 时，如果不存在 `plugin.json`，市场条目作为完整的插件清单。当 `strict: true`（默认）时，市场字段补充插件自己的清单文件。
</Note>

***

## 托管和分发市场

为您的插件分发需求选择最佳托管策略。

### 在 GitHub 上托管（推荐）

GitHub 提供最简单的分发方法：

1. **创建仓库**：为您的市场设置新仓库
2. **添加市场文件**：使用您的插件定义创建 `.claude-plugin/marketplace.json`
3. **与团队共享**：团队成员使用 `/plugin marketplace add owner/repo` 添加

**好处**：内置版本控制、问题跟踪和团队协作功能。

### 在其他 git 服务上托管

任何 git 托管服务都适用于市场分发，使用任意 git 仓库的 URL。

例如，使用 GitLab：

```shell  theme={null}
/plugin marketplace add https://gitlab.com/company/plugins.git
```

### 使用本地市场进行开发

在分发前本地测试您的市场：

```shell 添加本地市场进行测试 theme={null}
/plugin marketplace add ./my-local-marketplace
```

```shell 测试插件安装 theme={null}
/plugin install test-plugin@my-local-marketplace
```

## 管理市场操作

### 列出已知市场

```shell 列出所有配置的市场 theme={null}
/plugin marketplace list
```

显示所有配置的市场及其来源和状态。

### 更新市场元数据

```shell 刷新市场元数据 theme={null}
/plugin marketplace update marketplace-name
```

从市场来源刷新插件列表和元数据。

### 移除市场

```shell 移除市场 theme={null}
/plugin marketplace remove marketplace-name
```

从您的配置中移除市场。

<Warning>
  移除市场将卸载您从中安装的任何插件。
</Warning>

***

## 市场故障排除

### 常见市场问题

#### 市场未加载

**症状**：无法添加市场或看不到其中的插件

**解决方案**：

* 验证市场 URL 是否可访问
* 检查指定路径是否存在 `.claude-plugin/marketplace.json`
* 使用 `claude plugin validate` 确保 JSON 语法有效
* 对于私有仓库，确认您有访问权限

#### 插件安装失败

**症状**：市场出现但插件安装失败

**解决方案**：

* 验证插件来源 URL 是否可访问
* 检查插件目录是否包含所需文件
* 对于 GitHub 来源，确保仓库是公开的或您有访问权限
* 通过克隆/下载手动测试插件来源

### 验证和测试

在共享前测试您的市场：

```bash 验证市场 JSON 语法 theme={null}
claude plugin validate .
```

```shell 添加市场进行测试 theme={null}
/plugin marketplace add ./path/to/marketplace
```

```shell 安装测试插件 theme={null}
/plugin install test-plugin@marketplace-name
```

有关完整的插件测试工作流程，请参见[本地测试您的插件](/zh-CN/docs/claude-code/plugins#test-your-plugins-locally)。有关技术故障排除，请参见[插件参考](/zh-CN/docs/claude-code/plugins-reference)。

***

## 下一步

### 对于市场用户

* **发现社区市场**：在 GitHub 上搜索 Claude Code 插件集合
* **贡献反馈**：向市场维护者报告问题并提出改进建议
* **分享有用的市场**：帮助您的团队发现有价值的插件集合

### 对于市场创建者

* **构建插件集合**：围绕特定用例创建主题市场
* **建立版本控制**：实施清晰的版本控制和更新策略
* **社区参与**：收集反馈并维护活跃的市场社区
* **文档**：提供清晰的 README 文件解释您的市场内容

### 对于组织

* **私有市场**：为专有工具设置内部市场
* **治理策略**：建立插件批准和安全审查指南
* **培训资源**：帮助团队有效发现和采用有用的插件

## 另请参见

* [插件](/zh-CN/docs/claude-code/plugins) - 安装和使用插件
* [插件参考](/zh-CN/docs/claude-code/plugins-reference) - 完整的技术规范和架构
* [插件开发](/zh-CN/docs/claude-code/plugins#develop-more-complex-plugins) - 创建您自己的插件
* [设置](/zh-CN/docs/claude-code/settings#plugin-configuration) - 插件配置选项
