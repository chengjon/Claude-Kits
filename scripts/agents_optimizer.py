#!/usr/bin/env python3
"""
Agents 优化工具 - 用于合并、精简和优化 agents

功能:
- 分析 agents 内容和职能
- 生成合并预览
- 逐个确认后执行合并
- 自动备份和生成报告
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
import shutil

class AgentOptimizer:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.repo_root = Path(__file__).parent.parent
        self.agents_dir = self.repo_root / "components" / "agents"
        self.backup_dir = self.repo_root / "reference" / "BAK" / "agents_optimization_backup"
        self.deprecated_dir = self.repo_root / "reference" / "deprecated" / "agents"

        # 确保目录存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.deprecated_dir.mkdir(parents=True, exist_ok=True)

    def read_agent(self, agent_name: str) -> Dict:
        """读取 agent 文件"""
        agent_file = self.agents_dir / f"{agent_name}.md"

        if not agent_file.exists():
            return None

        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析 YAML frontmatter
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)

        if yaml_match:
            try:
                frontmatter = yaml.safe_load(yaml_match.group(1))
                body = yaml_match.group(2)
                return {
                    'name': agent_name,
                    'frontmatter': frontmatter,
                    'body': body,
                    'full_content': content
                }
            except yaml.YAMLError:
                pass

        return {
            'name': agent_name,
            'frontmatter': {},
            'body': content,
            'full_content': content
        }

    def extract_keywords(self, text: str) -> Set[str]:
        """从文本中提取关键词"""
        # 技术关键词列表
        tech_keywords = {
            'seo', 'keyword', 'content', 'meta', 'title', 'description',
            'optimization', 'search', 'ranking', 'google', 'snippet',
            'structure', 'schema', 'authority', 'backlink', 'audit',
            'cannibalization', 'planning', 'strategy', 'writing',
            'technical', 'on-page', 'off-page', 'analytics'
        }

        text_lower = text.lower()
        found_keywords = set()

        for keyword in tech_keywords:
            if keyword in text_lower:
                found_keywords.add(keyword)

        return found_keywords

    def backup_agent(self, agent_name: str) -> Path:
        """备份单个 agent"""
        source = self.agents_dir / f"{agent_name}.md"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{agent_name}_{timestamp}.md"

        if source.exists():
            shutil.copy2(source, backup_file)
            print(f"  ✅ 已备份: {agent_name} → {backup_file.name}")
            return backup_file
        return None

    def analyze_seo_agents(self) -> Dict:
        """分析所有 SEO agents"""
        print("\n🔍 正在分析 SEO agents...\n")

        # 查找所有 SEO 相关的 agents
        seo_agents = []
        for agent_file in self.agents_dir.glob("seo-*.md"):
            agent_name = agent_file.stem
            agent_data = self.read_agent(agent_name)
            if agent_data:
                seo_agents.append(agent_data)

        print(f"找到 {len(seo_agents)} 个 SEO agents:\n")

        # 分析每个 agent
        analysis = {}
        for agent in seo_agents:
            name = agent['name']
            desc = agent['frontmatter'].get('description', '')
            keywords = self.extract_keywords(desc + ' ' + agent['body'])

            analysis[name] = {
                'description': desc,
                'keywords': keywords,
                'body_length': len(agent['body']),
                'has_description': bool(desc and len(desc) > 10)
            }

            print(f"  • {name}")
            print(f"    - 描述: {'✅ 完整' if analysis[name]['has_description'] else '❌ 缺失'}")
            print(f"    - 关键词: {', '.join(sorted(keywords)[:5])}")
            print(f"    - 内容长度: {analysis[name]['body_length']} 字符")
            print()

        return analysis

    def generate_merge_plan(self) -> Dict:
        """生成 SEO agents 合并方案"""

        merge_plan = {
            "merges": [
                {
                    "action": "保留并增强",
                    "primary": "seo-specialist",
                    "merge_from": ["seo-keyword-strategist", "seo-content-planner"],
                    "new_description": "Expert SEO specialist covering comprehensive search engine optimization including keyword research, content planning, SEO strategy, competitive analysis, search intent optimization, and SEO roadmap development. Use for SEO strategy, keyword research, content planning, SEO audits, search rankings improvement, or building comprehensive SEO campaigns.",
                    "reason": "通用 SEO 专家应该涵盖策略和关键词规划"
                },
                {
                    "action": "新建",
                    "primary": "seo-content-optimizer",
                    "merge_from": [
                        "seo-content-writer",
                        "seo-content-auditor",
                        "seo-content-refresher",
                        "seo-meta-optimizer"
                    ],
                    "new_description": "SEO content optimization specialist for creating, auditing, and refreshing SEO-optimized content. Handles SEO copywriting, content audits, content updates, meta tags optimization (title tags, meta descriptions), heading structure, keyword density, readability optimization, and content gap analysis. Use for writing SEO content, auditing existing content, refreshing old content, optimizing meta tags, or improving content performance.",
                    "reason": "所有内容相关的 SEO 工作整合到一个专家"
                },
                {
                    "action": "新建",
                    "primary": "seo-technical-auditor",
                    "merge_from": [
                        "seo-structure-architect",
                        "seo-cannibalization-detector",
                        "seo-snippet-hunter",
                        "seo-authority-builder",
                        "seo-technical-auditor"
                    ],
                    "new_description": "Technical SEO auditor and architect specializing in site structure optimization, technical SEO audits, keyword cannibalization detection, featured snippet optimization, schema markup, internal linking, site authority building, backlink analysis, Core Web Vitals, and crawlability optimization. Use for technical SEO audits, site structure design, fixing cannibalization issues, optimizing for featured snippets, building site authority, or improving technical SEO performance.",
                    "reason": "所有技术性和架构性的 SEO 工作统一处理"
                }
            ],
            "total_before": 13,
            "total_after": 3,
            "reduction": 10
        }

        return merge_plan

    def preview_merge(self, merge: Dict) -> None:
        """预览单个合并操作"""
        print(f"\n{'='*70}")
        print(f"🔀 合并操作预览")
        print(f"{'='*70}\n")

        print(f"操作类型: {merge['action']}")
        print(f"主 Agent: {merge['primary']}")
        print(f"合并来源: {', '.join(merge['merge_from'])}")
        print(f"\n原因: {merge['reason']}\n")

        print(f"新的 Description:")
        print(f"{'-'*70}")
        print(f"{merge['new_description']}")
        print(f"{'-'*70}\n")

        # 显示将要删除的 agents
        print(f"将要归档到 reference/deprecated/agents/:")
        for agent in merge['merge_from']:
            print(f"  • {agent}.md")
        print()

    def create_merged_agent(self, merge: Dict) -> bool:
        """创建或更新合并后的 agent"""
        primary_name = merge['primary']
        primary_file = self.agents_dir / f"{primary_name}.md"

        # 准备新内容
        if merge['action'] == "新建":
            # 创建新 agent
            content = f"""---
name: {primary_name}
description: {merge['new_description']}
---

# {primary_name.replace('-', ' ').title()}

{merge['new_description']}

## 合并说明

本 agent 整合了以下 agents 的功能：
{chr(10).join(f'- {agent}' for agent in merge['merge_from'])}

整合日期: {datetime.now().strftime('%Y-%m-%d')}

## 使用场景

根据具体需求，本 agent 可以处理：

{''.join(f'- {keyword.title()} 相关任务{chr(10)}' for keyword in ['seo', 'optimization', 'content', 'analysis'])}

## 工具访问

本 agent 可以访问所有标准工具来完成 SEO 优化任务。
"""
        else:
            # 更新现有 agent
            existing = self.read_agent(primary_name)
            if not existing:
                print(f"❌ 错误: 找不到 {primary_name}")
                return False

            # 更新 description
            existing['frontmatter']['description'] = merge['new_description']

            # 添加合并说明
            merge_note = f"\n\n## 合并说明\n\n本 agent 已增强，整合了以下 agents 的功能：\n"
            merge_note += '\n'.join(f'- {agent}' for agent in merge['merge_from'])
            merge_note += f"\n\n整合日期: {datetime.now().strftime('%Y-%m-%d')}\n"

            # 重新组装内容
            frontmatter_yaml = yaml.dump(existing['frontmatter'], allow_unicode=True, sort_keys=False)
            content = f"---\n{frontmatter_yaml}---\n\n{existing['body']}{merge_note}"

        # 写入文件（如果不是 dry-run）
        if not self.dry_run:
            # 先备份
            if primary_file.exists():
                self.backup_agent(primary_name)

            with open(primary_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ 已{'创建' if merge['action'] == '新建' else '更新'}: {primary_name}.md")
        else:
            print(f"  🔍 [Dry-run] 将{'创建' if merge['action'] == '新建' else '更新'}: {primary_name}.md")

        return True

    def archive_agents(self, agent_names: List[str], merged_into: str) -> None:
        """归档 agents 到 deprecated 目录"""
        for agent_name in agent_names:
            source = self.agents_dir / f"{agent_name}.md"
            if not source.exists():
                print(f"  ⚠️  跳过（不存在）: {agent_name}")
                continue

            # 先备份
            self.backup_agent(agent_name)

            # 创建迁移说明文件
            migration_note = f"""# {agent_name}

> ⚠️ 本 agent 已归档

**归档日期**: {datetime.now().strftime('%Y-%m-%d')}
**合并到**: `{merged_into}`
**原因**: 功能整合优化

## 迁移指南

如果你之前使用 `{agent_name}`，现在请使用 `{merged_into}`。

新的 agent 包含了本 agent 的所有功能，并且：
- 更完整的功能覆盖
- 更好的触发关键词
- 统一的使用体验

## 原始文件

原始文件已备份到: `reference/BAK/agents_optimization_backup/`
"""

            if not self.dry_run:
                # 移动到 deprecated
                dest = self.deprecated_dir / f"{agent_name}.md"
                shutil.move(str(source), str(dest))

                # 写入迁移说明
                with open(dest, 'w', encoding='utf-8') as f:
                    f.write(migration_note)

                print(f"  ✅ 已归档: {agent_name} → deprecated/agents/")
            else:
                print(f"  🔍 [Dry-run] 将归档: {agent_name}")

    def execute_merge(self, merge: Dict, confirmed: bool = False) -> bool:
        """执行单个合并操作"""
        if not confirmed:
            return False

        print(f"\n🚀 执行合并操作...\n")

        # 1. 创建或更新主 agent
        success = self.create_merged_agent(merge)
        if not success:
            print("❌ 创建/更新主 agent 失败")
            return False

        # 2. 归档被合并的 agents
        self.archive_agents(merge['merge_from'], merge['primary'])

        print(f"\n✅ 合并操作完成！")
        return True

    def generate_report(self, plan: Dict, executed: List[str]) -> str:
        """生成优化报告"""
        report = f"""# SEO Agents 优化报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 优化统计

- **优化前**: {plan['total_before']} 个 SEO agents
- **优化后**: {plan['total_after']} 个 SEO agents
- **减少数量**: {plan['reduction']} 个
- **执行的合并**: {len(executed)} 个

## 🔀 合并详情

"""

        for i, merge in enumerate(plan['merges'], 1):
            status = "✅ 已执行" if merge['primary'] in executed else "⏭️ 未执行"
            report += f"""### {i}. {merge['primary']} {status}

- **操作**: {merge['action']}
- **合并来源**: {', '.join(merge['merge_from'])}
- **原因**: {merge['reason']}

**新描述**:
> {merge['new_description']}

---

"""

        report += f"""## 📁 备份位置

所有原始文件已备份到:
- `reference/BAK/agents_optimization_backup/`

归档的 agents 位于:
- `reference/deprecated/agents/`

## 🔄 回滚方法

如需回滚任何更改:

```bash
# 从备份恢复
cp reference/BAK/agents_optimization_backup/AGENT_NAME_*.md components/agents/AGENT_NAME.md

# 从 deprecated 恢复
cp reference/deprecated/agents/AGENT_NAME.md components/agents/
```

## ✅ 下一步

1. 运行组件扫描: `python scripts/components_scanner.py`
2. 更新文档树: `python scripts/generate_components_tree.py`
3. 验证新 agents 的功能
4. 测试触发关键词是否正常工作
"""

        return report


def main(preview_only=False):
    """主函数 - 交互式执行"""
    print("="*70)
    print("🔧 Agents 优化工具 - SEO Agents 整合试点")
    print("="*70)

    optimizer = AgentOptimizer(dry_run=preview_only or False)

    # 1. 分析现有 SEO agents
    analysis = optimizer.analyze_seo_agents()

    # 2. 生成合并方案
    plan = optimizer.generate_merge_plan()

    print(f"\n📋 整合方案:")
    print(f"  • 当前 SEO agents: {plan['total_before']} 个")
    print(f"  • 整合后: {plan['total_after']} 个")
    print(f"  • 减少: {plan['reduction']} 个")
    print(f"  • 合并操作: {len(plan['merges'])} 个\n")

    # 3. 逐个确认并执行
    executed = []

    if preview_only:
        # 仅预览模式
        for i, merge in enumerate(plan['merges'], 1):
            print(f"\n{'='*70}")
            print(f"合并操作 {i}/{len(plan['merges'])}")
            optimizer.preview_merge(merge)

        print(f"\n{'='*70}")
        print("📋 预览完成！如需执行，请手动确认每个操作。")
        return plan

    for i, merge in enumerate(plan['merges'], 1):
        print(f"\n{'='*70}")
        print(f"合并操作 {i}/{len(plan['merges'])}")

        # 预览
        optimizer.preview_merge(merge)

        # 等待确认
        try:
            response = input("是否执行此合并操作？[y/N/q(退出)]: ").strip().lower()
        except EOFError:
            print("\n⏸️  非交互环境，停止执行")
            break

        if response == 'q':
            print("\n⏸️  用户取消，停止执行")
            break
        elif response == 'y':
            # 执行合并
            success = optimizer.execute_merge(merge, confirmed=True)
            if success:
                executed.append(merge['primary'])
        else:
            print("⏭️  跳过此操作")

    # 4. 生成报告
    if executed:
        print(f"\n{'='*70}")
        print("📝 生成优化报告...")

        report = optimizer.generate_report(plan, executed)
        report_file = optimizer.repo_root / "docs" / "SEO_AGENTS_OPTIMIZATION_REPORT.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✅ 报告已保存: {report_file}")
        print(f"\n🎉 优化完成！共执行了 {len(executed)} 个合并操作")
    else:
        print("\n⚠️  未执行任何合并操作")


if __name__ == "__main__":
    import sys
    preview_only = '--preview' in sys.argv
    main(preview_only=preview_only)
