def get_reports_template():
    """Returns the complete reports HTML template"""
    
    from .styles import get_shared_styles
    
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Claude Reports - {{ page_title }}</title>
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
                    <a href="/phases">📁 Phases</a>
                    <a href="/manage">⚙️ Manage</a>
                    <a href="/generator">🏗️ Generator</a>
                    <a href="/reports" class="active">📈 Reports</a>
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
                <h2 class="section-title">📈 Claude Handoff Reports</h2>
                <p style="color: #ccc; margin-bottom: 20px;">Generate status reports for Claude session handoffs</p>
                
                <div class="form-group">
                    <label for="task-select">Select Task:</label>
                    <select id="task-select" onchange="updateSummary()">
                        <option value="">Choose a task...</option>
                        {% for phase_id in tasks_by_phase.keys()|sort %}
                            {% set phase_name = "Phase " + phase_id|string if phase_id > 0 else "Legacy" %}
                            <optgroup label="{{ phase_name }}">
                                {% for task in tasks_by_phase[phase_id] %}
                                    {% set status_icons = {'pending': '⏳', 'in-progress': '🔄', 'completed': '✅', 'blocked': '🚫'} %}
                                    {% set status_icon = status_icons.get(task.get('status'), '❓') %}
                                    {% set selected = 'selected' if task.id == selected_task else '' %}
                                    <option value="{{ task.id }}" {{ selected }}>{{ status_icon }} {{ task.id }} - {{ task.get("description", "")[:60] }}</option>
                                {% endfor %}
                            </optgroup>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="summary-input">Custom Summary (optional):</label>
                    <textarea id="summary-input" rows="4" placeholder="Leave empty for auto-generated summary based on task description"></textarea>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <button class="btn btn-primary" onclick="generateReport()">📈 Generate Report</button>
                    <button class="btn btn-info" onclick="copyReport()">📋 Copy to Clipboard</button>
                    <button class="btn btn-success" onclick="openReportsFolder()">📁 Open Reports Folder</button>
                </div>
                
                <div id="status-message"></div>
                
                <div class="form-group">
                    <label>Generated Report (For Claude Handoff):</label>
                    <div id="report-output" class="report-area">
Click "Generate Report" to create a Claude handoff report...

The report will include:
• Task ID and phase information
• Current status and progress
• Summary of work completed
• Files/artifacts created
• Context for continuing work

Reports are automatically saved to: claude_reports/Claude_Handoff_taskname_MMDD_HHMM.txt
                    </div>
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
            
            // Add session data to report request
            const requestData = {
                task_id: taskId,
                summary: summary,
                include_sessions: true  // New flag
            };

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
        
        function updateSummary() {
            const taskSelect = document.getElementById('task-select');
            const summaryInput = document.getElementById('summary-input');
            
            if (taskSelect.value) {
                const selectedOption = taskSelect.options[taskSelect.selectedIndex];
                const taskDesc = selectedOption.text.split(' - ')[1] || '';
                if (taskDesc) {
                    summaryInput.placeholder = `Auto-generated: "Implemented ${taskDesc}"`;
                }
            }
        }
        
        function generateReport() {
            const taskId = document.getElementById('task-select').value;
            const summary = document.getElementById('summary-input').value;
            
            if (!taskId) {
                showMessage('Please select a task first', 'error');
                return;
            }
            
            showMessage('Generating report...', 'info');
            
            fetch('/api/generate_report', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_id: taskId, summary: summary})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('report-output').textContent = data.report;
                    showMessage(`✅ Report generated and saved as: ${data.filename}`, 'success');
                } else {
                    showMessage(`❌ Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error}`, 'error');
            });
        }
        
        function copyReport() {
            const reportText = document.getElementById('report-output').textContent;
            if (!reportText || reportText.includes('Click "Generate Report"')) {
                showMessage('Generate a report first', 'error');
                return;
            }
            
            navigator.clipboard.writeText(reportText).then(() => {
                showMessage('📋 Report copied to clipboard! Ready for Claude handoff.', 'success');
            }).catch(() => {
                showMessage('❌ Failed to copy to clipboard', 'error');
            });
        }
        
        function openReportsFolder() {
            showMessage('📁 Reports are saved to: claude_reports/ folder in your project directory', 'info');
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
        
        window.onload = function() {
            updateSummary();
        };
        </script>
    </body>
    </html>
    """