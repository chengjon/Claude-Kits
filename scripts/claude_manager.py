#!/usr/bin/env python3
"""
Claude Code 组件统一管理脚本 (增强版)

此脚本提供了一个统一的入口来管理 Claude Code 的所有自定义组件：
1. Agent Skills
2. Subagents
3. Hooks
4. Slash Commands
5. Plugins
6. MCP Servers

使用方法：
python claude_manager.py [skills|subagents|hooks|commands|plugins|mcps] [action] [name] [...options]
或者
python claude_manager.py --type [component_type] [action] [name] [...options]
"""

import argparse
import sys
import subprocess
import os
from pathlib import Path

# 获取当前脚本所在目录，用于定位各个管理脚本
SCRIPT_DIR = Path(__file__).parent.resolve()

def run_manager_script(script_name, args):
    """运行指定的管理脚本"""
    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        print(f"Error: Management script {script_name} not found at {script_path}")
        return False
        
    # 构造完整的命令
    cmd = [sys.executable, str(script_path)] + args
    
    try:
        # 使用 subprocess.run 运行命令并捕获输出
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: Failed to run {script_name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Unified manager for Claude Code components: skills, subagents, hooks, commands, plugins, mcps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  claude_manager.py skills list --scope all
  claude_manager.py subagents install my-debugger --scope personal
  claude_manager.py hooks add PreToolUse --matcher "Bash" --command "echo 'Bash command executed'"
  claude_manager.py commands edit db/migrate --scope project
  claude_manager.py plugins list
  claude_manager.py mcps add my-server --transport http --uri http://localhost:8000
        """
    )
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(
        dest='component_type', 
        help='Type of Claude Code component to manage',
        metavar='{skills,subagents,hooks,commands,plugins,mcps}'
    )
    
    # 为每种组件类型创建通用的子命令解析器
    component_types = {
        'skills': 'skills_manager.py',
        'subagents': 'subagents_manager.py',
        'hooks': 'hooks_manager.py',
        'commands': 'commands_manager.py',
        'plugins': 'plugins_manager.py',
        'mcps': 'mcps_manager.py'
    }
    
    for comp_type, script_name in component_types.items():
        comp_parser = subparsers.add_parser(comp_type, help=f'Manage {comp_type}')
        
        # 添加动作参数 (对 plugins 和 mcps 稍作调整)
        if comp_type == 'plugins':
            comp_parser.add_argument(
                'action', 
                choices=['list', 'install', 'uninstall', 'marketplace', 'validate'],
                help='Action to perform'
            )
        elif comp_type == 'mcps':
            comp_parser.add_argument(
                'action', 
                choices=['list', 'add', 'edit', 'delete', 'validate'],
                help='Action to perform'
            )
        else:
            comp_parser.add_argument(
                'action', 
                choices=['list', 'install', 'edit', 'delete', 'validate', 'add'],
                help='Action to perform'
            )
        
        # 添加名称参数（对 list 为可选）
        comp_parser.add_argument(
            'name', 
            nargs='?',
            help='Name of the component (not required for list action)'
        )
        
        # 添加通用选项
        comp_parser.add_argument('--scope', choices=['personal', 'project', 'all', 'user', 'local'], 
                                default='project', help='Scope of the component')
        comp_parser.add_argument('--path', help='Path to the project directory')
        comp_parser.add_argument('--template', help='Path to a template directory for new components')
        
        # 为 hooks 添加特定选项
        if comp_type == 'hooks':
            comp_parser.add_argument('--event', help='Hook event (e.g., PreToolUse, PostToolUse)')
            comp_parser.add_argument('--matcher', help='Tool matcher pattern')
            comp_parser.add_argument('--command', help='Hook command to execute')
            comp_parser.add_argument('--timeout', type=int, help='Hook timeout in seconds')
            comp_parser.add_argument('--index', type=int, help='Index of the hook to edit/delete')
            comp_parser.add_argument('--settings-path', help='Path to the settings.json file')
        
        # 为 plugins 添加特定选项
        if comp_type == 'plugins':
            comp_parser.add_argument('--source', help='Source path or URL for installing plugins')
            comp_parser.add_argument('--marketplace', help='Marketplace name or URL to install from')
            comp_parser.add_argument('--url', help='URL for adding marketplaces')
            
        # 为 mcps 添加特定选项
        if comp_type == 'mcps':
            comp_parser.add_argument('--transport', choices=['stdio', 'http', 'sse'], 
                                   help='Transport type for the server')
            comp_parser.add_argument('--uri', help='URI for the server')
            comp_parser.add_argument('--description', help='Description of the server')
            comp_parser.add_argument('--env-vars', 
                                   help='Environment variables as KEY1=VALUE1,KEY2=VALUE2')
            comp_parser.add_argument('--config-path', help='Path to the MCP configuration file')
            
    # 也支持旧的 --type 参数格式
    parser.add_argument('--type', choices=['skills', 'subagents', 'hooks', 'commands', 'plugins', 'mcps'],
                       help='Type of Claude Code component to manage (alternative to subcommands)')
    
    # 解析已知参数，以便将剩余参数传递给子脚本
    args, unknown_args = parser.parse_known_args()
    
    # 确定组件类型
    component_type = args.component_type
    if not component_type and args.type:
        component_type = args.type
        
    if not component_type:
        parser.print_help()
        return 1
        
    if component_type not in component_types:
        print(f"Error: Unknown component type '{component_type}'")
        return 1
        
    # 构造传递给子脚本的参数
    script_args = []
    
    # 添加动作
    if hasattr(args, 'action') and args.action:
        script_args.append(args.action)
        
    # 添加名称
    if hasattr(args, 'name') and args.name:
        script_args.append(args.name)
        
    # 添加所有已知参数
    for arg, value in vars(args).items():
        # 跳过我们已经处理过的参数
        if arg in ['component_type', 'type', 'name', 'action']:
            continue
        # 跳过为特定组件类型添加但不适用于当前组件的参数
        if component_type not in ['hooks', 'plugins', 'mcps']:
            if arg in ['event', 'matcher', 'command', 'timeout', 'index', 'settings_path', 
                      'source', 'marketplace', 'url', 'transport', 'uri', 'description', 
                      'env_vars', 'config_path']:
                continue
        elif component_type != 'hooks':
            if arg in ['event', 'matcher', 'command', 'timeout', 'index', 'settings_path']:
                continue
        elif component_type != 'plugins':
            if arg in ['source', 'marketplace', 'url']:
                continue
        elif component_type != 'mcps':
            if arg in ['transport', 'uri', 'description', 'env_vars', 'config_path']:
                continue
                
        if value is not None:
            if isinstance(value, bool):
                if value:
                    script_args.append(f"--{arg.replace('_', '-')}")
            else:
                script_args.extend([f"--{arg.replace('_', '-')}", str(value)])
                
    # 添加未知参数（通常是布尔标志）
    script_args.extend(unknown_args)
    
    # 运行相应的管理脚本
    script_name = component_types[component_type]
    success = run_manager_script(script_name, script_args)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())