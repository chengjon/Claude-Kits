#!/usr/bin/env python3
"""扫描所有 SKILL.md 文件，找出缺少 description 的组件"""

import os
import re
from pathlib import Path

def extract_frontmatter(content):
    """提取 YAML frontmatter"""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        return match.group(1)
    return None

def check_description(frontmatter):
    """检查 frontmatter 中是否有 description"""
    if not frontmatter:
        return False

    # 检查是否有 description 字段且非空
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        # 检查是否为空或仅为引号
        if desc and desc not in ['""', "''", '']:
            return True
    return False

def extract_name(frontmatter):
    """提取技能名称"""
    if not frontmatter:
        return None

    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        return name_match.group(1).strip()
    return None

def main():
    skills_dir = Path('/opt/claude/Claude-Kits/components/skills')

    missing = []
    total = 0

    for skill_file in skills_dir.glob('*/SKILL.md'):
        total += 1
        content = skill_file.read_text(encoding='utf-8')
        frontmatter = extract_frontmatter(content)

        if not check_description(frontmatter):
            skill_name = extract_name(frontmatter) or skill_file.parent.name
            missing.append({
                'path': str(skill_file),
                'name': skill_name,
                'dir': skill_file.parent.name
            })

    print(f"Total skills: {total}")
    print(f"Missing descriptions: {len(missing)}\n")

    if missing:
        print("Skills without description:")
        for item in missing:
            print(f"  - {item['name']} ({item['dir']})")
            print(f"    Path: {item['path']}")

if __name__ == '__main__':
    main()
