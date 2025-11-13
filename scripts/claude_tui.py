#!/usr/bin/env python3
"""
Claude Code Manager TUI (Text-Based User Interface)

一个简单的基于文本的用户界面，用于通过键盘操作来管理 Claude Code 的各种组件。
使用箭头键导航，回车键选择。

功能：
- 浏览所有组件类型 (Skills, Subagents, Hooks, Commands, Plugins, MCPs)
- 对每种组件类型执行操作 (List, Install/Create, Edit/Modify, Delete, Validate/Other)
- 调用相应的 Python 管理脚本执行具体操作

依赖：
- Python 3.6+
- 'rich' 库用于美化终端输出 (pip install rich)
"""

import os
import sys
import subprocess
from pathlib import Path
import json

try:
    import yaml
except ImportError:
    print("Error: 'pyyaml' library is required for checklist management.")
    print("Please install it using: pip install pyyaml")
    yaml = None

try:
    from rich.console import Console
    from rich.text import Text
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    # 确保能正确处理中文
    console = Console()
except ImportError:
    print("Error: 'rich' library is required for this TUI.")
    print("Please install it using: pip install rich")
    sys.exit(1)

# 键盘输入处理
if os.name == 'nt':  # Windows
    import msvcrt

    def get_key():
        """获取键盘输入（Windows）"""
        key = msvcrt.getch()
        if key in [b'\xe0', b'\x00']:  # 特殊键前缀
            key = msvcrt.getch()
            if key == b'H':
                return 'UP'
            elif key == b'P':
                return 'DOWN'
        elif key == b'\x1b':  # ESC key
            return 'ESC'
        return key.decode('utf-8', errors='ignore')
else:  # Linux/Unix
    import tty
    import termios

    def get_key():
        """获取键盘输入（Linux/Unix）"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # ESC 序列
                # 尝试读取更多字符
                ch2 = sys.stdin.read(1)
                if not ch2:  # 如果没有更多字符，说明是单独的 ESC 键
                    return 'ESC'
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A':
                        return 'UP'
                    elif ch3 == 'B':
                        return 'DOWN'
                    elif ch3 == 'C':
                        return 'RIGHT'
                    elif ch3 == 'D':
                        return 'LEFT'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# 获取当前脚本所在目录，用于定位各个管理脚本
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
REGISTRY_FILE = PROJECT_ROOT / "components_registry.json"
CATALOG_FILE = PROJECT_ROOT / ".claude" / "component_catalog.json"

# 全局组件注册表和目录
COMPONENTS_REGISTRY = None
COMPONENT_CATALOG = None

# Claude-Kits LOGO
LOGO = """
██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗    ██╗  ██╗██╗████████╗███████╗
██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝    ██║ ██╔╝██║╚══██╔══╝██╔════╝
██║     ██║     ███████║██║   ██║██║  ██║█████╗█████╗█████╔╝ ██║   ██║   ███████╗
██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝╚════╝██╔═██╗ ██║   ██║   ╚════██║
╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗    ██║  ██╗██║   ██║   ███████║
 ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝    ╚═╝  ╚═╝╚═╝   ╚═╝   ╚══════╝
"""

def load_components_registry():
    """加载组件注册表"""
    global COMPONENTS_REGISTRY
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            COMPONENTS_REGISTRY = json.load(f)
    else:
        COMPONENTS_REGISTRY = {
            "components": {
                "agents": {},
                "commands": {},
                "skills": {},
                "hooks": {}
            }
        }
    return COMPONENTS_REGISTRY

def load_component_catalog():
    """加载组件目录（带分类信息）"""
    global COMPONENT_CATALOG
    if CATALOG_FILE.exists():
        try:
            with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
                COMPONENT_CATALOG = json.load(f)
                return COMPONENT_CATALOG
        except Exception as e:
            console.print(f"[yellow]警告：无法加载组件目录: {e}[/yellow]")
    return None

def run_component_scanner():
    """运行组件扫描器"""
    scanner_script = SCRIPT_DIR / "components_scanner.py"
    if not scanner_script.exists():
        console.print("[yellow]组件扫描器未找到，跳过扫描[/yellow]")
        return False

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("扫描组件目录...", total=None)
            result = subprocess.run(
                [sys.executable, str(scanner_script)],
                capture_output=True,
                text=True
            )
            progress.update(task, completed=True)

        if result.returncode == 0:
            console.print("[green]✓ 组件扫描完成[/green]")
            # 重新加载注册表
            load_components_registry()
            return True
        else:
            console.print("[yellow]组件扫描完成（有警告）[/yellow]")
            load_components_registry()
            return True
    except Exception as e:
        console.print(f"[red]扫描出错: {e}[/red]")
        return False

# 定义主菜单选项
MAIN_MENU_ITEMS = [
    "Agent Skills",
    "Subagents",
    "Hooks",
    "Slash Commands",
    "Plugins",
    "MCP Servers",
    "Role Checklists",
    "Exit"
]

# 为每种组件类型定义操作菜单
ACTIONS_MENU = {
    "Agent Skills": ["List", "View Details", "Install", "Edit", "Delete", "Validate", "Back"],
    "Subagents": ["List", "View Details", "Install", "Edit", "Delete", "Validate", "Back"],
    "Hooks": ["List", "Add", "Edit", "Delete", "Validate", "Back"],
    "Slash Commands": ["List", "View Details", "Install", "Edit", "Delete", "Validate", "Back"],
    "Plugins": ["List", "Install", "Uninstall", "Marketplace", "Validate", "Back"],
    "MCP Servers": ["List", "Add", "Edit", "Delete", "Validate", "Back"],
    "Role Checklists": ["View Roles", "View Checklist", "Install from Checklist", "Create Custom", "Edit Custom", "Delete Custom", "Back"]
}

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def run_manager_script(script_name, args):
    """运行指定的管理脚本"""
    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        console.print(f"[red]Error: Management script {script_name} not found at {script_path}[/red]")
        input("Press Enter to continue...")
        return False
        
    # 构造完整的命令
    cmd = [sys.executable, str(script_path)] + args
    
    try:
        clear_screen()
        console.print(Panel(f"Running: {' '.join(cmd)}", title="Executing Command", border_style="blue"))
        console.print()  # 空行分隔

        # ✅ 修复：不捕获输出，允许底层脚本直接访问 stdin/stdout/stderr
        # 这样底层脚本的交互式输入（Prompt.ask, input 等）可以正常工作
        result = subprocess.run(cmd, text=True)

        console.print()  # 空行分隔
        if result.returncode == 0:
            console.print("[green]✓ Command executed successfully.[/green]")
        else:
            console.print(f"[red]✗ Command failed with return code {result.returncode}.[/red]")

        input("\nPress Enter to return to menu...")
        return result.returncode == 0
    except Exception as e:
        console.print(f"[red]Error: Failed to run {script_name}: {e}[/red]")
        input("Press Enter to continue...")
        return False

def get_common_params(component_type="general"):
    """获取通用参数

    参数:
        component_type: 组件类型 ('skills', 'agents', 'hooks', 'commands', 'general')

    返回:
        命令行参数列表
    """
    params = []

    # 根据组件类型显示不同的提示信息
    scope_help = {
        'skills': "user: ~/.claude/skills/ | project: .claude/skills/ | plugin: from plugins | all: all scopes",
        'agents': "user: ~/.claude/agents/ | project: .claude/agents/ | plugin: from plugins | all: all scopes",
        'hooks': "user: ~/.claude/settings.json | project: .claude/settings.json + settings.local.json | plugin: from plugins | all: all scopes",
        'commands': "user: ~/.claude/commands/ | project: .claude/commands/ | plugin: from plugins | all: all scopes",
        'general': "user: user-level | project: project-level | plugin: plugin-level | all: all scopes"
    }

    console.print(f"\n[cyan]Scope options:[/cyan]")
    console.print(f"  {scope_help.get(component_type, scope_help['general'])}")
    console.print()

    # 所有组件类型使用相同的选项（三层级架构）
    scope_choices = ["user", "project", "plugin", "all"]

    scope = Prompt.ask(
        "Select scope",
        choices=scope_choices,
        default="project"
    )
    params.extend(["--scope", scope])

    # 如果选择了 project 或 all，可能需要指定项目路径
    if scope in ["project", "all"]:
        project_path = Prompt.ask(
            "Enter project path (leave blank for current directory)",
            default=""
        )
        if project_path:
            params.extend(["--path", project_path])

    return params

def view_component_details(component_type):
    """查看组件详情（增强版，支持直接安装）"""
    clear_screen()

    if not COMPONENTS_REGISTRY:
        console.print("[yellow]组件注册表未加载，请稍后重试[/yellow]")
        input("\nPress Enter to continue...")
        return

    components = COMPONENTS_REGISTRY.get("components", {}).get(component_type, {})

    if not components:
        console.print(f"[yellow]没有找到 {component_type} 组件[/yellow]")
        input("\nPress Enter to continue...")
        return

    # 创建组件列表
    component_list = [(name, info) for name, info in sorted(components.items())]

    # 显示组件列表
    console.print(Panel(f"Available {component_type.title()}", border_style="green"))
    console.print(f"\n共 {len(component_list)} 个组件\n")

    for i, (name, info) in enumerate(component_list, 1):
        desc = info.get('description', 'No description')
        console.print(f"{i}. [cyan]{name}[/cyan] - {desc[:80]}...")

    # 选择组件查看详情
    console.print("\n输入编号查看详情，或按 Enter 返回")
    choice = input("选择: ").strip()

    if not choice:
        return

    try:
        index = int(choice) - 1
        if 0 <= index < len(component_list):
            name, info = component_list[index]

            # 显示详细信息
            while True:
                clear_screen()
                console.print(Panel(f"[bold]{name}[/bold]", border_style="cyan"))

                table = Table(show_header=False, box=None)
                table.add_column("Field", style="cyan", width=15)
                table.add_column("Value", style="white")

                table.add_row("名称", info.get('name', name))
                table.add_row("类型", component_type)
                table.add_row("文件", info.get('file', info.get('dir', 'N/A')))
                table.add_row("路径", info.get('path', 'N/A'))

                if 'model' in info:
                    table.add_row("模型", info.get('model', 'N/A'))

                if 'description' in info:
                    # 分行显示长描述
                    desc = info.get('description', '')
                    table.add_row("描述", desc)

                console.print(table)

                # 提供操作选项
                console.print("\n[yellow]操作选项:[/yellow]")
                console.print("  [1] 安装到项目")
                console.print("  [2] 查看更多信息")
                console.print("  [0] 返回列表")

                action = input("\n选择: ").strip()

                if action == "1":
                    # 调用 install 操作
                    install_component_from_details(component_type, name)
                    break
                elif action == "2":
                    # 尝试显示源文件内容
                    try:
                        file_path = Path(info.get('path', ''))
                        if file_path.exists():
                            console.print("\n[cyan]=== 组件源文件预览 ===[/cyan]")
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()[:20]
                                for line in lines:
                                    console.print(line.rstrip())
                            input("\n按 Enter 返回详情...")
                    except Exception as e:
                        console.print(f"[red]无法读取文件: {e}[/red]")
                        input("按 Enter 返回...")
                elif action == "0":
                    break
                else:
                    console.print("[red]无效的选择[/red]")
                    input("按 Enter 继续...")
        else:
            console.print("[red]无效的选择[/red]")
            input("Press Enter to continue...")
    except ValueError:
        console.print("[red]无效的输入[/red]")
        input("Press Enter to continue...")

def install_component_from_details(component_type, component_name):
    """从详情页面直接安装组件"""
    clear_screen()
    console.print(Panel(f"安装 {component_name}", border_style="cyan"))

    # 获取目标项目路径
    project_path = Prompt.ask(
        "输入目标项目路径（留空则使用当前目录）",
        default="."
    )

    # 获取作用域
    scope_choices = ["user", "project"]
    scope = Prompt.ask(
        "选择安装作用域",
        choices=scope_choices,
        default="project"
    )

    # 构建安装命令参数
    params = ["install", component_name]
    if project_path != ".":
        params.extend(["--path", project_path])
    params.extend(["--scope", scope])

    # 调用相应的管理脚本
    manager_script = {
        "skills": "skills_manager.py",
        "agents": "subagents_manager.py",
        "hooks": "hooks_manager.py",
        "commands": "commands_manager.py"
    }.get(component_type, "skills_manager.py")

    console.print(f"\n[cyan]执行安装...[/cyan]")
    run_manager_script(manager_script, params)

    input("\n按 Enter 返回...")

# ============================================================================
# 新增：基于目录的层级化导航（使用 component_catalog.json）
# ============================================================================

def browse_agents_by_category():
    """按分类浏览 Agents（从目录读取）"""
    global COMPONENT_CATALOG

    if not COMPONENT_CATALOG:
        console.print("[yellow]组件目录未加载[/yellow]")
        input("\nPress Enter to continue...")
        return

    clear_screen()
    agents_data = COMPONENT_CATALOG.get('components', {}).get('agents', {})

    if not agents_data.get('categories'):
        console.print("[yellow]没有找到分类信息[/yellow]")
        input("\nPress Enter to continue...")
        return

    categories = sorted(agents_data['categories'].keys())

    # 显示分类列表
    console.print(Panel(f"Agent Categories ({len(categories)} 个分类)", border_style="green"))
    console.print()

    for i, cat in enumerate(categories, 1):
        count = agents_data['categories'][cat]['count']
        console.print(f"{i}. [cyan]{cat}[/cyan] ({count} agents)")

    # 选择分类
    console.print("\n输入编号选择分类，或按 Enter 返回")
    choice = input("选择: ").strip()

    if not choice:
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(categories):
            selected_cat = categories[idx]
            browse_agents_in_category(selected_cat, agents_data['categories'][selected_cat]['items'])
    except ValueError:
        console.print("[red]无效的输入[/red]")
        input("Press Enter to continue...")

def browse_agents_in_category(category, agent_list):
    """浏览特定分类中的 Agents"""
    clear_screen()

    console.print(Panel(f"Agents in {category} ({len(agent_list)} 个)", border_style="green"))
    console.print()

    # 显示分类中的 agents
    for i, agent in enumerate(agent_list, 1):
        console.print(f"{i}. [cyan]{agent}[/cyan]")

    # 选择 agent
    console.print("\n输入编号查看详情，或按 Enter 返回")
    choice = input("选择: ").strip()

    if not choice:
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(agent_list):
            show_component_detail("agents", agent_list[idx])
    except ValueError:
        console.print("[red]无效的输入[/red]")
        input("Press Enter to continue...")

def show_component_detail(component_type, component_name):
    """显示组件详情（4个操作选项：安装、修改、删除、返回）"""
    clear_screen()

    # 从注册表获取组件信息
    components = COMPONENTS_REGISTRY.get('components', {}).get(component_type, {})
    info = components.get(component_name, {})

    while True:
        clear_screen()
        console.print(Panel(f"[bold]{component_name}[/bold]", border_style="cyan"))

        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan", width=15)
        table.add_column("Value", style="white")

        table.add_row("Name", info.get('name', component_name))
        table.add_row("Type", component_type)
        table.add_row("File", info.get('file', info.get('dir', 'N/A')))
        table.add_row("Path", info.get('path', 'N/A'))

        if 'model' in info:
            table.add_row("Model", info.get('model', 'N/A'))

        if 'description' in info:
            desc = info.get('description', '')
            # 如果描述太长，截断显示
            if len(desc) > 100:
                desc = desc[:97] + "..."
            table.add_row("Description", desc)

        console.print(table)

        # 4 个操作选项
        console.print("\n[yellow]操作选项:[/yellow]")
        console.print("  [1] 安装 (Install)")
        console.print("  [2] 修改 (Edit)")
        console.print("  [3] 删除 (Delete)")
        console.print("  [0] 返回 (Back)")

        action = input("\n选择: ").strip()

        if action == "1":
            # 安装
            install_component_action(component_type, component_name)
            break
        elif action == "2":
            # 修改
            edit_component_action(component_type, component_name)
            break
        elif action == "3":
            # 删除
            delete_component_action(component_type, component_name)
            break
        elif action == "0":
            # 返回
            break
        else:
            console.print("[red]无效的选择[/red]")
            input("Press Enter to continue...")

def install_component_action(component_type, component_name):
    """安装组件"""
    clear_screen()
    console.print(Panel(f"安装 {component_name}", border_style="cyan"))

    project_path = Prompt.ask(
        "输入目标项目路径（留空则使用当前目录）",
        default="."
    )

    scope = Prompt.ask(
        "选择安装作用域",
        choices=["user", "project"],
        default="project"
    )

    params = ["install", component_name]
    if project_path != ".":
        params.extend(["--path", project_path])
    params.extend(["--scope", scope])

    manager_script = {
        "skills": "skills_manager.py",
        "agents": "subagents_manager.py",
        "hooks": "hooks_manager.py",
        "commands": "commands_manager.py"
    }.get(component_type, "skills_manager.py")

    run_manager_script(manager_script, params)

def edit_component_action(component_type, component_name):
    """修改组件"""
    clear_screen()
    console.print(Panel(f"修改 {component_name}", border_style="cyan"))

    project_path = Prompt.ask(
        "输入项目路径（留空则使用当前目录）",
        default="."
    )

    scope = Prompt.ask(
        "选择作用域",
        choices=["user", "project"],
        default="project"
    )

    params = ["edit", component_name]
    if project_path != ".":
        params.extend(["--path", project_path])
    params.extend(["--scope", scope])

    manager_script = {
        "skills": "skills_manager.py",
        "agents": "subagents_manager.py",
        "hooks": "hooks_manager.py",
        "commands": "commands_manager.py"
    }.get(component_type, "skills_manager.py")

    run_manager_script(manager_script, params)

def delete_component_action(component_type, component_name):
    """删除组件"""
    clear_screen()
    console.print(Panel(f"删除 {component_name}", border_style="cyan"))

    confirm = Prompt.ask(
        f"确定要删除 {component_name} 吗？",
        choices=["yes", "no"],
        default="no"
    )

    if confirm == "yes":
        scope = Prompt.ask(
            "选择作用域",
            choices=["user", "project"],
            default="project"
        )

        params = ["delete", component_name, "--scope", scope]

        manager_script = {
            "skills": "skills_manager.py",
            "agents": "subagents_manager.py",
            "hooks": "hooks_manager.py",
            "commands": "commands_manager.py"
        }.get(component_type, "skills_manager.py")

        run_manager_script(manager_script, params)

def browse_skills_list():
    """浏览 Skills 列表（显示所有 skills）"""
    global COMPONENT_CATALOG

    clear_screen()

    if not COMPONENT_CATALOG:
        console.print("[yellow]组件目录未加载[/yellow]")
        input("\nPress Enter to continue...")
        return

    skills_data = COMPONENT_CATALOG.get('components', {}).get('skills', {})
    skills_list = skills_data.get('items', [])

    if not skills_list:
        console.print("[yellow]没有找到 Skills[/yellow]")
        input("\nPress Enter to continue...")
        return

    # 显示 Skills 列表
    console.print(Panel(f"可用的 Skills ({len(skills_list)} 个)", border_style="green"))
    console.print()

    for i, skill in enumerate(skills_list, 1):
        # 获取 skill 的描述信息
        skill_info = COMPONENTS_REGISTRY.get('components', {}).get('skills', {}).get(skill, {})
        desc = skill_info.get('description', 'No description')
        console.print(f"{i}. [cyan]{skill}[/cyan] - {desc[:60]}...")

    # 选择要查看的 skill
    console.print("\n输入编号查看详情，或按 Enter 返回")
    choice = input("选择: ").strip()

    if not choice:
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(skills_list):
            show_component_detail("skills", skills_list[idx])
    except ValueError:
        console.print("[red]无效的输入[/red]")
        input("Press Enter to continue...")

def quick_install_component(component_type):
    """快速安装组件 - 显示列表供用户选择"""
    clear_screen()

    if not COMPONENTS_REGISTRY:
        console.print("[yellow]组件注册表未加载，请稍后重试[/yellow]")
        input("\nPress Enter to continue...")
        return

    components = COMPONENTS_REGISTRY.get("components", {}).get(component_type, {})

    if not components:
        console.print(f"[yellow]没有找到 {component_type} 组件[/yellow]")
        input("\nPress Enter to continue...")
        return

    # 创建组件列表
    component_list = [(name, info) for name, info in sorted(components.items())]

    # 显示组件列表
    console.print(Panel(f"快速安装 {component_type.title()}", border_style="green"))
    console.print(f"\n共 {len(component_list)} 个组件\n")

    for i, (name, info) in enumerate(component_list, 1):
        desc = info.get('description', 'No description')
        console.print(f"{i}. [cyan]{name}[/cyan] - {desc[:60]}...")

    # 选择要安装的组件
    console.print("\n输入编号选择要安装的组件，或按 Enter 返回")
    choice = input("选择: ").strip()

    if not choice:
        return

    try:
        index = int(choice) - 1
        if 0 <= index < len(component_list):
            name, info = component_list[index]
            install_component_from_details(component_type, name)
        else:
            console.print("[red]无效的选择[/red]")
            input("Press Enter to continue...")
    except ValueError:
        console.print("[red]无效的输入[/red]")
        input("Press Enter to continue...")

def handle_skills_actions(action):
    """处理 Agent Skills 的操作"""
    if action == "View Details":
        browse_skills_list()

    elif action == "List":
        params = ["list"]
        params.extend(get_common_params(component_type="skills"))
        run_manager_script("skills_manager.py", params)

    elif action == "Install":
        quick_install_component("skills")

    elif action == "Edit":
        name = Prompt.ask("Enter skill name to edit")
        if not name:
            console.print("[red]Skill name is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["edit", name]
        params.extend(get_common_params(component_type="skills"))
        run_manager_script("skills_manager.py", params)

    elif action == "Delete":
        name = Prompt.ask("Enter skill name to delete")
        if not name:
            console.print("[red]Skill name is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["delete", name]
        params.extend(get_common_params(component_type="skills"))
        run_manager_script("skills_manager.py", params)

    elif action == "Validate":
        name = Prompt.ask("Enter skill name to validate")
        if not name:
            console.print("[red]Skill name is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["validate", name]
        params.extend(get_common_params(component_type="skills"))
        run_manager_script("skills_manager.py", params)

def handle_subagents_actions(action):
    """处理 Subagents 的操作"""
    if action == "View Details":
        browse_agents_by_category()

    elif action == "List":
        params = ["list"]
        params.extend(get_common_params(component_type="agents"))
        run_manager_script("subagents_manager.py", params)

    elif action == "Install":
        quick_install_component("agents")

    elif action == "Edit":
        name = Prompt.ask("Enter subagent name to edit")
        if not name:
            console.print("[red]Subagent name is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["edit", name]
        params.extend(get_common_params(component_type="agents"))
        run_manager_script("subagents_manager.py", params)

    elif action == "Delete":
        name = Prompt.ask("Enter subagent name to delete")
        if not name:
            console.print("[red]Subagent name is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["delete", name]
        params.extend(get_common_params(component_type="agents"))
        run_manager_script("subagents_manager.py", params)

    elif action == "Validate":
        name = Prompt.ask("Enter subagent name to validate")
        if not name:
            console.print("[red]Subagent name is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["validate", name]
        params.extend(get_common_params(component_type="agents"))
        run_manager_script("subagents_manager.py", params)

def handle_hooks_actions(action):
    """处理 Hooks 的操作"""
    if action == "List":
        params = ["list"]
        scope = Prompt.ask("Select scope", choices=["user", "project", "plugin", "all"], default="project")
        params.extend(["--scope", scope])
        settings_path = Prompt.ask("Enter settings.json path (leave blank for default)", default="")
        if settings_path:
            params.extend(["--settings-path", settings_path])
        run_manager_script("hooks_manager.py", params)
        
    elif action == "Add":
        event = Prompt.ask("Enter hook event (e.g., PreToolUse, PostToolUse)")
        if not event:
            console.print("[red]Hook event is required.[/red]")
            input("Press Enter to continue...")
            return
        matcher = Prompt.ask("Enter tool matcher (leave blank for all tools)", default="")
        command = Prompt.ask("Enter hook command")
        if not command:
            console.print("[red]Hook command is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["add", "--event", event, "--command", command]
        if matcher:
            params.extend(["--matcher", matcher])
        scope = Prompt.ask("Select scope", choices=["user", "project"], default="project")
        params.extend(["--scope", scope])
        settings_path = Prompt.ask("Enter settings.json path (leave blank for default)", default="")
        if settings_path:
            params.extend(["--settings-path", settings_path])
        timeout = Prompt.ask("Enter timeout in seconds (leave blank for default)", default="")
        if timeout:
            try:
                params.extend(["--timeout", str(int(timeout))])
            except ValueError:
                console.print("[yellow]Invalid timeout value, ignoring.[/yellow]")
        run_manager_script("hooks_manager.py", params)
        
    elif action == "Edit":
        event = Prompt.ask("Enter hook event")
        if not event:
            console.print("[red]Hook event is required.[/red]")
            input("Press Enter to continue...")
            return
        try:
            index = int(Prompt.ask("Enter hook index to edit"))
        except ValueError:
            console.print("[red]Invalid index.[/red]")
            input("Press Enter to continue...")
            return
        params = ["edit", "--event", event, "--index", str(index)]
        # 为了简化，这里不提供修改所有参数的选项，用户可以先删除再添加
        new_command = Prompt.ask("Enter new command (leave blank to keep current)")
        if new_command:
            params.extend(["--command", new_command])
        scope = Prompt.ask("Select scope", choices=["user", "project"], default="project")
        params.extend(["--scope", scope])
        settings_path = Prompt.ask("Enter settings.json path (leave blank for default)", default="")
        if settings_path:
            params.extend(["--settings-path", settings_path])
        run_manager_script("hooks_manager.py", params)
        
    elif action == "Delete":
        event = Prompt.ask("Enter hook event")
        if not event:
            console.print("[red]Hook event is required.[/red]")
            input("Press Enter to continue...")
            return
        try:
            index = int(Prompt.ask("Enter hook index to delete"))
        except ValueError:
            console.print("[red]Invalid index.[/red]")
            input("Press Enter to continue...")
            return
        params = ["delete", "--event", event, "--index", str(index)]
        scope = Prompt.ask("Select scope", choices=["user", "project"], default="project")
        params.extend(["--scope", scope])
        settings_path = Prompt.ask("Enter settings.json path (leave blank for default)", default="")
        if settings_path:
            params.extend(["--settings-path", settings_path])
        run_manager_script("hooks_manager.py", params)
        
    elif action == "Validate":
        params = ["validate"]
        scope = Prompt.ask("Select scope", choices=["user", "project"], default="project")
        params.extend(["--scope", scope])
        settings_path = Prompt.ask("Enter settings.json path (leave blank for default)", default="")
        if settings_path:
            params.extend(["--settings-path", settings_path])
        run_manager_script("hooks_manager.py", params)

def handle_commands_actions(action):
    """处理 Slash Commands 的操作"""
    if action == "View Details":
        view_component_details("commands")

    elif action == "List":
        params = ["list"]
        params.extend(get_common_params(component_type="commands"))
        run_manager_script("commands_manager.py", params)

    elif action == "Install":
        quick_install_component("commands")

    elif action == "Edit":
        name = Prompt.ask("Enter command name to edit")
        if not name:
            console.print("[red]Command name is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["edit", name]
        params.extend(get_common_params(component_type="commands"))
        run_manager_script("commands_manager.py", params)

    elif action == "Delete":
        name = Prompt.ask("Enter command name to delete")
        if not name:
            console.print("[red]Command name is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["delete", name]
        params.extend(get_common_params(component_type="commands"))
        run_manager_script("commands_manager.py", params)

    elif action == "Validate":
        name = Prompt.ask("Enter command name to validate")
        if not name:
            console.print("[red]Command name is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["validate", name]
        params.extend(get_common_params(component_type="commands"))
        run_manager_script("commands_manager.py", params)

def handle_plugins_actions(action):
    """处理 Plugins 的操作"""
    if action == "List":
        params = ["list"]
        run_manager_script("plugins_manager.py", params)
        
    elif action == "Install":
        source = Prompt.ask("Enter plugin source (local path or URL)")
        if not source:
            console.print("[red]Plugin source is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["install", "--source", source]
        run_manager_script("plugins_manager.py", params)
        
    elif action == "Uninstall":
        name = Prompt.ask("Enter plugin name to uninstall")
        if not name:
            console.print("[red]Plugin name is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["uninstall", name]
        run_manager_script("plugins_manager.py", params)
        
    elif action == "Marketplace":
        # 简化处理，只列出市场
        params = ["marketplace"]
        run_manager_script("plugins_manager.py", params)
        
    elif action == "Validate":
        plugin_path = Prompt.ask("Enter path to plugin directory to validate")
        if not plugin_path:
            console.print("[red]Plugin path is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["validate", plugin_path]
        run_manager_script("plugins_manager.py", params)

def handle_mcps_actions(action):
    """处理 MCP Servers 的操作"""
    if action == "List":
        params = ["list"]
        scope = Prompt.ask("Select scope", choices=["user", "project", "all"], default="user")
        params.extend(["--scope", scope])
        config_path = Prompt.ask("Enter MCP config path (leave blank for default)", default="")
        if config_path:
            params.extend(["--config-path", config_path])
        run_manager_script("mcps_manager.py", params)
        
    elif action == "Add":
        name = Prompt.ask("Enter server name")
        if not name:
            console.print("[red]Server name is required.[/red]")
            input("Press Enter to continue...")
            return
        transport = Prompt.ask("Select transport", choices=["stdio", "http", "sse"])
        uri = Prompt.ask("Enter server URI")
        if not uri:
            console.print("[red]Server URI is required.[/red]")
            input("Press Enter to continue...")
            return
        description = Prompt.ask("Enter description (optional)", default="")
        env_vars = Prompt.ask("Enter environment variables (KEY1=VALUE1,KEY2=VALUE2, optional)", default="")
        params = ["add", name, "--transport", transport, "--uri", uri]
        if description:
            params.extend(["--description", description])
        if env_vars:
            params.extend(["--env-vars", env_vars])
        scope = Prompt.ask("Select scope", choices=["user", "project"], default="user")
        params.extend(["--scope", scope])
        config_path = Prompt.ask("Enter MCP config path (leave blank for default)", default="")
        if config_path:
            params.extend(["--config-path", config_path])
        run_manager_script("mcps_manager.py", params)
        
    elif action == "Edit":
        name = Prompt.ask("Enter server name to edit")
        if not name:
            console.print("[red]Server name is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["edit", name]
        # 为了简化，这里不提供修改所有参数的选项，用户可以先删除再添加
        new_uri = Prompt.ask("Enter new URI (leave blank to keep current)", default="")
        if new_uri:
            params.extend(["--uri", new_uri])
        scope = Prompt.ask("Select scope", choices=["user", "project"], default="user")
        params.extend(["--scope", scope])
        config_path = Prompt.ask("Enter MCP config path (leave blank for default)", default="")
        if config_path:
            params.extend(["--config-path", config_path])
        run_manager_script("mcps_manager.py", params)
        
    elif action == "Delete":
        name = Prompt.ask("Enter server name to delete")
        if not name:
            console.print("[red]Server name is required.[/red]")
            input("Press Enter to continue...")
            return
        params = ["delete", name]
        scope = Prompt.ask("Select scope", choices=["user", "project"], default="user")
        params.extend(["--scope", scope])
        config_path = Prompt.ask("Enter MCP config path (leave blank for default)", default="")
        if config_path:
            params.extend(["--config-path", config_path])
        run_manager_script("mcps_manager.py", params)
        
    elif action == "Validate":
        params = ["validate"]
        scope = Prompt.ask("Select scope", choices=["user", "project"], default="user")
        params.extend(["--scope", scope])
        config_path = Prompt.ask("Enter MCP config path (leave blank for default)", default="")
        if config_path:
            params.extend(["--config-path", config_path])
        run_manager_script("mcps_manager.py", params)

def load_checklist(checklist_path):
    """加载 YAML 格式的 checklist"""
    if yaml is None:
        console.print("[red]Error: pyyaml library not installed[/red]")
        return None

    try:
        with open(checklist_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]Error loading checklist: {e}[/red]")
        return None

def save_checklist(checklist_path, checklist_data):
    """保存 YAML 格式的 checklist"""
    if yaml is None:
        console.print("[red]Error: pyyaml library not installed[/red]")
        return False

    try:
        with open(checklist_path, 'w', encoding='utf-8') as f:
            yaml.dump(checklist_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        console.print(f"[red]Error saving checklist: {e}[/red]")
        return False

def display_checklist(checklist_data):
    """以表格形式显示 checklist 内容"""
    console.print(Panel(f"[bold]{checklist_data.get('name', 'Unnamed')}[/bold]", border_style="green"))
    console.print(f"[cyan]{checklist_data.get('description', 'No description')}\n")

    # 显示 Agents
    if 'agents' in checklist_data and checklist_data['agents']:
        table = Table(title="Agents", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Reason", style="white")
        for agent in checklist_data['agents']:
            table.add_row(agent['name'], agent.get('reason', ''))
        console.print(table)
        console.print()

    # 显示 Skills
    if 'skills' in checklist_data and checklist_data['skills']:
        table = Table(title="Skills", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Reason", style="white")
        for skill in checklist_data['skills']:
            table.add_row(skill['name'], skill.get('reason', ''))
        console.print(table)
        console.print()

    # 显示 Commands
    if 'commands' in checklist_data and checklist_data['commands']:
        table = Table(title="Commands", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Reason", style="white")
        for command in checklist_data['commands']:
            table.add_row(command['name'], command.get('reason', ''))
        console.print(table)
        console.print()

def handle_checklists_actions(action):
    """处理 Role Checklists 的操作"""
    checklists_dir = PROJECT_ROOT / "checklists"
    roles_dir = checklists_dir / "roles"
    custom_dir = checklists_dir / "custom"

    if action == "View Roles":
        clear_screen()
        console.print(Panel("Available Role-Based Checklists", border_style="green"))

        if not roles_dir.exists():
            console.print("[yellow]No role checklists found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        role_files = list(roles_dir.glob("*.yaml"))
        if not role_files:
            console.print("[yellow]No role checklists found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Role", style="cyan")
        table.add_column("Description", style="white")

        for role_file in sorted(role_files):
            checklist = load_checklist(role_file)
            if checklist:
                table.add_row(
                    checklist.get('name', role_file.stem),
                    checklist.get('description', 'No description')
                )

        console.print(table)
        input("\nPress Enter to continue...")

    elif action == "View Checklist":
        # 选择要查看的 checklist
        checklist_type = Prompt.ask("View role or custom checklist?", choices=["role", "custom"], default="role")

        if checklist_type == "role":
            checklist_dir = roles_dir
        else:
            checklist_dir = custom_dir

        if not checklist_dir.exists():
            console.print("[yellow]No checklists found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        checklist_files = list(checklist_dir.glob("*.yaml"))
        if not checklist_files:
            console.print("[yellow]No checklists found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        # 显示可用的 checklists
        console.print("\n[bold]Available Checklists:[/bold]")
        for i, f in enumerate(checklist_files, 1):
            console.print(f"{i}. {f.stem}")

        try:
            choice = int(Prompt.ask("\nSelect checklist number")) - 1
            if 0 <= choice < len(checklist_files):
                clear_screen()
                checklist = load_checklist(checklist_files[choice])
                if checklist:
                    display_checklist(checklist)
                input("\nPress Enter to continue...")
            else:
                console.print("[red]Invalid choice.[/red]")
                input("Press Enter to continue...")
        except (ValueError, KeyboardInterrupt):
            return

    elif action == "Install from Checklist":
        # 选择 checklist
        checklist_type = Prompt.ask("Install from role or custom checklist?", choices=["role", "custom"], default="role")

        if checklist_type == "role":
            checklist_dir = roles_dir
        else:
            checklist_dir = custom_dir

        if not checklist_dir.exists():
            console.print("[yellow]No checklists found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        checklist_files = list(checklist_dir.glob("*.yaml"))
        if not checklist_files:
            console.print("[yellow]No checklists found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        # 显示可用的 checklists
        console.print("\n[bold]Available Checklists:[/bold]")
        for i, f in enumerate(checklist_files, 1):
            console.print(f"{i}. {f.stem}")

        try:
            choice = int(Prompt.ask("\nSelect checklist number")) - 1
            if 0 <= choice < len(checklist_files):
                checklist = load_checklist(checklist_files[choice])
                if checklist:
                    # 显示 checklist 内容
                    clear_screen()
                    display_checklist(checklist)

                    confirm = Prompt.ask("\nInstall all components from this checklist?", choices=["y", "n"], default="n")
                    if confirm == "y":
                        # 获取安装参数
                        scope = Prompt.ask("Select scope", choices=["personal", "project", "user"], default="project")

                        # 安装 agents
                        if 'agents' in checklist and checklist['agents']:
                            console.print("\n[bold green]Installing Agents...[/bold green]")
                            for agent in checklist['agents']:
                                console.print(f"Installing agent: {agent['name']}")
                                run_manager_script("subagents_manager.py", ["install", agent['name'], "--scope", scope])

                        # 安装 skills
                        if 'skills' in checklist and checklist['skills']:
                            console.print("\n[bold green]Installing Skills...[/bold green]")
                            for skill in checklist['skills']:
                                console.print(f"Installing skill: {skill['name']}")
                                run_manager_script("skills_manager.py", ["install", skill['name'], "--scope", scope])

                        # 安装 commands
                        if 'commands' in checklist and checklist['commands']:
                            console.print("\n[bold green]Installing Commands...[/bold green]")
                            for command in checklist['commands']:
                                console.print(f"Installing command: {command['name']}")
                                run_manager_script("commands_manager.py", ["install", command['name'], "--scope", scope])

                        console.print("\n[bold green]Installation complete![/bold green]")
                        input("\nPress Enter to continue...")
            else:
                console.print("[red]Invalid choice.[/red]")
                input("Press Enter to continue...")
        except (ValueError, KeyboardInterrupt):
            return

    elif action == "Create Custom":
        # 使用增强的自定义 Role 构建器
        try:
            # 导入自定义 role builder
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
            from custom_role_builder import create_custom_role

            # 启动 Role 构建器
            role_filepath = create_custom_role()

            if role_filepath:
                # 询问是否立即安装
                install = Prompt.ask("\n[green]Role created successfully! Install it now?[/green]",
                                    choices=["y", "n"], default="n")
                if install == "y":
                    target_path = Prompt.ask("Enter target project path")
                    if target_path:
                        # 使用 roles_manager.py 安装
                        role_name = role_filepath.stem
                        params = ["install", role_name, "--path", target_path]
                        run_manager_script("roles_manager.py", params)

        except ImportError as e:
            console.print(f"[red]Error: Could not import custom_role_builder: {e}[/red]")
            console.print("[yellow]Falling back to simple text-based input...[/yellow]")
            input("Press Enter to continue...")

            # Fallback to simple method
            clear_screen()
            console.print(Panel("Create Custom Checklist", border_style="green"))

            name = Prompt.ask("Checklist name")
            if not name:
                console.print("[red]Name is required.[/red]")
                input("Press Enter to continue...")
                return

            description = Prompt.ask("Description")

            # ���始化 checklist 数据
            checklist_data = {
                'name': name,
                'description': description,
                'role': 'custom',
                'agents': [],
                'skills': [],
                'commands': []
            }

            # 添加 agents
            console.print("\n[bold]Add Agents (enter empty name to finish)[/bold]")
            while True:
                agent_name = Prompt.ask("Agent name (or press Enter to skip)")
                if not agent_name:
                    break
                reason = Prompt.ask("Reason for including this agent")
                checklist_data['agents'].append({'name': agent_name, 'reason': reason})

            # 添加 skills
            console.print("\n[bold]Add Skills (enter empty name to finish)[/bold]")
            while True:
                skill_name = Prompt.ask("Skill name (or press Enter to skip)")
                if not skill_name:
                    break
                reason = Prompt.ask("Reason for including this skill")
                checklist_data['skills'].append({'name': skill_name, 'reason': reason})

            # 添加 commands
            console.print("\n[bold]Add Commands (enter empty name to finish)[/bold]")
            while True:
                command_name = Prompt.ask("Command name (or press Enter to skip)")
                if not command_name:
                    break
                reason = Prompt.ask("Reason for including this command")
                checklist_data['commands'].append({'name': command_name, 'reason': reason})

            # 保存 checklist
            custom_dir.mkdir(parents=True, exist_ok=True)
            checklist_file = custom_dir / f"{name.lower().replace(' ', '-')}.yaml"

            if save_checklist(checklist_file, checklist_data):
                console.print(f"\n[green]Checklist saved to: {checklist_file}[/green]")
            else:
                console.print("\n[red]Failed to save checklist.[/red]")

            input("\nPress Enter to continue...")

    elif action == "Edit Custom":
        # 编辑自定义 checklist
        if not custom_dir.exists():
            console.print("[yellow]No custom checklists found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        checklist_files = list(custom_dir.glob("*.yaml"))
        if not checklist_files:
            console.print("[yellow]No custom checklists found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        console.print("\n[bold]Custom Checklists:[/bold]")
        for i, f in enumerate(checklist_files, 1):
            console.print(f"{i}. {f.stem}")

        try:
            choice = int(Prompt.ask("\nSelect checklist to edit")) - 1
            if 0 <= choice < len(checklist_files):
                # 使用默认编辑器打开文件
                editor = os.environ.get('EDITOR', 'nano')
                subprocess.run([editor, str(checklist_files[choice])])
                console.print("[green]Checklist updated.[/green]")
                input("\nPress Enter to continue...")
            else:
                console.print("[red]Invalid choice.[/red]")
                input("Press Enter to continue...")
        except (ValueError, KeyboardInterrupt):
            return

    elif action == "Delete Custom":
        # 删除自定义 checklist
        if not custom_dir.exists():
            console.print("[yellow]No custom checklists found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        checklist_files = list(custom_dir.glob("*.yaml"))
        if not checklist_files:
            console.print("[yellow]No custom checklists found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        console.print("\n[bold]Custom Checklists:[/bold]")
        for i, f in enumerate(checklist_files, 1):
            console.print(f"{i}. {f.stem}")

        try:
            choice = int(Prompt.ask("\nSelect checklist to delete")) - 1
            if 0 <= choice < len(checklist_files):
                confirm = Prompt.ask(f"Delete {checklist_files[choice].stem}?", choices=["y", "n"], default="n")
                if confirm == "y":
                    checklist_files[choice].unlink()
                    console.print(f"[green]Checklist {checklist_files[choice].stem} deleted.[/green]")
                input("\nPress Enter to continue...")
            else:
                console.print("[red]Invalid choice.[/red]")
                input("Press Enter to continue...")
        except (ValueError, KeyboardInterrupt):
            return

def show_actions_menu(component_type):
    """显示特定组件类型的操作菜单"""
    actions = ACTIONS_MENU[component_type]
    selected_index = 0

    while True:
        clear_screen()
        console.print(Panel(f"Managing: {component_type}", title="Claude Code Manager", border_style="green"))

        for i, action in enumerate(actions):
            if i == selected_index:
                console.print(f"-> [bold yellow]{i+1}. {action}[/bold yellow]")
            else:
                console.print(f"   {i+1}. {action}")

        console.print("\n[green]↑/↓ 箭头键导航，Enter 选择，数字快捷键，q/ESC 返回[/green]")

        try:
            key = get_key()

            if key == 'UP':
                selected_index = (selected_index - 1) % len(actions)
            elif key == 'DOWN':
                selected_index = (selected_index + 1) % len(actions)
            elif key in ['q', 'Q'] or key == 'ESC':
                break
            elif key == '\r' or key == '\n':  # Enter
                selected_action = actions[selected_index]
                if selected_action == "Back":
                    break

                # 根据组件类型调用相应的处理函数
                if component_type == "Agent Skills":
                    handle_skills_actions(selected_action)
                elif component_type == "Subagents":
                    handle_subagents_actions(selected_action)
                elif component_type == "Hooks":
                    handle_hooks_actions(selected_action)
                elif component_type == "Slash Commands":
                    handle_commands_actions(selected_action)
                elif component_type == "Plugins":
                    handle_plugins_actions(selected_action)
                elif component_type == "MCP Servers":
                    handle_mcps_actions(selected_action)
                elif component_type == "Role Checklists":
                    handle_checklists_actions(selected_action)
            elif key.isdigit():
                # 数字快捷键
                num = int(key)
                if 1 <= num <= len(actions):
                    selected_index = num - 1
                    selected_action = actions[selected_index]
                    if selected_action == "Back":
                        break

                    # 根据组件类型调用相应的处理函数
                    if component_type == "Agent Skills":
                        handle_skills_actions(selected_action)
                    elif component_type == "Subagents":
                        handle_subagents_actions(selected_action)
                    elif component_type == "Hooks":
                        handle_hooks_actions(selected_action)
                    elif component_type == "Slash Commands":
                        handle_commands_actions(selected_action)
                    elif component_type == "Plugins":
                        handle_plugins_actions(selected_action)
                    elif component_type == "MCP Servers":
                        handle_mcps_actions(selected_action)
                    elif component_type == "Role Checklists":
                        handle_checklists_actions(selected_action)

        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            input("Press Enter to continue...")

def main():
    """主函数"""
    selected_index = 0

    while True:
        clear_screen()
        # 显示 LOGO
        console.print(f"[bold cyan]{LOGO}[/bold cyan]")
        console.print(Panel("Claude Code Manager", title="Main Menu", border_style="blue"))

        for i, item in enumerate(MAIN_MENU_ITEMS):
            if i == selected_index:
                console.print(f"-> [bold yellow]{i+1}. {item}[/bold yellow]")
            else:
                console.print(f"   {i+1}. {item}")

        console.print("\n[green]↑/↓ 箭头键导航，Enter 选择，数字快捷键，q/ESC 退出[/green]")

        try:
            key = get_key()

            if key == 'UP':
                selected_index = (selected_index - 1) % len(MAIN_MENU_ITEMS)
            elif key == 'DOWN':
                selected_index = (selected_index + 1) % len(MAIN_MENU_ITEMS)
            elif key in ['q', 'Q'] or key == 'ESC':
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif key == '\r' or key == '\n':  # Enter
                selected_item = MAIN_MENU_ITEMS[selected_index]
                if selected_item == "Exit":
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                else:
                    # 显示子菜单
                    show_actions_menu(selected_item)
            elif key.isdigit():
                # 数字快捷键
                num = int(key)
                if 1 <= num <= len(MAIN_MENU_ITEMS):
                    selected_index = num - 1
                    selected_item = MAIN_MENU_ITEMS[selected_index]
                    if selected_item == "Exit":
                        console.print("[yellow]Goodbye![/yellow]")
                        break
                    else:
                        # 显示子菜单
                        show_actions_menu(selected_item)

        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            input("Press Enter to continue...")

if __name__ == "__main__":
    # 显示启动信息
    clear_screen()
    console.print(f"[bold cyan]{LOGO}[/bold cyan]")
    console.print(Panel("正在初始化...", border_style="blue"))

    # 检查依赖脚本是否存在
    required_scripts = [
        "skills_manager.py",
        "subagents_manager.py",
        "hooks_manager.py",
        "commands_manager.py",
        "plugins_manager.py",
        "mcps_manager.py"
    ]

    missing_scripts = []
    for script in required_scripts:
        if not (SCRIPT_DIR / script).exists():
            missing_scripts.append(script)

    if missing_scripts:
        console.print(f"[red]Error: Missing required scripts: {', '.join(missing_scripts)}[/red]")
        console.print(f"Please ensure they exist in {SCRIPT_DIR}")
        sys.exit(1)

    # 运行组件扫描器
    console.print("\n[cyan]扫描组件目录...[/cyan]")
    run_component_scanner()

    # 加载组件注册表
    console.print("[cyan]加载组件注册表...[/cyan]")
    load_components_registry()

    # 加载组件目录（分类信息）
    console.print("[cyan]加载组件分类目录...[/cyan]")
    load_component_catalog()

    if COMPONENTS_REGISTRY:
        metadata = COMPONENTS_REGISTRY.get("metadata", {})
        console.print(f"\n[green]✓ 已加载 {metadata.get('total_agents', 0)} 个 Agents[/green]")
        console.print(f"[green]✓ 已加载 {metadata.get('total_commands', 0)} 个 Commands[/green]")
        console.print(f"[green]✓ 已加载 {metadata.get('total_skills', 0)} 个 Skills[/green]")

    console.print("\n[green]初始化完成！按 Enter 继续...[/green]")
    input()

    main()