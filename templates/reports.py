"""
Reports template - Complete implementation for Claude handoff generation
"""

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
                <h1>🤖 {{ project_name }}</h1>
                <div class="domain-badge">🌐 AI Project Assistant • {{ domain }}</div>
                <div class="nav">
                    <a href="/">📊 Dashboard</a>
                    <a href="/tasks">📋 Tasks</a>
                    <a href="/phases">📁 Phases</a>
                    <a href="/manage">⚙️ Manage</a>
                    <a href="/generator">🏗️ Generator</a>
                    <a href="/reports" class="active">📈 Reports</a>
                    <a href="/config">⚙️ Config</a>
                    <a href="/help">❓ Help</a>
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