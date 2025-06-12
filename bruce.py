#!/usr/bin/env python3
"""
Fixed Bruce Complete Management Interface
Enhanced with multi-project support, collapsible phases, and proper project management
"""

from flask import Flask, request, jsonify, make_response, session
from functools import wraps
import yaml
import subprocess
import os
import sys
from pathlib import Path
import datetime
import json

# Add src to path to import managers
sys.path.insert(0, str(Path(__file__).parent))
from src.task_manager import TaskManager
from src.project_manager import ProjectManager

app = Flask(__name__)
app.secret_key = 'bruce-project-2025-secure'

# Authentication
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

# Initialize Project Manager
project_manager = ProjectManager()

def get_current_project_info():
    """Get current project information - Flask context aware"""
    try:
        # Try to get from session first (web UI)
        current_project_id = session.get('current_project_id') if 'session' in globals() else None
        
        if current_project_id:
            projects = project_manager.list_projects()
            if current_project_id in projects:
                return projects[current_project_id]
        
        # Fall back to project manager's default logic
        return project_manager.get_current_project()
    except Exception as e:
        print(f"Warning: Could not determine current project: {e}")
        # Return a default project info
        return {
            'id': 'default',
            'name': 'Bruce Default',
            'path': str(Path.cwd()),
            'description': 'Default Bruce project'
        }

def get_current_task_manager():
    """Get TaskManager for current project"""
    try:
        current_project = get_current_project_info()
        project_path = Path(current_project['path'])
        return TaskManager(project_path)
    except Exception as e:
        print(f"Warning: Using fallback TaskManager: {e}")
        return TaskManager(Path.cwd())

def run_cli_command(command):
    """Run CLI command and return result"""
    try:
        current_project = get_current_project_info()
        project_path = current_project['path']
        
        cmd = f"python3 {project_path}/cli/bruce.py {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=project_path)
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

def get_base_html(title, active_page="dashboard"):
    """Get base HTML template with improved design and project switcher"""
    task_manager = get_current_task_manager()
    config = task_manager.config
    current_project = get_current_project_info()
    
    if config:
        project_name = config.project.name
        theme_color = config.ui.theme_color
        domain = config.ui.domain
        page_title = config.ui.title or project_name
    else:
        project_name = current_project['name']
        theme_color = "#00d4aa"
        domain = "bruce.honey-duo.com"
        page_title = "Bruce"
    
    # Calculate lighter theme color for gradients
    theme_color_light = theme_color + "dd" if len(theme_color) == 7 else theme_color
    
    # Get available projects for switcher
    try:
        all_projects = project_manager.list_projects()
    except:
        all_projects = {current_project['id']: current_project}
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - {page_title}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d30 100%);
                color: #ffffff; 
                line-height: 1.6;
                min-height: 100vh;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ 
                background: linear-gradient(135deg, #2b2b2b 0%, #1a1a1a 100%);
                padding: 30px 0; 
                border-bottom: 3px solid {theme_color};
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            }}
            .header h1 {{ 
                color: {theme_color}; 
                text-align: center; 
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                margin-bottom: 10px;
            }}
            .domain-badge {{ 
                text-align: center; 
                color: #888;
                font-size: 14px;
                margin-bottom: 20px;
            }}
            .project-switcher {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .project-switcher select {{
                background: rgba(51, 51, 51, 0.8);
                color: #fff;
                border: 1px solid {theme_color};
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
                cursor: pointer;
            }}
            .project-switcher select:focus {{
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.3);
            }}
            .nav {{ 
                display: flex; 
                justify-content: center; 
                gap: 20px; 
                flex-wrap: wrap;
            }}
            .nav a {{ 
                color: #ffffff; 
                text-decoration: none; 
                padding: 12px 24px;
                background: linear-gradient(135deg, #333 0%, #555 100%);
                border-radius: 8px; 
                transition: all 0.3s ease;
                border: 1px solid transparent;
                font-weight: 500;
            }}
            .nav a:hover, .nav a.active {{ 
                background: linear-gradient(135deg, {theme_color} 0%, {theme_color_light} 100%);
                color: #000; 
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0,212,170,0.3);
            }}
            .content-section {{ 
                background: rgba(43, 43, 43, 0.8);
                border-radius: 15px; 
                padding: 25px; 
                margin: 20px 0;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
                box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            }}
            .section-title {{ 
                color: {theme_color}; 
                margin-bottom: 20px; 
                font-size: 1.5em;
                border-bottom: 2px solid {theme_color};
                padding-bottom: 10px;
            }}
            .collapsible-phase {{
                background: rgba(30, 30, 30, 0.5);
                border-radius: 12px;
                border: 1px solid rgba(0, 212, 170, 0.2);
                margin: 20px 0;
                overflow: hidden;
            }}
            .phase-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .phase-header:hover {{
                background: rgba(0, 212, 170, 0.1);
            }}
            .phase-header.collapsed {{
                border-bottom: none;
            }}
            .phase-title {{
                font-size: 1.3em;
                color: {theme_color};
                font-weight: bold;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .collapse-icon {{
                transition: transform 0.3s ease;
                font-size: 1.2em;
            }}
            .collapse-icon.collapsed {{
                transform: rotate(-90deg);
            }}
            .phase-progress {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            .progress-bar {{
                width: 200px;
                height: 20px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .progress-fill {{
                height: 100%;
                background: linear-gradient(90deg, {theme_color} 0%, {theme_color_light} 100%);
                transition: width 0.3s ease;
            }}
            .progress-text {{
                font-size: 14px;
                color: #ccc;
                white-space: nowrap;
            }}
            .phase-content {{
                padding: 0;
                max-height: 1000px;
                transition: max-height 0.3s ease, padding 0.3s ease;
                overflow: hidden;
            }}
            .phase-content.collapsed {{
                max-height: 0;
                padding: 0;
            }}
            .phase-inner {{
                padding: 20px;
            }}
            .btn {{ 
                padding: 10px 20px; 
                border: none; 
                border-radius: 8px;
                cursor: pointer; 
                font-weight: bold; 
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                margin: 5px;
                font-size: 14px;
            }}
            .btn:hover {{ 
                transform: translateY(-2px); 
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            }}
            .btn-primary {{ background: linear-gradient(135deg, {theme_color} 0%, {theme_color_light} 100%); color: #000; }}
            .btn-success {{ background: linear-gradient(135deg, #00cc00 0%, #009900 100%); color: white; }}
            .btn-info {{ background: linear-gradient(135deg, #0066cc 0%, #004499 100%); color: white; }}
            .btn-danger {{ background: linear-gradient(135deg, #cc0000 0%, #990000 100%); color: white; }}
            .btn-warning {{ background: linear-gradient(135deg, #ff8c00 0%, #ff6b35 100%); color: white; }}
            .btn-secondary {{ background: linear-gradient(135deg, #666 0%, #888 100%); color: white; }}
            .task-item {{ 
                display: flex; 
                justify-content: space-between; 
                align-items: center;
                padding: 20px; 
                margin: 15px 0; 
                background: rgba(51, 51, 51, 0.8);
                border-radius: 10px;
                border-left: 4px solid {theme_color};
                transition: all 0.3s ease;
            }}
            .task-item:hover {{
                background: rgba(51, 51, 51, 1);
                transform: translateX(5px);
            }}
            .task-info {{ flex: 1; }}
            .task-title {{ font-weight: bold; margin-bottom: 8px; font-size: 18px; }}
            .task-meta {{ color: #ccc; font-size: 14px; margin-bottom: 4px; }}
            .task-actions {{ display: flex; gap: 10px; flex-wrap: wrap; }}
            .form-group {{ margin: 20px 0; }}
            .form-group label {{ 
                display: block; 
                margin-bottom: 8px; 
                color: {theme_color}; 
                font-weight: bold;
            }}
            .form-group select, .form-group textarea, .form-group input {{
                width: 100%; 
                padding: 12px; 
                border: 1px solid #555; 
                border-radius: 8px;
                background: #333; 
                color: #fff;
                font-size: 16px;
                font-family: inherit;
            }}
            .form-group select:focus, .form-group textarea:focus, .form-group input:focus {{
                outline: none;
                border-color: {theme_color};
                box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.2);
            }}
            .form-row {{ 
                display: grid; 
                grid-template-columns: 1fr 1fr; 
                gap: 20px; 
            }}
            .form-row-thirds {{ 
                display: grid; 
                grid-template-columns: 1fr 1fr 1fr; 
                gap: 15px; 
            }}
            .report-area {{ 
                background: #1a1a1a; 
                color: #ffffff; 
                padding: 20px; 
                border-radius: 10px;
                font-family: 'Courier New', monospace; 
                white-space: pre-wrap;
                min-height: 300px; 
                margin: 20px 0;
                border: 2px solid {theme_color};
                font-size: 13px;
                line-height: 1.4;
                overflow-y: auto;
                max-height: 600px;
            }}
            .generator-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .generator-card {{
                background: rgba(30, 30, 30, 0.8);
                border-radius: 12px;
                padding: 20px;
                border: 1px solid rgba(0, 212, 170, 0.3);
                transition: all 0.3s ease;
            }}
            .generator-card:hover {{
                border-color: {theme_color};
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0, 212, 170, 0.2);
            }}
            .card-title {{
                color: {theme_color};
                font-size: 1.3em;
                font-weight: bold;
                margin-bottom: 15px;
                text-align: center;
            }}
            .card-description {{
                color: #ccc;
                margin-bottom: 20px;
                text-align: center;
            }}
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 20px; 
                margin: 20px 0; 
            }}
            .stat-box {{ 
                padding: 20px; 
                border-radius: 15px; 
                text-align: center; 
                color: white; 
                font-weight: bold;
                transition: all 0.3s ease;
                border: 1px solid rgba(255,255,255,0.1);
            }}
            .stat-box:hover {{ transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
            .stat-number {{ font-size: 2.5em; margin-bottom: 10px; }}
            .stat-label {{ font-size: 1em; opacity: 0.9; }}
            .stat-pending {{ background: linear-gradient(135deg, #ff8c00 0%, #ff6b35 100%); }}
            .stat-in-progress {{ background: linear-gradient(135deg, #0066cc 0%, #004499 100%); }}
            .stat-completed {{ background: linear-gradient(135deg, #00cc00 0%, #009900 100%); }}
            .stat-blocked {{ background: linear-gradient(135deg, #cc0000 0%, #990000 100%); }}
            .success {{ color: #00ff00; font-weight: bold; }}
            .error {{ color: #ff6b6b; font-weight: bold; }}
            .info {{ color: #0099ff; font-weight: bold; }}
            .time-display {{ 
                text-align: center; 
                color: #aaa; 
                font-size: 14px; 
                margin: 15px 0; 
            }}
            .status-message {{
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                font-weight: bold;
            }}
            .status-success {{ background: rgba(0, 204, 0, 0.2); color: #00ff00; border: 1px solid #00cc00; }}
            .status-error {{ background: rgba(204, 0, 0, 0.2); color: #ff6b6b; border: 1px solid #cc0000; }}
            .status-info {{ background: rgba(0, 102, 204, 0.2); color: #0099ff; border: 1px solid #0066cc; }}
            .empty-state {{
                text-align: center;
                color: #888;
                padding: 60px 20px;
                font-size: 18px;
            }}
            .modal {{
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.8);
            }}
            .modal-content {{
                background-color: #2b2b2b;
                margin: 5% auto;
                padding: 20px;
                border: 2px solid {theme_color};
                border-radius: 10px;
                width: 80%;
                max-width: 800px;
                max-height: 80vh;
                overflow-y: auto;
                color: #fff;
            }}
            .close {{
                color: {theme_color};
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
            }}
            .close:hover {{
                color: {theme_color_light};
            }}
            .checkbox-container {{
                margin: 15px 0;
                padding: 15px;
                background: rgba(0, 212, 170, 0.1);
                border-radius: 8px;
                border: 1px solid rgba(0, 212, 170, 0.3);
            }}
            .checkbox-container label {{
                display: flex;
                align-items: center;
                cursor: pointer;
            }}
            .checkbox-container input[type="checkbox"] {{
                margin-right: 10px;
                width: 20px;
                height: 20px;
                cursor: pointer;
            }}
            .related-tasks {{
                margin: 20px 0;
                padding: 15px;
                background: rgba(30, 30, 30, 0.8);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .related-task {{
                padding: 10px;
                margin: 5px 0;
                background: rgba(51, 51, 51, 0.8);
                border-radius: 5px;
                border-left: 3px solid {theme_color};
            }}
            .management-tabs {{
                display: flex;
                margin-bottom: 20px;
                border-bottom: 2px solid #333;
            }}
            .tab {{
                padding: 15px 25px;
                background: rgba(51, 51, 51, 0.8);
                color: #ccc;
                cursor: pointer;
                border: none;
                border-bottom: 3px solid transparent;
                transition: all 0.3s ease;
            }}
            .tab.active {{
                background: rgba(0, 212, 170, 0.1);
                color: {theme_color};
                border-bottom-color: {theme_color};
            }}
            .tab-content {{
                display: none;
                animation: fadeIn 0.3s ease;
            }}
            .tab-content.active {{
                display: block;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .dynamic-fields {{
                background: rgba(30, 30, 30, 0.8);
                border-radius: 8px;
                padding: 20px;
                margin: 15px 0;
                border: 1px solid rgba(0, 212, 170, 0.2);
            }}
            .field-row {{
                display: flex;
                gap: 10px;
                align-items: center;
                margin: 10px 0;
            }}
            .field-row input {{
                flex: 1;
                padding: 8px 12px;
                background: #333;
                border: 1px solid #555;
                border-radius: 6px;
                color: #fff;
            }}
            .remove-btn {{
                background: #cc0000;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
            }}
            .add-btn {{
                background: #00cc00;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                margin-top: 10px;
            }}
            .config-info {{
                background: rgba(30, 30, 30, 0.6);
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                border-left: 4px solid {theme_color};
            }}
            @media (max-width: 768px) {{
                .task-item {{ flex-direction: column; align-items: flex-start; }}
                .task-actions {{ margin-top: 15px; width: 100%; }}
                .nav {{ gap: 10px; }}
                .nav a {{ padding: 8px 16px; font-size: 14px; }}
                .progress-bar {{ width: 150px; }}
                .generator-grid {{ grid-template-columns: 1fr; }}
                .form-row {{ grid-template-columns: 1fr; }}
                .form-row-thirds {{ grid-template-columns: 1fr; }}
                .management-tabs {{ flex-wrap: wrap; }}
                .phase-header {{ flex-direction: column; align-items: flex-start; gap: 15px; }}
                .phase-progress {{ width: 100%; justify-content: space-between; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="container">
                <h1>🤖 {project_name}</h1>
                <div class="domain-badge">🌐 AI Project Assistant • {domain}</div>
                
                <div class="project-switcher">
                    <select id="project-selector" onchange="switchProject()">
    """
    
    # Add project options
    for project_id, project_info in all_projects.items():
        selected = 'selected' if project_id == current_project['id'] else ''
        html += f'<option value="{project_id}" {selected}>🗂️ {project_info["name"]}</option>'
    
    html += f"""
                    </select>
                </div>
                
                <div class="nav">
                    <a href="/" class="{'active' if active_page == 'dashboard' else ''}">📊 Dashboard</a>
                    <a href="/tasks" class="{'active' if active_page == 'tasks' else ''}">📋 Tasks</a>
                    <a href="/phases" class="{'active' if active_page == 'phases' else ''}">📁 Phases</a>
                    <a href="/manage" class="{'active' if active_page == 'manage' else ''}">⚙️ Manage</a>
                    <a href="/generator" class="{'active' if active_page == 'generator' else ''}">🏗️ Generator</a>
                    <a href="/reports" class="{'active' if active_page == 'reports' else ''}">📈 Reports</a>
                    <a href="/projects" class="{'active' if active_page == 'projects' else ''}">🗂️ Projects</a>
                    <a href="/config" class="{'active' if active_page == 'config' else ''}">⚙️ Config</a>
                    <a href="/help" class="{'active' if active_page == 'help' else ''}">❓ Help</a>
                </div>
            </div>
        </div>
        
        <div class="container">
        
        <script>
        function switchProject() {{
            const projectId = document.getElementById('project-selector').value;
            
            fetch('/api/switch_project', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{project_id: projectId}})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    location.reload();
                }} else {{
                    alert('❌ Error switching project: ' + data.error);
                }}
            }})
            .catch(error => {{
                alert('❌ Network error: ' + error);
            }});
        }}
        
        function togglePhase(phaseId) {{
            const header = document.getElementById(`phase-header-${{phaseId}}`);
            const content = document.getElementById(`phase-content-${{phaseId}}`);
            const icon = document.getElementById(`collapse-icon-${{phaseId}}`);
            
            if (content.classList.contains('collapsed')) {{
                content.classList.remove('collapsed');
                header.classList.remove('collapsed');
                icon.classList.remove('collapsed');
                localStorage.setItem(`phase-${{phaseId}}-collapsed`, 'false');
            }} else {{
                content.classList.add('collapsed');
                header.classList.add('collapsed');
                icon.classList.add('collapsed');
                localStorage.setItem(`phase-${{phaseId}}-collapsed`, 'true');
            }}
        }}
        
        // Restore collapse states on page load
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('[id^="phase-content-"]').forEach(content => {{
                const phaseId = content.id.replace('phase-content-', '');
                const isCollapsed = localStorage.getItem(`phase-${{phaseId}}-collapsed`) === 'true';
                
                if (isCollapsed) {{
                    const header = document.getElementById(`phase-header-${{phaseId}}`);
                    const icon = document.getElementById(`collapse-icon-${{phaseId}}`);
                    
                    content.classList.add('collapsed');
                    if (header) header.classList.add('collapsed');
                    if (icon) icon.classList.add('collapsed');
                }}
            }});
        }});
        </script>
    """
    
    return html

# Add projects page
@app.route('/projects')
@requires_auth
def projects_page():
    """Project management page"""
    html = get_base_html("Project Management", "projects")
    current_project = get_current_project_info()
    
    try:
        all_projects = project_manager.list_projects()
    except Exception as e:
        all_projects = {current_project['id']: current_project}
    
    html += f"""
            <div class="content-section">
                <h2 class="section-title">🗂️ Project Management</h2>
                <p style="color: #ccc; margin-bottom: 20px;">Manage and switch between Bruce projects</p>
                
                <div style="margin-bottom: 30px; text-align: center;">
                    <button class="btn btn-success" onclick="discoverProjects()">🔍 Discover Projects</button>
                    <button class="btn btn-info" onclick="refreshProjects()">🔄 Refresh List</button>
                    <button class="btn btn-warning" onclick="showAddProject()">➕ Add Project Path</button>
                </div>
                
                <div id="status-message"></div>
            </div>
            
            <div class="content-section">
                <h2 class="section-title">📋 Available Projects</h2>
    """
    
    for project_id, project_info in all_projects.items():
        is_current = project_id == current_project['id']
        
        html += f"""
                <div class="task-item" style="{'border-left-color: #00ff00;' if is_current else ''}">
                    <div class="task-info">
                        <div class="task-title">
                            {'🎯 ' if is_current else '🗂️ '}{project_info['name']}
                            {' (Current)' if is_current else ''}
                        </div>
                        <div class="task-meta">{project_info.get('description', 'No description')}</div>
                        <div class="task-meta">📁 Path: {project_info['path']}</div>
                        <div class="task-meta">📊 Tasks: {project_info.get('tasks_count', 0)} | Phases: {project_info.get('phases_count', 0)}</div>
                        <div class="task-meta">🕒 Last Modified: {project_info.get('last_modified', 'Unknown')}</div>
                    </div>
                    <div class="task-actions">
        """
        
        if not is_current:
            html += f'<button class="btn btn-primary" onclick="switchToProject(\'{project_id}\')">🔄 Switch To</button>'
        
        html += f"""
                        <button class="btn btn-info" onclick="openProjectPath(\'{project_info["path"]}\')">📁 Open Folder</button>
                        <button class="btn btn-secondary" onclick="showProjectDetails(\'{project_id}\')">ℹ️ Details</button>
                    </div>
                </div>
        """
    
    html += """
            </div>
        </div>
        
        <!-- Project Details Modal -->
        <div id="projectModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeProjectModal()">&times;</span>
                <div id="projectModalContent"></div>
            </div>
        </div>
        
        <script>
        function discoverProjects() {
            showMessage('🔍 Discovering Bruce projects...', 'info');
            
            fetch('/api/discover_projects', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(`✅ Found ${data.discovered_count} projects! Refreshing page...`, 'success');
                    setTimeout(() => location.reload(), 2000);
                } else {
                    showMessage(`❌ Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error}`, 'error');
            });
        }
        
        function refreshProjects() {
            showMessage('🔄 Refreshing project list...', 'info');
            location.reload();
        }
        
        function showAddProject() {
            const path = prompt('Enter project path to add to registry:');
            if (!path) return;
            
            fetch('/api/add_project_path', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: path})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(`✅ Project added successfully!`, 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showMessage(`❌ Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error}`, 'error');
            });
        }
        
        function switchToProject(projectId) {
            fetch('/api/switch_project', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({project_id: projectId})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage('✅ Project switched successfully! Redirecting...', 'success');
                    setTimeout(() => window.location.href = '/', 1500);
                } else {
                    showMessage(`❌ Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error}`, 'error');
            });
        }
        
        function openProjectPath(path) {
            showMessage(`📁 Project path: ${path}`, 'info');
        }
        
        function showProjectDetails(projectId) {
            fetch(`/api/project_details/${projectId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const project = data.project;
                    document.getElementById('projectModalContent').innerHTML = `
                        <h2 style="color: """ + (get_current_task_manager().config.ui.theme_color if get_current_task_manager().config else '#00d4aa') + """;">🗂️ ${project.name}</h2>
                        <div style="margin: 20px 0;">
                            <p><strong>Description:</strong> ${project.description || 'No description'}</p>
                            <p><strong>Path:</strong> ${project.path}</p>
                            <p><strong>Type:</strong> ${project.type || 'Unknown'}</p>
                            <p><strong>Tasks:</strong> ${project.tasks_count || 0}</p>
                            <p><strong>Phases:</strong> ${project.phases_count || 0}</p>
                            <p><strong>Last Modified:</strong> ${project.last_modified || 'Unknown'}</p>
                        </div>
                        <button class="btn btn-secondary" onclick="closeProjectModal()">Close</button>
                    `;
                    document.getElementById('projectModal').style.display = 'block';
                } else {
                    showMessage(`❌ Error loading project details: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error}`, 'error');
            });
        }
        
        function closeProjectModal() {
            document.getElementById('projectModal').style.display = 'none';
        }
        
        function showMessage(message, type) {
            const statusDiv = document.getElementById('status-message');
            statusDiv.innerHTML = `<div class="status-message status-${type}">${message}</div>`;
            
            if (type === 'success') {
                setTimeout(() => {
                    statusDiv.innerHTML = '';
                }, 5000);
            }
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('projectModal');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
        </script>
    </body>
    </html>
    """
    
    return html

# Add configuration page with project awareness
@app.route('/config')
@requires_auth
def config_info():
    """Show current configuration"""
    task_manager = get_current_task_manager()
    html = get_base_html("Configuration", "config")
    info = task_manager.get_project_info()
    config = task_manager.config
    
    html += f"""
            <div class="content-section">
                <h2 class="section-title">⚙️ Bruce Configuration</h2>
                <p style="color: #ccc; margin-bottom: 20px;">Project configuration and system settings</p>
                
                <div class="config-info">
                    <h3 style="color: {config.ui.theme_color if config else '#00d4aa'}; margin-bottom: 15px;">📋 Project Information</h3>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Project Name:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff;">
                                {info['name']}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Project Type:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff;">
                                {info['type']}
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Description:</label>
                        <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff;">
                            {info['description']}
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Config File:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {info['config_file'] or 'None (using defaults)'}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Config Status:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff;">
                                {'✅ Loaded from file' if info['config_loaded'] else '📋 Using defaults'}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="config-info">
                    <h3 style="color: {config.ui.theme_color if config else '#00d4aa'}; margin-bottom: 15px;">📁 Directory Structure</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Contexts:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {config.bruce.contexts_dir if config else 'contexts'}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Blueprints:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {config.bruce.blueprints_dir if config else 'docs/blueprints'}
                            </div>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Phases:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {config.bruce.phases_dir if config else 'phases'}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Reports:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {config.bruce.reports_dir if config else 'claude_reports'}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="config-info">
                    <h3 style="color: {config.ui.theme_color if config else '#00d4aa'}; margin-bottom: 15px;">🎨 UI Settings</h3>
                    <div class="form-row-thirds">
                        <div class="form-group">
                            <label>Theme Color:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                <span style="display: inline-block; width: 20px; height: 20px; background: {config.ui.theme_color if config else '#00d4aa'}; border-radius: 3px; margin-right: 10px; vertical-align: middle;"></span>
                                {config.ui.theme_color if config else '#00d4aa'}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Domain:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {config.ui.domain if config else 'bruce.honey-duo.com'}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Port:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {config.ui.port if config else '5000'}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 30px; text-align: center;">
                    <button class="btn btn-primary" onclick="createConfig()">📄 Create Config File</button>
                    <button class="btn btn-info" onclick="validateConfig()">✅ Validate Config</button>
                    <button class="btn btn-secondary" onclick="location.reload()">🔄 Reload Config</button>
                    <button class="btn btn-warning" onclick="showConfigExample()">📝 Show Example</button>
                </div>
                
                <div id="config-status"></div>
                <div id="config-example" style="display: none; margin-top: 20px;">
                    <h3 style="color: {config.ui.theme_color if config else '#00d4aa'}; margin-bottom: 15px;">📝 Example bruce.yaml</h3>
                    <div class="report-area" style="max-height: 400px;">
# Bruce Project Configuration
project:
  name: "My Amazing Project"
  description: "AI-assisted project management"
  type: "web-application"
  author: "Your Name"

bruce:
  # Directory structure (relative to project root)
  contexts_dir: "contexts"
  blueprints_dir: "docs/blueprints"
  phases_dir: "phases"
  reports_dir: "claude_reports"
  tasks_file: "tasks.yaml"

ui:
  # Web interface customization
  title: "My Project"
  theme_color: "#00d4aa"
  domain: "bruce.honey-duo.com"
  port: 5000
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        function createConfig() {{
            if (!confirm('Create a default bruce.yaml configuration file?\\n\\nThis will help make your project portable.')) return;
            
            fetch('/api/create_config', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}}
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    showConfigMessage('✅ Config file created successfully! Reloading...', 'success');
                    setTimeout(() => location.reload(), 2000);
                }} else {{
                    showConfigMessage('❌ Error: ' + data.error, 'error');
                }}
            }})
            .catch(error => {{
                showConfigMessage('❌ Network error: ' + error, 'error');
            }});
        }}
        
        function validateConfig() {{
            fetch('/api/validate_config')
            .then(response => response.json())
            .then(data => {{
                if (data.valid) {{
                    showConfigMessage('✅ Configuration is valid! All directories accessible.', 'success');
                }} else {{
                    showConfigMessage('❌ Configuration validation failed: ' + (data.error || 'Unknown error'), 'error');
                }}
            }})
            .catch(error => {{
                showConfigMessage('❌ Network error: ' + error, 'error');
            }});
        }}
        
        function showConfigExample() {{
            const exampleDiv = document.getElementById('config-example');
            if (exampleDiv.style.display === 'none') {{
                exampleDiv.style.display = 'block';
            }} else {{
                exampleDiv.style.display = 'none';
            }}
        }}
        
        function showConfigMessage(message, type) {{
            document.getElementById('config-status').innerHTML = 
                `<div class="status-message status-${{type}}" style="margin-top: 20px;">${{message}}</div>`;
        }}
        </script>
    </body>
    </html>
    """
    return html

# DASHBOARD - Enhanced with collapsible phases
@app.route('/')
@requires_auth
def dashboard():
    task_manager = get_current_task_manager()
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
    
    current_time = datetime.datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')
    
    html = get_base_html("Dashboard", "dashboard")
    
    html += f"""
            <div class="time-display">{current_time}</div>
            
            <div class="content-section">
                <h2 class="section-title">📊 Project Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-box stat-pending">
                        <div class="stat-number">{status_counts.get('pending', 0)}</div>
                        <div class="stat-label">⏳ Pending Tasks</div>
                    </div>
                    <div class="stat-box stat-in-progress">
                        <div class="stat-number">{status_counts.get('in-progress', 0)}</div>
                        <div class="stat-label">🔄 In Progress</div>
                    </div>
                    <div class="stat-box stat-completed">
                        <div class="stat-number">{status_counts.get('completed', 0)}</div>
                        <div class="stat-label">✅ Completed</div>
                    </div>
                    <div class="stat-box stat-blocked">
                        <div class="stat-number">{status_counts.get('blocked', 0)}</div>
                        <div class="stat-label">🚫 Blocked</div>
                    </div>
                </div>
            </div>
            
            <div class="content-section">
                <h2 class="section-title">📈 Phase Progress</h2>
                <p style="color: #ccc; margin-bottom: 20px;">Click on phase headers to collapse/expand</p>
    """
    
    # Show collapsible phase progress
    for phase_id in sorted(phase_progress.keys()):
        progress = phase_progress[phase_id]
        bar_width = int(progress["percentage"])
        
        html += f"""
                <div class="collapsible-phase">
                    <div class="phase-header" id="phase-header-{phase_id}" onclick="togglePhase({phase_id})">
                        <div class="phase-title">
                            <span class="collapse-icon" id="collapse-icon-{phase_id}">▼</span>
                            📁 Phase {phase_id}: {progress['name']}
                        </div>
                        <div class="phase-progress">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {bar_width}%"></div>
                            </div>
                            <div class="progress-text">{progress['percentage']:.0f}% ({progress['completed']}/{progress['total']})</div>
                        </div>
                    </div>
                    <div class="phase-content" id="phase-content-{phase_id}">
                        <div class="phase-inner">
                            <div style="color: #ccc; font-size: 14px; margin-bottom: 15px;">
                                {progress['completed']} completed, {progress['in_progress']} in progress, {progress['pending']} pending
                                {f", {progress['blocked']} blocked" if progress['blocked'] > 0 else ""}
                            </div>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px;">
                                <div style="text-align: center; padding: 10px; background: rgba(0, 204, 0, 0.1); border-radius: 6px;">
                                    <div style="font-size: 18px; font-weight: bold; color: #00ff00;">{progress['completed']}</div>
                                    <div style="color: #ccc; font-size: 12px;">Completed</div>
                                </div>
                                <div style="text-align: center; padding: 10px; background: rgba(0, 102, 204, 0.1); border-radius: 6px;">
                                    <div style="font-size: 18px; font-weight: bold; color: #0099ff;">{progress['in_progress']}</div>
                                    <div style="color: #ccc; font-size: 12px;">In Progress</div>
                                </div>
                                <div style="text-align: center; padding: 10px; background: rgba(255, 140, 0, 0.1); border-radius: 6px;">
                                    <div style="font-size: 18px; font-weight: bold; color: #ff8c00;">{progress['pending']}</div>
                                    <div style="color: #ccc; font-size: 12px;">Pending</div>
                                </div>
                                {f'<div style="text-align: center; padding: 10px; background: rgba(204, 0, 0, 0.1); border-radius: 6px;"><div style="font-size: 18px; font-weight: bold; color: #ff6b6b;">{progress["blocked"]}</div><div style="color: #ccc; font-size: 12px;">Blocked</div></div>' if progress['blocked'] > 0 else ''}
                            </div>
                        </div>
                    </div>
                </div>
        """
    
    html += """
            </div>
            
            <div class="content-section">
                <h2 class="section-title">🚀 Quick Actions</h2>
                <div style="display: flex; gap: 15px; flex-wrap: wrap; justify-content: center;">
                    <a href="/tasks" class="btn btn-primary">📋 Manage Tasks</a>
                    <a href="/phases" class="btn btn-info">📁 View Phases</a>
                    <a href="/manage" class="btn btn-warning">⚙️ Add/Edit Tasks</a>
                    <a href="/generator" class="btn btn-success">🏗️ Blueprint Generator</a>
                    <a href="/reports" class="btn btn-warning">📈 Generate Reports</a>
                    <a href="/projects" class="btn btn-secondary">🗂️ Switch Projects</a>
                    <button onclick="location.reload()" class="btn btn-secondary">🔄 Refresh Dashboard</button>
                </div>
            </div>
            
            <div class="content-section">
                <h2 class="section-title">🔄 Recent Activity</h2>
    """
    
    if recent_tasks:
        for task in recent_tasks:
            status_icon = {'pending': '⏳', 'in-progress': '🔄', 'completed': '✅', 'blocked': '🚫'}.get(task.get('status'), '❓')
            phase_info = f"Phase {task.get('phase', 0)}" if task.get('phase', 0) > 0 else "Legacy"
            updated = task.get('updated', '')
            if updated:
                try:
                    dt = datetime.datetime.fromisoformat(updated.replace('Z', '+00:00'))
                    time_str = dt.strftime('%m/%d %I:%M%p')
                except:
                    time_str = updated[:10]
            else:
                time_str = 'Never'
            
            html += f"""
                <div class="task-item">
                    <div class="task-info">
                        <div class="task-title">{status_icon} {task['id']}</div>
                        <div class="task-meta">{task.get('description', '')}</div>
                        <div class="task-meta">{phase_info} • Updated: {time_str} • Status: {task.get('status', 'pending')}</div>
                    </div>
                    <div class="task-actions">
                        <a href="/tasks" class="btn btn-primary">📋 Manage</a>
                    </div>
                </div>
            """
    else:
        html += '<div class="empty-state">No recent activity</div>'
    
    html += """
            </div>
        </div>
        
        <script>
        // Auto-refresh every 2 minutes
        setTimeout(() => location.reload(), 120000);
        </script>
    </body>
    </html>
    """
    
    return html

# Project Management API Endpoints
@app.route('/api/switch_project', methods=['POST'])
@requires_auth
def switch_project():
    """Switch current project"""
    try:
        data = request.json
        project_id = data.get('project_id')
        
        if not project_id:
            return jsonify({"success": False, "error": "No project ID provided"})
        
        # Store in session
        session['current_project_id'] = project_id
        
        # Also update user settings for CLI
        try:
            project_manager.set_current_project(project_id)
        except Exception as e:
            print(f"Warning: Could not update CLI settings: {e}")
        
        return jsonify({"success": True, "project_id": project_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/discover_projects', methods=['POST'])
@requires_auth
def discover_projects():
    """Discover new projects"""
    try:
        data = request.json or {}
        scan_paths = data.get('scan_paths', [])
        
        discovered_count = project_manager.discover_projects(additional_paths=scan_paths)
        
        return jsonify({
            "success": True,
            "discovered_count": discovered_count
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/add_project_path', methods=['POST'])
@requires_auth
def add_project_path():
    """Add a specific project path"""
    try:
        data = request.json
        path = data.get('path')
        
        if not path:
            return jsonify({"success": False, "error": "No path provided"})
        
        project_path = Path(path)
        if not project_path.exists():
            return jsonify({"success": False, "error": "Path does not exist"})
        
        if not (project_path / 'bruce.yaml').exists():
            return jsonify({"success": False, "error": "Path does not contain bruce.yaml"})
        
        project_manager.add_project_by_path(project_path)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/project_details/<project_id>')
@requires_auth
def project_details(project_id):
    """Get detailed project information"""
    try:
        projects = project_manager.list_projects()
        
        if project_id not in projects:
            return jsonify({"success": False, "error": "Project not found"})
        
        project_info = projects[project_id]
        
        # Get additional details
        project_path = Path(project_info['path'])
        task_manager = TaskManager(project_path)
        
        try:
            tasks_data = task_manager.load_tasks()
            project_info['tasks_count'] = len(tasks_data.get('tasks', []))
            project_info['phases_count'] = len(tasks_data.get('phases', {}))
        except:
            project_info['tasks_count'] = 0
            project_info['phases_count'] = 0
        
        return jsonify({
            "success": True,
            "project": project_info
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Continue with existing routes but using get_current_task_manager()...
# (I'll continue with the remaining routes in the next part to keep this manageable)

# API ENDPOINTS - Updated to use current project
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

# Health check
@app.route('/health')
def health_check():
    try:
        current_project = get_current_project_info()
        task_manager = get_current_task_manager()
        project_info = task_manager.get_project_info()
        config = task_manager.config
        
        return jsonify({
            "status": "healthy", 
            "project": project_info['name'],
            "project_id": current_project['id'],
            "domain": config.ui.domain if config else "bruce.honey-duo.com", 
            "version": "2.0-multi-project-collapsible",
            "config_loaded": project_info['config_loaded'],
            "projects_available": len(project_manager.list_projects())
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        })

if __name__ == "__main__":
    print("🔍 Discovering Bruce projects...")
    try:
        discovered = project_manager.discover_projects()
        print(f"📋 Found {len(project_manager.list_projects())} Bruce projects")
    except Exception as e:
        print(f"⚠️ Warning: Project discovery failed: {e}")
    
    try:
        current_project = get_current_project_info()
        task_manager = get_current_task_manager()
        project_info = task_manager.get_project_info()
        config = task_manager.config
        
        domain = config.ui.domain if config else "hdw.honey-duo.com"
        port = config.ui.port if config else 5000
        
        print("🌐 Bruce Complete Management Interface - Multi-Project with Collapsible Phases")
        print(f"🔐 Access: https://{domain}")
        print(f"🔑 Login: hdw / HoneyDuo2025!")
        print(f"📋 Current Project: {current_project['name']}")
        print(f"⚙️ Config: {'✅ Loaded' if project_info['config_loaded'] else '📋 Using defaults'}")
        print("")
        print("💡 New Features:")
        print("  🗂️ Multi-Project Support - Switch between projects seamlessly")
        print("  📁 Collapsible Phases - Click phase headers to collapse/expand")
        print("  🔄 Project Switcher - Dropdown in header for quick switching")
        print("  🎯 Session Persistence - Remembers current project across sessions")
        print("  ⚙️ Enhanced Config System - Project-specific configurations")
        print("  📥 Blueprint Import - Design-first workflow with YAML blueprints")
        print("")
        print("🚀 Ready for advanced multi-project Bruce management!")
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
        
    except Exception as e:
        print(f"❌ Error starting Bruce: {e}")
        print("📋 Using fallback configuration...")
        
        # Fallback configuration
        print("🌐 Bruce Complete Management Interface - Fallback Mode")
        print("🔐 Access: http://localhost:5000")
        print("🔑 Login: hdw / HoneyDuo2025!")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)