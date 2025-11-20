#!/usr/bin/env python3
"""
Unified manager for Claude Code components: skills, subagents, hooks, commands, plugins, mcps
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

# 定义组件类型与对应脚本的映射
COMPONENT_TYPES = {
    'skills': 'skills_manager.py',
    'subagents': 'subagents_manager.py',
    'hooks': 'hooks_manager.py',
    'commands': 'commands_manager.py',
    'plugins': 'plugins_manager.py',
    'mcps': 'mcps_manager.py'
}


def create_arg_parser():
    """创建命令行解析器"""
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
    
    return parser, subparsers


def add_component_parsers(subparsers):
    """为每种组件类型创建子命令解析器"""
    for comp_type, script_name in COMPONENT_TYPES.items():
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


def parse_args(parser):
    """解析命令行参数"""
    # 也支持旧的 --type 参数格式
    parser.add_argument('--type', choices=['skills', 'subagents', 'hooks', 'commands', 'plugins', 'mcps'],
                       help='Type of Claude Code component to manage (alternative to subcommands)')
    
    # 解析已知参数，以便将剩余参数传递给子脚本
    args, unknown_args = parser.parse_known_args()
    
    return args, unknown_args


def construct_script_args(args):
    """构造传递给子脚本的参数"""
    script_args = []
    
    # 添加动作
    if hasattr(args, 'action') and args.action:
        script_args.append(args.action)
    
    # 添加名称
    if hasattr(args, 'name') and args.name:
        script_args.append(args.name)
    
    # 添加通用选项
    if hasattr(args, 'scope') and args.scope:
        script_args.extend(['--scope', args.scope])
    
    if hasattr(args, 'path') and args.path:
        script_args.extend(['--path', args.path])
    
    if hasattr(args, 'template') and args.template:
        script_args.extend(['--template', args.template])
    
    # 添加 hooks 特定选项
    if hasattr(args, 'event') and args.event:
        script_args.extend(['--event', args.event])
    
    if hasattr(args, 'matcher') and args.matcher:
        script_args.extend(['--matcher', args.matcher])
    
    if hasattr(args, 'command') and args.command:
        script_args.extend(['--command', args.command])
    
    if hasattr(args, 'timeout') and args.timeout is not None:
        script_args.extend(['--timeout', str(args.timeout)])
    
    if hasattr(args, 'index') and args.index is not None:
        script_args.extend(['--index', str(args.index)])
    
    if hasattr(args, 'settings_path') and args.settings_path:
        script_args.extend(['--settings-path', args.settings_path])
    
    # 添加 plugins 特定选项
    if hasattr(args, 'source') and args.source:
        script_args.extend(['--source', args.source])
    
    if hasattr(args, 'marketplace') and args.marketplace:
        script_args.extend(['--marketplace', args.marketplace])
    
    if hasattr(args, 'url') and args.url:
        script_args.extend(['--url', args.url])
    
    # 添加 mcps 特定选项
    if hasattr(args, 'transport') and args.transport:
        script_args.extend(['--transport', args.transport])
    
    if hasattr(args, 'uri') and args.uri:
        script_args.extend(['--uri', args.uri])
    
    if hasattr(args, 'description') and args.description:
        script_args.extend(['--description', args.description])
    
    if hasattr(args, 'env_vars') and args.env_vars:
        script_args.extend(['--env-vars', args.env_vars])
    
    if hasattr(args, 'config_path') and args.config_path:
        script_args.extend(['--config-path', args.config_path])
    
    return script_args


def execute_script(component_type, script_args, unknown_args):
    """执行子脚本"""
    # 导入BaseManager并调用静态方法
    from base_manager import BaseManager
    return BaseManager.execute_script_static(component_type, script_args, unknown_args)


def main():
    """主函数"""
    # 创建命令行解析器
    parser, subparsers = create_arg_parser()
    
    # 为每种组件类型创建子命令解析器
    add_component_parsers(subparsers)
    
    # 解析命令行参数
    args, unknown_args = parse_args(parser)
    
    # 确定组件类型
    component_type = args.component_type
    if not component_type and args.type:
        component_type = args.type
    
    if not component_type:
        parser.print_help()
        return 1
    
    if component_type not in COMPONENT_TYPES:
        print(f"Error: Unknown component type '{component_type}'")
        return 1
    
    # 构造传递给子脚本的参数
    script_args = construct_script_args(args)
    
    # 执行子脚本
    return execute_script(component_type, script_args, unknown_args)


if __name__ == '__main__':
    sys.exit(main())
