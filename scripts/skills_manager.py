#!/usr/bin/env python3
"""
Agent Skills 管理脚本

功能：
1. 浏览可用的 Agent Skills (个人, 项目, 插件)
2. 安装/创建新的 Agent Skill (个人: ~/.claude/skills/, 项目: .claude/skills/)
3. 修改现有 Agent Skill 的内容或元数据
4. 删除 Agent Skill
5. 验证 Skill 配置 (YAML 语法等)

使用方法：
python skills_manager.py [list|install|edit|delete|validate] [skill_name] [--scope personal|project] [--path /path/to/project]
"""

import os
import sys
import argparse
import yaml
import json
import subprocess
from pathlib import Path

# 导入 UniversalInstaller
try:
    from universal_installer import UniversalInstaller
except ImportError:
    # 如果直接运行此脚本，添加 scripts/ 到路径
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from universal_installer import UniversalInstaller

# 默认路径
USER_SKILLS_DIR = Path.home() / '.claude' / 'skills'
PROJECT_SKILLS_DIR = Path('.claude') / 'skills'

def get_skills(scope='all', project_path=None):
    """获取指定范围内的所有 Skills

    优先级顺序：项目级 > 插件级 > 用户级
    """
    skills = {}

    # 用户级 (最低优先级)
    if scope in ['all', 'user', 'personal']:
        user_skills = _list_skills_in_dir(USER_SKILLS_DIR, 'user')
        skills.update(user_skills)

    # 插件级 (中等优先级)
    if scope in ['all', 'plugin']:
        # 插件 Skills 存储在 ~/.claude/plugins/*/skills/
        plugins_dir = Path.home() / '.claude' / 'plugins'
        if plugins_dir.exists():
            for plugin_dir in plugins_dir.iterdir():
                if plugin_dir.is_dir():
                    plugin_skills_dir = plugin_dir / 'skills'
                    if plugin_skills_dir.exists():
                        plugin_skills = _list_skills_in_dir(plugin_skills_dir, f'plugin:{plugin_dir.name}')
                        # 插件 Skills 会覆盖同名的用户级 Skills
                        skills.update(plugin_skills)

    # 项目级 (最高优先级)
    if scope in ['all', 'project']:
        project_dir = Path(project_path) / '.claude' / 'skills' if project_path else PROJECT_SKILLS_DIR
        project_skills = _list_skills_in_dir(project_dir, 'project')
        # 项目级 Skills 会覆盖同名的插件级和用户级 Skills
        skills.update(project_skills)

    return skills

def _list_skills_in_dir(skills_dir, scope_type):
    """列出指定目录下的 Skills"""
    skills = {}
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / 'SKILL.md'
                if skill_md.exists():
                    try:
                        with open(skill_md, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # 简单解析 YAML frontmatter
                            if content.startswith('---'):
                                end = content.find('---', 3)
                                if end != -1:
                                    frontmatter = yaml.safe_load(content[3:end])
                                    skills[skill_dir.name] = {
                                        'name': frontmatter.get('name', skill_dir.name),
                                        'description': frontmatter.get('description', 'No description'),
                                        'scope': scope_type,
                                        'path': str(skill_dir)
                                    }
                    except Exception as e:
                        print(f"Warning: Could not parse {skill_md}: {e}")
    return skills

def install_skill(skill_name, scope='project', project_path=None, template_dir=None, dry_run=False, interactive=True):
    """安装一个 Skill（使用 UniversalInstaller）

    从 components/skills/ 复制完整的 Skill 模板到目标位置。

    支持的 scope:
    - user: 用户级 (~/.claude/skills/)
    - project: 项目级 ({project_path}/.claude/skills/)
    - plugin: 插件级 (不支持直接安装，由插件管理)

    Args:
        skill_name: Skill 名称（如 'task-planning-pro'）
        scope: 安装作用域
        project_path: 项目路径（scope='project' 时使用）
        template_dir: 已废弃（兼容性保留）
        dry_run: 预览模式，不执行实际安装
        interactive: 交互模式，冲突时询问用户

    Returns:
        bool: 是否安装成功
    """
    if scope == 'plugin':
        print("Error: Cannot directly install skills at plugin scope. Use plugin manager instead.")
        return False

    # 确定目标目录
    if scope in ['user', 'personal']:
        target_dir = str(Path.home())
    elif scope == 'project':
        target_dir = project_path if project_path else str(Path.cwd())
    else:
        raise ValueError(f"Unknown scope: {scope}. Must be 'user', 'personal', or 'project'")

    # 使用 UniversalInstaller 安装
    try:
        installer = UniversalInstaller()
        success = installer.install_component(
            component_type='skills',
            component_name=skill_name,
            target_dir=target_dir,
            scope=scope,
            dry_run=dry_run,
            interactive=interactive
        )
        return success
    except FileNotFoundError as e:
        print(f"Error: Skill '{skill_name}' not found in components/skills/")
        print(f"Available skills: run 'python scripts/skills_manager.py list'")
        return False
    except Exception as e:
        print(f"Error installing skill: {e}")
        return False

def edit_skill(skill_name, scope='project', project_path=None):
    """编辑一个现有的 Skill"""
    # 确定 Skill 的位置
    skill_path = None
    project_dir = Path(project_path) if project_path else Path.cwd()
    
    # 优先查找项目级 Skill
    if scope in ['project', 'all']:
        project_skill_dir = project_dir / '.claude' / 'skills' / skill_name
        if project_skill_dir.exists():
            skill_path = project_skill_dir
            
    # 如果没找到或指定了个人范围，查找个人 Skill
    if skill_path is None and scope in ['personal', 'all']:
        personal_skill_dir = USER_SKILLS_DIR / skill_name
        if personal_skill_dir.exists():
            skill_path = personal_skill_dir
            
    if skill_path is None:
        print(f"Error: Skill '{skill_name}' not found.")
        return False
        
    skill_md_path = skill_path / 'SKILL.md'
    if not skill_md_path.exists():
        print(f"Error: SKILL.md not found in {skill_path}")
        return False
        
    # 使用系统默认编辑器打开
    editor = os.environ.get('EDITOR', 'nano')  # 默认使用 nano
    try:
        subprocess.run([editor, str(skill_md_path)])
        print(f"Successfully edited Skill '{skill_name}' at {skill_path}")
        return True
    except Exception as e:
        print(f"Error: Could not open editor: {e}")
        # 提示用户手动编辑
        print(f"Please manually edit the file: {skill_md_path}")
        return False

def delete_skill(skill_name, scope='project', project_path=None):
    """删除一个 Skill"""
    skill_path = None
    project_dir = Path(project_path) if project_path else Path.cwd()
    
    if scope in ['project', 'all']:
        project_skill_dir = project_dir / '.claude' / 'skills' / skill_name
        if project_skill_dir.exists():
            skill_path = project_skill_dir
            
    if skill_path is None and scope in ['personal', 'all']:
        personal_skill_dir = USER_SKILLS_DIR / skill_name
        if personal_skill_dir.exists():
            skill_path = personal_skill_dir
            
    if skill_path is None:
        print(f"Error: Skill '{skill_name}' not found in specified scope.")
        return False
        
    try:
        import shutil
        shutil.rmtree(skill_path)
        print(f"Successfully deleted Skill '{skill_name}' from {skill_path}")
        return True
    except Exception as e:
        print(f"Error: Could not delete Skill: {e}")
        return False

def validate_skill(skill_name, scope='project', project_path=None):
    """验证 Skill 的配置"""
    skill_path = None
    project_dir = Path(project_path) if project_path else Path.cwd()
    
    if scope in ['project', 'all']:
        project_skill_dir = project_dir / '.claude' / 'skills' / skill_name
        if project_skill_dir.exists():
            skill_path = project_skill_dir
            
    if skill_path is None and scope in ['personal', 'all']:
        personal_skill_dir = USER_SKILLS_DIR / skill_name
        if personal_skill_dir.exists():
            skill_path = personal_skill_dir
            
    if skill_path is None:
        print(f"Error: Skill '{skill_name}' not found.")
        return False
        
    skill_md_path = skill_path / 'SKILL.md'
    if not skill_md_path.exists():
        print(f"Error: SKILL.md not found in {skill_path}")
        return False
        
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. 检查 YAML frontmatter
        if not content.startswith('---'):
            print(f"Error: SKILL.md in {skill_path} does not start with '---'")
            return False
            
        end = content.find('---', 3)
        if end == -1:
            print(f"Error: Could not find closing '---' in {skill_md_path}")
            return False
            
        frontmatter_str = content[3:end]
        frontmatter = yaml.safe_load(frontmatter_str)
        
        # 2. 检查必需字段
        if 'name' not in frontmatter:
            print(f"Error: 'name' field is missing in {skill_md_path}")
            return False
            
        if 'description' not in frontmatter:
            print(f"Error: 'description' field is missing in {skill_md_path}")
            return False
            
        # 3. 检查 name 格式
        name = frontmatter['name']
        if not all(c.islower() or c.isdigit() or c == '-' for c in name):
            print(f"Warning: 'name' should only contain lowercase letters, digits, and hyphens in {skill_md_path}")
            
        # 4. 检查 description 长度
        description = frontmatter['description']
        if len(description) > 1024:
            print(f"Warning: 'description' is longer than 1024 characters in {skill_md_path}")
            
        print(f"Skill '{skill_name}' at {skill_path} is valid.")
        return True
        
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in {skill_md_path}: {e}")
        return False
    except Exception as e:
        print(f"Error: Could not validate Skill: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Manage Claude Code Agent Skills')
    parser.add_argument('action', choices=['list', 'install', 'edit', 'delete', 'validate'], help='Action to perform')
    parser.add_argument('skill_name', nargs='?', help='Name of the skill')
    parser.add_argument('--scope', choices=['user', 'personal', 'project', 'plugin', 'all'], default='project',
                       help='Scope of the skill (user: ~/.claude/skills/, project: .claude/skills/, plugin: from plugins)')
    parser.add_argument('--path', help='Path to the project directory')
    parser.add_argument('--template', help='Path to a template directory for new skills (deprecated)')
    parser.add_argument('--dry-run', action='store_true', help='Preview installation without making changes')
    parser.add_argument('--non-interactive', action='store_true', help='Non-interactive mode (skip conflicts automatically)')

    args = parser.parse_args()

    if args.action == 'list':
        skills = get_skills(scope=args.scope, project_path=args.path)
        if not skills:
            print("No skills found.")
        else:
            print(f"Found {len(skills)} skill(s):")
            for name, info in skills.items():
                print(f"  - {name}: {info['description']} ({info['scope']})")

    elif args.action == 'install':
        if not args.skill_name:
            print("Error: skill_name is required for install action")
            sys.exit(1)
        success = install_skill(
            args.skill_name,
            scope=args.scope,
            project_path=args.path,
            template_dir=args.template,
            dry_run=args.dry_run,
            interactive=not args.non_interactive
        )
        sys.exit(0 if success else 1)
        
    elif args.action == 'edit':
        if not args.skill_name:
            print("Error: skill_name is required for edit action")
            sys.exit(1)
        edit_skill(args.skill_name, scope=args.scope, project_path=args.path)
        
    elif args.action == 'delete':
        if not args.skill_name:
            print("Error: skill_name is required for delete action")
            sys.exit(1)
        delete_skill(args.skill_name, scope=args.scope, project_path=args.path)
        
    elif args.action == 'validate':
        if not args.skill_name:
            print("Error: skill_name is required for validate action")
            sys.exit(1)
        validate_skill(args.skill_name, scope=args.scope, project_path=args.path)

if __name__ == '__main__':
    main()