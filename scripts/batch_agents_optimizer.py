#!/usr/bin/env python3
"""
批量 Agents 优化器
基于 SEO agents 优化的成功经验，批量优化多个 agent 组
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

class BatchAgentsOptimizer:
    """批量 Agents 优化器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.agents_dir = self.project_root / "components/agents"
        self.backup_dir = self.project_root / "reference/BAK/agents_batch_optimization_backup"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # 加载分析结果
        with open('/tmp/agents_analysis.json', 'r', encoding='utf-8') as f:
            self.analysis = json.load(f)

    def read_agent_file(self, agent_name: str) -> Dict:
        """读取 agent 文件并解析"""
        file_path = self.agents_dir / f"{agent_name}.md"

        if not file_path.exists():
            return {}

        content = file_path.read_text(encoding='utf-8')

        # 解析 YAML frontmatter
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)

        result = {
            'name': agent_name,
            'file_path': file_path,
            'content': content,
            'body': content,
            'yaml': {},
            'description': '',
            'tools': '',
            'model': 'sonnet'
        }

        if yaml_match:
            yaml_content = yaml_match.group(1)
            result['body'] = content[yaml_match.end():]

            # 提取字段
            for field in ['name', 'description', 'tools', 'model']:
                match = re.search(rf'{field}:\s*[\'"]?(.*?)[\'"]?\s*\n', yaml_content, re.DOTALL)
                if match:
                    result[field] = match.group(1).strip()
                    result['yaml'][field] = result[field]

        return result

    def extract_keywords(self, text: str) -> Set[str]:
        """提取关键词"""
        # 转换为小写
        text_lower = text.lower()

        # 常见技术关键词
        keywords = set()

        # 技术栈关键词
        tech_keywords = [
            'api', 'rest', 'graphql', 'database', 'sql', 'nosql', 'backend', 'frontend',
            'testing', 'performance', 'security', 'deployment', 'ci/cd', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'cloud', 'microservices', 'architecture',
            'optimization', 'monitoring', 'logging', 'debugging', 'documentation',
            'authentication', 'authorization', 'caching', 'scaling', 'load balancing',
            'data', 'analytics', 'visualization', 'reporting', 'dashboard',
            'mobile', 'ios', 'android', 'react native', 'flutter',
            'web', 'react', 'vue', 'angular', 'nextjs', 'nuxt',
            'django', 'rails', 'laravel', 'express', 'fastapi',
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch'
        ]

        for keyword in tech_keywords:
            if keyword in text_lower:
                keywords.add(keyword)

        return keywords

    def analyze_group(self, prefix: str, agents: List[Dict]) -> Dict:
        """分析一组 agents"""
        print(f"\n{'='*70}")
        print(f"分析 {prefix} agents ({len(agents)} 个)")
        print(f"{'='*70}")

        # 读取所有 agents
        agents_data = []
        all_keywords = set()
        all_descriptions = []
        total_size = 0

        for agent_info in agents:
            agent_name = agent_info['name']
            agent_data = self.read_agent_file(agent_name)

            if agent_data:
                agents_data.append(agent_data)

                # 收集关键词
                keywords = self.extract_keywords(agent_data.get('description', '') + agent_data.get('body', ''))
                all_keywords.update(keywords)

                # 收集描述
                if agent_data.get('description'):
                    all_descriptions.append(agent_data['description'])

                total_size += agent_info['size']

                print(f"  ✓ {agent_name:30s} ({agent_info['size']:>6,} bytes)")

        print(f"\n  关键词数量: {len(all_keywords)}")
        print(f"  总大小: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        print(f"  平均大小: {total_size/len(agents):,.0f} bytes")

        # 合并策略
        merge_strategy = self.determine_merge_strategy(prefix, agents_data, all_keywords)

        return {
            'prefix': prefix,
            'agents': agents_data,
            'keywords': list(all_keywords),
            'descriptions': all_descriptions,
            'total_size': total_size,
            'merge_strategy': merge_strategy
        }

    def determine_merge_strategy(self, prefix: str, agents: List[Dict], keywords: Set[str]) -> Dict:
        """确定合并策略"""

        # 根据 agent 数量和功能相似度决定合并方案
        num_agents = len(agents)

        if num_agents >= 5:
            # 5个以上：合并为 2-3 个
            target_count = 2
            strategy_type = "aggressive"  # 激进合并
        elif num_agents == 4:
            # 4个：合并为 2 个
            target_count = 2
            strategy_type = "moderate"  # 适度合并
        elif num_agents == 3:
            # 3个：合并为 2 个
            target_count = 2
            strategy_type = "conservative"  # 保守合并
        else:
            # 2个或更少：不合并
            return {'type': 'skip', 'reason': 'Too few agents'}

        return {
            'type': strategy_type,
            'current_count': num_agents,
            'target_count': target_count,
            'reduction_rate': (num_agents - target_count) / num_agents * 100
        }

    def generate_optimization_plan(self) -> Dict:
        """生成优化计划"""
        print("\n" + "="*70)
        print("生成批量优化计划")
        print("="*70)

        groups = self.analysis['groups']
        optimization_plan = {
            'timestamp': datetime.now().isoformat(),
            'total_groups': len(groups),
            'optimizable_groups': 0,
            'groups': {}
        }

        for prefix, agents_info in groups.items():
            if len(agents_info) < 3:
                continue

            analysis = self.analyze_group(prefix, agents_info)

            if analysis['merge_strategy']['type'] != 'skip':
                optimization_plan['optimizable_groups'] += 1
                optimization_plan['groups'][prefix] = {
                    'current_count': len(agents_info),
                    'target_count': analysis['merge_strategy']['target_count'],
                    'reduction_rate': analysis['merge_strategy']['reduction_rate'],
                    'total_size': analysis['total_size'],
                    'keywords_count': len(analysis['keywords']),
                    'agents': [a['name'] for a in analysis['agents']]
                }

        # 保存计划
        plan_file = self.project_root / "docs/AGENTS_BATCH_OPTIMIZATION_PLAN.md"
        self.generate_plan_report(optimization_plan, plan_file)

        return optimization_plan

    def generate_plan_report(self, plan: Dict, output_file: Path):
        """生成优化计划报告"""
        lines = [
            "# Agents 批量优化计划",
            "",
            f"> 生成时间: {plan['timestamp']}",
            f"> 待优化组数: {plan['optimizable_groups']}/{plan['total_groups']}",
            "",
            "---",
            "",
            "## 📊 优化概览",
            "",
            "| 组名 | 当前数量 | 目标数量 | 精简率 | 总大小 | 关键词 |",
            "|------|---------|---------|--------|--------|--------|"
        ]

        # 按精简率排序
        sorted_groups = sorted(plan['groups'].items(),
                              key=lambda x: x[1]['reduction_rate'],
                              reverse=True)

        total_current = 0
        total_target = 0

        for prefix, info in sorted_groups:
            total_current += info['current_count']
            total_target += info['target_count']

            lines.append(
                f"| **{prefix}** | {info['current_count']} | {info['target_count']} | "
                f"{info['reduction_rate']:.1f}% | {info['total_size']/1024:.1f} KB | "
                f"{info['keywords_count']} |"
            )

        total_reduction = (total_current - total_target) / total_current * 100

        lines.extend([
            f"| **总计** | **{total_current}** | **{total_target}** | "
            f"**{total_reduction:.1f}%** | - | - |",
            "",
            "## 📋 详细优化方案",
            ""
        ])

        for prefix, info in sorted_groups:
            lines.extend([
                f"### {prefix} agents",
                "",
                f"**当前**: {info['current_count']} 个 agents",
                f"**目标**: {info['target_count']} 个 agents",
                f"**精简率**: {info['reduction_rate']:.1f}%",
                "",
                "**待合并的 agents**:",
                ""
            ])

            for agent in info['agents']:
                lines.append(f"- `{agent}`")

            lines.append("")

        lines.extend([
            "---",
            "",
            "## 🎯 优化目标",
            "",
            "1. **文件精简**: 减少管理负担和维护成本",
            "2. **功能完整**: 保持 100% 关键词和触发场景覆盖",
            "3. **实质功能**: 确保 100% 实质功能逻辑覆盖 (剔除格式化元素)",
            "4. **可追溯性**: 通过功能映射表保证来源清晰",
            "",
            "## 🔧 优化方法",
            "",
            "基于 SEO agents 优化的成功经验:",
            "- ✅ 功能域聚类合并",
            "- ✅ 100% 关键词覆盖",
            "- ✅ 结构化 description",
            "- ✅ 功能映射表",
            "- ✅ V2 验证方法 (剔除格式化元素)",
            ""
        ])

        output_file.write_text('\n'.join(lines), encoding='utf-8')
        print(f"\n✓ 优化计划已生成: {output_file}")

def main():
    optimizer = BatchAgentsOptimizer()
    plan = optimizer.generate_optimization_plan()

    print("\n" + "="*70)
    print("批量优化计划生成完成")
    print("="*70)
    print(f"待优化组数: {plan['optimizable_groups']}")
    print(f"详细计划: docs/AGENTS_BATCH_OPTIMIZATION_PLAN.md")
    print("="*70)

if __name__ == '__main__':
    main()
