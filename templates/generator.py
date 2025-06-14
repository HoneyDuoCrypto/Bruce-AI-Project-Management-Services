"""
Blueprint generator template - Complete implementation
"""

def get_generator_template():
    """Returns the complete blueprint generator HTML template"""
    
    from .styles import get_shared_styles
    
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Blueprint Generator - {{ page_title }}</title>
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
                    <a href="/generator" class="active">🏗️ Generator</a>
                    <a href="/reports">📈 Reports</a>
                    <a href="/config">⚙️ Config</a>
                    <a href="/help">❓ Help</a>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="content-section">
                <h2 class="section-title">🏗️ Blueprint Generator</h2>
                <p style="color: #ccc; margin-bottom: 20px;">Generate comprehensive documentation for Claude session handoffs</p>
                
                <div class="form-group">
                    <label for="phase-select">Select Phase:</label>
                    <select id="phase-select">
                        {% for phase_id in phase_progress.keys()|sort %}
                            {% set progress = phase_progress[phase_id] %}
                            {% set selected = 'selected' if phase_id|string == selected_phase else '' %}
                            {% set status_emoji = "✅" if progress.percentage == 100 else "🔄" if progress.completed > 0 else "⏳" %}
                            <option value="{{ phase_id }}" {{ selected }}>{{ status_emoji }} Phase {{ phase_id }}: {{ progress.name }} ({{ "%.0f"|format(progress.percentage) }}%)</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            
            <div class="generator-grid">
                <div class="generator-card">
                    <div class="card-title">📋 Phase Blueprint</div>
                    <div class="card-description">Complete technical blueprint with tasks, architecture, and progress for the selected phase</div>
                    <button class="btn btn-primary" onclick="generateDocument('phase')" style="width: 100%;">🏗️ Generate Phase Blueprint</button>
                </div>
                
                <div class="generator-card">
                    <div class="card-title">🤝 Session Handoff</div>
                    <div class="card-description">Comprehensive handoff document for new Claude sessions with all context needed</div>
                    <button class="btn btn-success" onclick="generateDocument('handoff')" style="width: 100%;">📋 Generate Session Handoff</button>
                </div>
                
                <div class="generator-card">
                    <div class="card-title">🏗️ System Architecture</div>
                    <div class="card-description">Current system architecture analysis with component connections and data flows</div>
                    <button class="btn btn-info" onclick="generateDocument('architecture')" style="width: 100%;">🏗️ Generate Architecture Map</button>
                </div>
            </div>
            
            <div class="content-section">
                <h2 class="section-title">📊 Generation Controls</h2>
                <div style="text-align: center; margin: 20px 0;">
                    <button class="btn btn-warning" onclick="copyToClipboard()">📋 Copy Generated Content</button>
                    <button class="btn btn-secondary" onclick="downloadAsFile()">💾 Download as File</button>
                    <button class="btn btn-info" onclick="viewSavedFiles()">📁 View Saved Files</button>
                </div>
                
                <div id="status-message"></div>
            </div>
            
            <div class="content-section">
                <h2 class="section-title">📄 Generated Content</h2>
                <div id="generated-content" class="report-area">
Select a blueprint type above to generate comprehensive documentation...

🏗️ Phase Blueprint: Complete technical overview of the selected phase
🤝 Session Handoff: Everything needed for Claude session continuity  
🏗️ System Architecture: Technical component mapping and data flows

Generated documents are automatically saved to docs/blueprints/ for future reference.
                </div>
            </div>
        </div>
        
        <script>
        let currentContent = '';
        let currentFilename = '';
        
        function generateDocument(docType) {
            const phaseId = document.getElementById('phase-select').value;
            
            showMessage(`Generating ${docType} documentation...`, 'info');
            
            const requestData = {
                type: docType,
                phase_id: parseInt(phaseId)
            };
            
            fetch('/api/generate_blueprint', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentContent = data.content;
                    currentFilename = data.filename || data.filepath || `${docType}_${phaseId}.md`;
                    
                    document.getElementById('generated-content').textContent = currentContent;
                    showMessage(`✅ ${docType} documentation generated successfully!`, 'success');
                    
                    if (data.filepath) {
                        showMessage(`💾 Saved to: ${data.filepath}`, 'info');
                    }
                } else {
                    showMessage(`❌ Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error}`, 'error');
            });
        }
        
        function copyToClipboard() {
            if (!currentContent) {
                showMessage('Generate content first before copying', 'error');
                return;
            }
            
            navigator.clipboard.writeText(currentContent).then(() => {
                showMessage('📋 Content copied to clipboard! Ready for Claude handoff.', 'success');
            }).catch(() => {
                showMessage('❌ Failed to copy to clipboard', 'error');
            });
        }
        
        function downloadAsFile() {
            if (!currentContent) {
                showMessage('Generate content first before downloading', 'error');
                return;
            }
            
            const blob = new Blob([currentContent], { type: 'text/markdown' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = currentFilename || 'blueprint.md';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showMessage(`💾 Downloaded: ${a.download}`, 'success');
        }
        
        function viewSavedFiles() {
            showMessage('📁 Generated files are saved to: docs/blueprints/ and docs/sessions/', 'info');
        }
        
        function showMessage(message, type) {
            const statusDiv = document.getElementById('status-message');
            statusDiv.innerHTML = `<div class="status-message status-${type}">${message}</div>`;
            
            if (type === 'success' || type === 'info') {
                setTimeout(() => {
                    statusDiv.innerHTML = '';
                }, 5000);
            }
        }
        </script>
    </body>
    </html>
    """