#!/usr/bin/env python3
"""
MCPS Manager for Claude Code
"""

import argparse
import sys
import os
from pathlib import Path

# Import base manager
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base_manager import BaseManager


class McpsManager(BaseManager):
    """MCPS manager"""
    
    def __init__(self):
        super().__init__('mcps', 'mcps_manager.py')
    
    def main(self):
        """主函数"""
        # 创建命令行解析器
        parser = self.create_arg_parser()
        
        # 添加动作参数（mcps有自己的特定动作）
        self.add_action_parser(parser, ['list', 'add', 'edit', 'delete', 'validate'])
        
        # 添加通用选项
        self.add_common_options(parser)
        
        # 解析命令行参数
        args = self.parse_args(parser)
        
        # 构造传递给子脚本的参数
        script_args = self.construct_script_args(args)
        
        # 执行子脚本
        return self.execute_script(script_args, [])


if __name__ == '__main__':
    sys.exit(McpsManager().main())
