"""
Phases template - Complete implementation for phase overview and progress tracking
"""

def get_phases_template():
    """Returns the complete phases overview HTML template"""
    
    from .styles import get_shared_styles
    
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Phase Overview - {{ page_title }}</title>
        <style>
""" + get_shared_styles() + """
        </style>
    </head>
    <body>
        <div class="header">
            <div class="container">
                <h1>🤖 {{ project_name }}</h1>
                <div class="domain-badge">🌐 AI Project Assistant • {{ domain }}</div>
                <div class="nav">
                    <a href="/">📊 Dashboard</a>
                    <a href="/tasks">📋 Tasks</a>
                    <a href="/phases" class="active">📁 Phases</a>
                    <a href="/manage">⚙️ Manage</a>
                    <a href="/generator">🏗️ Generator</a>
                    <a href="/reports">📈 Reports</a>
                    <a href="/config">⚙️ Config</a>
                    <a href="/help">❓ Help</a>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="content-section">
                <h2 class="section-title">📁 Phase Management</h2>
                <p style="color: #ccc; margin-bottom: 20px;">Track progress across all project phases</p>
            </div>
            
            {% for phase_id in phase_progress.keys()|sort %}
                {% set progress = phase_progress[phase_id] %}
                {% set phase_info = tasks_data.get("phases", {}).get(phase_id|string, {}) %}
                
                <div class="content-section">
                    <div class="phase-header">
                        <div>
                            <h3 class="phase-title">📁 Phase {{ phase_id }}: {{ progress.name }}</h3>
                            {% if phase_info.get("description") %}
                                <p style="color: #ccc; margin: 10px 0;">{{ phase_info.description }}</p>
                            {% endif %}
                        </div>
                        <div class="phase-progress">
                            <div class="progress-bar" style="width: 300px;">
                                <div class="progress-fill" style="width: {{ progress.percentage }}%"></div>
                            </div>
                            <div class="progress-text" style="font-size: 18px; color: {{ theme_color }};">{{ "%.0f"|format(progress.percentage) }}%</div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0;">
                        <div style="text-align: center; padding: 15px; background: rgba(0, 204, 0, 0.1); border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: bold; color: #00ff00;">{{ progress.completed }}</div>
                            <div style="color: #ccc;">Completed</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: rgba(0, 102, 204, 0.1); border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: bold; color: #0099ff;">{{ progress.in_progress }}</div>
                            <div style="color: #ccc;">In Progress</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: rgba(255, 140, 0, 0.1); border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: bold; color: #ff8c00;">{{ progress.pending }}</div>
                            <div style="color: #ccc;">Pending</div>
                        </div>
                        {% if progress.blocked > 0 %}
                            <div style="text-align: center; padding: 15px; background: rgba(204, 0, 0, 0.1); border-radius: 8px;">
                                <div style="font-size: 24px; font-weight: bold; color: #ff6b6b;">{{ progress.blocked }}</div>
                                <div style="color: #ccc;">Blocked</div>
                            </div>
                        {% endif %}
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <a href="/tasks" class="btn btn-primary">📋 View Phase Tasks</a>
                        <a href="/generator?phase={{ phase_id }}" class="btn btn-success">🏗️ Generate Blueprint</a>
                        {% if phase_id > 0 %}
                            <span style="color: #888; margin-left: 15px;">Source: {{ phase_info.get("file", "tasks.yaml") }}</span>
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """