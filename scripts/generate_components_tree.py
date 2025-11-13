#!/usr/bin/env python3
"""
Generate Components Tree Documentation

This script generates a comprehensive tree view of all components with descriptions.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
import yaml
import re

def extract_description_from_md(filepath: Path) -> str:
    """Extract description from markdown file (YAML frontmatter or first paragraph)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try YAML frontmatter first
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    if isinstance(frontmatter, dict) and 'description' in frontmatter:
                        return frontmatter['description']
                except:
                    pass

        # Try to find description in content
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            # Skip YAML frontmatter
            if i < 10 and (line == '---' or not line):
                continue
            # Skip headings
            if line.startswith('#'):
                continue
            # Return first non-empty paragraph
            if line and not line.startswith('[') and not line.startswith('!'):
                # Clean and truncate
                desc = re.sub(r'\[.*?\]\(.*?\)', '', line)  # Remove markdown links
                desc = re.sub(r'[*_`]', '', desc)  # Remove formatting
                return desc[:200] + ('...' if len(desc) > 200 else '')

        return "暂无描述"
    except Exception as e:
        return f"读取文件出错: {str(e)}"

def extract_description_from_sh(filepath: Path) -> str:
    """Extract description from shell script comments"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Look for Purpose or Description in comments
        in_header = False
        description_lines = []

        for line in lines[:50]:  # Check first 50 lines
            line = line.strip()

            if line.startswith('# Purpose:') or line.startswith('# 作用:'):
                desc = line.split(':', 1)[1].strip()
                return desc

            if 'Purpose:' in line or '作用:' in line:
                in_header = True
                continue

            if in_header and line.startswith('#'):
                desc_part = line.lstrip('#').strip()
                if desc_part and not desc_part.startswith('='):
                    description_lines.append(desc_part)
            elif in_header:
                break

        if description_lines:
            return ' '.join(description_lines[:3])  # First 3 lines

        # Fallback: find first meaningful comment
        for line in lines[:20]:
            line = line.strip()
            if line.startswith('#') and not line.startswith('#!') and not line.startswith('# ==='):
                comment = line.lstrip('#').strip()
                if len(comment) > 20 and not comment.startswith('='):
                    return comment[:200]

        return "Shell 脚本"
    except Exception as e:
        return f"读取文件出错: {str(e)}"

def get_file_description(filepath: Path, component_type: str) -> str:
    """Get description for any file type"""
    filename = filepath.name

    # Special cases
    if filename == 'README.md':
        return "组件文档和使用指南"
    if filename == 'package.json':
        return "Hook 依赖配置文件"
    if filename.endswith('-template.md') or filename.endswith('template.md'):
        return f"创建新 {component_type} 的模板"
    if filename.endswith('.bak'):
        return "备份文件"

    # Extract by file type
    if filepath.suffix == '.md':
        return extract_description_from_md(filepath)
    elif filepath.suffix in ['.sh', '.bash']:
        return extract_description_from_sh(filepath)
    elif filepath.suffix == '.ts':
        return "TypeScript Hook 实现"
    elif filepath.suffix == '.json':
        return "配置文件"
    else:
        return "组件文件"

def generate_tree_structure(base_path: Path) -> Dict:
    """Generate tree structure with descriptions"""
    structure = {
        'agents': {},
        'commands': {},
        'skills': {},
        'hooks': {}
    }

    for comp_type in structure.keys():
        comp_dir = base_path / comp_type
        if not comp_dir.exists():
            continue

        # List all files and directories
        items = sorted(comp_dir.iterdir(), key=lambda x: (not x.is_dir(), x.name))

        for item in items:
            rel_path = item.relative_to(comp_dir)

            if item.is_file():
                desc = get_file_description(item, comp_type)
                structure[comp_type][str(rel_path)] = {
                    'type': 'file',
                    'description': desc
                }
            elif item.is_dir():
                # For skills, dive into subdirectories
                if comp_type == 'skills':
                    skill_files = {}
                    for skill_file in item.rglob('*'):
                        if skill_file.is_file():
                            skill_rel_path = skill_file.relative_to(comp_dir)
                            desc = get_file_description(skill_file, comp_type)
                            skill_files[str(skill_rel_path)] = {
                                'type': 'file',
                                'description': desc
                            }
                    structure[comp_type].update(skill_files)
                # For hooks, dive into subdirectories
                elif comp_type == 'hooks':
                    for hook_file in item.rglob('*'):
                        if hook_file.is_file():
                            hook_rel_path = hook_file.relative_to(comp_dir)
                            desc = get_file_description(hook_file, comp_type)
                            structure[comp_type][str(hook_rel_path)] = {
                                'type': 'file',
                                'description': desc
                            }

    return structure

def format_tree_markdown(structure: Dict) -> str:
    """Format tree structure as markdown"""
    md_lines = [
        "# Claude-Kits 组件文件树",
        "",
        "> 自动生成的组件文件树，包含所有组件的简介",
        "",
        f"**生成时间**: {Path(__file__).stat().st_mtime}",
        "",
        "---",
        ""
    ]

    type_names = {
        'agents': '🤖 Agents (子代理)',
        'commands': '⚡ Slash Commands (斜杠命令)',
        'skills': '📚 Skills (技能)',
        'hooks': '🪝 Hooks (钩子)'
    }

    for comp_type, items in structure.items():
        if not items:
            continue

        md_lines.append(f"## {type_names[comp_type]}")
        md_lines.append(f"")
        md_lines.append(f"**总计**: {len(items)} 个文件")
        md_lines.append("")

        # Group by directory for skills and hooks
        if comp_type in ['skills', 'hooks']:
            # Group files by top-level directory
            grouped = {}
            for filepath, info in sorted(items.items()):
                parts = Path(filepath).parts
                if len(parts) > 1:
                    top_dir = parts[0]
                    if top_dir not in grouped:
                        grouped[top_dir] = []
                    grouped[top_dir].append((filepath, info))
                else:
                    if '__root__' not in grouped:
                        grouped['__root__'] = []
                    grouped['__root__'].append((filepath, info))

            for dir_name in sorted(grouped.keys()):
                files = grouped[dir_name]

                if dir_name != '__root__':
                    md_lines.append(f"### 📁 {dir_name}/")
                    md_lines.append("")

                for filepath, info in files:
                    filename = Path(filepath).name
                    indent = "  " if dir_name != '__root__' else ""
                    md_lines.append(f"{indent}- **{filename}**")
                    md_lines.append(f"{indent}  - {info['description']}")
                    md_lines.append("")
        else:
            # Simple list for agents and commands
            for filepath, info in sorted(items.items()):
                filename = Path(filepath).name
                md_lines.append(f"- **{filename}**")
                md_lines.append(f"  - {info['description']}")
                md_lines.append("")

        md_lines.append("---")
        md_lines.append("")

    return '\n'.join(md_lines)

def main():
    """Main entry point"""
    script_dir = Path(__file__).parent
    base_path = script_dir.parent / 'components'
    output_path = script_dir.parent / 'docs' / 'COMPONENTS_TREE.md'

    print("🔍 正在扫描组件目录...")
    structure = generate_tree_structure(base_path)

    print("📝 正在生成 Markdown 文档...")
    markdown = format_tree_markdown(structure)

    # Ensure docs directory exists
    output_path.parent.mkdir(exist_ok=True)

    print(f"💾 正在保存到 {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"✅ 完成！已生成包含描述的文件树文档。")
    print(f"   文档化的文件总数: {sum(len(items) for items in structure.values())}")
    print(f"   输出文件: {output_path}")

if __name__ == '__main__':
    main()
