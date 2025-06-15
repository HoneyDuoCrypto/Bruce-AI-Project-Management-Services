"""
Bruce Templates Package - FIXED VERSION
Modular HTML templates for Bruce Project Management System

This package contains all the HTML templates for the Bruce web interface,
separated from the Python logic for easier maintenance and development.

FIXED: Template imports and error handling for better reliability
"""

# Safe template imports with error handling
try:
    from .dashboard import get_dashboard_template
except ImportError:
    print("Warning: dashboard template not found")
    get_dashboard_template = lambda: "<html><body>Dashboard template error</body></html>"

try:
    from .tasks import get_tasks_template
except ImportError:
    print("Warning: tasks template not found")
    get_tasks_template = lambda: "<html><body>Tasks template error</body></html>"

try:
    from .phases import get_phases_template
except ImportError:
    print("Warning: phases template not found")
    get_phases_template = lambda: "<html><body>Phases template error</body></html>"

try:
    from .manage import get_manage_template
except ImportError:
    print("Warning: manage template not found")
    get_manage_template = lambda: "<html><body>Manage template error</body></html>"

try:
    from .generator import get_generator_template
except ImportError:
    print("Warning: generator template not found")
    get_generator_template = lambda: "<html><body>Generator template error</body></html>"

try:
    from .reports import get_reports_template
except ImportError:
    print("Warning: reports template not found")
    get_reports_template = lambda: "<html><body>Reports template error</body></html>"

try:
    from .config import get_config_template
except ImportError:
    print("Warning: config template not found")
    get_config_template = lambda: "<html><body>Config template error</body></html>"

try:
    from .help import get_help_template
except ImportError:
    print("Warning: help template not found")
    get_help_template = lambda: "<html><body>Help template error</body></html>"

try:
    from .styles import get_shared_styles
except ImportError:
    print("Warning: styles not found")
    get_shared_styles = lambda: "/* No styles available */"

__version__ = "2.0.1-bugfixed"
__author__ = "Bruce Project Management System"

# Template registry for dynamic loading with error handling
TEMPLATES = {
    'dashboard': get_dashboard_template,
    'tasks': get_tasks_template,
    'phases': get_phases_template,
    'manage': get_manage_template,
    'generator': get_generator_template,
    'reports': get_reports_template,
    'config': get_config_template,
    'help': get_help_template
}

def get_template(template_name):
    """Get a template by name with error handling"""
    if template_name in TEMPLATES:
        try:
            return TEMPLATES[template_name]()
        except Exception as e:
            print(f"Error loading template {template_name}: {e}")
            return f"<html><body><h1>Template Error</h1><p>Failed to load {template_name}: {e}</p></body></html>"
    else:
        available = list(TEMPLATES.keys())
        return f"<html><body><h1>Template Not Found</h1><p>Template '{template_name}' not found. Available: {available}</p></body></html>"

def list_templates():
    """List all available templates"""
    return list(TEMPLATES.keys())

def template_info():
    """Get information about the template system"""
    return {
        'version': __version__,
        'templates': list_templates(),
        'features': [
            'Modular architecture',
            'Shared styling system',
            'Jinja2 template syntax',
            'Config-driven theming',
            'Enhanced error handling',
            'Multi-project support',
            'Bug fixes applied'
        ]
    }