#!/usr/bin/env python3
"""
Universal Installer - 统一组件安装程序

核心原则：
1. 永不覆盖用户文件（除非明确授权）
2. 从 components/ 复制完整模板
3. 支持冲突检测和处理
4. 透明显示所有操作

支持的组件类型：
- skills: Agent Skills
- agents: Subagents
- hooks: Hooks (Shell/TypeScript scripts)
- commands: Slash Commands

使用方法：
    from universal_installer import UniversalInstaller

    installer = UniversalInstaller()
    installer.install_component(
        component_type='skills',
        component_name='task-planning-pro',
        target_dir='/path/to/project',
        scope='project'
    )
"""

import os
import sys
import shutil
import json
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

# 冲突处理动作
class ConflictAction(Enum):
    SKIP = "skip"              # 跳过，保留原文件
    RENAME = "rename"          # 重命名新文件（添加后缀）
    BACKUP = "backup"          # 备份原文件后安装新文件
    ABORT = "abort"            # 中止安装

# 组件类型
class ComponentType(Enum):
    SKILLS = "skills"
    AGENTS = "agents"
    HOOKS = "hooks"
    COMMANDS = "commands"

@dataclass
class FileConflict:
    """文件冲突信息"""
    source: Path
    target: Path
    conflict_type: str  # 'file', 'directory'
    existing_size: Optional[int] = None
    new_size: Optional[int] = None

@dataclass
class InstallOperation:
    """安装操作"""
    component_name: str
    source: Path
    target: Path
    component_type: str

class InstallPlan:
    """安装计划"""
    def __init__(self):
        self.operations: List[InstallOperation] = []
        self.conflicts: List[FileConflict] = []

    def add_operation(self, operation: InstallOperation):
        self.operations.append(operation)

    def add_conflict(self, conflict: FileConflict):
        self.conflicts.append(conflict)

    def count_operations(self) -> int:
        return len(self.operations)

    def count_conflicts(self) -> int:
        return len(self.conflicts)

    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

class UniversalInstaller:
    """统一组件安装程序"""

    def __init__(self, claude_kits_root: Optional[str] = None):
        """
        初始化安装程序

        Args:
            claude_kits_root: Claude-Kits 仓库根目录（如果为 None，自动检测）
        """
        if claude_kits_root:
            self.root_dir = Path(claude_kits_root).resolve()
        else:
            # 自动检测：假设此脚本在 scripts/ 目录下
            self.root_dir = Path(__file__).parent.parent.resolve()

        self.components_dir = self.root_dir / 'components'

        # 验证 components/ 目录存在
        if not self.components_dir.exists():
            raise FileNotFoundError(f"Components directory not found: {self.components_dir}")

    def get_source_path(self, component_type: str, component_name: str) -> Path:
        """
        获取组件的源路径

        Args:
            component_type: 组件类型 ('skills', 'agents', 'hooks', 'commands')
            component_name: 组件名称

        Returns:
            源路径 Path 对象
        """
        # Skills 是目录
        if component_type == 'skills':
            source = self.components_dir / component_type / component_name

        # Agents 是 .md 文件
        elif component_type == 'agents':
            source = self.components_dir / 'agents' / f"{component_name}.md"

        # Hooks 是 .sh 或 .ts 文件（支持子目录）
        elif component_type == 'hooks':
            # 尝试多种文件扩展名
            for ext in ['.sh', '.ts', '.js']:
                # 先在根目录查找
                source = self.components_dir / 'hooks' / f"{component_name}{ext}"
                if source.exists():
                    return source

                # 然后在子目录查找
                for subdir in (self.components_dir / 'hooks').glob('*'):
                    if subdir.is_dir():
                        source = subdir / f"{component_name}{ext}"
                        if source.exists():
                            return source

            # 如果都没找到，返回默认 .sh 路径（后续会报错）
            source = self.components_dir / 'hooks' / f"{component_name}.sh"

        # Commands 是 .md 文件
        elif component_type == 'commands':
            source = self.components_dir / 'commands' / f"{component_name}.md"

        else:
            raise ValueError(f"Unknown component type: {component_type}")

        return source

    def get_target_path(
        self,
        component_type: str,
        component_name: str,
        target_dir: str,
        scope: str = 'project'
    ) -> Path:
        """
        获取组件的目标路径

        Args:
            component_type: 组件类型
            component_name: 组件名称
            target_dir: 目标项目根目录
            scope: 作用域 ('user', 'project')

        Returns:
            目标路径 Path 对象
        """
        if scope == 'user':
            # 用户级：~/.claude/{component_type}/
            base_dir = Path.home() / '.claude'
        elif scope == 'project':
            # 项目级：{target_dir}/.claude/{component_type}/
            base_dir = Path(target_dir) / '.claude'
        else:
            raise ValueError(f"Unknown scope: {scope}")

        # Skills 是目录
        if component_type == 'skills':
            target = base_dir / component_type / component_name

        # Agents 是 .md 文件
        elif component_type == 'agents':
            target = base_dir / 'agents' / f"{component_name}.md"

        # Hooks 是文件（保留原扩展名）
        elif component_type == 'hooks':
            source = self.get_source_path(component_type, component_name)
            target = base_dir / 'hooks' / source.name

        # Commands 是 .md 文件
        elif component_type == 'commands':
            target = base_dir / 'commands' / f"{component_name}.md"

        else:
            raise ValueError(f"Unknown component type: {component_type}")

        return target

    def check_conflict(self, target_path: Path) -> bool:
        """检查目标路径是否已存在"""
        return target_path.exists()

    def handle_conflict(
        self,
        conflict: FileConflict,
        interactive: bool = True
    ) -> ConflictAction:
        """
        处理冲突

        Args:
            conflict: 冲突信息
            interactive: 是否交互式询问用户

        Returns:
            用户选择的冲突处理动作
        """
        if not interactive:
            return ConflictAction.SKIP  # 非交互模式默认跳过

        print(f"\n⚠️  冲突: {conflict.target} 已存在")
        print(f"   源: {conflict.source}")
        print(f"   目标: {conflict.target}")

        if conflict.existing_size:
            print(f"   现有大小: {conflict.existing_size} bytes")
        if conflict.new_size:
            print(f"   新大小: {conflict.new_size} bytes")

        print("\n选项:")
        print("  [s] skip    - 跳过，保留现有文件（推荐）")
        print("  [r] rename  - 重命名新文件（添加后缀）")
        print("  [b] backup  - 备份现有文件后安装新文件")
        print("  [a] abort   - 中止安装")

        while True:
            choice = input("\n你的选择 (s/r/b/a): ").strip().lower()

            if choice in ['s', 'skip', '']:
                return ConflictAction.SKIP
            elif choice in ['r', 'rename']:
                return ConflictAction.RENAME
            elif choice in ['b', 'backup']:
                return ConflictAction.BACKUP
            elif choice in ['a', 'abort']:
                return ConflictAction.ABORT
            else:
                print("无效选择，请重新输入")

    def generate_install_plan(
        self,
        component_type: str,
        component_name: str,
        target_dir: str,
        scope: str = 'project'
    ) -> InstallPlan:
        """生成安装计划"""
        plan = InstallPlan()

        source = self.get_source_path(component_type, component_name)
        target = self.get_target_path(component_type, component_name, target_dir, scope)

        # 检查源是否存在
        if not source.exists():
            raise FileNotFoundError(f"Source not found: {source}")

        # 检查冲突
        if self.check_conflict(target):
            conflict = FileConflict(
                source=source,
                target=target,
                conflict_type='directory' if source.is_dir() else 'file',
                existing_size=self._get_size(target) if target.exists() else None,
                new_size=self._get_size(source)
            )
            plan.add_conflict(conflict)
        else:
            operation = InstallOperation(
                component_name=component_name,
                source=source,
                target=target,
                component_type=component_type
            )
            plan.add_operation(operation)

        return plan

    def _get_size(self, path: Path) -> int:
        """获取文件或目录大小"""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            total = 0
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
            return total
        return 0

    def show_install_plan(self, plan: InstallPlan, component_name: str):
        """显示安装计划"""
        print(f"\n📋 安装计划: {component_name}")
        print("=" * 60)

        if plan.count_operations() > 0:
            print(f"\n✅ 将要安装 {plan.count_operations()} 个组件:")
            for op in plan.operations:
                print(f"  • {op.component_name}")
                print(f"    源: {op.source}")
                print(f"    目标: {op.target}")

        if plan.has_conflicts():
            print(f"\n⚠️  发现 {plan.count_conflicts()} 个冲突:")
            for conflict in plan.conflicts:
                print(f"  • {conflict.target.name}")
                print(f"    路径: {conflict.target}")
                print(f"    状态: 已存在")

    def execute_install_operation(
        self,
        operation: InstallOperation,
        dry_run: bool = False
    ) -> bool:
        """
        执行安装操作

        Args:
            operation: 安装操作
            dry_run: 是否为预览模式

        Returns:
            是否成功
        """
        if dry_run:
            print(f"  [DRY-RUN] 复制: {operation.source} → {operation.target}")
            return True

        try:
            # 创建目标父目录
            operation.target.parent.mkdir(parents=True, exist_ok=True)

            # 复制文件或目录
            if operation.source.is_dir():
                shutil.copytree(operation.source, operation.target, dirs_exist_ok=False)
                print(f"  ✅ 已安装目录: {operation.component_name}")
            else:
                shutil.copy2(operation.source, operation.target)
                print(f"  ✅ 已安装文件: {operation.component_name}")

                # 如果是 hook 脚本，设置可执行权限
                if operation.component_type == 'hooks' and operation.target.suffix == '.sh':
                    operation.target.chmod(0o755)
                    print(f"    ├─ 已设置可执行权限")

            return True

        except Exception as e:
            print(f"  ❌ 安装失败: {operation.component_name}")
            print(f"     错误: {e}")
            return False

    def validate_installation(
        self,
        component_type: str,
        component_name: str,
        target_path: Path
    ) -> bool:
        """
        验证安装是否成功

        Args:
            component_type: 组件类型
            component_name: 组件名称
            target_path: 目标路径

        Returns:
            是否验证通过
        """
        if not target_path.exists():
            print(f"  ❌ 验证失败: {target_path} 不存在")
            return False

        # Skills 和 Agents: 验证 YAML frontmatter
        if component_type in ['skills', 'agents']:
            main_file = target_path / 'SKILL.md' if component_type == 'skills' else target_path / f"{component_name}.md"

            # Agents 直接是 .md 文件
            if component_type == 'agents':
                main_file = target_path

            if not main_file.exists():
                print(f"  ❌ 验证失败: 主文件不存在 {main_file}")
                return False

            try:
                with open(main_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if not content.startswith('---'):
                    print(f"  ❌ 验证失败: 缺少 YAML frontmatter")
                    return False

                end = content.find('---', 3)
                if end == -1:
                    print(f"  ❌ 验证失败: YAML frontmatter 格式错误")
                    return False

                frontmatter = yaml.safe_load(content[3:end])

                # 检查必需字段
                if 'name' not in frontmatter:
                    print(f"  ❌ 验证失败: YAML 缺少 'name' 字段")
                    return False

                if 'description' not in frontmatter:
                    print(f"  ❌ 验证失败: YAML 缺少 'description' 字段")
                    return False

                print(f"  ✓ YAML frontmatter 验证通过")

            except yaml.YAMLError as e:
                print(f"  ❌ 验证失败: YAML 语法错误 - {e}")
                return False
            except Exception as e:
                print(f"  ❌ 验证失败: {e}")
                return False

        # Hooks: 验证文件权限
        elif component_type == 'hooks' and target_path.suffix == '.sh':
            is_executable = os.access(target_path, os.X_OK)
            if is_executable:
                print(f"  ✓ Hook 脚本可执行权限验证通过")
            else:
                print(f"  ⚠️  Hook 脚本不可执行，运行: chmod +x {target_path}")

        print(f"  ✅ 验证通过: {component_name}")
        return True

    def install_component(
        self,
        component_type: str,
        component_name: str,
        target_dir: str,
        scope: str = 'project',
        dry_run: bool = False,
        interactive: bool = True
    ) -> bool:
        """
        安装单个组件

        Args:
            component_type: 组件类型 ('skills', 'agents', 'hooks', 'commands')
            component_name: 组件名称（如 'task-planning-pro'）
            target_dir: 目标项目根目录
            scope: 作用域 ('user', 'project')
            dry_run: 是否为预览模式（不执行实际安装）
            interactive: 是否为交互模式（冲突时询问用户）

        Returns:
            是否安装成功
        """
        print(f"\n🚀 开始安装 {component_type}/{component_name}...")

        # 1. 生成安装计划
        try:
            plan = self.generate_install_plan(component_type, component_name, target_dir, scope)
        except FileNotFoundError as e:
            print(f"❌ 错误: {e}")
            return False
        except Exception as e:
            print(f"❌ 生成安装计划失败: {e}")
            return False

        # 2. 显示安装计划
        self.show_install_plan(plan, component_name)

        if dry_run:
            print("\n[yellow]Dry-run 模式：不会执行实际安装[/yellow]")
            return True

        # 3. 处理冲突
        if plan.has_conflicts():
            for conflict in plan.conflicts:
                action = self.handle_conflict(conflict, interactive)

                if action == ConflictAction.SKIP:
                    print(f"  ⏭️  跳过: {conflict.target.name}")
                    return False

                elif action == ConflictAction.RENAME:
                    # 重命名新文件
                    new_target = Path(str(conflict.target) + '.new')
                    operation = InstallOperation(
                        component_name=component_name,
                        source=conflict.source,
                        target=new_target,
                        component_type=component_type
                    )
                    plan.operations.append(operation)
                    print(f"  📝 将安装为: {new_target.name}")

                elif action == ConflictAction.BACKUP:
                    # 备份现有文件
                    backup_target = Path(str(conflict.target) + '.backup')
                    shutil.move(str(conflict.target), str(backup_target))
                    print(f"  💾 已备份至: {backup_target.name}")

                    # 添加安装操作
                    operation = InstallOperation(
                        component_name=component_name,
                        source=conflict.source,
                        target=conflict.target,
                        component_type=component_type
                    )
                    plan.operations.append(operation)

                elif action == ConflictAction.ABORT:
                    print("\n❌ 安装已中止")
                    return False

        # 4. 确认安装
        if interactive and plan.count_operations() > 0:
            print(f"\n📦 准备安装 {plan.count_operations()} 个组件")
            confirm = input("确认安装? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("安装已取消")
                return False

        # 5. 执行安装
        if plan.count_operations() == 0:
            print("\n⚠️  没有需要安装的组件")
            return False

        print(f"\n📦 执行安装...")
        success = True
        for operation in plan.operations:
            if not self.execute_install_operation(operation, dry_run):
                success = False

        # 6. 验证安装
        if success and not dry_run:
            print(f"\n✅ 验证安装...")
            target_path = self.get_target_path(component_type, component_name, target_dir, scope)
            self.validate_installation(component_type, component_name, target_path)

        # 7. 安装后提示
        if success:
            print(f"\n🎉 安装成功！")
            self._show_post_install_tips(component_type, component_name, target_dir, scope)
        else:
            print(f"\n❌ 安装过程中出现错误")

        return success

    def _show_post_install_tips(
        self,
        component_type: str,
        component_name: str,
        target_dir: str,
        scope: str
    ):
        """显示安装后提示"""
        print("\n📝 后续步骤:")

        if component_type == 'skills':
            print(f"  1. 重启 Claude Code 加载新 Skill")
            print(f"  2. 测试激活：根据 Skill 的 description 发送相关提示")
            print(f"  3. 可选：编辑 SKILL.md 的 description 添加项目特定关键词")

        elif component_type == 'agents':
            print(f"  1. 重启 Claude Code")
            print(f"  2. 使用 Task tool 调用: subagent_type=\"{component_name}\"")

        elif component_type == 'hooks':
            target_path = self.get_target_path(component_type, component_name, target_dir, scope)
            if target_path.suffix == '.sh':
                print(f"  1. 确保可执行权限: chmod +x {target_path}")
            print(f"  2. 在 .claude/settings.json 中配置 hook 事件")
            print(f"  3. 重启 Claude Code")

        elif component_type == 'commands':
            print(f"  1. 重启 Claude Code")
            print(f"  2. 使用命令: /{component_name}")

def main():
    """CLI 入口（供测试使用）"""
    import argparse

    parser = argparse.ArgumentParser(description='Universal Component Installer')
    parser.add_argument('component_type', choices=['skills', 'agents', 'hooks', 'commands'],
                       help='Component type')
    parser.add_argument('component_name', help='Component name')
    parser.add_argument('--target-dir', required=True, help='Target project directory')
    parser.add_argument('--scope', choices=['user', 'project'], default='project',
                       help='Installation scope')
    parser.add_argument('--dry-run', action='store_true', help='Preview mode (no actual installation)')
    parser.add_argument('--non-interactive', action='store_true', help='Non-interactive mode (skip conflicts)')

    args = parser.parse_args()

    installer = UniversalInstaller()
    success = installer.install_component(
        component_type=args.component_type,
        component_name=args.component_name,
        target_dir=args.target_dir,
        scope=args.scope,
        dry_run=args.dry_run,
        interactive=not args.non_interactive
    )

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
