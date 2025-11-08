#!/usr/bin/env python3
"""
Plugins 管理脚本

功能：
1. 浏览已安装的插件和可用的市场
2. 安装/卸载插件
3. 管理插件市场（添加/删除）
4. 验证插件配置

注意：此脚本主要通过调用 Claude Code 的 CLI 命令 (`claude`) 来管理插件，
因为它涉及到与 Claude Code 进程的交互和复杂的配置。

使用方法：
python plugins_manager.py [list|install|uninstall|marketplace] [plugin_name] [...options]
"""

import argparse
import subprocess
import sys
import json
import os
from pathlib import Path

def run_claude_command(args):
    """运行 Claude Code CLI 命令"""
    try:
        # 尝试直接运行 'claude' 命令
        cmd = ['claude'] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Error: Command timed out"
    except FileNotFoundError:
        # 如果 'claude' 不在 PATH 中，尝试使用完整路径或其他方式
        # 这里可以添加更复杂的查找逻辑
        return -1, "", "Error: 'claude' command not found. Please ensure Claude Code is installed and in your PATH."
    except Exception as e:
        return -1, "", f"Error: Failed to run command: {e}"

def list_plugins():
    """列出已安装的插件"""
    # Claude Code 没有直接列出插件的 CLI 命令
    # 我们可以通过检查插件目录来实现
    plugin_dirs = [
        Path.home() / '.claude' / 'plugins',  # 用户级插件
        Path('.claude') / 'plugins'           # 项目级插件
    ]
    
    plugins = []
    for plugin_dir in plugin_dirs:
        if plugin_dir.exists():
            for plugin in plugin_dir.iterdir():
                if plugin.is_dir():
                    plugin_json = plugin / '.claude-plugin' / 'plugin.json'
                    if plugin_json.exists():
                        try:
                            with open(plugin_json, 'r') as f:
                                plugin_info = json.load(f)
                                plugins.append({
                                    'name': plugin_info.get('name', plugin.name),
                                    'version': plugin_info.get('version', 'Unknown'),
                                    'description': plugin_info.get('description', 'No description'),
                                    'path': str(plugin),
                                    'scope': 'user' if 'home' in str(plugin) else 'project'
                                })
                        except Exception as e:
                            print(f"Warning: Could not read plugin info from {plugin_json}: {e}")
    
    if not plugins:
        print("No plugins found.")
    else:
        print(f"Found {len(plugins)} plugin(s):")
        for plugin in plugins:
            print(f"  - {plugin['name']} (v{plugin['version']}): {plugin['description']} [{plugin['scope']}]")
            
    return True

def install_plugin(plugin_source, marketplace=None):
    """安装插件"""
    if marketplace:
        # 从市场安装
        # 注意：Claude Code CLI 没有直接的 "install from marketplace" 命令
        # 通常是通过 /plugin 命令在 REPL 中交互式完成
        # 这里我们提供一个模拟的实现
        print(f"Installing plugin '{plugin_source}' from marketplace '{marketplace}'")
        print("Note: This operation usually requires interactive mode. Please use '/plugin install' in Claude Code REPL.")
        return False
    else:
        # 从本地路径或 URL 安装
        print(f"Installing plugin from: {plugin_source}")
        # Claude Code CLI 也没有直接的非交互式安装命令
        # 最接近的是 `claude plugin` 然后在 REPL 中操作
        print("Note: Plugin installation typically requires interactive mode.")
        print("You can:")
        print("1. Start Claude Code: `claude`")
        print("2. Run the command: `/plugin install`")
        print("3. Follow the prompts to install from local path or URL")
        return False

def uninstall_plugin(plugin_name):
    """卸载插件"""
    # Claude Code CLI 没有直接的卸载命令
    # 通常需要手动删除插件目录
    plugin_dirs = [
        Path.home() / '.claude' / 'plugins',  # 用户级插件
        Path('.claude') / 'plugins'           # 项目级插件
    ]
    
    removed = False
    for plugin_dir in plugin_dirs:
        plugin_path = plugin_dir / plugin_name
        if plugin_path.exists():
            try:
                import shutil
                shutil.rmtree(plugin_path)
                print(f"Successfully uninstalled plugin '{plugin_name}' from {plugin_path}")
                removed = True
            except Exception as e:
                print(f"Error: Could not remove {plugin_path}: {e}")
                
    if not removed:
        print(f"Plugin '{plugin_name}' not found.")
        return False
    return True

def list_marketplaces():
    """列出已配置的插件市场"""
    # 插件市场信息通常存储在配置文件中
    marketplace_files = [
        Path.home() / '.claude' / 'marketplaces.json',  # 用户级市场
        Path('.claude') / 'marketplaces.json'           # 项目级市场
    ]
    
    marketplaces = []
    for mp_file in marketplace_files:
        if mp_file.exists():
            try:
                with open(mp_file, 'r') as f:
                    data = json.load(f)
                    if 'marketplaces' in data:
                        for mp in data['marketplaces']:
                            marketplaces.append({
                                'name': mp.get('name', 'Unknown'),
                                'url': mp.get('url', 'No URL'),
                                'path': str(mp_file),
                                'scope': 'user' if 'home' in str(mp_file) else 'project'
                            })
                    # 也支持旧格式或简单列表
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                marketplaces.append({
                                    'name': item.get('name', 'Unknown'),
                                    'url': item.get('url', item.get('source', 'No URL')),
                                    'path': str(mp_file),
                                    'scope': 'user' if 'home' in str(mp_file) else 'project'
                                })
            except Exception as e:
                print(f"Warning: Could not read marketplaces from {mp_file}: {e}")
    
    if not marketplaces:
        print("No marketplaces configured.")
    else:
        print(f"Found {len(marketplaces)} marketplace(s):")
        for mp in marketplaces:
            print(f"  - {mp['name']}: {mp['url']} [{mp['scope']}]")
    return True

def add_marketplace(name, url_or_path):
    """添加插件市场"""
    # 这通常涉及修改配置文件
    user_mp_file = Path.home() / '.claude' / 'marketplaces.json'
    project_mp_file = Path('.claude') / 'marketplaces.json'
    
    # 确定要使用的配置文件
    mp_file = user_mp_file  # 默认使用用户级
    
    # 如果当前目录有 .claude 目录，则使用项目级
    if Path('.claude').exists():
        mp_file = project_mp_file
        
    # 确保目录存在
    mp_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 读取现有配置
    marketplaces = []
    if mp_file.exists():
        try:
            with open(mp_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'marketplaces' in data:
                    marketplaces = data['marketplaces']
                elif isinstance(data, list):
                    marketplaces = data
        except Exception as e:
            print(f"Warning: Could not read existing marketplaces: {e}")
    
    # 检查是否已存在
    for mp in marketplaces:
        if mp.get('name') == name:
            print(f"Marketplace '{name}' already exists.")
            return False
    
    # 添加新市场
    new_marketplace = {
        'name': name,
        'url': url_or_path
    }
    marketplaces.append(new_marketplace)
    
    # 保存配置
    try:
        with open(mp_file, 'w') as f:
            json.dump({'marketplaces': marketplaces}, f, indent=2)
        print(f"Successfully added marketplace '{name}' to {mp_file}")
        return True
    except Exception as e:
        print(f"Error: Could not save marketplace configuration: {e}")
        return False

def remove_marketplace(name):
    """删除插件市场"""
    user_mp_file = Path.home() / '.claude' / 'marketplaces.json'
    project_mp_file = Path('.claude') / 'marketplaces.json'
    
    removed = False
    for mp_file in [user_mp_file, project_mp_file]:
        if mp_file.exists():
            try:
                with open(mp_file, 'r') as f:
                    data = json.load(f)
                    marketplaces = []
                    if isinstance(data, dict) and 'marketplaces' in data:
                        marketplaces = data['marketplaces']
                    elif isinstance(data, list):
                        marketplaces = data
                
                # 过滤掉要删除的市场
                original_count = len(marketplaces)
                marketplaces = [mp for mp in marketplaces if mp.get('name') != name]
                
                if len(marketplaces) < original_count:
                    # 保存更新后的配置
                    with open(mp_file, 'w') as f:
                        json.dump({'marketplaces': marketplaces}, f, indent=2)
                    print(f"Successfully removed marketplace '{name}' from {mp_file}")
                    removed = True
                    
            except Exception as e:
                print(f"Warning: Could not process {mp_file}: {e}")
    
    if not removed:
        print(f"Marketplace '{name}' not found.")
        return False
    return True

def validate_plugin(plugin_path):
    """验证插件目录结构和配置文件"""
    plugin_dir = Path(plugin_path)
    if not plugin_dir.exists():
        print(f"Error: Plugin path '{plugin_path}' does not exist.")
        return False
        
    if not plugin_dir.is_dir():
        print(f"Error: Plugin path '{plugin_path}' is not a directory.")
        return False
    
    # 检查 .claude-plugin 目录
    plugin_config_dir = plugin_dir / '.claude-plugin'
    if not plugin_config_dir.exists():
        print(f"Error: Missing '.claude-plugin' directory in {plugin_dir}")
        return False
        
    if not plugin_config_dir.is_dir():
        print(f"Error: '.claude-plugin' in {plugin_dir} is not a directory.")
        return False
    
    # 检查 plugin.json
    plugin_json = plugin_config_dir / 'plugin.json'
    if not plugin_json.exists():
        print(f"Error: Missing 'plugin.json' in {plugin_config_dir}")
        return False
        
    try:
        with open(plugin_json, 'r') as f:
            plugin_info = json.load(f)
            
        # 检查必需字段
        required_fields = ['name', 'version', 'description']
        for field in required_fields:
            if field not in plugin_info:
                print(f"Error: Missing required field '{field}' in plugin.json")
                return False
                
        print(f"Plugin at {plugin_path} is valid.")
        return True
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {plugin_json}: {e}")
        return False
    except Exception as e:
        print(f"Error: Could not validate plugin: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Manage Claude Code Plugins')
    parser.add_argument('action', choices=['list', 'install', 'uninstall', 'marketplace', 'validate'], 
                       help='Action to perform')
    
    # 通用参数
    parser.add_argument('name', nargs='?', help='Name or path of the plugin/marketplace')
    parser.add_argument('--source', help='Source path or URL for installing plugins')
    parser.add_argument('--marketplace', help='Marketplace name or URL to install from')
    parser.add_argument('--url', help='URL for adding marketplaces')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_plugins()
        
    elif args.action == 'install':
        if not args.name and not args.source:
            print("Error: name or --source is required for install action")
            sys.exit(1)
        source = args.source or args.name
        install_plugin(source, marketplace=args.marketplace)
        
    elif args.action == 'uninstall':
        if not args.name:
            print("Error: name is required for uninstall action")
            sys.exit(1)
        uninstall_plugin(args.name)
        
    elif args.action == 'marketplace':
        if args.name:
            # 如果提供了名称，可能是 list, add, remove 子操作
            # 为简化，我们假设没有子命令，直接列出市场
            list_marketplaces()
        else:
            list_marketplaces()
            
    elif args.action == 'validate':
        if not args.name:
            print("Error: name (plugin path) is required for validate action")
            sys.exit(1)
        validate_plugin(args.name)

if __name__ == '__main__':
    main()