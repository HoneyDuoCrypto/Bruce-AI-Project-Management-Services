#!/usr/bin/env python3
"""
Bruce Init Command Implementation
Adds 'bruce init' functionality to the existing CLI
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

def create_bruce_config(project_name: str, project_description: str = "", project_root: Path = None) -> Dict[str, Any]:
    """Create a bruce.yaml configuration with sensible defaults"""
    
    if project_root is None:
        project_root = Path.cwd()
    
    config = {
        'project': {
            'name': project_name,
            'description': project_description or f"AI-assisted development project: {project_name}",
            'type': 'ai-assisted',
            'created': datetime.now().isoformat(),
            'root_dir': str(project_root)
        },
        'bruce': {
            'version': '2.0',
            'contexts_dir': 'bruce_contexts',
            'phases_dir': 'phases', 
            'blueprints_dir': 'docs/blueprints',
            'sessions_dir': 'docs/sessions',
            'reports_dir': 'bruce_reports'
        },
        'web_ui': {
            'title': f'🤖 {project_name} - Bruce Assistant',
            'port': 5000,
            'auth': {
                'username': 'bruce',
                'password': 'change-me-please!'
            }
        },
        'features': {
            'enhanced_context': True,
            'blueprint_generation': True,
            'session_handoffs': True,
            'git_integration': True
        }
    }
    
    return config

def create_directory_structure(project_root: Path, config: Dict[str, Any]) -> None:
    """Create the Bruce directory structure"""
    
    # Create main directories
    directories = [
        config['bruce']['contexts_dir'],
        config['bruce']['phases_dir'],
        config['bruce']['blueprints_dir'],
        config['bruce']['sessions_dir'], 
        config['bruce']['reports_dir'],
        'src',
        'cli',
        'tests'
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}/")

def create_gitignore(project_root: Path) -> None:
    """Create or update .gitignore with Bruce-specific entries"""
    
    gitignore_entries = [
        "# Bruce Project Management",
        "bruce_contexts/",
        "bruce_reports/",
        "docs/sessions/",
        ".task_context_*.md",
        "",
        "# Python",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        "*.so",
        ".Python",
        "env/",
        "venv/",
        ".venv",
        "",
        "# IDE",
        ".vscode/",
        ".idea/",
        "*.swp",
        "*.swo",
        "",
        "# OS",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    gitignore_path = project_root / '.gitignore'
    
    if gitignore_path.exists():
        # Read existing gitignore
        with open(gitignore_path, 'r') as f:
            existing = f.read()
        
        # Only add Bruce entries if they don't exist
        if "# Bruce Project Management" not in existing:
            with open(gitignore_path, 'a') as f:
                f.write('\n' + '\n'.join(gitignore_entries))
            print("✓ Updated .gitignore with Bruce entries")
        else:
            print("✓ .gitignore already contains Bruce entries")
    else:
        # Create new gitignore
        with open(gitignore_path, 'w') as f:
            f.write('\n'.join(gitignore_entries))
        print("✓ Created .gitignore")

def create_sample_phase(project_root: Path, project_name: str) -> None:
    """Create a sample phase file to get started"""
    
    sample_phase = {
        'phase': {
            'id': 1,
            'name': 'Project Setup',
            'description': f'Initial setup and configuration for {project_name}'
        },
        'tasks': [
            {
                'id': 'setup-environment',
                'description': 'Set up development environment and dependencies',
                'output': 'Working development environment with all tools configured',
                'status': 'pending',
                'acceptance_criteria': [
                    'All required dependencies are installed',
                    'Development environment is functional',
                    'Bruce interface is accessible'
                ]
            },
            {
                'id': 'define-requirements',
                'description': 'Define project requirements and initial architecture',
                'output': 'Requirements document and initial architecture design',
                'status': 'pending',
                'depends_on': ['setup-environment'],
                'acceptance_criteria': [
                    'Clear requirements documentation',
                    'Initial architecture diagram',
                    'Technology stack decisions documented'
                ]
            }
        ]
    }
    
    phase_file = project_root / 'phases' / 'phase1_setup.yml'
    with open(phase_file, 'w') as f:
        yaml.dump(sample_phase, f, default_flow_style=False, indent=2, sort_keys=False)
    
    print(f"✓ Created sample phase: phases/phase1_setup.yml")

def create_readme(project_root: Path, project_name: str) -> None:
    """Create a README with Bruce usage instructions"""
    
    readme_content = f"""# {project_name}

This project uses **Bruce** - an AI-assisted project management system designed for seamless Claude session handoffs.

## Quick Start

1. **Start the web interface:**
   ```bash
   bruce ui
   ```
   Access at: http://localhost:5000
   Login: bruce / change-me-please!

2. **Use the CLI:**
   ```bash
   # Check project status
   bruce status
   
   # List all tasks
   bruce list
   
   # Start a task with enhanced context
   bruce start <task-id>
   
   # Complete a task
   bruce commit <task-id>
   ```

## Project Structure

- `phases/` - Task definitions organized by project phases
- `bruce_contexts/` - Generated context files for Claude sessions
- `docs/blueprints/` - Auto-generated project documentation
- `docs/sessions/` - Session handoff documents for Claude
- `bruce_reports/` - Status reports and progress tracking

## Bruce Features

- **Enhanced Context**: Automatically finds related tasks and decisions
- **Blueprint Generation**: Creates comprehensive technical documentation
- **Session Handoffs**: Seamless context preservation between Claude sessions
- **Multi-Phase Organization**: Organize work into logical phases
- **Progress Tracking**: Visual progress bars and status reports

## Configuration

Edit `bruce.yaml` to customize:
- Project settings
- Directory locations  
- Web UI configuration
- Feature toggles

## Getting Help

- Web UI: Built-in help and tutorials
- CLI: `bruce --help` or `bruce <command> --help`
- Documentation: Check `docs/blueprints/` for auto-generated docs

---

*Powered by Bruce - AI-Assisted Project Management*
"""
    
    readme_path = project_root / 'README.md'
    if not readme_path.exists():
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print("✓ Created README.md with Bruce usage instructions")
    else:
        print("✓ README.md already exists (not modified)")

def cmd_init(project_name: str = None, project_description: str = "", force: bool = False) -> None:
    """
    Initialize a new Bruce project in the current directory
    
    Args:
        project_name: Name of the project (defaults to directory name)
        project_description: Description of the project
        force: Force initialization even if bruce.yaml exists
    """
    
    project_root = Path.cwd()
    
    # Use directory name if no project name provided
    if not project_name:
        project_name = project_root.name
        if project_name == ".":
            project_name = "My Bruce Project"
    
    # Check if already initialized
    bruce_config_path = project_root / 'bruce.yaml'
    if bruce_config_path.exists() and not force:
        print(f"❌ Bruce project already initialized in {project_root}")
        print("   Use --force to reinitialize or 'bruce status' to check current project")
        return
    
    print(f"🤖 Bruce: Initializing AI-assisted project management...")
    print(f"📁 Project: {project_name}")
    print(f"📍 Location: {project_root}")
    print()
    
    try:
        # Create configuration
        config = create_bruce_config(project_name, project_description, project_root)
        
        # Save bruce.yaml
        with open(bruce_config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2, sort_keys=False)
        print("✓ Created bruce.yaml")
        
        # Create directory structure
        create_directory_structure(project_root, config)
        
        # Create .gitignore
        create_gitignore(project_root)
        
        # Create sample phase
        create_sample_phase(project_root, project_name)
        
        # Create README
        create_readme(project_root, project_name)
        
        print()
        print("🎉 Bruce project initialized successfully!")
        print()
        print("📋 Next steps:")
        print("  1. Edit bruce.yaml to customize your project settings")
        print("  2. Review the sample phase in phases/phase1_setup.yml")
        print("  3. Start the web interface: bruce ui")
        print("  4. Or use the CLI: bruce status")
        print()
        print("🚀 Ready to begin AI-assisted development!")
        
    except Exception as e:
        print(f"❌ Failed to initialize Bruce project: {e}")
        print("Please check permissions and try again.")
        sys.exit(1)

def add_init_to_existing_cli():
    """
    Function to demonstrate how to add the init command to the existing CLI
    This would be integrated into cli/hdw-task.py or the new bruce-task.py
    """
    
    # This is how you'd add it to the existing argparse structure:
    init_parser = subparsers.add_parser("init", help="Initialize Bruce in current directory")
    init_parser.add_argument("project_name", nargs="?", help="Project name (defaults to directory name)")
    init_parser.add_argument("--description", help="Project description")
    init_parser.add_argument("--force", action="store_true", help="Force initialization even if bruce.yaml exists")
    
    # In the main command handling:
    if args.command == 'init':
        cmd_init(args.project_name, args.description or "", args.force)

# Integration point for existing CLI
def integrate_with_cli():
    """
    Instructions for integrating with the existing CLI structure
    """
    integration_instructions = """
    
    TO INTEGRATE WITH EXISTING CLI:
    
    1. Add this import to cli/hdw-task.py (or bruce-task.py):
       from bruce_init import cmd_init
    
    2. Add the subparser (in main() function):
       init_parser = subparsers.add_parser("init", help="Initialize Bruce in current directory")
       init_parser.add_argument("project_name", nargs="?", help="Project name (defaults to directory name)")
       init_parser.add_argument("--description", help="Project description")
       init_parser.add_argument("--force", action="store_true", help="Force initialization")
    
    3. Add the command handler:
       elif args.command == 'init':
           cmd_init(args.project_name, args.description or "", args.force)
    
    USAGE EXAMPLES:
    
    # Initialize with directory name
    bruce init
    
    # Initialize with custom name
    bruce init "My Trading Bot"
    
    # Initialize with description
    bruce init "Trading Bot" --description "High-frequency trading system"
    
    # Force reinitialize
    bruce init --force
    
    """
    print(integration_instructions)

if __name__ == "__main__":
    # Simple test/demo
    import argparse
    
    parser = argparse.ArgumentParser(description="Bruce Init Command")
    parser.add_argument("project_name", nargs="?", help="Project name")
    parser.add_argument("--description", help="Project description")
    parser.add_argument("--force", action="store_true", help="Force initialization")
    parser.add_argument("--demo", action="store_true", help="Show integration instructions")
    
    args = parser.parse_args()
    
    if args.demo:
        integrate_with_cli()
    else:
        cmd_init(args.project_name, args.description or "", args.force)