# Claude-Kits

<div align="center">

![Claude-Kits Logo](https://img.shields.io/badge/Claude--Kits-v3.1.0-blue?style=for-the-badge)
![GitHub stars](https://img.shields.io/github/stars/chengjon/Claude-Kits?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/chengjon/Claude-Kits?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

**专业的 Claude Code 自定义组件管理工具集**

基于 Reddit 工程师 30 万行代码实践经验，提供 434+ 个高质量专业组件

[GitHub 仓库](https://github.com/chengjon/Claude-Kits) • [快速开始](#-快速开始) • [文档](#-文档) • [贡献](#-贡献)

</div>

## 📋 目录

- [🛡️ 安全第一](#-安全第一)
- [🚀 快速开始](#-快速开始)
- [📦 可用组件](#-可用组件)
- [🔥 核心功能](#-核心功能)
- [📖 文档](#-文档)
- [🔗 GitHub 相关](#-github-相关)
- [🛠️ 管理工具](#️-管理工具)
- [⚠️ 安装前必读](#️-安装前必读)
- [🎯 使用场景](#-使用场景)
- [💡 最佳实践](#-最佳实践)
- [🏗️ 系统架构](#️-系统架构)
- [🤝 贡献](#-贡献)
- [📄 许可证](#-许可证)
- [🙏 致谢](#-致谢)

## 🛡️ 安全第一

**本项目最重要的原则：永不覆盖用户文件**

- ✅ 所有安装操作都需要用户授权
- ✅ 完整的冲突检测和解决机制
- ✅ 支持 dry-run 预览模式
- ✅ 透明显示所有将要执行的操作

## 🚀 快速开始

### 💡 推荐方式：使用交互式 TUI 界面

```bash
# 启动 TUI 界面（推荐新手使用）
python scripts/claude_tui.py

# Skills 浏览流程：
# Agent Skills → View Details → 选择分类 → 选择skill → 操作选择
```

### 方法 1: TUI 界面安装（推荐）

**优势**: 直观易用，支持三层分类浏览和智能路径检测

```bash
python scripts/claude_tui.py
# 1. 选择组件类型（Agent Skills/Subagents/Slash Commands）
# 2. 选择操作方式（View Details/Install/Edit等）
# 3. 按分类浏览或直接搜索
# 4. 查看详情后选择安装/修改/删除
```

### 方法 2: 命令行批量安装 Role 集合

**优势**: 快速部署完整工具链，适合有经验的用户

```bash
# 查看所有可用的 Role 集合
python scripts/roles_manager.py list

# 查看特定 Role 详情
python scripts/roles_manager.py info backend-developer

# 批量安装完整工具链
python scripts/roles_manager.py install backend-developer --path /path/to/project

# 选择性安装（只安装特定组件类型）
python scripts/roles_manager.py install backend-developer \
    --path /path/to/project \
    --components skills,agents  # 不安装commands和hooks
```

### 方法 3: 单个组件精确安装

**优势**: 精确控制，只安装需要的组件

```bash
# 安装 Skill（支持智能路径检测）
python scripts/skills_manager.py install task-planning-pro --path /path/to/project

# 安装 Agent
python scripts/subagents_manager.py install api-architect --path /path/to/project

# 安装 Slash Command
python scripts/commands_manager.py install api-mock --path /path/to/project

# 预览模式（强烈推荐先使用）
python scripts/skills_manager.py install task-planning-pro --path /path/to/project --dry-run
```

### 方法 4: 创建自定义 Role 集合

**优势**: 根据项目需求定制专属工具集

```bash
# 使用 TUI 界面创建（推荐）
python scripts/claude_tui.py
# 导航到: Role Checklists → Create Custom

# 或使用命令行工具
python scripts/custom_role_builder.py

# 安装自定义 Role
python scripts/roles_manager.py install your-custom-role --path /path/to/project
```

**详细安装指南**: 查看 [QUICK_INSTALL_GUIDE.md](QUICK_INSTALL_GUIDE.md)

## 📦 可用组件

### 🎯 7 个预定义 Role 集合
- **reddit-case** - Reddit 工程师 30 万行代码实践（11 个组件）
- **backend-developer** - 后端开发工具集（13 个组件）
- **frontend-developer** - 前端开发工具集
- **fullstack-developer** - 全栈开发工具集
- **devops-engineer** - DevOps 工具集
- **test-engineer** - 测试工程师工具集
- **security-engineer** - 安全工程师工具集

### 📚 84 个 Agent Skills

**最新更新 (2025-11-14)**:
- ✨ **新增三层分类浏览系统** - 按9个主要分类智能浏览skills
- ✨ **智能路径检测功能** - 自动检测已安装skills的安装路径
- 🚀 **TUI界面优化** - ESC键支持和模板化浏览体验

**技能分类体系**:
- **开发与编程** (13个) - 核心开发技能、语言特定模式、性能优化
- **架构与设计** (8个) - 架构模式、API与数据库、分布式系统
- **AI与机器学习** (18个) - AI系统、LLM架构、模型工程
- **测试与质量保证** (7个) - 代码审查、测试模式
- **DevOps与部署** (10个) - CI/CD、基础设施、监控运维
- **安全技能** (5个) - 安全审计、区块链安全
- **云与基础设施** (6个) - 云架构、Kubernetes、Terraform
- **区块链与Web3** (7个) - DeFi协议、Web3标准
- **开发工具与工作流** (5个) - 项目管理、自动化工具

**热门 Skills**:
- `backend-dev-guidelines` - 后端开发指南
- `frontend-dev-guidelines` - 前端开发指南
- `task-planning-pro` - 任务规划专家
- `debugging-strategies` - 调试策略
- `code-review-excellence` - 代码审查卓越
- `api-design-principles` - API 设计原则

**查看完整列表**: `ls /opt/claude/Claude-Kits/components/skills/`

### 🤖 256 个 Agents (子代理)
**包含 38 个新的 -pro 整合 Agents (2025-11-11)**

按类别分类，包括：
- `api-architect` - API 架构设计
- `backend-architect` - 后端架构
- `database-optimizer` - 数据库优化
- `code-architecture-reviewer` - 代码架构审查
- `build-error-resolver` - 构建错误自动修复
- `frontend-error-fixer` - 前端错误修复
- ... 以及更多

**查看完整列表**: `ls /opt/claude/Claude-Kits/components/agents/`
**详细分类**: 查看 [组件覆盖面分析](docs/COMPONENT_COVERAGE_ANALYSIS.md)

### ⚡ 63 个 Slash Commands
- `/api-mock` - API Mock 服务
- `/dev-docs` - 创建 Dev Docs 系统
- `/code-review` - 代码审查
- `/build-and-fix` - 构建并修复错误
- ... 以及更多

**查看完整列表**: `ls /opt/claude/Claude-Kits/components/commands/`

### 🪝 13 个 Hooks (自动化管道)
**新增 7 个核心 Hooks + 3 个 Code Compliance Hooks + 3 个配置文件 (2025-11-18)**

**核心 Hooks**:
- `user-prompt-submit-skill-activation.sh` - **Skills 自动激活**（最重要）
- `post-tool-use-file-edit-tracker.sh` - 文件编辑追踪 (JSONL 格式)
- `stop-python-quality-gate.sh` - **Python 质量门禁**（批量检查，错误>=阈值则阻止）
- `post-tool-use-database-schema-validator.sh` - 数据库架构验证
- `post-tool-use-document-organizer.sh` - 文档自动整理
- `session-start-task-master-injector.sh` - Task Master 上下文恢复
- `session-end-cleanup.sh` - 会话结束清理

**Code Compliance Hooks** (NEW - 2025-11-18):
- `post-tool-use-python-header-validator.sh` - Python 文件头部注释验证（零硬编码，可配置）
- `post-tool-use-md-frontmatter-validator.sh` - Markdown YAML frontmatter 验证（零硬编码，可配置）
- `post-tool-use-chinese-filename-checker.sh` - 中文/非ASCII文件名检测（跨平台兼容性）

**配置文件**:
- `settings.json` - Hook 注册配置（9 Event 类型）
- `skill-rules.json` - Skill 激活规则（16KB，双语支持）
- `build-checker-python.json` - Python 质量检查配置

**特性**:
- ✅ 符合 Claude Code 9 Event 规范
- ✅ 支持双语（中英文）提示和关键词
- ✅ 非阻塞 + 阻塞混合设计（编辑追踪非阻塞，质量门禁阻塞）
- ✅ JSON-LD 结构化输出
- ✅ JSONL 格式日志（自动限制 10,000 条）
- ✅ **零硬编码配置** - 所有 Code Compliance Hooks 完全可通过环境变量自定义
- ✅ **Python 导入路径检查** - 自动检测移动文件后的导入路径问题

**详细文档**:
- [CODE_COMPLIANCE_HOOKS.md](components/hooks/CODE_COMPLIANCE_HOOKS.md) - Code Compliance Hooks 使用指南
- [CONFIGURATION_GUIDE.md](components/hooks/CONFIGURATION_GUIDE.md) - 完整配置指南

**查看完整列表**: `ls /opt/claude/Claude-Kits/components/hooks/`

## 🔥 核心功能

### 5. 交互式 TUI 界面 🖥️ (NEW)
**问题**: 命令行操作复杂，需要记忆各种参数和路径

**解决**: 提供直观的文本用户界面，支持键盘导航和鼠标式操作

**核心特性**:
- ✨ **Skills 三层分类浏览** - 9个一级分类 → 18个二级分类 → 84个skills
- ✨ **智能路径检测** - 自动检测已安装skills的安装路径，避免手动输入
- ✅ **跨平台键盘支持** - Windows/Linux/Unix ESC键和箭头键兼容
- ✅ **模板化浏览** - 从JSON模板库浏览所有可用组件
- ✅ **详情页面增强** - 显示完整信息并支持直接安装
- ✅ **批量安装支持** - Role集合一键批量安装所有组件
- ✅ **四种操作选项** - 安装、修改、删除、返回

**浏览流程示例 (Skills)**:
1. **进入 Agent Skills** → 选择 "View Details"
2. **一级分类选择** - 从9个主要分类中选择（如：开发与编程）
3. **二级分类选择** - 在选定分类下选择子分类（如：核心开发技能）
4. **三级技能列表** - 查看该分类下的具体skills列表
5. **详情查看** - 显示技能描述、文件路径等信息
6. **四种操作** - 选择安装/修改/删除/返回

**智能修改功能**:
- 自动检测已安装skills的安装路径
- 按优先级检查：项目级 → 用户级
- 支持手动输入路径作为备选方案

**使用示例**:
```bash
python scripts/claude_tui.py
# Agent Skills → View Details → 选择分类 → 选择skill → [2]修改
# 系统自动检测安装路径或让用户手动输入
```

### 1. 统一安装系统 🎯 (NEW)
**特性**:
- ✅ 单一数据源：所有组件从 `components/` 目录安装
- ✅ 统一接口：所有管理器使用相同的 CLI 模式
- ✅ Role 批量安装：一次安装多个组件集合
- ✅ 完整的冲突处理：skip/rename/backup/abort
- ✅ Dry-run 预览：安装前查看所有操作
- ✅ YAML 验证：自动验证组件元数据

**管理器**:
- `skills_manager.py` - Skills 安装和管理
- `subagents_manager.py` - Agents 安装和管理
- `commands_manager.py` - Slash Commands 安装和管理
- `roles_manager.py` - **批量安装 Role 集合** (NEW)
- `universal_installer.py` - 底层统一安装引擎

### 2. Skills 自动激活系统 ⭐
**问题**: Claude 不会自动加载 `.claude/skills/` 中的技能

**解决**: UserPromptSubmit hook + skill-rules.json 强制激活

**效果**: 确保 Claude 始终使用相关技能，提高一致性

### 3. 零错误容忍系统 🛡️
**模式**: 先记录（PostToolUse）→ 后检查（Stop）

**优点**: 允许临时破坏，减少构建噪声

**结果**: Reddit 团队 **6个月零错误记录**

### 4. 上下文持久化 🧠
**三文档系统**: plan.md + context.md + tasks.md

**自动恢复**: SessionStart hook 注入上下文

**跨会话**: 压缩后仍能继续工作

## 📖 文档

### 🚀 快速入门
- **[QUICK_INSTALL_GUIDE.md](QUICK_INSTALL_GUIDE.md)** - 快速安装指南（推荐从这里开始）
- **[TUI 新工作流指南](docs/TUI_NEW_WORKFLOW.md)** - 交互式TUI界面使用指南

### 🔧 技术文档
- **[三级架构设计](docs/THREE_TIER_ARCHITECTURE.md)** - user/project/plugin 三层级架构详解
- **[Role 集合指南](docs/ROLE_CHECKLISTS_IMPLEMENTATION.md)** - 所有 Role 配置和使用指南
- [架构设计](docs/ARCHITECTURE_DESIGN.md) - 设计原则和标准流程
- [安装系统实施](docs/COMPONENT_MANAGEMENT_SYSTEM.md) - 统一安装系统技术文档

### 📊 项目分析
- **[组件覆盖面分析](docs/COMPONENT_COVERAGE_ANALYSIS.md)** - 组件分类和覆盖统计
- **[实现完成报告](docs/IMPLEMENTATION_COMPLETION_REPORT.md)** - 项目实施进度报告

### 📋 使用指南
- [CLAUDE.md](CLAUDE.md) - Claude Code 使用指南

## 🔗 GitHub 相关

**仓库信息**:
- **GitHub**: [https://github.com/chengjon/Claude-Kits](https://github.com/chengjon/Claude-Kits)
- **问题反馈**: [GitHub Issues](https://github.com/chengjon/Claude-Kits/issues)
- **功能建议**: [GitHub Discussions](https://github.com/chengjon/Claude-Kits/discussions)
- **贡献指南**: 请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

**统计数据**:
- ⭐ Stars: [GitHub Stars](https://github.com/chengjon/Claude-Kits/stargazers)
- 🍴 Forks: [GitHub Forks](https://github.com/chengjon/Claude-Kits/network/members)
- 🐛 Issues: [GitHub Issues](https://github.com/chengjon/Claude-Kits/issues)
- 📦 Releases: [GitHub Releases](https://github.com/chengjon/Claude-Kits/releases)

**社区**:
- 欢迎提交 Issue 反馈问题
- 欢迎提交 PR 贡献代码
- 欢迎参与 Discussions 讨论功能建议

## 🛠️ 管理工具

### 组件安装器（推荐）
```bash
# Skills 安装
python scripts/skills_manager.py install task-planning-pro --path /project

# Agents 安装
python scripts/subagents_manager.py install api-architect --path /project

# Commands 安装
python scripts/commands_manager.py install api-mock --path /project

# Role 批量安装
python scripts/roles_manager.py install backend-developer --path /project

# 预览模式（所有管理器通用）
python scripts/skills_manager.py install <name> --path /project --dry-run

# 非交互模式（所有管理器通用）
python scripts/skills_manager.py install <name> --path /project --non-interactive
```

### 传统安装器（Reddit-Case）
```bash
# 安装 Reddit-Case 完整工具链
python scripts/install_reddit_case.py /path/to/project

# 预览模式
python scripts/install_reddit_case.py /path/to/project --dry-run

# 冲突检查
python scripts/check_conflicts.py /path/to/project
```

### 交互式 TUI 界面（推荐）
```bash
# 启动交互式文本用户界面
python scripts/claude_tui.py
```

**新功能亮点 (2025-11-13)**:
- ✅ **ESC键支持** - 除q键外，ESC键也能返回上级菜单
- ✅ **模板化浏览** - 从JSON模板库浏览所有可用组件
- ✅ **详情页面增强** - 显示完整信息并支持直接安装
- ✅ **三级架构优化** - 用户友好的作用域显示（user/project/plugin）
- ✅ **批量安装** - Role集合一键批量安装
- ✅ **交叉平台兼容** - Windows和Linux键盘输入处理

**菜单结构**:
```
1. Agent Skills → View Templates → 查看详情 → 直接安装
2. Subagents → 同上流程
3. Hooks → 配置文件管理方式
4. Slash Commands → 同上流程  
5. Plugins → 插件管理系统
6. MCP Servers → 服务器管理
7. Role Checklists → 批量安装工具集
8. Exit → 退出程序
```

**键盘导航**:
- ↑/↓ 箭头键：导航菜单选项
- Enter：确认选择进入下一级
- q 或 ESC：返回上级菜单
- 数字键1-8：快速选择菜单项

**操作流程**:
1. 选择组件类型（如 Agent Skills）
2. 选择操作方式（推荐 View Templates）
3. 浏览组件列表，选择感兴趣的项
4. 查看详情页面，了解功能描述
5. 直接安装到项目（支持三级架构选择）

**批量安装示例**:
```
Role Checklists → View Role Templates → 选择 backend-developer
→ 查看工具清单 → 一键安装所有相关组件
```

## ⚠️ 安装前必读

1. **永远先使用 --dry-run** 预览操作
2. **查看组件列表** 使用 `roles_manager.py list` 和 `roles_manager.py info <role-name>`
3. **选择合适的 Role** 根据你的开发角色和项目需求
4. **选择 skip 选项** 对于冲突，然后手动合并
5. **重启 Claude Code** 安装后重启以加载新组件

## 🎯 使用场景

### Claude-Kits 适用于：

- ✅ 任何规模的项目（从小型到大型）
- ✅ 多种开发角色（后端/前端/全栈/DevOps/测试/安全）
- ✅ 需要特定领域专业知识（API设计/数据库/架构/测试等）
- ✅ 团队协作开发
- ✅ 需要自动化工作流

### Reddit-Case 特别适用于：

- ✅ 需要高质量、零错误容忍的项目
- ✅ 中大型项目（10,000+ 行代码）
- ✅ 需要跨会话上下文持久化
- ✅ 需要自动化质量门禁

## 💡 最佳实践

### 1. 选择合适的安装方式

**单个组件** - 需要特定技能或代理时：
```bash
python scripts/skills_manager.py install debugging-strategies --path /project
```

**Role 集合** - 作为特定角色工作时（推荐）：
```bash
python scripts/roles_manager.py install backend-developer --path /project
```

**Reddit-Case** - 需要完整的质量保证系统时：
```bash
python scripts/roles_manager.py install reddit-case --path /project
```

### 2. 安装后配置

**Skills 自动激活** (仅 Reddit-Case):
编辑 `.claude/skill-rules.json`，调整路径模式以匹配你的项目：

```json
{
  "skills": {
    "backend-dev-guidelines": {
      "fileTriggers": {
        "pathPatterns": [
          "src/routes/**/*.ts",      // 改为你的路径
          "src/controllers/**/*.ts"
        ]
      }
    }
  }
}
```

**构建检查配置** (仅 Reddit-Case):
编辑 `.claude/build-checker.json`：

```json
{
  "repos": {
    "/absolute/path/to/your/project": {
      "buildCommand": "npm run build",  // 改为你的构建命令
      "errorThreshold": 5
    }
  }
}
```

**Skills 描述自定义**:
编辑每个 `.claude/skills/*/SKILL.md` 的 `description` 字段，添加项目特定关键词，提高激活准确性。

### 3. 选择性安装

只安装需要的组件类型：
```bash
# 只安装 Skills 和 Agents，不安装 Commands 和 Hooks
python scripts/roles_manager.py install backend-developer \
    --path /project \
    --components skills,agents
```

## 🏗️ 系统架构

### 统一安装系统 (v3.0.0)

```
components/              # 单一数据源
├── skills/             # 72+ Agent Skills
├── agents/             # 大量 Agents (.md 文件)
├── commands/           # 大量 Slash Commands (.md 文件)
└── hooks/              # Hooks 脚本

scripts/                # 管理工具
├── universal_installer.py    # 核心安装引擎
├── skills_manager.py         # Skills 管理
├── subagents_manager.py      # Agents 管理
├── commands_manager.py       # Commands 管理
└── roles_manager.py          # Role 批量安装 (NEW)

checklists/roles/       # Role 定义
├── reddit-case.yaml
├── backend-developer.yaml
├── frontend-developer.yaml
└── ... (7 个 Roles)
```

### 工作流程

1. **安装**: 从 `components/` 复制到用户项目的 `.claude/` 目录
2. **验证**: 自动验证 YAML frontmatter 和文件结构
3. **冲突处理**: skip/rename/backup/abort 四种策略
4. **激活**: 重启 Claude Code 加载新组件

## 🤝 贡献

欢迎贡献代码、报告问题或提出功能建议！

**贡献方式**:

1. **Fork 项目**: [https://github.com/chengjon/Claude-Kits/fork](https://github.com/chengjon/Claude-Kits/fork)
2. **创建分支**: `git checkout -b feature/amazing-feature`
3. **提交变更**: `git commit -m 'Add amazing feature'`
4. **推送分支**: `git push origin feature/amazing-feature`
5. **提交 PR**: 在 GitHub 上创建 Pull Request

**贡献要求**:

1. ✅ 遵循安全原则（永不覆盖用户文件）
2. ✅ 添加适当的测试覆盖
3. ✅ 更新相关文档
4. ✅ 遵循 500 行规则（技能文档）
5. ✅ 更新组件注册表（运行 `python scripts/components_scanner.py`）
6. ✅ 保持代码风格一致性

**开发环境设置**:
```bash
# 克隆仓库
git clone https://github.com/chengjon/Claude-Kits.git
cd Claude-Kits

# 安装依赖
pip install rich pyyaml

# 运行测试
python scripts/check_conflicts.py /path/to/test-project --dry-run
```

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 🙏 致谢

本项目基于 Reddit 工程师 30 万行代码实践经验构建，感谢：

- **Reddit 工程团队** - 最佳实践和零错误容忍系统
- **Claude Code 团队** - 优秀的 AI 编程助手平台
- **开源社区** - 持续的贡献和反馈

特别感谢所有贡献者的支持！

---

**🚀 版本**: v3.1.0 (2025-11-14)

**📋 最新更新**:
- ✨ **Skills 三层分类浏览** - 9个一级分类，18个二级分类，84个skills
- ✨ **智能路径检测** - 自动检测已安装skills的安装路径
- 🚀 **TUI界面增强** - ESC键支持，详情页面优化，键盘导航改进
- ✅ **跨平台兼容** - Windows/Linux/Unix 全平台键盘支持
- ✅ **组件统计** - 256个Agents、84个Skills、63个Commands、10个Hooks
- ✅ **7个预定义Role** + 自定义Role构建器
- ✅ **零错误容忍系统** + 上下文持久化机制

**🛡️ 安全承诺**: 永远不会覆盖你的文件，所有操作都需要你的确认！
