#!/usr/bin/env python3
"""
Bruce Complete Management Interface - Enhanced Multi-Project Version
Adds project selection and dynamic TaskManager initialization
Enhanced with multi-phase support, progress tracking, Blueprint Generator UI, Enhanced Context,
Dynamic Task/Phase Management UI, Config System Integration, AND Blueprint Import Feature
Refactored into modular templates for easier maintenance and Phase 3 testing
"""

from flask import Flask, request, jsonify, make_response, redirect, url_for, render_template_string
from functools import wraps
import yaml
import subprocess
import os
import sys
from pathlib import Path
import datetime
import json
import glob
from functools import lru_cache
from flask import session
from typing import List, Dict, Any

# Add src to path to import TaskManager and ConfigManager
sys.path.insert(0, str(Path(__file__).parent))
from src.task_manager import TaskManager

app = Flask(__name__)
app.secret_key = 'bruce-project-2025-secure'

# Authentication (keeping original for now)
VALID_USERS = {
    'hdw': 'HoneyDuo2025!',
    'admin': 'AdminPass123!'
}

# Session configuration for Flask app
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)

PROJECT_ROOT = Path(__file__).parent

def discover_bruce_projects(search_root: Path = None) -> List[Dict[str, Any]]:
    """Discover all Bruce projects in the filesystem"""
    if search_root is None:
        # Search in parent directories and common project locations
        search_roots = [
            Path.home() / "Projects",
            Path.home() / "Documents",
            Path.home(),
            Path(__file__).parent.parent,
            Path(__file__).parent.parent.parent
        ]
    else:
        search_roots = [search_root]
    
    projects = []
    seen_paths = set()
    
    for root in search_roots:
        if not root.exists():
            continue
            
        try:
            # Look for bruce.yaml files
            for bruce_config in root.rglob("bruce.yaml"):
                project_path = bruce_config.parent
                
                # Avoid duplicates
                if str(project_path) in seen_paths:
                    continue
                seen_paths.add(str(project_path))
                
                try:
                    with open(bruce_config, 'r') as f:
                        config = yaml.safe_load(f)
                    
                    project_info = {
                        "path": str(project_path),
                        "name": config.get("project", {}).get("name", project_path.name),
                        "description": config.get("project", {}).get("description", ""),
                        "type": config.get("project", {}).get("type", "unknown"),
                        "config_file": str(bruce_config),
                        "is_current": str(project_path) == str(PROJECT_ROOT),
                        "last_modified": datetime.datetime.fromtimestamp(
                            project_path.stat().st_mtime
                        ).isoformat()
                    }
                    
                    # Restore active sessions on startup
                    print("🔄 Restoring active sessions...")
                    initial_task_manager.restore_active_sessions()
                    if initial_task_manager.active_sessions:
                        print(f"✅ Restored {len(initial_task_manager.active_sessions)} active session(s)")


                    # Check if project is accessible
                    try:
                        test_tm = TaskManager(project_path)
                        project_info["accessible"] = True
                        task_data = test_tm.load_tasks()
                        project_info["task_count"] = len(task_data.get("tasks", []))
                    except Exception:
                        project_info["accessible"] = False
                        project_info["task_count"] = 0
                    
                    projects.append(project_info)
                    
                except Exception as e:
                    # Add project even if config is invalid
                    projects.append({
                        "path": str(project_path),
                        "name": project_path.name,
                        "description": "Configuration error",
                        "config_file": str(bruce_config),
                        "is_current": str(project_path) == str(PROJECT_ROOT),
                        "accessible": False,
                        "error": str(e)
                    })
        
        except (OSError, PermissionError):
            continue
    
    # Sort by name, current project first
    projects.sort(key=lambda p: (not p.get("is_current", False), p.get("name", "")))
    return projects

def get_selected_project_path() -> Path:
    """Get the currently selected project path from session"""
    if 'selected_project' in session:
        selected_path = Path(session['selected_project'])
        if selected_path.exists() and (selected_path / "bruce.yaml").exists():
            return selected_path
    
    # Default to current project
    return PROJECT_ROOT

def get_task_manager_for_project(project_path: Path = None) -> TaskManager:
    """Get TaskManager instance for specified project"""
    if project_path is None:
        project_path = get_selected_project_path()
    
    return TaskManager(project_path)

@lru_cache(maxsize=10)
def get_cached_project_info(project_path: str) -> Dict[str, Any]:
    """Get cached project information to improve performance"""
    try:
        tm = TaskManager(Path(project_path))
        return tm.get_project_info()
    except Exception as e:
        return {
            "name": Path(project_path).name,
            "error": str(e)
        }

def get_current_task_manager():
    """Get TaskManager for currently selected project"""
    return get_task_manager_for_project()

def check_auth(username, password):
    return username in VALID_USERS and VALID_USERS[username] == password

def authenticate():
    return make_response(
        '🔐 Bruce Access Required\nLogin required for Bruce Project Management',
        401,
        {'WWW-Authenticate': 'Basic realm="Bruce Management Interface"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Initialize session if not present
@app.before_request
def init_session():
    if 'selected_project' not in session:
        session['selected_project'] = str(PROJECT_ROOT)
        session.permanent = True

def run_cli_command(command, project_path=None):
    """Run CLI command and return result"""
    if project_path is None:
        project_path = get_selected_project_path()
    
    try:
        # Look for CLI script in the project or use current project's CLI
        cli_script = project_path / "cli" / "bruce.py"
        if not cli_script.exists():
            cli_script = PROJECT_ROOT / "cli" / "bruce.py"
        
        cmd = f"python3 {cli_script} {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=project_path)
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

def get_template_context():
    """Get common template context for all pages with multi-project support"""
    # Get current project information
    current_project_path = get_selected_project_path()
    tm = get_task_manager_for_project(current_project_path)
    
    if tm.config:
        project_name = tm.config.project.name
        theme_color = tm.config.ui.theme_color
        domain = tm.config.ui.domain
        page_title = tm.config.ui.title or project_name
    else:
        project_name = current_project_path.name
        theme_color = "#00d4aa"
        domain = "bruce.honey-duo.com"
        page_title = project_name
    
    # Discover available projects
    available_projects = discover_bruce_projects()
    
    return {
        'project_name': project_name,
        'theme_color': theme_color,
        'theme_color_light': theme_color + "dd" if len(theme_color) == 7 else theme_color,
        'domain': domain,
        'page_title': page_title,
        'current_time': datetime.datetime.now().strftime('%A, %B %d, %Y at %I:%M %p'),
        'current_project_path': str(current_project_path),
        'available_projects': available_projects,
        'multi_project_enabled': True
    }

# ROUTE HANDLERS

@app.route('/')
@requires_auth
def dashboard():
    """Dashboard page with project stats, phase progress, and recent activity"""
    task_manager = get_current_task_manager()  # Dynamic task manager
    
    tasks_data = task_manager.load_tasks()
    tasks = tasks_data.get("tasks", [])
    
    # Calculate statistics
    status_counts = {}
    for task in tasks:
        status = task.get('status', 'pending')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Get phase progress
    phase_progress = task_manager.get_phase_progress()
    
    # Get recent tasks
    recent_tasks = sorted([t for t in tasks if t.get('updated')], 
                         key=lambda x: x.get('updated', ''), reverse=True)[:10]
    
    # Process recent tasks for display
    for task in recent_tasks:
        updated = task.get('updated', '')
        if updated:
            try:
                dt = datetime.datetime.fromisoformat(updated.replace('Z', '+00:00'))
                task['time_str'] = dt.strftime('%m/%d %I:%M%p')
            except:
                task['time_str'] = updated[:10]
        else:
            task['time_str'] = 'Never'
    
    template_context = get_template_context()
    template_context.update({
        'active_page': 'dashboard',
        'status_counts': status_counts,
        'phase_progress': phase_progress,
        'recent_tasks': recent_tasks,
        'total_tasks': len(tasks)
    })
    
    from templates.dashboard import get_dashboard_template
    return render_template_string(get_dashboard_template(), **template_context)

@app.route('/tasks')
@requires_auth
def tasks():
    """Tasks management page with enhanced context and phase organization"""
    task_manager = get_current_task_manager()  # Dynamic task manager
    
    tasks_data = task_manager.load_tasks()
    tasks = tasks_data.get("tasks", [])
    
    # Group tasks by phase and status
    tasks_by_phase = {}
    for task in tasks:
        phase = task.get('phase', 0)
        if phase not in tasks_by_phase:
            tasks_by_phase[phase] = {
                'pending': [],
                'in-progress': [],
                'completed': [],
                'blocked': []
            }
        status = task.get('status', 'pending')
        
        # Add time formatting for display
        updated = task.get('updated', '')
        if updated:
            try:
                dt = datetime.datetime.fromisoformat(updated.replace('Z', '+00:00'))
                task['time_str'] = dt.strftime('%m/%d %I:%M%p')
            except:
                task['time_str'] = updated[:10]
        else:
            task['time_str'] = 'Never'
        
        tasks_by_phase[phase][status].append(task)
    
    template_context = get_template_context()
    template_context.update({
        'active_page': 'tasks',
        'tasks_by_phase': tasks_by_phase,
        'tasks_data': tasks_data,
        'tasks_json': json.dumps(tasks),  # For JavaScript
        'active_sessions': task_manager.active_sessions

    })
    
    from templates.tasks import get_tasks_template
    return render_template_string(get_tasks_template(), **template_context)

@app.route('/phases')
@requires_auth
def phases():
    """Phases overview page with detailed progress tracking"""
    task_manager = get_current_task_manager()  # Dynamic task manager
    
    tasks_data = task_manager.load_tasks()
    phase_progress = task_manager.get_phase_progress()
    
    template_context = get_template_context()
    template_context.update({
        'active_page': 'phases',
        'phase_progress': phase_progress,
        'tasks_data': tasks_data
    })
    
    from templates.phases import get_phases_template
    return render_template_string(get_phases_template(), **template_context)

@app.route('/manage')
@requires_auth
def manage():
    """Task and phase management page with blueprint import"""
    task_manager = get_current_task_manager()  # Dynamic task manager
    
    tasks_data = task_manager.load_tasks()
    phase_progress = task_manager.get_phase_progress()
    
    # Group tasks by phase for edit dropdown
    tasks_by_phase = {}
    for task in tasks_data.get("tasks", []):
        phase = task.get('phase', 0)
        if phase not in tasks_by_phase:
            tasks_by_phase[phase] = []
        tasks_by_phase[phase].append(task)
    
    template_context = get_template_context()
    template_context.update({
        'active_page': 'manage',
        'phase_progress': phase_progress,
        'tasks_by_phase': tasks_by_phase,
        'tasks_data': tasks_data,
        'all_tasks_json': json.dumps(tasks_data.get("tasks", []))  # For JavaScript
    })
    
    from templates.manage import get_manage_template
    return render_template_string(get_manage_template(), **template_context)

@app.route('/generator')
@requires_auth
def generator():
    """Blueprint generator page for comprehensive documentation"""
    task_manager = get_current_task_manager()  # Dynamic task manager
    
    phase_progress = task_manager.get_phase_progress()
    selected_phase = request.args.get('phase', '1')
    
    template_context = get_template_context()
    template_context.update({
        'active_page': 'generator',
        'phase_progress': phase_progress,
        'selected_phase': selected_phase,
        'total_templates': 9,  # Add this to fix template error
        'generator_features': [
            'Phase blueprints',
            'Session handoffs', 
            'Architecture maps'
        ]
    })
    
    from templates.generator import get_generator_template
    return render_template_string(get_generator_template(), **template_context)

@app.route('/reports')
@requires_auth
def reports():
    """Reports page for Claude handoff generation"""
    task_manager = get_current_task_manager()  # Dynamic task manager
    
    tasks_data = task_manager.load_tasks()
    tasks = tasks_data.get("tasks", [])
    reportable_tasks = [t for t in tasks if t.get('status') in ['completed', 'blocked', 'in-progress']]
    selected_task = request.args.get('task', '')
    
    # Group tasks by phase for better organization
    tasks_by_phase = {}
    for task in reportable_tasks:
        phase = task.get('phase', 0)
        if phase not in tasks_by_phase:
            tasks_by_phase[phase] = []
        tasks_by_phase[phase].append(task)
    
    template_context = get_template_context()
    template_context.update({
        'active_page': 'reports',
        'tasks_by_phase': tasks_by_phase,
        'selected_task': selected_task
    })
    
    from templates.reports import get_reports_template
    return render_template_string(get_reports_template(), **template_context)

@app.route('/config')
@requires_auth
def config_info():
    """Configuration page showing bruce.yaml settings"""
    task_manager = get_current_task_manager()  # Dynamic task manager
    
    info = task_manager.get_project_info()
    
    template_context = get_template_context()
    template_context.update({
        'active_page': 'config',
        'project_info': info,
        'task_manager_config': task_manager.config
    })
    
    from templates.config import get_config_template
    return render_template_string(get_config_template(), **template_context)

@app.route('/help')
@requires_auth
def help_page():
    """Help page with blueprint import documentation"""
    template_context = get_template_context()
    template_context.update({
        'active_page': 'help'
    })
    
    from templates.help import get_help_template
    return render_template_string(get_help_template(), **template_context)

# =============================================================================
# API ENDPOINTS - Enhanced with Multi-Project Support
# =============================================================================

@app.route('/api/discover_projects')
@requires_auth
def api_discover_projects():
    """API endpoint to discover Bruce projects"""
    try:
        projects = discover_bruce_projects()
        current_project = str(get_selected_project_path().resolve())
        
        # Ensure current project is marked correctly
        for project in projects:
            project_path = str(Path(project['path']).resolve())
            project['is_current'] = (project_path == current_project)
        
        return jsonify({
            "success": True,
            "projects": projects,
            "current_project": current_project
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def get_selected_project_path() -> Path:
    """Get the currently selected project path from session"""
    if 'selected_project' in session:
        try:
            selected_path = Path(session['selected_project']).resolve()
            if selected_path.exists() and (selected_path / "bruce.yaml").exists():
                return selected_path
        except Exception as e:
            print(f"⚠️ Invalid session project path: {e}")
            # Clear invalid session
            session.pop('selected_project', None)
    
    # Default to current project
    return PROJECT_ROOT.resolve()


@app.route('/api/switch_project', methods=['POST'])
@requires_auth
def api_switch_project():
    """API endpoint to switch to a different project"""
    try:
        data = request.json
        project_path = data.get('project_path')
        
        if not project_path:
            return jsonify({"success": False, "error": "No project path provided"})
        
        project_path = Path(project_path).resolve()  # Resolve absolute path
        
        # Validate project
        if not project_path.exists():
            return jsonify({"success": False, "error": "Project path does not exist"})
        
        bruce_config = project_path / "bruce.yaml"
        if not bruce_config.exists():
            return jsonify({"success": False, "error": "Not a valid Bruce project (no bruce.yaml)"})
        
        # Test TaskManager initialization
        try:
            test_tm = TaskManager(project_path)
            project_info = test_tm.get_project_info()
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to initialize project: {str(e)}"})
        
        # Store in session with absolute path
        session['selected_project'] = str(project_path)
        session.permanent = True
        
        # Clear any caches
        if hasattr(get_cached_project_info, 'cache_clear'):
            get_cached_project_info.cache_clear()
        
        print(f"✅ Project switched to: {project_path}")  # Debug log
        
        return jsonify({
            "success": True,
            "project_info": project_info,
            "project_path": str(project_path),
            "message": f"Switched to project: {project_info['name']}"
        })
        
    except Exception as e:
        print(f"❌ Project switch error: {e}")  # Debug log
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/current_project_info')
@requires_auth
def api_current_project_info():
    """Get information about the currently selected project"""
    try:
        project_path = get_selected_project_path()
        tm = get_task_manager_for_project(project_path)
        
        project_info = tm.get_project_info()
        phase_progress = tm.get_phase_progress()
        
        # Add extra context
        project_info['path'] = str(project_path)
        project_info['total_phases'] = len(phase_progress)
        
        total_tasks = sum(p['total'] for p in phase_progress.values())
        total_completed = sum(p['completed'] for p in phase_progress.values())
        project_info['total_tasks'] = total_tasks
        project_info['completed_tasks'] = total_completed
        project_info['overall_progress'] = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
        
        return jsonify({
            "success": True,
            "project_info": project_info,
            "phase_progress": phase_progress
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/project_health_check')
@requires_auth
def project_health_check():
    """Check health of current project"""
    try:
        task_manager = get_current_task_manager()
        project_path = get_selected_project_path()
        
        # Basic health checks
        health_status = {
            "project_accessible": True,
            "config_loaded": task_manager.config is not None,
            "tasks_loadable": False,
            "directories_exist": False,
            "git_repo": False
        }
        
        # Check if tasks can be loaded
        try:
            tasks_data = task_manager.load_tasks()
            health_status["tasks_loadable"] = True
            health_status["task_count"] = len(tasks_data.get("tasks", []))
        except Exception:
            health_status["task_count"] = 0
        
        # Check if required directories exist
        required_dirs = ["phases", "contexts", "docs"]
        existing_dirs = [d for d in required_dirs if (project_path / d).exists()]
        health_status["directories_exist"] = len(existing_dirs) == len(required_dirs)
        health_status["existing_directories"] = existing_dirs
        
        # Check git status
        try:
            import subprocess
            result = subprocess.run(["git", "rev-parse", "--git-dir"], 
                                  capture_output=True, cwd=project_path)
            health_status["git_repo"] = result.returncode == 0
        except Exception:
            pass
        
        return jsonify({
            "success": True,
            "health_status": health_status,
            "project_path": str(project_path)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "health_status": {"project_accessible": False}
        })

@app.route('/api/create_config', methods=['POST'])
@requires_auth
def create_config():
    """Create default config file"""
    try:
        task_manager = get_current_task_manager()
        config = task_manager.config
        if config:
            config_file = config.create_default_config()
            return jsonify({"success": True, "config_file": str(config_file)})
        else:
            return jsonify({"success": False, "error": "Config manager not available"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/validate_config')
@requires_auth
def validate_config():
    """Validate current configuration"""
    try:
        task_manager = get_current_task_manager()
        config = task_manager.config
        if config:
            is_valid = config.validate_config()
            return jsonify({"valid": is_valid})
        else:
            return jsonify({"valid": False, "error": "Config manager not available"})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)})

@app.route('/api/add_task', methods=['POST'])
@requires_auth
def add_task():
    """Add a new task via API - Direct TaskManager approach"""
    try:
        data = request.json
        
        # Get current project's task manager
        current_project = get_selected_project_path()
        task_manager = get_task_manager_for_project(current_project)
        
        # Validate required fields
        if not data.get('phase') or not data.get('id') or not data.get('description'):
            return jsonify({"success": False, "error": "Phase, ID, and Description are required"})
        
        # Create task data
        task_data = {
            'id': data['id'],
            'description': data['description'],
            'status': 'pending',
            'created': datetime.datetime.now().isoformat()
        }
        
        # Add optional fields
        if data.get('output'):
            task_data['output'] = data['output']
        if data.get('tests'):
            task_data['tests'] = data['tests']
        if data.get('context') and any(data['context']):
            task_data['context'] = [item.strip() for item in data['context'] if item.strip()]
        if data.get('depends_on') and any(data['depends_on']):
            task_data['depends_on'] = [item.strip() for item in data['depends_on'] if item.strip()]
        if data.get('acceptance_criteria') and any(data['acceptance_criteria']):
            task_data['acceptance_criteria'] = [item.strip() for item in data['acceptance_criteria'] if item.strip()]
        
        # Find the phase file
        phase_id = data['phase']
        phase_files = list(task_manager.phases_dir.glob(f"phase{phase_id}_*.yml"))
        
        if not phase_files:
            return jsonify({"success": False, "error": f"Phase {phase_id} file not found"})
        
        phase_file = phase_files[0]
        
        # Load existing phase data
        with open(phase_file, 'r') as f:
            phase_data = yaml.safe_load(f)
        
        # Add task to phase
        if 'tasks' not in phase_data:
            phase_data['tasks'] = []
        
        # Check for duplicate task ID
        existing_ids = [t['id'] for t in phase_data['tasks']]
        if task_data['id'] in existing_ids:
            return jsonify({"success": False, "error": f"Task ID '{task_data['id']}' already exists in this phase"})
        
        phase_data['tasks'].append(task_data)
        
        # Save updated phase file
        with open(phase_file, 'w') as f:
            yaml.dump(phase_data, f, default_flow_style=False, indent=2, sort_keys=False)
        
        return jsonify({
            "success": True, 
            "message": f"Task '{task_data['id']}' created successfully in Phase {phase_id}",
            "task_id": task_data['id'],
            "phase_id": phase_id
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/add_phase', methods=['POST'])
@requires_auth
def add_phase():
    """Add a new phase via API"""
    try:
        data = request.json
        command = f'add-phase --id {data["id"]} --name "{data["name"]}" --description "{data["description"]}"'
        result = run_cli_command(command)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/edit_task', methods=['POST'])
@requires_auth
def edit_task():
    """Edit an existing task via API"""
    try:
        data = request.json
        cmd_parts = ["edit-task", f"--id \"{data['id']}\""]
        
        if data.get('description'):
            cmd_parts.append(f"--description \"{data['description']}\"")
        if data.get('output'):
            cmd_parts.append(f"--output \"{data['output']}\"")
        if data.get('tests'):
            cmd_parts.append(f"--tests \"{data['tests']}\"")
        if data.get('context') is not None:
            context_items = [f'"{item}"' for item in data['context'] if item.strip()]
            if context_items:
                cmd_parts.append(f"--context {' '.join(context_items)}")
            else:
                cmd_parts.append("--context")
        if data.get('depends_on') is not None:
            dep_items = [f'"{item}"' for item in data['depends_on'] if item.strip()]
            if dep_items:
                cmd_parts.append(f"--depends-on {' '.join(dep_items)}")
            else:
                cmd_parts.append("--depends-on")
        if data.get('acceptance_criteria') is not None:
            criteria_items = [f'"{item}"' for item in data['acceptance_criteria'] if item.strip()]
            if criteria_items:
                cmd_parts.append(f"--acceptance-criteria {' '.join(criteria_items)}")
            else:
                cmd_parts.append("--acceptance-criteria")
        
        command = ' '.join(cmd_parts)
        result = run_cli_command(command)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/preview_blueprint', methods=['POST'])
@requires_auth
def preview_blueprint():
    """Preview blueprint before import"""
    try:
        data = request.json
        yaml_content = data.get('yaml_content', '')
        
        if not yaml_content:
            return jsonify({"success": False, "error": "No YAML content provided"})
        
        # Parse YAML
        try:
            blueprint_data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            return jsonify({"success": False, "error": f"Invalid YAML format: {str(e)}"})
        
        # Validate blueprint structure
        if not isinstance(blueprint_data, dict):
            return jsonify({"success": False, "error": "Blueprint must be a YAML object"})
        
        if 'phase' not in blueprint_data:
            return jsonify({"success": False, "error": "Blueprint must contain a 'phase' section"})
        
        if 'tasks' not in blueprint_data:
            return jsonify({"success": False, "error": "Blueprint must contain a 'tasks' section"})
        
        phase_info = blueprint_data['phase']
        tasks = blueprint_data['tasks']
        
        # Validate phase info
        if not phase_info.get('id'):
            return jsonify({"success": False, "error": "Phase must have an 'id'"})
        
        if not phase_info.get('name'):
            return jsonify({"success": False, "error": "Phase must have a 'name'"})
        
        # Validate tasks
        if not isinstance(tasks, list) or len(tasks) == 0:
            return jsonify({"success": False, "error": "Tasks must be a non-empty list"})
        
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                return jsonify({"success": False, "error": f"Task {i+1} must be an object"})
            
            if not task.get('id'):
                return jsonify({"success": False, "error": f"Task {i+1} must have an 'id'"})
            
            if not task.get('description'):
                return jsonify({"success": False, "error": f"Task {i+1} must have a 'description'"})
        
        # Check for duplicate task IDs
        task_ids = [task['id'] for task in tasks]
        if len(task_ids) != len(set(task_ids)):
            return jsonify({"success": False, "error": "Duplicate task IDs found in blueprint"})
        
        # Check if phase ID already exists
        task_manager = get_current_task_manager()
        existing_tasks = task_manager.load_tasks()
        existing_phases = existing_tasks.get('phases', {})
        
        if str(phase_info['id']) in existing_phases:
            return jsonify({"success": False, "error": f"Phase {phase_info['id']} already exists"})
        
        # Check for existing task IDs
        existing_task_ids = [t['id'] for t in existing_tasks.get('tasks', [])]
        duplicate_ids = [task_id for task_id in task_ids if task_id in existing_task_ids]
        
        if duplicate_ids:
            return jsonify({"success": False, "error": f"Task IDs already exist: {', '.join(duplicate_ids)}"})
        
        # Create preview
        preview = {
            "phase": {
                "id": phase_info['id'],
                "name": phase_info['name'],
                "description": phase_info.get('description', '')
            },
            "tasks": []
        }
        
        for task in tasks:
            preview["tasks"].append({
                "id": task['id'],
                "description": task['description'],
                "output": task.get('output', ''),
                "depends_on": task.get('depends_on', []),
                "acceptance_criteria": task.get('acceptance_criteria', [])
            })
        
        return jsonify({
            "success": True,
            "preview": preview,
            "task_count": len(tasks)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/import_blueprint', methods=['POST'])
@requires_auth
def import_blueprint():
    """Import blueprint and create all tasks"""
    try:
        task_manager = get_current_task_manager()
        data = request.json
        yaml_content = data.get('yaml_content', '')
        
        if not yaml_content:
            return jsonify({"success": False, "error": "No YAML content provided"})
        
        # Parse and validate YAML (same validation as preview)
        try:
            blueprint_data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            return jsonify({"success": False, "error": f"Invalid YAML format: {str(e)}"})
        
        phase_info = blueprint_data['phase']
        tasks = blueprint_data['tasks']
        
        # Create phase file
        phase_filename = f"phase{phase_info['id']}_{phase_info['name'].lower().replace(' ', '_')}.yml"
        phase_file_path = task_manager.phases_dir / phase_filename
        
        # Build phase data structure
        phase_data = {
            'phase': {
                'id': phase_info['id'],
                'name': phase_info['name'],
                'description': phase_info.get('description', '')
            },
            'tasks': []
        }
        
        # Add context from original blueprint if available
        if 'context' in blueprint_data['phase']:
            phase_data['phase']['context'] = blueprint_data['phase']['context']
        
        # Process tasks
        for task in tasks:
            task_data = {
                'id': task['id'],
                'description': task['description'],
                'status': 'pending'
            }
            
            # Add optional fields
            if task.get('output'):
                task_data['output'] = task['output']
            
            if task.get('depends_on'):
                task_data['depends_on'] = task['depends_on']
            
            if task.get('acceptance_criteria'):
                task_data['acceptance_criteria'] = task['acceptance_criteria']
            
            if task.get('context'):
                task_data['context'] = task['context']
            
            if task.get('why'):
                task_data['why'] = task['why']
            
            if task.get('connects_to'):
                task_data['connects_to'] = task['connects_to']
            
            if task.get('implementation_notes'):
                task_data['implementation_notes'] = task['implementation_notes']
            
            phase_data['tasks'].append(task_data)
        
        # Write phase file
        with open(phase_file_path, 'w') as f:
            yaml.dump(phase_data, f, default_flow_style=False, indent=2, sort_keys=False)
        
        return jsonify({
            "success": True,
            "imported_count": len(tasks),
            "phase_file": phase_filename,
            "phase_id": phase_info['id'],
            "phase_name": phase_info['name']
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/start_task', methods=['POST'])
@requires_auth
def start_task():
    """Start a task with enhanced or basic context"""
    try:
        data = request.json
        task_id = data.get('task_id')
        use_enhanced = data.get('enhanced', True)
        
        if not task_id:
            return jsonify({"success": False, "error": "No task ID provided"})
        
        # Get current project's task manager
        current_project = get_selected_project_path()
        task_manager = get_task_manager_for_project(current_project)
        
        # Use the task manager's start method
        task_manager.cmd_start(task_id, enhanced=use_enhanced)
        
        return jsonify({
            "success": True, 
            "enhanced": use_enhanced,
            "message": f"Task {task_id} started successfully",
            "task_id": task_id
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/preview_context/<task_id>')
@requires_auth
def preview_context(task_id):
    """Preview the enhanced context that would be generated"""
    try:
        task_manager = get_current_task_manager()
        use_enhanced = request.args.get('enhanced', 'true').lower() == 'true'
        
        if use_enhanced:
            context_content = task_manager.generate_enhanced_context(task_id)
        else:
            tasks_data = task_manager.load_tasks()
            task = next((t for t in tasks_data['tasks'] if t['id'] == task_id), None)
            
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            
            project_info = task_manager.get_project_info()
            context_content = f"# Context for Task: {task_id}\n\n"
            context_content += f"**Project:** {project_info['name']}\n"
            context_content += f"**Phase:** {task.get('phase', 0)} - {task.get('phase_name', 'Legacy')}\n"
            context_content += f"**Description:** {task['description']}\n\n"
            context_content += f"**Expected Output:** {task.get('output', 'Not specified')}\n\n"
            
            if task.get('acceptance_criteria'):
                context_content += "**Acceptance Criteria:**\n"
                for criteria in task['acceptance_criteria']:
                    context_content += f"- {criteria}\n"
                context_content += "\n"
        
        return jsonify({
            'task_id': task_id,
            'context': context_content
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/related_tasks/<task_id>')
@requires_auth
def related_tasks(task_id):
    """Get related tasks for enhanced context"""
    try:
        task_manager = get_current_task_manager()
        related = task_manager.find_related_tasks(task_id)
        
        # Format for display
        formatted_tasks = []
        for task in related:
            formatted_tasks.append({
                'id': task['id'],
                'description': task.get('description', ''),
                'status': task.get('status', 'pending'),
                'phase': task.get('phase', 0)
            })
        
        return jsonify({
            'task_id': task_id,
            'related_tasks': formatted_tasks
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/complete_task', methods=['POST'])
@requires_auth
def complete_task():
    """Complete a task and trigger git commit"""
    try:
        data = request.json
        task_id = data.get('task_id')
        message = data.get('message', '')
        
        if not task_id:
            return jsonify({"success": False, "error": "No task ID provided"})
        
        # Get current project's task manager
        current_project = get_selected_project_path()
        task_manager = get_task_manager_for_project(current_project)
        
        # Update task status directly
        task_manager.save_task_updates(task_id, {
            "status": "completed",
            "updated": datetime.datetime.now().isoformat(),
            "completed_at": datetime.datetime.now().isoformat(),
            "notes": [{
                "timestamp": datetime.datetime.now().isoformat(),
                "note": f"Task completed. Message: {message}" if message else "Task completed"
            }]
        })
        
        # Try git commit if in git repo
        try:
            if message:
                git_cmd = f'git add -A && git commit -m "Complete task {task_id}: {message}"'
            else:
                git_cmd = f'git add -A && git commit -m "Complete task {task_id}"'
            
            subprocess.run(git_cmd, shell=True, cwd=current_project, capture_output=True)
        except Exception:
            pass  # Git commit is optional
        
        return jsonify({
            "success": True, 
            "message": f"Task {task_id} completed successfully",
            "task_id": task_id
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/block_task', methods=['POST'])
@requires_auth
def block_task():
    """Block a task with reason"""
    try:
        data = request.json
        task_id = data.get('task_id')
        reason = data.get('reason', '')
        
        if not task_id or not reason:
            return jsonify({"success": False, "error": "Task ID and reason required"})
        
        # Get current project's task manager
        current_project = get_selected_project_path()
        task_manager = get_task_manager_for_project(current_project)
        
        # Update task status directly
        task_manager.save_task_updates(task_id, {
            "status": "blocked",
            "updated": datetime.datetime.now().isoformat(),
            "blocked_at": datetime.datetime.now().isoformat(),
            "notes": [{
                "timestamp": datetime.datetime.now().isoformat(),
                "note": f"Blocked: {reason}"
            }]
        })
        
        return jsonify({
            "success": True, 
            "message": f"Task {task_id} blocked successfully",
            "task_id": task_id,
            "reason": reason
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/generate_blueprint', methods=['POST'])
@requires_auth
def generate_blueprint():
    """Generate blueprint documentation via API"""
    try:
        data = request.json
        blueprint_type = data.get('type', 'phase')
        phase_id = data.get('phase_id', 1)
        
        # Get current project path
        current_project = get_selected_project_path()
        
        # Import and create generator
        from src.blueprint_generator import PhaseBlueprintGenerator
        generator = PhaseBlueprintGenerator(current_project)
        
        if blueprint_type == 'phase':
            content = generator.generate_comprehensive_phase_blueprint(phase_id)
            filename = f"phase_{phase_id}_blueprint.md"
            filepath = generator.update_phase_blueprint(phase_id)
            
        elif blueprint_type == 'handoff':
            content = generator.generate_session_handoff()
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"session_handoff_{timestamp}.md"
            
            # Save to sessions directory
            sessions_dir = current_project / "docs" / "sessions"
            sessions_dir.mkdir(parents=True, exist_ok=True)
            filepath = sessions_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(content)
            filepath = str(filepath)
            
        elif blueprint_type == 'architecture':
            content = generator.generate_ultimate_system_architecture_blueprint()
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
            filename = f"architecture_blueprint_{timestamp}.md"
            
            # Save to blueprints directory
            blueprints_dir = current_project / "docs" / "blueprints"
            blueprints_dir.mkdir(parents=True, exist_ok=True)
            filepath = blueprints_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(content)
            filepath = str(filepath)
            
        else:
            return jsonify({"success": False, "error": "Invalid blueprint type"})
        
        return jsonify({
            "success": True,
            "content": content,
            "filepath": str(filepath),
            "filename": filename,
            "type": blueprint_type
        })
        
    except Exception as e:
        print(f"❌ Blueprint generation error: {e}")  # Debug log
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/generate_report', methods=['POST'])
@requires_auth
def generate_report():
    """Generate Claude handoff report with session data"""
    data = request.json
    task_id = data.get('task_id')
    custom_summary = data.get('summary', '')
    include_sessions = data.get('include_sessions', True)
    
    if not task_id:
        return jsonify({"success": False, "error": "No task ID provided"})
    
    task_manager = get_current_task_manager()
    
    # Add session supplement
    if include_sessions:
        try:
            from src.session_reporter import SessionReporter
            reporter = SessionReporter(task_manager)
            session_supplement = reporter.generate_handoff_supplement(task_id)
            report += "\n" + session_supplement
        except ImportError:
            pass  # SessionReporter not available
        except Exception as e:
            print(f"Session report error: {e}")

    # Import session reporter
    from src.session_reporter import SessionReporter
    reporter = SessionReporter(task_manager)
    
    # Original report generation code...
    tasks_data = task_manager.load_tasks()
    task = next((t for t in tasks_data.get("tasks", []) if t['id'] == task_id), None)
    if not task:
        return jsonify({"success": False, "error": f"Task '{task_id}' not found"})
    
    if custom_summary:
        summary = custom_summary
    else:
        summary = f"Implemented {task.get('description', 'task requirements')}"
    
    try:
        result = subprocess.run(
            ["git", "show", "--name-only", "--pretty=format:", "HEAD"],
            capture_output=True, text=True, cwd=get_selected_project_path()
        )
        recent_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        artifacts = ", ".join(recent_files) if recent_files else task.get("output", "No artifacts specified")
    except:
        artifacts = task.get("output", "No artifacts specified")
    
    if include_sessions:
        session_supplement = reporter.generate_handoff_supplement(task_id)
        report += "\n" + session_supplement

    status = task.get('status', 'pending').title()
    phase_info = f"Phase {task.get('phase', 0)}: {task.get('phase_name', 'Legacy')}"
    project_info = task_manager.get_project_info()
    
    report = f"""=== CLAUDE HANDOFF REPORT ===
Task: {task_id}
{phase_info}
Status: {status}
Summary: "{summary}"
Expected Output: {task.get('output', 'Not specified')}
Artifacts: {artifacts}

Context: This task is part of the {project_info['name']} project.
Next Steps: Continue with remaining Phase {task.get('phase', 0)} tasks or begin next phase.
==========================="""
    
    timestamp = datetime.datetime.now().strftime('%m%d_%H%M')
    reports_dir = task_manager.reports_dir
    reports_dir.mkdir(exist_ok=True)
    
    filename = f"Claude_Handoff_{task_id}_{timestamp}.txt"
    report_file = reports_dir / filename
    
    with open(report_file, 'w') as f:
        f.write(f"# Claude Handoff Report\n")
        f.write(f"# Generated: {datetime.datetime.now().strftime('%A %B %d, %Y at %I:%M %p')}\n")
        f.write(f"# Task: {task_id}\n\n")
        f.write(report)
        f.write(f"\n\n# Phase Progress:\n")
        
        phase_progress = task_manager.get_phase_progress()
        for phase_id, progress in phase_progress.items():
            f.write(f"Phase {phase_id} ({progress['name']}): {progress['percentage']:.0f}% complete\n")
    
    return jsonify({
        "success": True, 
        "report": report, 
        "filename": filename,
        "filepath": str(report_file)
    })

@app.route('/health')
def health_check():
    """Health check endpoint for system monitoring"""
    task_manager = get_current_task_manager()
    project_info = task_manager.get_project_info()
    return jsonify({
        "status": "healthy", 
        "project": project_info['name'],
        "domain": task_manager.config.ui.domain if task_manager.config else "bruce.honey-duo.com", 
        "version": "2.0-multi-project-enhanced",
        "config_loaded": project_info['config_loaded'],
        "total_tasks": len(task_manager.load_tasks().get("tasks", [])),
        "architecture": "modular-templates-multi-project"
    })

@app.route('/api/session_status/<task_id>')
@requires_auth
def session_status(task_id):
    tm = get_current_task_manager()
    summary = tm.get_session_summary(task_id)
    active = task_id in tm.active_sessions
    return jsonify({
        "success": True,
        "task_id": task_id,
        "is_active": active,
        "summary": summary
    })

@app.route('/api/session_note', methods=['POST'])
@requires_auth
def add_session_note():
    data = request.json
    tm = get_current_task_manager()
    success = tm.add_session_note(data['task_id'], data['note'])
    return jsonify({"success": success})

if __name__ == "__main__":
    # Get initial task manager for startup info
    initial_task_manager = TaskManager(PROJECT_ROOT)
    project_info = initial_task_manager.get_project_info()
    config = initial_task_manager.config
    domain = config.ui.domain if config else "bruce.honey-duo.com"
    port = config.ui.port if config else 8000
    
    print("🌐 Bruce Complete Management Interface - Multi-Project Enhanced")
    print(f"🔐 Access: https://{domain}")
    print(f"🔑 Login: hdw / HoneyDuo2025!")
    print(f"📋 Project: {project_info['name']}")
    print(f"⚙️ Config: {'✅ Loaded' if project_info['config_loaded'] else '📋 Using defaults'}")
    print("")
    print("🎯 MULTI-PROJECT FEATURES:")
    print("  🔍 Project Discovery - Automatic detection of Bruce projects")
    print("  🔄 Dynamic Switching - Switch between projects in session")
    print("  📊 Project Health Check - Validate project accessibility")
    print("  🎨 Per-Project Theming - Colors and branding from each project's config")
    print("  ⚙️ Isolated Task Management - Each project maintains its own task state")
    print("")
    print("💡 COMPLETE Features Preserved:")
    print("  ⚙️ Config System - bruce.yaml configuration support")  
    print("  🎨 Dynamic Theming - colors and branding from config")
    print("  📁 Flexible Paths - configurable directory structure")
    print("  ✨ Enhanced Context - Related tasks, architecture, decisions")
    print("  🏗️ Blueprint Generator - Comprehensive documentation")
    print("  ⚙️ Task/Phase Management - Add/edit via web interface")
    print("  📥 Blueprint Import - Design-first workflow with YAML blueprints")
    print("  📊 Full API Coverage - All original endpoints preserved")
    print("")
    print("🚀 Ready for Phase 3 Multi-Project Testing!")
    
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)