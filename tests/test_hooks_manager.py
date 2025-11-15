import pytest
import sys
import os
import tempfile
import json
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from hooks_manager import (
    load_user_hooks,
    load_plugin_hooks,
    load_project_hooks,
    load_all_hooks,
    validate_matcher,
    validate_hook_command,
    get_hook_event_names
)


def test_load_user_hooks():
    """测试加载用户级的hooks"""
    # 创建一个临时的用户设置文件
    temp_dir = tempfile.mkdtemp()
    user_settings_path = Path(temp_dir) / '.claude' / 'settings.json'
    user_settings_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入一些测试数据
    test_data = {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "Edit:*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "pnpm type:check"
                        }
                    ]
                }
            ]
        }
    }
    
    with open(user_settings_path, 'w') as f:
        json.dump(test_data, f)
    
    # 临时修改DEFAULT_USER_SETTINGS
    from hooks_manager import DEFAULT_USER_SETTINGS as original_default_user_settings
    from hooks_manager import load_settings
    
    import hooks_manager
    hooks_manager.DEFAULT_USER_SETTINGS = user_settings_path
    
    # 测试加载用户级的hooks
    user_hooks = load_user_hooks()
    
    # 恢复原来的DEFAULT_USER_SETTINGS
    hooks_manager.DEFAULT_USER_SETTINGS = original_default_user_settings
    
    # 检查结果
    assert "PostToolUse" in user_hooks
    assert len(user_hooks["PostToolUse"]) == 1
    assert user_hooks["PostToolUse"][0]["matcher"] == "Edit:*"
    assert user_hooks["PostToolUse"][0]["hooks"][0]["command"] == "pnpm type:check"
    
    # 清理临时目录
    import shutil
    shutil.rmtree(temp_dir)


def test_validate_matcher():
    """测试验证 matcher 模式"""
    # 测试有效的正则表达式
    assert validate_matcher("Edit:*") == True
    assert validate_matcher("Write|Edit") == True
    
    # 测试无效的正则表达式
    assert validate_matcher("*") == True  # * 是有效的正则表达式？
    assert validate_matcher("(") == False  # 未闭合的括号


def test_validate_hook_command():
    """测试验证 Hook 命令是否安全"""
    # 测试安全命令
    assert validate_hook_command("pnpm type:check") == True
    assert validate_hook_command("echo 'test'") == True
    
    # 测试危险命令
    assert validate_hook_command("rm -rf /") == False
    assert validate_hook_command("shutdown") == False


def test_get_hook_event_names():
    """测试获取所有支持的 Hook 事件名称"""
    event_names = get_hook_event_names()
    
    assert "PreToolUse" in event_names
    assert "PostToolUse" in event_names
    assert "UserPromptSubmit" in event_names
    assert "Stop" in event_names
    assert len(event_names) >= 9  # 至少有9个事件
