"""
Bruce Templates Package
Modular HTML templates for Bruce Project Management System

This package contains all the HTML templates for the Bruce web interface,
separated from the Python logic for easier maintenance and development.

Template Structure:
- styles.py: Shared CSS styles for all templates
- dashboard.py: Main dashboard with project stats and phase progress
- tasks.py: Task management with enhanced context and modals
- phases.py: Phase overview and progress tracking
- manage.py: Task/phase management with blueprint import
- generator.py: Blueprint generation interface
- reports.py: Claude handoff report generation
- config.py: Configuration display and management
- help.py: User guide and documentation

Each template follows the pattern:
def get_[page]_template():
    return "<!DOCTYPE html>..."

Templates use Jinja2 syntax for variables and control structures.
All styling is centralized in styles.py and imported by each template.
"""

# Template imports for easy access
from .dashboard import get_dashboard_template
from .tasks import get_tasks_template
from .phases import get_phases_template
from .manage import get_manage_template
from .generator import get_generator_template
from .reports import get_reports_template
from .config import get_config_template
from .help import get_help_template
from .styles import get_shared_styles

__version__ = "2.0.0-modular"
__author__ = "Bruce Project Management System"

# Template registry for dynamic loading
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
    """Get a template by name"""
    if template_name in TEMPLATES:
        return TEMPLATES[template_name]()
    else:
        raise ValueError(f"Template '{template_name}' not found. Available: {list(TEMPLATES.keys())}")

def list_templates():
    """List all available templates"""
    return list(TEMPLATES.keys())

# For backwards compatibility and debugging
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
            'Phase 3 testing ready',
            'Enhanced context support',
            'Blueprint import/export',
            'Multi-project support'
        ]
    }