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
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <div>
                        <h1>🤖 {{ project_name }}</h1>
                        <div class="domain-badge">🌐 AI Project Assistant • {{ domain }}</div>
                    </div>
                    {% if multi_project_enabled %}
                    <div class="project-selector">
                        <label for="project-select">Project:</label>
                        <select id="project-select" onchange="switchProject()">
                            {% for project in available_projects %}
                                {% set selected = 'selected' if project.is_current else '' %}
                                {% set accessible_icon = '✅' if project.get('accessible', True) else '❌' %}
                                <option value="{{ project.path }}" {{ selected }}>
                                    {{ accessible_icon }} {{ project.name }} ({{ project.get('task_count', 0) }} tasks)
                                </option>
                            {% endfor %}
                        </select>
                    </div>
                    {% endif %}
                </div>
                <div class="nav">
                    <a href="/">📊 Dashboard</a>
                    <a href="/tasks">📋 Tasks</a>
                    <a href="/phases" class="active">📁 Phases</a>
                    <a href="/manage">⚙️ Manage</a>
                    <a href="/generator">🏗️ Generator</a>
                    <a href="/reports">📈 Reports</a>
                    <a href="/config">⚙️ Config</a>
                    <a href="/help">❓ Help</a>
                    {% if multi_project_enabled %}
                    <button onclick="discoverProjects()" class="btn btn-info" style="margin-left: 15px;">🔍 Discover</button>
                    {% endif %}
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
        
        <script>
        // Fix dropdown selection state on page load
        document.addEventListener('DOMContentLoaded', function() {
            const select = document.getElementById('project-select');
            if (!select) return;
            
            console.log('🔧 Setting up dropdown fix...');
            
            // Get backend current project and sync dropdown
            fetch('/api/current_project_info')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.project_info && data.project_info.path) {
                    const currentPath = data.project_info.path;
                    console.log('Backend current project:', currentPath);
                    console.log('Dropdown current value:', select.value);
                    
                    // Find matching option and select it
                    for (let i = 0; i < select.options.length; i++) {
                        if (select.options[i].value === currentPath) {
                            console.log('✅ Syncing dropdown to index', i);
                            select.selectedIndex = i;
                            break;
                        }
                    }
                }
            })
            .catch(error => console.log('❌ Error syncing dropdown:', error));
            
            // Add event handlers
            select.addEventListener('change', function() {
                console.log('🔄 CHANGE event - switching to:', this.value);
                switchProject();
            });
            
            // Force handler for clicks (bypasses onchange issues)
            select.addEventListener('click', function() {
                const originalIndex = this.selectedIndex;
                setTimeout(() => {
                    if (this.selectedIndex !== originalIndex) {
                        console.log('🔄 CLICK caused selection change - switching to:', this.value);
                        switchProject();
                    }
                }, 100);
            });
            
            console.log('✅ Dropdown handlers setup complete');
        });

        function switchProject() {
            const select = document.getElementById('project-select');
            const projectPath = select.value;
    
            console.log('=== PROJECT SWITCH TRIGGERED ===');
            console.log('Target path:', projectPath);
            console.log('Selected index:', select.selectedIndex);
    
            if (!projectPath || projectPath === '') {
                console.log('❌ Empty path, aborting');
                return;
            }
    
            const selectedOption = select.options[select.selectedIndex];
            const originalText = selectedOption.text;
    
            select.disabled = true;
            selectedOption.text = '🔄 Switching...';
    
            console.log('🔄 Making API call...');
    
            fetch('/api/switch_project', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache'
                },
                body: JSON.stringify({project_path: projectPath})
            })
            .then(response => {
                console.log('✅ API status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('✅ API response:', data);
        
                if (data.success) {
                    console.log('✅ SUCCESS - reloading page...');
                    window.location.href = window.location.href.split('?')[0] + '?refresh=' + Date.now();
                } else {
                    console.log('❌ FAILED:', data.error);
                    alert('Failed to switch project: ' + data.error);
                    selectedOption.text = originalText;
                    select.disabled = false;
                }
            })
            .catch(error => {
                console.log('❌ ERROR:', error);
                alert('Error switching project: ' + error);
                selectedOption.text = originalText;
                select.disabled = false;
            });
        }

        function discoverProjects() {
            fetch('/api/discover_projects')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const select = document.getElementById('project-select');
                    select.innerHTML = '';
                    
                    data.projects.forEach(project => {
                        const option = document.createElement('option');
                        option.value = project.path;
                        option.selected = project.is_current;
                        
                        const accessIcon = project.accessible ? '✅' : '❌';
                        const taskCount = project.task_count || 0;
                        option.textContent = `${accessIcon} ${project.name} (${taskCount} tasks)`;
                        
                        select.appendChild(option);
                    });
                    
                    alert(`Discovered ${data.projects.length} Bruce projects!`);
                } else {
                    alert('Failed to discover projects: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error discovering projects: ' + error);
            });
        }
        </script>
    </body>
    </html>
    """