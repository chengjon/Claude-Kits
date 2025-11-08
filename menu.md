# Claude-Kits TUI 功能树

## 概述

Claude Code Manager TUI (Text-Based User Interface) 是一个基于文本的交互式用户界面，用于管理 Claude Code 的各种组件。

**导航方式**：
- ↑/↓ 箭头键：上下导航
- Enter 键：选择当前项
- 数字键 1-8：快捷选择
- q 键：返回上级/退出

---

## 功能树结构

```
Claude-Kits TUI (Main Menu)
│
├── 1. Agent Skills
│   ├── 1. List                    # 列出所有 Agent Skills
│   ├── 2. View Details            # 查看详细信息（名称、描述、模型、路径）
│   ├── 3. Install                 # 安装新的 Agent Skill
│   ├── 4. Edit                    # 编辑现有 Agent Skill
│   ├── 5. Delete                  # 删除 Agent Skill
│   ├── 6. Validate                # 验证 Agent Skill 合规性
│   └── 7. Back                    # 返回主菜单
│
├── 2. Subagents
│   ├── 1. List                    # 列出所有 Subagents
│   ├── 2. View Details            # 查看详细信息（名称、描述、模型、路径）
│   ├── 3. Install                 # 安装新的 Subagent
│   ├── 4. Edit                    # 编辑现有 Subagent
│   ├── 5. Delete                  # 删除 Subagent
│   ├── 6. Validate                # 验证 Subagent 合规性
│   └── 7. Back                    # 返回主菜单
│
├── 3. Hooks
│   ├── 1. List                    # 列出所有 Hooks 配置
│   ├── 2. Add                     # 添加新的 Hook
│   │   ├── 输入 Hook 事件类型（PreToolUse, PostToolUse, UserPromptSubmit）
│   │   ├── 输入工具匹配器（可选，如 "Bash", "Edit"）
│   │   ├── 输入 Hook 命令
│   │   ├── 选择作用域（personal, project, user, local）
│   │   ├── 输入 settings.json 路径（可选）
│   │   └── 输入超时时间（可选）
│   ├── 3. Edit                    # 编辑现有 Hook
│   │   ├── 输入 Hook 事件类型
│   │   ├── 输入 Hook 索引
│   │   ├── 输入新命令（可选）
│   │   ├── 选择作用域
│   │   └── 输入 settings.json 路径（可选）
│   ├── 4. Delete                  # 删除 Hook
│   │   ├── 输入 Hook 事件类型
│   │   ├── 输入 Hook 索引
│   │   ├── 选择作用域
│   │   └── 输入 settings.json 路径（可选）
│   ├── 5. Validate                # 验证 Hooks 配置
│   └── 6. Back                    # 返回主菜单
│
├── 4. Slash Commands
│   ├── 1. List                    # 列出所有 Slash Commands
│   ├── 2. View Details            # 查看详细信息（名称、描述、路径）
│   ├── 3. Install                 # 安装新的 Slash Command
│   ├── 4. Edit                    # 编辑现有 Slash Command
│   ├── 5. Delete                  # 删除 Slash Command
│   ├── 6. Validate                # 验证 Slash Command 合规性
│   └── 7. Back                    # 返回主菜单
│
├── 5. Plugins
│   ├── 1. List                    # 列出所有已安装的 Plugins
│   ├── 2. Install                 # 安装新的 Plugin
│   │   └── 输入 Plugin 源（本地路径或 URL）
│   ├── 3. Uninstall               # 卸载 Plugin
│   │   └── 输入 Plugin 名称
│   ├── 4. Marketplace             # 浏览 Plugin 市场
│   ├── 5. Validate                # 验证 Plugin 结构
│   │   └── 输入 Plugin 目录路径
│   └── 6. Back                    # 返回主菜单
│
├── 6. MCP Servers
│   ├── 1. List                    # 列出所有 MCP Servers 配置
│   │   ├── 选择作用域（user, project, all）
│   │   └── 输入 MCP 配置路径（可选）
│   ├── 2. Add                     # 添加新的 MCP Server
│   │   ├── 输入服务器名称
│   │   ├── 选择传输协议（stdio, http, sse）
│   │   ├── 输入服务器 URI
│   │   ├── 输入描述（可选）
│   │   ├── 输入环境变量（可选，格式：KEY1=VALUE1,KEY2=VALUE2）
│   │   ├── 选择作用域（user, project）
│   │   └── 输入 MCP 配置路径（可选）
│   ├── 3. Edit                    # 编辑现有 MCP Server
│   │   ├── 输入服务器名称
│   │   ├── 输入新 URI（可选）
│   │   ├── 选择作用域
│   │   └��─ 输入 MCP 配置路径（可选）
│   ├── 4. Delete                  # 删除 MCP Server
│   │   ├── 输入服务器名称
│   │   ├── 选择作用域
│   │   └── 输入 MCP 配置路径（可选）
│   ├── 5. Validate                # 验证 MCP Servers 配置
│   └── 6. Back                    # 返回主菜单
│
├── 7. Role Checklists
│   ├── 1. View Roles              # 查看所有角色清单
│   │   └── 显示所有 roles/*.yaml 文件的名称和描述
│   ├── 2. View Checklist          # 查看特定清单详情
│   │   ├── 选择清单类型（role, custom）
│   │   ├── 显示可用清单列表
│   │   ├── 选择清单编号
│   │   └── 显示清单详细内容（Agents, Skills, Commands）
│   ├── 3. Install from Checklist  # 从清单批量安装组件
│   │   ├── 选择清单类型（role, custom）
│   │   ├── 显示可用清单列表
│   │   ├── 选择清单编号
│   │   ├── 显示清单内容
│   │   ├── 确认安装（y/n）
│   │   ├── 选择安装作用域（personal, project, user）
│   │   └── 依次安装所有 Agents, Skills, Commands
│   ├── 4. Create Custom           # 创建自定义清单
│   │   ├── 输入清单名称
│   │   ├── 输入清单描述
│   │   ├── 添加 Agents（循环输入：名称、原因）
│   │   ├── 添加 Skills（循环输入：名称、原因）
│   │   ├── 添加 Commands（循环输入：名称、原因）
│   │   └── 保存到 checklists/custom/*.yaml
│   ├── 5. Edit Custom             # 编辑自定义清单
│   │   ├── 显示自定义清单列表
│   │   ├── 选择清单编号
│   │   └── 使用默认编辑器打开 YAML 文件
│   ├── 6. Delete Custom           # 删除自定义清单
│   │   ├── 显示自定义清单列表
│   │   ├── 选择清单编号
│   │   ├── 确认删除（y/n）
│   │   └── 删除文件
│   └── 7. Back                    # 返回主菜单
│
└── 8. Exit                        # 退出程序
```

---

## 初始化流程

程序启动时自动执行：

1. **检查依赖脚本**
   - skills_manager.py
   - subagents_manager.py
   - hooks_manager.py
   - commands_manager.py
   - plugins_manager.py
   - mcps_manager.py

2. **扫描组件目录**
   - 运行 components_scanner.py
   - 检测新增/修改的文件
   - 验证合规性并自动修正

3. **加载组件注册表**
   - 读取 components_registry.json
   - 显示统计信息：
     - Agents 总数
     - Commands 总数
     - Skills 总数

---

## 通用参数

所有组件管理操作都支持以下参数：

### 作用域 (Scope)
- **personal** / **user**: 用户级别（~/.claude/）
- **project**: 项目级别（.claude/）
- **local**: 本地设置（用于 Hooks）
- **all**: 所有作用域

### 路径选项
- **project_path**: 项目路径（默认：当前目录）
- **settings_path**: settings.json 路径（用于 Hooks）
- **config_path**: MCP 配置文件路径

---

## 查看详情功能

对于 **Agent Skills**, **Subagents**, **Slash Commands**，"View Details" 功能提供：

1. **列表视图**
   - 编号、名称、描述（前80字符）
   - 组件总数统计

2. **详细视图**（选择特定组件后）
   - 名称 (name)
   - 类型 (type)
   - 文件名 (file)
   - 完整路径 (path)
   - 模型 (model) - 仅适用于 Agents/Skills
   - 完整描述 (description)

---

## 角色清单 (Role Checklists) 详解

### 清单结构 (YAML)

```yaml
name: "清单名称"
description: "清单描述"
role: "角色类型"
agents:
  - name: "agent-name"
    reason: "包含此 agent 的原因"
skills:
  - name: "skill-name"
    reason: "包含此 skill 的原因"
commands:
  - name: "command-name"
    reason: "包含此 command 的原因"
```

### 清单类型

- **角色清单 (roles/)**: 预定义的专业角色配置
- **自定义清单 (custom/)**: 用户创建的自定义配置

### 批量安装流程

1. 选择清单（角色或自定义）
2. 显示清单内容预览
3. 确认安装
4. 选择安装作用域
5. 依次自动安装：
   - 所有 Agents
   - 所有 Skills
   - 所有 Commands

---

## 键盘快捷键

### 主菜单快捷键
- **1** - Agent Skills
- **2** - Subagents
- **3** - Hooks
- **4** - Slash Commands
- **5** - Plugins
- **6** - MCP Servers
- **7** - Role Checklists
- **8** - Exit
- **q** - 退出

### 子菜单快捷键
- **1-7** - 对应功能选项
- **↑/↓** - 上下导航
- **Enter** - 确认选择
- **q** - 返回上级

---

## 依赖的管理脚本

TUI 通过调用以下 Python 脚本执行具体操作：

| 脚本名称 | 管理对象 | 主要功能 |
|---------|---------|---------|
| skills_manager.py | Agent Skills | list, install, edit, delete, validate |
| subagents_manager.py | Subagents | list, install, edit, delete, validate |
| hooks_manager.py | Hooks | list, add, edit, delete, validate |
| commands_manager.py | Slash Commands | list, install, edit, delete, validate |
| plugins_manager.py | Plugins | list, install, uninstall, marketplace, validate |
| mcps_manager.py | MCP Servers | list, add, edit, delete, validate |
| components_scanner.py | 组件扫描 | 扫描、验证、自动修正、更新注册表 |

---

## 数据文件

### components_registry.json

组件注册表，包含所有组件的元数据：

```json
{
  "last_scan": "2025-11-07T14:21:52",
  "components": {
    "agents": { ... },
    "commands": { ... },
    "skills": { ... },
    "hooks": { ... }
  },
  "metadata": {
    "total_agents": 162,
    "total_commands": 63,
    "total_skills": 60
  }
}
```

### checklists/*.yaml

角色清单文件，存储预定义的组件集合：

- **checklists/roles/**: 角色清单
- **checklists/custom/**: 自定义清单

---

## 错误处理

TUI 提供以下错误处理机制：

1. **依赖检查**: 启动时检查所有必需的管理脚本
2. **输入验证**: 验证用户输入的有效性
3. **命令执行**: 捕获并显示命令输出和错误
4. **友好提示**: 提供清晰的错误信息和建议

---

## 平台兼容性

### Windows
- 使用 `msvcrt` 库处理键盘输入
- 特殊键前缀：`\xe0`, `\x00`
- 箭头键：H (UP), P (DOWN)

### Linux/Unix
- 使用 `termios` 和 `tty` 库处理键盘输入
- ESC 序列：`\x1b[A` (UP), `\x1b[B` (DOWN), `\x1b[C` (RIGHT), `\x1b[D` (LEFT)

---

## 使用建议

1. **首次使用**: 让 TUI 自动扫描组件目录，建立注册表
2. **查看详情**: 使用 "View Details" 了解已有组件的功能
3. **批量安装**: 使用 "Role Checklists" 快速配置专业环境
4. **自定义清单**: 创建自定义清单保存常用组件配置
5. **定期验证**: 使用 "Validate" 功能确保组件合规性

---

**维护**: Claude-Kits Team
**最后更新**: 2025-11-07
