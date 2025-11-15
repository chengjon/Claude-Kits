import pytest
import sys
import os

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from claude_manager import (
    create_arg_parser,
    add_component_parsers,
    parse_args,
    construct_script_args,
    execute_script
)


def test_create_arg_parser():
    """测试创建命令行解析器"""
    parser, subparsers = create_arg_parser()
    assert parser is not None
    assert subparsers is not None


def test_parse_args():
    """测试解析命令行参数"""
    parser, subparsers = create_arg_parser()
    add_component_parsers(subparsers)
    
    # 测试解析skills list命令
    sys.argv = ['claude_manager.py', 'skills', 'list', '--scope', 'all']
    args, unknown_args = parse_args(parser)
    
    assert args.component_type == 'skills'
    assert args.action == 'list'
    assert args.scope == 'all'
    assert unknown_args == []


def test_construct_script_args():
    """测试构造传递给子脚本的参数"""
    # 创建一个模拟的args对象
    class MockArgs:
        def __init__(self):
            self.component_type = 'skills'
            self.action = 'list'
            self.scope = 'all'
            self.name = None
            self.path = None
            self.template = None
            self.event = None
            self.matcher = None
            self.command = None
            self.timeout = None
            self.index = None
            self.settings_path = None
            self.source = None
            self.marketplace = None
            self.url = None
            self.transport = None
            self.uri = None
            self.description = None
            self.env_vars = None
            self.config_path = None
    
    args = MockArgs()
    script_args = construct_script_args(args)
    
    assert script_args == ['list', '--scope', 'all']


def test_execute_script():
    """测试执行子脚本"""
    # 测试执行一个简单的脚本命令
    component_type = 'skills'
    script_args = ['list', '--scope', 'user']
    
    # 这只是一个简单的测试，实际执行可能需要更复杂的测试环境
    result = execute_script(component_type, script_args, [])
    assert isinstance(result, int)
