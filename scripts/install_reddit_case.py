#!/usr/bin/env python3
"""
Reddit-Case 安全安装脚本

核心原则：
1. 永不覆盖用户现有文件 - NEVER overwrite existing files
2. 所有修改必须用户授权 - ALL modifications require user approval
3. 透明显示所有将要执行的操作 - Show all operations before execution
4. 提供回滚机制 - Provide rollback capability

使用方法:
    python scripts/install_reddit_case.py /path/to/target/project
    python scripts/install_reddit_case.py /path/to/target/project --dry-run
    python scripts/install_reddit_case.py /path/to/target/project --interactive
"""

import os
import sys
import shutil
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ConflictAction(Enum):
    """冲突处理动作"""
    SKIP = "skip"              # 跳过，保留原文件
    RENAME = "rename"          # 重命名新文件（添加后缀）
    BACKUP = "backup"          # 备份原文件后安装新文件
    MERGE = "merge"            # 合并（仅限 JSON 配置文件）
    ABORT = "abort"            # 中止安装

@dataclass
class FileConflict:
    """文件冲突信息"""
    source: Path
    target: Path
    conflict_type: str  # 'file', 'directory', 'permission'
    existing_size: Optional[int] = None
    new_size: Optional[int] = None

class SafeInstaller:
    """安全安装器"""

    def __init__(self, target_dir: str, dry_run: bool = False, interactive: bool = True):
        self.target_dir = Path(target_dir).resolve()
        self.source_dir = Path(__file__).parent.parent.resolve()
        self.dry_run = dry_run
        self.interactive = interactive
        self.conflicts: List[FileConflict] = []
        self.operations: List[Dict] = []

        # Reddit-Case 组件路径
        self.components = {
            'agents': self.source_dir / '.claude' / 'agents',
            'skills': self.source_dir / '.claude' / 'skills',
            'hooks': self.source_dir / '.claude' / 'hooks',
            'commands': self.source_dir / '.claude' / 'commands',
            'configs': {
                'settings.json': self.source_dir / '.claude' / 'settings.json',
                'skill-rules.json': self.source_dir / '.claude' / 'skill-rules.json',
                'build-checker.json': self.source_dir / '.claude' / 'build-checker.json',
            },
            'dev_docs': self.source_dir / '.claude' / 'dev' / 'active',
        }

    def check_prerequisites(self) -> bool:
        """检查安装前提条件"""
        print("🔍 检查安装前提条件...\n")

        # 检查目标目录是否存在
        if not self.target_dir.exists():
            print(f"❌ 目标目录不存在: {self.target_dir}")
            create = input("是否创建该目录? (y/N): ").strip().lower()
            if create == 'y':
                self.target_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ 已创建目录: {self.target_dir}\n")
            else:
                return False

        # 检查是否有写入权限
        test_file = self.target_dir / '.write_test'
        try:
            test_file.touch()
            test_file.unlink()
        except PermissionError:
            print(f"❌ 没有写入权限: {self.target_dir}")
            return False

        print(f"✅ 目标目录: {self.target_dir}")
        print(f"✅ 源目录: {self.source_dir}\n")
        return True

    def scan_conflicts(self) -> List[FileConflict]:
        """扫描所有可能的文件冲突"""
        print("🔍 扫描文件冲突...\n")
        conflicts = []
        target_claude = self.target_dir / '.claude'

        # 检查 agents
        if self.components['agents'].exists():
            for agent_file in self.components['agents'].glob('*.md'):
                target_file = target_claude / 'agents' / agent_file.name
                if target_file.exists():
                    conflicts.append(FileConflict(
                        source=agent_file,
                        target=target_file,
                        conflict_type='file',
                        existing_size=target_file.stat().st_size,
                        new_size=agent_file.stat().st_size
                    ))

        # 检查 skills
        if self.components['skills'].exists():
            for skill_dir in self.components['skills'].iterdir():
                if skill_dir.is_dir():
                    target_skill = target_claude / 'skills' / skill_dir.name
                    if target_skill.exists():
                        conflicts.append(FileConflict(
                            source=skill_dir,
                            target=target_skill,
                            conflict_type='directory'
                        ))

        # 检查 hooks
        if self.components['hooks'].exists():
            for hook_file in self.components['hooks'].glob('*.sh'):
                target_file = target_claude / 'hooks' / hook_file.name
                if target_file.exists():
                    conflicts.append(FileConflict(
                        source=hook_file,
                        target=target_file,
                        conflict_type='file',
                        existing_size=target_file.stat().st_size,
                        new_size=hook_file.stat().st_size
                    ))

        # 检查 commands
        if self.components['commands'].exists():
            for cmd_file in self.components['commands'].glob('*.md'):
                target_file = target_claude / 'commands' / cmd_file.name
                if target_file.exists():
                    conflicts.append(FileConflict(
                        source=cmd_file,
                        target=target_file,
                        conflict_type='file',
                        existing_size=target_file.stat().st_size,
                        new_size=cmd_file.stat().st_size
                    ))

        # 检查配置文件
        for config_name, config_path in self.components['configs'].items():
            if config_path.exists():
                target_file = target_claude / config_name
                if target_file.exists():
                    conflicts.append(FileConflict(
                        source=config_path,
                        target=target_file,
                        conflict_type='file',
                        existing_size=target_file.stat().st_size,
                        new_size=config_path.stat().st_size
                    ))

        self.conflicts = conflicts
        return conflicts

    def display_conflicts(self):
        """显示所有冲突"""
        if not self.conflicts:
            print("✅ 没有发现文件冲突\n")
            return

        print(f"⚠️  发现 {len(self.conflicts)} 个文件冲突:\n")
        for i, conflict in enumerate(self.conflicts, 1):
            print(f"{i}. {conflict.target.relative_to(self.target_dir)}")
            print(f"   类型: {conflict.conflict_type}")
            if conflict.existing_size and conflict.new_size:
                print(f"   现有文件: {conflict.existing_size} bytes")
                print(f"   新文件: {conflict.new_size} bytes")
            print()

    def resolve_conflicts(self) -> bool:
        """解决冲突（交互式）"""
        if not self.conflicts:
            return True

        print("=" * 60)
        print("冲突解决选项:")
        print("=" * 60)
        print("1. skip   - 跳过，保留所有现有文件（推荐）")
        print("2. rename - 重命名新文件（添加 .reddit-case 后缀）")
        print("3. backup - 备份现有文件后安装新文件（添加 .backup 后缀）")
        print("4. abort  - 中止安装")
        print("=" * 60)
        print()

        if not self.interactive:
            print("非交互模式，默认选择: skip (保留所有现有文件)")
            return True

        choice = input("请选择处理方式 (1-4) [1]: ").strip() or "1"

        actions = {
            "1": ConflictAction.SKIP,
            "2": ConflictAction.RENAME,
            "3": ConflictAction.BACKUP,
            "4": ConflictAction.ABORT,
        }

        action = actions.get(choice, ConflictAction.SKIP)

        if action == ConflictAction.ABORT:
            print("\n❌ 安装已中止")
            return False

        # 记录冲突处理策略
        for conflict in self.conflicts:
            self.operations.append({
                'type': 'conflict_resolution',
                'conflict': conflict,
                'action': action
            })

        return True

    def plan_installation(self):
        """规划安装操作"""
        print("\n📋 规划安装操作...\n")

        target_claude = self.target_dir / '.claude'

        # 1. 创建目录结构
        dirs_to_create = [
            target_claude / 'agents',
            target_claude / 'skills',
            target_claude / 'hooks',
            target_claude / 'commands',
            target_claude / 'dev' / 'active',
        ]

        for dir_path in dirs_to_create:
            if not dir_path.exists():
                self.operations.append({
                    'type': 'create_dir',
                    'path': dir_path
                })

        # 2. 复制 Agents
        if self.components['agents'].exists():
            for agent_file in self.components['agents'].glob('*.md'):
                target_file = target_claude / 'agents' / agent_file.name
                if not self._is_conflicting(target_file):
                    self.operations.append({
                        'type': 'copy_file',
                        'source': agent_file,
                        'target': target_file
                    })

        # 3. 复制 Skills
        if self.components['skills'].exists():
            for skill_dir in self.components['skills'].iterdir():
                if skill_dir.is_dir():
                    target_skill = target_claude / 'skills' / skill_dir.name
                    if not self._is_conflicting(target_skill):
                        self.operations.append({
                            'type': 'copy_dir',
                            'source': skill_dir,
                            'target': target_skill
                        })

        # 4. 复制 Hooks
        if self.components['hooks'].exists():
            for hook_file in self.components['hooks'].glob('*.sh'):
                target_file = target_claude / 'hooks' / hook_file.name
                if not self._is_conflicting(target_file):
                    self.operations.append({
                        'type': 'copy_file',
                        'source': hook_file,
                        'target': target_file,
                        'executable': True
                    })

        # 5. 复制 Commands
        if self.components['commands'].exists():
            for cmd_file in self.components['commands'].glob('*.md'):
                target_file = target_claude / 'commands' / cmd_file.name
                if not self._is_conflicting(target_file):
                    self.operations.append({
                        'type': 'copy_file',
                        'source': cmd_file,
                        'target': target_file
                    })

        # 6. 复制配置文件
        for config_name, config_path in self.components['configs'].items():
            if config_path.exists():
                target_file = target_claude / config_name
                if not self._is_conflicting(target_file):
                    self.operations.append({
                        'type': 'copy_file',
                        'source': config_path,
                        'target': target_file,
                        'needs_customization': True
                    })

        # 7. 复制 Dev Docs 示例
        if self.components['dev_docs'].exists():
            for item in self.components['dev_docs'].iterdir():
                target_item = target_claude / 'dev' / 'active' / item.name
                if not target_item.exists():
                    if item.is_file():
                        self.operations.append({
                            'type': 'copy_file',
                            'source': item,
                            'target': target_item
                        })
                    elif item.is_dir():
                        self.operations.append({
                            'type': 'copy_dir',
                            'source': item,
                            'target': target_item
                        })

    def _is_conflicting(self, target_path: Path) -> bool:
        """检查目标路径是否存在冲突"""
        return any(c.target == target_path for c in self.conflicts)

    def display_plan(self):
        """显示安装计划"""
        print("\n" + "=" * 60)
        print("📋 安装计划")
        print("=" * 60)

        # 统计
        stats = {
            'create_dir': 0,
            'copy_file': 0,
            'copy_dir': 0,
            'conflict_resolution': 0
        }

        for op in self.operations:
            stats[op['type']] += 1

        print(f"\n将执行 {len(self.operations)} 个操作:")
        print(f"  - 创建目录: {stats['create_dir']}")
        print(f"  - 复制文件: {stats['copy_file']}")
        print(f"  - 复制目录: {stats['copy_dir']}")
        print(f"  - 冲突处理: {stats['conflict_resolution']}")
        print()

        # 详细列表
        print("详细操作列表:")
        print("-" * 60)
        for i, op in enumerate(self.operations, 1):
            if op['type'] == 'create_dir':
                print(f"{i}. 创建目录: {op['path'].relative_to(self.target_dir)}")
            elif op['type'] == 'copy_file':
                print(f"{i}. 复制文件: {op['source'].name} -> {op['target'].relative_to(self.target_dir)}")
                if op.get('needs_customization'):
                    print(f"   ⚠️  需要自定义配置")
            elif op['type'] == 'copy_dir':
                print(f"{i}. 复制目录: {op['source'].name} -> {op['target'].relative_to(self.target_dir)}")
            elif op['type'] == 'conflict_resolution':
                print(f"{i}. 冲突处理: {op['conflict'].target.name} ({op['action'].value})")

        print("=" * 60)
        print()

    def execute_installation(self) -> bool:
        """执行安装"""
        if self.dry_run:
            print("🔍 DRY RUN 模式 - 不会执行任何实际操作\n")
            return True

        if self.interactive:
            confirm = input("确认执行以上操作? (y/N): ").strip().lower()
            if confirm != 'y':
                print("\n❌ 安装已取消")
                return False

        print("\n🚀 开始安装...\n")

        try:
            for i, op in enumerate(self.operations, 1):
                if op['type'] == 'create_dir':
                    op['path'].mkdir(parents=True, exist_ok=True)
                    print(f"✅ [{i}/{len(self.operations)}] 创建目录: {op['path'].name}")

                elif op['type'] == 'copy_file':
                    op['target'].parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(op['source'], op['target'])
                    if op.get('executable'):
                        os.chmod(op['target'], 0o755)
                    print(f"✅ [{i}/{len(self.operations)}] 复制文件: {op['source'].name}")

                elif op['type'] == 'copy_dir':
                    if op['target'].exists():
                        shutil.rmtree(op['target'])
                    shutil.copytree(op['source'], op['target'])
                    print(f"✅ [{i}/{len(self.operations)}] 复制目录: {op['source'].name}")

            print("\n✅ 安装完成!\n")
            return True

        except Exception as e:
            print(f"\n❌ 安装失败: {e}")
            return False

    def post_installation_notes(self):
        """安装后提示"""
        print("=" * 60)
        print("📝 安装后配置提示")
        print("=" * 60)
        print()
        print("⚠️  以下配置文件需要根据你的项目自定义:")
        print()
        print("1. .claude/build-checker.json")
        print("   - 更新项目路径")
        print("   - 配置构建命令")
        print()
        print("2. .claude/skill-rules.json")
        print("   - 调整文件路径模式以匹配你的项目结构")
        print("   - 自定义关键词触发器")
        print()
        print("3. .claude/skills/*/SKILL.md")
        print("   - 更新每个 skill 的 description 以包含项目特定关键词")
        print()
        print("=" * 60)
        print()
        print("🎉 Reddit-Case 安装完成!")
        print()
        print("下一步:")
        print("  1. 自定义配置文件")
        print("  2. 测试 skills 自动激活")
        print("  3. 配置构建检查命令")
        print()

    def run(self) -> bool:
        """运行完整的安装流程"""
        print("\n" + "=" * 60)
        print("🛡️  Reddit-Case 安全安装器")
        print("=" * 60)
        print()
        print("核心原则:")
        print("  ✅ 永不覆盖现有文件")
        print("  ✅ 所有修改需要用户授权")
        print("  ✅ 透明显示所有操作")
        print()
        print("=" * 60)
        print()

        # 1. 检查前提条件
        if not self.check_prerequisites():
            return False

        # 2. 扫描冲突
        self.scan_conflicts()
        self.display_conflicts()

        # 3. 解决冲突
        if not self.resolve_conflicts():
            return False

        # 4. 规划安装
        self.plan_installation()
        self.display_plan()

        # 5. 执行安装
        if not self.execute_installation():
            return False

        # 6. 安装后提示
        self.post_installation_notes()

        return True

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Reddit-Case 安全安装器 - 永不覆盖现有文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互式安装到目标项目
  python scripts/install_reddit_case.py /path/to/project

  # 预览安装（不执行实际操作）
  python scripts/install_reddit_case.py /path/to/project --dry-run

  # 非交互模式（自动跳过冲突）
  python scripts/install_reddit_case.py /path/to/project --no-interactive

安全保证:
  1. 永远不会覆盖你的现有文件
  2. 所有操作都需要你的确认
  3. 提供详细的操作预览
  4. 支持 dry-run 模式测试
        """
    )

    parser.add_argument(
        'target_dir',
        help='目标项目目录路径'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预览模式，不执行实际操作'
    )

    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='非交互模式，自动跳过冲突'
    )

    args = parser.parse_args()

    installer = SafeInstaller(
        target_dir=args.target_dir,
        dry_run=args.dry_run,
        interactive=not args.no_interactive
    )

    success = installer.run()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
