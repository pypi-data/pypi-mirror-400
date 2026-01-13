"""Project scaffolding logic."""

import re
import shutil
from pathlib import Path
from typing import Any, Dict

from rich.console import Console
from rich.tree import Tree


def scaffold_project(target_dir: Path, config: Dict[str, Any], console: Console) -> None:
    """
    Scaffold a new Product Kit project.
    
    Args:
        target_dir: Target directory for the project
        config: Configuration dictionary from prompts
        console: Rich console for output
    """
    # Create progress tree
    tree = Tree("├── [cyan]●[/cyan] Initialize directory structure")
    
    # Get the data directory (either from package or development)
    package_dir = Path(__file__).parent  # /product-kit/cli/src/product_kit
    data_dir = package_dir / "data"
    
    # If data dir doesn't exist (development mode), use root directory
    if not data_dir.exists():
        root_dir = package_dir.parent.parent.parent  # /product-kit
    else:
        root_dir = data_dir
    
    # Verify we have the necessary files
    if not (root_dir / "agents").exists():
        raise FileNotFoundError(
            f"Cannot find product-kit data. "
            f"Expected agents/ folder at {root_dir}"
        )
    
    # Create directory structure
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "context").mkdir(exist_ok=True)
    (target_dir / "inventory").mkdir(exist_ok=True)
    (target_dir / "templates").mkdir(exist_ok=True)
    (target_dir / "agents").mkdir(exist_ok=True)
    (target_dir / "prompts").mkdir(exist_ok=True)
    
    # Determine AI-specific folder
    ai_assistant = config.get("ai_assistant", "copilot")
    if ai_assistant == "copilot":
        (target_dir / ".github").mkdir(exist_ok=True)
    # Claude uses CLAUDE.md in root, Gemini uses .gemini/
    # No additional folders needed for Claude
    # Gemini structure TBD
    
    tree.add("[cyan]●[/cyan] Select AI assistant ([green]" + ai_assistant + "[/green])")
    console.print(tree)
    
    # Define replacements
    replacements = build_replacements(config)
    
    # Copy core files
    step = tree.add("[cyan]●[/cyan] Copy template files")
    files_copied = copy_template_files(root_dir, target_dir, config, replacements, step, console)
    console.print(tree)
    
    # Copy AI-specific agents
    step_agents = tree.add("[cyan]●[/cyan] Setup AI agent configurations")
    copy_ai_agents(root_dir, target_dir, config, step_agents)
    console.print(tree)
    
    # Create editor-specific configuration
    step_editor = tree.add("[cyan]●[/cyan] Setup editor configuration")
    create_editor_config(target_dir, config)
    console.print(tree)
    
    # Create .gitignore
    step_git = tree.add("[cyan]●[/cyan] Create .gitignore")
    create_gitignore(target_dir, config)
    console.print(tree)
    
    # Finalize
    tree.add("[cyan]●[/cyan] Finalize (project ready)")
    console.print(tree)


def build_replacements(config: Dict[str, Any]) -> Dict[str, str]:
    """Build replacement dictionary from config."""
    # Extract persona name parts
    persona_parts = config["primary_persona"].split()
    representative_name = persona_parts[-1] if persona_parts else "Alex"
    
    # Build pillars
    pillars = config.get("strategic_pillars", [])
    
    return {
        "[PRODUCT_NAME]": config["product_name"],
        "[EXECUTIVE_SUMMARY]": config["product_vision"],
        "[NORTH_STAR_METRIC]": config["north_star_metric"],
        "[PERSONA_1_NAME]": config["primary_persona"],
        "[REPRESENTATIVE_NAME]": representative_name,
        "[GOAL_1]": f'"{config["persona_goal"]}"',
        "[STRATEGIC_PILLAR_1]": pillars[0] if len(pillars) > 0 else "Growth & Acquisition",
        "[STRATEGIC_PILLAR_2]": pillars[1] if len(pillars) > 1 else "Product Excellence",
        "[STRATEGIC_PILLAR_3]": pillars[2] if len(pillars) > 2 else "Operational Efficiency",
    }


def render_template_file(
    src_file: Path,
    dest_file: Path,
    replacements: Dict[str, str],
    include_examples: bool,
    console: Console,
) -> None:
    """
    Render a template file with replacements.
    
    Args:
        src_file: Source template file
        dest_file: Destination file
        replacements: Dictionary of placeholder -> value
        include_examples: Whether to include example sections
        console: Rich console for output
    """
    content = src_file.read_text(encoding="utf-8")
    
    # Apply replacements
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    
    # Remove example sections if not wanted
    if not include_examples:
        # Remove HTML comment blocks with examples
        content = re.sub(r"<!-- Example:.*?-->", "", content, flags=re.DOTALL)
        # Clean up excessive newlines
        content = re.sub(r"\n{3,}", "\n\n", content)
    
    # Write to destination
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    dest_file.write_text(content, encoding="utf-8")
    
    console.print(f"  [gray]✓ {dest_file.relative_to(dest_file.parent.parent)}[/gray]")


def copy_template_files(
    root_dir: Path, 
    target_dir: Path, 
    config: Dict[str, Any],
    replacements: Dict[str, str],
    tree_node: Tree,
    console: Console,
) -> int:
    """Copy and render template files."""
    files_to_copy = [
        ("constitution.md", "constitution.md"),
        ("context/product-vision.md", "context/product-vision.md"),
        ("context/personas.md", "context/personas.md"),
        ("context/glossary.md", "context/glossary.md"),
        ("context/market_research.md", "context/market_research.md"),
        ("inventory/feature-catalog.md", "inventory/feature-catalog.md"),
        ("inventory/tech-constraints.md", "inventory/tech-constraints.md"),
        ("inventory/data-model.md", "inventory/data-model.md"),
        ("inventory/product-map.md", "inventory/product-map.md"),
        ("templates/brd_template.md", "templates/brd_template.md"),
        ("templates/prd_template.md", "templates/prd_template.md"),
        ("templates/epic_template.md", "templates/epic_template.md"),
    ]
    
    ai_assistant = config.get("ai_assistant", "copilot")
    if ai_assistant == "copilot":
        files_to_copy.append((".ai-providers/copilot-instructions.md", ".github/copilot-instructions.md"))
    elif ai_assistant == "claude":
        files_to_copy.append((".ai-providers/CLAUDE.md", "CLAUDE.md"))
    elif ai_assistant == "gemini":
        files_to_copy.append((".ai-providers/GEMINI.md", "GEMINI.md"))
    
    count = 0
    for src_path, dest_path in files_to_copy:
        src_file = root_dir / src_path
        dest_file = target_dir / dest_path
        
        if src_file.exists():
            content = src_file.read_text(encoding="utf-8")
            
            # Apply replacements
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
            
            # Remove examples if not wanted
            if not config.get("include_examples", True):
                content = re.sub(r"<!-- Example:.*?-->", "", content, flags=re.DOTALL)
                content = re.sub(r"\n{3,}", "\n\n", content)
            
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            dest_file.write_text(content, encoding="utf-8")
            count += 1
    
    tree_node.label = f"[cyan]●[/cyan] Copy template files ([green]{count} files[/green])"
    return count


def copy_ai_agents(
    root_dir: Path,
    target_dir: Path,
    config: Dict[str, Any],
    tree_node: Tree,
) -> None:
    """Copy AI-specific agent and prompt files to shared directories."""
    ai_assistant = config.get("ai_assistant", "copilot")
    
    agents_src = root_dir / "agents"
    prompts_src = root_dir / "prompts"
    
    # All providers get agents/ and prompts/ in root
    agents_dest = target_dir / "agents"
    prompts_dest = target_dir / "prompts"
    
    count = 0
    
    # Copy agent files to root
    if agents_src.exists():
        agents_dest.mkdir(parents=True, exist_ok=True)
        for agent_file in agents_src.glob("*.md"):
            dest_file = agents_dest / agent_file.name
            shutil.copy2(agent_file, dest_file)
            count += 1
    
    # Copy prompt files to root
    if prompts_src.exists():
        prompts_dest.mkdir(parents=True, exist_ok=True)
        for prompt_file in prompts_src.glob("*.md"):
            dest_file = prompts_dest / prompt_file.name
            shutil.copy2(prompt_file, dest_file)
            count += 1
    
    # GitHub Copilot also needs agents/ and prompts/ in .github for slash commands
    if ai_assistant == "copilot":
        github_dir = target_dir / ".github"
        github_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy entire agents folder to .github/agents/
        if agents_src.exists():
            github_agents = github_dir / "agents"
            github_agents.mkdir(parents=True, exist_ok=True)
            for agent_file in agents_src.glob("*.md"):
                dest_file = github_agents / agent_file.name
                shutil.copy2(agent_file, dest_file)
                count += 1
        
        # Copy entire prompts folder to .github/prompts/
        if prompts_src.exists():
            github_prompts = github_dir / "prompts"
            github_prompts.mkdir(parents=True, exist_ok=True)
            for prompt_file in prompts_src.glob("*.md"):
                dest_file = github_prompts / prompt_file.name
                shutil.copy2(prompt_file, dest_file)
                count += 1
    
    tree_node.label = f"[cyan]●[/cyan] Setup AI agent configurations ([green]{count} files[/green])"


def create_editor_config(target_dir: Path, config: Dict[str, Any]) -> None:
    """Create editor-specific configuration files."""
    ai_assistant = config.get("ai_assistant", "copilot")
    editor = config.get("editor", "vscode")
    
    # Create .vscode/settings.json for VS Code + GitHub Copilot
    if ai_assistant == "copilot" and editor in ["vscode", "vscode-web"]:
        vscode_dir = target_dir / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        settings = {
            "chat.promptFilesRecommendations": {
                "productkit.clarify": True,
                "productkit.brd": True,
                "productkit.prd": True,
                "productkit.epic": True,
                "productkit.constitution": True,
                "productkit.update-context": True,
                "productkit.update-inventory": True
            }
        }
        
        import json
        settings_file = vscode_dir / "settings.json"
        settings_file.write_text(json.dumps(settings, indent=4))


def create_gitignore(target_dir: Path, config: Dict[str, Any]) -> None:
    """Create .gitignore file."""
    gitignore_path = target_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_content = """# Product Kit
.DS_Store
*.swp
*.swo
*~
.vscode/
.idea/
__pycache__/
*.pyc
.env
"""
        gitignore_path.write_text(gitignore_content)