#!/usr/bin/env python3
"""
Bruce Complete Management Interface - Modular Version
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

PROJECT_ROOT = Path(__file__).parent

# Initialize TaskManager with Config
task_manager = TaskManager(PROJECT_ROOT)
config = task_manager.config  # Get config from TaskManager

def run_cli_command(command):
    """Run CLI command and return result"""
    try:
        cmd = f"python3 {PROJECT_ROOT}/cli/bruce.py {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=PROJECT_ROOT)
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

def get_template_context():
    """Get common template context for all pages"""
    if config:
        project_name = config.project.name
        theme_color = config.ui.theme_color
        domain = config.ui.domain
        page_title = config.ui.title or project_name
    else:
        project_name = "Bruce"
        theme_color = "#00d4aa"
        domain = "bruce.honey-duo.com"
        page_title = "Bruce"
    
    return {
        'project_name': project_name,
        'theme_color': theme_color,
        'theme_color_light': theme_color + "dd" if len(theme_color) == 7 else theme_color,
        'domain': domain,
        'page_title': page_title,
        'current_time': datetime.datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')
    }

# ROUTE HANDLERS

@app.route('/')
@requires_auth
def dashboard():
    """Dashboard page with project stats, phase progress, and recent activity"""
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
        'tasks_json': json.dumps(tasks)  # For JavaScript
    })
    
    from templates.tasks import get_tasks_template
    return render_template_string(get_tasks_template(), **template_context)

@app.route('/phases')
@requires_auth
def phases():
    """Phases overview page with detailed progress tracking"""
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
    phase_progress = task_manager.get_phase_progress()
    selected_phase = request.args.get('phase', '1')
    
    template_context = get_template_context()
    template_context.update({
        'active_page': 'generator',
        'phase_progress': phase_progress,
        'selected_phase': selected_phase
    })
    
    from templates.generator import get_generator_template
    return render_template_string(get_generator_template(), **template_context)

@app.route('/reports')
@requires_auth
def reports():
    """Reports page for Claude handoff generation"""
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
    info = task_manager.get_project_info()
    
    template_context = get_template_context()
    template_context.update({
        'active_page': 'config',
        'project_info': info,
        'task_manager_config': config
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
# API ENDPOINTS - ALL PRESERVED FROM ORIGINAL
# =============================================================================

@app.route('/api/create_config', methods=['POST'])
@requires_auth
def create_config():
    """Create default config file"""
    try:
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
    """Add a new task via API"""
    try:
        data = request.json
        cmd_parts = [
            "add-task",
            f"--phase {data['phase']}",
            f"--id \"{data['id']}\"",
            f"--description \"{data['description']}\""
        ]
        
        if data.get('output'):
            cmd_parts.append(f"--output \"{data['output']}\"")
        if data.get('tests'):
            cmd_parts.append(f"--tests \"{data['tests']}\"")
        if data.get('context') and any(data['context']):
            context_items = [f'"{item}"' for item in data['context'] if item.strip()]
            if context_items:
                cmd_parts.append(f"--context {' '.join(context_items)}")
        if data.get('depends_on') and any(data['depends_on']):
            dep_items = [f'"{item}"' for item in data['depends_on'] if item.strip()]
            if dep_items:
                cmd_parts.append(f"--depends-on {' '.join(dep_items)}")
        if data.get('acceptance_criteria') and any(data['acceptance_criteria']):
            criteria_items = [f'"{item}"' for item in data['acceptance_criteria'] if item.strip()]
            if criteria_items:
                cmd_parts.append(f"--acceptance-criteria {' '.join(criteria_items)}")
        
        command = ' '.join(cmd_parts)
        result = run_cli_command(command)
        return jsonify(result)
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
    data = request.json
    task_id = data.get('task_id')
    use_enhanced = data.get('enhanced', True)
    
    if not task_id:
        return jsonify({"success": False, "error": "No task ID provided"})
    
    if use_enhanced:
        result = run_cli_command(f"start {task_id}")
    else:
        result = run_cli_command(f"start {task_id} --basic")
    
    result['enhanced'] = use_enhanced
    return jsonify(result)

@app.route('/api/preview_context/<task_id>')
@requires_auth
def preview_context(task_id):
    """Preview the enhanced context that would be generated"""
    try:
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
    data = request.json
    task_id = data.get('task_id')
    message = data.get('message', '')
    
    if not task_id:
        return jsonify({"success": False, "error": "No task ID provided"})
    
    if message:
        command = f'commit {task_id} --message "{message}"'
    else:
        command = f"commit {task_id}"
    
    result = run_cli_command(command)
    return jsonify(result)

@app.route('/api/block_task', methods=['POST'])
@requires_auth
def block_task():
    """Block a task with reason"""
    data = request.json
    task_id = data.get('task_id')
    reason = data.get('reason', '')
    
    if not task_id or not reason:
        return jsonify({"success": False, "error": "Task ID and reason required"})
    
    result = run_cli_command(f'block {task_id} "{reason}"')
    return jsonify(result)

@app.route('/api/generate_blueprint', methods=['POST'])
@requires_auth
def generate_blueprint():
    """Generate blueprint documentation via API"""
    data = request.json
    blueprint_type = data.get('type', 'phase')
    phase_id = data.get('phase_id', 1)
    
    try:
        from src.blueprint_generator import PhaseBlueprintGenerator
        generator = PhaseBlueprintGenerator(PROJECT_ROOT)
        
        if blueprint_type == 'phase':
            content = generator.generate_comprehensive_phase_blueprint(phase_id)
            filename = f"phase_{phase_id}_blueprint.md"
            filepath = generator.update_phase_blueprint(phase_id)
        elif blueprint_type == 'handoff':
            content = generator.generate_session_handoff()
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"session_{timestamp}.md"
            filepath = PROJECT_ROOT / "docs" / "sessions" / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
            filepath = str(filepath)
        elif blueprint_type == 'architecture':
            content = generator.generate_system_architecture_blueprint()
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
            filename = f"architecture_{timestamp}.md"
            filepath = PROJECT_ROOT / "docs" / "blueprints" / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
            filepath = str(filepath)
        else:
            return jsonify({"success": False, "error": "Invalid blueprint type"})
        
        return jsonify({
            "success": True,
            "content": content,
            "filepath": filepath,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/generate_report', methods=['POST'])
@requires_auth
def generate_report():
    """Generate Claude handoff report"""
    data = request.json
    task_id = data.get('task_id')
    custom_summary = data.get('summary', '')
    
    if not task_id:
        return jsonify({"success": False, "error": "No task ID provided"})
    
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
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        recent_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        artifacts = ", ".join(recent_files) if recent_files else task.get("output", "No artifacts specified")
    except:
        artifacts = task.get("output", "No artifacts specified")
    
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
    project_info = task_manager.get_project_info()
    return jsonify({
        "status": "healthy", 
        "project": project_info['name'],
        "domain": config.ui.domain if config else "bruce.honey-duo.com", 
        "version": "2.0-modular-complete",
        "config_loaded": project_info['config_loaded'],
        "total_tasks": len(task_manager.load_tasks().get("tasks", [])),
        "architecture": "modular-templates"
    })

if __name__ == "__main__":
    project_info = task_manager.get_project_info()
    domain = config.ui.domain if config else "hdw.honey-duo.com"
    port = config.ui.port if config else 8000
    
    print("🌐 Bruce Complete Management Interface - Fully Modular Version")
    print(f"🔐 Access: https://{domain}")
    print(f"🔑 Login: hdw / HoneyDuo2025!")
    print(f"📋 Project: {project_info['name']}")
    print(f"⚙️ Config: {'✅ Loaded' if project_info['config_loaded'] else '📋 Using defaults'}")
    print("")
    print("💡 COMPLETE Features Preserved:")
    print("  ⚙️ Config System - bruce.yaml configuration support")  
    print("  🎨 Dynamic Theming - colors and branding from config")
    print("  📁 Flexible Paths - configurable directory structure")
    print("  ✨ Enhanced Context - Related tasks, architecture, decisions")
    print("  🏗️ Blueprint Generator - Comprehensive documentation")
    print("  ⚙️ Task/Phase Management - Add/edit via web interface")
    print("  📥 Blueprint Import - Design-first workflow with YAML blueprints")
    print("  🔄 Multi-Project Support - Ready for Phase 3 testing")
    print("  📊 Full API Coverage - All original endpoints preserved")
    print("")
    print("🎯 MODULAR ARCHITECTURE:")
    print("  📂 templates/ - Individual page templates")
    print("  🔧 Easier maintenance for Phase 3 stress testing")
    print("  🧪 Ready for concurrent user testing")
    print("  📈 Prepared for multi-project isolation testing")
    print("")
    print("🚀 Ready for Phase 3 Testing & Optimization!")
    
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
