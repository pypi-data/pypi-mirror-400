"""Utility functions for project scaffolding."""
from pathlib import Path
import shutil
from typing import Dict, List
from .logger import logger


def create_project_structure(template_path: Path, target_path: Path, project_name: str) -> None:
    """
    Copy template structure to target location.
    
    Args:
        template_path: Path to the template directory
        target_path: Where to create the new project
        project_name: Name of the project
    """
    if target_path.exists():
        logger.error(f"❌ Directory '{project_name}' already exists!")
        raise FileExistsError(f"Directory '{project_name}' already exists")
    
    try:
        logger.info(f"📁 Creating project directory: {project_name}")
        shutil.copytree(template_path, target_path)
        logger.info(f"✅ Successfully created {project_name}")
        logger.info(f"📍 Location: {target_path.absolute()}")
    except Exception as e:
        logger.error(f"❌ Error creating project: {e}")
        raise


def create_files_from_list(base_path: Path, file_list: List[str]) -> None:
    """
    Create files and directories from a list of file paths.
    
    Args:
        base_path: Base directory for the project
        file_list: List of file paths to create
    """
    for filepath in file_list:
        full_path = base_path / filepath
        file_dir = full_path.parent
        
        # Create directory if needed
        if not file_dir.exists():
            file_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📂 Created directory: {file_dir.relative_to(base_path)}")
        
        # Create empty file if it doesn't exist or is empty
        if not full_path.exists() or full_path.stat().st_size == 0:
            full_path.touch()
            logger.info(f"📄 Created file: {full_path.relative_to(base_path)}")
        else:
            logger.info(f"⏭️  File already exists: {full_path.name}")


def get_available_templates() -> List[str]:
    """Return list of available project templates."""
    return ["ds", "research", "backend", "ai", "automation"]


def get_template_description(template: str) -> str:
    """Get description for a template type."""
    descriptions = {
        "ds": "Data Science project with data/, notebooks/, src/, and reports/",
        "research": "Research project with experiments/, notebooks/, and paper/",
        "backend": "Backend API project with FastAPI/Flask structure",
        "ai": "AI/ML application with models/, training/, and deployment structure",
        "automation": "Automation/scripting project with clean modular structure"
    }
    return descriptions.get(template, "Unknown template")
