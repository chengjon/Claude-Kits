#!/usr/bin/env python3
"""
快速冲突检查工具

在安装前快速检查目标项目中是否存在冲突文件。
不执行任何安装操作，只显示冲突报告。

使用方法:
    python scripts/check_conflicts.py /path/to/target/project
"""

import sys
from pathlib import Path
from typing import List, Tuple

class Color:
    """终端颜色"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def check_conflicts(target_dir: Path) -> Tuple[List[Path], List[Path]]:
    """
    检查冲突文件

    Returns:
        (conflicts, missing) - 冲突的文件列表和缺失的文件列表
    """
    source_dir = Path(__file__).parent.parent.resolve()
    target_claude = target_dir / '.claude'

    conflicts = []
    missing = []

    # 检查的组件
    checks = [
        # Agents
        ('agents', '*.md'),
        # Hooks
        ('hooks', '*.sh'),
        # Commands
        ('commands', '*.md'),
    ]

    for component, pattern in checks:
        source_path = source_dir / '.claude' / component
        if not source_path.exists():
            continue

        for source_file in source_path.glob(pattern):
            target_file = target_claude / component / source_file.name
            if target_file.exists():
                conflicts.append(target_file)
            else:
                missing.append(target_file)

    # 检查 Skills (目录)
    source_skills = source_dir / '.claude' / 'skills'
    if source_skills.exists():
        for skill_dir in source_skills.iterdir():
            if skill_dir.is_dir():
                target_skill = target_claude / 'skills' / skill_dir.name
                if target_skill.exists():
                    conflicts.append(target_skill)
                else:
                    missing.append(target_skill)

    # 检查配置文件
    configs = ['settings.json', 'skill-rules.json', 'build-checker.json']
    for config in configs:
        source_config = source_dir / '.claude' / config
        if source_config.exists():
            target_config = target_claude / config
            if target_config.exists():
                conflicts.append(target_config)
            else:
                missing.append(target_config)

    return conflicts, missing

def display_report(target_dir: Path, conflicts: List[Path], missing: List[Path]):
    """显示冲突报告"""
    print()
    print(f"{Color.BOLD}{'=' * 60}{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}🔍 Reddit-Case 冲突检查报告{Color.RESET}")
    print(f"{Color.BOLD}{'=' * 60}{Color.RESET}")
    print()
    print(f"{Color.BOLD}目标目录:{Color.RESET} {target_dir}")
    print()

    # 显示冲突
    if conflicts:
        print(f"{Color.BOLD}{Color.YELLOW}⚠️  发现 {len(conflicts)} 个冲突{Color.RESET}")
        print()
        print(f"{Color.YELLOW}以下文件/目录已存在于目标项目中:{Color.RESET}")
        for i, conflict in enumerate(conflicts, 1):
            rel_path = conflict.relative_to(target_dir)
            file_type = "目录" if conflict.is_dir() else "文件"
            print(f"  {i}. {Color.RED}{rel_path}{Color.RESET} ({file_type})")
        print()
        print(f"{Color.YELLOW}建议:{Color.RESET}")
        print(f"  1. 安装时选择 'skip' 保留这些文件")
        print(f"  2. 手动备份这些文件后选择 'backup'")
        print(f"  3. 安装时选择 'rename' 然后手动对比合并")
        print()
    else:
        print(f"{Color.GREEN}✅ 没有冲突 - 可以安全安装{Color.RESET}")
        print()

    # 显示将要安装的文件
    if missing:
        print(f"{Color.BOLD}{Color.GREEN}📦 将要安装 {len(missing)} 个新组件{Color.RESET}")
        print()
        print(f"{Color.GREEN}以下是将要安装的新文件/目录:{Color.RESET}")
        for i, item in enumerate(missing[:10], 1):  # 只显示前 10 个
            rel_path = item.relative_to(target_dir)
            file_type = "目录" if item.suffix == '' else "文件"
            print(f"  {i}. {Color.GREEN}{rel_path}{Color.RESET} ({file_type})")

        if len(missing) > 10:
            print(f"  ... 还有 {len(missing) - 10} 个文件/目录")
        print()

    # 安装命令
    print(f"{Color.BOLD}{'=' * 60}{Color.RESET}")
    print(f"{Color.BOLD}下一步:{Color.RESET}")
    print()
    if conflicts:
        print(f"{Color.YELLOW}存在冲突，建议先预览安装:{Color.RESET}")
        print(f"  {Color.CYAN}python scripts/install_reddit_case.py {target_dir} --dry-run{Color.RESET}")
        print()
        print(f"{Color.YELLOW}确认无误后执行安装:{Color.RESET}")
        print(f"  {Color.CYAN}python scripts/install_reddit_case.py {target_dir}{Color.RESET}")
    else:
        print(f"{Color.GREEN}没有冲突，可以直接安装:{Color.RESET}")
        print(f"  {Color.CYAN}python scripts/install_reddit_case.py {target_dir}{Color.RESET}")
    print()
    print(f"{Color.BOLD}{'=' * 60}{Color.RESET}")
    print()

def main():
    if len(sys.argv) != 2:
        print(f"{Color.RED}错误: 缺少目标目录参数{Color.RESET}")
        print()
        print(f"使用方法:")
        print(f"  python scripts/check_conflicts.py /path/to/target/project")
        print()
        sys.exit(1)

    target_dir = Path(sys.argv[1]).resolve()

    if not target_dir.exists():
        print(f"{Color.RED}错误: 目标目录不存在: {target_dir}{Color.RESET}")
        sys.exit(1)

    conflicts, missing = check_conflicts(target_dir)
    display_report(target_dir, conflicts, missing)

    # 返回状态码：0 = 无冲突，1 = 有冲突
    sys.exit(1 if conflicts else 0)

if __name__ == '__main__':
    main()
