import pytest
import sys
import os

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from skills_manager import get_skills
from commands_manager import get_commands
from subagents_manager import get_subagents


def test_get_skills():
    # 测试获取技能列表
    skills = get_skills(scope='user')
    assert isinstance(skills, dict)


def test_get_commands():
    # 测试获取命令列表
    commands = get_commands(scope='user')
    assert isinstance(commands, dict)


def test_get_subagents():
    # 测试获取子代理列表
    subagents = get_subagents(scope='user')
    assert isinstance(subagents, dict)
