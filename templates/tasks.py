"""
Tasks management template - Complete implementation with enhanced context and modals
FIXED: Removed invalid {% break %} tag and added proper multi-project header
"""

def get_tasks_template():
    """Returns the complete tasks management HTML template"""
    
    from .styles import get_shared_styles
    
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Task Management - {{ page_title }}</title>
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
                    <a href="/tasks" class="active">📋 Tasks</a>
                    <a href="/phases">📁 Phases</a>
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
                <h2 class="section-title">📋 Task Management</h2>
                <div style="margin-bottom: 20px; text-align: center;">
                    <button onclick="location.reload()" class="btn btn-info">🔄 Refresh Tasks</button>
                </div>
            </div>
            
            {% if tasks_by_phase %}
                {% for phase_id in tasks_by_phase.keys()|sort %}
                    {% set phase_tasks = tasks_by_phase[phase_id] %}
                    {% set phase_info = tasks_data.get("phases", {}).get(phase_id|string, {}) %}
                    {% set phase_name = phase_info.get("name", "Legacy Tasks" if phase_id == 0 else "Phase " + phase_id|string) %}
                    {% set total_tasks = phase_tasks.pending|length + phase_tasks.get('in-progress', [])|length + phase_tasks.completed|length + phase_tasks.blocked|length %}
                    
                    {% if total_tasks > 0 %}
                        <div class="content-section">
                            <h2 class="section-title">📁 {{ phase_name }}</h2>
                            
                            {% for status in ['in-progress', 'pending', 'blocked', 'completed'] %}
                                {% set task_list = phase_tasks.get(status, []) %}
                                {% if task_list %}
                                    {% set status_info = {
                                        'pending': ('⏳', 'Pending'),
                                        'in-progress': ('🔄', 'In Progress'),
                                        'completed': ('✅', 'Completed'),
                                        'blocked': ('🚫', 'Blocked')
                                    } %}
                                    {% set emoji, label = status_info[status] %}
                                    
                                    <h4 style="color: {{ theme_color }}; margin: 20px 0 10px 0;">{{ emoji }} {{ label }} ({{ task_list|length }})</h4>
                                    
                                    {% for task in task_list %}
                                        <div class="task-item">
                                            <div class="task-info">
                                                <div class="task-title">{{ task.id }}</div>
                                                <div class="task-meta">{{ task.get('description', 'No description') }}</div>
                                                <div class="task-meta">Updated: {{ task.get('time_str', 'Never') }}</div>
                                                <div class="task-meta">Output: {{ task.get('output', 'Not specified') }}</div>
                                                {% if task.get('tests') %}
                                                    <div class="task-meta">Tests: {{ task.tests }}</div>
                                                {% endif %}
                                                
                                                {% if status == "blocked" and task.get("notes") %}
                                                    {% for note in task.get("notes", [])|reverse %}
                                                        {% if "Blocked:" in note.get("note", "") %}
                                                            <div class="task-meta" style="color: #ff6b6b; font-weight: bold;">🚫 {{ note.note }}</div>
                                                        {% endif %}
                                                    {% endfor %}
                                                {% endif %}
                                            </div>
                                            <div class="task-actions">
                                                {% if status == 'pending' %}
                                                    <button class="btn btn-success" onclick="showStartDialog('{{ task.id }}')">🚀 Start Task</button>
                                                {% elif status == 'in-progress' %}
                                                    <button class="btn btn-primary" onclick="completeTask('{{ task.id }}')">✅ Complete Task</button>
                                                {% endif %}
                                                
                                                {% if status not in ['completed', 'blocked'] %}
                                                    <button class="btn btn-danger" onclick="blockTask('{{ task.id }}')">🚫 Block Task</button>
                                                {% endif %}
                                                
                                                {% if status in ['pending', 'in-progress'] %}
                                                    <button class="btn btn-secondary" onclick="previewContext('{{ task.id }}')">👁️ Preview Context</button>
                                                    <button class="btn btn-info" onclick="showRelatedTasks('{{ task.id }}')">🔗 Related Tasks</button>
                                                {% endif %}
                                                
                                                {% if status in ['completed', 'blocked', 'in-progress'] %}
                                                    <a href="/reports?task={{ task.id }}" class="btn btn-warning">📈 Generate Report</a>
                                                {% endif %}
                                            </div>
                                        </div>
                                    {% endfor %}
                                {% endif %}
                            {% endfor %}
                        </div>
                    {% endif %}
                {% endfor %}
            {% else %}
                <div class="content-section">
                    <div class="empty-state">No tasks found.</div>
                </div>
            {% endif %}
            
            <!-- Enhanced context modal -->
            <div id="contextModal" class="modal">
                <div class="modal-content">
                    <span class="close" onclick="closeModal()">&times;</span>
                    <div id="modalContent"></div>
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
        
        function showStartDialog(taskId) {
            const modalContent = `
                <h2 style="color: {{ theme_color }}; margin-bottom: 20px;">🚀 Start Task: ${taskId}</h2>
                <div class="checkbox-container">
                    <label>
                        <input type="checkbox" id="useEnhanced" checked>
                        <span style="font-size: 16px;">✨ Use Enhanced Context</span>
                    </label>
                    <p style="color: #ccc; margin-top: 10px; margin-left: 30px; font-size: 14px;">
                        Includes related tasks, architecture diagrams, and decision history
                    </p>
                </div>
                <div style="margin-top: 20px;">
                    <button class="btn btn-success" onclick="startTaskWithOptions('${taskId}')">🚀 Start Task</button>
                    <button class="btn btn-secondary" onclick="previewContextInModal('${taskId}')">👁️ Preview Context</button>
                    <button class="btn btn-secondary" onclick="closeModal()">❌ Cancel</button>
                </div>
                <div id="previewArea" style="margin-top: 20px;"></div>
            `;
            
            document.getElementById('modalContent').innerHTML = modalContent;
            document.getElementById('contextModal').style.display = 'block';
        }
        
        function startTaskWithOptions(taskId) {
            const useEnhanced = document.getElementById('useEnhanced').checked;
            
            if (!confirm(`Start task '${taskId}' with ${useEnhanced ? 'enhanced' : 'basic'} context?\\n\\nThis will create a context file for Claude.`)) return;
            
            fetch('/api/start_task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    task_id: taskId,
                    enhanced: useEnhanced
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`✅ Task '${taskId}' started successfully!\\n\\n📄 ${data.enhanced ? 'Enhanced' : 'Basic'} context file created.`);
                    location.reload();
                } else {
                    alert(`❌ Error starting task: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`❌ Network error: ${error}`);
            });
        }
        
        function startTask(taskId) {
            // Legacy function for backward compatibility
            showStartDialog(taskId);
        }
        
        function previewContext(taskId) {
            fetch(`/api/preview_context/${taskId}`)
                .then(response => response.json())
                .then(data => {
                    const modalContent = `
                        <h2 style="color: {{ theme_color }};">📄 Context Preview: ${taskId}</h2>
                        <div class="report-area" style="max-height: 500px;">
                            ${data.context.replace(/\\n/g, '\\n')}
                        </div>
                        <button class="btn btn-secondary" onclick="closeModal()">Close</button>
                    `;
                    document.getElementById('modalContent').innerHTML = modalContent;
                    document.getElementById('contextModal').style.display = 'block';
                })
                .catch(error => {
                    alert(`❌ Error loading context: ${error}`);
                });
        }
        
        function previewContextInModal(taskId) {
            const useEnhanced = document.getElementById('useEnhanced').checked;
            
            fetch(`/api/preview_context/${taskId}?enhanced=${useEnhanced}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('previewArea').innerHTML = `
                        <h3 style="color: {{ theme_color }};">Preview:</h3>
                        <div class="report-area" style="max-height: 300px;">
                            ${data.context.replace(/\\n/g, '\\n')}
                        </div>
                    `;
                })
                .catch(error => {
                    document.getElementById('previewArea').innerHTML = `<p class="error">Error loading preview</p>`;
                });
        }
        
        function showRelatedTasks(taskId) {
            fetch(`/api/related_tasks/${taskId}`)
                .then(response => response.json())
                .then(data => {
                    let relatedHtml = '<h3 style="color: {{ theme_color }};">🔗 Related Tasks</h3>';
                    
                    if (data.related_tasks && data.related_tasks.length > 0) {
                        relatedHtml += '<div class="related-tasks">';
                        data.related_tasks.forEach(task => {
                            const statusIcon = task.status === 'completed' ? '✅' : '🔄';
                            relatedHtml += `
                                <div class="related-task">
                                    <strong>${statusIcon} ${task.id}</strong>: ${task.description}
                                    <div style="color: #888; font-size: 12px; margin-top: 5px;">
                                        Phase ${task.phase} • Status: ${task.status}
                                    </div>
                                </div>
                            `;
                        });
                        relatedHtml += '</div>';
                    } else {
                        relatedHtml += '<p style="color: #888;">No related tasks found.</p>';
                    }
                    
                    relatedHtml += '<button class="btn btn-secondary" onclick="closeModal()" style="margin-top: 20px;">Close</button>';
                    
                    document.getElementById('modalContent').innerHTML = relatedHtml;
                    document.getElementById('contextModal').style.display = 'block';
                })
                .catch(error => {
                    alert(`❌ Error loading related tasks: ${error}`);
                });
        }
        
        function closeModal() {
            document.getElementById('contextModal').style.display = 'none';
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('contextModal');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
        
        function completeTask(taskId) {
            const message = prompt(`Complete task '${taskId}'\\n\\nOptional commit message:`);
            if (message === null) return; // User cancelled
            
            fetch('/api/complete_task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_id: taskId, message: message || ''})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`✅ Task '${taskId}' completed and committed to git!`);
                    location.reload();
                } else {
                    alert(`❌ Error completing task: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`❌ Network error: ${error}`);
            });
        }
        
        function blockTask(taskId) {
            const reason = prompt(`Block task '${taskId}'\\n\\nReason for blocking:`);
            if (!reason) return;
            
            fetch('/api/block_task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_id: taskId, reason: reason})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`🚫 Task '${taskId}' blocked successfully!`);
                    location.reload();
                } else {
                    alert(`❌ Error blocking task: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`❌ Network error: ${error}`);
            });
        }
        </script>
    </body>
    </html>
    """