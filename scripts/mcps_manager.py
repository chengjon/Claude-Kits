#!/usr/bin/env python3
"""
MCP Servers 管理脚本

功能：
1. 浏览已配置的 MCP 服务器
2. 添加新的 MCP 服务器配置
3. 修改现有 MCP 服务器配置
4. 删除 MCP 服务器配置
5. 验证 MCP 服务器配置

MCP (Model Context Protocol) 服务器允许 Claude Code 连接到外部工具和数据源。

使用方法：
python mcps_manager.py [list|add|edit|delete|validate] [server_name] [...options]
"""

import argparse
import json
import sys
from pathlib import Path

# 默认配置文件路径
USER_MCP_CONFIG = Path.home() / '.claude' / 'mcp.json'
PROJECT_MCP_CONFIG = Path('.claude') / 'mcp.json'

def get_mcp_config(config_path=None, scope='user'):
    """获取 MCP 配置"""
    if config_path:
        config_file = Path(config_path)
    else:
        if scope == 'user':
            config_file = USER_MCP_CONFIG
        else:  # project
            config_file = PROJECT_MCP_CONFIG
            
    if not config_file.exists():
        return {"servers": []}
        
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {config_file}: {e}")
        return None
    except Exception as e:
        print(f"Error: Could not read {config_file}: {e}")
        return None

def save_mcp_config(config, config_path=None, scope='user'):
    """保存 MCP 配置"""
    if config_path:
        config_file = Path(config_path)
    else:
        if scope == 'user':
            config_file = USER_MCP_CONFIG
        else:  # project
            config_file = PROJECT_MCP_CONFIG
            
    # 确保目录存在
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error: Could not write to {config_file}: {e}")
        return False

def list_servers(config_path=None, scope='all'):
    """列出 MCP 服务器"""
    servers = []
    
    if scope in ['all', 'user']:
        user_config = get_mcp_config(scope='user')
        if user_config and 'servers' in user_config:
            for server in user_config['servers']:
                server_copy = server.copy()
                server_copy['scope'] = 'user'
                server_copy['config_file'] = str(USER_MCP_CONFIG)
                servers.append(server_copy)
                
    if scope in ['all', 'project']:
        project_config = get_mcp_config(scope='project')
        if project_config and 'servers' in project_config:
            for server in project_config['servers']:
                server_copy = server.copy()
                server_copy['scope'] = 'project'
                server_copy['config_file'] = str(PROJECT_MCP_CONFIG)
                servers.append(server_copy)
                
    if not servers:
        print("No MCP servers configured.")
    else:
        print(f"Found {len(servers)} MCP server(s):")
        for server in servers:
            print(f"  - {server['name']}: {server.get('description', 'No description')} [{server['scope']}]")
            print(f"    Transport: {server.get('transport', 'Unknown')}")
            print(f"    URI: {server.get('uri', 'None')}")
            config_file = server.get('config_file', 'Unknown')
            print(f"    Config: {config_file}")
            if 'env' in server:
                print(f"    Environment: {', '.join(server['env'].keys())}")
            print()
            
    return True

def add_server(name, transport, uri, description=None, env_vars=None, config_path=None, scope='user'):
    """添加 MCP 服务器"""
    config = get_mcp_config(config_path, scope)
    if config is None:
        return False
        
    # 检查是否已存在同名服务器
    for server in config.get('servers', []):
        if server['name'] == name:
            print(f"Error: Server '{name}' already exists.")
            return False
    
    # 构造新服务器配置
    new_server = {
        "name": name,
        "transport": transport,
        "uri": uri
    }
    
    if description:
        new_server["description"] = description
        
    if env_vars:
        # env_vars 应该是 "KEY1=VALUE1,KEY2=VALUE2" 格式的字符串
        env_dict = {}
        for pair in env_vars.split(','):
            if '=' in pair:
                key, value = pair.split('=', 1)
                env_dict[key.strip()] = value.strip()
        if env_dict:
            new_server["env"] = env_dict
    
    if 'servers' not in config:
        config['servers'] = []
        
    config['servers'].append(new_server)
    
    if save_mcp_config(config, config_path, scope):
        print(f"Successfully added MCP server '{name}' to {scope} configuration.")
        return True
    else:
        return False

def edit_server(name, new_transport=None, new_uri=None, new_description=None, new_env_vars=None, 
                config_path=None, scope='user'):
    """修改 MCP 服务器配置"""
    config = get_mcp_config(config_path, scope)
    if config is None:
        return False
        
    server_found = False
    for server in config.get('servers', []):
        if server['name'] == name:
            server_found = True
            if new_transport:
                server['transport'] = new_transport
            if new_uri:
                server['uri'] = new_uri
            if new_description:
                server['description'] = new_description
            if new_env_vars:
                # 处理环境变量
                if new_env_vars == "":  # 清空环境变量
                    server.pop('env', None)
                else:
                    env_dict = {}
                    for pair in new_env_vars.split(','):
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            env_dict[key.strip()] = value.strip()
                    if env_dict:
                        server['env'] = env_dict
                    elif 'env' in server:
                        del server['env']
            break
            
    if not server_found:
        print(f"Error: Server '{name}' not found.")
        return False
        
    if save_mcp_config(config, config_path, scope):
        print(f"Successfully updated MCP server '{name}' in {scope} configuration.")
        return True
    else:
        return False

def delete_server(name, config_path=None, scope='user'):
    """删除 MCP 服务器"""
    config = get_mcp_config(config_path, scope)
    if config is None:
        return False
        
    if 'servers' not in config:
        print(f"Error: No servers configured in {scope} scope.")
        return False
        
    original_count = len(config['servers'])
    config['servers'] = [s for s in config['servers'] if s['name'] != name]
    
    if len(config['servers']) == original_count:
        print(f"Error: Server '{name}' not found.")
        return False
        
    if save_mcp_config(config, config_path, scope):
        print(f"Successfully deleted MCP server '{name}' from {scope} configuration.")
        return True
    else:
        return False

def validate_config(config_path=None, scope='user'):
    """验证 MCP 配置文件"""
    config = get_mcp_config(config_path, scope)
    if config is None:
        return False
        
    is_valid = True
    
    if 'servers' not in config:
        print(f"Warning: No 'servers' key found in {scope} configuration.")
        # 这不一定是错误，可能是空配置
    else:
        if not isinstance(config['servers'], list):
            print(f"Error: 'servers' in {scope} configuration should be a list.")
            is_valid = False
        else:
            for i, server in enumerate(config['servers']):
                if not isinstance(server, dict):
                    print(f"Error: Server at index {i} in {scope} configuration should be a dictionary.")
                    is_valid = False
                    continue
                    
                # 检查必需字段
                if 'name' not in server:
                    print(f"Error: Server at index {i} is missing 'name' field.")
                    is_valid = False
                    
                if 'transport' not in server:
                    print(f"Error: Server '{server.get('name', 'Unknown')}' is missing 'transport' field.")
                    is_valid = False
                elif server['transport'] not in ['stdio', 'http', 'sse']:
                    print(f"Warning: Server '{server.get('name', 'Unknown')}' has unknown transport '{server['transport']}'.")
                    
                if 'uri' not in server:
                    print(f"Error: Server '{server.get('name', 'Unknown')}' is missing 'uri' field.")
                    is_valid = False
                    
                # 检查可选字段
                if 'env' in server:
                    if not isinstance(server['env'], dict):
                        print(f"Error: 'env' for server '{server.get('name', 'Unknown')}' should be a dictionary.")
                        is_valid = False
                        
    if is_valid:
        print(f"MCP configuration in {scope} scope is valid.")
        
    return is_valid

def main():
    parser = argparse.ArgumentParser(description='Manage Claude Code MCP Servers')
    parser.add_argument('action', choices=['list', 'add', 'edit', 'delete', 'validate'], 
                       help='Action to perform')
    
    # 通用参数
    parser.add_argument('name', nargs='?', help='Name of the MCP server')
    parser.add_argument('--config-path', help='Path to the MCP configuration file')
    parser.add_argument('--scope', choices=['user', 'project', 'all'], default='user',
                       help='Scope of the configuration (default: user)')
    
    # add/edit 特定参数
    parser.add_argument('--transport', choices=['stdio', 'http', 'sse'], 
                       help='Transport type for the server')
    parser.add_argument('--uri', help='URI for the server')
    parser.add_argument('--description', help='Description of the server')
    parser.add_argument('--env-vars', 
                       help='Environment variables as KEY1=VALUE1,KEY2=VALUE2')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_servers(config_path=args.config_path, scope=args.scope)
        
    elif args.action == 'add':
        if not args.name or not args.transport or not args.uri:
            print("Error: name, --transport, and --uri are required for add action")
            sys.exit(1)
        add_server(args.name, args.transport, args.uri, 
                  description=args.description, env_vars=args.env_vars,
                  config_path=args.config_path, scope=args.scope)
        
    elif args.action == 'edit':
        if not args.name:
            print("Error: name is required for edit action")
            sys.exit(1)
        if not any([args.transport, args.uri, args.description, args.env_vars is not None]):
            print("Error: At least one of --transport, --uri, --description, or --env-vars must be provided for edit action")
            sys.exit(1)
        edit_server(args.name, 
                   new_transport=args.transport, new_uri=args.uri,
                   new_description=args.description, new_env_vars=args.env_vars,
                   config_path=args.config_path, scope=args.scope)
        
    elif args.action == 'delete':
        if not args.name:
            print("Error: name is required for delete action")
            sys.exit(1)
        delete_server(args.name, config_path=args.config_path, scope=args.scope)
        
    elif args.action == 'validate':
        validate_config(config_path=args.config_path, scope=args.scope)

if __name__ == '__main__':
    main()