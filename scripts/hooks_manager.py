#!/usr/bin/env python3
"""
Hooks 管理脚本

╔════════════════════════════════════════════════════════════════════════════╗
║  ⚠️  严重安全警告 - 使用风险自负  ⚠️                                       ║
╠════════════════════════════════════════════════════════════════════════════╣
║  Hooks 会以你的用户权限自动执行任意 shell 命令，无需确认！                 ║
║                                                                            ║
║  • 你对配置的 hooks 安全性负全部责任                                       ║
║  • Hooks 可以修改、删除或访问你的用户账户能访问的任何文件                   ║
║  • 恶意或编写不当的 hooks 可能导致不可逆的数据丢失或系统损坏                ║
║  • Anthropic 不提供任何保证，对因 hook 使用导致的任何损害不承担责任         ║
║  • 只使用来自可信来源的 hooks，防止数据泄露                                ║
║  • 在添加任何 hook 前，请仔细审查并理解命令内容                            ║
║                                                                            ║
║  参考文档: https://docs.claude.com/en/docs/claude-code/hooks              ║
╚════════════════════════════════════════════════════════════════════════════╝

功能：
1. 浏览已配置的 Hooks (用户级, 项目级, 本地项目级)
2. 添加新的 Hook 配置到 settings.json
3. 修改现有 Hook 的配置
4. 删除 Hook 配置
5. 验证 Hooks 配置 (JSON 语法等)

注意：
• 此脚本管理的是 Hooks 的配置，而不是 Hooks 脚本文件本身
• Hooks 脚本文件应手动放置在项目或用户的 .claude/hooks/ 目录下
• 在 /hooks 菜单外修改 hooks 配置需要重启 Claude Code 才能生效
• 默认超时: 60 秒
• 同一事件的多个 hooks 会并行执行

使用方法：
python hooks_manager.py [list|add|edit|delete|validate] [--settings-path /path/to/settings.json]
"""

import os
import sys
import argparse
import json
import subprocess
import re
from pathlib import Path
from typing import Tuple, List

# 默认设置文件路径
DEFAULT_USER_SETTINGS = Path.home() / '.claude' / 'settings.json'
DEFAULT_PROJECT_SETTINGS = Path('.claude') / 'settings.json'
DEFAULT_LOCAL_SETTINGS = Path('.claude') / 'settings.local.json'

# Hook 配置常量
DEFAULT_HOOK_TIMEOUT = 60  # 秒，与官方默认值一致
MAX_HOOK_TIMEOUT = 600     # 最大 10 分钟
MIN_HOOK_TIMEOUT = 1       # 最小 1 秒

# 危险命令模式列表
DANGEROUS_PATTERNS = [
    (r'rm\s+-rf\s+/', "递归删除根目录"),
    (r'rm\s+-rf\s+\$HOME', "递归删除用户主目录"),
    (r'rm\s+-rf\s+~', "递归删除用户主目录"),
    (r'dd\s+if=/dev/(zero|random)', "使用 dd 写入大量数据"),
    (r'dd\s+of=/dev/sd[a-z]', "直接写入磁盘设备"),
    (r':\(\)\s*\{.*:\|:.*\}', "Fork bomb 攻击"),
    (r'>\s*/dev/sd[a-z]', "重定向到磁盘设备"),
    (r'mkfs\.\w+', "格式化文件系统"),
    (r'chmod\s+-R\s+777', "递归设置 777 权限"),
    (r'chmod\s+777\s+/', "设置根目录 777 权限"),
    (r'curl.*\|\s*bash', "下载并执行未知脚本"),
    (r'wget.*\|\s*sh', "下载并执行未知脚本"),
    (r'eval\s+\$\(curl', "执行远程命令"),
    (r'/etc/shadow', "访问影子密码文件"),
    (r'/etc/passwd', "访问密码文件"),
    (r'iptables\s+-F', "清空防火墙规则"),
    (r'sudo\s+rm', "使用 sudo 删除文件"),
]

# 敏感路径模式
SENSITIVE_PATH_PATTERNS = [
    r'\.\./\.\./',  # 路径遍历
    r'/etc/shadow',
    r'/etc/passwd',
    r'\.ssh/id_rsa',
    r'\.aws/credentials',
    r'\.kube/config',
]

# Hook 事件列表
VALID_HOOK_EVENTS = [
    'PreToolUse',
    'PostToolUse',
    'Notification',
    'UserPromptSubmit',
    'Stop',
    'SubagentStop',
    'PreCompact',
    'SessionStart',
    'SessionEnd'
]

# 支持 matcher 的事件
MATCHER_SUPPORTED_EVENTS = ['PreToolUse', 'PostToolUse']

# 已知的 Claude Code 工具列表
KNOWN_TOOLS = [
    'Read', 'Write', 'Edit', 'Bash', 'Glob', 'Grep',
    'Task', 'WebFetch', 'WebSearch', 'NotebookEdit',
    'TodoWrite', 'Skill', 'SlashCommand', 'AskUserQuestion',
    'ExitPlanMode', 'BashOutput', 'KillShell'
]

# JSON 输出模板（基于 9个Event要点.md 和 Reddit 案例）
HOOK_JSON_TEMPLATES = {
    'PreToolUse': {
        'auto-approve': {
            'description': '自动批准工具调用（白名单模式）',
            'template': {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'allow',
                    'permissionDecisionReason': 'Auto-approved based on whitelist'
                }
            },
            'use_case': 'PM2 只读命令、文档读取等安全操作'
        },
        'deny': {
            'description': '阻止工具调用',
            'template': {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': 'Security policy violation'
                }
            },
            'use_case': '敏感文件修改、危险命令等'
        },
        'ask': {
            'description': '要求用户确认',
            'template': {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'ask',
                    'permissionDecisionReason': 'Requires user confirmation'
                }
            },
            'use_case': 'PM2 restart/stop、数据库变更等需要确认的操作'
        }
    },
    'PostToolUse': {
        'add-context': {
            'description': '向 Claude 添加补充上下文',
            'template': {
                'hookSpecificOutput': {
                    'hookEventName': 'PostToolUse',
                    'additionalContext': 'File formatting corrected by prettier'
                }
            },
            'use_case': '自动格式化、静态检查结果等'
        },
        'block-with-reason': {
            'description': '阻止并提供原因（虽然工具已执行）',
            'template': {
                'decision': 'block',
                'reason': 'Post-execution validation failed'
            },
            'use_case': '工具执行后发现问题需要 Claude 注意'
        }
    },
    'UserPromptSubmit': {
        'skill-activation': {
            'description': 'Skills 自动激活（Reddit 案例核心）',
            'template': {
                'hookSpecificOutput': {
                    'hookEventName': 'UserPromptSubmit',
                    'additionalContext': 'SKILL ACTIVATION: backend-dev-guidelines, frontend-dev-guidelines'
                }
            },
            'use_case': '强制 Claude 加载相关技能'
        },
        'block-prompt': {
            'description': '阻止提示处理',
            'template': {
                'decision': 'block',
                'reason': 'Security policy: prompt contains credentials. Please remove secrets.'
            },
            'use_case': '敏感词检测、安全策略违规'
        }
    },
    'Stop': {
        'block-with-errors': {
            'description': '阻止停止（Reddit 构建检查器模式）',
            'template': {
                'decision': 'block',
                'reason': 'Build check failed: Found 7 TypeScript errors. Run /build-and-fix.'
            },
            'use_case': '构建错误 >= 阈值时阻止停止'
        }
    },
    'SessionStart': {
        'context-injection': {
            'description': '注入上下文（stdout 会被注入）',
            'template': None,  # SessionStart 直接使用 stdout，不需要 JSON
            'use_case': 'Dev Docs 上下文恢复、环境设置'
        }
    }
}


def validate_hook_command(command: str) -> Tuple[bool, List[str]]:
    """
    验证 hook 命令的安全性

    参数:
        command: 要验证的命令字符串

    返回:
        (is_safe, warnings):
            - is_safe: 布尔值，表示命令是否安全
            - warnings: 警告信息列表
    """
    warnings = []

    # 检查危险命令模式
    for pattern, description in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            warnings.append(f"⚠️  检测到危险模式: {description}")

    # 检查敏感路径
    for pattern in SENSITIVE_PATH_PATTERNS:
        if re.search(pattern, command):
            warnings.append(f"⚠️  检测到敏感路径模式: {pattern}")

    # 检查未引用的变量（可能导致命令注入）
    if re.search(r'\$\w+(?!["\'])', command) and '$CLAUDE_PROJECT_DIR' not in command:
        warnings.append("⚠️  检测到未引用的环境变量，可能存在注入风险")

    # 如果有警告，命令被认为是不安全的
    is_safe = len(warnings) == 0

    return is_safe, warnings


def validate_hook_path(path: str) -> Tuple[bool, str]:
    """
    验证 hook 脚本路径的安全性

    参数:
        path: 脚本路径

    返回:
        (is_safe, message): 是否安全和相关消息
    """
    # 检查路径遍历
    if '..' in path:
        return False, "路径包含 '..'，可能存在路径遍历攻击风险"

    # 如果是绝对路径，检查是否在敏感目录
    if os.path.isabs(path):
        sensitive_dirs = ['/etc/', '/sys/', '/proc/', '/dev/']
        for sensitive in sensitive_dirs:
            if path.startswith(sensitive):
                return False, f"路径指向敏感系统目录: {sensitive}"

    return True, ""


def validate_timeout(timeout: int) -> Tuple[bool, str]:
    """
    验证 timeout 配置

    参数:
        timeout: 超时时间（秒）

    返回:
        (is_valid, message): 是否有效和相关消息
    """
    if timeout < MIN_HOOK_TIMEOUT:
        return False, f"Timeout 不能小于 {MIN_HOOK_TIMEOUT} 秒"

    if timeout > MAX_HOOK_TIMEOUT:
        return False, f"Timeout 不能大于 {MAX_HOOK_TIMEOUT} 秒 (10 分钟)"

    return True, ""


def validate_matcher(event: str, matcher: str) -> Tuple[bool, str]:
    """
    验证 matcher 是否有效

    检查项：
    1. 事件是否支持 matcher（只有 PreToolUse/PostToolUse 支持）
    2. 正则表达式语法是否正确
    3. 工具名称是否正确（区分大小写）

    参数:
        event: Hook 事件名称
        matcher: 匹配模式字符串

    返回:
        (is_valid, error_message): 是否有效和错误消息
    """
    # 如果没有 matcher，直接通过
    if not matcher:
        return True, ""

    # 检查事件是否支持 matcher
    if event not in MATCHER_SUPPORTED_EVENTS:
        return False, f"Event '{event}' does not support matcher. Only {', '.join(MATCHER_SUPPORTED_EVENTS)} support matcher."

    # 验证正则表达式语法
    try:
        re.compile(matcher)
    except re.error as e:
        return False, f"Invalid regex pattern: {e}"

    # 检查是否有末尾多余的 |
    if matcher.endswith('|') or matcher.startswith('|'):
        return False, "Matcher should not start or end with '|'"

    # 提取工具名称（分割 | 和去除空格）
    tool_names = [name.strip() for name in matcher.split('|') if name.strip()]

    # 检查工具名称的大小写
    for tool in tool_names:
        # 跳过明显的正则表达式（包含特殊字符）
        if any(char in tool for char in ['*', '(', ')', '[', ']', '.', '^', '$']):
            continue

        # 检查是否在已知工具列表中
        if tool in KNOWN_TOOLS:
            continue

        # 检查是否是大小写错误
        tool_lower = tool.lower()
        matching_tool = next((t for t in KNOWN_TOOLS if t.lower() == tool_lower), None)

        if matching_tool:
            return False, f"Tool name is case-sensitive. Did you mean '{matching_tool}' instead of '{tool}'?"

        # 如果不在已知工具列表中，给出警告（但不阻止）
        # 因为可能是 MCP 工具或正则表达式
        # 我们不返回 False，但可以记录警告

    return True, ""


def generate_json_template(event: str, template_type: str = None) -> str:
    """
    生成 Hook JSON 输出模板

    基于 9个Event要点.md 和 Reddit 案例的 JSON 输出格式

    参数:
        event: Hook 事件名称
        template_type: 模板类型（如 'auto-approve', 'deny', 'skill-activation' 等）

    返回:
        格式化的 JSON 模板字符串
    """
    if event not in HOOK_JSON_TEMPLATES:
        return f"# No JSON templates available for event: {event}\n# Some events like SessionStart use stdout directly instead of JSON"

    event_templates = HOOK_JSON_TEMPLATES[event]

    # 如果没有指定模板类型，显示所有可用模板
    if not template_type:
        result = f"# Available JSON templates for {event}:\n\n"
        for ttype, tdata in event_templates.items():
            result += f"## {ttype}\n"
            result += f"# {tdata['description']}\n"
            result += f"# Use case: {tdata['use_case']}\n"
            if tdata['template']:
                result += f"{json.dumps(tdata['template'], indent=2, ensure_ascii=False)}\n\n"
            else:
                result += "# (No JSON template - uses stdout directly)\n\n"
        return result

    # 返回指定的模板
    if template_type not in event_templates:
        available = ', '.join(event_templates.keys())
        return f"# Template type '{template_type}' not found for {event}\n# Available types: {available}"

    template_data = event_templates[template_type]
    result = f"# {template_data['description']}\n"
    result += f"# Use case: {template_data['use_case']}\n\n"

    if template_data['template']:
        result += json.dumps(template_data['template'], indent=2, ensure_ascii=False)
    else:
        result += "# (No JSON template - uses stdout directly)"

    return result


def list_json_templates() -> str:
    """列出所有可用的 JSON 模板"""
    result = "# Hook JSON Templates (based on Reddit Case Study & 9 Event Specification)\n\n"

    for event, templates in HOOK_JSON_TEMPLATES.items():
        result += f"## {event}\n"
        for ttype, tdata in templates.items():
            result += f"  - {ttype}: {tdata['description']}\n"
        result += "\n"

    result += "# Usage:\n"
    result += "#   python hooks_manager.py show-template <event> [template_type]\n"
    result += "#   Example: python hooks_manager.py show-template PreToolUse auto-approve\n"

    return result


def generate_skill_rules_template(output_path: str = None) -> bool:
    """
    生成 skill-rules.json 模板文件

    基于 claude-code-infrastructure-showcase 的实际格式

    参数:
        output_path: 输出文件路径（默认：.claude/skills/skill-rules.json）

    返回:
        是否成功生成
    """
    if not output_path:
        output_path = Path('.claude/skills/skill-rules.json')
    else:
        output_path = Path(output_path)

    # 确保父目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 检查文件是否已存在
    if output_path.exists():
        print(f"⚠️  文件已存在: {output_path}")
        if not confirm_action("是否覆盖现有文件？", default=False):
            print("操作已取消")
            return False

    # 基本的 skill-rules.json 模板
    template = {
        "version": "1.0",
        "description": "Skill activation triggers for Claude Code. Controls when skills automatically suggest or block actions.",
        "skills": {
            "backend-dev-guidelines": {
                "type": "domain",
                "enforcement": "suggest",
                "priority": "high",
                "description": "Backend development patterns: Routes → Controllers → Services → Repositories",
                "promptTriggers": {
                    "keywords": [
                        "backend", "API", "endpoint", "route", "controller",
                        "service", "repository", "middleware", "database"
                    ],
                    "intentPatterns": [
                        "(create|add|implement).*?(route|endpoint|API)",
                        "(fix|debug).*?(backend|API)"
                    ]
                },
                "fileTriggers": {
                    "pathPatterns": [
                        "src/**/*.ts",
                        "backend/**/*.ts",
                        "api/**/*.ts"
                    ],
                    "pathExclusions": [
                        "**/*.test.ts",
                        "**/*.spec.ts"
                    ],
                    "contentPatterns": [
                        "router\\.",
                        "app\\.(get|post|put|delete)",
                        "export.*Controller"
                    ]
                }
            },
            "skill-developer": {
                "type": "domain",
                "enforcement": "suggest",
                "priority": "high",
                "description": "Meta-skill for creating and managing Claude Code skills",
                "promptTriggers": {
                    "keywords": [
                        "skill", "create skill", "skill system",
                        "skill-rules.json", "SKILL.md"
                    ],
                    "intentPatterns": [
                        "(create|add|modify).*?skill",
                        "skill.*?(system|activation)"
                    ]
                }
            }
        },
        "notes": {
            "enforcement_types": {
                "suggest": "Skill suggestion appears but doesn't block execution",
                "block": "Requires skill to be used before proceeding (guardrail)",
                "warn": "Shows warning but allows proceeding"
            },
            "priority_levels": {
                "critical": "Highest - Always trigger when matched",
                "high": "Important - Trigger for most matches",
                "medium": "Moderate - Trigger for clear matches",
                "low": "Optional - Trigger only for explicit matches"
            },
            "customization_required": {
                "pathPatterns": "⚠️ MUST CUSTOMIZE: Adjust to match YOUR project structure",
                "keywords": "Add domain-specific terms relevant to YOUR project",
                "intentPatterns": "Use regex for flexible user intent matching"
            }
        }
    }

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 成功生成 skill-rules.json 模板: {output_path}")
        print("\n⚠️  重要提示:")
        print("   • 必须修改 pathPatterns 以匹配你的项目结构！")
        print("   • 添加更多技能定义以覆盖你的项目需求")
        print("   • 参考: components/hooks/essential/skill-rules.json.template")
        print("\n验证语法:")
        print(f"   cat {output_path} | jq .")
        return True

    except Exception as e:
        print(f"\n❌ 生成文件失败: {e}")
        return False


def validate_skill_rules(rules_path: str = None) -> bool:
    """
    验证 skill-rules.json 文件的语法和结构

    参数:
        rules_path: skill-rules.json 文件路径（默认：.claude/skills/skill-rules.json）

    返回:
        是否有效
    """
    if not rules_path:
        rules_path = Path('.claude/skills/skill-rules.json')
    else:
        rules_path = Path(rules_path)

    print(f"\n正在验证: {rules_path}")

    # 检查文件是否存在
    if not rules_path.exists():
        print(f"❌ 文件不存在: {rules_path}")
        return False

    # 读取并解析 JSON
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 语法错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

    is_valid = True

    # 验证顶层字段
    if 'version' not in rules:
        print("⚠️  警告: 缺少 'version' 字段")

    if 'skills' not in rules:
        print("❌ 错误: 缺少 'skills' 字段")
        return False

    if not isinstance(rules['skills'], dict):
        print("❌ 错误: 'skills' 必须是字典类型")
        return False

    # 验证每个技能配置
    for skill_name, skill_config in rules['skills'].items():
        print(f"\n检查技能: {skill_name}")

        # 验证必需字段
        required_fields = ['type', 'enforcement', 'priority', 'description']
        for field in required_fields:
            if field not in skill_config:
                print(f"  ⚠️  警告: 缺少 '{field}' 字段")

        # 验证 enforcement 值
        if 'enforcement' in skill_config:
            valid_enforcements = ['suggest', 'block', 'warn']
            if skill_config['enforcement'] not in valid_enforcements:
                print(f"  ❌ 错误: enforcement '{skill_config['enforcement']}' 无效")
                print(f"     有效值: {', '.join(valid_enforcements)}")
                is_valid = False

        # 验证 priority 值
        if 'priority' in skill_config:
            valid_priorities = ['critical', 'high', 'medium', 'low']
            if skill_config['priority'] not in valid_priorities:
                print(f"  ❌ 错误: priority '{skill_config['priority']}' 无效")
                print(f"     有效值: {', '.join(valid_priorities)}")
                is_valid = False

        # 验证触发器
        if 'promptTriggers' not in skill_config and 'fileTriggers' not in skill_config:
            print(f"  ⚠️  警告: 既没有 promptTriggers 也没有 fileTriggers")

        # 验证 intentPatterns 正则表达式
        if 'promptTriggers' in skill_config and 'intentPatterns' in skill_config['promptTriggers']:
            patterns = skill_config['promptTriggers']['intentPatterns']
            if isinstance(patterns, list):
                for pattern in patterns:
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        print(f"  ❌ 错误: intentPattern 正则无效: {pattern}")
                        print(f"     错误: {e}")
                        is_valid = False

        print(f"  ✓ 技能 '{skill_name}' 检查完成")

    if is_valid:
        print(f"\n✅ skill-rules.json 验证通过")
        print(f"\n下一步:")
        print(f"   1. 确保 pathPatterns 匹配你的项目结构")
        print(f"   2. 确保 user-prompt-submit-skill-activation.sh 已安装")
        print(f"   3. 测试: 在 Claude Code 中输入相关关键词，应该看到技能激活提示")
    else:
        print(f"\n❌ skill-rules.json 验证失败，请修复上述错误")

    return is_valid


# ============================================================================
# Hook 管道生成器 (Pipeline Generator)
# ============================================================================

# 项目模板定义
PROJECT_TEMPLATES = {
    "backend-api": {
        "name": "Backend API (Node.js/Express/PM2)",
        "description": "后端 API 项目，使用 PM2 管理服务，需要安全守卫和构建检查",
        "hooks": {
            "UserPromptSubmit": [
                {
                    "type": "command",
                    "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/user-prompt-submit-skill-activation.sh",
                    "timeout": 5
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-file-edit-tracker.sh"
                        }
                    ],
                    "timeout": 2
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-build-checker.sh"
                        }
                    ],
                    "timeout": 120
                }
            ],
            "SessionStart": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start-dev-docs-injector.sh"
                        }
                    ],
                    "timeout": 5
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-pm2-permission-gatekeeper.sh"
                        }
                    ],
                    "timeout": 2
                },
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-sensitive-file-guard.sh"
                        }
                    ],
                    "timeout": 2
                }
            ],
            "PreCompact": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-compact-dev-docs-snapshot.sh"
                        }
                    ],
                    "timeout": 10
                }
            ]
        },
        "required_files": [
            ".claude/hooks/user-prompt-submit-skill-activation.sh",
            ".claude/hooks/post-tool-use-file-edit-tracker.sh",
            ".claude/hooks/stop-build-checker.sh",
            ".claude/hooks/session-start-dev-docs-injector.sh",
            ".claude/hooks/pre-tool-use-pm2-permission-gatekeeper.sh",
            ".claude/hooks/pre-tool-use-sensitive-file-guard.sh",
            ".claude/hooks/pre-compact-dev-docs-snapshot.sh",
            ".claude/skills/skill-rules.json",
            ".claude/hooks/build-checker.json"
        ]
    },
    "frontend-spa": {
        "name": "Frontend SPA (React/Vue/Prettier)",
        "description": "前端单页应用，需要代码格式化、安全守卫和桌面通知",
        "hooks": {
            "UserPromptSubmit": [
                {
                    "type": "command",
                    "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/user-prompt-submit-skill-activation.sh",
                    "timeout": 5
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-file-edit-tracker.sh"
                        }
                    ],
                    "timeout": 2
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-build-checker.sh"
                        }
                    ],
                    "timeout": 120
                }
            ],
            "SessionStart": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start-dev-docs-injector.sh"
                        }
                    ],
                    "timeout": 5
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-sensitive-file-guard.sh"
                        }
                    ],
                    "timeout": 2
                }
            ],
            "SessionEnd": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-end-batch-prettier.sh"
                        }
                    ],
                    "timeout": 60
                }
            ],
            "Notification": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/notification-desktop-notifier.sh"
                        }
                    ],
                    "timeout": 5
                }
            ],
            "PreCompact": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-compact-dev-docs-snapshot.sh"
                        }
                    ],
                    "timeout": 10
                }
            ]
        },
        "required_files": [
            ".claude/hooks/user-prompt-submit-skill-activation.sh",
            ".claude/hooks/post-tool-use-file-edit-tracker.sh",
            ".claude/hooks/stop-build-checker.sh",
            ".claude/hooks/session-start-dev-docs-injector.sh",
            ".claude/hooks/pre-tool-use-sensitive-file-guard.sh",
            ".claude/hooks/session-end-batch-prettier.sh",
            ".claude/hooks/notification-desktop-notifier.sh",
            ".claude/hooks/pre-compact-dev-docs-snapshot.sh",
            ".claude/skills/skill-rules.json",
            ".claude/hooks/build-checker.json"
        ]
    },
    "fullstack-monorepo": {
        "name": "Fullstack Monorepo (All Features)",
        "description": "全栈 Monorepo 项目，包含所有可选 hooks",
        "hooks": {
            "UserPromptSubmit": [
                {
                    "type": "command",
                    "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/user-prompt-submit-skill-activation.sh",
                    "timeout": 5
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-file-edit-tracker.sh"
                        }
                    ],
                    "timeout": 2
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-build-checker.sh"
                        }
                    ],
                    "timeout": 180
                }
            ],
            "SessionStart": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start-dev-docs-injector.sh"
                        }
                    ],
                    "timeout": 5
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-pm2-permission-gatekeeper.sh"
                        }
                    ],
                    "timeout": 2
                },
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-sensitive-file-guard.sh"
                        }
                    ],
                    "timeout": 2
                }
            ],
            "PreCompact": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-compact-dev-docs-snapshot.sh"
                        }
                    ],
                    "timeout": 10
                }
            ],
            "SessionEnd": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-end-batch-prettier.sh"
                        }
                    ],
                    "timeout": 60
                }
            ],
            "Notification": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/notification-desktop-notifier.sh"
                        }
                    ],
                    "timeout": 5
                }
            ]
        },
        "required_files": [
            ".claude/hooks/user-prompt-submit-skill-activation.sh",
            ".claude/hooks/post-tool-use-file-edit-tracker.sh",
            ".claude/hooks/stop-build-checker.sh",
            ".claude/hooks/session-start-dev-docs-injector.sh",
            ".claude/hooks/pre-tool-use-pm2-permission-gatekeeper.sh",
            ".claude/hooks/pre-tool-use-sensitive-file-guard.sh",
            ".claude/hooks/pre-compact-dev-docs-snapshot.sh",
            ".claude/hooks/session-end-batch-prettier.sh",
            ".claude/hooks/notification-desktop-notifier.sh",
            ".claude/skills/skill-rules.json",
            ".claude/hooks/build-checker.json"
        ]
    },
    "minimal": {
        "name": "Minimal (Essential Hooks Only)",
        "description": "最小配置，只包含必需的 essential hooks",
        "hooks": {
            "UserPromptSubmit": [
                {
                    "type": "command",
                    "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/user-prompt-submit-skill-activation.sh",
                    "timeout": 5
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-file-edit-tracker.sh"
                        }
                    ],
                    "timeout": 2
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-build-checker.sh"
                        }
                    ],
                    "timeout": 120
                }
            ],
            "SessionStart": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start-dev-docs-injector.sh"
                        }
                    ],
                    "timeout": 5
                }
            ]
        },
        "required_files": [
            ".claude/hooks/user-prompt-submit-skill-activation.sh",
            ".claude/hooks/post-tool-use-file-edit-tracker.sh",
            ".claude/hooks/stop-build-checker.sh",
            ".claude/hooks/session-start-dev-docs-injector.sh",
            ".claude/skills/skill-rules.json",
            ".claude/hooks/build-checker.json"
        ]
    }
}


def list_project_templates():
    """列出所有可用的项目模板"""
    print("\n" + "="*80)
    print("可用的项目模板 (Project Templates)")
    print("="*80)

    for template_id, template_data in PROJECT_TEMPLATES.items():
        print(f"\n📦 {template_id}")
        print(f"   名称: {template_data['name']}")
        print(f"   描述: {template_data['description']}")
        print(f"   Hook 事件数: {len(template_data['hooks'])}")
        print(f"   所需文件数: {len(template_data['required_files'])}")


def generate_pipeline(template_id: str, output_path: str = None, check_files: bool = True) -> bool:
    """
    根据项目模板生成 hooks 管道配置

    参数:
        template_id: 模板 ID（backend-api, frontend-spa, fullstack-monorepo, minimal）
        output_path: 输出路径（默认: .claude/settings.json）
        check_files: 是否检查所需文件是否存在

    返回:
        bool: 是否成功生成
    """
    if template_id not in PROJECT_TEMPLATES:
        print(f"\n❌ 无效的模板 ID: {template_id}")
        print(f"有效的模板: {', '.join(PROJECT_TEMPLATES.keys())}")
        return False

    template = PROJECT_TEMPLATES[template_id]

    print("\n" + "="*80)
    print(f"生成 Hook 管道: {template['name']}")
    print("="*80)
    print(f"\n描述: {template['description']}")

    # 检查所需文件
    if check_files:
        print(f"\n正在检查所需文件...")
        missing_files = []
        for required_file in template['required_files']:
            # 替换 $CLAUDE_PROJECT_DIR
            file_path = required_file.replace("$CLAUDE_PROJECT_DIR/", "")
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            print(f"\n⚠️  缺少以下文件:")
            for missing_file in missing_files:
                print(f"   ❌ {missing_file}")
            print(f"\n💡 提示: 请先从 components/hooks/ 复制所需的 hook 脚本到 .claude/hooks/")
            if not confirm_action("\n是否继续生成配置（即使文件缺失）？", default=False):
                print("操作已取消")
                return False
        else:
            print(f"✓ 所有所需文件都存在")

    # 确定输出路径
    if not output_path:
        output_path = ".claude/settings.json"

    output_file = Path(output_path)

    # 检查文件是否存在
    if output_file.exists():
        print(f"\n⚠️  文件已存在: {output_file}")
        if not confirm_action("是否覆盖现有配置？", default=False):
            print("操作已取消")
            return False

    # 生成配置
    settings = {
        "hooks": template['hooks']
    }

    # 保存配置
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 成功生成 Hook 管道配置: {output_file}")
        print(f"\n📊 配置摘要:")
        print(f"   • Hook 事件数: {len(template['hooks'])}")

        total_hooks = sum(len(hooks) for hooks in template['hooks'].values())
        print(f"   • 总 Hook 数: {total_hooks}")

        print(f"\n下一步:")
        print(f"   1. 复制所需的 hook 脚本到 .claude/hooks/")
        print(f"   2. 设置脚本可执行权限: chmod +x .claude/hooks/*.sh")
        print(f"   3. 生成 skill-rules.json: python scripts/hooks_manager.py generate-skill-rules")
        print(f"   4. 生成 build-checker.json 并配置项目路径")
        print(f"   5. 重启 Claude Code 使配置生效")

        return True
    except Exception as e:
        print(f"\n❌ 保存配置失败: {e}")
        return False


def interactive_wizard():
    """交互式向导，引导用户生成 hooks 管道"""
    print("\n" + "="*80)
    print("🧙 Hook 管道生成器 - 交互式向导")
    print("="*80)
    print("\n欢迎使用 Hook 管道生成器！")
    print("此向导将帮助你根据项目类型生成适合的 hooks 配置。\n")

    # 步骤 1: 选择项目类型
    print("步骤 1/3: 选择项目类型")
    print("-"*80)

    templates_list = list(PROJECT_TEMPLATES.items())
    for i, (template_id, template_data) in enumerate(templates_list, 1):
        print(f"\n  {i}. {template_data['name']}")
        print(f"     {template_data['description']}")

    while True:
        try:
            choice = input(f"\n请选择项目类型 (1-{len(templates_list)}): ").strip()
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(templates_list):
                selected_template_id = templates_list[choice_idx][0]
                selected_template = templates_list[choice_idx][1]
                break
            else:
                print(f"❌ 无效的选择，请输入 1-{len(templates_list)}")
        except ValueError:
            print(f"❌ 无效的输入，请输入数字")
        except (KeyboardInterrupt, EOFError):
            print("\n\n操作已取消")
            return False

    print(f"\n✓ 已选择: {selected_template['name']}")

    # 步骤 2: 选择输出路径
    print(f"\n步骤 2/3: 选择输出路径")
    print("-"*80)
    print(f"默认路径: .claude/settings.json")

    output_path = input(f"输出路径 (直接回车使用默认路径): ").strip()
    if not output_path:
        output_path = ".claude/settings.json"

    print(f"✓ 输出路径: {output_path}")

    # 步骤 3: 确认
    print(f"\n步骤 3/3: 确认配置")
    print("-"*80)
    print(f"  模板: {selected_template['name']}")
    print(f"  输出: {output_path}")
    print(f"  Hook 事件数: {len(selected_template['hooks'])}")

    total_hooks = sum(len(hooks) for hooks in selected_template['hooks'].values())
    print(f"  总 Hook 数: {total_hooks}")

    if not confirm_action("\n确认生成配置？", default=True):
        print("操作已取消")
        return False

    # 生成配置
    return generate_pipeline(selected_template_id, output_path, check_files=True)


def confirm_action(message: str, default: bool = False) -> bool:
    """
    向用户请求确认

    参数:
        message: 确认消息
        default: 默认选项 (True=yes, False=no)

    返回:
        用户的确认结果
    """
    suffix = " [Y/n]: " if default else " [y/N]: "

    try:
        response = input(message + suffix).strip().lower()

        if not response:  # 用户直接按回车
            return default

        return response in ['y', 'yes', '是']
    except (KeyboardInterrupt, EOFError):
        print("\n操作已取消")
        return False


def get_settings_file(settings_path=None, scope='project'):
    """获取要操作的 settings.json 文件路径"""
    if settings_path:
        return Path(settings_path)

    if scope == 'user':
        return DEFAULT_USER_SETTINGS
    elif scope == 'project':
        return DEFAULT_PROJECT_SETTINGS
    else:
        raise ValueError("Scope must be 'user' or 'project'")

def load_settings(settings_path):
    """加载 settings.json 文件"""
    settings_file = Path(settings_path)
    if not settings_file.exists():
        # 如果文件不存在，返回空配置
        return {"hooks": {}}
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {settings_file}: {e}")
        return None
    except Exception as e:
        print(f"Error: Could not read {settings_file}: {e}")
        return None

def save_settings(settings_path, settings):
    """保存 settings.json 文件"""
    settings_file = Path(settings_path)
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # 格式化 JSON 输出
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error: Could not write to {settings_file}: {e}")
        return False

def get_hooks(settings_path=None, scope='project'):
    """获取指定范围内的所有 Hooks 配置

    优先级顺序：项目级 > 插件级 > 用户级

    注意：项目级自动包含 settings.json 和 settings.local.json
    """
    if scope == 'all':
        # 按优先级顺序加载所有设置（从低到高）
        all_hooks = {}

        # 1. 用户级 (最低优先级)
        settings = load_settings(DEFAULT_USER_SETTINGS)
        if settings and 'hooks' in settings:
            for event, hook_list in settings['hooks'].items():
                if event not in all_hooks:
                    all_hooks[event] = []
                for hook_config in hook_list:
                    hook_config_with_scope = hook_config.copy()
                    hook_config_with_scope['scope'] = 'user'
                    hook_config_with_scope['settings_file'] = str(DEFAULT_USER_SETTINGS)
                    all_hooks[event].append(hook_config_with_scope)

        # 2. 插件级 (中等优先级)
        plugins_dir = Path.home() / '.claude' / 'plugins'
        if plugins_dir.exists():
            for plugin_dir in plugins_dir.iterdir():
                if plugin_dir.is_dir():
                    plugin_hooks_file = plugin_dir / 'hooks' / 'hooks.json'
                    if plugin_hooks_file.exists():
                        plugin_settings = load_settings(plugin_hooks_file)
                        if plugin_settings and 'hooks' in plugin_settings:
                            for event, hook_list in plugin_settings['hooks'].items():
                                if event not in all_hooks:
                                    all_hooks[event] = []
                                for hook_config in hook_list:
                                    hook_config_with_scope = hook_config.copy()
                                    hook_config_with_scope['scope'] = f'plugin:{plugin_dir.name}'
                                    hook_config_with_scope['settings_file'] = str(plugin_hooks_file)
                                    all_hooks[event].append(hook_config_with_scope)

        # 3. 项目级 (最高优先级)
        # 项目级包含 settings.json 和 settings.local.json
        # 先加载 settings.json
        settings = load_settings(DEFAULT_PROJECT_SETTINGS)
        if settings and 'hooks' in settings:
            for event, hook_list in settings['hooks'].items():
                if event not in all_hooks:
                    all_hooks[event] = []
                for hook_config in hook_list:
                    hook_config_with_scope = hook_config.copy()
                    hook_config_with_scope['scope'] = 'project'
                    hook_config_with_scope['settings_file'] = str(DEFAULT_PROJECT_SETTINGS)
                    all_hooks[event].append(hook_config_with_scope)

        # 再加载 settings.local.json (会追加，优先级更高)
        local_settings = load_settings(DEFAULT_LOCAL_SETTINGS)
        if local_settings and 'hooks' in local_settings:
            for event, hook_list in local_settings['hooks'].items():
                if event not in all_hooks:
                    all_hooks[event] = []
                for hook_config in hook_list:
                    hook_config_with_scope = hook_config.copy()
                    hook_config_with_scope['scope'] = 'project:local'
                    hook_config_with_scope['settings_file'] = str(DEFAULT_LOCAL_SETTINGS)
                    all_hooks[event].append(hook_config_with_scope)

        return all_hooks

    elif scope == 'plugin':
        # 列出所有插件的 hooks
        all_plugin_hooks = {}
        plugins_dir = Path.home() / '.claude' / 'plugins'
        if plugins_dir.exists():
            for plugin_dir in plugins_dir.iterdir():
                if plugin_dir.is_dir():
                    plugin_hooks_file = plugin_dir / 'hooks' / 'hooks.json'
                    if plugin_hooks_file.exists():
                        plugin_settings = load_settings(plugin_hooks_file)
                        if plugin_settings and 'hooks' in plugin_settings:
                            for event, hook_list in plugin_settings['hooks'].items():
                                if event not in all_plugin_hooks:
                                    all_plugin_hooks[event] = []
                                for hook_config in hook_list:
                                    hook_config_with_scope = hook_config.copy()
                                    hook_config_with_scope['scope'] = f'plugin:{plugin_dir.name}'
                                    hook_config_with_scope['settings_file'] = str(plugin_hooks_file)
                                    all_plugin_hooks[event].append(hook_config_with_scope)
        return all_plugin_hooks

    elif scope == 'project':
        # 项目级自动加载 settings.json 和 settings.local.json
        hooks_with_scope = {}

        # 先加载 settings.json
        if settings_path:
            settings_file = Path(settings_path)
        else:
            settings_file = DEFAULT_PROJECT_SETTINGS

        settings = load_settings(settings_file)
        if settings and 'hooks' in settings:
            for event, hook_list in settings['hooks'].items():
                hooks_with_scope[event] = []
                for hook_config in hook_list:
                    hook_config_with_scope = hook_config.copy()
                    hook_config_with_scope['scope'] = 'project'
                    hook_config_with_scope['settings_file'] = str(settings_file)
                    hooks_with_scope[event].append(hook_config_with_scope)

        # 再加载 settings.local.json (如果不是自定义路径)
        if not settings_path:
            local_settings = load_settings(DEFAULT_LOCAL_SETTINGS)
            if local_settings and 'hooks' in local_settings:
                for event, hook_list in local_settings['hooks'].items():
                    if event not in hooks_with_scope:
                        hooks_with_scope[event] = []
                    for hook_config in hook_list:
                        hook_config_with_scope = hook_config.copy()
                        hook_config_with_scope['scope'] = 'project:local'
                        hook_config_with_scope['settings_file'] = str(DEFAULT_LOCAL_SETTINGS)
                        hooks_with_scope[event].append(hook_config_with_scope)

        return hooks_with_scope

    else:
        # user scope
        settings_file = get_settings_file(settings_path, scope)
        settings = load_settings(settings_file)
        if settings and 'hooks' in settings:
            hooks_with_scope = {}
            for event, hook_list in settings['hooks'].items():
                hooks_with_scope[event] = []
                for hook_config in hook_list:
                    hook_config_with_scope = hook_config.copy()
                    hook_config_with_scope['scope'] = scope
                    hook_config_with_scope['settings_file'] = str(settings_file)
                    hooks_with_scope[event].append(hook_config_with_scope)
            return hooks_with_scope
        return {}

def add_hook(event, matcher, hook_command, settings_path=None, scope='project', timeout=None):
    """
    添加一个新的 Hook 配置（包含安全检查）

    参数:
        event: Hook 事件名称
        matcher: 工具匹配模式（可选）
        hook_command: 要执行的命令
        settings_path: settings.json 路径（可选）
        scope: 作用域 ('user', 'project', 'local')
        timeout: 超时时间（秒，可选）

    返回:
        布尔值，表示是否成功添加
    """
    print("\n" + "="*80)
    print("开始添加 Hook 配置")
    print("="*80)

    # ====== 1. 事件验证 ======
    if event not in VALID_HOOK_EVENTS:
        print(f"\n❌ 无效的事件类型: {event}")
        print(f"有效的事件类型: {', '.join(VALID_HOOK_EVENTS)}")
        return False

    # ====== 2. Matcher 验证 ======
    if matcher:
        print(f"\n正在验证 matcher: {matcher}")
        is_matcher_valid, matcher_error = validate_matcher(event, matcher)
        if not is_matcher_valid:
            print(f"❌ Matcher 验证失败: {matcher_error}")
            return False
        print(f"✓ Matcher 验证通过")
    elif event in MATCHER_SUPPORTED_EVENTS:
        print(f"\n💡 提示: {event} 支持 matcher 参数来匹配特定工具")
        print(f"   例如: --matcher 'Edit|Write' 或 --matcher 'Bash'")

    # ====== 3. 作用域警告 ======
    if scope == 'user':
        print("\n🚨 警告: 你正在添加用户级 Hook！")
        print("   • 此 hook 将应用到你的所有项目")
        print("   • 如果存在安全问题，影响范围极大")
        print("   • 建议只对完全信任的命令使用 user 作用域")
        if not confirm_action("\n确定要添加用户级 Hook 吗？", default=False):
            print("操作已取消")
            return False

    # ====== 4. 命令安全检查 ======
    print(f"\n正在检查命令安全性...")
    print(f"命令: {hook_command}")

    is_safe, warnings = validate_hook_command(hook_command)

    if not is_safe:
        print("\n🚨 安全警告:")
        for warning in warnings:
            print(f"   {warning}")
        print("\n此命令可能存在安全风险！")
        if not confirm_action("你确定要继续添加此 hook 吗？", default=False):
            print("操作已取消")
            return False
        print("\n⚠️  警告已确认，继续添加...")
    else:
        print("✓ 命令初步检查通过")

    # ====== 5. 路径验证（如果命令包含脚本路径）======
    # 尝试提取可能的脚本路径
    script_path_match = re.search(r'(["\']?)([/\w.-]+\.(?:sh|py|js|ts))\1', hook_command)
    if script_path_match:
        script_path = script_path_match.group(2)
        is_path_safe, path_msg = validate_hook_path(script_path)
        if not is_path_safe:
            print(f"\n⚠️  路径安全警告: {path_msg}")
            if not confirm_action("继续添加此 hook？", default=False):
                print("操作已取消")
                return False

    # ====== 6. Timeout 验证 ======
    if timeout is not None:
        is_timeout_valid, timeout_msg = validate_timeout(timeout)
        if not is_timeout_valid:
            print(f"\n❌ Timeout 配置错误: {timeout_msg}")
            return False

        if timeout > DEFAULT_HOOK_TIMEOUT:
            print(f"\n⚠️  注意: Timeout {timeout}秒 超过默认值 {DEFAULT_HOOK_TIMEOUT}秒")
    else:
        timeout_display = f"使用默认值 {DEFAULT_HOOK_TIMEOUT}秒"
        print(f"✓ Timeout: {timeout_display}")

    # ====== 7. 加载和修改配置 ======
    settings_file = get_settings_file(settings_path, scope)
    settings = load_settings(settings_file)

    if settings is None:
        print(f"\n❌ 无法加载配置文件: {settings_file}")
        return False

    if 'hooks' not in settings:
        settings['hooks'] = {}

    if event not in settings['hooks']:
        settings['hooks'][event] = []

    # ====== 8. 构造新的 hook 配置 ======
    new_hook = {
        "type": "command",
        "command": hook_command
    }
    if matcher:
        new_hook["matcher"] = matcher
    if timeout:
        new_hook["timeout"] = timeout

    # ====== 9. 最终确认 ======
    print("\n" + "-"*80)
    print("即将添加以下 Hook 配置:")
    print(f"  事件 (Event): {event}")
    print(f"  匹配器 (Matcher): {matcher or '无'}")
    print(f"  命令 (Command): {hook_command}")
    print(f"  超时 (Timeout): {timeout or f'{DEFAULT_HOOK_TIMEOUT} (默认)'}秒")
    print(f"  作用域 (Scope): {scope}")
    print(f"  配置文件: {settings_file}")
    print("-"*80)

    if not confirm_action("\n确认添加此 Hook？", default=True):
        print("操作已取消")
        return False

    # ====== 10. 保存配置 ======
    settings['hooks'][event].append(new_hook)

    if save_settings(settings_file, settings):
        print(f"\n✅ 成功添加 Hook for event '{event}' in {settings_file}")
        print("\n⚠️  重要提示:")
        print("   • 在 /hooks 菜单外修改的配置需要重启 Claude Code 才能生效")
        print("   • 请确保 hook 脚本文件有可执行权限 (chmod +x)")
        print("   • 建议先在测试环境验证 hook 的行为")
        return True
    else:
        print(f"\n❌ 保存配置失败")
        return False

def edit_hook(event, index, new_matcher=None, new_command=None, new_timeout=None, settings_path=None, scope='project'):
    """编辑一个现有的 Hook 配置"""
    settings_file = get_settings_file(settings_path, scope)
    settings = load_settings(settings_file)
    
    if settings is None or 'hooks' not in settings or event not in settings['hooks']:
        print(f"Error: No hooks found for event '{event}' in {settings_file}")
        return False
        
    hooks_list = settings['hooks'][event]
    if index < 0 or index >= len(hooks_list):
        print(f"Error: Invalid hook index {index} for event '{event}'")
        return False
        
    # 更新 hook 配置
    if new_matcher is not None:
        if new_matcher == "":
            hooks_list[index].pop("matcher", None)  # 删除 matcher 字段
        else:
            hooks_list[index]["matcher"] = new_matcher
            
    if new_command is not None:
        hooks_list[index]["command"] = new_command
        
    if new_timeout is not None:
        if new_timeout <= 0:
            hooks_list[index].pop("timeout", None)  # 删除 timeout 字段
        else:
            hooks_list[index]["timeout"] = new_timeout
    
    if save_settings(settings_file, settings):
        print(f"✅ Successfully edited hook at index {index} for event '{event}' in {settings_file}")
        print("\n⚠️  重要提示:")
        print("   • 在 /hooks 菜单外修改的配置需要重启 Claude Code 才能生效")
        return True
    else:
        return False

def delete_hook(event, index, settings_path=None, scope='project'):
    """删除一个 Hook 配置"""
    settings_file = get_settings_file(settings_path, scope)
    settings = load_settings(settings_file)
    
    if settings is None or 'hooks' not in settings or event not in settings['hooks']:
        print(f"Error: No hooks found for event '{event}' in {settings_file}")
        return False
        
    hooks_list = settings['hooks'][event]
    if index < 0 or index >= len(hooks_list):
        print(f"Error: Invalid hook index {index} for event '{event}'")
        return False
        
    # 删除 hook
    deleted_hook = hooks_list.pop(index)
    
    # 如果事件下没有更多 hooks，删除事件键
    if not hooks_list:
        del settings['hooks'][event]
    
    if save_settings(settings_file, settings):
        print(f"✅ Successfully deleted hook at index {index} for event '{event}' from {settings_file}")
        print("\n⚠️  重要提示:")
        print("   • 在 /hooks 菜单外修改的配置需要重启 Claude Code 才能生效")
        return True
    else:
        # 如果保存失败，恢复删除的 hook
        if event not in settings['hooks']:
            settings['hooks'][event] = []
        settings['hooks'][event].insert(index, deleted_hook)
        return False

def validate_hooks(settings_path=None, scope='project'):
    """验证 Hooks 配置"""
    settings_file = get_settings_file(settings_path, scope)
    settings = load_settings(settings_file)
    
    if settings is None:
        return False
        
    if 'hooks' not in settings:
        print(f"No hooks configuration found in {settings_file}")
        return True  # 没有配置不算错误
        
    hooks = settings['hooks']
    is_valid = True
    
    # 验证 hooks 结构
    if not isinstance(hooks, dict):
        print(f"Error: 'hooks' in {settings_file} should be a dictionary")
        return False
        
    for event, hook_list in hooks.items():
        if not isinstance(hook_list, list):
            print(f"Error: hooks for event '{event}' in {settings_file} should be a list")
            is_valid = False
            continue
            
        for i, hook_config in enumerate(hook_list):
            # 验证每个 hook 配置
            if not isinstance(hook_config, dict):
                print(f"Error: hook at index {i} for event '{event}' in {settings_file} should be a dictionary")
                is_valid = False
                continue
                
            if 'type' not in hook_config or hook_config['type'] != 'command':
                print(f"Error: hook at index {i} for event '{event}' in {settings_file} must have 'type': 'command'")
                is_valid = False
                
            if 'command' not in hook_config:
                print(f"Error: hook at index {i} for event '{event}' in {settings_file} is missing 'command'")
                is_valid = False
                
            if 'timeout' in hook_config and not isinstance(hook_config['timeout'], (int, float)):
                print(f"Error: 'timeout' for hook at index {i} for event '{event}' in {settings_file} must be a number")
                is_valid = False
                
    if is_valid:
        print(f"Hooks configuration in {settings_file} is valid.")
        
    return is_valid

def main():
    parser = argparse.ArgumentParser(
        description='Manage Claude Code Hooks Configuration',
        epilog='Examples:\n'
               '  %(prog)s list --scope all\n'
               '  %(prog)s add --event PreToolUse --matcher "Edit|Write" --command "echo test"\n'
               '  %(prog)s show-template PreToolUse auto-approve\n'
               '  %(prog)s list-templates\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('action',
                       choices=['list', 'add', 'edit', 'delete', 'validate',
                                'show-template', 'list-templates',
                                'generate-skill-rules', 'validate-skill-rules',
                                'list-project-templates', 'generate-pipeline', 'wizard'],
                       help='Action to perform')
    
    # 通用参数
    parser.add_argument('--settings-path', help='Path to the settings.json file')
    parser.add_argument('--scope', choices=['user', 'project', 'plugin', 'all'], default='project',
                        help='Scope of the settings file (user: ~/.claude/settings.json, project: .claude/settings.json + settings.local.json, plugin: from plugins, all: all scopes)')
    
    # add/edit/delete 特定参数
    parser.add_argument('--event', help='Hook event (e.g., PreToolUse, PostToolUse, UserPromptSubmit)')
    parser.add_argument('--matcher', help='Tool matcher pattern (for PreToolUse/PostToolUse)')
    parser.add_argument('--command', help='Hook command to execute')
    parser.add_argument('--timeout', type=int, help='Hook timeout in seconds')
    parser.add_argument('--index', type=int, help='Index of the hook to edit/delete')

    # show-template 特定参数
    parser.add_argument('--template-type', help='Template type (e.g., auto-approve, deny, skill-activation)')

    # skill-rules 特定参数
    parser.add_argument('--rules-path', help='Path to skill-rules.json file (default: .claude/skills/skill-rules.json)')

    # pipeline generator 特定参数
    parser.add_argument('--template-id', help='Project template ID (backend-api, frontend-spa, fullstack-monorepo, minimal)')
    parser.add_argument('--output', help='Output path for generated settings.json (default: .claude/settings.json)')
    parser.add_argument('--no-check-files', action='store_true', help='Skip checking if required files exist')

    args = parser.parse_args()
    
    if args.action == 'list':
        hooks = get_hooks(settings_path=args.settings_path, scope=args.scope)
        if not hooks:
            print("No hooks found.")
        else:
            print(f"Hooks configuration:")
            for event, hook_list in hooks.items():
                print(f"  Event: {event}")
                for i, hook_config in enumerate(hook_list):
                    scope_info = hook_config.get('scope', 'unknown')
                    file_info = hook_config.get('settings_file', 'unknown')
                    print(f"    [{i}] Matcher: {hook_config.get('matcher', 'None')} (Scope: {scope_info}, File: {file_info})")
                    print(f"        Command: {hook_config.get('command', 'None')}")
                    if 'timeout' in hook_config:
                        print(f"        Timeout: {hook_config['timeout']}s")
                        
    elif args.action == 'add':
        if not args.event or not args.command:
            print("Error: --event and --command are required for add action")
            sys.exit(1)
        add_hook(args.event, args.matcher, args.command, 
                 settings_path=args.settings_path, scope=args.scope, timeout=args.timeout)
        
    elif args.action == 'edit':
        if not args.event or args.index is None:
            print("Error: --event and --index are required for edit action")
            sys.exit(1)
        if not any([args.matcher is not None, args.command is not None, args.timeout is not None]):
            print("Error: At least one of --matcher, --command, or --timeout must be provided for edit action")
            sys.exit(1)
        edit_hook(args.event, args.index, 
                  new_matcher=args.matcher, new_command=args.command, new_timeout=args.timeout,
                  settings_path=args.settings_path, scope=args.scope)
        
    elif args.action == 'delete':
        if not args.event or args.index is None:
            print("Error: --event and --index are required for delete action")
            sys.exit(1)
        delete_hook(args.event, args.index, 
                    settings_path=args.settings_path, scope=args.scope)
        
    elif args.action == 'validate':
        validate_hooks(settings_path=args.settings_path, scope=args.scope)

    elif args.action == 'show-template':
        if not args.event:
            print("Error: --event is required for show-template action")
            sys.exit(1)
        template = generate_json_template(args.event, args.template_type)
        print(template)

    elif args.action == 'list-templates':
        templates = list_json_templates()
        print(templates)

    elif args.action == 'generate-skill-rules':
        generate_skill_rules_template(args.rules_path)

    elif args.action == 'validate-skill-rules':
        validate_skill_rules(args.rules_path)

    elif args.action == 'list-project-templates':
        list_project_templates()

    elif args.action == 'generate-pipeline':
        if not args.template_id:
            print("Error: --template-id is required for generate-pipeline action")
            print("Use 'list-project-templates' to see available templates")
            sys.exit(1)
        generate_pipeline(
            template_id=args.template_id,
            output_path=args.output,
            check_files=not args.no_check_files
        )

    elif args.action == 'wizard':
        interactive_wizard()

if __name__ == '__main__':
    main()