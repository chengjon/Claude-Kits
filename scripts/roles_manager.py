#!/usr/bin/env python3
"""
Roles Manager - 批量安装组件集合

功能：
1. 列出所有可用的 Role 集合
2. 查看 Role 的详细信息（包含的组件列表）
3. 安装完整的 Role 集合到项目
4. 支持选择性安装（仅 skills、仅 agents 等）
5. 生成详细的安装报告

使用方法：
python roles_manager.py [list|info|install] [role_name] [--path /path/to/project] [--components skills,agents,commands,hooks]
"""

import os
import sys
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# 导入 UniversalInstaller
try:
    from universal_installer import UniversalInstaller
except ImportError:
    # 如果直接运行此脚本，添加 scripts/ 到路径
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from universal_installer import UniversalInstaller

# 默认路径
ROLES_DIR = Path(__file__).parent.parent / 'checklists' / 'roles'

@dataclass
class RoleComponent:
    """Role 中的单个组件"""
    name: str
    reason: str
    component_type: str  # 'skills', 'agents', 'commands', 'hooks'

@dataclass
class RoleDefinition:
    """Role 定义"""
    name: str
    description: str
    role: str
    agents: List[RoleComponent] = field(default_factory=list)
    skills: List[RoleComponent] = field(default_factory=list)
    commands: List[RoleComponent] = field(default_factory=list)
    hooks: List[Dict] = field(default_factory=list)

    @property
    def total_components(self) -> int:
        """总组件数"""
        return len(self.agents) + len(self.skills) + len(self.commands) + len(self.hooks)

@dataclass
class InstallResult:
    """单个组件的安装结果"""
    component_type: str
    component_name: str
    success: bool
    message: str = ""

@dataclass
class InstallReport:
    """完整的安装报告"""
    role_name: str
    target_dir: str
    results: List[InstallResult] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.success)

    @property
    def total_count(self) -> int:
        return len(self.results)

def load_role(role_name: str) -> Optional[RoleDefinition]:
    """
    从 YAML 文件加载 Role 定义

    Args:
        role_name: Role 名称（不带 .yaml 后缀）

    Returns:
        RoleDefinition 对象，如果文件不存在则返回 None
    """
    role_file = ROLES_DIR / f"{role_name}.yaml"

    if not role_file.exists():
        return None

    try:
        with open(role_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        role_def = RoleDefinition(
            name=data.get('name', role_name),
            description=data.get('description', 'No description'),
            role=data.get('role', role_name)
        )

        # 解析 agents
        for agent_data in data.get('agents', []):
            role_def.agents.append(RoleComponent(
                name=agent_data['name'],
                reason=agent_data.get('reason', ''),
                component_type='agents'
            ))

        # 解析 skills
        for skill_data in data.get('skills', []):
            role_def.skills.append(RoleComponent(
                name=skill_data['name'],
                reason=skill_data.get('reason', ''),
                component_type='skills'
            ))

        # 解析 commands
        for command_data in data.get('commands', []):
            # commands 可能只有 name 或完整的 name + reason
            if isinstance(command_data, str):
                name = command_data
                reason = ''
            else:
                name = command_data['name']
                reason = command_data.get('reason', '')

            # 移除命令前缀 '/'
            if name.startswith('/'):
                name = name[1:]

            role_def.commands.append(RoleComponent(
                name=name,
                reason=reason,
                component_type='commands'
            ))

        # 解析 hooks（hooks 结构更复杂，保留原始数据）
        role_def.hooks = data.get('hooks', [])

        return role_def

    except Exception as e:
        print(f"Error: Could not load role '{role_name}': {e}")
        return None

def list_roles() -> List[Tuple[str, str]]:
    """
    列出所有可用的 Role

    Returns:
        List of (role_name, description) tuples
    """
    roles = []

    if not ROLES_DIR.exists():
        return roles

    for role_file in ROLES_DIR.glob('*.yaml'):
        role_name = role_file.stem
        role_def = load_role(role_name)

        if role_def:
            roles.append((role_name, role_def.description))

    return roles

def show_role_info(role_name: str) -> bool:
    """
    显示 Role 的详细信息

    Args:
        role_name: Role 名称

    Returns:
        是否成功显示
    """
    role_def = load_role(role_name)

    if not role_def:
        print(f"Error: Role '{role_name}' not found.")
        return False

    print(f"\n{'='*80}")
    print(f"Role: {role_def.name}")
    print(f"{'='*80}")
    print(f"\n{role_def.description}\n")

    print(f"📊 统计信息:")
    print(f"  - Skills:   {len(role_def.skills)} 个")
    print(f"  - Agents:   {len(role_def.agents)} 个")
    print(f"  - Commands: {len(role_def.commands)} 个")
    print(f"  - Hooks:    {len(role_def.hooks)} 个")
    print(f"  - 总计:     {role_def.total_components} 个组件\n")

    if role_def.skills:
        print(f"🎯 Skills ({len(role_def.skills)} 个):")
        for skill in role_def.skills:
            print(f"  • {skill.name}")
            if skill.reason:
                # 简化原因显示（只显示第一行）
                first_line = skill.reason.strip().split('\n')[0]
                print(f"    └─ {first_line}")
        print()

    if role_def.agents:
        print(f"🤖 Agents ({len(role_def.agents)} 个):")
        for agent in role_def.agents:
            print(f"  • {agent.name}")
            if agent.reason:
                first_line = agent.reason.strip().split('\n')[0]
                print(f"    └─ {first_line}")
        print()

    if role_def.commands:
        print(f"⚡ Slash Commands ({len(role_def.commands)} 个):")
        for command in role_def.commands:
            print(f"  • /{command.name}")
            if command.reason:
                first_line = command.reason.strip().split('\n')[0]
                print(f"    └─ {first_line}")
        print()

    if role_def.hooks:
        print(f"🔗 Hooks ({len(role_def.hooks)} 个):")
        for hook in role_def.hooks:
            event = hook.get('event', 'Unknown')
            script = hook.get('script', 'Unknown')
            matcher = hook.get('matcher')

            hook_desc = f"  • {event}"
            if matcher:
                hook_desc += f" (matcher: {matcher})"
            hook_desc += f" → {script}"
            print(hook_desc)

            if hook.get('reason'):
                first_line = hook['reason'].strip().split('\n')[0]
                print(f"    └─ {first_line}")
        print()

    return True

def install_role(
    role_name: str,
    target_dir: str,
    scope: str = 'project',
    components: Optional[List[str]] = None,
    dry_run: bool = False,
    interactive: bool = True
) -> InstallReport:
    """
    安装 Role 集合到项目

    Args:
        role_name: Role 名称
        target_dir: 目标项目根目录
        scope: 安装作用域 ('user', 'project')
        components: 要安装的组件类型列表，None 表示全部
        dry_run: 预览模式
        interactive: 交互模式

    Returns:
        InstallReport 对象
    """
    report = InstallReport(role_name=role_name, target_dir=target_dir)

    # 加载 Role 定义
    role_def = load_role(role_name)
    if not role_def:
        print(f"❌ 错误: Role '{role_name}' 不存在")
        return report

    # 确定要安装的组件类型
    if components is None:
        components = ['skills', 'agents', 'commands', 'hooks']

    print(f"\n{'='*80}")
    print(f"🚀 Role 安装: {role_def.name}")
    print(f"{'='*80}\n")

    print(f"目标目录: {target_dir}")
    print(f"作用域: {scope}")
    print(f"组件类型: {', '.join(components)}")

    if dry_run:
        print(f"⚠️  Dry-run 模式：仅预览，不执行实际安装\n")
    else:
        print()

    # 统计要安装的组件
    to_install = []

    if 'skills' in components:
        to_install.extend(role_def.skills)
    if 'agents' in components:
        to_install.extend(role_def.agents)
    if 'commands' in components:
        to_install.extend(role_def.commands)
    if 'hooks' in components and role_def.hooks:
        # Hooks 需要特殊处理（安装脚本文件）
        for hook in role_def.hooks:
            script_name = hook.get('script', '').replace('.sh', '').replace('.ts', '')
            if script_name:
                to_install.append(RoleComponent(
                    name=script_name,
                    reason=hook.get('reason', ''),
                    component_type='hooks'
                ))

    print(f"📦 将要安装 {len(to_install)} 个组件:\n")

    # 按类型分组显示
    by_type = {}
    for component in to_install:
        if component.component_type not in by_type:
            by_type[component.component_type] = []
        by_type[component.component_type].append(component)

    for comp_type, comps in sorted(by_type.items()):
        print(f"  {comp_type.upper()} ({len(comps)} 个):")
        for comp in comps:
            print(f"    • {comp.name}")

    print()

    # 交互确认
    if interactive and not dry_run:
        response = input("确认安装? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("❌ 安装已取消")
            return report
        print()

    # 安装每个组件
    installer = UniversalInstaller()

    for component in to_install:
        print(f"🔧 安装 {component.component_type}/{component.name}...")

        try:
            success = installer.install_component(
                component_type=component.component_type,
                component_name=component.name,
                target_dir=target_dir,
                scope=scope,
                dry_run=dry_run,
                interactive=False  # Role 安装时不逐个询问
            )

            result = InstallResult(
                component_type=component.component_type,
                component_name=component.name,
                success=success,
                message="安装成功" if success else "安装失败"
            )

        except FileNotFoundError as e:
            result = InstallResult(
                component_type=component.component_type,
                component_name=component.name,
                success=False,
                message=f"组件不存在: {component.name}"
            )
            print(f"  ⏭️  跳过: {component.name} (未找到)")

        except Exception as e:
            result = InstallResult(
                component_type=component.component_type,
                component_name=component.name,
                success=False,
                message=str(e)
            )
            print(f"  ❌ 错误: {component.name} - {e}")

        report.results.append(result)

    # 打印安装报告
    print(f"\n{'='*80}")
    print(f"📊 安装报告")
    print(f"{'='*80}\n")

    print(f"Role: {role_def.name}")
    print(f"目标: {target_dir}")
    print(f"总计: {report.total_count} 个组件")
    print(f"✅ 成功: {report.success_count} 个")
    print(f"❌ 失败: {report.failed_count} 个\n")

    if report.failed_count > 0:
        print("失败的组件:")
        for result in report.results:
            if not result.success:
                print(f"  ❌ {result.component_type}/{result.component_name}: {result.message}")
        print()

    if not dry_run and report.success_count > 0:
        print("📝 后续步骤:")
        print("  1. 重启 Claude Code 加载新组件")
        print("  2. 检查 .claude/ 目录确认文件已安装")
        if 'hooks' in components:
            print("  3. 配置 .claude/settings.json 添加 hooks 配置")
            print("     (提示: hooks 脚本已安装，但需要在 settings.json 中配置才能激活)")

    return report

def main():
    parser = argparse.ArgumentParser(
        description='Manage Claude Code Role Collections',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available roles
  python roles_manager.py list

  # Show role details
  python roles_manager.py info reddit-case

  # Install complete role
  python roles_manager.py install reddit-case --path /path/to/project

  # Install only skills and agents
  python roles_manager.py install backend-developer --path /project --components skills,agents

  # Dry-run preview
  python roles_manager.py install reddit-case --path /project --dry-run
"""
    )

    parser.add_argument('action', choices=['list', 'info', 'install'], help='Action to perform')
    parser.add_argument('role_name', nargs='?', help='Name of the role')
    parser.add_argument('--path', help='Path to the project directory')
    parser.add_argument('--scope', choices=['user', 'personal', 'project'], default='project',
                       help='Installation scope (default: project)')
    parser.add_argument('--components', help='Comma-separated list of component types to install (skills,agents,commands,hooks)')
    parser.add_argument('--dry-run', action='store_true', help='Preview installation without making changes')
    parser.add_argument('--non-interactive', action='store_true', help='Non-interactive mode (no confirmation prompts)')

    args = parser.parse_args()

    if args.action == 'list':
        roles = list_roles()
        if not roles:
            print("No roles found.")
        else:
            print(f"\n可用的 Role 集合 ({len(roles)} 个):\n")
            for role_name, description in roles:
                print(f"📦 {role_name}")
                # 简化描述（只显示第一行）
                first_line = description.strip().split('\n')[0] if description else "No description"
                print(f"   {first_line}\n")

    elif args.action == 'info':
        if not args.role_name:
            print("Error: role_name is required for info action")
            sys.exit(1)
        success = show_role_info(args.role_name)
        sys.exit(0 if success else 1)

    elif args.action == 'install':
        if not args.role_name:
            print("Error: role_name is required for install action")
            sys.exit(1)
        if not args.path:
            print("Error: --path is required for install action")
            sys.exit(1)

        # 解析 components 参数
        components = None
        if args.components:
            components = [c.strip() for c in args.components.split(',')]
            # 验证组件类型
            valid_types = ['skills', 'agents', 'commands', 'hooks']
            for comp in components:
                if comp not in valid_types:
                    print(f"Error: Invalid component type '{comp}'. Must be one of: {', '.join(valid_types)}")
                    sys.exit(1)

        report = install_role(
            role_name=args.role_name,
            target_dir=args.path,
            scope=args.scope,
            components=components,
            dry_run=args.dry_run,
            interactive=not args.non_interactive
        )

        # 退出码：如果有失败的组件，返回 1
        sys.exit(0 if report.failed_count == 0 else 1)

if __name__ == '__main__':
    main()
