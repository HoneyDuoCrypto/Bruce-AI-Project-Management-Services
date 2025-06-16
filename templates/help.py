def get_help_template():
    """Returns the complete help HTML template"""
    
    from .styles import get_shared_styles
    
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Help & User Guide - {{ page_title }}</title>
        <style>
""" + get_shared_styles() + """
            .help-section {
                background: rgba(30, 30, 30, 0.6);
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid {{ theme_color }};
            }
            .code-block {
                background: #1a1a1a;
                color: #ffffff;
                padding: 15px;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.4;
                overflow-x: auto;
                margin: 15px 0;
                border: 1px solid {{ theme_color }};
            }
            .workflow-step {
                background: rgba(0, 212, 170, 0.1);
                border: 1px solid rgba(0, 212, 170, 0.3);
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
            }
            .workflow-step h4 {
                color: {{ theme_color }};
                margin-bottom: 10px;
            }
            .tip-box {
                background: rgba(0, 212, 170, 0.1);
                border: 1px solid {{ theme_color }};
                border-radius: 8px;
                padding: 20px;
                margin: 25px 0;
            }
            .tip-box h4 {
                color: {{ theme_color }};
                margin-bottom: 15px;
            }
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
                    <a href="/phases">📁 Phases</a>
                    <a href="/manage">⚙️ Manage</a>
                    <a href="/generator">🏗️ Generator</a>
                    <a href="/reports">📈 Reports</a>
                    <a href="/config">⚙️ Config</a>
                    <a href="/help" class="active">❓ Help</a>
                    {% if multi_project_enabled %}
                    <button onclick="discoverProjects()" class="btn btn-info" style="margin-left: 15px;">🔍 Discover</button>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <div class="help-section">
            <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">⏱️ Session Tracking System</h3>
            <p style="color: #ccc; margin-bottom: 15px;">Bruce automatically tracks your work sessions for better handoffs:</p>
            <ul style="margin-left: 20px; line-height: 1.8; color: #ccc;">
                <li><strong>Automatic Time Tracking:</strong> Records how long you work on each task</li>
                <li><strong>File Change Monitoring:</strong> Tracks which files you modify during work</li>
                <li><strong>Git Integration:</strong> Associates commits with work sessions</li>
                <li><strong>Session Notes:</strong> Add progress notes during work</li>
                <li><strong>Handoff Context:</strong> Session data included in Claude reports</li>
            </ul>
            <div class="code-block">
            # Session commands
            bruce session status task-id     # Check active session
            bruce session note task-id --message "Progress update"
            bruce session end task-id       # Manually end session
            bruce session report task-id    # Generate session report
                </div>
        </div>



        <div class="container">
            <div class="content-section">
                <h2 class="section-title">📖 Bruce User Guide - Complete with Multi-Project Support</h2>
                
                <div class="help-section">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">🆕 What's New: Multi-Project Management</h3>
                    <ul style="margin-left: 20px; line-height: 1.8; color: #ccc;">
                        <li><strong>Project Switching:</strong> Switch between multiple Bruce projects seamlessly</li>
                        <li><strong>Project Discovery:</strong> Automatically find all Bruce projects on your system</li>
                        <li><strong>Project Health Status:</strong> See which projects are accessible and their task counts</li>
                        <li><strong>Session Management:</strong> Maintain separate states for each project</li>
                        <li><strong>Blueprint Import:</strong> Import structured phase definitions across projects</li>
                    </ul>
                </div>
                
                <div class="help-section">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">🔄 How to Use Multi-Project Features</h3>
                    <ol style="margin-left: 20px; line-height: 2; color: #ccc;">
                        <li><strong>Switch Projects:</strong> Use the project dropdown in the header to switch between projects</li>
                        <li><strong>Discover Projects:</strong> Click "🔍 Discover" to scan for new Bruce projects</li>
                        <li><strong>Project Status:</strong> ✅ indicates accessible projects, ❌ indicates issues</li>
                        <li><strong>Task Counts:</strong> See how many tasks each project has in the dropdown</li>
                        <li><strong>Independent Sessions:</strong> Each project maintains its own state and progress</li>
                    </ol>
                </div>
                
                <div class="help-section">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">📥 Blueprint Import System</h3>
                    <ol style="margin-left: 20px; line-height: 2; color: #ccc;">
                        <li><strong>Go to Manage Page:</strong> Click the "Import Blueprint" tab</li>
                        <li><strong>Choose Source:</strong> Paste YAML content or upload a .yml file</li>
                        <li><strong>Preview Import:</strong> Click "Preview" to see all tasks that will be created</li>
                        <li><strong>Validate Format:</strong> Use "Validate YAML" to check structure</li>
                        <li><strong>Import Blueprint:</strong> Click "Import" to create all tasks at once</li>
                    </ol>
                </div>
                
                <div class="help-section">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">📝 Blueprint YAML Format</h3>
                    <div class="code-block">
phase:
  id: 3
  name: "Trading Engine Phase"
  description: "Build core trading functionality"

tasks:
  - id: trading-core
    description: "Implement core trading engine"
    output: "src/trading_engine.py with full functionality"
    depends_on: []
    acceptance_criteria:
      - "Handles buy/sell orders correctly"
      - "Real-time price updates working"
      - "Risk management integrated"
  
  - id: trading-ui
    description: "Build trading interface"
    output: "Trading dashboard UI component"
    depends_on: ["trading-core"]
    acceptance_criteria:
      - "User can place orders"
      - "Portfolio view functional"
      - "Real-time updates display"
                    </div>
                </div>
                
                <div class="help-section">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">🎯 Enhanced Multi-Project Workflow</h3>
                    <div class="workflow-step">
                        <h4>1. Organize Projects</h4>
                        <p>Keep separate Bruce projects for different work streams. Each project maintains its own tasks, phases, and progress tracking.</p>
                    </div>
                    <div class="workflow-step">
                        <h4>2. Switch Contexts</h4>
                        <p>Use the project selector to seamlessly switch between projects. Your progress and state are maintained separately for each project.</p>
                    </div>
                    <div class="workflow-step">
                        <h4>3. Import Blueprints</h4>
                        <p>Design phase structures in YAML and import them into any project. Perfect for reusing patterns across similar work.</p>
                    </div>
                    <div class="workflow-step">
                        <h4>4. Monitor Health</h4>
                        <p>Check project health status indicators to ensure all projects are accessible and functioning properly.</p>
                    </div>
                    <div class="workflow-step">
                        <h4>5. Generate Reports</h4>
                        <p>Create handoff reports and blueprints specific to each project for effective collaboration.</p>
                    </div>
                </div>
                
                <div class="tip-box">
                    <h4>🎯 Pro Tip: Project Templates</h4>
                    <p>Create template projects with common phase structures and blueprint files. When starting new work, copy a template project and import your standard blueprints to get up and running quickly.</p>
                </div>
                
                <div class="tip-box">
                    <h4>💡 Pro Tip: Data Organization Projects</h4>
                    <p>Perfect for your data organization work! Create separate projects for different data sources or transformation workflows. Use blueprints for common patterns like "Extract → Transform → Load" phases.</p>
                </div>
                
                <div class="help-section">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">🚀 Quick Reference Commands</h3>
                    <div class="code-block">
# CLI Commands (work within current project directory)
bruce init "My Project"           # Initialize new Bruce project
bruce status                      # Show current project status
bruce list                        # List all tasks in current project
bruce start task-id               # Start task with enhanced context
bruce commit task-id              # Complete and commit task
bruce phases                      # Show phase progress
bruce ui                          # Start web interface

# Multi-Project Web Interface
Project Selector: Switch between discovered projects
🔍 Discover: Find all Bruce projects on system
Dashboard: Project-specific stats and progress
Tasks: Enhanced task management with context modals
Manage: Add tasks, phases, and import blueprints
Generator: Create project-specific documentation
Reports: Generate Claude handoff reports
Config: View and manage project configuration
                    </div>
                </div>
                
                <div class="help-section">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">📋 Multi-Project Architecture Benefits</h3>
                    <ul style="margin-left: 20px; line-height: 1.8; color: #ccc;">
                        <li><strong>Isolated Workspaces:</strong> Each project maintains independent state and progress</li>
                        <li><strong>Flexible Organization:</strong> Organize work by client, technology, or phase</li>
                        <li><strong>Easy Context Switching:</strong> Jump between projects without losing context</li>
                        <li><strong>Reusable Patterns:</strong> Import blueprints across similar projects</li>
                        <li><strong>Scalable Management:</strong> Handle multiple concurrent projects efficiently</li>
                    </ul>
                </div>
                
                <div class="tip-box">
                    <h4>🏗️ System Ready for Advanced Workflows</h4>
                    <p>The multi-project system is designed for complex scenarios: concurrent development streams, client work separation, and large-scale data processing pipelines. Each project can have its own themes, configurations, and workflows.</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="/" class="btn btn-primary">🏠 Back to Dashboard</a>
                    <a href="/manage" class="btn btn-success">📥 Try Blueprint Import</a>
                    <a href="/generator" class="btn btn-info">🏗️ Generate Documentation</a>
                </div>
            </div>
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