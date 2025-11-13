# 快速安装指南

## 🎉 立即可用！

统一安装系统已经实施完成，现在可以正确地从 `components/` 复制完整的模板到你的项目。

---

## 🚀 快速开始

### 方法 1: 使用专用管理器（单个组件安装）

```bash
# 1. 查看所有可用组件
ls /opt/claude/Claude-Kits/components/skills/     # 72 个 Skills
ls /opt/claude/Claude-Kits/components/agents/     # 大量 Agents
ls /opt/claude/Claude-Kits/components/commands/   # 大量 Commands
ls /opt/claude/Claude-Kits/components/hooks/      # 各类 Hooks

# 2. 安装 Skill
python /opt/claude/Claude-Kits/scripts/skills_manager.py install task-planning-pro \
    --path /path/to/your/project

# 3. 安装 Agent
python /opt/claude/Claude-Kits/scripts/subagents_manager.py install api-architect \
    --path /path/to/your/project

# 4. 安装 Slash Command
python /opt/claude/Claude-Kits/scripts/commands_manager.py install api-mock \
    --path /path/to/your/project

# 5. Dry-run 模式（预览，不执行实际安装）
python /opt/claude/Claude-Kits/scripts/skills_manager.py install task-planning-pro \
    --path /path/to/your/project \
    --dry-run
```

### 方法 2: 批量安装预定义 Role 集合（推荐）

```bash
# 查看所有可用的 Roles
python /opt/claude/Claude-Kits/scripts/roles_manager.py list

# 查看 Role 详情
python /opt/claude/Claude-Kits/scripts/roles_manager.py info backend-developer

# 安装完整的 Role（包括 Reddit-Case）
python /opt/claude/Claude-Kits/scripts/roles_manager.py install backend-developer \
    --path /path/to/your/project

# 只安装特定类型的组件
python /opt/claude/Claude-Kits/scripts/roles_manager.py install backend-developer \
    --path /path/to/your/project \
    --components skills,agents

# Dry-run 预览
python /opt/claude/Claude-Kits/scripts/roles_manager.py install backend-developer \
    --path /path/to/your/project \
    --dry-run
```

### 方法 3: 创建并安装自定义 Role 集合（NEW）

```bash
# 3A: 使用 TUI 图形化构建器（推荐）
python /opt/claude/Claude-Kits/scripts/claude_tui.py
# 1. 导航到 "Role Checklists" 菜单
# 2. 选择 "Create Custom"
# 3. 输入 Role 名称和描述
# 4. 使用多选界面浏览和选择组件：
#    - 方向键或 W/S: 导航
#    - SPACE: 选择/取消选择
#    - TAB: 切换组件类型（Skills/Agents/Commands）
#    - /: 搜索组件
#    - R: 查看已选择的组件
#    - F: 完成选择
# 5. 保存并可选择立即安装
# ⚠️  限制：最多 15 个组件，推荐 10 个以内

# 3B: 直接使用命令行工具
python /opt/claude/Claude-Kits/scripts/custom_role_builder.py
# 同样提供多选界面和实时计数

# 3C: 安装已创建的自定义 Role
python /opt/claude/Claude-Kits/scripts/roles_manager.py install your-custom-role \
    --path /path/to/your/project
```

---

## 📦 安装示例

### 示例 1: 安装 task-planning-pro Skill

```bash
$ cd /path/to/your/project

$ python /opt/claude/Claude-Kits/scripts/skills_manager.py install task-planning-pro --path .

🚀 开始安装 skills/task-planning-pro...

📋 安装计划: task-planning-pro
============================================================

✅ 将要安装 1 个组件:
  • task-planning-pro
    源: /opt/claude/Claude-Kits/components/skills/task-planning-pro
    目标: /path/to/your/project/.claude/skills/task-planning-pro

📦 准备安装 1 个组件
确认安装? (y/N): y

📦 执行安装...
  ✅ 已安装目录: task-planning-pro

✅ 验证安装...
  ✓ YAML frontmatter 验证通过
  ✅ 验证通过: task-planning-pro

🎉 安装成功！

📝 后续步骤:
  1. 重启 Claude Code 加载新 Skill
  2. 测试激活：发送 "我需要规划任务"
  3. 可选：编辑 description 添加项目特定关键词
```

### 示例 2: 预览安装（Dry-run）

```bash
$ python /opt/claude/Claude-Kits/scripts/skills_manager.py install backend-dev-guidelines \
    --path /path/to/your/project \
    --dry-run

🚀 开始安装 skills/backend-dev-guidelines...

📋 安装计划: backend-dev-guidelines
============================================================

✅ 将要安装 1 个组件:
  • backend-dev-guidelines
    源: /opt/claude/Claude-Kits/components/skills/backend-dev-guidelines
    目标: /path/to/your/project/.claude/skills/backend-dev-guidelines

[yellow]Dry-run 模式：不会执行实际安装[/yellow]
```

### 示例 3: 非交互模式（自动跳过冲突）

```bash
$ python /opt/claude/Claude-Kits/scripts/skills_manager.py install task-planning-pro \
    --path /path/to/your/project \
    --non-interactive

# 如果文件已存在，自动跳过（不询问用户）
⏭️  跳过: task-planning-pro (已存在)
```

### 示例 4: 安装 Agent

```bash
$ python /opt/claude/Claude-Kits/scripts/subagents_manager.py install api-architect \
    --path /path/to/your/project

🚀 开始安装 agents/api-architect...

📋 安装计划: api-architect
============================================================

✅ 将要安装 1 个组件:
  • api-architect
    源: /opt/claude/Claude-Kits/components/agents/api-architect.md
    目标: /path/to/your/project/.claude/agents/api-architect.md

📦 执行安装...
  ✅ 已安装文件: api-architect

✅ 验证安装...
  ✓ YAML frontmatter 验证通过
  ✅ 验证通过: api-architect

🎉 安装成功！

📝 后续步骤:
  1. 重启 Claude Code
  2. 使用 Task tool 调用: subagent_type="api-architect"
```

### 示例 5: 安装 Slash Command

```bash
$ python /opt/claude/Claude-Kits/scripts/commands_manager.py install api-mock \
    --path /path/to/your/project

🚀 开始安装 commands/api-mock...

📋 安装计划: api-mock
============================================================

✅ 将要安装 1 个组件:
  • api-mock
    源: /opt/claude/Claude-Kits/components/commands/api-mock.md
    目标: /path/to/your/project/.claude/commands/api-mock.md

📦 执行安装...
  ✅ 已安装文件: api-mock

✅ 验证安装...
  ✅ 验证通过: api-mock

🎉 安装成功！

📝 后续步骤:
  1. 重启 Claude Code
  2. 使用命令: /api-mock
```

---

## 🎯 可用的 Skills（72 个）

### Reddit Case Skills (11 个)
- `backend-dev-guidelines` - 后端开发指南
- `frontend-dev-guidelines` - 前端开发指南
- `dev-docs-workflow` - Dev Docs 工作流
- `skill-developer` - Skill 开发元技能
- `workflow-developer` - 工作流开发指南
- `notification-developer` - 通知系统开发
- `progressive-disclosure-pattern` - 渐进式披露模式
- `task-planning-pro` - 任务规划专家
- `code-style-enforcer` - 代码风格执行器
- `conversational-coding-assistant` - 对话式编程助手
- `parallel-execution-optimizer` - 并行执行优化器

### 通用 Skills (61 个)
- `code-reviewer` - 代码审查
- `debugging-strategies` - 调试策略
- `async-python-patterns` - Python 异步模式
- `typescript-advanced-types` - TypeScript 高级类型
- `architecture-patterns` - 架构模式
- `api-design-principles` - API 设计原则
- `microservices-patterns` - 微服务模式
- `gitops-workflow` - GitOps 工作流
- `helm-chart-scaffolding` - Helm Chart 脚手架
- ... 还有 52 个更多 Skills

**查看完整列表**:
```bash
ls /opt/claude/Claude-Kits/components/skills/
```

---

## 🔧 命令参数说明

### skills_manager.py 参数

```bash
python scripts/skills_manager.py install SKILL_NAME [OPTIONS]

必需参数:
  SKILL_NAME              要安装的 Skill 名称

可选参数:
  --path PATH             目标项目路径（默认：当前目录）
  --scope {user|project}  安装作用域（默认：project）
                          - user: ~/.claude/skills/
                          - project: {path}/.claude/skills/
  --dry-run               预览模式，不执行实际安装
  --non-interactive       非交互模式，自动跳过冲突
```

### UniversalInstaller 参数

```bash
python scripts/universal_installer.py TYPE NAME [OPTIONS]

必需参数:
  TYPE                    组件类型: skills|agents|hooks|commands
  NAME                    组件名称

可选参数:
  --target-dir DIR        目标项目根目录（必需）
  --scope {user|project}  安装作用域（默认：project）
  --dry-run               预览模式
  --non-interactive       非交互模式
```

---

## ⚠️ 冲突处理

当目标位置已存在同名文件时，会提示你选择处理方式：

```
⚠️  冲突: /path/.claude/skills/my-skill 已存在
   源: /opt/claude/Claude-Kits/components/skills/my-skill
   目标: /path/.claude/skills/my-skill

选项:
  [s] skip    - 跳过，保留现有文件（推荐）
  [r] rename  - 重命名新文件（添加后缀）
  [b] backup  - 备份现有文件后安装新文件
  [a] abort   - 中止安装

你的选择 (s/r/b/a):
```

**推荐选择**: `skip` - 保留现有文件，避免覆盖你的自定义修改

---

## 📝 安装后步骤

1. **重启 Claude Code**
   - 让 Claude Code 重新加载新安装的 Skills

2. **测试 Skill 激活**
   - 根据 Skill 的 `description` 发送相关提示
   - 例如 task-planning-pro: "我需要规划一个功能的开发任务"

3. **可选：自定义 description**
   - 编辑 `.claude/skills/SKILL_NAME/SKILL.md`
   - 在 `description` 字段添加项目特定的触发关键词

---

## 🐛 故障排查

### 问题 1: "Source not found" 错误

```bash
❌ 错误: Source not found: /opt/claude/Claude-Kits/components/skills/my-skill
```

**解决方案**:
- 检查 Skill 名称是否正确
- 查看所有可用 Skills: `ls /opt/claude/Claude-Kits/components/skills/`

### 问题 2: 权限错误

```bash
❌ 没有写入权限: /path/to/project
```

**解决方案**:
```bash
# 检查目录权限
ls -la /path/to/project

# 修改权限（如需要）
chmod u+w /path/to/project
```

### 问题 3: Hook 脚本不可执行

```bash
⚠️  Hook 脚本不可执行
```

**解决方案**:
```bash
# 手动设置可执行权限
chmod +x .claude/hooks/*.sh
```

---

## 📚 相关文档

- `docs/UNIVERSAL_INSTALLER_DESIGN.md` - 详细设计文档
- `docs/INSTALLATION_SYSTEM_IMPLEMENTATION.md` - 实施总结
- `CLAUDE.md` - 项目指导和安全原则

---

## 🚀 批量安装 - Roles Manager（新功能）

### 什么是 Role？

Role 是一组预定义的组件集合（Skills + Agents + Commands + Hooks），代表特定的开发角色或工作场景。

**可用的 Roles (7 个)**:
- `reddit-case` - Reddit 工程师 30 万行代码实践
- `backend-developer` - 后端开发工具集
- `frontend-developer` - 前端开发工具集
- `fullstack-developer` - 全栈开发工具集
- `devops-engineer` - DevOps 工具集
- `test-engineer` - 测试工程师工具集
- `security-engineer` - 安全工程师工具集

### 使用方法

```bash
# 1. 查看所有可用的 Roles
python scripts/roles_manager.py list

# 2. 查看 Role 详情（包含的组件列表）
python scripts/roles_manager.py info backend-developer

# 3. 安装完整的 Role（所有组件）
python scripts/roles_manager.py install backend-developer --path /project

# 4. 只安装特定类型的组件
python scripts/roles_manager.py install backend-developer \
    --path /project \
    --components skills,agents

# 5. Dry-run 预览
python scripts/roles_manager.py install reddit-case \
    --path /project \
    --dry-run

# 6. 非交互模式
python scripts/roles_manager.py install devops-engineer \
    --path /project \
    --non-interactive
```

### 示例输出

```bash
$ python scripts/roles_manager.py info backend-developer

================================================================================
Role: Backend Developer
================================================================================

Essential tools for backend development, API design, and database management

📊 统计信息:
  - Skills:   4 个
  - Agents:   5 个
  - Commands: 4 个
  - Hooks:    0 个
  - 总计:     13 个组件

🎯 Skills (4 个):
  • sql-optimization-patterns
  • error-handling-patterns
  • debugging-strategies
  • code-review-excellence

🤖 Agents (5 个):
  • backend-architect
  • database-optimizer
  • api-designer
  • test-writer
  • debugger
```

---

## 🎨 自定义 Role 构建器使用指南（方法 3 详解）

### 什么是自定义 Role？

自定义 Role 允许你根据特定项目需求，从 72+ 可用组件中精心挑选组合，创建专属的组件集合。

### 为什么使用自定义 Role？

- ✅ **精准匹配需求**: 只选择真正需要的组件，避免冗余
- ✅ **保持简洁**: 强制限制（≤15 个组件），防止过度安装
- ✅ **可重用**: 保存为 YAML 文件，可在多个项目中重复使用
- ✅ **易于分享**: 团队成员可以共享自定义 Role 配置

### 使用 TUI 图形化构建器（推荐）

#### 启动构建器

```bash
python scripts/claude_tui.py
# 或使用 tmux 运行（避免终端兼容性问题）
bash scripts/run_tui_with_tmux.sh
```

#### 导航到创建界面

1. 使用方向键或 W/S 导航到 **"Role Checklists"**
2. 按 Enter 进入子菜单
3. 选择 **"Create Custom"**

#### 输入基本信息

```
Role name: my-project-toolkit
Description: Custom toolkit for my web application project
```

#### 多选组件界面操作

**界面布局**:
```
Custom Role Builder: my-project-toolkit | Components: 5/15

• SKILLS •  agents  commands

🔍 Search: (Press '/' to search)

→ [✓] task-planning-pro
    Expert task planning and breakdown for complex features

  [ ] code-style-enforcer
    Enforce coding standards and best practices

  [✓] debugging-strategies
    Advanced debugging techniques and troubleshooting

  [ ] sql-optimization-patterns
    Database query optimization and indexing strategies

================================================================
Controls:
  ↑/↓ or W/S: Navigate  |  SPACE: Select/Deselect  |  TAB: Switch type
  /: Search  |  R: Review selections  |  F: Finish  |  Q: Cancel
```

**键盘操作**:
- **方向键 ↑/↓** 或 **W/S**: 上下导航组件列表
- **SPACE**: 选择/取消选择当前组件
- **TAB**: 在 Skills/Agents/Commands 之间切换
- **/**: 打开搜索框，可以按名称或描述搜索
- **R**: 查看当前已选择的所有组件
- **F**: 完成选择，进入保存流程
- **Q**: 取消并退出

#### 数量限制和警告

- **绿色 (0-9 个)**: `5/15` - 正常范围
- **黄色 (10-14 个)**: `12/15 (⚠️  Approaching limit)` - 接近推荐上限
- **红色 (15 个)**: `15/15 (LIMIT REACHED)` - 达到最大限制，无法再选择

达到 15 个限制后，必须先取消选择已有组件才能选择新的。

#### 审查和保存

1. 按 **R** 键查看已选择的组件汇总
2. 按 **F** 键完成选择
3. 确认保存 (y/n)
4. 选择是否立即安装

### 使用命令行工具

```bash
python scripts/custom_role_builder.py
```

提供与 TUI 相同的多选界面，适合在不方便使用 TUI 的环境中运行。

### 安装自定义 Role

创建完成后，自定义 Role 会保存到 `checklists/roles/your-role-name.yaml`。

**安装方式**:

```bash
# 方式 1: 使用 roles_manager.py
python scripts/roles_manager.py install my-project-toolkit --path /path/to/project

# 方式 2: 在 TUI 中安装
python scripts/claude_tui.py
# 导航到 "Role Checklists" → "Install from Checklist" → 选择 "role"
```

### 管理自定义 Role

**查看**:
```bash
python scripts/roles_manager.py info my-project-toolkit
```

**编辑**:
```bash
# 方法 1: 在 TUI 中编辑
python scripts/claude_tui.py
# 导航到 "Role Checklists" → "Edit Custom"

# 方法 2: 直接编辑 YAML 文件
nano checklists/roles/my-project-toolkit.yaml
```

**删除**:
```bash
# 在 TUI 中删除
python scripts/claude_tui.py
# 导航到 "Role Checklists" → "Delete Custom"
```

### 自定义 Role 最佳实践

1. **按项目类型组织**: 为不同类型的项目创建不同的 Role
   - `web-api-toolkit` - API 开发专用
   - `frontend-spa-toolkit` - 前端 SPA 开发
   - `data-pipeline-toolkit` - 数据处理管道

2. **控制组件数量**: 严格遵守 ≤10 个推荐限制
   - 只选择真正会使用的组件
   - 避免"以防万一"的选择

3. **使用描述性名称**: 让 Role 名称清晰表达用途
   - ✅ `react-typescript-project`
   - ❌ `my-role`

4. **团队共享**: 将自定义 Role YAML 文件提交到版本控制
   ```bash
   git add checklists/roles/team-shared-toolkit.yaml
   git commit -m "Add team shared toolkit role"
   ```

---

## 🚀 下一步

### Phase 4: TUI 改进（可选）
- 详情页面添加 Install 按钮
- Roles Manager 界面
- 安装进度实时显示

---

## 💡 使用技巧

### 技巧 1: 批量预览

```bash
# 预览多个 Skills 的安装
for skill in task-planning-pro code-style-enforcer debugging-strategies; do
    echo "=== Previewing $skill ==="
    python scripts/skills_manager.py install $skill --path /project --dry-run
done
```

### 技巧 2: 创建安装脚本

```bash
#!/bin/bash
# install-my-skills.sh

PROJECT_PATH="/path/to/my/project"
SKILLS="task-planning-pro backend-dev-guidelines debugging-strategies"

for skill in $SKILLS; do
    python /opt/claude/Claude-Kits/scripts/skills_manager.py install $skill \
        --path "$PROJECT_PATH" \
        --non-interactive
done

echo "✅ All skills installed!"
```

### 技巧 3: 验证安装

```bash
# 检查 Skill 是否安装成功
ls -la /path/to/project/.claude/skills/task-planning-pro/

# 验证 YAML frontmatter
head -20 /path/to/project/.claude/skills/task-planning-pro/SKILL.md
```

---

**版本**: 3.0.0
**更新日期**: 2025-11-10
**状态**: ✅ 可立即使用（Phase 1, 2 & 3 完成）

**Phase 2 新增功能**:
- ✅ `subagents_manager.py` 支持从 components/agents/ 安装
- ✅ `commands_manager.py` 支持从 components/commands/ 安装
- ✅ 所有管理器统一使用 UniversalInstaller
- ✅ 统一的 CLI 接口（--dry-run, --non-interactive）

**Phase 3 新增功能**:
- ✅ `roles_manager.py` 批量安装组件集合
- ✅ 支持 7 个预定义 Roles（reddit-case, backend-developer 等）
- ✅ 支持选择性安装（--components skills,agents,commands,hooks）
- ✅ 详细的安装报告和统计信息
