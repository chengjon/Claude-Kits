#!/usr/bin/env python3
"""
Slash Commands 管理脚本

功能：
1. 浏览可用的 Slash Commands (个人, 项目, 插件)
2. 安装/创建新的 Slash Command (个人: ~/.claude/commands/, 项目: .claude/commands/)
3. 修改现有 Slash Command 的内容或元数据
4. 删除 Slash Command
5. 验证 Slash Command 配置 (YAML 语法等)

使用方法：
python commands_manager.py [list|install|edit|delete|validate] [command_name] [--scope personal|project] [--path /path/to/project]
"""

import os
import sys
import argparse
import yaml
import subprocess
from pathlib import Path

# 导入 UniversalInstaller
try:
    from universal_installer import UniversalInstaller
except ImportError:
    # 如果直接运行此脚本，添加 scripts/ 到路径
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from universal_installer import UniversalInstaller

# 默认路径
USER_COMMANDS_DIR = Path.home() / '.claude' / 'commands'
PROJECT_COMMANDS_DIR = Path('.claude') / 'commands'

def get_commands(scope='all', project_path=None):
    """获取指定范围内的所有 Slash Commands"""
    commands = {}
    
    if scope in ['all', 'personal']:
        personal_commands = _list_commands_in_dir(USER_COMMANDS_DIR, 'personal')
        commands.update(personal_commands)
        
    if scope in ['all', 'project']:
        project_dir = Path(project_path) / '.claude' / 'commands' if project_path else PROJECT_COMMANDS_DIR
        project_commands = _list_commands_in_dir(project_dir, 'project')
        commands.update(project_commands)
        
    # 插件 Commands 需要通过 Claude Code 本身或插件系统获取，这里暂不实现
    # if scope in ['all', 'plugin']:
    #     plugin_commands = _list_plugin_commands()
    #     commands.update(plugin_commands)
        
    return commands

def _list_commands_in_dir(commands_dir, scope_type):
    """列出指定目录及其子目录下的 Slash Commands"""
    commands = {}
    if commands_dir.exists():
        # 使用 rglob 递归查找所有 .md 文件
        for command_file in commands_dir.rglob('*.md'):
            # 计算相对于 commands_dir 的路径，用于构造命令名
            relative_path = command_file.relative_to(commands_dir)
            # stem 是不带扩展名的文件名
            parts = relative_path.with_suffix('').parts
            command_name = '/'.join(parts)  # 例如: db/migrate -> db/migrate
            
            try:
                with open(command_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单解析 YAML frontmatter
                    description = "No description"
                    argument_hint = ""
                    if content.startswith('---'):
                        end = content.find('---', 3)
                        if end != -1:
                            frontmatter = yaml.safe_load(content[3:end])
                            description = frontmatter.get('description', description)
                            argument_hint = frontmatter.get('argument-hint', argument_hint)
                            
                    commands[command_name] = {
                        'name': command_name,
                        'description': description,
                        'argument_hint': argument_hint,
                        'scope': scope_type,
                        'path': str(command_file),
                        'namespace': '/'.join(parts[:-1]) if len(parts) > 1 else ''
                    }
            except Exception as e:
                print(f"Warning: Could not parse {command_file}: {e}")
    return commands

def install_command(command_name, scope='project', project_path=None, template_dir=None, dry_run=False, interactive=True):
    """安装一个 Slash Command（使用 UniversalInstaller）

    从 components/commands/ 复制完整的 Command 模板到目标位置。

    Args:
        command_name: Command 名称（如 'review-pr'）
        scope: 安装作用域 ('personal', 'project')
        project_path: 项目路径（scope='project' 时使用）
        template_dir: 已废弃（兼容性保留）
        dry_run: 预览模式，不执行实际安装
        interactive: 交互模式，冲突时询问用户

    Returns:
        bool: 是否安装成功
    """
    # 确定目标目录
    if scope == 'personal':
        target_dir = str(Path.home())
    elif scope == 'project':
        target_dir = project_path if project_path else str(Path.cwd())
    else:
        raise ValueError(f"Unknown scope: {scope}. Must be 'personal' or 'project'")

    # 使用 UniversalInstaller 安装
    try:
        installer = UniversalInstaller()
        success = installer.install_component(
            component_type='commands',
            component_name=command_name,
            target_dir=target_dir,
            scope=scope,
            dry_run=dry_run,
            interactive=interactive
        )
        return success
    except FileNotFoundError as e:
        print(f"Error: Slash Command '{command_name}' not found in components/commands/")
        print(f"Available commands: run 'python scripts/commands_manager.py list'")
        return False
    except Exception as e:
        print(f"Error installing command: {e}")
        return False

def edit_command(command_name, scope='project', project_path=None):
    """编辑一个现有的 Slash Command"""
    # 确定 Command 的位置
    command_path = None
    project_dir = Path(project_path) if project_path else Path.cwd()
    
    # 优先查找项目级 Command
    if scope in ['project', 'all']:
        project_command_file = project_dir / '.claude' / 'commands'
        # 重构 command_name 为路径
        parts = Path(command_name).parts
        file_name = parts[-1] + '.md'
        namespace_dirs = parts[:-1]
        full_project_path = project_command_file.joinpath(*namespace_dirs, file_name)
        if full_project_path.exists():
            command_path = full_project_path
            
    # 如果没找到或指定了个人范围，查找个人 Command
    if command_path is None and scope in ['personal', 'all']:
        personal_command_file = USER_COMMANDS_DIR
        parts = Path(command_name).parts
        file_name = parts[-1] + '.md'
        namespace_dirs = parts[:-1]
        full_personal_path = personal_command_file.joinpath(*namespace_dirs, file_name)
        if full_personal_path.exists():
            command_path = full_personal_path
            
    if command_path is None:
        print(f"Error: Slash Command '{command_name}' not found.")
        return False
        
    # 使用系统默认编辑器打开
    editor = os.environ.get('EDITOR', 'nano')  # 默认使用 nano
    try:
        subprocess.run([editor, str(command_path)])
        print(f"Successfully edited Slash Command '{command_name}' at {command_path}")
        return True
    except Exception as e:
        print(f"Error: Could not open editor: {e}")
        # 提示用户手动编辑
        print(f"Please manually edit the file: {command_path}")
        return False

def delete_command(command_name, scope='project', project_path=None):
    """删除一个 Slash Command"""
    command_path = None
    project_dir = Path(project_path) if project_path else Path.cwd()
    
    if scope in ['project', 'all']:
        project_command_file = project_dir / '.claude' / 'commands'
        parts = Path(command_name).parts
        file_name = parts[-1] + '.md'
        namespace_dirs = parts[:-1]
        full_project_path = project_command_file.joinpath(*namespace_dirs, file_name)
        if full_project_path.exists():
            command_path = full_project_path
            
    if command_path is None and scope in ['personal', 'all']:
        personal_command_file = USER_COMMANDS_DIR
        parts = Path(command_name).parts
        file_name = parts[-1] + '.md'
        namespace_dirs = parts[:-1]
        full_personal_path = personal_command_file.joinpath(*namespace_dirs, file_name)
        if full_personal_path.exists():
            command_path = full_personal_path
            
    if command_path is None:
        print(f"Error: Slash Command '{command_name}' not found in specified scope.")
        return False
        
    try:
        command_path.unlink()
        # 如果目录为空，尝试删除目录
        try:
            command_path.parent.rmdir()  # 仅在目录为空时删除
        except OSError:
            pass  # 目录非空，忽略
        print(f"Successfully deleted Slash Command '{command_name}' from {command_path}")
        return True
    except Exception as e:
        print(f"Error: Could not delete Slash Command: {e}")
        return False

def validate_command(command_name, scope='project', project_path=None):
    """验证 Slash Command 的配置"""
    command_path = None
    project_dir = Path(project_path) if project_path else Path.cwd()
    
    if scope in ['project', 'all']:
        project_command_file = project_dir / '.claude' / 'commands'
        parts = Path(command_name).parts
        file_name = parts[-1] + '.md'
        namespace_dirs = parts[:-1]
        full_project_path = project_command_file.joinpath(*namespace_dirs, file_name)
        if full_project_path.exists():
            command_path = full_project_path
            
    if command_path is None and scope in ['personal', 'all']:
        personal_command_file = USER_COMMANDS_DIR
        parts = Path(command_name).parts
        file_name = parts[-1] + '.md'
        namespace_dirs = parts[:-1]
        full_personal_path = personal_command_file.joinpath(*namespace_dirs, file_name)
        if full_personal_path.exists():
            command_path = full_personal_path
            
    if command_path is None:
        print(f"Error: Slash Command '{command_name}' not found.")
        return False
        
    try:
        with open(command_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. 检查可选的 YAML frontmatter
        description = "No description"
        argument_hint = ""
        if content.startswith('---'):
            end = content.find('---', 3)
            if end == -1:
                print(f"Error: Could not find closing '---' in {command_path}")
                return False
                
            frontmatter_str = content[3:end]
            frontmatter = yaml.safe_load(frontmatter_str)
            
            # 检查可选字段
            if 'description' in frontmatter:
                description = frontmatter['description']
            if 'argument-hint' in frontmatter:
                argument_hint = frontmatter['argument-hint']
                
        print(f"Slash Command '{command_name}' at {command_path} is valid.")
        return True
        
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in {command_path}: {e}")
        return False
    except Exception as e:
        print(f"Error: Could not validate Slash Command: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Manage Claude Code Slash Commands')
    parser.add_argument('action', choices=['list', 'install', 'edit', 'delete', 'validate'], help='Action to perform')
    parser.add_argument('command_name', nargs='?', help='Name of the command (can include namespace, e.g., db/migrate)')
    parser.add_argument('--scope', choices=['personal', 'project', 'all'], default='project', help='Scope of the command')
    parser.add_argument('--path', help='Path to the project directory')
    parser.add_argument('--template', help='Path to a template directory for new commands (deprecated)')
    parser.add_argument('--dry-run', action='store_true', help='Preview installation without making changes')
    parser.add_argument('--non-interactive', action='store_true', help='Non-interactive mode (skip conflicts automatically)')

    args = parser.parse_args()
    
    if args.action == 'list':
        commands = get_commands(scope=args.scope, project_path=args.path)
        if not commands:
            print("No slash commands found.")
        else:
            print(f"Found {len(commands)} slash command(s):")
            # 按命名空间分组显示
            namespaces = {}
            for name, info in commands.items():
                ns = info['namespace']
                if ns not in namespaces:
                    namespaces[ns] = []
                namespaces[ns].append((name, info))
                
            for ns in sorted(namespaces.keys()):
                prefix = f" ({ns})" if ns else ""
                print(f"  Namespace: {ns if ns else 'root'}")
                for name, info in sorted(namespaces[ns]):
                    print(f"    /{name}: {info['description']} ({info['scope']})")
                    if info['argument_hint']:
                        print(f"      Hint: {info['argument_hint']}")
                        
    elif args.action == 'install':
        if not args.command_name:
            print("Error: command_name is required for install action")
            sys.exit(1)
        success = install_command(
            args.command_name,
            scope=args.scope,
            project_path=args.path,
            template_dir=args.template,
            dry_run=args.dry_run,
            interactive=not args.non_interactive
        )
        sys.exit(0 if success else 1)
        
    elif args.action == 'edit':
        if not args.command_name:
            print("Error: command_name is required for edit action")
            sys.exit(1)
        edit_command(args.command_name, scope=args.scope, project_path=args.path)
        
    elif args.action == 'delete':
        if not args.command_name:
            print("Error: command_name is required for delete action")
            sys.exit(1)
        delete_command(args.command_name, scope=args.scope, project_path=args.path)
        
    elif args.action == 'validate':
        if not args.command_name:
            print("Error: command_name is required for validate action")
            sys.exit(1)
        validate_command(args.command_name, scope=args.scope, project_path=args.path)

if __name__ == '__main__':
    main()