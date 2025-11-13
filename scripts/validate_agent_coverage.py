#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO Agents 功能覆盖完整性验证工具
基于三维度验证：关键词、触发场景、核心功能逻辑
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class AgentCoverageValidator:
    """Agent 功能覆盖验证器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.inventory_file = self.project_root / "docs/SEO_AGENTS_INVENTORY.json"
        self.new_agents_dir = self.project_root / "components/agents"

        # 加载原功能资产清单
        with open(self.inventory_file, 'r', encoding='utf-8') as f:
            self.original_inventory = json.load(f)

        # 新 agents 映射
        self.merge_mapping = {
            'seo-specialist': ['seo-specialist', 'seo-keyword-strategist', 'seo-content-planner'],
            'seo-content-optimizer': ['seo-content-writer', 'seo-content-auditor',
                                      'seo-content-refresher', 'seo-meta-optimizer'],
            'seo-technical-auditor': ['seo-structure-architect', 'seo-cannibalization-detector',
                                      'seo-snippet-hunter', 'seo-authority-builder']
        }

        # 新 agents 内容
        self.new_agents = {}
        for new_agent_name in self.merge_mapping.keys():
            agent_file = self.new_agents_dir / f"{new_agent_name}.md"
            if agent_file.exists():
                with open(agent_file, 'r', encoding='utf-8') as f:
                    self.new_agents[new_agent_name] = f.read()

    def extract_keywords_from_text(self, text: str) -> Set[str]:
        """从文本中提取关键词（忽略大小写）"""
        # 转换为小写并提取所有可能的关键词
        text_lower = text.lower()
        keywords = set()

        # 常见 SEO 关键词列表
        common_keywords = [
            'seo', 'keyword', 'content', 'optimization', 'search', 'ranking',
            'google', 'meta', 'title', 'description', 'audit', 'strategy',
            'schema', 'snippet', 'featured snippet', 'rich snippet', 'serp',
            'backlink', 'internal linking', 'external linking', 'anchor text',
            'crawlability', 'indexing', 'sitemap', 'robots.txt', 'canonical',
            'authority', 'e-e-a-t', 'cannibalization', 'technical', 'on-page',
            'off-page', 'url structure', 'site architecture', 'analytics',
            'core web vitals', 'page speed', 'mobile-first', 'structure',
            'planning'  # 添加 planning 关键词
        ]

        for kw in common_keywords:
            if kw in text_lower:
                keywords.add(kw)

        return keywords

    def validate_keyword_coverage(self) -> Dict:
        """维度1: 验证关键词覆盖率"""
        print("\n" + "="*70)
        print("维度1: 功能关键词覆盖率验证")
        print("="*70)

        results = {}

        for new_agent, original_agents in self.merge_mapping.items():
            print(f"\n🔍 验证 {new_agent}")
            print(f"   合并来源: {', '.join(original_agents)}")

            # 收集原 agents 的所有关键词
            original_keywords = set()
            for orig_agent in original_agents:
                if orig_agent in self.original_inventory:
                    kws = self.original_inventory[orig_agent].get('keywords', [])
                    original_keywords.update(kw.lower() for kw in kws)

            # 从新 agent 文本中提取关键词
            new_agent_text = self.new_agents.get(new_agent, '')
            new_keywords = self.extract_keywords_from_text(new_agent_text)

            # 计算覆盖率
            missing_keywords = original_keywords - new_keywords
            coverage_rate = ((len(original_keywords) - len(missing_keywords)) /
                           len(original_keywords) * 100 if original_keywords else 100)

            results[new_agent] = {
                'original_keywords': sorted(original_keywords),
                'new_keywords': sorted(new_keywords),
                'missing_keywords': sorted(missing_keywords),
                'coverage_rate': coverage_rate,
                'total_original': len(original_keywords),
                'total_covered': len(original_keywords) - len(missing_keywords)
            }

            print(f"   原关键词数: {len(original_keywords)}")
            print(f"   已覆盖数: {len(original_keywords) - len(missing_keywords)}")
            print(f"   覆盖率: {coverage_rate:.1f}%")

            if missing_keywords:
                print(f"   ⚠️  缺失的关键词: {', '.join(missing_keywords)}")
            else:
                print(f"   ✅ 所有关键词已覆盖")

        return results

    def validate_scenario_coverage(self) -> Dict:
        """维度2: 验证触发场景完整性"""
        print("\n" + "="*70)
        print("维度2: 触发场景完整性验证")
        print("="*70)

        results = {}

        for new_agent, original_agents in self.merge_mapping.items():
            print(f"\n🔍 验证 {new_agent}")

            # 收集原 agents 的所有触发场景
            original_scenarios = []
            for orig_agent in original_agents:
                if orig_agent in self.original_inventory:
                    scenarios = self.original_inventory[orig_agent].get('trigger_scenarios', [])
                    for scenario in scenarios:
                        original_scenarios.append({
                            'source': orig_agent,
                            'scenario': scenario
                        })

            # 检查新 agent 的 description 是否包含这些场景
            new_agent_text = self.new_agents.get(new_agent, '')

            covered_scenarios = []
            missing_scenarios = []

            for item in original_scenarios:
                scenario = item['scenario']
                # 提取场景中的关键短语
                scenario_keywords = self.extract_scenario_keywords(scenario)

                # 检查这些关键短语是否在新 agent 中
                if self.is_scenario_covered(scenario_keywords, new_agent_text):
                    covered_scenarios.append(item)
                else:
                    missing_scenarios.append(item)

            coverage_rate = (len(covered_scenarios) / len(original_scenarios) * 100
                           if original_scenarios else 100)

            results[new_agent] = {
                'original_scenarios': original_scenarios,
                'covered_scenarios': covered_scenarios,
                'missing_scenarios': missing_scenarios,
                'coverage_rate': coverage_rate,
                'total_original': len(original_scenarios),
                'total_covered': len(covered_scenarios)
            }

            print(f"   原触发场景数: {len(original_scenarios)}")
            print(f"   已覆盖数: {len(covered_scenarios)}")
            print(f"   覆盖率: {coverage_rate:.1f}%")

            if missing_scenarios:
                print(f"   ⚠️  可能缺失的场景:")
                for item in missing_scenarios:
                    print(f"      - {item['source']}: {item['scenario']}")
            else:
                print(f"   ✅ 所有触发场景已覆盖")

        return results

    def extract_scenario_keywords(self, scenario: str) -> Set[str]:
        """从触发场景描述中提取关键短语"""
        keywords = set()

        # 移除 "Use PROACTIVELY" 等前缀
        scenario = re.sub(r'Use PROACTIVELY (for|when)', '', scenario, flags=re.IGNORECASE)

        # 提取重要短语
        phrases = [
            'content creation', 'content review', 'older content', 'new content',
            'content optimization', 'content strategy', 'content planning',
            'content structuring', 'similar content', 'question-based content',
            'YMYL topics', 'reviewing', 'optimization'
        ]

        scenario_lower = scenario.lower()
        for phrase in phrases:
            if phrase in scenario_lower:
                keywords.add(phrase)

        return keywords

    def is_scenario_covered(self, scenario_keywords: Set[str], new_agent_text: str) -> bool:
        """检查场景是否被新 agent 覆盖"""
        if not scenario_keywords:
            return True  # 如果没有关键短语，认为已覆盖

        new_agent_lower = new_agent_text.lower()

        # 检查至少一半的关键短语在新 agent 中
        covered_count = sum(1 for kw in scenario_keywords if kw in new_agent_lower)
        return covered_count >= len(scenario_keywords) * 0.5

    def validate_function_logic_coverage(self) -> Dict:
        """维度3: 验证核心功能逻辑复用"""
        print("\n" + "="*70)
        print("维度3: 核心功能逻辑复用验证")
        print("="*70)

        results = {}

        for new_agent, original_agents in self.merge_mapping.items():
            print(f"\n🔍 验证 {new_agent}")

            # 收集原 agents 的所有核心功能
            original_functions = []
            for orig_agent in original_agents:
                if orig_agent in self.original_inventory:
                    funcs = self.original_inventory[orig_agent].get('core_functions', [])
                    for func in funcs:
                        original_functions.append({
                            'source': orig_agent,
                            'function': func
                        })

            # 检查新 agent 中是否包含这些功能
            new_agent_text = self.new_agents.get(new_agent, '')

            covered_functions = []
            missing_functions = []

            for item in original_functions:
                func = item['function']
                # 提取功能中的关键词
                func_keywords = self.extract_keywords_from_text(func)

                # 检查这些关键词是否在新 agent 中
                if func_keywords and any(kw in new_agent_text.lower() for kw in func_keywords):
                    covered_functions.append(item)
                else:
                    # 某些功能点是标题性质的，检查其在功能映射表中
                    if self.is_function_in_mapping_table(func, new_agent_text):
                        covered_functions.append(item)
                    else:
                        missing_functions.append(item)

            coverage_rate = (len(covered_functions) / len(original_functions) * 100
                           if original_functions else 100)

            results[new_agent] = {
                'original_functions': original_functions,
                'covered_functions': covered_functions,
                'missing_functions': missing_functions,
                'coverage_rate': coverage_rate,
                'total_original': len(original_functions),
                'total_covered': len(covered_functions)
            }

            print(f"   原核心功能数: {len(original_functions)}")
            print(f"   已覆盖数: {len(covered_functions)}")
            print(f"   覆盖率: {coverage_rate:.1f}%")

            if missing_functions:
                print(f"   ⚠️  可能缺失的功能:")
                for item in missing_functions[:5]:  # 只显示前5个
                    print(f"      - {item['source']}: {item['function']}")
                if len(missing_functions) > 5:
                    print(f"      ... 还有 {len(missing_functions) - 5} 个")
            else:
                print(f"   ✅ 所有核心功能已覆盖")

        return results

    def is_function_in_mapping_table(self, function: str, new_agent_text: str) -> bool:
        """检查功能是否在功能映射表中"""
        # 功能映射表通常在文件末尾
        if '功能映射表' in new_agent_text or '整合了以下 agents' in new_agent_text:
            mapping_section = new_agent_text.split('功能映射表')[-1]
            return function.lower() in mapping_section.lower()
        return False

    def generate_test_queries(self) -> List[Dict]:
        """生成实战测试查询"""
        print("\n" + "="*70)
        print("实战测试: 生成模拟用户查询")
        print("="*70)

        test_queries = []

        # 为每个原 agent 生成典型查询
        agent_queries = {
            'seo-specialist': [
                "如何做全站 SEO 审计？",
                "提升网站关键词排名的策略",
                "分析竞品的 SEO 策略"
            ],
            'seo-keyword-strategist': [
                "如何做关键词研究？",
                "计算关键词密度是否合理",
                "找相关的 LSI 关键词"
            ],
            'seo-content-planner': [
                "制定内容日历和发布计划",
                "规划主题集群和支柱内容"
            ],
            'seo-content-writer': [
                "写一篇 SEO 优化的博客文章",
                "创建产品页面的 SEO 内容"
            ],
            'seo-content-auditor': [
                "审计这个页面的内容质量",
                "检查内容的 E-E-A-T 信号"
            ],
            'seo-content-refresher': [
                "更新这篇旧文章的内容",
                "刷新过时的统计数据和案例"
            ],
            'seo-meta-optimizer': [
                "优化页面的 meta 标题和描述",
                "改进 URL 结构"
            ],
            'seo-structure-architect': [
                "优化网站的信息架构",
                "设计 schema 标记策略",
                "改进内部链接结构"
            ],
            'seo-cannibalization-detector': [
                "检测关键词自相竞争问题",
                "我的两个页面都在排同一个词"
            ],
            'seo-snippet-hunter': [
                "如何优化内容以获得精选摘要？",
                "为问答内容创建 snippet 优化"
            ],
            'seo-authority-builder': [
                "提升网站的权威度和可信度",
                "为 YMYL 主题添加 E-E-A-T 信号"
            ]
        }

        for orig_agent, queries in agent_queries.items():
            for query in queries:
                # 找到该原 agent 应该映射到哪个新 agent
                target_agent = None
                for new_agent, orig_list in self.merge_mapping.items():
                    if orig_agent in orig_list:
                        target_agent = new_agent
                        break

                test_queries.append({
                    'query': query,
                    'original_agent': orig_agent,
                    'expected_new_agent': target_agent
                })

        print(f"\n✅ 生成了 {len(test_queries)} 个测试查询")
        print("\n示例查询:")
        for i, item in enumerate(test_queries[:5], 1):
            print(f"{i}. \"{item['query']}\"")
            print(f"   原agent: {item['original_agent']} → 新agent: {item['expected_new_agent']}")

        return test_queries

    def generate_report(self, keyword_results: Dict, scenario_results: Dict,
                       function_results: Dict, test_queries: List[Dict]) -> str:
        """生成验证报告"""
        report = []

        report.append("# SEO Agents 功能覆盖完整性验证报告")
        report.append("")
        report.append(f"> 验证时间: 2025-11-11")
        report.append("> 验证方法: 三维度反向校验（关键词、触发场景、核心功能逻辑）")
        report.append("> 基准数据: SEO_AGENTS_INVENTORY.json")
        report.append("")
        report.append("---")
        report.append("")

        # 总体统计
        report.append("## 📊 总体验证结果")
        report.append("")

        # 关键词覆盖率
        total_keyword_coverage = sum(r['coverage_rate'] for r in keyword_results.values()) / len(keyword_results)
        report.append(f"### 维度1: 功能关键词覆盖率")
        report.append(f"- **平均覆盖率**: {total_keyword_coverage:.1f}%")
        report.append("")

        for agent, result in keyword_results.items():
            status = "✅" if result['coverage_rate'] == 100 else "⚠️"
            report.append(f"- {status} **{agent}**: {result['coverage_rate']:.1f}% "
                         f"({result['total_covered']}/{result['total_original']})")
            if result['missing_keywords']:
                report.append(f"  - 缺失: {', '.join(result['missing_keywords'])}")
        report.append("")

        # 触发场景覆盖率
        total_scenario_coverage = sum(r['coverage_rate'] for r in scenario_results.values()) / len(scenario_results)
        report.append(f"### 维度2: 触发场景完整性")
        report.append(f"- **平均覆盖率**: {total_scenario_coverage:.1f}%")
        report.append("")

        for agent, result in scenario_results.items():
            status = "✅" if result['coverage_rate'] == 100 else "⚠️"
            report.append(f"- {status} **{agent}**: {result['coverage_rate']:.1f}% "
                         f"({result['total_covered']}/{result['total_original']})")
        report.append("")

        # 功能逻辑覆盖率
        total_function_coverage = sum(r['coverage_rate'] for r in function_results.values()) / len(function_results)
        report.append(f"### 维度3: 核心功能逻辑复用")
        report.append(f"- **平均覆盖率**: {total_function_coverage:.1f}%")
        report.append("")

        for agent, result in function_results.items():
            status = "✅" if result['coverage_rate'] >= 90 else "⚠️"
            report.append(f"- {status} **{agent}**: {result['coverage_rate']:.1f}% "
                         f"({result['total_covered']}/{result['total_original']})")
        report.append("")

        # 综合评分
        report.append("## 🎯 综合评分")
        report.append("")
        overall_score = (total_keyword_coverage + total_scenario_coverage + total_function_coverage) / 3

        if overall_score >= 95:
            verdict = "✅ **优秀** - 未过度精简，功能覆盖完整"
        elif overall_score >= 85:
            verdict = "⚠️ **良好** - 基本覆盖，有少量缺失"
        else:
            verdict = "❌ **需改进** - 存在明显功能缺失"

        report.append(f"- **综合覆盖率**: {overall_score:.1f}%")
        report.append(f"- **验证结论**: {verdict}")
        report.append("")

        # 实战测试查询
        report.append("## 🧪 实战测试查询（共 {} 个）".format(len(test_queries)))
        report.append("")
        report.append("以下查询可用于实际测试新 agents 的响应能力：")
        report.append("")

        by_new_agent = defaultdict(list)
        for item in test_queries:
            by_new_agent[item['expected_new_agent']].append(item)

        for new_agent, queries in by_new_agent.items():
            report.append(f"### {new_agent} ({len(queries)} 个查询)")
            report.append("")
            for item in queries:
                report.append(f"- \"{item['query']}\" (原: {item['original_agent']})")
            report.append("")

        # 详细数据
        report.append("---")
        report.append("")
        report.append("## 📋 详细验证数据")
        report.append("")

        # 关键词详情
        report.append("### 维度1详情: 关键词对比")
        report.append("")
        for agent, result in keyword_results.items():
            report.append(f"#### {agent}")
            report.append("")
            report.append(f"**原关键词** ({len(result['original_keywords'])} 个):")
            report.append(f"```")
            report.append(", ".join(result['original_keywords']))
            report.append(f"```")
            report.append("")
            if result['missing_keywords']:
                report.append(f"**缺失关键词** ({len(result['missing_keywords'])} 个):")
                report.append(f"```")
                report.append(", ".join(result['missing_keywords']))
                report.append(f"```")
                report.append("")

        return "\n".join(report)

    def run(self):
        """执行完整验证流程"""
        print("\n" + "="*70)
        print("SEO Agents 功能覆盖完整性验证")
        print("="*70)
        print(f"\n基准数据: {self.inventory_file}")
        print(f"新 Agents 目录: {self.new_agents_dir}")
        print(f"验证对象: {', '.join(self.merge_mapping.keys())}")

        # Step 1: 已完成（功能资产清单已存在）
        print("\n✅ Step 1: 原 Agents 功能资产库已加载")
        print(f"   共 {len(self.original_inventory)} 个原 Agents")

        # Step 2: 对新 Agents 进行全量拆解（��验证过程中进行）
        print("\n✅ Step 2: 新 Agents 内容已加载")
        print(f"   共 {len(self.new_agents)} 个新 Agents")

        # Step 3: 三维度验证
        keyword_results = self.validate_keyword_coverage()
        scenario_results = self.validate_scenario_coverage()
        function_results = self.validate_function_logic_coverage()

        # Step 4: 生成实战测试查询
        test_queries = self.generate_test_queries()

        # 生成报告
        report = self.generate_report(keyword_results, scenario_results,
                                     function_results, test_queries)

        # 保存报告
        report_file = self.project_root / "docs/SEO_AGENTS_COVERAGE_VALIDATION_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print("\n" + "="*70)
        print(f"✅ 验证报告已生成: {report_file}")
        print("="*70)

        return keyword_results, scenario_results, function_results, test_queries


if __name__ == "__main__":
    validator = AgentCoverageValidator()
    validator.run()
