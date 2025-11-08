#!/usr/bin/env python3
"""
Subagents 管理脚本

功能：
1. 浏览可用的 Subagents (个人, 项目, 插件, CLI)
2. 安装/创建新的 Subagent (个人: ~/.claude/agents/, 项目: .claude/agents/)
3. 修改现有 Subagent 的内容或元数据
4. 删除 Subagent
5. 验证 Subagent 配置 (YAML 语法等)

使用方法：
python subagents_manager.py [list|install|edit|delete|validate] [subagent_name] [--scope personal|project] [--path /path/to/project]
"""

import os
import sys
import argparse
import yaml
import subprocess
from pathlib import Path

# 默认路径
USER_AGENTS_DIR = Path.home() / '.claude' / 'agents'
PROJECT_AGENTS_DIR = Path('.claude') / 'agents'

def get_subagents(scope='all', project_path=None):
    """获取指定范围内的所有 Subagents

    优先级顺序：项目级 > 插件级 > 用户级
    """
    subagents = {}

    # 用户级 (最低优先级)
    if scope in ['all', 'user', 'personal']:
        user_agents = _list_agents_in_dir(USER_AGENTS_DIR, 'user')
        subagents.update(user_agents)

    # 插件级 (中等优先级)
    if scope in ['all', 'plugin']:
        # 插件 Agents 存储在 ~/.claude/plugins/*/agents/
        plugins_dir = Path.home() / '.claude' / 'plugins'
        if plugins_dir.exists():
            for plugin_dir in plugins_dir.iterdir():
                if plugin_dir.is_dir():
                    plugin_agents_dir = plugin_dir / 'agents'
                    if plugin_agents_dir.exists():
                        plugin_agents = _list_agents_in_dir(plugin_agents_dir, f'plugin:{plugin_dir.name}')
                        # 插件 Agents 会覆盖同名的用户级 Agents
                        subagents.update(plugin_agents)

    # 项目级 (最高优先级)
    if scope in ['all', 'project']:
        project_dir = Path(project_path) / '.claude' / 'agents' if project_path else PROJECT_AGENTS_DIR
        project_agents = _list_agents_in_dir(project_dir, 'project')
        # 项目级 Agents 会覆盖同名的插件级和用户级 Agents
        subagents.update(project_agents)

    return subagents

def _list_agents_in_dir(agents_dir, scope_type):
    """列出指定目录下的 Subagents"""
    subagents = {}
    if agents_dir.exists():
        for agent_file in agents_dir.iterdir():
            if agent_file.is_file() and agent_file.suffix == '.md':
                agent_name = agent_file.stem
                try:
                    with open(agent_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 简单解析 YAML frontmatter
                        if content.startswith('---'):
                            end = content.find('---', 3)
                            if end != -1:
                                frontmatter = yaml.safe_load(content[3:end])
                                subagents[agent_name] = {
                                    'name': frontmatter.get('name', agent_name),
                                    'description': frontmatter.get('description', 'No description'),
                                    'scope': scope_type,
                                    'path': str(agent_file),
                                    'tools': frontmatter.get('tools', 'Inherited'),
                                    'model': frontmatter.get('model', 'Default')
                                }
                except Exception as e:
                    print(f"Warning: Could not parse {agent_file}: {e}")
    return subagents

def install_subagent(subagent_name, scope='project', project_path=None, template_dir=None):
    """安装/创建一个新的 Subagent

    支持的 scope:
    - user: 用户级 (~/.claude/agents/)
    - project: 项目级 (.claude/agents/)
    - plugin: 插件级 (不支持直接安装，由插件管理)
    """
    if scope in ['user', 'personal']:
        target_dir = USER_AGENTS_DIR
    elif scope == 'project':
        project_dir = Path(project_path) if project_path else Path.cwd()
        target_dir = project_dir / '.claude' / 'agents'
    elif scope == 'plugin':
        print("Error: Cannot directly install agents at plugin scope. Use plugin manager instead.")
        return False
    else:
        raise ValueError("Scope must be 'user', 'personal', or 'project'")
    
    target_dir.mkdir(parents=True, exist_ok=True)
    agent_md_path = target_dir / f'{subagent_name}.md'
    
    if agent_md_path.exists():
        print(f"Error: Subagent '{subagent_name}' already exists at {agent_md_path}")
        return False
        
    # 如果提供了模板目录，则复制模板
    if template_dir and Path(template_dir).exists():
        # 这里可以实现复制模板的逻辑
        # 为简化，我们只创建基本结构
        pass
    
    # 创建基本的 .md 文件
    with open(agent_md_path, 'w', encoding='utf-8') as f:
        f.write(f"""---
name: {subagent_name}
description: Brief description of what this Subagent does and when to use it.
---

# {subagent_name.replace('-', ' ').title()}

## Role
Define the specific role and responsibilities of this Subagent.

## Instructions
Provide clear, step-by-step guidance for the Subagent on how to perform its tasks.

## Best Practices
List any specific best practices or constraints this Subagent should follow.
""")
    
    print(f"Successfully created new Subagent '{subagent_name}' at {agent_md_path}")
    return True

def edit_subagent(subagent_name, scope='project', project_path=None):
    """编辑一个现有的 Subagent"""
    # 确定 Subagent 的位置
    agent_path = None
    project_dir = Path(project_path) if project_path else Path.cwd()
    
    # 优先查找项目级 Subagent
    if scope in ['project', 'all']:
        project_agent_file = project_dir / '.claude' / 'agents' / f'{subagent_name}.md'
        if project_agent_file.exists():
            agent_path = project_agent_file
            
    # 如果没找到或指定了个人范围，查找个人 Subagent
    if agent_path is None and scope in ['personal', 'all']:
        personal_agent_file = USER_AGENTS_DIR / f'{subagent_name}.md'
        if personal_agent_file.exists():
            agent_path = personal_agent_file
            
    if agent_path is None:
        print(f"Error: Subagent '{subagent_name}' not found.")
        return False
        
    # 使用系统默认编辑器打开
    editor = os.environ.get('EDITOR', 'nano')  # 默认使用 nano
    try:
        subprocess.run([editor, str(agent_path)])
        print(f"Successfully edited Subagent '{subagent_name}' at {agent_path}")
        return True
    except Exception as e:
        print(f"Error: Could not open editor: {e}")
        # 提示用户手动编辑
        print(f"Please manually edit the file: {agent_path}")
        return False

def delete_subagent(subagent_name, scope='project', project_path=None):
    """删除一个 Subagent"""
    agent_path = None
    project_dir = Path(project_path) if project_path else Path.cwd()
    
    if scope in ['project', 'all']:
        project_agent_file = project_dir / '.claude' / 'agents' / f'{subagent_name}.md'
        if project_agent_file.exists():
            agent_path = project_agent_file
            
    if agent_path is None and scope in ['personal', 'all']:
        personal_agent_file = USER_AGENTS_DIR / f'{subagent_name}.md'
        if personal_agent_file.exists():
            agent_path = personal_agent_file
            
    if agent_path is None:
        print(f"Error: Subagent '{subagent_name}' not found in specified scope.")
        return False
        
    try:
        agent_path.unlink()
        print(f"Successfully deleted Subagent '{subagent_name}' from {agent_path}")
        return True
    except Exception as e:
        print(f"Error: Could not delete Subagent: {e}")
        return False

def validate_subagent(subagent_name, scope='project', project_path=None):
    """验证 Subagent 的配置"""
    agent_path = None
    project_dir = Path(project_path) if project_path else Path.cwd()
    
    if scope in ['project', 'all']:
        project_agent_file = project_dir / '.claude' / 'agents' / f'{subagent_name}.md'
        if project_agent_file.exists():
            agent_path = project_agent_file
            
    if agent_path is None and scope in ['personal', 'all']:
        personal_agent_file = USER_AGENTS_DIR / f'{subagent_name}.md'
        if personal_agent_file.exists():
            agent_path = personal_agent_file
            
    if agent_path is None:
        print(f"Error: Subagent '{subagent_name}' not found.")
        return False
        
    try:
        with open(agent_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. 检查 YAML frontmatter
        if not content.startswith('---'):
            print(f"Error: Subagent file {agent_path} does not start with '---'")
            return False
            
        end = content.find('---', 3)
        if end == -1:
            print(f"Error: Could not find closing '---' in {agent_path}")
            return False
            
        frontmatter_str = content[3:end]
        frontmatter = yaml.safe_load(frontmatter_str)
        
        # 2. 检查必需字段
        if 'name' not in frontmatter:
            print(f"Error: 'name' field is missing in {agent_path}")
            return False
            
        if 'description' not in frontmatter:
            print(f"Error: 'description' field is missing in {agent_path}")
            return False
            
        # 3. 检查 name 格式
        name = frontmatter['name']
        if not all(c.islower() or c.isdigit() or c == '-' for c in name):
            print(f"Warning: 'name' should only contain lowercase letters, digits, and hyphens in {agent_path}")
            
        print(f"Subagent '{subagent_name}' at {agent_path} is valid.")
        return True
        
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in {agent_path}: {e}")
        return False
    except Exception as e:
        print(f"Error: Could not validate Subagent: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Manage Claude Code Subagents')
    parser.add_argument('action', choices=['list', 'install', 'edit', 'delete', 'validate'], help='Action to perform')
    parser.add_argument('subagent_name', nargs='?', help='Name of the subagent')
    parser.add_argument('--scope', choices=['user', 'personal', 'project', 'plugin', 'all'], default='project',
                       help='Scope of the subagent (user: ~/.claude/agents/, project: .claude/agents/, plugin: from plugins)')
    parser.add_argument('--path', help='Path to the project directory')
    parser.add_argument('--template', help='Path to a template directory for new subagents')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        subagents = get_subagents(scope=args.scope, project_path=args.path)
        if not subagents:
            print("No subagents found.")
        else:
            print(f"Found {len(subagents)} subagent(s):")
            for name, info in subagents.items():
                print(f"  - {name}: {info['description']} ({info['scope']})")
                print(f"    Tools: {info['tools']}, Model: {info['model']}")
                
    elif args.action == 'install':
        if not args.subagent_name:
            print("Error: subagent_name is required for install action")
            sys.exit(1)
        install_subagent(args.subagent_name, scope=args.scope, project_path=args.path, template_dir=args.template)
        
    elif args.action == 'edit':
        if not args.subagent_name:
            print("Error: subagent_name is required for edit action")
            sys.exit(1)
        edit_subagent(args.subagent_name, scope=args.scope, project_path=args.path)
        
    elif args.action == 'delete':
        if not args.subagent_name:
            print("Error: subagent_name is required for delete action")
            sys.exit(1)
        delete_subagent(args.subagent_name, scope=args.scope, project_path=args.path)
        
    elif args.action == 'validate':
        if not args.subagent_name:
            print("Error: subagent_name is required for validate action")
            sys.exit(1)
        validate_subagent(args.subagent_name, scope=args.scope, project_path=args.path)

if __name__ == '__main__':
    main()