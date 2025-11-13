#!/usr/bin/env python3
"""
Migrate Components from Reference Projects

This script migrates agents, skills, hooks, and commands from reference projects
to the main components directory, avoiding duplicates and maintaining format.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml
import hashlib

console_output = []

def log(message: str):
    """Log message to both console and list"""
    print(message)
    console_output.append(message)

def load_existing_components() -> Dict[str, Set[str]]:
    """Load names of existing components"""
    base_path = Path(__file__).parent.parent / "components"

    existing = {
        'agents': set(),
        'skills': set(),
        'commands': set(),
        'hooks': set()
    }

    # Load agents
    agents_dir = base_path / "agents"
    if agents_dir.exists():
        for file in agents_dir.glob("*.md"):
            if not file.name.endswith('.bak') and file.name != "README.md":
                existing['agents'].add(file.stem)

    # Load skills
    skills_dir = base_path / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                existing['skills'].add(skill_dir.name)

    # Load commands
    commands_dir = base_path / "commands"
    if commands_dir.exists():
        for file in commands_dir.glob("*.md"):
            if file.name != "README.md":
                existing['commands'].add(file.stem)

    # Load hooks
    hooks_dir = base_path / "hooks"
    if hooks_dir.exists():
        for file in hooks_dir.rglob("*"):
            if file.is_file() and file.suffix in ['.sh', '.ts']:
                existing['hooks'].add(file.stem)

    return existing

def extract_frontmatter(file_path: Path) -> Dict:
    """Extract YAML frontmatter from markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            return {}

        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}

        return yaml.safe_load(parts[1])
    except Exception as e:
        log(f"  ⚠️  Error reading frontmatter from {file_path}: {e}")
        return {}

def is_duplicate_content(source_file: Path, target_file: Path) -> bool:
    """Check if two files have similar content (by hash)"""
    try:
        if not target_file.exists():
            return False

        with open(source_file, 'rb') as f:
            source_hash = hashlib.md5(f.read()).hexdigest()
        with open(target_file, 'rb') as f:
            target_hash = hashlib.md5(f.read()).hexdigest()

        return source_hash == target_hash
    except:
        return False

def migrate_agents_from_awesome(existing: Set[str]) -> Tuple[int, List[str]]:
    """Migrate agents from awesome-claude-code-subagents"""
    source_base = Path(__file__).parent.parent / "reference" / "awesome-claude-code-subagents" / "categories"
    target_dir = Path(__file__).parent.parent / "components" / "agents"

    migrated = 0
    new_agents = []

    if not source_base.exists():
        log(f"  ⚠️  Source directory not found: {source_base}")
        return 0, []

    # Scan all category directories
    for category_dir in source_base.iterdir():
        if not category_dir.is_dir():
            continue

        log(f"\n  📁 Scanning {category_dir.name}...")

        for agent_file in category_dir.glob("*.md"):
            if agent_file.name == "README.md":
                continue

            agent_name = agent_file.stem

            # Check if already exists
            if agent_name in existing:
                continue

            # Extract frontmatter to validate
            frontmatter = extract_frontmatter(agent_file)
            if not frontmatter or 'name' not in frontmatter:
                log(f"    ⚠️  Skipping {agent_name} (invalid frontmatter)")
                continue

            # Check for duplicate content
            target_file = target_dir / agent_file.name
            if is_duplicate_content(agent_file, target_file):
                log(f"    ⏭️  Skipping {agent_name} (duplicate content)")
                continue

            # Copy to target
            try:
                shutil.copy2(agent_file, target_file)
                migrated += 1
                new_agents.append(agent_name)
                log(f"    ✅ Migrated: {agent_name}")
            except Exception as e:
                log(f"    ❌ Failed to migrate {agent_name}: {e}")

    return migrated, new_agents

def migrate_agents_from_guide(existing: Set[str]) -> Tuple[int, List[str]]:
    """Migrate agents from claude-code-guide CLAUDE.md Collection"""
    source_base = Path(__file__).parent.parent / "reference" / "claude-code-guide" / "Guide On CLAUDE.md" / "CLAUDE.md Collection"
    target_dir = Path(__file__).parent.parent / "components" / "agents"

    migrated = 0
    new_agents = []

    if not source_base.exists():
        log(f"  ⚠️  Source directory not found: {source_base}")
        return 0, []

    # Scan framework directories (django, rails, vue, laravel, etc.)
    for framework_dir in source_base.iterdir():
        if not framework_dir.is_dir():
            continue

        log(f"\n  📁 Scanning {framework_dir.name}...")

        for agent_file in framework_dir.glob("*.md"):
            if agent_file.name in ["README.md", "CLAUDE.md"]:
                continue

            agent_name = agent_file.stem

            # Check if already exists
            if agent_name in existing:
                continue

            # Extract frontmatter to validate
            frontmatter = extract_frontmatter(agent_file)
            if not frontmatter or 'name' not in frontmatter:
                log(f"    ⚠️  Skipping {agent_name} (invalid frontmatter)")
                continue

            # Check for duplicate content
            target_file = target_dir / agent_file.name
            if is_duplicate_content(agent_file, target_file):
                log(f"    ⏭️  Skipping {agent_name} (duplicate content)")
                continue

            # Copy to target
            try:
                shutil.copy2(agent_file, target_file)
                migrated += 1
                new_agents.append(agent_name)
                log(f"    ✅ Migrated: {agent_name}")
            except Exception as e:
                log(f"    ❌ Failed to migrate {agent_name}: {e}")

    return migrated, new_agents

def save_migration_report(report: Dict):
    """Save migration report to file"""
    report_dir = Path(__file__).parent.parent / "docs"
    report_file = report_dir / "MIGRATION_REPORT.md"

    content = [
        "# Component Migration Report",
        "",
        f"> 迁移时间: {Path(__file__).stat().st_mtime}",
        "",
        "## 📊 迁移统计",
        "",
        f"- **Agents (awesome-claude-code-subagents)**: {report['awesome_agents']} 个",
        f"- **Agents (claude-code-guide)**: {report['guide_agents']} 个",
        f"- **总计**: {report['total']} 个新组件",
        "",
        "## 📝 迁移日志",
        "",
        "```"
    ]

    content.extend(console_output)
    content.append("```")
    content.append("")

    if report.get('new_agents'):
        content.append("## 🆕 新增 Agents")
        content.append("")
        for agent in sorted(report['new_agents']):
            content.append(f"- {agent}")
        content.append("")

    content.append("---")
    content.append("")
    content.append("**下一步**: 运行 `python scripts/components_scanner.py` 更新组件注册表")
    content.append("")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))

    log(f"\n📄 Migration report saved to: {report_file}")

def main():
    """Main entry point"""
    log("🔍 Component Migration Tool")
    log("=" * 70)

    # Load existing components
    log("\n📦 Loading existing components...")
    existing = load_existing_components()
    log(f"  - Agents: {len(existing['agents'])}")
    log(f"  - Skills: {len(existing['skills'])}")
    log(f"  - Commands: {len(existing['commands'])}")
    log(f"  - Hooks: {len(existing['hooks'])}")

    # Migrate from awesome-claude-code-subagents
    log("\n" + "=" * 70)
    log("🚀 Migrating from awesome-claude-code-subagents...")
    log("=" * 70)
    awesome_count, awesome_agents = migrate_agents_from_awesome(existing['agents'])

    # Migrate from claude-code-guide
    log("\n" + "=" * 70)
    log("🚀 Migrating from claude-code-guide...")
    log("=" * 70)
    guide_count, guide_agents = migrate_agents_from_guide(existing['agents'])

    # Summary
    total = awesome_count + guide_count
    all_new_agents = awesome_agents + guide_agents

    log("\n" + "=" * 70)
    log("✅ Migration Complete!")
    log("=" * 70)
    log(f"\n📊 Summary:")
    log(f"  - From awesome-claude-code-subagents: {awesome_count} agents")
    log(f"  - From claude-code-guide: {guide_count} agents")
    log(f"  - Total new components: {total}")

    if total > 0:
        log(f"\n🎉 Successfully migrated {total} new components!")
        log("\n⚠️  Next steps:")
        log("  1. Run: python scripts/components_scanner.py")
        log("  2. Review migrated components in components/agents/")
        log("  3. Update documentation if needed")
    else:
        log("\n✨ No new components to migrate (all up to date)")

    # Save report
    report = {
        'awesome_agents': awesome_count,
        'guide_agents': guide_count,
        'total': total,
        'new_agents': all_new_agents
    }
    save_migration_report(report)

if __name__ == '__main__':
    main()
