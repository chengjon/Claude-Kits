#!/usr/bin/env python3
"""
组件扫描器和合规性检查工具

功能:
1. 扫描 components 目录检测新增文件
2. 验证组件是否符合 Claude Code 官方规范
3. 自动修正不合规组件
4. 更新组件注册表 (components_registry.json)

规范要求:
- Agents: 必须包含 YAML frontmatter (name, description, model)
- Skills: 必须包含 YAML frontmatter，主文件 < 500 行
- Commands: 推荐包含 YAML frontmatter (description, allowed-tools)
- Hooks: 必须有执行权限
"""

import os
import sys
import json
import yaml
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import shutil

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
COMPONENTS_DIR = PROJECT_ROOT / "components"
REGISTRY_FILE = PROJECT_ROOT / "components_registry.json"
BACKUP_DIR = PROJECT_ROOT / ".backups"


class ComponentScanner:
    """组件扫描器"""

    def __init__(self):
        self.components_dir = COMPONENTS_DIR
        self.registry_file = REGISTRY_FILE
        self.backup_dir = BACKUP_DIR
        self.registry = self.load_registry()

    def load_registry(self) -> Dict:
        """加载组件注册表"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "last_scan": None,
                "components": {
                    "agents": {},
                    "commands": {},
                    "skills": {},
                    "hooks": {}
                },
                "metadata": {
                    "total_agents": 0,
                    "total_commands": 0,
                    "total_skills": 0,
                    "total_hooks": 0
                }
            }

    def save_registry(self):
        """保存组件注册表（带备份）"""
        # 备份旧文件
        if self.registry_file.exists():
            self.backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"components_registry_{timestamp}.json"
            shutil.copy2(self.registry_file, backup_file)
            print(f"✓ 备份注册表到: {backup_file}")

        # 保存新文件
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
        print(f"✓ 注册表已更新: {self.registry_file}")

    def calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def scan_agents(self) -> Tuple[List[Path], List[Path]]:
        """扫描 Agents 目录"""
        agents_dir = self.components_dir / "agents"
        if not agents_dir.exists():
            return [], []

        new_files = []
        modified_files = []
        current_agents = {}

        for agent_file in agents_dir.glob("*.md"):
            file_hash = self.calculate_file_hash(agent_file)
            agent_name = agent_file.stem

            current_agents[agent_name] = {
                "file": agent_file.name,
                "path": str(agent_file.relative_to(PROJECT_ROOT)),
                "hash": file_hash
            }

            if agent_name not in self.registry["components"]["agents"]:
                new_files.append(agent_file)
            elif self.registry["components"]["agents"][agent_name]["hash"] != file_hash:
                modified_files.append(agent_file)

        # 更新当前列表（保留元数据）
        for agent_name, info in current_agents.items():
            if agent_name in self.registry["components"]["agents"]:
                # 保留已有的元数据
                self.registry["components"]["agents"][agent_name].update(info)
            else:
                self.registry["components"]["agents"][agent_name] = info

        return new_files, modified_files

    def scan_commands(self) -> Tuple[List[Path], List[Path]]:
        """扫描 Commands 目录"""
        commands_dir = self.components_dir / "commands"
        if not commands_dir.exists():
            return [], []

        new_files = []
        modified_files = []
        current_commands = {}

        for command_file in commands_dir.glob("*.md"):
            file_hash = self.calculate_file_hash(command_file)
            command_name = command_file.stem

            current_commands[command_name] = {
                "file": command_file.name,
                "path": str(command_file.relative_to(PROJECT_ROOT)),
                "hash": file_hash
            }

            if command_name not in self.registry["components"]["commands"]:
                new_files.append(command_file)
            elif self.registry["components"]["commands"][command_name]["hash"] != file_hash:
                modified_files.append(command_file)

        for command_name, info in current_commands.items():
            if command_name in self.registry["components"]["commands"]:
                self.registry["components"]["commands"][command_name].update(info)
            else:
                self.registry["components"]["commands"][command_name] = info

        return new_files, modified_files

    def scan_skills(self) -> Tuple[List[Path], List[Path]]:
        """扫描 Skills 目录"""
        skills_dir = self.components_dir / "skills"
        if not skills_dir.exists():
            return [], []

        new_files = []
        modified_files = []
        current_skills = {}

        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            file_hash = self.calculate_file_hash(skill_file)
            skill_name = skill_dir.name

            current_skills[skill_name] = {
                "dir": skill_dir.name,
                "path": str(skill_dir.relative_to(PROJECT_ROOT)),
                "hash": file_hash
            }

            if skill_name not in self.registry["components"]["skills"]:
                new_files.append(skill_file)
            elif self.registry["components"]["skills"][skill_name]["hash"] != file_hash:
                modified_files.append(skill_file)

        for skill_name, info in current_skills.items():
            if skill_name in self.registry["components"]["skills"]:
                self.registry["components"]["skills"][skill_name].update(info)
            else:
                self.registry["components"]["skills"][skill_name] = info

        return new_files, modified_files

    def scan_all(self) -> Dict:
        """扫描所有组件"""
        print("="*70)
        print("开始扫描组件目录...")
        print("="*70)

        results = {
            "agents": {"new": [], "modified": []},
            "commands": {"new": [], "modified": []},
            "skills": {"new": [], "modified": []}
        }

        # 扫描各类组件
        results["agents"]["new"], results["agents"]["modified"] = self.scan_agents()
        results["commands"]["new"], results["commands"]["modified"] = self.scan_commands()
        results["skills"]["new"], results["skills"]["modified"] = self.scan_skills()

        # 更新元数据
        self.registry["metadata"]["total_agents"] = len(self.registry["components"]["agents"])
        self.registry["metadata"]["total_commands"] = len(self.registry["components"]["commands"])
        self.registry["metadata"]["total_skills"] = len(self.registry["components"]["skills"])
        self.registry["last_scan"] = datetime.now().isoformat()

        return results


class ComponentValidator:
    """组件合规性验证器"""

    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []

    def extract_frontmatter(self, content: str) -> Tuple[Optional[Dict], str]:
        """提取 YAML frontmatter"""
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(frontmatter_pattern, content, re.DOTALL)

        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1))
                body = match.group(2)
                return frontmatter, body
            except yaml.YAMLError:
                return None, content
        return None, content

    def validate_agent(self, file_path: Path) -> Tuple[bool, List[str]]:
        """验证 Agent 文件"""
        issues = []
        content = file_path.read_text(encoding='utf-8')
        frontmatter, body = self.extract_frontmatter(content)

        # 检查 frontmatter
        if not frontmatter:
            issues.append("缺少 YAML frontmatter")
        else:
            # 检查必需字段
            if 'name' not in frontmatter:
                issues.append("frontmatter 缺少 'name' 字段")
            if 'description' not in frontmatter:
                issues.append("frontmatter 缺少 'description' 字段")
            if 'model' not in frontmatter:
                issues.append("frontmatter 缺少 'model' 字段（推荐: sonnet）")

        return len(issues) == 0, issues

    def validate_skill(self, skill_dir: Path) -> Tuple[bool, List[str]]:
        """验证 Skill 目录"""
        issues = []
        skill_file = skill_dir / "SKILL.md"

        if not skill_file.exists():
            issues.append("缺少 SKILL.md 主文件")
            return False, issues

        content = skill_file.read_text(encoding='utf-8')
        frontmatter, body = self.extract_frontmatter(content)

        # 检查 frontmatter
        if not frontmatter:
            issues.append("SKILL.md 缺少 YAML frontmatter")
        else:
            if 'name' not in frontmatter:
                issues.append("frontmatter 缺少 'name' 字段")
            if 'description' not in frontmatter:
                issues.append("frontmatter 缺少 'description' 字段")

        # 检查 500 行规则
        lines = content.split('\n')
        if len(lines) > 500:
            issues.append(f"SKILL.md 超过 500 行 (当前: {len(lines)} 行)")

        return len(issues) == 0, issues

    def validate_command(self, file_path: Path) -> Tuple[bool, List[str]]:
        """验证 Command 文件"""
        issues = []
        content = file_path.read_text(encoding='utf-8')
        frontmatter, body = self.extract_frontmatter(content)

        # Commands 的 frontmatter 是推荐但非必需
        if not frontmatter:
            issues.append("推荐添加 YAML frontmatter (description 字段)")

        return len(issues) == 0, issues

    def fix_agent(self, file_path: Path) -> bool:
        """自动修正 Agent 文件"""
        content = file_path.read_text(encoding='utf-8')
        frontmatter, body = self.extract_frontmatter(content)

        if not frontmatter:
            # 创建默认 frontmatter
            agent_name = file_path.stem
            new_frontmatter = {
                'name': agent_name,
                'description': f'{agent_name} agent - please update this description',
                'model': 'sonnet'
            }

            new_content = f"---\n{yaml.dump(new_frontmatter, allow_unicode=True)}---\n\n{content}"

            # 备份原文件
            backup_file = file_path.with_suffix('.md.bak')
            shutil.copy2(file_path, backup_file)

            # 写入新内容
            file_path.write_text(new_content, encoding='utf-8')
            self.fixes_applied.append(f"为 {file_path.name} 添加了 frontmatter（已备份）")
            return True
        else:
            # 补充缺失字段
            modified = False
            if 'name' not in frontmatter:
                frontmatter['name'] = file_path.stem
                modified = True
            if 'description' not in frontmatter:
                frontmatter['description'] = f"{frontmatter.get('name', file_path.stem)} - please update"
                modified = True
            if 'model' not in frontmatter:
                frontmatter['model'] = 'sonnet'
                modified = True

            if modified:
                backup_file = file_path.with_suffix('.md.bak')
                shutil.copy2(file_path, backup_file)

                new_content = f"---\n{yaml.dump(frontmatter, allow_unicode=True)}---\n\n{body}"
                file_path.write_text(new_content, encoding='utf-8')
                self.fixes_applied.append(f"补充 {file_path.name} 的 frontmatter 字段（已备份）")
                return True

        return False

    def fix_skill(self, skill_dir: Path) -> bool:
        """自动修正 Skill"""
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            return False

        content = skill_file.read_text(encoding='utf-8')
        frontmatter, body = self.extract_frontmatter(content)

        if not frontmatter:
            # 创建默认 frontmatter
            skill_name = skill_dir.name
            new_frontmatter = {
                'name': skill_name,
                'description': f'{skill_name} skill - please update this description'
            }

            new_content = f"---\n{yaml.dump(new_frontmatter, allow_unicode=True)}---\n\n{content}"

            backup_file = skill_file.with_suffix('.md.bak')
            shutil.copy2(skill_file, backup_file)

            skill_file.write_text(new_content, encoding='utf-8')
            self.fixes_applied.append(f"为 {skill_name}/SKILL.md 添加了 frontmatter（已备份）")
            return True
        else:
            modified = False
            if 'name' not in frontmatter:
                frontmatter['name'] = skill_dir.name
                modified = True
            if 'description' not in frontmatter:
                frontmatter['description'] = f"{frontmatter.get('name', skill_dir.name)} - please update"
                modified = True

            if modified:
                backup_file = skill_file.with_suffix('.md.bak')
                shutil.copy2(skill_file, backup_file)

                new_content = f"---\n{yaml.dump(frontmatter, allow_unicode=True)}---\n\n{body}"
                skill_file.write_text(new_content, encoding='utf-8')
                self.fixes_applied.append(f"补充 {skill_dir.name}/SKILL.md 的 frontmatter（已备份）")
                return True

        return False


def main():
    """主函数"""
    print("\n" + "="*70)
    print("Claude-Kits 组件扫描和合规性检查工具")
    print("="*70 + "\n")

    # 1. 扫描组件
    scanner = ComponentScanner()
    scan_results = scanner.scan_all()

    # 显示扫描结果
    print("\n扫描结果:")
    print(f"  Agents:   {len(scanner.registry['components']['agents'])} 个")
    print(f"    - 新增: {len(scan_results['agents']['new'])} 个")
    print(f"    - 修改: {len(scan_results['agents']['modified'])} 个")

    print(f"  Commands: {len(scanner.registry['components']['commands'])} 个")
    print(f"    - 新增: {len(scan_results['commands']['new'])} 个")
    print(f"    - 修改: {len(scan_results['commands']['modified'])} 个")

    print(f"  Skills:   {len(scanner.registry['components']['skills'])} 个")
    print(f"    - 新增: {len(scan_results['skills']['new'])} 个")
    print(f"    - 修改: {len(scan_results['skills']['modified'])} 个")

    # 2. 验证新增和修改的组件
    validator = ComponentValidator()
    issues_found = False

    print("\n" + "="*70)
    print("开始合规性检查...")
    print("="*70 + "\n")

    # 验证 Agents
    # 处理所有 agents，不仅是新增和修改的
    agents_to_validate = scan_results['agents']['new'] + scan_results['agents']['modified']

    # 同时处理已存在但缺少 description 的 agents
    for agent_name, agent_info in scanner.registry['components']['agents'].items():
        agent_file = COMPONENTS_DIR / "agents" / f"{agent_name}.md"

        # 如果缺少 description 且不在待验证列表中，加入列表
        if agent_file.exists() and agent_file not in agents_to_validate:
            if 'description' not in agent_info or not agent_info.get('description'):
                agents_to_validate.append(agent_file)

    for agent_file in agents_to_validate:
        is_valid, issues = validator.validate_agent(agent_file)
        if not is_valid:
            issues_found = True
            print(f"❌ {agent_file.name}:")
            for issue in issues:
                print(f"   - {issue}")

            # 尝试自动修正
            print(f"   尝试自动修正...")
            if validator.fix_agent(agent_file):
                print(f"   ✓ 已修正")
                # 提取元数据
                content = agent_file.read_text(encoding='utf-8')
                fm, _ = validator.extract_frontmatter(content)
                if fm:
                    agent_name = agent_file.stem
                    scanner.registry['components']['agents'][agent_name]['name'] = fm.get('name', agent_name)
                    scanner.registry['components']['agents'][agent_name]['description'] = fm.get('description', '')
                    scanner.registry['components']['agents'][agent_name]['model'] = fm.get('model', 'sonnet')
        else:
            # 提取元数据（即使已合规，也要确保 description 被提取）
            content = agent_file.read_text(encoding='utf-8')
            fm, _ = validator.extract_frontmatter(content)
            if fm:
                agent_name = agent_file.stem
                scanner.registry['components']['agents'][agent_name]['name'] = fm.get('name', agent_name)
                scanner.registry['components']['agents'][agent_name]['description'] = fm.get('description', '')
                scanner.registry['components']['agents'][agent_name]['model'] = fm.get('model', 'sonnet')
            print(f"✓ {agent_file.name} - 合规")

    # 验证 Commands
    # 处理所有 commands，不仅是新增和修改的
    commands_to_validate = scan_results['commands']['new'] + scan_results['commands']['modified']

    # 同时处理已存在但缺少 description 的 commands
    for command_name, command_info in scanner.registry['components']['commands'].items():
        command_file = COMPONENTS_DIR / "commands" / f"{command_name}.md"

        # 如果缺少 description 且不在待验证列表中，加入列表
        if command_file.exists() and command_file not in commands_to_validate:
            if 'description' not in command_info or not command_info.get('description'):
                commands_to_validate.append(command_file)

    for command_file in commands_to_validate:
        is_valid, issues = validator.validate_command(command_file)
        if not is_valid:
            print(f"⚠ {command_file.name}:")
            for issue in issues:
                print(f"   - {issue}")

        # 提取元数据（总是提取，确保 description 被更新）
        content = command_file.read_text(encoding='utf-8')
        fm, _ = validator.extract_frontmatter(content)
        command_name = command_file.stem
        if fm:
            scanner.registry['components']['commands'][command_name]['description'] = fm.get('description', '')
        else:
            scanner.registry['components']['commands'][command_name]['description'] = ''

        if is_valid:
            print(f"✓ {command_file.name} - 合规")

    # 验证 Skills
    # 处理所有技能，不仅是新增和修改的
    skills_to_validate = scan_results['skills']['new'] + scan_results['skills']['modified']

    # 同时处理已存在但缺少 description 的技能
    for skill_name, skill_info in scanner.registry['components']['skills'].items():
        skill_dir = COMPONENTS_DIR / "skills" / skill_name
        skill_file = skill_dir / "SKILL.md"

        # 如果缺少 description 且不在待验证列表中，加入列表
        if skill_file.exists() and skill_file not in skills_to_validate:
            if 'description' not in skill_info or not skill_info.get('description'):
                skills_to_validate.append(skill_file)

    for skill_file in skills_to_validate:
        skill_dir = skill_file.parent
        is_valid, issues = validator.validate_skill(skill_dir)
        if not is_valid:
            issues_found = True
            print(f"❌ {skill_dir.name}/SKILL.md:")
            for issue in issues:
                print(f"   - {issue}")

            # 尝试自动修正
            print(f"   尝试自动修正...")
            if validator.fix_skill(skill_dir):
                print(f"   ✓ 已修正")
                # 提取元数据
                content = skill_file.read_text(encoding='utf-8')
                fm, _ = validator.extract_frontmatter(content)
                if fm:
                    skill_name = skill_dir.name
                    scanner.registry['components']['skills'][skill_name]['name'] = fm.get('name', skill_name)
                    scanner.registry['components']['skills'][skill_name]['description'] = fm.get('description', '')
        else:
            # 提取元数据（即使已合规，也要确保 description 被提取）
            content = skill_file.read_text(encoding='utf-8')
            fm, _ = validator.extract_frontmatter(content)
            if fm:
                skill_name = skill_dir.name
                scanner.registry['components']['skills'][skill_name]['name'] = fm.get('name', skill_name)
                scanner.registry['components']['skills'][skill_name]['description'] = fm.get('description', '')
            print(f"✓ {skill_dir.name}/SKILL.md - 合规")

    # 3. 保存注册表
    print("\n" + "="*70)
    scanner.save_registry()

    # 4. 显示修正摘要
    if validator.fixes_applied:
        print("\n" + "="*70)
        print("自动修正摘要:")
        print("="*70)
        for fix in validator.fixes_applied:
            print(f"  ✓ {fix}")
        print("\n⚠ 请检查自动生成的 frontmatter 并更新描述信息")

    print("\n" + "="*70)
    print("扫描和检查完成!")
    print("="*70 + "\n")

    return 0 if not issues_found else 1


if __name__ == "__main__":
    sys.exit(main())
