#!/usr/bin/env python3
"""
Agents 优化分析工具

分析 233 个 Agents，识别：
1. 重复或高度相似的 agents
2. 功能重叠的 agents
3. 可以合并的 agents
4. 描述不完整或需要优化的 agents
5. 使用频率低的 agents
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import re

def load_agents() -> Dict[str, Dict]:
    """加载所有 agents"""
    agents_dir = Path(__file__).parent.parent / "components" / "agents"
    agents = {}

    for agent_file in agents_dir.glob("*.md"):
        if agent_file.name in ['README.md', 'agent-template.md']:
            continue

        try:
            with open(agent_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    if frontmatter:
                        agent_name = agent_file.stem
                        agents[agent_name] = {
                            'file': agent_file.name,
                            'name': frontmatter.get('name', agent_name),
                            'description': frontmatter.get('description', ''),
                            'tools': frontmatter.get('tools', []),
                            'model': frontmatter.get('model', 'sonnet'),
                            'content': parts[2] if len(parts) > 2 else ''
                        }
        except Exception as e:
            print(f"⚠️  Error reading {agent_file.name}: {e}")

    return agents

def extract_keywords(text: str) -> Set[str]:
    """从文本中提取关键词"""
    # 常见技术关键词
    keywords = set()

    tech_terms = {
        # Languages
        'python', 'javascript', 'typescript', 'java', 'c#', 'go', 'rust', 'swift', 'kotlin',
        'php', 'ruby', 'scala', 'elixir', 'dart', 'shell', 'bash',

        # Frameworks
        'react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express', 'spring',
        'rails', 'laravel', 'next.js', 'nuxt', 'nest.js', 'electron',

        # Infrastructure
        'docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'aws', 'azure', 'gcp',
        'serverless', 'lambda', 'cloud', 'ci/cd', 'devops', 'gitops',

        # Databases
        'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'sql', 'nosql',

        # Concepts
        'api', 'rest', 'graphql', 'microservices', 'testing', 'security', 'performance',
        'optimization', 'architecture', 'frontend', 'backend', 'fullstack', 'mobile',
        'machine learning', 'ai', 'ml', 'nlp', 'data', 'analytics',
        'seo', 'marketing', 'content', 'design', 'ui', 'ux'
    }

    text_lower = text.lower()
    for term in tech_terms:
        if term in text_lower:
            keywords.add(term)

    return keywords

def find_similar_agents(agents: Dict[str, Dict]) -> List[Tuple[str, str, float, List[str]]]:
    """查找相似的 agents"""
    similar_pairs = []
    agent_names = list(agents.keys())

    for i, name1 in enumerate(agent_names):
        for name2 in agent_names[i+1:]:
            agent1 = agents[name1]
            agent2 = agents[name2]

            # 提取关键词
            keywords1 = extract_keywords(agent1['description'])
            keywords2 = extract_keywords(agent2['description'])

            # 计算相似度
            if keywords1 and keywords2:
                intersection = keywords1 & keywords2
                union = keywords1 | keywords2
                similarity = len(intersection) / len(union) if union else 0

                # 如果相似度 > 50%，认为可能重复
                if similarity > 0.5:
                    similar_pairs.append((name1, name2, similarity, list(intersection)))

    return sorted(similar_pairs, key=lambda x: x[2], reverse=True)

def find_incomplete_agents(agents: Dict[str, Dict]) -> List[Tuple[str, List[str]]]:
    """查找描述不完整的 agents"""
    incomplete = []

    for name, info in agents.items():
        issues = []

        desc = info['description']

        # 检查描述是否太短
        if len(desc) < 50:
            issues.append(f"描述太短 ({len(desc)} 字符)")

        # 检查是否包含 "please update"
        if 'please update' in desc.lower():
            issues.append("需要更新描述")

        # 检查是否缺少使用场景说明
        if 'use when' not in desc.lower() and 'use proactively' not in desc.lower():
            issues.append("缺少使用场景说明")

        # 检查是否为空或占位符
        if not desc or desc == f'{name} agent - please update this description':
            issues.append("空描述或占位符")

        if issues:
            incomplete.append((name, issues))

    return incomplete

def find_framework_duplicates(agents: Dict[str, Dict]) -> Dict[str, List[str]]:
    """查找框架特定的重复 agents"""
    frameworks = defaultdict(list)

    framework_patterns = {
        'django': ['django'],
        'rails': ['rails'],
        'laravel': ['laravel'],
        'vue': ['vue'],
        'react': ['react'],
        'angular': ['angular'],
        'next.js': ['next', 'nextjs'],
        'fastapi': ['fastapi'],
        'spring': ['spring'],
    }

    for name, info in agents.items():
        desc_lower = info['description'].lower()
        name_lower = name.lower()

        for framework, patterns in framework_patterns.items():
            if any(p in desc_lower or p in name_lower for p in patterns):
                frameworks[framework].append(name)

    return {k: v for k, v in frameworks.items() if len(v) > 1}

def find_role_overlaps(agents: Dict[str, Dict]) -> Dict[str, List[str]]:
    """查找职能重叠的 agents"""
    roles = defaultdict(list)

    role_patterns = {
        'architect': ['architect', 'architecture'],
        'developer': ['developer', 'engineer', 'coder'],
        'designer': ['designer', 'design'],
        'tester': ['tester', 'testing', 'qa'],
        'security': ['security', 'penetration', 'vulnerability'],
        'optimizer': ['optimizer', 'optimization', 'performance'],
        'analyst': ['analyst', 'analysis'],
        'manager': ['manager', 'coordinator', 'organizer'],
        'specialist': ['specialist', 'expert', 'pro', 'master'],
    }

    for name, info in agents.items():
        desc_lower = info['description'].lower()
        name_lower = name.lower()

        for role, patterns in role_patterns.items():
            if any(p in name_lower for p in patterns):
                roles[role].append(name)

    return {k: v for k, v in roles.items() if len(v) > 3}

def analyze_seo_agents(agents: Dict[str, Dict]) -> Dict:
    """专门分析 SEO 相关的 agents"""
    seo_agents = {}

    for name, info in agents.items():
        if 'seo' in name.lower() or 'seo' in info['description'].lower():
            seo_agents[name] = info

    return seo_agents

def generate_optimization_report(agents: Dict[str, Dict]) -> str:
    """生成优化建议报告"""
    lines = [
        "# Agents 优化分析报告",
        "",
        f"> 分析时间: 2025-11-11",
        f"> 总 Agents 数: {len(agents)}",
        "",
        "---",
        "",
        "## 📊 总体统计",
        "",
        f"- **总计**: {len(agents)} 个 Agents",
        f"- **需要优化**: 待分析",
        "",
        "---",
        ""
    ]

    # 1. 相似度分析
    print("🔍 分析相似 agents...")
    similar_pairs = find_similar_agents(agents)

    lines.extend([
        "## 🔄 高度相似的 Agents",
        "",
        f"**发现 {len(similar_pairs)} 对高度相似的 agents（相似度 > 50%）**",
        ""
    ])

    if similar_pairs:
        lines.append("### 建议合并的组合")
        lines.append("")

        for i, (name1, name2, similarity, common_keywords) in enumerate(similar_pairs[:20], 1):
            lines.append(f"#### {i}. {name1} ↔ {name2}")
            lines.append(f"- **相似度**: {similarity:.1%}")
            lines.append(f"- **共同关键词**: {', '.join(common_keywords)}")
            lines.append(f"- **描述 1**: {agents[name1]['description'][:100]}...")
            lines.append(f"- **描述 2**: {agents[name2]['description'][:100]}...")
            lines.append("")

        if len(similar_pairs) > 20:
            lines.append(f"... 还有 {len(similar_pairs) - 20} 对相似的 agents")
            lines.append("")

    lines.extend(["---", ""])

    # 2. 不完整描述
    print("🔍 分析不完整描述...")
    incomplete = find_incomplete_agents(agents)

    lines.extend([
        "## ⚠️ 描述不完整的 Agents",
        "",
        f"**发现 {len(incomplete)} 个需要完善描述的 agents**",
        ""
    ])

    if incomplete:
        for name, issues in incomplete[:30]:
            lines.append(f"### {name}")
            for issue in issues:
                lines.append(f"- ❌ {issue}")
            lines.append(f"- 当前描述: `{agents[name]['description'][:150]}...`")
            lines.append("")

        if len(incomplete) > 30:
            lines.append(f"... 还有 {len(incomplete) - 30} 个需要完善")
            lines.append("")

    lines.extend(["---", ""])

    # 3. 框架重复
    print("🔍 分析框架重复...")
    framework_dups = find_framework_duplicates(agents)

    lines.extend([
        "## 🏗️ 框架特定的重复 Agents",
        "",
        f"**发现 {len(framework_dups)} 个框架有多个相关 agents**",
        ""
    ])

    for framework, agent_list in sorted(framework_dups.items(), key=lambda x: -len(x[1])):
        lines.append(f"### {framework.title()} ({len(agent_list)} 个)")
        lines.append("")
        for agent in agent_list:
            lines.append(f"- **{agent}**")
            lines.append(f"  - {agents[agent]['description'][:120]}...")
        lines.append("")
        lines.append(f"**优化建议**: 考虑合并为 1-2 个通用的 {framework} agent")
        lines.append("")

    lines.extend(["---", ""])

    # 4. 职能重叠
    print("🔍 分析职能重叠...")
    role_overlaps = find_role_overlaps(agents)

    lines.extend([
        "## 👥 职能重叠的 Agents",
        "",
        f"**发现 {len(role_overlaps)} 种职能有多个 agents**",
        ""
    ])

    for role, agent_list in sorted(role_overlaps.items(), key=lambda x: -len(x[1])):
        lines.append(f"### {role.title()} ({len(agent_list)} 个)")
        lines.append("")
        for agent in agent_list[:10]:
            lines.append(f"- {agent}")
        if len(agent_list) > 10:
            lines.append(f"- ... 还有 {len(agent_list) - 10} 个")
        lines.append("")

    lines.extend(["---", ""])

    # 5. SEO agents 专项分析
    print("🔍 分析 SEO agents...")
    seo_agents = analyze_seo_agents(agents)

    lines.extend([
        "## 🔍 SEO Agents 专项分析",
        "",
        f"**发现 {len(seo_agents)} 个 SEO 相关的 agents**",
        ""
    ])

    if seo_agents:
        for name, info in seo_agents.items():
            lines.append(f"### {name}")
            lines.append(f"- {info['description'][:150]}...")
            lines.append("")

        lines.append("**优化建议**: SEO agents 数量较多，考虑整合为:")
        lines.append("- `seo-content-optimizer` - 内容优化（合并 content-auditor, content-refresher, meta-optimizer）")
        lines.append("- `seo-technical-auditor` - 技术审计（合并 structure-architect, cannibalization-detector）")
        lines.append("- `seo-authority-builder` - 权威建设（保留）")
        lines.append("")

    lines.extend(["---", ""])

    # 6. 优化建议总结
    lines.extend([
        "## 💡 优化建议总结",
        "",
        "### 优先级 1: 立即处理（高优先级）",
        "",
        f"1. **完善空描述** - {len([x for x in incomplete if '空描述' in str(x[1])])} 个 agents 缺少描述",
        f"2. **更新占位符** - {len([x for x in incomplete if 'please update' in agents[x[0]]['description'].lower()])} 个 agents 需要更新",
        "",
        "### 优先级 2: 短期优化（1-2 周）",
        "",
        f"3. **合并相似 agents** - 至少 {len([x for x in similar_pairs if x[2] > 0.7])} 对高度相似（>70%）可以合并",
        f"4. **整合框架 agents** - {sum(len(v) for v in framework_dups.values())} 个框架特定 agents 可以整合",
        f"5. **整合 SEO agents** - {len(seo_agents)} 个 SEO agents 可以合并为 2-3 个",
        "",
        "### 优先级 3: 长期优化（持续改进）",
        "",
        "6. **职能分工优化** - 重新定义 architect/developer/specialist 等职能边界",
        "7. **描述标准化** - 统一描述格式，包含使用场景、触发关键词",
        "8. **去重和归档** - 将低频使用的 agents 移至 reference/deprecated/",
        "",
        "---",
        "",
        "## 📋 具体行动计划",
        "",
        "### Phase 1: 清理（1 周）",
        "",
        "- [ ] 完善所有空描述和占位符",
        "- [ ] 删除或归档明显重复的 agents",
        "- [ ] 整合 SEO agents（10+ → 2-3 个）",
        "",
        "### Phase 2: 合并（2 周）",
        "",
        "- [ ] 合并框架特定的重复 agents",
        "- [ ] 合并高相似度 agents（>80%）",
        "- [ ] 统一职能命名规范",
        "",
        "### Phase 3: 优化（持续）",
        "",
        "- [ ] 标准化所有描述格式",
        "- [ ] 添加使用场景和触发关键词",
        "- [ ] 建立 agents 使用统计",
        "- [ ] 根据使用频率归档低频 agents",
        "",
        "---",
        "",
        "## 🎯 预期成果",
        "",
        f"**当前**: {len(agents)} 个 Agents",
        "**目标**: 100-120 个高质量 Agents",
        "**减少**: ~50%",
        "",
        "### 质量提升",
        "",
        "- ✅ 所有 agents 都有完整的描述",
        "- ✅ 清晰的使用场景和触发条件",
        "- ✅ 无重复或高度相似的 agents",
        "- ✅ 合理的职能分工和命名",
        "",
        "---",
        "",
        "**版本**: v1.0.0",
        "**分析日期**: 2025-11-11",
        "**状态**: 待执行优化",
        ""
    ])

    return '\n'.join(lines)

def main():
    """主函数"""
    print("🔍 Agents 优化分析工具")
    print("=" * 70)
    print()

    print("📦 加载 agents...")
    agents = load_agents()
    print(f"✅ 已加载 {len(agents)} 个 agents")
    print()

    print("📊 生成分析报告...")
    report = generate_optimization_report(agents)

    output_path = Path(__file__).parent.parent / "docs" / "AGENTS_OPTIMIZATION_ANALYSIS.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print()
    print(f"✅ 分析完成！报告已保存到: {output_path}")
    print()
    print("📋 快速摘要:")
    print(f"  - 总 agents 数: {len(agents)}")
    print(f"  - 建议目标数: 100-120 个")
    print(f"  - 优化潜力: ~50%")

if __name__ == '__main__':
    main()
