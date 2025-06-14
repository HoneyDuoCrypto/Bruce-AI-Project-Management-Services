"""
Dashboard template - Complete implementation with all features
"""

def get_dashboard_template():
    """Returns the complete dashboard HTML template"""
    
    from .styles import get_shared_styles
    
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard - {{ page_title }}</title>
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
                    <a href="/" class="active">📊 Dashboard</a>
                    <a href="/tasks">📋 Tasks</a>
                    <a href="/phases">📁 Phases</a>
                    <a href="/manage">⚙️ Manage</a>
                    <a href="/generator">🏗️ Generator</a>
                    <a href="/reports">📈 Reports</a>
                    <a href="/config">⚙️ Config</a>
                    <a href="/help">❓ Help</a>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="time-display">{{ current_time }}</div>
            
            <div class="content-section">
                <h2 class="section-title">📊 Project Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-box stat-pending">
                        <div class="stat-number">{{ status_counts.get('pending', 0) }}</div>
                        <div class="stat-label">⏳ Pending Tasks</div>
                    </div>
                    <div class="stat-box stat-in-progress">
                        <div class="stat-number">{{ status_counts.get('in-progress', 0) }}</div>
                        <div class="stat-label">🔄 In Progress</div>
                    </div>
                    <div class="stat-box stat-completed">
                        <div class="stat-number">{{ status_counts.get('completed', 0) }}</div>
                        <div class="stat-label">✅ Completed</div>
                    </div>
                    <div class="stat-box stat-blocked">
                        <div class="stat-number">{{ status_counts.get('blocked', 0) }}</div>
                        <div class="stat-label">🚫 Blocked</div>
                    </div>
                </div>
            </div>
            
            <div class="content-section">
                <h2 class="section-title">📈 Phase Progress</h2>
                {% for phase_id in phase_progress.keys()|sort %}
                    {% set progress = phase_progress[phase_id] %}
                    <div class="phase-section">
                        <div class="phase-header">
                            <div class="phase-title">📁 Phase {{ phase_id }}: {{ progress.name }}</div>
                            <div class="phase-progress">
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: {{ progress.percentage }}%"></div>
                                </div>
                                <div class="progress-text">{{ "%.0f"|format(progress.percentage) }}% ({{ progress.completed }}/{{ progress.total }})</div>
                            </div>
                        </div>
                        <div style="color: #ccc; font-size: 14px;">
                            {{ progress.completed }} completed, {{ progress.in_progress }} in progress, {{ progress.pending }} pending
                            {% if progress.blocked > 0 %}, {{ progress.blocked }} blocked{% endif %}
                        </div>
                    </div>
                {% endfor %}
            </div>
            
            <div class="content-section">
                <h2 class="section-title">🚀 Quick Actions</h2>
                <div style="display: flex; gap: 15px; flex-wrap: wrap; justify-content: center;">
                    <a href="/tasks" class="btn btn-primary">📋 Manage Tasks</a>
                    <a href="/phases" class="btn btn-info">📁 View Phases</a>
                    <a href="/manage" class="btn btn-warning">⚙️ Add/Edit Tasks</a>
                    <a href="/generator" class="btn btn-success">🏗️ Blueprint Generator</a>
                    <a href="/reports" class="btn btn-warning">📈 Generate Reports</a>
                    <a href="/config" class="btn btn-secondary">⚙️ Configuration</a>
                    <button onclick="location.reload()" class="btn btn-secondary">🔄 Refresh Dashboard</button>
                </div>
            </div>
            
            <div class="content-section">
                <h2 class="section-title">🔄 Recent Activity</h2>
                {% if recent_tasks %}
                    {% for task in recent_tasks %}
                        {% set status_icons = {'pending': '⏳', 'in-progress': '🔄', 'completed': '✅', 'blocked': '🚫'} %}
                        {% set status_icon = status_icons.get(task.get('status'), '❓') %}
                        {% set phase_info = "Phase " + (task.get('phase', 0)|string) if task.get('phase', 0) > 0 else "Legacy" %}
                        
                        <div class="task-item">
                            <div class="task-info">
                                <div class="task-title">{{ status_icon }} {{ task.id }}</div>
                                <div class="task-meta">{{ task.get('description', '') }}</div>
                                <div class="task-meta">{{ phase_info }} • Updated: {{ task.get('time_str', 'Never') }} • Status: {{ task.get('status', 'pending') }}</div>
                            </div>
                            <div class="task-actions">
                                <a href="/tasks" class="btn btn-primary">📋 Manage</a>
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <div class="empty-state">No recent activity</div>
                {% endif %}
            </div>
        </div>
        
        <script>
        // Auto-refresh every 2 minutes
        setTimeout(() => location.reload(), 120000);
        </script>
    </body>
    </html>
    """