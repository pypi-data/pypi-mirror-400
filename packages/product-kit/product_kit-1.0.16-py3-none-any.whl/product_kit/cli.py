"""Main CLI entry point for create-product-kit."""

import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.align import Align
from rich import box

from .scaffolder import scaffold_project, update_project

app = typer.Typer(
    name="prod",
    help="Scaffold a Product Kit framework for requirement-driven design",
    add_completion=False,
)
console = Console()

BANNER = """
██████╗ ██████╗  ██████╗ ██████╗ ██╗   ██╗ ██████╗████████╗    ██╗  ██╗██╗████████╗
██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██║   ██║██╔════╝╚══██╔══╝    ██║ ██╔╝██║╚══██╔══╝
██████╔╝██████╔╝██║   ██║██║  ██║██║   ██║██║        ██║       █████╔╝ ██║   ██║   
██╔═══╝ ██╔══██╗██║   ██║██║  ██║██║   ██║██║        ██║       ██╔═██╗ ██║   ██║   
██║     ██║  ██║╚██████╔╝██████╔╝╚██████╔╝╚██████╗   ██║       ██║  ██╗██║   ██║   
╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝  ╚═════╝   ╚═╝       ╚═╝  ╚═╝╚═╝   ╚═╝   
"""


@app.command("init")
def init(
    project_name: Optional[str] = typer.Argument(
        None,
        help="Project name (directory will be created)",
    ),
    product_name: Optional[str] = typer.Option(
        None,
        "--product-name",
        "-p",
        help="Product name (skips prompt)",
    ),
    no_prompts: bool = typer.Option(
        False,
        "--no-prompts",
        help="Skip interactive prompts and use defaults",
    ),
) -> None:
    """
    Scaffold a new Product Kit project with customized templates.
    
    Examples:
        prod init my-product
        prod --no-prompts
        prod init my-product --product-name "My Awesome Product"
    """
    print_banner()

    # Determine target directory
    if project_name:
        target_dir = Path.cwd() / project_name
        default_product_name = project_name.replace("-", " ").replace("_", " ").title()
    else:
        target_dir = Path.cwd()
        default_product_name = target_dir.name.replace("-", " ").replace("_", " ").title()

    # Check if directory exists and has content
    if target_dir.exists() and any(target_dir.iterdir()):
        items_count = len(list(target_dir.iterdir()))
        console.print(f"[yellow]Warning: Current directory is not empty ({items_count} items)[/yellow]")
        console.print("[yellow]Template files will be merged with existing content and may overwrite existing files[/yellow]")
        if not Confirm.ask("Do you want to continue?", default=False):
            console.print("[red]✖ Cancelled[/red]")
            sys.exit(0)
        console.print()

    # Show project setup panel
    console.print(
        Panel(
            f"[bold]Product Kit Setup[/bold]\n\n"
            f"Project         {default_product_name}\n"
            f"Working Path    {target_dir.absolute()}",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    console.print()

    # Interactive prompts (unless disabled)
    if no_prompts:
        config = {
            "product_name": product_name or default_product_name,
            "product_vision": "Build the best product in our category",
            "north_star_metric": "Weekly Active Users",
            "primary_persona": "The Busy Professional",
            "persona_goal": "Complete tasks efficiently without context switching",
            "strategic_pillars": ["Growth & Acquisition", "Product Excellence", "Operational Efficiency"],
            "ai_assistant": "copilot",
            "editor": "vscode",
            "include_copilot_agents": True,
            "include_examples": True,
        }
    else:
        config = gather_configuration(product_name or default_product_name, target_dir)

    # Scaffold the project with progress tree
    console.print()
    console.print("[bold cyan]Initialize Product Kit Project[/bold cyan]")
    
    try:
        scaffold_project(target_dir, config, console)
    except Exception as e:
        console.print(f"[red]✖ Error: {e}[/red]")
        sys.exit(1)

    console.print()
    console.print("[bold green]Project ready.[/bold green]")
    console.print()

    # Show next steps
    ai_assistant = config.get("ai_assistant", "copilot")
    ai_name = ai_assistant.title()
    ai_file_map = {
        "copilot": ".github/copilot-instructions.md",
        "claude": "CLAUDE.md",
        "gemini": "GEMINI.md",
        "codex": ".codex/skills",
    }
    ai_file = ai_file_map.get(ai_assistant, "AI_INSTRUCTIONS.md")
    ai_instruction_line = (
        f"4. Review [yellow]{ai_file}[/yellow] for AI assistant integration\n"
        if ai_assistant != "codex"
        else "4. Review [yellow].codex/skills[/yellow] and [yellow].codex/prompts[/yellow] for Codex commands\n"
    )

    console.print(
        Panel(
            f"[bold]Next Steps[/bold]\n\n"
            + (f"1. cd {project_name}\n" if project_name else "1. You're already in the project directory!\n")
            + f"2. git init (if not already initialized)\n"
            f"3. code . (open in VS Code)\n"
            f"{ai_instruction_line}"
            f"5. Review [yellow]constitution.md[/yellow] and customize your standards\n"
            f"6. Fill out [yellow]context/[/yellow] files with your product details\n"
            f"7. Document current state in [yellow]inventory/[/yellow]\n"
            f"8. Explore [yellow]agents/[/yellow] to understand available commands",
            title="📋 Getting Started",
            box=box.ROUNDED,
        )
    )
    console.print()

    command_label = "Skills" if ai_assistant == "codex" else "Commands"
    console.print(
        Panel(
            f"[bold]Start using slash commands with {ai_name}:[/bold]\n\n"
            f"  /productkit.clarify - Ask clarifying questions\n"
            f"  /productkit.brd - Create Business Requirements\n"
            f"  /productkit.prd - Create Product Requirements\n"
            f"  /productkit.epic - Plan large initiatives\n"
            f"  /productkit.timeline - Build implementation timeline\n"
            f"  /productkit.constitution - Review & update standards\n"
            f"  /productkit.update-context - Update product context\n"
            f"  /productkit.update-inventory - Update system inventory",
            title=f"🤖 {ai_name} {command_label}",
            box=box.ROUNDED,
        )
    )
    console.print()


@app.command("update")
def update() -> None:
    """Update templates and AI configs in the current Product Kit project."""
    print_banner()
    
    target_dir = Path.cwd()
    if not is_product_kit_project(target_dir):
        console.print("[yellow]No Product Kit project detected in the current directory.[/yellow]")
        if Confirm.ask("Do you want to initialize Product Kit here?", default=False):
            init(project_name=None, product_name=None, no_prompts=False)
            return
        console.print("[red]✖ Cancelled[/red]")
        sys.exit(0)
    
    detected = detect_ai_assistants(target_dir)
    ai_assistant = choose_ai_assistant(detected)
    editor = "vscode" if ai_assistant == "copilot" else "other"
    config = {
        "ai_assistant": ai_assistant,
        "editor": editor,
    }
    
    console.print()
    console.print("[bold cyan]Update Product Kit Project[/bold cyan]")
    
    try:
        update_project(target_dir, config, console)
    except Exception as e:
        console.print(f"[red]✖ Error: {e}[/red]")
        sys.exit(1)
    
    console.print()
    console.print("[bold green]Update complete.[/bold green]")
    console.print()


def gather_configuration(default_product_name: str, target_dir: Path) -> dict:
    """Gather configuration through interactive prompts."""
    console.print("[bold]Let's set up your Product Kit:[/bold]")
    console.print()

    product_name = Prompt.ask(
        "Product name",
        default=default_product_name,
    )

    # AI Assistant choice
    console.print()
    console.print("[bold]Select AI Assistant:[/bold]")
    console.print("  1. GitHub Copilot (VS Code)")
    console.print("  2. Claude (Claude.ai or Claude Desktop)")
    console.print("  3. Gemini (AI Studio or CLI)")
    console.print("  4. Codex (CLI or VS Code)")
    
    ai_choice = Prompt.ask(
        "Choose AI assistant",
        choices=["1", "2", "3", "4"],
        default="1",
    )
    
    ai_assistant_map = {
        "1": "copilot",
        "2": "claude",
        "3": "gemini",
        "4": "codex",
    }
    ai_assistant = ai_assistant_map[ai_choice]
    
    # Editor/Platform choice (for additional setup)
    console.print()
    if ai_assistant == "copilot":
        console.print("[bold]Select Editor:[/bold]")
        console.print("  1. VS Code")
        console.print("  2. VS Code (web)")
        console.print("  3. Other")
        
        editor_choice = Prompt.ask(
            "Choose editor",
            choices=["1", "2", "3"],
            default="1",
        )
        
        editor_map = {
            "1": "vscode",
            "2": "vscode-web",
            "3": "other",
        }
        editor = editor_map[editor_choice]
    elif ai_assistant == "claude":
        console.print("[bold]Select Platform:[/bold]")
        console.print("  1. Claude.ai (web)")
        console.print("  2. Claude Desktop")
        console.print("  3. Claude Code Editor")
        
        platform_choice = Prompt.ask(
            "Choose platform",
            choices=["1", "2", "3"],
            default="1",
        )
        
        platform_map = {
            "1": "claude-web",
            "2": "claude-desktop",
            "3": "claude-code",
        }
        editor = platform_map[platform_choice]
    elif ai_assistant == "gemini":
        console.print("[bold]Select Platform:[/bold]")
        console.print("  1. Google AI Studio (web)")
        console.print("  2. Gemini API/CLI")
        console.print("  3. IDE Extension")
        
        platform_choice = Prompt.ask(
            "Choose platform",
            choices=["1", "2", "3"],
            default="1",
        )
        
        platform_map = {
            "1": "gemini-studio",
            "2": "gemini-cli",
            "3": "gemini-ide",
        }
        editor = platform_map[platform_choice]
    elif ai_assistant == "codex":
        console.print("[bold]Select Platform:[/bold]")
        console.print("  1. Codex CLI")
        console.print("  2. Codex VS Code")
        
        platform_choice = Prompt.ask(
            "Choose platform",
            choices=["1", "2"],
            default="1",
        )
        
        platform_map = {
            "1": "codex-cli",
            "2": "codex-vscode",
        }
        editor = platform_map[platform_choice]
    else:
        editor = "other"
    
    console.print(f"[green]Selected: {ai_assistant} on {editor}[/green]")
    console.print()

    product_vision = Prompt.ask(
        "Product vision (one sentence)",
        default="Build the best product in our category",
    )

    north_star_metric = Prompt.ask(
        "North Star Metric",
        default="Weekly Active Users",
    )

    primary_persona = Prompt.ask(
        "Primary persona name",
        default="The Busy Professional",
    )

    persona_goal = Prompt.ask(
        "What does this persona want to achieve?",
        default="Complete tasks efficiently without context switching",
    )

    strategic_pillars_input = Prompt.ask(
        "Strategic pillars (comma-separated)",
        default="Growth & Acquisition, Product Excellence, Operational Efficiency",
    )
    strategic_pillars = [p.strip() for p in strategic_pillars_input.split(",")]

    include_examples = Confirm.ask(
        "Include example content in templates?",
        default=True,
    )

    return {
        "product_name": product_name,
        "product_vision": product_vision,
        "north_star_metric": north_star_metric,
        "primary_persona": primary_persona,
        "persona_goal": persona_goal,
        "strategic_pillars": strategic_pillars,
        "ai_assistant": ai_assistant,
        "editor": editor,
        "include_copilot_agents": ai_assistant == "copilot",
        "include_examples": include_examples,
    }


def print_banner() -> None:
    """Render the CLI banner."""
    console.print()
    console.print(Align.center(BANNER, style="bold cyan"))
    console.print("Requirement-Driven Design Framework", style="bold cyan", justify="center")
    console.print()


def is_product_kit_project(target_dir: Path) -> bool:
    """Heuristic check for an existing Product Kit project."""
    markers = [
        target_dir / "constitution.md",
        target_dir / "context",
        target_dir / "inventory",
        target_dir / "templates",
        target_dir / "agents",
        target_dir / "prompts",
        target_dir / ".github" / "agents",
        target_dir / ".codex" / "skills",
    ]
    return any(marker.exists() for marker in markers)


def detect_ai_assistants(target_dir: Path) -> List[str]:
    """Detect which AI assistants are configured in the project."""
    detected: List[str] = []
    if (target_dir / ".codex" / "skills").exists() or (target_dir / ".codex" / "prompts").exists():
        detected.append("codex")
    if (target_dir / ".github" / "agents").exists() or (target_dir / ".github" / "copilot-instructions.md").exists():
        detected.append("copilot")
    if (target_dir / "CLAUDE.md").exists():
        detected.append("claude")
    if (target_dir / "GEMINI.md").exists():
        detected.append("gemini")
    return detected


def choose_ai_assistant(detected: List[str]) -> str:
    """Pick an AI assistant to update, prompting when needed."""
    if len(detected) == 1:
        return detected[0]
    
    if detected:
        console.print(f"[yellow]Detected: {', '.join(detected)}[/yellow]")
    
    console.print("[bold]Select AI Assistant to update:[/bold]")
    console.print("  1. GitHub Copilot (VS Code)")
    console.print("  2. Claude (Claude.ai or Claude Desktop)")
    console.print("  3. Gemini (AI Studio or CLI)")
    console.print("  4. Codex (CLI or VS Code)")
    
    ai_assistant_map = {
        "1": "copilot",
        "2": "claude",
        "3": "gemini",
        "4": "codex",
    }
    default_choice = "1"
    for key, value in ai_assistant_map.items():
        if value in detected:
            default_choice = key
            break
    
    ai_choice = Prompt.ask(
        "Choose AI assistant",
        choices=list(ai_assistant_map.keys()),
        default=default_choice,
    )
    return ai_assistant_map[ai_choice]


if __name__ == "__main__":
    app()
