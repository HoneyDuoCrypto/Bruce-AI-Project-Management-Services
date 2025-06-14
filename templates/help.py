"""
Help template - Complete implementation with blueprint import documentation
"""

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
                <h1>🤖 {{ project_name }}</h1>
                <div class="domain-badge">🌐 AI Project Assistant • {{ domain }}</div>
                <div class="nav">
                    <a href="/">📊 Dashboard</a>
                    <a href="/tasks">📋 Tasks</a>
                    <a href="/phases">📁 Phases</a>
                    <a href="/manage">⚙️ Manage</a>
                    <a href="/generator">🏗️ Generator</a>
                    <a href="/reports">📈 Reports</a>
                    <a href="/config">⚙️ Config</a>
                    <a href="/help" class="active">❓ Help</a>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="content-section">
                <h2 class="section-title">📖 Bruce User Guide - Complete with Blueprint Import</h2>
                
                <div class="help-section">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">🆕 What's New: Blueprint Import</h3>
                    <ul style="margin-left: 20px; line-height: 1.8; color: #ccc;">
                        <li><strong>Design-First Workflow:</strong> Plan entire phases before implementation</li>
                        <li><strong>Bulk Task Creation:</strong> Import multiple related tasks at once</li>
                        <li><strong>YAML Blueprint Format:</strong> Structured, readable phase definitions</li>
                        <li><strong>Preview Before Import:</strong> See exactly what will be created</li>
                        <li><strong>Dependency Mapping:</strong> Automatic task relationship setup</li>
                    </ul>
                </div>
                
                <div class="help-section">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">📥 How to Use Blueprint Import</h3>
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
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">🎯 Enhanced Workflow with Blueprint Import</h3>
                    <div class="workflow-step">
                        <h4>1. Plan Phase</h4>
                        <p>Design entire phase structure in YAML format. Think through all tasks, dependencies, and acceptance criteria before starting implementation.</p>
                    </div>
                    <div class="workflow-step">
                        <h4>2. Import Tasks</h4>
                        <p>Use blueprint import to create all tasks instantly. Preview functionality lets you see exactly what will be created.</p>
                    </div>
                    <div class="workflow-step">
                        <h4>3. Manage Dependencies</h4>
                        <p>Tasks automatically linked based on blueprint dependencies. No manual dependency setup required.</p>
                    </div>
                    <div class="workflow-step">
                        <h4>4. Start Development</h4>
                        <p>Begin work with enhanced context and clear structure. All tasks have detailed descriptions and acceptance criteria.</p>
                    </div>
                    <div class="workflow-step">
                        <h4>5. Track Progress</h4>
                        <p>Monitor phase completion with visual progress bars. Generate blueprints and handoff reports as you progress.</p>
                    </div>
                </div>
                
                <div class="tip-box">
                    <h4>🎯 Pro Tip: Blueprint Templates</h4>
                    <p>Create blueprint templates for common project patterns! Save YAML blueprints for "Web App Setup", "API Development", "Database Design" phases and reuse them across projects. This makes starting new phases incredibly fast.</p>
                </div>
                
                <div class="tip-box">
                    <h4>💡 Pro Tip: Data Migration Projects</h4>
                    <p>Perfect for your data organization work! Create blueprints for common data migration patterns: "Extract Phase", "Transform Phase", "Load Phase". Each blueprint can include tasks for validation, cleanup, and verification steps.</p>
                </div>
                
                <div class="help-section">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">🔧 Phase 3 Testing Features</h3>
                    <ul style="margin-left: 20px; line-height: 1.8; color: #ccc;">
                        <li><strong>Stress Testing:</strong> Modular UI makes it easy to test with 50+ tasks</li>
                        <li><strong>Multi-Project Support:</strong> Config-driven themes and settings per project</li>
                        <li><strong>Concurrent Users:</strong> Template-based architecture supports multiple sessions</li>
                        <li><strong>Data Isolation:</strong> Clean API boundaries prevent data bleeding</li>
                        <li><strong>Performance Monitoring:</strong> Health check endpoints for system monitoring</li>
                    </ul>
                </div>
                
                <div class="help-section">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">🚀 Quick Reference Commands</h3>
                    <div class="code-block">
# CLI Commands
bruce init "My Project"           # Initialize new Bruce project
bruce status                      # Show project status
bruce list                        # List all tasks
bruce start task-id               # Start task with enhanced context
bruce commit task-id              # Complete and commit task
bruce phases                      # Show phase progress
bruce ui                          # Start web interface

# Web Interface
Dashboard: Project stats and phase progress
Tasks: Enhanced task management with context modals
Manage: Add tasks, phases, and import blueprints
Generator: Create comprehensive documentation
Reports: Generate Claude handoff reports
Config: View and manage bruce.yaml settings
                    </div>
                </div>
                
                <div class="help-section">
                    <h3 style="color: {{ theme_color }}; margin-bottom: 15px;">📋 Modular Architecture Benefits</h3>
                    <ul style="margin-left: 20px; line-height: 1.8; color: #ccc;">
                        <li><strong>Easier Maintenance:</strong> Each page in its own template file</li>
                        <li><strong>Faster Development:</strong> Change specific pages without affecting others</li>
                        <li><strong>Better Testing:</strong> Test individual components in isolation</li>
                        <li><strong>Cleaner Code:</strong> Separation of Python logic and HTML display</li>
                        <li><strong>Collaboration Ready:</strong> Easy to work with ChatGPT on specific templates</li>
                    </ul>
                </div>
                
                <div class="tip-box">
                    <h4>🏗️ System Architecture Ready for Phase 3</h4>
                    <p>The modular template system is specifically designed for your Phase 3 testing goals. Each template handles a specific concern, making it easy to test concurrent users, multi-project scenarios, and large datasets without the UI becoming a bottleneck.</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="/" class="btn btn-primary">🏠 Back to Dashboard</a>
                    <a href="/manage" class="btn btn-success">📥 Try Blueprint Import</a>
                    <a href="/generator" class="btn btn-info">🏗️ Generate Documentation</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """