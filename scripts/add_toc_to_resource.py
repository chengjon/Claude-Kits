#!/usr/bin/env python3
"""
TOC Generator for Resource Files

Intelligently adds Table of Contents to large markdown resource files.
Follows established pattern from manual TOC additions.

Usage:
    python scripts/add_toc_to_resource.py <file_path>
    python scripts/add_toc_to_resource.py --batch  # Process all files >200 lines
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def extract_headings(content: str) -> List[Tuple[int, str, str]]:
    """
    Extract markdown headings, ignoring those inside code blocks.

    Returns: List of (level, text, anchor) tuples
    """
    headings = []
    in_code_block = False

    for line in content.split('\n'):
        # Track code block state
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue

        # Skip if inside code block
        if in_code_block:
            continue

        # Match markdown headers (## or ###)
        match = re.match(r'^(#{2,3})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()

            # Skip the title (single #)
            if level < 2:
                continue

            # Generate anchor (GitHub-style)
            anchor = text.lower()
            anchor = re.sub(r'[^\w\s-]', '', anchor)  # Remove special chars
            anchor = re.sub(r'[\s_]+', '-', anchor)    # Replace spaces with hyphens
            anchor = anchor.strip('-')

            headings.append((level, text, anchor))

    return headings


def generate_toc(headings: List[Tuple[int, str, str]]) -> str:
    """Generate TOC markdown from headings."""
    if not headings:
        return ""

    toc_lines = ["## 📑 Table of Contents", ""]

    for level, text, anchor in headings:
        indent = "  " * (level - 2)  # ## = no indent, ### = 2 spaces
        toc_lines.append(f"{indent}- [{text}](#{anchor})")

    toc_lines.append("")
    toc_lines.append("---")
    toc_lines.append("")

    return '\n'.join(toc_lines)


def has_toc(content: str) -> bool:
    """Check if file already has a TOC."""
    return '## 📑 Table of Contents' in content or '## Table of Contents' in content


def add_toc_to_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Add TOC to a markdown file.

    Returns: True if TOC was added, False otherwise
    """
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    content = file_path.read_text(encoding='utf-8')

    # Check if TOC already exists
    if has_toc(content):
        print(f"⏭️  {file_path.name} - TOC already exists")
        return False

    # Extract headings
    headings = extract_headings(content)

    if len(headings) < 3:
        print(f"⏭️  {file_path.name} - Too few sections ({len(headings)}), skipping")
        return False

    # Generate TOC
    toc = generate_toc(headings)

    # Find insertion point (after title and description, before first ##)
    lines = content.split('\n')
    insert_index = 0

    # Skip title (# Title)
    for i, line in enumerate(lines):
        if line.startswith('# '):
            insert_index = i + 1
            break

    # Skip blank lines and description
    while insert_index < len(lines) and (not lines[insert_index].strip() or not lines[insert_index].startswith('#')):
        insert_index += 1

    # Insert TOC
    new_content = '\n'.join(lines[:insert_index]) + '\n\n' + toc + '\n'.join(lines[insert_index:])

    if dry_run:
        print(f"🔍 {file_path.name} - Would add TOC with {len(headings)} sections")
        return True

    # Write back
    file_path.write_text(new_content, encoding='utf-8')
    line_count = len(lines)
    print(f"✅ {file_path.name} ({line_count} lines) - Added TOC with {len(headings)} sections")
    return True


def process_batch(resources_dir: Path, min_lines: int = 200, dry_run: bool = False):
    """Process all large resource files."""
    resource_files = []

    # Find all .md files except README.md
    for md_file in resources_dir.rglob('*.md'):
        if md_file.name == 'README.md':
            continue

        line_count = len(md_file.read_text(encoding='utf-8').splitlines())
        if line_count >= min_lines:
            resource_files.append((md_file, line_count))

    # Sort by line count (descending)
    resource_files.sort(key=lambda x: x[1], reverse=True)

    print(f"\n📊 Found {len(resource_files)} resource files with ≥{min_lines} lines\n")

    added_count = 0
    for file_path, line_count in resource_files:
        if add_toc_to_file(file_path, dry_run=dry_run):
            added_count += 1

    print(f"\n✅ Complete! Added TOC to {added_count}/{len(resource_files)} files")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_toc_to_resource.py <file_path>")
        print("       python scripts/add_toc_to_resource.py --batch [--dry-run]")
        sys.exit(1)

    if sys.argv[1] == '--batch':
        dry_run = '--dry-run' in sys.argv
        resources_dir = Path('/opt/claude/Claude-Kits/components/agents/resources')
        process_batch(resources_dir, min_lines=200, dry_run=dry_run)
    else:
        file_path = Path(sys.argv[1])
        dry_run = '--dry-run' in sys.argv
        add_toc_to_file(file_path, dry_run=dry_run)


if __name__ == '__main__':
    main()
