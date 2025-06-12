#!/usr/bin/env python3
"""
Bruce Task CLI - Complete Portable Version
Enhanced with Dynamic Task/Phase Management and Init Command
Save as: cli/bruce-task.py
"""

import argparse
import sys
import yaml
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add src to path to import TaskManager
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import TaskManager, but handle gracefully if not available
try:
    from src.task_manager import TaskManager
    TASK_MANAGER_AVAILABLE = True
except ImportError:
    TASK_MANAGER_AVAILABLE = False
    print("⚠️  TaskManager not found - some features may be limited")

def load_bruce_config(project_root: Path = None) -> Dict[str, Any]:
    """Load bruce.yaml configuration with fallbacks"""
    if project_root is None:
        project_root = Path.cwd()
    
    config_path = project_root / 'bruce.yaml'
    
    # Default configuration
    default_config = {
        'project': {
            'name': project_root.name,
            'description': f'AI-assisted project: {project_root.name}',
            'type': 'ai-assisted'
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
            'title': f'🤖 {project_root.name} - Bruce Assistant',
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
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                # Merge user config with defaults
                if user_config:
                    default_config.update(user_config)
        except Exception as e:
            print(f"⚠️  Error loading bruce.yaml: {e}")
            print("Using default configuration...")
    
    return default_config

def get_project_root() -> Path:
    """Find project root by looking for bruce.yaml or using current directory"""
    current = Path.cwd()
    
    # Look up the directory tree for bruce.yaml
    for parent in [current] + list(current.parents):
        if (parent / 'bruce.yaml').exists():
            return parent
    
    # If not found, use current directory
    return current

def initialize_task_manager() -> Optional['TaskManager']:
    """Initialize TaskManager with project-relative paths"""
    if not TASK_MANAGER_AVAILABLE:
        return None
    
    project_root = get_project_root()
    return TaskManager(project_root)

# ===== BRUCE INIT COMMAND =====

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
    """Initialize a new Bruce project in the current directory"""
    
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

# ===== UTILITY FUNCTIONS =====

def run_cli_command(command: str, project_root: Path = None) -> Dict[str, Any]:
    """Run CLI command and return result"""
    if project_root is None:
        project_root = get_project_root()
    
    try:
        cmd = f"python3 {project_root}/cli/bruce-task.py {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=project_root)
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

def check_bruce_project() -> bool:
    """Check if we're in a Bruce project"""
    project_root = get_project_root()
    return (project_root / 'bruce.yaml').exists()

def require_bruce_project():
    """Ensure we're in a Bruce project, exit if not"""
    if not check_bruce_project():
        print("❌ Not in a Bruce project directory")
        print("Run 'bruce init' to initialize Bruce in this directory")
        print("Or navigate to a directory with bruce.yaml")
        sys.exit(1)

# ===== COMMAND IMPLEMENTATIONS =====

def cmd_list_enhanced(task_manager: 'TaskManager', status_filter=None, phase_filter=None):
    """Enhanced list command with phase support"""
    tasks_data = task_manager.load_tasks()
    tasks = tasks_data.get("tasks", [])
    
    # Apply filters
    if status_filter:
        tasks = [t for t in tasks if t.get("status") == status_filter]
    if phase_filter is not None:
        tasks = [t for t in tasks if t.get("phase", 0) == phase_filter]
    
    if not tasks:
        print("No tasks found.")
        return
    
    # Group by phase
    tasks_by_phase = {}
    for task in tasks:
        phase = task.get("phase", 0)
        if phase not in tasks_by_phase:
            tasks_by_phase[phase] = []
        tasks_by_phase[phase].append(task)
    
    # Display tasks grouped by phase
    for phase in sorted(tasks_by_phase.keys()):
        phase_tasks = tasks_by_phase[phase]
        phase_info = tasks_data.get("phases", {}).get(str(phase), {})
        phase_name = phase_info.get("name", "Legacy Tasks" if phase == 0 else f"Phase {phase}")
        
        print(f"\n📋 {phase_name} ({len(phase_tasks)} tasks):")
        print("-" * 80)
        
        for task in phase_tasks:
            status = task.get("status", "pending")
            status_emoji = {
                "pending": "⏳",
                "in-progress": "🔄", 
                "completed": "✅",
                "blocked": "🚫"
            }.get(status, "❓")
            
            print(f"{status_emoji} {task['id']:<20} {status:<12} {task.get('description', '')}")

def cmd_status_enhanced(task_manager: 'TaskManager', task_id=None):
    """Enhanced status command with phase progress"""
    if task_id:
        # Show specific task details
        tasks_data = task_manager.load_tasks()
        task = None
        for t in tasks_data.get("tasks", []):
            if t["id"] == task_id:
                task = t
                break
        
        if not task:
            print(f"❌ Task '{task_id}' not found")
            return
        
        print(f"\n📄 Task: {task['id']}")
        print(f"Phase: {task.get('phase', 0)} - {task.get('phase_name', 'Legacy')}")
        print(f"Status: {task.get('status', 'pending')}")
        print(f"Description: {task.get('description', '')}")
        print(f"Output: {task.get('output', '')}")
        if task.get('context'):
            print(f"Context: {', '.join(task['context'])}")
        if task.get('acceptance_criteria'):
            print("Acceptance Criteria:")
            for criteria in task['acceptance_criteria']:
                print(f"  - {criteria}")
        if task.get('updated'):
            print(f"Updated: {task['updated']}")
    else:
        # Show overall project status with phase breakdown
        config = load_bruce_config()
        tasks_data = task_manager.load_tasks()
        tasks = tasks_data.get("tasks", [])
        
        print(f"\n🤖 Bruce Project Status: {config['project']['name']}")
        print("-" * 50)
        
        # Overall stats
        status_counts = {}
        for task in tasks:
            status = task.get("status", "pending")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total_tasks = len(tasks)
        if total_tasks > 0:
            print(f"📊 Total Tasks: {total_tasks}")
            for status, count in status_counts.items():
                percentage = (count / total_tasks) * 100
                print(f"  {status}: {count} ({percentage:.1f}%)")
        else:
            print("📊 No tasks found - run 'bruce init' or add tasks in phases/")
        
        # Phase progress
        if TASK_MANAGER_AVAILABLE:
            phase_progress = task_manager.get_phase_progress()
            if phase_progress:
                print(f"\n📈 Phase Progress:")
                print("-" * 50)
                for phase_id in sorted(phase_progress.keys()):
                    progress = phase_progress[phase_id]
                    bar_length = 20
                    filled = int(bar_length * progress["percentage"] / 100)
                    bar = "█" * filled + "░" * (bar_length - filled)
                    
                    print(f"Phase {phase_id}: {progress['name']}")
                    print(f"  [{bar}] {progress['percentage']:.0f}% ({progress['completed']}/{progress['total']})")

def cmd_commit_enhanced(task_manager: 'TaskManager', task_id: str, message=None):
    """Enhanced commit with proper task updates and blueprint generation"""
    import subprocess
    from datetime import datetime
    
    # Find task to get current data
    tasks_data = task_manager.load_tasks()
    task = None
    for t in tasks_data.get("tasks", []):
        if t["id"] == task_id:
            task = t
            break
    
    if not task:
        print(f"❌ Task '{task_id}' not found")
        return
    
    # Update task
    commit_message = message or f"Complete task: {task_id}"
    updates = {
        "status": "completed",
        "updated": datetime.now().isoformat(),
        "notes": task.get("notes", []) + [{
            "timestamp": datetime.now().isoformat(),
            "note": f"Task committed: {commit_message}"
        }]
    }
    
    task_manager.save_task_updates(task_id, updates)
    
    # Git operations
    project_root = get_project_root()
    try:
        subprocess.run(["git", "add", "."], cwd=project_root, check=True)
        subprocess.run(["git", "commit", "-m", commit_message], cwd=project_root, check=True)
        print(f"✅ Task {task_id} committed to git")
    except subprocess.CalledProcessError:
        print(f"⚠️  Git commit failed (not in git repo?)")
    except FileNotFoundError:
        print(f"⚠️  Git not found")
    
    # Clean up context file
    config = load_bruce_config()
    contexts_dir = project_root / config['bruce']['contexts_dir']
    for context_dir in contexts_dir.glob("phase*"):
        context_file = context_dir / f"context_{task_id}.md"
        if context_file.exists():
            context_file.unlink()
            break
    
    # Also check old location for backward compatibility
    old_context_file = project_root / f".task_context_{task_id}.md"
    if old_context_file.exists():
        old_context_file.unlink()
    
    print(f"✅ Task {task_id} marked as completed")
    
    # Auto-generate blueprint documentation
    try:
        from src.blueprint_generator import PhaseBlueprintGenerator
        generator = PhaseBlueprintGenerator(project_root)
        blueprint_results = generator.auto_generate_on_completion(task_id)
        
        if blueprint_results and "error" not in blueprint_results:
            print("\n📋 Auto-generated blueprints:")
            for doc_type, filepath in blueprint_results.items():
                print(f"  ✅ {doc_type}: {Path(filepath).name}")
        elif blueprint_results and "error" in blueprint_results:
            print(f"\n⚠️  Blueprint generation warning: {blueprint_results['error']}")
    except ImportError:
        print("\n⚠️  Blueprint generator not available (src/blueprint_generator.py not found)")
    except Exception as e:
        print(f"\n⚠️  Blueprint generation failed: {e}")

def cmd_block_enhanced(task_manager: 'TaskManager', task_id: str, reason: str):
    """Enhanced block command"""
    from datetime import datetime
    
    # Find task
    tasks_data = task_manager.load_tasks()
    task = None
    for t in tasks_data.get("tasks", []):
        if t["id"] == task_id:
            task = t
            break
    
    if not task:
        print(f"❌ Task '{task_id}' not found")
        return
    
    # Update task
    updates = {
        "status": "blocked",
        "updated": datetime.now().isoformat(),
        "notes": task.get("notes", []) + [{
            "timestamp": datetime.now().isoformat(),
            "note": f"Blocked: {reason}"
        }]
    }
    
    task_manager.save_task_updates(task_id, updates)
    print(f"🚫 Task {task_id} marked as blocked: {reason}")

def cmd_phases(task_manager: 'TaskManager'):
    """Show detailed phase progress"""
    if not TASK_MANAGER_AVAILABLE:
        print("❌ TaskManager not available")
        return
        
    phase_progress = task_manager.get_phase_progress()
    tasks_data = task_manager.load_tasks()
    
    print("\n📊 Phase Overview")
    print("=" * 60)
    
    for phase_id in sorted(phase_progress.keys()):
        progress = phase_progress[phase_id]
        phase_info = tasks_data.get("phases", {}).get(str(phase_id), {})
        
        # Progress bar
        bar_length = 30
        filled = int(bar_length * progress["percentage"] / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"\n📁 Phase {phase_id}: {progress['name']}")
        if phase_info.get("description"):
            print(f"   {phase_info['description']}")
        
        print(f"\n   Progress: [{bar}] {progress['percentage']:.0f}%")
        print(f"   Tasks: {progress['completed']} completed, {progress['in_progress']} in progress, {progress['pending']} pending")
        
        if progress["blocked"] > 0:
            print(f"   ⚠️  Blocked: {progress['blocked']} tasks")

def cmd_ui():
    """Start the Bruce web interface"""
    project_root = get_project_root()
    config = load_bruce_config()
    
    # Look for the web interface file
    web_files = ['bruce_complete.py', 'bruce.py']
    web_file = None
    
    for filename in web_files:
        if (project_root / filename).exists():
            web_file = project_root / filename
            break
    
    if not web_file:
        print("❌ Web interface not found")
        print("Expected bruce_complete.py or bruce.py in project root")
        return
    
    print(f"🌐 Starting Bruce web interface...")
    print(f"📍 Project: {config['project']['name']}")
    print(f"🔗 URL: http://localhost:{config['web_ui']['port']}")
    print(f"🔐 Login: {config['web_ui']['auth']['username']} / {config['web_ui']['auth']['password']}")
    print()
    print("Press Ctrl+C to stop")
    
    try:
        subprocess.run([sys.executable, str(web_file)], cwd=project_root)
    except KeyboardInterrupt:
        print("\n👋 Bruce web interface stopped")
    except FileNotFoundError:
        print("❌ Python not found")

# ===== TASK MANAGEMENT COMMANDS =====

def cmd_add_task(args):
    """Add a new task to an existing phase"""
    require_bruce_project()
    
    if not TASK_MANAGER_AVAILABLE:
        print("❌ TaskManager not available - cannot add tasks")
        return
    
    task_manager = initialize_task_manager()
    
    # Check if task ID already exists
    tasks_data = task_manager.load_tasks()
    existing_task = next((t for t in tasks_data.get("tasks", []) if t["id"] == args.id), None)
    if existing_task:
        print(f"❌ Task '{args.id}' already exists")
        return
    
    # Build CLI command for TaskManager
    cmd_parts = [
        "add-task",
        f"--phase {args.phase}",
        f"--id \"{args.id}\"",
        f"--description \"{args.description}\""
    ]
    
    if args.output:
        cmd_parts.append(f"--output \"{args.output}\"")
    
    if args.context:
        context_items = [f'"{item}"' for item in args.context]
        cmd_parts.append(f"--context {' '.join(context_items)}")
    
    if args.depends_on:
        dep_items = [f'"{item}"' for item in args.depends_on]
        cmd_parts.append(f"--depends-on {' '.join(dep_items)}")
    
    if args.acceptance_criteria:
        criteria_items = [f'"{item}"' for item in args.acceptance_criteria]
        cmd_parts.append(f"--acceptance-criteria {' '.join(criteria_items)}")
    
    command = ' '.join(cmd_parts)
    result = run_cli_command(command)
    
    if result["success"]:
        print(f"✅ Added task '{args.id}' to phase {args.phase}")
    else:
        print(f"❌ Error: {result['error']}")

def cmd_add_phase(args):
    """Add a new phase"""
    require_bruce_project()
    
    if not TASK_MANAGER_AVAILABLE:
        print("❌ TaskManager not available - cannot add phases")
        return
    
    command = f'add-phase --id {args.id} --name "{args.name}" --description "{args.description}"'
    result = run_cli_command(command)
    
    if result["success"]:
        print(f"✅ Created phase {args.id}: {args.name}")
    else:
        print(f"❌ Error: {result['error']}")

# ===== MAIN CLI FUNCTION =====

def main():
    parser = argparse.ArgumentParser(
        description="🤖 Bruce - AI-Assisted Project Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bruce init "My AI Project"          # Initialize new project
  bruce status                        # Show project status  
  bruce list                          # List all tasks
  bruce start task-id                 # Start a task
  bruce commit task-id                # Complete a task
  bruce ui                            # Start web interface

For more help: bruce <command> --help
        """
    )
    parser.add_argument("--project-root", type=Path, help="Project root directory (auto-detected)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize Bruce in current directory")
    init_parser.add_argument("project_name", nargs="?", help="Project name (defaults to directory name)")
    init_parser.add_argument("--description", help="Project description")
    init_parser.add_argument("--force", action="store_true", help="Force initialization even if bruce.yaml exists")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show project status")
    status_parser.add_argument("task_id", nargs="?", help="Specific task ID")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--phase", type=int, help="Filter by phase")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start a task")
    start_parser.add_argument("task_id", help="Task ID to start")
    start_parser.add_argument("--basic", action="store_true", 
                            help="Use basic context instead of enhanced (default: enhanced)")
    
    # Commit command
    commit_parser = subparsers.add_parser("commit", help="Complete and commit a task")
    commit_parser.add_argument("task_id", help="Task ID to complete")
    commit_parser.add_argument("--message", help="Commit message")
    
    # Block command
    block_parser = subparsers.add_parser("block", help="Block a task")
    block_parser.add_argument("task_id", help="Task ID to block")
    block_parser.add_argument("reason", help="Reason for blocking")
    
    # Phases command
    phases_parser = subparsers.add_parser("phases", help="Show phase progress")
    
    # UI command
    ui_parser = subparsers.add_parser("ui", help="Start web interface")
    
    # Add task command
    add_task_parser = subparsers.add_parser("add-task", help="Add new task to phase")
    add_task_parser.add_argument("--phase", type=int, required=True, help="Phase ID")
    add_task_parser.add_argument("--id", required=True, help="Task ID")
    add_task_parser.add_argument("--description", required=True, help="Task description")
    add_task_parser.add_argument("--output", help="Expected output")
    add_task_parser.add_argument("--context", nargs="*", help="Context files")
    add_task_parser.add_argument("--depends-on", nargs="*", help="Task dependencies")
    add_task_parser.add_argument("--acceptance-criteria", nargs="*", help="Acceptance criteria")
    
    # Add phase command
    add_phase_parser = subparsers.add_parser("add-phase", help="Add new phase")
    add_phase_parser.add_argument("--id", type=int, required=True, help="Phase ID")
    add_phase_parser.add_argument("--name", required=True, help="Phase name")
    add_phase_parser.add_argument("--description", required=True, help="Phase description")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle init command (doesn't require existing project)
    if args.command == "init":
        cmd_init(args.project_name, args.description or "", args.force)
        return
    
    # All other commands require a Bruce project
    require_bruce_project()
    
    # Initialize TaskManager for commands that need it
    task_manager = None
    if TASK_MANAGER_AVAILABLE and args.command in ['list', 'status', 'start', 'commit', 'block', 'phases']:
        task_manager = initialize_task_manager()
        if not task_manager:
            print("❌ Failed to initialize TaskManager")
            return
    
    # Execute commands
    if args.command == "status":
        if task_manager:
            cmd_status_enhanced(task_manager, args.task_id)
        else:
            print("❌ TaskManager not available")
    elif args.command == "list":
        if task_manager:
            cmd_list_enhanced(task_manager, args.status, args.phase if hasattr(args, 'phase') else None)
        else:
            print("❌ TaskManager not available")
    elif args.command == "start":
        if task_manager:
            task_manager.cmd_start(args.task_id, enhanced=not args.basic)
        else:
            print("❌ TaskManager not available")
    elif args.command == "commit":
        if task_manager:
            cmd_commit_enhanced(task_manager, args.task_id, args.message)
        else:
            print("❌ TaskManager not available")
    elif args.command == "block":
        if task_manager:
            cmd_block_enhanced(task_manager, args.task_id, args.reason)
        else:
            print("❌ TaskManager not available")
    elif args.command == "phases":
        if task_manager:
            cmd_phases(task_manager)
        else:
            print("❌ TaskManager not available")
    elif args.command == "ui":
        cmd_ui()
    elif args.command == "add-task":
        cmd_add_task(args)
    elif args.command == "add-phase":
        cmd_add_phase(args)

if __name__ == "__main__":
    main()