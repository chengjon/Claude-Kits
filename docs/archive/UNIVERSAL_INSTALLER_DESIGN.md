# 统一安装程序设计文档

## 🎯 设计目标

根据用户反馈，重新设计 Claude-Kits 的安装系统，实现：

1. **统一的公用安装程序** - 单一入口，处理所有组件类型的安装
2. **从模板库复制** - 从 `components/` 复制完整的模板到项目
3. **Role 集合安装** - 支持安装预定义的工具集合（如 Reddit Case Study）
4. **TUI 深度集成** - 详情页面直接安装，流畅的用户体验

---

## 📋 当前问题分析

### 问题 1: `skills_manager.py install` 不复制模板
```python
# 当前代码：只创建空模板
def install_skill(skill_name, scope='project', project_path=None, template_dir=None):
    target_dir.mkdir(parents=True, exist_ok=True)

    if template_dir and Path(template_dir).exists():
        pass  # ← 什么都不做！

    # 只创建一个空的 SKILL.md
```

**应该做的**：从 `components/skills/` 复制完整的 Skill（包括 resources/）

---

### 问题 2: `install_reddit_case.py` 只针对特定 Role
```python
# 当前代码：硬编码 Reddit Case 的路径
self.components = {
    'skills': self.source_dir / '.claude' / 'skills',  # 错误的源路径
    ...
}
```

**应该做的**：
- 创建通用的安装程序，可以处理任何 Role
- 读取 `checklists/roles/*.yaml` 获取工具列表
- 逐个安装每个组件

---

### 问题 3: TUI 流程不直观
**当前流程**：
```
Skills Manager → List → (无法直接安装)
```

**应该做的流程**：
```
Skills Manager → View Details → 选择 Skill → 查看详情 → Install
```

---

## 🏗️ 新架构设计

### 核心组件

```
scripts/
├── universal_installer.py       # 🔧 核心：公用安装程序
├── skills_manager.py            # 调用 universal_installer
├── subagents_manager.py         # 调用 universal_installer
├── hooks_manager.py             # 调用 universal_installer
├── commands_manager.py          # 调用 universal_installer
├── roles_manager.py             # 🆕 管理 Role 集合安装
└── claude_tui.py                # 集成新的安装流程
```

---

## 📦 Universal Installer 设计

### 功能规格

```python
class UniversalInstaller:
    """
    统一安装程序 - 处理所有组件类型的安装

    核心原则：
    1. 永不覆盖用户文件（除非明确授权）
    2. 从 components/ 复制完整模板
    3. 支持冲突检测和处理
    4. 透明显示所有操作
    """

    def install_component(
        self,
        component_type: str,      # 'skills', 'agents', 'hooks', 'commands'
        component_name: str,       # 如 'task-planning-pro'
        target_dir: str,           # 目标项目根目录
        scope: str = 'project',    # 'user', 'project', 'plugin'
        dry_run: bool = False,     # 预览模式
        interactive: bool = True,  # 交互模式
    ) -> bool:
        """安装单个组件"""
        pass

    def install_role(
        self,
        role_name: str,            # 如 'reddit-case'
        target_dir: str,
        components: List[str],     # ['skills', 'agents', 'hooks']
        dry_run: bool = False,
    ) -> bool:
        """安装 Role 集合"""
        pass
```

---

### 安装流程

#### 单个组件安装

```
1. 确定源路径
   components/{component_type}/{component_name}/

2. 确定目标路径
   {target_dir}/.claude/{component_type}/{component_name}/

3. 检查冲突
   - 目标是否存在
   - 是否有写入权限

4. 处理冲突
   - skip: 跳过
   - rename: 新文件添加后缀
   - backup: 备份原文件
   - abort: 中止安装

5. 复制文件
   shutil.copytree(source, target)

6. 验证安装
   - 检查文件完整性
   - 验证 YAML frontmatter（Skills/Agents）
   - 验证权限（Hooks）
```

#### Role 集合安装

```
1. 读取 Role 配置
   checklists/roles/{role_name}.yaml

2. 解析组件列表
   agents: [...]
   skills: [...]
   hooks: [...]
   commands: [...]

3. 依次安装每个组件
   for each component in list:
       install_component(...)

4. 生成安装报告
   - 成功安装的组件
   - 跳过的组件（冲突）
   - 失败的组件（错误）

5. 后续配置提示
   - 需要自定义的文件
   - 需要设置权限的脚本
```

---

## 🎨 TUI 改进设计

### 新的交互流程

#### 场景 1: 安装单个 Skill

```
用户操作:
1. 启动 TUI: python scripts/claude_tui.py
2. 选择: Skills Manager
3. 选择: View Details (默认)
4. 浏览: 显示所有可用 Skills（从 components_registry.json）
5. 选择: 输入编号选择 Skill
6. 查看: 详情页面显示名称、描述、路径等
7. 选择: Install 选项
8. 输入: 目标项目路径
9. 选择: 作用域（user/project）
10. 确认: 查看安装计划
11. 执行: 安装

系统操作:
- 调用 UniversalInstaller.install_component()
- 显示进度和结果
```

#### 场景 2: 安装 Role 集合

```
用户操作:
1. 启动 TUI
2. 选择: Roles Manager (新增)
3. 选择: View Roles
4. 浏览: 显示所有 Role（reddit-case, backend-developer, ...）
5. 选择: 输入编号选择 Role
6. 查看: 详情页面显示包含的组件列表
7. 选择: Install Role
8. 选择: 要安装的组件类型（All/Skills Only/Agents Only/...）
9. 输入: 目标项目路径
10. 确认: 查看详细安装计划
11. 执行: 批量安装

系统操作:
- 调用 UniversalInstaller.install_role()
- 显示每个组件的安装进度
- 生成最终报告
```

---

## 📁 目录结构映射

### 源路径（模板库）

```
Claude-Kits/
└── components/
    ├── skills/
    │   ├── task-planning-pro/
    │   │   ├── SKILL.md
    │   │   └── resources/
    │   │       ├── task-breakdown-patterns.md
    │   │       ├── progress-tracking-patterns.md
    │   │       └── ...
    │   ├── code-style-enforcer/
    │   └── ...
    │
    ├── agents/
    │   ├── code-architecture-reviewer.md
    │   ├── build-error-resolver.md
    │   └── ...
    │
    ├── hooks/
    │   ├── skill-activation-prompt.sh
    │   ├── build-checker.sh
    │   └── ...
    │
    └── commands/
        ├── dev-docs.md
        ├── code-review.md
        └── ...
```

### 目标路径（用户项目）

```
/path/to/user-project/
└── .claude/
    ├── skills/
    │   ├── task-planning-pro/
    │   │   ├── SKILL.md
    │   │   └── resources/
    │   └── ...
    │
    ├── agents/
    │   ├── code-architecture-reviewer.md
    │   └── ...
    │
    ├── hooks/
    │   ├── skill-activation-prompt.sh
    │   └── ...
    │
    ├── commands/
    │   ├── dev-docs.md
    │   └── ...
    │
    └── settings.json  # Hooks 配置
```

---

## 🔒 安全保证

### 1. 永不覆盖用户文件

```python
def check_conflict(target_path: Path) -> bool:
    """检查目标路径是否已存在"""
    if target_path.exists():
        return True  # 存在冲突
    return False

def handle_conflict(conflict_type: str, interactive: bool) -> ConflictAction:
    """处理冲突"""
    if interactive:
        choice = prompt_user("File exists. Action? (skip/rename/backup/abort)")
        return ConflictAction(choice)
    else:
        return ConflictAction.SKIP  # 非交互模式默认跳过
```

### 2. 透明的操作预览

```python
def generate_install_plan(components: List[str]) -> InstallPlan:
    """生成安装计划"""
    plan = InstallPlan()

    for component in components:
        source = get_source_path(component)
        target = get_target_path(component)

        if check_conflict(target):
            plan.add_conflict(component, source, target)
        else:
            plan.add_operation(component, source, target)

    return plan

def show_install_plan(plan: InstallPlan):
    """显示安装计划"""
    console.print("\n📋 安装计划:")
    console.print(f"\n将要安装 {plan.count_operations()} 个组件:")
    for op in plan.operations:
        console.print(f"  ✅ {op.component} → {op.target}")

    if plan.has_conflicts():
        console.print(f"\n⚠️  发现 {plan.count_conflicts()} 个冲突:")
        for conflict in plan.conflicts:
            console.print(f"  ❌ {conflict.target} (已存在)")
```

### 3. Dry-run 模式

```python
def install_component(..., dry_run: bool = False):
    """安装组件"""
    plan = generate_install_plan(...)
    show_install_plan(plan)

    if dry_run:
        console.print("\n[yellow]Dry-run 模式：不会执行实际安装[/yellow]")
        return True

    # 确认后执行实际安装
    if not confirm_install():
        console.print("安装已取消")
        return False

    execute_install_plan(plan)
```

---

## 🚀 实施计划

### Phase 1: 创建 UniversalInstaller
- [ ] 实现 `universal_installer.py`
- [ ] 单元测试：冲突检测、文件复制、权限处理
- [ ] 集成测试：安装单个 Skill/Agent/Hook/Command

### Phase 2: 修改现有 Managers
- [ ] 修改 `skills_manager.py` 调用 UniversalInstaller
- [ ] 修改 `subagents_manager.py` 调用 UniversalInstaller
- [ ] 修改 `hooks_manager.py` 调用 UniversalInstaller
- [ ] 修改 `commands_manager.py` 调用 UniversalInstaller
- [ ] 向后兼容：保留现有 CLI 接口

### Phase 3: 创建 Roles Manager
- [ ] 实现 `roles_manager.py`
- [ ] 支持读取 `checklists/roles/*.yaml`
- [ ] 支持批量安装组件
- [ ] 生成安装报告

### Phase 4: 改进 TUI
- [ ] 修改 `handle_skills_actions()` 添加详情页 Install
- [ ] 添加 `handle_roles_actions()` 管理 Role 集合
- [ ] 优化交互流程和用户体验
- [ ] 添加安装进度显示

### Phase 5: 测试和文档
- [ ] 端到端测试：TUI → Install → 验证
- [ ] 更新 README.md 和 CLAUDE.md
- [ ] 创建视频演示或截图
- [ ] 更新所有安装相关文档

---

## 📊 使用示例

### 命令行安装单个 Skill

```bash
# 使用新的 UniversalInstaller
python scripts/skills_manager.py install task-planning-pro \
    --scope project \
    --path /path/to/my-project

# 内部调用：
# UniversalInstaller.install_component(
#     component_type='skills',
#     component_name='task-planning-pro',
#     target_dir='/path/to/my-project',
#     scope='project'
# )
```

### 命令行安装 Role 集合

```bash
# 安装 Reddit Case 的所有组件
python scripts/roles_manager.py install reddit-case \
    --path /path/to/my-project \
    --components all

# 只安装 Skills 和 Agents
python scripts/roles_manager.py install reddit-case \
    --path /path/to/my-project \
    --components skills,agents

# Dry-run 预览
python scripts/roles_manager.py install reddit-case \
    --path /path/to/my-project \
    --dry-run
```

### TUI 交互式安装

```bash
# 启动 TUI
python scripts/claude_tui.py

# 用户操作流程：
# 1. Skills Manager → View Details
# 2. 选择 "5" (task-planning-pro)
# 3. 查看详情页面
# 4. 选择 "Install"
# 5. 输入目标路径
# 6. 确认安装
```

---

## 🎯 预期效果

### 安装成功输出示例

```
🚀 开始安装 task-planning-pro...

📋 安装计划:
  源路径: /opt/claude/Claude-Kits/components/skills/task-planning-pro
  目标路径: /home/user/my-project/.claude/skills/task-planning-pro
  作用域: project

✅ 检查前提条件...
  ✓ 目标目录存在
  ✓ 有写入权限
  ✓ 无冲突

📦 复制文件...
  ✓ SKILL.md (379 行)
  ✓ resources/task-breakdown-patterns.md (63 行)
  ✓ resources/progress-tracking-patterns.md (441 行)
  ✓ resources/practical-scenarios.md (137 行)
  ✓ resources/advanced-tips.md (168 行)

✅ 验证安装...
  ✓ YAML frontmatter 有效
  ✓ 文件完整性检查通过

🎉 安装成功！

📝 后续步骤:
  1. 重启 Claude Code 加载新 Skill
  2. 测试激活：发送 "我需要规划任务"
  3. 可选：编辑 description 添加项目特定关键词
```

### Role 安装输出示例

```
🚀 开始安装 Reddit Case Study...

📋 Role 配置:
  名称: Reddit Case Study - 30万行代码工程实践
  包含组件:
    - 7 个 Agents
    - 7 个 Skills
    - 4 个 Commands
    - 9 个 Hooks
  目标路径: /home/user/my-project

确认安装? (y/N): y

📦 安装进度:

Agents (7/7):
  ✅ code-architecture-reviewer
  ✅ build-error-resolver
  ✅ strategic-plan-architect
  ✅ frontend-error-fixer
  ✅ documentation-architect
  ✅ auth-route-tester
  ✅ database-verifier

Skills (7/7):
  ✅ backend-dev-guidelines
  ✅ frontend-dev-guidelines
  ✅ skill-developer
  ✅ workflow-developer
  ✅ notification-developer
  ✅ progressive-disclosure-pattern
  ✅ dev-docs-workflow

Commands (4/4):
  ✅ /dev-docs
  ✅ /dev-docs-update
  ✅ /code-review
  ✅ /build-and-fix

Hooks (9/9):
  ✅ skill-activation-prompt.sh
  ✅ file-edit-tracker.sh
  ✅ build-checker.sh
  ⚠️  error-handling-reminder.sh (冲突，已跳过)
  ✅ dev-docs-injector.sh
  ✅ dev-docs-snapshot.sh
  ✅ pm2-permission-gatekeeper.sh
  ✅ batch-prettier.sh
  ✅ desktop-notifier.sh

🎉 安装完成！

📊 安装摘要:
  ✅ 成功: 26 个组件
  ⚠️  跳过: 1 个组件（冲突）
  ❌ 失败: 0 个组件

📝 后续配置:
  1. 设置 hook 可执行权限: chmod +x .claude/hooks/*.sh
  2. 编辑 .claude/skill-rules.json 定制触发规则
  3. 编辑 .claude/build-checker.json 配置构建命令
  4. 重启 Claude Code
```

---

## 📚 相关文档

- `CLAUDE.md` - 安全原则和项目指导
- `checklists/roles/*.yaml` - Role 配置示例
- `components_registry.json` - 组件注册表
- `INSTALLATION.md` - 用户安装指南

---

**版本**: 1.0.0
**创建日期**: 2025-11-10
**状态**: 设计阶段
