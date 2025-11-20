#!/usr/bin/env python3
"""
Base Manager for Claude Code components
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path


class BaseManager:
    """所有manager的基础类
    
    提供了所有manager的通用功能，包括：
    - 创建命令行解析器
    - 添加动作参数
    - 添加通用选项
    - 解析命令行参数
    - 构造传递给子脚本的参数
    - 执行子脚本
    
    使用方法：
    class MyManager(BaseManager):
        def __init__(self):
            super().__init__('my-component', 'my_manager.py')
        
        def main(self):
            # 创建命令行解析器
            parser = self.create_arg_parser()
            
            # 添加动作参数
            self.add_action_parser(parser, ['list', 'install', 'edit', 'delete', 'validate', 'add'])
            
            # 添加通用选项
            self.add_common_options(parser)
            
            # 解析命令行参数
            args = self.parse_args(parser)
            
            # 构造传递给子脚本的参数
            script_args = self.construct_script_args(args)
            
            # 执行子脚本
            return self.execute_script(script_args, [])
    """
    
    def __init__(self, component_type, script_name):
        """初始化BaseManager
        
        参数:
            component_type: 组件类型（如'skills', 'subagents', 'hooks', 'commands', 'plugins', 'mcps'）
            script_name: 脚本名称（如'skills_manager.py'）
        """
        self.component_type = component_type
        self.script_name = script_name
        
        # 组件类型与对应脚本的映射
        self.COMPONENT_TYPES = {
            'skills': 'skills_manager.py',
            'subagents': 'subagents_manager.py',
            'hooks': 'hooks_manager.py',
            'commands': 'commands_manager.py',
            'plugins': 'plugins_manager.py',
            'mcps': 'mcps_manager.py'
        }
    
    def create_arg_parser(self):
        """创建命令行解析器
        
        返回:
            argparse.ArgumentParser: 命令行解析器对象
        """
        parser = argparse.ArgumentParser(
            description=f'Manage {self.component_type}',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        return parser
    
    def add_action_parser(self, parser, actions):
        """添加动作参数
        
        参数:
            parser: 命令行解析器对象
            actions: 动作列表（如['list', 'install', 'edit', 'delete', 'validate', 'add']）
        """
        parser.add_argument(
            'action', 
            choices=actions,
            help='Action to perform'
        )
    
    def add_common_options(self, parser):
        """添加通用选项
        
        参数:
            parser: 命令行解析器对象
        """
        parser.add_argument('--scope', choices=['personal', 'project', 'all', 'user', 'local'], 
                            default='project', help='Scope of the component')
        parser.add_argument('--path', help='Path to the project directory')
        parser.add_argument('--template', help='Path to a template directory for new components')
    
    def parse_args(self, parser):
        """解析命令行参数
        
        参数:
            parser: 命令行解析器对象
            
        返回:
            argparse.Namespace: 解析后的参数对象
        """
        return parser.parse_args()
    
    def construct_script_args(self, args):
        """构造传递给子脚本的参数
        
        参数:
            args: 解析后的参数对象
            
        返回:
            list: 传递给子脚本的参数列表
        """
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
        
        return script_args
    
    def execute_script(self, script_args, unknown_args):
        """执行子脚本
        
        参数:
            script_args: 传递给子脚本的参数列表
            unknown_args: 未知参数列表
            
        返回:
            int: 子脚本的返回码
        """
        # 获取脚本路径
        script_dir = Path(__file__).parent
        script_path = script_dir / self.script_name
        
        if not script_path.exists():
            print(f"Error: Management script '{self.script_name}' not found at '{script_path}'")
            return 1
        
        # 构造完整的命令
        cmd = [sys.executable, str(script_path)] + script_args + unknown_args
        
        try:
            result = subprocess.run(cmd, text=True)
            return result.returncode
        except Exception as e:
            print(f"Error executing script: {e}")
            return 1
    
    @staticmethod
    def execute_script_static(component_type, script_args, unknown_args):
        """静态方法：执行子脚本
        
        参数:
            component_type: 组件类型（如'skills', 'subagents', 'hooks', 'commands', 'plugins', 'mcps'）
            script_args: 传递给子脚本的参数列表
            unknown_args: 未知参数列表
            
        返回:
            int: 子脚本的返回码
        """
        # 组件类型与对应脚本的映射
        COMPONENT_TYPES = {
            'skills': 'skills_manager.py',
            'subagents': 'subagents_manager.py',
            'hooks': 'hooks_manager.py',
            'commands': 'commands_manager.py',
            'plugins': 'plugins_manager.py',
            'mcps': 'mcps_manager.py'
        }
        
        script_name = COMPONENT_TYPES.get(component_type)
        if not script_name:
            print(f"Error: Unknown component type '{component_type}'")
            return 1
        
        # 获取脚本路径
        script_dir = Path(__file__).parent
        script_path = script_dir / script_name
        
        if not script_path.exists():
            print(f"Error: Management script '{script_name}' not found at '{script_path}'")
            return 1
        
        # 构造完整的命令
        cmd = [sys.executable, str(script_path)] + script_args + unknown_args
        
        try:
            result = subprocess.run(cmd, text=True)
            return result.returncode
        except Exception as e:
            print(f"Error executing script: {e}")
            return 1
