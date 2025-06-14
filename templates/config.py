"""
Configuration template - Complete implementation for bruce.yaml settings
"""

def get_config_template():
    """Returns the complete configuration HTML template"""
    
    from .styles import get_shared_styles
    
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Configuration - {{ page_title }}</title>
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
                    <a href="/reports">📈 Reports</a>
                    <a href="/config" class="active">⚙️ Config</a>
                    <a href="/help">❓ Help</a>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="content-section">
                <h2 class="section-title">⚙️ Bruce Configuration</h2>
                <p style="color: #ccc; margin-bottom: 20px;">Project configuration and system settings</p>
                
                <div class="config-info">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">📋 Project Information</h3>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Project Name:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff;">
                                {{ project_info.name }}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Project Type:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff;">
                                {{ project_info.type }}
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Description:</label>
                        <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff;">
                            {{ project_info.description }}
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Config File:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {{ project_info.config_file or 'None (using defaults)' }}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Config Status:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff;">
                                {% if project_info.config_loaded %}✅ Loaded from file{% else %}📋 Using defaults{% endif %}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="config-info">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">📁 Directory Structure</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Contexts:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {% if task_manager_config %}{{ task_manager_config.bruce.contexts_dir }}{% else %}contexts{% endif %}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Blueprints:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {% if task_manager_config %}{{ task_manager_config.bruce.blueprints_dir }}{% else %}docs/blueprints{% endif %}
                            </div>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Phases:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {% if task_manager_config %}{{ task_manager_config.bruce.phases_dir }}{% else %}phases{% endif %}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Reports:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {% if task_manager_config %}{{ task_manager_config.bruce.reports_dir }}{% else %}claude_reports{% endif %}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="config-info">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">🎨 UI Settings</h3>
                    <div class="form-row-thirds">
                        <div class="form-group">
                            <label>Theme Color:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                <span style="display: inline-block; width: 20px; height: 20px; background: {{ theme_color }}; border-radius: 3px; margin-right: 10px; vertical-align: middle;"></span>
                                {{ theme_color }}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Domain:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {{ domain }}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Port:</label>
                            <div style="padding: 12px; background: #333; border-radius: 8px; color: #fff; font-family: monospace;">
                                {% if task_manager_config %}{{ task_manager_config.ui.port }}{% else %}5000{% endif %}
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
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">📝 Example bruce.yaml</h3>
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
        function createConfig() {
            if (!confirm('Create a default bruce.yaml configuration file?\\n\\nThis will help make your project portable.')) return;
            
            fetch('/api/create_config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showConfigMessage('✅ Config file created successfully! Reloading...', 'success');
                    setTimeout(() => location.reload(), 2000);
                } else {
                    showConfigMessage('❌ Error: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showConfigMessage('❌ Network error: ' + error, 'error');
            });
        }
        
        function validateConfig() {
            fetch('/api/validate_config')
            .then(response => response.json())
            .then(data => {
                if (data.valid) {
                    showConfigMessage('✅ Configuration is valid! All directories accessible.', 'success');
                } else {
                    showConfigMessage('❌ Configuration validation failed: ' + (data.error || 'Unknown error'), 'error');
                }
            })
            .catch(error => {
                showConfigMessage('❌ Network error: ' + error, 'error');
            });
        }
        
        function showConfigExample() {
            const exampleDiv = document.getElementById('config-example');
            if (exampleDiv.style.display === 'none') {
                exampleDiv.style.display = 'block';
            } else {
                exampleDiv.style.display = 'none';
            }
        }
        
        function showConfigMessage(message, type) {
            document.getElementById('config-status').innerHTML = 
                `<div class="status-message status-${type}" style="margin-top: 20px;">${message}</div>`;
        }
        </script>
    </body>
    </html>
    """