#!/usr/bin/env python3
"""
Component Coverage Analysis Tool

Analyzes all components and categorizes them scientifically to understand coverage areas.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import yaml

def load_components_registry() -> Dict:
    """Load components registry"""
    registry_path = Path(__file__).parent.parent / "components_registry.json"
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def extract_keywords_from_description(description: str) -> Set[str]:
    """Extract technology and domain keywords from description"""
    description_lower = description.lower()

    # Technology keywords
    tech_keywords = {
        # Languages
        'python', 'javascript', 'typescript', 'java', 'c#', 'c++', 'rust', 'go', 'golang',
        'swift', 'kotlin', 'php', 'ruby', 'scala', 'elixir', 'dart', 'r',

        # Frameworks/Libraries
        'react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express', 'nest.js',
        'spring', 'rails', 'laravel', 'next.js', 'nuxt', 'svelte', 'electron',

        # Infrastructure
        'docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'jenkins', 'gitlab',
        'aws', 'azure', 'gcp', 'cloud', 'serverless', 'lambda',

        # Databases
        'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
        'dynamodb', 'sql', 'nosql',

        # AI/ML
        'machine learning', 'deep learning', 'nlp', 'llm', 'ai', 'neural network',
        'tensorflow', 'pytorch', 'transformers',

        # Testing
        'jest', 'pytest', 'junit', 'selenium', 'cypress', 'testing',

        # DevOps
        'ci/cd', 'devops', 'gitops', 'monitoring', 'logging', 'observability',
    }

    found_keywords = set()
    for keyword in tech_keywords:
        if keyword in description_lower:
            found_keywords.add(keyword)

    return found_keywords

def categorize_agents(agents_data: Dict) -> Dict[str, List[Dict]]:
    """Categorize agents by domain"""
    categories = defaultdict(list)

    for agent_name, agent_info in agents_data.items():
        description = agent_info.get('description', '').lower()

        # Define category patterns
        category_patterns = {
            'Backend Development': [
                'backend', 'server-side', 'api', 'microservices', 'rest', 'graphql',
                'database', 'orm', 'express', 'fastapi', 'django', 'rails', 'spring'
            ],
            'Frontend Development': [
                'frontend', 'ui', 'react', 'vue', 'angular', 'component', 'css',
                'html', 'responsive', 'web design', 'user interface'
            ],
            'Full Stack Development': [
                'fullstack', 'full-stack', 'end-to-end', 'full stack'
            ],
            'Mobile Development': [
                'mobile', 'ios', 'android', 'flutter', 'react native', 'swift', 'kotlin'
            ],
            'DevOps & Infrastructure': [
                'devops', 'infrastructure', 'deployment', 'ci/cd', 'docker', 'kubernetes',
                'terraform', 'ansible', 'cloud', 'aws', 'azure', 'gcp'
            ],
            'Data & AI': [
                'data', 'machine learning', 'deep learning', 'ai', 'ml', 'nlp', 'llm',
                'analytics', 'data science', 'neural', 'model training'
            ],
            'Quality & Testing': [
                'testing', 'qa', 'quality', 'test automation', 'e2e', 'integration test',
                'unit test', 'tdd', 'bdd'
            ],
            'Security': [
                'security', 'penetration', 'vulnerability', 'compliance', 'encryption',
                'authentication', 'authorization', 'oauth', 'jwt'
            ],
            'Architecture & Design': [
                'architect', 'architecture', 'design patterns', 'system design',
                'scalability', 'distributed systems'
            ],
            'Performance & Optimization': [
                'performance', 'optimization', 'profiling', 'caching', 'load balancing',
                'scalability'
            ],
            'Documentation & Tools': [
                'documentation', 'docs', 'technical writing', 'api documentation',
                'cli', 'tooling', 'developer experience'
            ],
            'Business & Product': [
                'product', 'project manager', 'business', 'sales', 'marketing',
                'analytics', 'stakeholder'
            ],
            'Specialized Domains': [
                'blockchain', 'web3', 'iot', 'embedded', 'game', 'fintech', 'e-commerce',
                'healthcare', 'seo'
            ],
            'Meta & Orchestration': [
                'orchestrat', 'coordinator', 'workflow', 'multi-agent', 'task distribut'
            ]
        }

        # Assign to categories
        assigned = False
        for category, patterns in category_patterns.items():
            if any(pattern in description for pattern in patterns):
                categories[category].append({
                    'name': agent_name,
                    'description': agent_info.get('description', 'No description')
                })
                assigned = True
                break  # Assign to first matching category

        if not assigned:
            categories['Other'].append({
                'name': agent_name,
                'description': agent_info.get('description', 'No description')
            })

    return dict(categories)

def categorize_skills(skills_data: Dict) -> Dict[str, List[Dict]]:
    """Categorize skills by domain"""
    categories = defaultdict(list)

    for skill_name, skill_info in skills_data.items():
        description = skill_info.get('description', '').lower()

        category_patterns = {
            'Development Patterns': [
                'pattern', 'architecture', 'design', 'best practices', 'clean code',
                'solid', 'ddd', 'mvc'
            ],
            'Language-Specific': [
                'python', 'javascript', 'typescript', 'java', 'go', 'rust', 'c++',
                'async', 'concurrency'
            ],
            'Framework-Specific': [
                'react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express',
                'spring', 'rails', 'laravel'
            ],
            'Testing & Quality': [
                'testing', 'test', 'tdd', 'bdd', 'e2e', 'unit test', 'integration',
                'quality', 'coverage'
            ],
            'DevOps & Deployment': [
                'devops', 'deployment', 'ci/cd', 'docker', 'kubernetes', 'terraform',
                'gitops', 'pipeline'
            ],
            'Backend Development': [
                'api', 'backend', 'microservices', 'rest', 'graphql', 'database',
                'orm', 'server'
            ],
            'Frontend Development': [
                'frontend', 'component', 'ui', 'css', 'responsive', 'accessibility',
                'web performance'
            ],
            'Data & AI': [
                'data', 'machine learning', 'ai', 'ml', 'analytics', 'pipeline',
                'rag', 'llm', 'prompt'
            ],
            'Security & Compliance': [
                'security', 'auth', 'encryption', 'compliance', 'oauth', 'vulnerability'
            ],
            'Performance & Optimization': [
                'performance', 'optimization', 'caching', 'profiling', 'monitoring'
            ],
            'Documentation': [
                'documentation', 'docs', 'technical writing', 'api docs'
            ],
            'Workflow & Productivity': [
                'workflow', 'automation', 'productivity', 'task management', 'planning'
            ]
        }

        assigned = False
        for category, patterns in category_patterns.items():
            if any(pattern in description for pattern in patterns):
                categories[category].append({
                    'name': skill_name,
                    'description': skill_info.get('description', 'No description')
                })
                assigned = True
                break

        if not assigned:
            categories['Other'].append({
                'name': skill_name,
                'description': skill_info.get('description', 'No description')
            })

    return dict(categories)

def categorize_commands(commands_data: Dict) -> Dict[str, List[Dict]]:
    """Categorize commands by purpose"""
    categories = defaultdict(list)

    for command_name, command_info in commands_data.items():
        description = command_info.get('description', '').lower()

        category_patterns = {
            'Development Workflow': [
                'develop', 'scaffold', 'generate', 'create', 'build', 'workflow'
            ],
            'Testing & Quality': [
                'test', 'tdd', 'coverage', 'quality', 'lint', 'format'
            ],
            'Documentation': [
                'doc', 'documentation', 'api doc', 'readme', 'guide'
            ],
            'Code Analysis': [
                'analyze', 'review', 'audit', 'inspect', 'explain', 'refactor'
            ],
            'Debugging & Troubleshooting': [
                'debug', 'trace', 'error', 'fix', 'troubleshoot', 'diagnose'
            ],
            'Security & Compliance': [
                'security', 'vulnerability', 'compliance', 'audit', 'scan'
            ],
            'Performance': [
                'performance', 'optimize', 'profil', 'benchmark', 'monitor'
            ],
            'DevOps & Deployment': [
                'deploy', 'ci/cd', 'pipeline', 'release', 'gitops'
            ],
            'Database': [
                'database', 'migration', 'sql', 'query', 'schema'
            ],
            'API & Integration': [
                'api', 'rest', 'graphql', 'integration', 'webhook'
            ],
            'Project Management': [
                'project', 'issue', 'task', 'standup', 'planning'
            ]
        }

        assigned = False
        for category, patterns in category_patterns.items():
            if any(pattern in description for pattern in patterns):
                categories[category].append({
                    'name': command_name,
                    'description': command_info.get('description', 'No description')
                })
                assigned = True
                break

        if not assigned:
            categories['Other'].append({
                'name': command_name,
                'description': command_info.get('description', 'No description')
            })

    return dict(categories)

def generate_coverage_report(registry: Dict) -> str:
    """Generate coverage analysis report"""
    components = registry.get('components', registry)

    agents_data = components.get('agents', {})
    skills_data = components.get('skills', {})
    commands_data = components.get('commands', {})

    # Categorize
    agent_categories = categorize_agents(agents_data)
    skill_categories = categorize_skills(skills_data)
    command_categories = categorize_commands(commands_data)

    # Build report
    lines = [
        "# Component Coverage Analysis",
        "",
        "> 自动生成的组件覆盖面分析报告",
        "",
        f"**生成时间**: 2025-11-11",
        "",
        "---",
        "",
        "## 📊 总体统计",
        "",
        f"- **Agents**: {len(agents_data)} 个",
        f"- **Skills**: {len(skills_data)} 个",
        f"- **Commands**: {len(commands_data)} 个",
        f"- **总计**: {len(agents_data) + len(skills_data) + len(commands_data)} 个组件",
        "",
        "---",
        "",
        "## 🤖 Agents 分类覆盖",
        "",
        f"**总计**: {len(agents_data)} 个 Agents，分为 {len(agent_categories)} 个类别",
        ""
    ]

    # Agent categories
    for category, agents in sorted(agent_categories.items(), key=lambda x: -len(x[1])):
        lines.append(f"### {category} ({len(agents)} 个)")
        lines.append("")

        # Show first 10 as examples
        for agent in sorted(agents[:10], key=lambda x: x['name']):
            lines.append(f"- **{agent['name']}**")
            lines.append(f"  - {agent['description'][:150]}{'...' if len(agent['description']) > 150 else ''}")

        if len(agents) > 10:
            lines.append(f"  - ... 还有 {len(agents) - 10} 个")

        lines.append("")

    lines.extend([
        "---",
        "",
        "## 📚 Skills 分类覆盖",
        "",
        f"**总计**: {len(skills_data)} 个 Skills，分为 {len(skill_categories)} 个类别",
        ""
    ])

    # Skill categories
    for category, skills in sorted(skill_categories.items(), key=lambda x: -len(x[1])):
        lines.append(f"### {category} ({len(skills)} 个)")
        lines.append("")

        for skill in sorted(skills, key=lambda x: x['name']):
            lines.append(f"- **{skill['name']}**")
            lines.append(f"  - {skill['description'][:150]}{'...' if len(skill['description']) > 150 else ''}")

        lines.append("")

    lines.extend([
        "---",
        "",
        "## ⚡ Commands 分类覆盖",
        "",
        f"**总计**: {len(commands_data)} 个 Commands，分为 {len(command_categories)} 个类别",
        ""
    ])

    # Command categories
    for category, commands in sorted(command_categories.items(), key=lambda x: -len(x[1])):
        lines.append(f"### {category} ({len(commands)} 个)")
        lines.append("")

        for command in sorted(commands, key=lambda x: x['name']):
            lines.append(f"- **{command['name']}**")
            lines.append(f"  - {command['description'][:150]}{'...' if len(command['description']) > 150 else ''}")

        lines.append("")

    # Technology coverage
    lines.extend([
        "---",
        "",
        "## 🔧 技术栈覆盖分析",
        ""
    ])

    # Extract all tech keywords
    all_tech = defaultdict(int)
    for agent in agents_data.values():
        keywords = extract_keywords_from_description(agent.get('description', ''))
        for keyword in keywords:
            all_tech[keyword] += 1

    lines.append("### 主要技术栈 (按组件数排序)")
    lines.append("")
    lines.append("| 技术 | Agent 数量 |")
    lines.append("|------|-----------|")

    for tech, count in sorted(all_tech.items(), key=lambda x: -x[1])[:20]:
        lines.append(f"| {tech} | {count} |")

    lines.extend([
        "",
        "---",
        "",
        "## 📈 覆盖面总结",
        "",
        "### Agents 覆盖最全的领域",
        ""
    ])

    top_agent_categories = sorted(agent_categories.items(), key=lambda x: -len(x[1]))[:5]
    for i, (category, agents) in enumerate(top_agent_categories, 1):
        lines.append(f"{i}. **{category}**: {len(agents)} 个 agents")

    lines.extend([
        "",
        "### Skills 覆盖最全的领域",
        ""
    ])

    top_skill_categories = sorted(skill_categories.items(), key=lambda x: -len(x[1]))[:5]
    for i, (category, skills) in enumerate(top_skill_categories, 1):
        lines.append(f"{i}. **{category}**: {len(skills)} 个 skills")

    lines.extend([
        "",
        "### Commands 覆盖最全的领域",
        ""
    ])

    top_command_categories = sorted(command_categories.items(), key=lambda x: -len(x[1]))[:5]
    for i, (category, commands) in enumerate(top_command_categories, 1):
        lines.append(f"{i}. **{category}**: {len(commands)} 个 commands")

    lines.extend([
        "",
        "---",
        "",
        "**Note**: 此报告基于组件的 description 字段自动分类生成，可能存在分类重叠或不准确的情况。",
        ""
    ])

    return '\n'.join(lines)

def main():
    """Main entry point"""
    print("🔍 Component Coverage Analysis Tool")
    print("=" * 70)

    print("\n📦 Loading components registry...")
    registry = load_components_registry()

    print("📊 Analyzing coverage...")
    report = generate_coverage_report(registry)

    output_path = Path(__file__).parent.parent / "docs" / "COMPONENT_COVERAGE_ANALYSIS.md"
    print(f"💾 Saving report to {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ Done! Coverage analysis saved to: {output_path}")

if __name__ == '__main__':
    main()
