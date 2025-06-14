"""
Management template - Complete implementation with blueprint import functionality
"""

def get_manage_template():
    """Returns the complete task/phase management HTML template with blueprint import"""
    
    from .styles import get_shared_styles
    
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Task & Phase Management - {{ page_title }}</title>
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
                    <a href="/manage" class="active">⚙️ Manage</a>
                    <a href="/generator">🏗️ Generator</a>
                    <a href="/reports">📈 Reports</a>
                    <a href="/config">⚙️ Config</a>
                    <a href="/help">❓ Help</a>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="content-section">
                <h2 class="section-title">⚙️ Task & Phase Management</h2>
                <p style="color: #ccc; margin-bottom: 20px;">Add new phases, create tasks, edit existing items, and import blueprints</p>
                
                <div class="management-tabs">
                    <button class="tab active" onclick="switchTab('add-task')">➕ Add Task</button>
                    <button class="tab" onclick="switchTab('add-phase')">📁 Add Phase</button>
                    <button class="tab" onclick="switchTab('edit-task')">✏️ Edit Task</button>
                    <button class="tab" onclick="switchTab('import-blueprint')">📥 Import Blueprint</button>
                </div>
                
                <!-- Add Task Tab -->
                <div id="add-task" class="tab-content active">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 20px;">➕ Add New Task</h3>
                    
                    <form id="add-task-form">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="task-phase">Phase:</label>
                                <select id="task-phase" required>
                                    <option value="">Select Phase...</option>
                                    {% for phase_id in phase_progress.keys()|sort %}
                                        {% set progress = phase_progress[phase_id] %}
                                        <option value="{{ phase_id }}">Phase {{ phase_id }}: {{ progress.name }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="task-id">Task ID:</label>
                                <input type="text" id="task-id" required placeholder="e.g., trading-engine-core">
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="task-description">Description:</label>
                            <textarea id="task-description" rows="3" required placeholder="What needs to be implemented?"></textarea>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="task-output">Expected Output:</label>
                                <input type="text" id="task-output" placeholder="e.g., src/trading_engine.py with core functionality">
                            </div>
                            <div class="form-group">
                                <label for="task-tests">Test File:</label>
                                <input type="text" id="task-tests" placeholder="e.g., tests/test_trading_engine.py">
                            </div>
                        </div>
                        
                        <div class="dynamic-fields">
                            <label style="color: {{ theme_color }}; font-weight: bold;">Context Files:</label>
                            <div id="context-fields">
                                <div class="field-row">
                                    <input type="text" placeholder="e.g., docs/architecture.md">
                                    <button type="button" class="remove-btn" onclick="removeField(this)">✖</button>
                                </div>
                            </div>
                            <button type="button" class="add-btn" onclick="addContextField()">➕ Add Context File</button>
                        </div>
                        
                        <div class="dynamic-fields">
                            <label style="color: {{ theme_color }}; font-weight: bold;">Dependencies:</label>
                            <div id="dependency-fields">
                                <div class="field-row">
                                    <input type="text" placeholder="e.g., other-task-id">
                                    <button type="button" class="remove-btn" onclick="removeField(this)">✖</button>
                                </div>
                            </div>
                            <button type="button" class="add-btn" onclick="addDependencyField()">➕ Add Dependency</button>
                        </div>
                        
                        <div class="dynamic-fields">
                            <label style="color: {{ theme_color }}; font-weight: bold;">Acceptance Criteria:</label>
                            <div id="criteria-fields">
                                <div class="field-row">
                                    <input type="text" placeholder="e.g., Handles 1000+ requests per second">
                                    <button type="button" class="remove-btn" onclick="removeField(this)">✖</button>
                                </div>
                            </div>
                            <button type="button" class="add-btn" onclick="addCriteriaField()">➕ Add Criteria</button>
                        </div>
                        
                        <div style="margin-top: 30px; text-align: center;">
                            <button type="submit" class="btn btn-primary" style="font-size: 16px; padding: 15px 30px;">➕ Create Task</button>
                            <button type="button" class="btn btn-secondary" onclick="clearForm('add-task-form')">🧹 Clear Form</button>
                        </div>
                    </form>
                </div>
                
                <!-- Add Phase Tab -->
                <div id="add-phase" class="tab-content">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 20px;">📁 Add New Phase</h3>
                    
                    <form id="add-phase-form">
                        <div class="form-row-thirds">
                            <div class="form-group">
                                <label for="phase-id">Phase ID:</label>
                                <input type="number" id="phase-id" required min="1" placeholder="e.g., 3">
                            </div>
                            <div class="form-group">
                                <label for="phase-name">Phase Name:</label>
                                <input type="text" id="phase-name" required placeholder="e.g., Trading Bot Core">
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="phase-description">Phase Description:</label>
                            <textarea id="phase-description" rows="4" required placeholder="What will this phase accomplish?"></textarea>
                        </div>
                        
                        <div style="margin-top: 30px; text-align: center;">
                            <button type="submit" class="btn btn-success" style="font-size: 16px; padding: 15px 30px;">📁 Create Phase</button>
                            <button type="button" class="btn btn-secondary" onclick="clearForm('add-phase-form')">🧹 Clear Form</button>
                        </div>
                    </form>
                </div>
                
                <!-- Edit Task Tab -->
                <div id="edit-task" class="tab-content">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 20px;">✏️ Edit Existing Task</h3>
                    
                    <div class="form-group">
                        <label for="edit-task-select">Select Task to Edit:</label>
                        <select id="edit-task-select" onchange="loadTaskForEdit()">
                            <option value="">Choose a task...</option>
                            {% for phase_id in tasks_by_phase.keys()|sort %}
                                {% set phase_name = "Phase " + phase_id|string if phase_id > 0 else "Legacy" %}
                                <optgroup label="{{ phase_name }}">
                                    {% for task in tasks_by_phase[phase_id] %}
                                        {% set status_icons = {'pending': '⏳', 'in-progress': '🔄', 'completed': '✅', 'blocked': '🚫'} %}
                                        {% set status_icon = status_icons.get(task.get('status'), '❓') %}
                                        <option value="{{ task.id }}">{{ status_icon }} {{ task.id }} - {{ task.get("description", "")[:50] }}</option>
                                    {% endfor %}
                                </optgroup>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <form id="edit-task-form" style="display: none;">
                        <div class="form-group">
                            <label for="edit-task-description">Description:</label>
                            <textarea id="edit-task-description" rows="3"></textarea>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="edit-task-output">Expected Output:</label>
                                <input type="text" id="edit-task-output">
                            </div>
                            <div class="form-group">
                                <label for="edit-task-tests">Test File:</label>
                                <input type="text" id="edit-task-tests">
                            </div>
                        </div>
                        
                        <div class="dynamic-fields">
                            <label style="color: {{ theme_color }}; font-weight: bold;">Context Files:</label>
                            <div id="edit-context-fields"></div>
                            <button type="button" class="add-btn" onclick="addEditContextField()">➕ Add Context File</button>
                        </div>
                        
                        <div class="dynamic-fields">
                            <label style="color: {{ theme_color }}; font-weight: bold;">Dependencies:</label>
                            <div id="edit-dependency-fields"></div>
                            <button type="button" class="add-btn" onclick="addEditDependencyField()">➕ Add Dependency</button>
                        </div>
                        
                        <div class="dynamic-fields">
                            <label style="color: {{ theme_color }}; font-weight: bold;">Acceptance Criteria:</label>
                            <div id="edit-criteria-fields"></div>
                            <button type="button" class="add-btn" onclick="addEditCriteriaField()">➕ Add Criteria</button>
                        </div>
                        
                        <div style="margin-top: 30px; text-align: center;">
                            <button type="submit" class="btn btn-warning" style="font-size: 16px; padding: 15px 30px;">✏️ Update Task</button>
                            <button type="button" class="btn btn-secondary" onclick="cancelEdit()">❌ Cancel</button>
                        </div>
                    </form>
                </div>
                
                <!-- Import Blueprint Tab -->
                <div id="import-blueprint" class="tab-content">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 20px;">📥 Import Blueprint</h3>
                    
                    <form id="import-blueprint-form">
                        <div class="form-group">
                            <label for="blueprint-source">Blueprint Source:</label>
                            <select id="blueprint-source" onchange="toggleImportMethod()">
                                <option value="paste">Paste YAML Content</option>
                                <option value="file">Upload File</option>
                            </select>
                        </div>
                        
                        <div id="paste-method" class="form-group">
                            <label for="blueprint-yaml">Blueprint YAML:</label>
                            <textarea id="blueprint-yaml" rows="15" placeholder="Paste your blueprint YAML here...

Example:
phase:
  id: 3
  name: 'Trading Engine'
  description: 'Core trading functionality'

tasks:
  - id: trading-core
    description: 'Implement core trading engine'
    output: 'src/trading_engine.py'
    acceptance_criteria:
      - 'Handles buy/sell orders'
      - 'Real-time price updates'"></textarea>
                        </div>
                        
                        <div id="file-method" class="form-group" style="display: none;">
                            <label for="blueprint-file">Upload Blueprint File:</label>
                            <input type="file" id="blueprint-file" accept=".yaml,.yml" onchange="handleFileUpload()">
                        </div>
                        
                        <div style="margin: 20px 0;">
                            <button type="button" class="btn btn-info" onclick="previewBlueprint()">👁️ Preview Import</button>
                            <button type="button" class="btn btn-secondary" onclick="validateBlueprint()">✅ Validate YAML</button>
                        </div>
                        
                        <div id="preview-area" style="display: none;">
                            <h4 style="color: {{ theme_color }};">Preview:</h4>
                            <div id="preview-content" class="report-area" style="max-height: 300px;"></div>
                            
                            <div style="margin: 20px 0;">
                                <button type="submit" class="btn btn-primary" style="font-size: 16px; padding: 15px 30px;">📥 Import Blueprint</button>
                                <button type="button" class="btn btn-secondary" onclick="clearPreview()">🧹 Clear</button>
                            </div>
                        </div>
                    </form>
                </div>
                
                <div id="status-message" style="margin-top: 20px;"></div>
            </div>
        </div>
        
        <script>
        let allTasks = {{ all_tasks_json|safe }};
        
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        // Blueprint Import Functions
        function toggleImportMethod() {
            const source = document.getElementById('blueprint-source').value;
            const pasteDiv = document.getElementById('paste-method');
            const fileDiv = document.getElementById('file-method');
            
            if (source === 'paste') {
                pasteDiv.style.display = 'block';
                fileDiv.style.display = 'none';
            } else {
                pasteDiv.style.display = 'none';
                fileDiv.style.display = 'block';
            }
            clearPreview();
        }
        
        function handleFileUpload() {
            const fileInput = document.getElementById('blueprint-file');
            const file = fileInput.files[0];
            
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('blueprint-yaml').value = e.target.result;
                    showMessage(`File "${file.name}" loaded successfully`, 'success');
                };
                reader.readAsText(file);
            }
        }
        
        function validateBlueprint() {
            const yamlContent = getBlueprintContent();
            if (!yamlContent) {
                showMessage('Please provide blueprint content first', 'error');
                return;
            }
            
            try {
                // Basic YAML validation (client-side)
                const lines = yamlContent.split('\\n');
                let hasPhase = false;
                let hasTasks = false;
                
                for (const line of lines) {
                    if (line.trim().startsWith('phase:')) hasPhase = true;
                    if (line.trim().startsWith('tasks:')) hasTasks = true;
                }
                
                if (!hasPhase) {
                    showMessage('❌ Blueprint must contain a "phase:" section', 'error');
                    return;
                }
                
                if (!hasTasks) {
                    showMessage('❌ Blueprint must contain a "tasks:" section', 'error');
                    return;
                }
                
                showMessage('✅ Blueprint YAML structure looks valid', 'success');
                
            } catch (error) {
                showMessage(`❌ YAML validation error: ${error}`, 'error');
            }
        }
        
        function getBlueprintContent() {
            const source = document.getElementById('blueprint-source').value;
            
            if (source === 'paste') {
                return document.getElementById('blueprint-yaml').value;
            } else {
                return document.getElementById('blueprint-yaml').value; // File content gets copied here
            }
        }
        
        function previewBlueprint() {
            const yamlContent = getBlueprintContent();
            if (!yamlContent) {
                showMessage('Please provide blueprint content first', 'error');
                return;
            }
            
            showMessage('Parsing blueprint...', 'info');
            
            fetch('/api/preview_blueprint', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({yaml_content: yamlContent})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayPreview(data.preview);
                    document.getElementById('preview-area').style.display = 'block';
                    showMessage(`✅ Found ${data.task_count} tasks to import`, 'success');
                } else {
                    showMessage(`❌ Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error}`, 'error');
            });
        }
        
        function displayPreview(preview) {
            const previewHtml = `
                <h5>Phase: ${preview.phase.name}</h5>
                <p><strong>Description:</strong> ${preview.phase.description}</p>
                <p><strong>Tasks to create:</strong> ${preview.tasks.length}</p>
                
                <h6>Task List:</h6>
                <ul style="margin-left: 20px;">
                    ${preview.tasks.map(task => `
                        <li><strong>${task.id}:</strong> ${task.description}
                            ${task.depends_on ? `<br><small>Dependencies: ${task.depends_on.join(', ')}</small>` : ''}
                        </li>
                    `).join('')}
                </ul>
            `;
            
            document.getElementById('preview-content').innerHTML = previewHtml;
        }
        
        function clearPreview() {
            document.getElementById('preview-area').style.display = 'none';
            document.getElementById('preview-content').innerHTML = '';
        }
        
        // Original task management functions
        function addContextField() {
            const container = document.getElementById('context-fields');
            const div = document.createElement('div');
            div.className = 'field-row';
            div.innerHTML = `
                <input type="text" placeholder="e.g., docs/architecture.md">
                <button type="button" class="remove-btn" onclick="removeField(this)">✖</button>
            `;
            container.appendChild(div);
        }
        
        function addDependencyField() {
            const container = document.getElementById('dependency-fields');
            const div = document.createElement('div');
            div.className = 'field-row';
            div.innerHTML = `
                <input type="text" placeholder="e.g., other-task-id">
                <button type="button" class="remove-btn" onclick="removeField(this)">✖</button>
            `;
            container.appendChild(div);
        }
        
        function addCriteriaField() {
            const container = document.getElementById('criteria-fields');
            const div = document.createElement('div');
            div.className = 'field-row';
            div.innerHTML = `
                <input type="text" placeholder="e.g., Handles 1000+ requests per second">
                <button type="button" class="remove-btn" onclick="removeField(this)">✖</button>
            `;
            container.appendChild(div);
        }
        
        function addEditContextField() {
            const container = document.getElementById('edit-context-fields');
            const div = document.createElement('div');
            div.className = 'field-row';
            div.innerHTML = `
                <input type="text" placeholder="e.g., docs/architecture.md">
                <button type="button" class="remove-btn" onclick="removeField(this)">✖</button>
            `;
            container.appendChild(div);
        }
        
        function addEditDependencyField() {
            const container = document.getElementById('edit-dependency-fields');
            const div = document.createElement('div');
            div.className = 'field-row';
            div.innerHTML = `
                <input type="text" placeholder="e.g., other-task-id">
                <button type="button" class="remove-btn" onclick="removeField(this)">✖</button>
            `;
            container.appendChild(div);
        }
        
        function addEditCriteriaField() {
            const container = document.getElementById('edit-criteria-fields');
            const div = document.createElement('div');
            div.className = 'field-row';
            div.innerHTML = `
                <input type="text" placeholder="e.g., Handles 1000+ requests per second">
                <button type="button" class="remove-btn" onclick="removeField(this)">✖</button>
            `;
            container.appendChild(div);
        }
        
        function removeField(button) {
            button.parentElement.remove();
        }
        
        function collectFieldValues(containerId) {
            const container = document.getElementById(containerId);
            const inputs = container.querySelectorAll('input[type="text"]');
            const values = [];
            inputs.forEach(input => {
                if (input.value.trim()) {
                    values.push(input.value.trim());
                }
            });
            return values;
        }
        
        function clearForm(formId) {
            document.getElementById(formId).reset();
            if (formId === 'add-task-form') {
                document.getElementById('context-fields').innerHTML = `
                    <div class="field-row">
                        <input type="text" placeholder="e.g., docs/architecture.md">
                        <button type="button" class="remove-btn" onclick="removeField(this)">✖</button>
                    </div>
                `;
                document.getElementById('dependency-fields').innerHTML = `
                    <div class="field-row">
                        <input type="text" placeholder="e.g., other-task-id">
                        <button type="button" class="remove-btn" onclick="removeField(this)">✖</button>
                    </div>
                `;
                document.getElementById('criteria-fields').innerHTML = `
                    <div class="field-row">
                        <input type="text" placeholder="e.g., Handles 1000+ requests per second">
                        <button type="button" class="remove-btn" onclick="removeField(this)">✖</button>
                    </div>
                `;
            }
        }
        
        function loadTaskForEdit() {
            const taskId = document.getElementById('edit-task-select').value;
            const form = document.getElementById('edit-task-form');
            
            if (!taskId) {
                form.style.display = 'none';
                return;
            }
            
            const task = allTasks.find(t => t.id === taskId);
            if (!task) {
                showMessage('Task not found', 'error');
                return;
            }
            
            document.getElementById('edit-task-description').value = task.description || '';
            document.getElementById('edit-task-output').value = task.output || '';
            document.getElementById('edit-task-tests').value = task.tests || '';
            
            populateEditFields('edit-context-fields', task.context || [], 'docs/architecture.md');
            populateEditFields('edit-dependency-fields', task.depends_on || [], 'other-task-id');
            populateEditFields('edit-criteria-fields', task.acceptance_criteria || [], 'Handles 1000+ requests per second');
            
            form.style.display = 'block';
        }
        
        function populateEditFields(containerId, values, placeholder) {
            const container = document.getElementById(containerId);
            container.innerHTML = '';
            
            if (values.length === 0) {
                values = [''];
            }
            
            values.forEach(value => {
                const div = document.createElement('div');
                div.className = 'field-row';
                div.innerHTML = `
                    <input type="text" value="${value}" placeholder="e.g., ${placeholder}">
                    <button type="button" class="remove-btn" onclick="removeField(this)">✖</button>
                `;
                container.appendChild(div);
            });
        }
        
        function cancelEdit() {
            document.getElementById('edit-task-select').value = '';
            document.getElementById('edit-task-form').style.display = 'none';
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
        
        // Form submissions
        document.getElementById('add-task-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                phase: parseInt(document.getElementById('task-phase').value),
                id: document.getElementById('task-id').value,
                description: document.getElementById('task-description').value,
                output: document.getElementById('task-output').value,
                tests: document.getElementById('task-tests').value,
                context: collectFieldValues('context-fields'),
                depends_on: collectFieldValues('dependency-fields'),
                acceptance_criteria: collectFieldValues('criteria-fields')
            };
            
            if (!formData.phase || !formData.id || !formData.description) {
                showMessage('Please fill in required fields (Phase, ID, Description)', 'error');
                return;
            }
            
            fetch('/api/add_task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(`✅ Task '${formData.id}' created successfully!`, 'success');
                    clearForm('add-task-form');
                } else {
                    showMessage(`❌ Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error}`, 'error');
            });
        });
        
        document.getElementById('add-phase-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                id: parseInt(document.getElementById('phase-id').value),
                name: document.getElementById('phase-name').value,
                description: document.getElementById('phase-description').value
            };
            
            if (!formData.id || !formData.name || !formData.description) {
                showMessage('Please fill in all fields', 'error');
                return;
            }
            
            fetch('/api/add_phase', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(`✅ Phase ${formData.id} '${formData.name}' created successfully!`, 'success');
                    clearForm('add-phase-form');
                    setTimeout(() => location.reload(), 2000);
                } else {
                    showMessage(`❌ Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error}`, 'error');
            });
        });
        
        document.getElementById('edit-task-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const taskId = document.getElementById('edit-task-select').value;
            if (!taskId) {
                showMessage('No task selected', 'error');
                return;
            }
            
            const formData = {
                id: taskId,
                description: document.getElementById('edit-task-description').value,
                output: document.getElementById('edit-task-output').value,
                tests: document.getElementById('edit-task-tests').value,
                context: collectFieldValues('edit-context-fields'),
                depends_on: collectFieldValues('edit-dependency-fields'),
                acceptance_criteria: collectFieldValues('edit-criteria-fields')
            };
            
            fetch('/api/edit_task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(`✅ Task '${taskId}' updated successfully!`, 'success');
                    cancelEdit();
                } else {
                    showMessage(`❌ Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error}`, 'error');
            });
        });
        
        // Import Blueprint form submission
        document.getElementById('import-blueprint-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const yamlContent = getBlueprintContent();
            if (!yamlContent) {
                showMessage('Please provide blueprint content first', 'error');
                return;
            }
            
            if (!confirm('Import this blueprint? This will create all tasks shown in the preview.')) {
                return;
            }
            
            showMessage('Importing blueprint...', 'info');
            
            fetch('/api/import_blueprint', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({yaml_content: yamlContent})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(`✅ Successfully imported ${data.imported_count} tasks!`, 'success');
                    document.getElementById('import-blueprint-form').reset();
                    clearPreview();
                    
                    // Offer to redirect to tasks page
                    setTimeout(() => {
                        if (confirm('Blueprint imported successfully! Go to Tasks page to see the new tasks?')) {
                            window.location.href = '/tasks';
                        }
                    }, 2000);
                } else {
                    showMessage(`❌ Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error}`, 'error');
            });
        });
        </script>
    </body>
    </html>
    """