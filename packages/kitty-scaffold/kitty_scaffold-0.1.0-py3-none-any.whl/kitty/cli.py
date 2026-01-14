"""Command-line interface for Kitty."""
import sys
from pathlib import Path
from .core.utils import (
    create_project_structure,
    get_available_templates,
    get_template_description
)
from .core.logger import logger


def show_help():
    """Display help information."""
    help_text = """
🐱 Kitty - Project Scaffolding Tool

Usage:
    kitty init <type> <project_name>    Create a new project
    kitty list                          List available templates
    kitty help                          Show this help message

Available Templates:
"""
    print(help_text)
    for template in get_available_templates():
        desc = get_template_description(template)
        print(f"    {template:12} - {desc}")
    
    print("\nExamples:")
    print("    kitty init ds my_data_project")
    print("    kitty init ai chatbot_app")
    print("    kitty init backend api_server")
    print()


def list_templates():
    """List all available project templates."""
    logger.info("📋 Available project templates:\n")
    for template in get_available_templates():
        desc = get_template_description(template)
        print(f"  • {template:12} - {desc}")
    print()


def init_project(project_type: str, project_name: str):
    """
    Initialize a new project from template.
    
    Args:
        project_type: Type of project (ds, research, backend, etc.)
        project_name: Name for the new project
    """
    available = get_available_templates()
    
    if project_type not in available:
        logger.error(f"❌ Unknown project type: '{project_type}'")
        logger.info(f"Available types: {', '.join(available)}")
        logger.info("Run 'kitty list' to see all templates")
        sys.exit(1)
    
    # Get template path
    base_path = Path(__file__).parent
    template_path = base_path / "templates" / project_type
    
    if not template_path.exists():
        logger.error(f"❌ Template not found: {project_type}")
        logger.error(f"Expected at: {template_path}")
        sys.exit(1)
    
    # Create project
    target_path = Path.cwd() / project_name
    
    try:
        create_project_structure(template_path, target_path, project_name)
        
        # Success message
        print()
        logger.info("🎉 Project created successfully!")
        logger.info(f"📂 Type: {project_type}")
        logger.info(f"📍 Path: {target_path.absolute()}")
        print()
        logger.info("Next steps:")
        print(f"  cd {project_name}")
        print(f"  pip install -r requirements.txt  # if applicable")
        print()
        
    except FileExistsError:
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Failed to create project: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    args = sys.argv[1:]
    
    # No arguments - show help
    if len(args) == 0:
        show_help()
        return
    
    command = args[0]
    
    # Handle commands
    if command in ["help", "-h", "--help"]:
        show_help()
    
    elif command == "list":
        list_templates()
    
    elif command == "init":
        if len(args) < 3:
            logger.error("❌ Usage: kitty init <type> <project_name>")
            logger.info("Example: kitty init ds my_project")
            sys.exit(1)
        
        project_type = args[1]
        project_name = args[2]
        init_project(project_type, project_name)
    
    else:
        logger.error(f"❌ Unknown command: '{command}'")
        logger.info("Run 'kitty help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
