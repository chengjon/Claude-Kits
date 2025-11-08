# 插件

> 通过插件系统使用自定义命令、代理、钩子、技能和 MCP 服务器扩展 Claude Code。

<Tip>
  有关完整的技术规范和架构，请参阅[插件参考](/zh-CN/docs/claude-code/plugins-reference)。有关市场管理，请参阅[插件市场](/zh-CN/docs/claude-code/plugin-marketplaces)。
</Tip>

插件让您能够使用可在项目和团队中共享的自定义功能扩展 Claude Code。从[市场](/zh-CN/docs/claude-code/plugin-marketplaces)安装插件以添加预构建的命令、代理、钩子、技能和 MCP 服务器，或创建您自己的插件来自动化您的工作流程。

## 快速入门

让我们创建一个简单的问候插件，帮助您熟悉插件系统。我们将构建一个有效的插件，添加自定义命令，在本地测试它，并理解核心概念。

### 前置条件

* 在您的计算机上安装了 Claude Code
* 对命令行工具的基本熟悉

### 创建您的第一个插件

<Steps>
  <Step title="创建市场结构">
    ```bash  theme={null}
    mkdir test-marketplace
    cd test-marketplace
    ```
  </Step>

  <Step title="创建插件目录">
    ```bash  theme={null}
    mkdir my-first-plugin
    cd my-first-plugin
    ```
  </Step>

  <Step title="创建插件清单">
    ```bash 创建 .claude-plugin/plugin.json theme={null}
    mkdir .claude-plugin
    cat > .claude-plugin/plugin.json << 'EOF'
    {
    "name": "my-first-plugin",
    "description": "A simple greeting plugin to learn the basics",
    "version": "1.0.0",
    "author": {
    "name": "Your Name"
    }
    }
    EOF
    ```
  </Step>

  <Step title="添加自定义命令">
    ```bash 创建 commands/hello.md theme={null}
    mkdir commands
    cat > commands/hello.md << 'EOF'
    ---
    description: Greet the user with a personalized message
    ---

    # Hello Command

    Greet the user warmly and ask how you can help them today. Make the greeting personal and encouraging.
    EOF
    ```
  </Step>

  <Step title="创建市场清单">
    ```bash 创建 marketplace.json theme={null}
    cd ..
    mkdir .claude-plugin
    cat > .claude-plugin/marketplace.json << 'EOF'
    {
    "name": "test-marketplace",
    "owner": {
    "name": "Test User"
    },
    "plugins": [
    {
      "name": "my-first-plugin",
      "source": "./my-first-plugin",
      "description": "My first test plugin"
    }
    ]
    }
    EOF
    ```
  </Step>

  <Step title="安装并测试您的插件">
    ```bash 从父目录启动 Claude Code theme={null}
    cd ..
    claude
    ```

    ```shell 添加测试市场 theme={null}
    /plugin marketplace add ./test-marketplace
    ```

    ```shell 安装您的插件 theme={null}
    /plugin install my-first-plugin@test-marketplace
    ```

    选择"立即安装"。然后您需要重新启动 Claude Code 才能使用新插件。

    ```shell 尝试您的新命令 theme={null}
    /hello
    ```

    您将看到 Claude 使用您的问候命令！检查 `/help` 以查看您的新命令列表。
  </Step>
</Steps>

您已成功创建并测试了包含以下关键组件的插件：

* **插件清单** (`.claude-plugin/plugin.json`) - 描述您的插件的元数据
* **命令目录** (`commands/`) - 包含您的自定义斜杠命令
* **测试市场** - 允许您在本地测试您的插件

### 插件结构概览

您的插件遵循以下基本结构：

```
my-first-plugin/
├── .claude-plugin/
│   └── plugin.json          # 插件元数据
├── commands/                 # 自定义斜杠命令（可选）
│   └── hello.md
├── agents/                   # 自定义代理（可选）
│   └── helper.md
├── skills/                   # 代理技能（可选）
│   └── my-skill/
│       └── SKILL.md
└── hooks/                    # 事件处理程序（可选）
    └── hooks.json
```

**您可以添加的其他组件：**

* **命令**：在 `commands/` 目录中创建 markdown 文件
* **代理**：在 `agents/` 目录中创建代理定义
* **技能**：在 `skills/` 目录中创建 `SKILL.md` 文件
* **钩子**：为事件处理创建 `hooks/hooks.json`
* **MCP 服务器**：为外部工具集成创建 `.mcp.json`

<Note>
  **后续步骤**：准备好添加更多功能了吗？跳转到[开发更复杂的插件](#develop-more-complex-plugins)以添加代理、钩子和 MCP 服务器。有关所有插件组件的完整技术规范，请参阅[插件参考](/zh-CN/docs/claude-code/plugins-reference)。
</Note>

***

## 安装和管理插件

了解如何发现、安装和管理插件以扩展您的 Claude Code 功能。

### 前置条件

* Claude Code 已安装并运行
* 对命令行界面的基本熟悉

### 添加市场

市场是可用插件的目录。添加它们以发现和安装插件：

```shell 添加市场 theme={null}
/plugin marketplace add your-org/claude-plugins
```

```shell 浏览可用插件 theme={null}
/plugin
```

有关详细的市场管理，包括 Git 存储库、本地开发和团队分发，请参阅[插件市场](/zh-CN/docs/claude-code/plugin-marketplaces)。

### 安装插件

#### 通过交互式菜单（推荐用于发现）

```shell 打开插件管理界面 theme={null}
/plugin
```

选择"浏览插件"以查看可用选项及其描述、功能和安装选项。

#### 通过直接命令（用于快速安装）

```shell 安装特定插件 theme={null}
/plugin install formatter@your-org
```

```shell 启用已禁用的插件 theme={null}
/plugin enable plugin-name@marketplace-name
```

```shell 禁用而不卸载 theme={null}
/plugin disable plugin-name@marketplace-name
```

```shell 完全删除插件 theme={null}
/plugin uninstall plugin-name@marketplace-name
```

### 验证安装

安装插件后：

1. **检查可用命令**：运行 `/help` 以查看新命令
2. **测试插件功能**：尝试插件的命令和功能
3. **查看插件详情**：使用 `/plugin` → "管理插件"以查看插件提供的内容

## 设置团队插件工作流程

在存储库级别配置插件以确保整个团队的工具一致。当团队成员信任您的存储库文件夹时，Claude Code 会自动安装指定的市场和插件。

**设置团队插件的步骤：**

1. 将市场和插件配置添加到您的存储库的 `.claude/settings.json`
2. 团队成员信任存储库文件夹
3. 插件自动为所有团队成员安装

有关完整说明，包括配置示例、市场设置和推出最佳实践，请参阅[配置团队市场](/zh-CN/docs/claude-code/plugin-marketplaces#how-to-configure-team-marketplaces)。

***

## 开发更复杂的插件

一旦您熟悉了基本插件，您可以创建更复杂的扩展。

### 向您的插件添加技能

插件可以包含[代理技能](/zh-CN/docs/claude-code/skills)以扩展 Claude 的功能。技能是由模型调用的——Claude 根据任务上下文自主使用它们。

要向您的插件添加技能，请在您的插件根目录创建一个 `skills/` 目录，并添加包含 `SKILL.md` 文件的技能文件夹。插件技能在安装插件时自动可用。

有关完整的技能编写指南，请参阅[代理技能](/zh-CN/docs/claude-code/skills)。

### 组织复杂的插件

对于具有许多组件的插件，按功能组织您的目录结构。有关完整的目录布局和组织模式，请参阅[插件目录结构](/zh-CN/docs/claude-code/plugins-reference#plugin-directory-structure)。

### 在本地测试您的插件

开发插件时，使用本地市场来迭代测试更改。此工作流程基于快速入门模式，适用于任何复杂程度的插件。

<Steps>
  <Step title="设置您的开发结构">
    组织您的插件和市场以进行测试：

    ```bash 创建目录结构 theme={null}
    mkdir dev-marketplace
    cd dev-marketplace
    mkdir my-plugin
    ```

    这将创建：

    ```
    dev-marketplace/
    ├── .claude-plugin/marketplace.json  (您将创建此文件)
    └── my-plugin/                        (您正在开发的插件)
        ├── .claude-plugin/plugin.json
        ├── commands/
        ├── agents/
        └── hooks/
    ```
  </Step>

  <Step title="创建市场清单">
    ```bash 创建 marketplace.json theme={null}
    mkdir .claude-plugin
    cat > .claude-plugin/marketplace.json << 'EOF'
    {
    "name": "dev-marketplace",
    "owner": {
    "name": "Developer"
    },
    "plugins": [
    {
      "name": "my-plugin",
      "source": "./my-plugin",
      "description": "Plugin under development"
    }
    ]
    }
    EOF
    ```
  </Step>

  <Step title="安装并测试">
    ```bash 从父目录启动 Claude Code theme={null}
    cd ..
    claude
    ```

    ```shell 添加您的开发市场 theme={null}
    /plugin marketplace add ./dev-marketplace
    ```

    ```shell 安装您的插件 theme={null}
    /plugin install my-plugin@dev-marketplace
    ```

    测试您的插件组件：

    * 使用 `/command-name` 尝试您的命令
    * 检查代理是否出现在 `/agents` 中
    * 验证钩子是否按预期工作
  </Step>

  <Step title="迭代您的插件">
    对您的插件代码进行更改后：

    ```shell 卸载当前版本 theme={null}
    /plugin uninstall my-plugin@dev-marketplace
    ```

    ```shell 重新安装以测试更改 theme={null}
    /plugin install my-plugin@dev-marketplace
    ```

    在开发和改进插件时重复此周期。
  </Step>
</Steps>

<Note>
  **对于多个插件**：在 `./plugins/plugin-name` 等子目录中组织插件，并相应地更新您的 marketplace.json。请参阅[插件源](/zh-CN/docs/claude-code/plugin-marketplaces#plugin-sources)以了解组织模式。
</Note>

### 调试插件问题

如果您的插件不按预期工作：

1. **检查结构**：确保您的目录位于插件根目录，而不是在 `.claude-plugin/` 内
2. **单独测试组件**：分别检查每个命令、代理和钩子
3. **使用验证和调试工具**：请参阅[调试和开发工具](/zh-CN/docs/claude-code/plugins-reference#debugging-and-development-tools)以了解 CLI 命令和故障排除技术

### 共享您的插件

当您的插件准备好共享时：

1. **添加文档**：包含包含安装和使用说明的 README.md
2. **版本化您的插件**：在您的 `plugin.json` 中使用语义版本控制
3. **创建或使用市场**：通过插件市场分发以便于安装
4. **与他人测试**：在更广泛的分发之前让团队成员测试插件

<Note>
  有关完整的技术规范、调试技术和分发策略，请参阅[插件参考](/zh-CN/docs/claude-code/plugins-reference)。
</Note>

***

## 后续步骤

现在您了解了 Claude Code 的插件系统，以下是针对不同目标的建议路径：

### 对于插件用户

* **发现插件**：浏览社区市场以查找有用的工具
* **团队采用**：为您的项目设置存储库级别的插件
* **市场管理**：学习管理多个插件源
* **高级用法**：探索插件组合和工作流程

### 对于插件开发者

* **创建您的第一个市场**：[插件市场指南](/zh-CN/docs/claude-code/plugin-marketplaces)
* **高级组件**：深入了解特定的插件组件：
  * [斜杠命令](/zh-CN/docs/claude-code/slash-commands) - 命令开发详情
  * [子代理](/zh-CN/docs/claude-code/sub-agents) - 代理配置和功能
  * [代理技能](/zh-CN/docs/claude-code/skills) - 扩展 Claude 的功能
  * [钩子](/zh-CN/docs/claude-code/hooks) - 事件处理和自动化
  * [MCP](/zh-CN/docs/claude-code/mcp) - 外部工具集成
* **分发策略**：有效地打包和共享您的插件
* **社区贡献**：考虑为社区插件集合做出贡献

### 对于团队主管和管理员

* **存储库配置**：为团队项目设置自动插件安装
* **插件治理**：建立插件批准和安全审查的指南
* **市场维护**：创建和维护组织特定的插件目录
* **培训和文档**：帮助团队成员有效地采用插件工作流程

## 另请参阅

* [插件市场](/zh-CN/docs/claude-code/plugin-marketplaces) - 创建和管理插件目录
* [斜杠命令](/zh-CN/docs/claude-code/slash-commands) - 理解自定义命令
* [子代理](/zh-CN/docs/claude-code/sub-agents) - 创建和使用专门的代理
* [代理技能](/zh-CN/docs/claude-code/skills) - 扩展 Claude 的功能
* [钩子](/zh-CN/docs/claude-code/hooks) - 使用事件处理程序自动化工作流程
* [MCP](/zh-CN/docs/claude-code/mcp) - 连接到外部工具和服务
* [设置](/zh-CN/docs/claude-code/settings) - 插件的配置选项
