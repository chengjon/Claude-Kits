#!/usr/bin/env python3
"""
Custom Role Builder - Interactive Multi-select Component Browser

This module provides an enhanced TUI interface for creating custom role collections
with the following features:
- Multi-select component browser with keyboard navigation
- Real-time component counter (X/15 selected, warn at 10)
- Browse all components from components_registry.json
- Search/filter functionality
- Quantity limits enforcement
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt
    import yaml
except ImportError:
    print("Error: Required libraries not installed.")
    print("Please run: pip install rich pyyaml")
    sys.exit(1)

# Platform-specific keyboard input handling
if sys.platform == 'win32':
    import msvcrt
    def get_key():
        """Get a single key press on Windows"""
        key = msvcrt.getch()
        if key == b'\xe0':  # Arrow key prefix
            key = msvcrt.getch()
            if key == b'H':
                return 'UP'
            elif key == b'P':
                return 'DOWN'
        return key.decode('utf-8', errors='ignore')
else:
    import tty
    import termios
    def get_key():
        """Get a single key press on Unix/Linux"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # Escape sequence
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A':
                        return 'UP'
                    elif ch3 == 'B':
                        return 'DOWN'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

console = Console()

@dataclass
class Component:
    """Represents a single component"""
    name: str
    component_type: str  # 'skills', 'agents', 'commands'
    description: str = ""
    selected: bool = False

@dataclass
class RoleBuilderState:
    """State management for the role builder"""
    role_name: str = ""
    role_description: str = ""
    all_components: List[Component] = field(default_factory=list)
    selected_components: Set[str] = field(default_factory=set)  # Set of component names
    current_component_type: str = "skills"  # Current browsing type
    search_query: str = ""

    MAX_COMPONENTS = 15
    RECOMMENDED_MAX = 10

    @property
    def selected_count(self) -> int:
        """Total number of selected components"""
        return len(self.selected_components)

    @property
    def is_at_limit(self) -> bool:
        """Check if at maximum limit"""
        return self.selected_count >= self.MAX_COMPONENTS

    @property
    def is_at_recommended(self) -> bool:
        """Check if at recommended limit"""
        return self.selected_count >= self.RECOMMENDED_MAX

    def get_filtered_components(self) -> List[Component]:
        """Get components filtered by type and search query"""
        filtered = [c for c in self.all_components if c.component_type == self.current_component_type]

        if self.search_query:
            query = self.search_query.lower()
            filtered = [c for c in filtered if query in c.name.lower() or query in c.description.lower()]

        return filtered

    def toggle_selection(self, component: Component) -> bool:
        """
        Toggle component selection
        Returns True if successful, False if at limit
        """
        if component.name in self.selected_components:
            self.selected_components.remove(component.name)
            component.selected = False
            return True
        else:
            if self.is_at_limit:
                return False
            self.selected_components.add(component.name)
            component.selected = True
            return True

    def get_selected_by_type(self) -> Dict[str, List[Component]]:
        """Get selected components grouped by type"""
        result = {'skills': [], 'agents': [], 'commands': []}
        for comp in self.all_components:
            if comp.name in self.selected_components:
                result[comp.component_type].append(comp)
        return result

def clear_screen():
    """Clear the terminal screen"""
    console.clear()

def load_components_registry() -> Dict:
    """Load the components registry"""
    registry_path = Path(__file__).parent.parent / "components_registry.json"

    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading components registry: {e}[/red]")
        return {}

def initialize_components(state: RoleBuilderState):
    """Initialize components from registry"""
    registry = load_components_registry()

    # Check registry structure - could be flat or nested under 'components'
    components_data = registry.get('components', registry)

    # Load Skills
    skills_data = components_data.get('skills', {})
    for skill_name, skill_data in skills_data.items():
        state.all_components.append(Component(
            name=skill_name,
            component_type='skills',
            description=skill_data.get('description', 'No description')
        ))

    # Load Agents
    agents_data = components_data.get('agents', {})
    for agent_name, agent_data in agents_data.items():
        state.all_components.append(Component(
            name=agent_name,
            component_type='agents',
            description=agent_data.get('description', 'No description')
        ))

    # Load Commands
    commands_data = components_data.get('commands', {})
    for command_name, command_data in commands_data.items():
        state.all_components.append(Component(
            name=command_name,
            component_type='commands',
            description=command_data.get('description', 'No description')
        ))

def show_header(state: RoleBuilderState):
    """Display the header with role info and counter"""
    title = f"Custom Role Builder: {state.role_name}" if state.role_name else "Custom Role Builder"

    # Determine counter color based on limits
    if state.is_at_limit:
        counter_color = "red"
        counter_text = f"[{counter_color}]{state.selected_count}/{state.MAX_COMPONENTS} (LIMIT REACHED)[/{counter_color}]"
    elif state.is_at_recommended:
        counter_color = "yellow"
        counter_text = f"[{counter_color}]{state.selected_count}/{state.MAX_COMPONENTS} (⚠️  Approaching limit)[/{counter_color}]"
    else:
        counter_color = "green"
        counter_text = f"[{counter_color}]{state.selected_count}/{state.MAX_COMPONENTS}[/{counter_color}]"

    header = f"{title} | Components: {counter_text}"
    console.print(Panel(header, border_style="cyan", expand=False))

def show_component_browser(state: RoleBuilderState, selected_index: int) -> None:
    """Display the component browser interface"""
    clear_screen()
    show_header(state)

    # Component type tabs
    tabs = []
    for comp_type in ['skills', 'agents', 'commands']:
        if comp_type == state.current_component_type:
            tabs.append(f"[bold cyan]• {comp_type.upper()} •[/bold cyan]")
        else:
            tabs.append(f"[dim]{comp_type.upper()}[/dim]")
    console.print("  ".join(tabs))
    console.print()

    # Search bar
    if state.search_query:
        console.print(f"🔍 Search: [cyan]{state.search_query}[/cyan] (Press '/' to clear)")
    else:
        console.print("[dim]Press '/' to search[/dim]")
    console.print()

    # Component list
    components = state.get_filtered_components()

    if not components:
        console.print("[yellow]No components found[/yellow]")
        return

    # Display components (max 20 at a time)
    display_start = max(0, selected_index - 10)
    display_end = min(len(components), display_start + 20)

    for i in range(display_start, display_end):
        comp = components[i]
        prefix = "→ " if i == selected_index else "  "

        # Selection indicator
        checkbox = "[✓]" if comp.name in state.selected_components else "[ ]"

        # Component name
        name_style = "bold yellow" if i == selected_index else "white"

        # Description (truncated)
        desc = comp.description[:60] + "..." if len(comp.description) > 60 else comp.description
        desc_style = "dim"

        console.print(f"{prefix}{checkbox} [{name_style}]{comp.name}[/{name_style}]")
        console.print(f"    [{desc_style}]{desc}[/{desc_style}]")

    # Show pagination info
    if len(components) > 20:
        console.print(f"\n[dim]Showing {display_start+1}-{display_end} of {len(components)} components[/dim]")

    # Instructions
    console.print("\n" + "="*70)
    console.print("[green]Controls:[/green]")
    console.print("  ↑/↓ or W/S: Navigate  |  SPACE: Select/Deselect  |  TAB: Switch type")
    console.print("  /: Search  |  R: Review selections  |  F: Finish  |  Q: Cancel")

def browse_components(state: RoleBuilderState) -> bool:
    """
    Main component browser loop
    Returns True if user finished successfully, False if cancelled
    """
    selected_index = 0

    while True:
        components = state.get_filtered_components()

        # Bounds checking
        if not components:
            selected_index = 0
        else:
            selected_index = max(0, min(selected_index, len(components) - 1))

        show_component_browser(state, selected_index)

        try:
            key = get_key()

            # Navigation
            if key in ['UP', 'w', 'W']:
                selected_index = max(0, selected_index - 1)
            elif key in ['DOWN', 's', 'S']:
                selected_index = min(len(components) - 1, selected_index + 1)

            # Selection
            elif key == ' ':  # Space bar
                if components:
                    comp = components[selected_index]
                    if not state.toggle_selection(comp):
                        console.print("\n[red]⚠️  Maximum limit (15) reached![/red]")
                        input("Press Enter to continue...")

            # Switch component type
            elif key in ['\t', 'T', 't']:  # Tab
                types = ['skills', 'agents', 'commands']
                current_idx = types.index(state.current_component_type)
                state.current_component_type = types[(current_idx + 1) % len(types)]
                selected_index = 0

            # Search
            elif key == '/':
                state.search_query = Prompt.ask("Search query (leave blank to clear)")
                selected_index = 0

            # Review selections
            elif key in ['R', 'r']:
                show_review_screen(state)

            # Finish
            elif key in ['F', 'f']:
                if state.selected_count == 0:
                    console.print("\n[yellow]⚠️  No components selected. Please select at least one component.[/yellow]")
                    input("Press Enter to continue...")
                else:
                    return True

            # Cancel
            elif key in ['Q', 'q']:
                confirm = Prompt.ask("\n[yellow]Cancel role creation?[/yellow]", choices=["y", "n"], default="n")
                if confirm == "y":
                    return False

        except KeyboardInterrupt:
            return False
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            input("Press Enter to continue...")

def show_review_screen(state: RoleBuilderState):
    """Display review screen with all selections"""
    clear_screen()
    console.print(Panel("Review Selected Components", border_style="green"))

    # Show counter with warning
    if state.is_at_limit:
        console.print(f"[red]⚠️  At maximum limit: {state.selected_count}/{state.MAX_COMPONENTS}[/red]\n")
    elif state.is_at_recommended:
        console.print(f"[yellow]⚠️  Approaching limit: {state.selected_count}/{state.MAX_COMPONENTS} (recommended: ≤{state.RECOMMENDED_MAX})[/yellow]\n")
    else:
        console.print(f"[green]Selected: {state.selected_count}/{state.MAX_COMPONENTS}[/green]\n")

    selected_by_type = state.get_selected_by_type()

    # Display by type
    for comp_type, components in selected_by_type.items():
        if components:
            console.print(f"[bold cyan]{comp_type.upper()} ({len(components)})[/bold cyan]")
            for comp in components:
                console.print(f"  • {comp.name}")
            console.print()

    if state.selected_count == 0:
        console.print("[yellow]No components selected yet[/yellow]\n")

    input("\nPress Enter to continue...")

def save_custom_role(state: RoleBuilderState, output_dir: Path) -> Optional[Path]:
    """
    Save the custom role to YAML file
    Returns the filepath if successful, None otherwise
    """
    selected_by_type = state.get_selected_by_type()

    # Build YAML structure
    role_data = {
        'name': state.role_name,
        'description': state.role_description,
        'role': 'custom',
        'agents': [],
        'skills': [],
        'commands': []
    }

    # Add selected components
    for comp in selected_by_type['agents']:
        role_data['agents'].append({
            'name': comp.name,
            'reason': comp.description[:200]  # Truncate if too long
        })

    for comp in selected_by_type['skills']:
        role_data['skills'].append({
            'name': comp.name,
            'reason': comp.description[:200]
        })

    for comp in selected_by_type['commands']:
        role_data['commands'].append({
            'name': comp.name,
            'reason': comp.description[:200]
        })

    # Save to file
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = state.role_name.lower().replace(' ', '-').replace('_', '-')
    filepath = output_dir / f"{filename}.yaml"

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(role_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return filepath
    except Exception as e:
        console.print(f"[red]Error saving role: {e}[/red]")
        return None

def create_custom_role() -> Optional[Path]:
    """
    Main entry point for creating a custom role
    Returns the path to the saved role file, or None if cancelled
    """
    clear_screen()
    console.print(Panel("Create Custom Role Collection", border_style="green", expand=False))
    console.print()
    console.print("[cyan]This wizard will help you create a custom role by selecting components from:")
    console.print("  • Skills (Agent Skills)")
    console.print("  • Agents (Subagents)")
    console.print("  • Commands (Slash Commands)")
    console.print()
    console.print(f"[yellow]⚠️  Limits: Recommended ≤10 components, Maximum 15 components[/yellow]")
    console.print()

    # Get basic info
    role_name = Prompt.ask("Role name")
    if not role_name:
        console.print("[red]Role name is required[/red]")
        return None

    role_description = Prompt.ask("Description")
    if not role_description:
        console.print("[red]Description is required[/red]")
        return None

    # Initialize state
    state = RoleBuilderState(
        role_name=role_name,
        role_description=role_description
    )

    # Load components
    console.print("\n[cyan]Loading components...[/cyan]")
    initialize_components(state)
    console.print(f"[green]Loaded {len(state.all_components)} components[/green]")
    input("Press Enter to start browsing...")

    # Browse and select components
    if not browse_components(state):
        console.print("\n[yellow]Role creation cancelled[/yellow]")
        return None

    # Final review
    clear_screen()
    console.print(Panel("Final Review", border_style="green"))
    console.print(f"\n[bold]Role Name:[/bold] {state.role_name}")
    console.print(f"[bold]Description:[/bold] {state.role_description}")
    console.print(f"[bold]Total Components:[/bold] {state.selected_count}")
    console.print()

    show_review_screen(state)

    # Confirm save
    confirm = Prompt.ask("\n[green]Save this role?[/green]", choices=["y", "n"], default="y")
    if confirm != "y":
        console.print("\n[yellow]Role creation cancelled[/yellow]")
        return None

    # Save
    output_dir = Path(__file__).parent.parent / "checklists" / "roles"
    filepath = save_custom_role(state, output_dir)

    if filepath:
        console.print(f"\n[green]✓ Role saved to: {filepath}[/green]")

        # Offer to install
        install = Prompt.ask("\nInstall this role now?", choices=["y", "n"], default="n")
        if install == "y":
            return filepath
        return filepath
    else:
        console.print("\n[red]Failed to save role[/red]")
        return None

if __name__ == "__main__":
    """Test the custom role builder standalone"""
    result = create_custom_role()
    if result:
        print(f"\nRole saved to: {result}")
    else:
        print("\nRole creation cancelled or failed")
