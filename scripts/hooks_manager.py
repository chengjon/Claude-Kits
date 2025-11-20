#!/usr/bin/env python3
"""
Hooks Manager for Claude Code
"""

import os
import sys
import argparse
import yaml
import json
import re
import subprocess
from pathlib import Path

# 默认路径配置
DEFAULT_USER_SETTINGS = Path.home() / '.claude' / 'settings.json'
DEFAULT_PROJECT_SETTINGS = Path('.claude') / 'settings.json'
DEFAULT_LOCAL_SETTINGS = Path('.claude') / 'settings.local.json'


def load_settings(settings_file):
    """加载配置文件（JSON格式）"""
    if not settings_file.exists():
        return None
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {settings_file}")
        return None
    except Exception as e:
        print(f"Error loading settings from {settings_file}: {e}")
        return None


def get_settings_file(settings_path=None, scope='project'):
    """根据scope获取配置文件路径"""
    if settings_path:
        return Path(settings_path)
    
    if scope == 'user':
        return DEFAULT_USER_SETTINGS
    elif scope == 'project' or scope == 'local':
        return DEFAULT_PROJECT_SETTINGS if scope == 'project' else DEFAULT_LOCAL_SETTINGS
    return DEFAULT_PROJECT_SETTINGS


def load_user_hooks():
    """加载用户级的hooks"""
    hooks_with_scope = {}
    
    # 加载用户级配置
    settings = load_settings(DEFAULT_USER_SETTINGS)
    if settings and 'hooks' in settings:
        for event, hook_list in settings['hooks'].items():
            hooks_with_scope[event] = []
            for hook_config in hook_list:
                hook_config_with_scope = hook_config.copy()
                hook_config_with_scope['scope'] = 'user'
                hook_config_with_scope['settings_file'] = str(DEFAULT_USER_SETTINGS)
                hooks_with_scope[event].append(hook_config_with_scope)
    
    return hooks_with_scope


def load_plugin_hooks():
    """加载插件级的hooks"""
    all_plugin_hooks = {}
    
    # 遍历所有插件目录
    plugins_dir = Path.home() / '.claude' / 'plugins'
    if plugins_dir.exists():
        for plugin_dir in plugins_dir.iterdir():
            if plugin_dir.is_dir():
                plugin_hooks_file = plugin_dir / 'hooks' / 'hooks.json'
                if plugin_hooks_file.exists():
                    plugin_settings = load_settings(plugin_hooks_file)
                    if plugin_settings and 'hooks' in plugin_settings:
                        for event, hook_list in plugin_settings['hooks'].items():
                            if event not in all_plugin_hooks:
                                all_plugin_hooks[event] = []
                            
                            for hook_config in hook_list:
                                hook_config_with_scope = hook_config.copy()
                                hook_config_with_scope['scope'] = f'plugin:{plugin_dir.name}'
                                hook_config_with_scope['settings_file'] = str(plugin_hooks_file)
                                all_plugin_hooks[event].append(hook_config_with_scope)
    
    return all_plugin_hooks


def load_project_hooks(settings_path=None):
    """加载项目级的hooks"""
    hooks_with_scope = {}
    
    # 先加载 settings.json
    if settings_path:
        settings_file = Path(settings_path)
    else:
        settings_file = DEFAULT_PROJECT_SETTINGS
    
    settings = load_settings(settings_file)
    if settings and 'hooks' in settings:
        for event, hook_list in settings['hooks'].items():
            hooks_with_scope[event] = []
            for hook_config in hook_list:
                hook_config_with_scope = hook_config.copy()
                hook_config_with_scope['scope'] = 'project'
                hook_config_with_scope['settings_file'] = str(settings_file)
                hooks_with_scope[event].append(hook_config_with_scope)
    
    # 再加载 settings.local.json (如果不是自定义路径)
    if not settings_path:
        local_settings = load_settings(DEFAULT_LOCAL_SETTINGS)
        if local_settings and 'hooks' in local_settings:
            for event, hook_list in local_settings['hooks'].items():
                if event not in hooks_with_scope:
                    hooks_with_scope[event] = []
                
                for hook_config in hook_list:
                    hook_config_with_scope = hook_config.copy()
                    hook_config_with_scope['scope'] = 'project:local'
                    hook_config_with_scope['settings_file'] = str(DEFAULT_LOCAL_SETTINGS)
                    hooks_with_scope[event].append(hook_config_with_scope)
    
    return hooks_with_scope


def load_all_hooks():
    """加载所有范围内的hooks"""
    # 按优先级顺序加载所有设置（从低到高）
    all_hooks = {}
    
    # 1. 用户级 (最低优先级)
    user_hooks = load_user_hooks()
    for event, hook_list in user_hooks.items():
        if event not in all_hooks:
            all_hooks[event] = []
        all_hooks[event].extend(hook_list)
    
    # 2. 插件级 (中等优先级)
    plugin_hooks = load_plugin_hooks()
    for event, hook_list in plugin_hooks.items():
        if event not in all_hooks:
            all_hooks[event] = []
        all_hooks[event].extend(hook_list)
    
    # 3. 项目级 (最高优先级)
    project_hooks = load_project_hooks()
    for event, hook_list in project_hooks.items():
        if event not in all_hooks:
            all_hooks[event] = []
        all_hooks[event].extend(hook_list)
    
    return all_hooks


def get_hooks(settings_path=None, scope='project'):
    """获取指定范围内的所有 Hooks 配置
    优先级顺序：项目级 > 插件级 > 用户级
    注意：项目级自动包含 settings.json 和 settings.local.json
    """
    if scope == 'all':
        return load_all_hooks()
    elif scope == 'plugin':
        return load_plugin_hooks()
    elif scope == 'project':
        return load_project_hooks(settings_path)
    elif scope == 'user':
        return load_user_hooks()
    else:
        # 默认加载用户级
        return load_user_hooks()


def add_hook(event, matcher, hook_command, settings_path=None, scope='project', timeout=None):
    """
    添加一个新的 Hook 配置（包含安全检查）
    参数:
        event: Hook 事件名称
        matcher: 工具匹配模式（可选）
        hook_command: 要执行的命令
        settings_path: settings.json 路径（可选）
        scope: 作用域 ('user', 'project', 'local')
        timeout: 超时时间（秒，可选）
    """
    # 基本安全检查
    if 'rm -rf' in hook_command:
        print("Error: Invalid command - 'rm -rf' is not allowed for security reasons")
        return False
    
    # 获取配置文件路径
    if settings_path:
        settings_file = Path(settings_path)
    else:
        if scope == 'local':
            settings_file = DEFAULT_LOCAL_SETTINGS
        elif scope == 'user':
            settings_file = DEFAULT_USER_SETTINGS
        else:
            settings_file = DEFAULT_PROJECT_SETTINGS
    
    # 加载现有设置
    settings = load_settings(settings_file) or {"hooks": {}}
    
    # 更新 Hooks 配置
    if event not in settings["hooks"]:
        settings["hooks"][event] = []
    
    hook_config = {
        "matcher": matcher,
        "hooks": [
            {
                "type": "command",
                "command": hook_command,
                "timeout": timeout
            }
        ]
    }
    
    settings["hooks"][event].append(hook_config)
    
    # 保存到文件
    try:
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving hook configuration: {e}")
        return False


def validate_matcher(matcher):
    """验证 matcher 模式是否有效"""
    if not matcher or matcher == "*":
        return True
    
    try:
        re.compile(matcher)
        return True
    except re.error:
        return False


def validate_hook_command(command):
    """验证 Hook 命令是否安全"""
    # 防止恶意命令执行
    dangerous_commands = ['rm -rf', 'shutdown', 'reboot', 'dd if=', 'mkfs.', 'fdisk', 'mount', 'umount', 'chmod 777']
    
    for dangerous_cmd in dangerous_commands:
        if dangerous_cmd in command:
            return False
    
    return True


def get_hook_event_names():
    """获取所有支持的 Hook 事件名称"""
    return [
        "PreToolUse",
        "PostToolUse",
        "Notification",
        "UserPromptSubmit",
        "Stop",
        "SubagentStop",
        "PreCompact",
        "SessionStart",
        "SessionEnd"
    ]


def get_current_scope():
    """确定当前工作目录对应的作用域"""
    if (Path.cwd() / ".claude" / "settings.json").exists():
        return "project"
    return "user"


# 其他函数保持不变...
