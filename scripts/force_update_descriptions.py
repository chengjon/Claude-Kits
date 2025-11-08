#!/usr/bin/env python3
"""
强制更新所有组件的 description 到注册表
"""

import json
import re
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
COMPONENTS_DIR = PROJECT_ROOT / "components"
REGISTRY_FILE = PROJECT_ROOT / "components_registry.json"


def extract_frontmatter(content):
    """提取 YAML frontmatter"""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
    return None


def update_skills_descriptions():
    """更新所有 skills 的 description"""
    # 加载注册表
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    skills_dir = COMPONENTS_DIR / "skills"
    updated_count = 0

    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        skill_name = skill_dir.name

        # 读取文件内容
        content = skill_file.read_text(encoding='utf-8')
        frontmatter = extract_frontmatter(content)

        if frontmatter and skill_name in registry['components']['skills']:
            # 提取 description
            description = frontmatter.get('description', '')
            name = frontmatter.get('name', skill_name)

            # 更新到注册表
            if description:
                registry['components']['skills'][skill_name]['description'] = description
                registry['components']['skills'][skill_name]['name'] = name
                updated_count += 1
                print(f"✓ Updated: {skill_name}")

    # 保存注册表
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print(f"\n总计更新 {updated_count} 个技能的 description")


def update_agents_descriptions():
    """更新所有 agents 的 description"""
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    agents_dir = COMPONENTS_DIR / "agents"
    updated_count = 0

    for agent_file in agents_dir.glob("*.md"):
        agent_name = agent_file.stem

        content = agent_file.read_text(encoding='utf-8')
        frontmatter = extract_frontmatter(content)

        if frontmatter and agent_name in registry['components']['agents']:
            description = frontmatter.get('description', '')
            name = frontmatter.get('name', agent_name)
            model = frontmatter.get('model', 'sonnet')

            if description:
                registry['components']['agents'][agent_name]['description'] = description
                registry['components']['agents'][agent_name]['name'] = name
                registry['components']['agents'][agent_name]['model'] = model
                updated_count += 1
                print(f"✓ Updated: {agent_name}")

    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print(f"\n总计更新 {updated_count} 个 agent 的 description")


def update_commands_descriptions():
    """更新所有 commands 的 description"""
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    commands_dir = COMPONENTS_DIR / "commands"
    updated_count = 0

    for command_file in commands_dir.glob("*.md"):
        command_name = command_file.stem

        content = command_file.read_text(encoding='utf-8')
        frontmatter = extract_frontmatter(content)

        if frontmatter and command_name in registry['components']['commands']:
            description = frontmatter.get('description', '')

            if description:
                registry['components']['commands'][command_name]['description'] = description
                updated_count += 1
                print(f"✓ Updated: {command_name}")

    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print(f"\n总计更新 {updated_count} 个 command 的 description")


if __name__ == "__main__":
    print("="*70)
    print("强制更新所有组件的 description")
    print("="*70)

    print("\n更新 Skills...")
    update_skills_descriptions()

    print("\n更新 Agents...")
    update_agents_descriptions()

    print("\n更新 Commands...")
    update_commands_descriptions()

    print("\n" + "="*70)
    print("更新完成！")
    print("="*70)
