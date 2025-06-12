#!/usr/bin/env python3
"""
Bruce Configuration Manager
Handles loading and managing bruce.yaml configuration files
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ProjectConfig:
    """Project-specific configuration"""
    name: str = "Bruce Project"
    description: str = "AI-assisted project management"
    type: str = "general"
    author: str = "Bruce User"
    
@dataclass 
class BruceConfig:
    """Bruce system configuration"""
    contexts_dir: str = "contexts"
    blueprints_dir: str = "docs/blueprints"
    phases_dir: str = "phases"
    reports_dir: str = "claude_reports"
    tasks_file: str = "tasks.yaml"
    
@dataclass
class UIConfig:
    """UI customization configuration"""
    title: str = None  # Will default to project name
    theme_color: str = "#00d4aa"  # Bruce teal
    domain: str = "bruce.honey-duo.com"
    port: int = 5000


class ConfigManager:
    """Manages Bruce configuration loading and defaults"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.config_data = None
        self.project = ProjectConfig()
        self.bruce = BruceConfig()
        self.ui = UIConfig()
        
        # Load configuration
        self._load_config()
    
    def _find_config_file(self) -> Optional[Path]:
        """Find bruce.yaml in current directory or .bruce/ subdirectory"""
        # Check for bruce.yaml in project root
        config_file = self.project_root / "bruce.yaml"
        if config_file.exists():
            return config_file
        
        # Check for config.yaml in .bruce/ directory
        bruce_dir = self.project_root / ".bruce"
        config_file = bruce_dir / "config.yaml"
        if config_file.exists():
            return config_file
        
        return None
    
    def _load_config(self):
        """Load configuration from file or use defaults"""
        config_file = self._find_config_file()
        
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    self.config_data = yaml.safe_load(f)
                
                # Parse project config
                if 'project' in self.config_data:
                    project_data = self.config_data['project']
                    self.project = ProjectConfig(
                        name=project_data.get('name', self.project.name),
                        description=project_data.get('description', self.project.description),
                        type=project_data.get('type', self.project.type),
                        author=project_data.get('author', self.project.author)
                    )
                
                # Parse Bruce config
                if 'bruce' in self.config_data:
                    bruce_data = self.config_data['bruce']
                    self.bruce = BruceConfig(
                        contexts_dir=bruce_data.get('contexts_dir', self.bruce.contexts_dir),
                        blueprints_dir=bruce_data.get('blueprints_dir', self.bruce.blueprints_dir),
                        phases_dir=bruce_data.get('phases_dir', self.bruce.phases_dir),
                        reports_dir=bruce_data.get('reports_dir', self.bruce.reports_dir),
                        tasks_file=bruce_data.get('tasks_file', self.bruce.tasks_file)
                    )
                
                # Parse UI config
                if 'ui' in self.config_data:
                    ui_data = self.config_data['ui']
                    self.ui = UIConfig(
                        title=ui_data.get('title', self.project.name),
                        theme_color=ui_data.get('theme_color', self.ui.theme_color),
                        domain=ui_data.get('domain', self.ui.domain),
                        port=ui_data.get('port', self.ui.port)
                    )
                
                # Set UI title default if not specified
                if self.ui.title is None:
                    self.ui.title = self.project.name
                    
                print(f"📋 Loaded config from: {config_file.name}")
                
            except Exception as e:
                print(f"⚠️  Error loading config from {config_file}: {e}")
                print("📋 Using default configuration")
        else:
            print("📋 No config file found, using defaults")
    
    def get_absolute_path(self, relative_path: str) -> Path:
        """Convert relative path from config to absolute path"""
        return self.project_root / relative_path
    
    def get_contexts_dir(self) -> Path:
        """Get absolute path to contexts directory"""
        return self.get_absolute_path(self.bruce.contexts_dir)
    
    def get_blueprints_dir(self) -> Path:
        """Get absolute path to blueprints directory"""
        return self.get_absolute_path(self.bruce.blueprints_dir)
    
    def get_phases_dir(self) -> Path:
        """Get absolute path to phases directory"""
        return self.get_absolute_path(self.bruce.phases_dir)
    
    def get_reports_dir(self) -> Path:
        """Get absolute path to reports directory"""
        return self.get_absolute_path(self.bruce.reports_dir)
    
    def get_tasks_file(self) -> Path:
        """Get absolute path to tasks file"""
        return self.get_absolute_path(self.bruce.tasks_file)
    
    def create_default_config(self, config_path: Optional[Path] = None) -> Path:
        """Create a default bruce.yaml config file"""
        if config_path is None:
            config_path = self.project_root / "bruce.yaml"
        
        # Create default configuration
        default_config = {
            'project': asdict(self.project),
            'bruce': asdict(self.bruce),
            'ui': asdict(self.ui)
        }
        
        # Add comments for clarity
        config_content = f"""# Bruce Project Configuration
# Generated on {Path.cwd().name}

project:
  name: "{self.project.name}"
  description: "{self.project.description}"
  type: "{self.project.type}"
  author: "{self.project.author}"

bruce:
  # Directory structure (relative to project root)
  contexts_dir: "{self.bruce.contexts_dir}"
  blueprints_dir: "{self.bruce.blueprints_dir}"
  phases_dir: "{self.bruce.phases_dir}"
  reports_dir: "{self.bruce.reports_dir}"
  
  # Task configuration
  tasks_file: "{self.bruce.tasks_file}"

ui:
  # Web interface customization
  title: "{self.ui.title}"
  theme_color: "{self.ui.theme_color}"
  domain: "{self.ui.domain}"
  port: {self.ui.port}

# Bruce Version: 1.0-portable
"""
        
        # Create directories if they don't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write configuration file
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Created default config: {config_path}")
        return config_path
    
    def validate_config(self) -> bool:
        """Validate that all configured directories exist or can be created"""
        try:
            # Ensure all directories exist
            self.get_contexts_dir().mkdir(parents=True, exist_ok=True)
            self.get_blueprints_dir().mkdir(parents=True, exist_ok=True)
            self.get_phases_dir().mkdir(parents=True, exist_ok=True)
            self.get_reports_dir().mkdir(parents=True, exist_ok=True)
            
            return True
        except Exception as e:
            print(f"❌ Config validation failed: {e}")
            return False
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get project information for display"""
        return {
            'name': self.project.name,
            'description': self.project.description,
            'type': self.project.type,
            'author': self.project.author,
            'config_loaded': self.config_data is not None,
            'config_file': str(self._find_config_file()) if self._find_config_file() else None
        }
    
    def update_project_config(self, **kwargs):
        """Update project configuration"""
        for key, value in kwargs.items():
            if hasattr(self.project, key):
                setattr(self.project, key, value)
    
    def save_config(self, config_path: Optional[Path] = None):
        """Save current configuration to file"""
        if config_path is None:
            config_path = self._find_config_file() or (self.project_root / "bruce.yaml")
        
        config_data = {
            'project': asdict(self.project),
            'bruce': asdict(self.bruce),
            'ui': asdict(self.ui)
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2, sort_keys=False)
        
        print(f"💾 Saved config to: {config_path}")


def get_config(project_root: Optional[Path] = None) -> ConfigManager:
    """Get global config manager instance"""
    return ConfigManager(project_root)


def main():
    """CLI interface for config management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bruce Configuration Manager")
    parser.add_argument('command', choices=['show', 'create', 'validate', 'set'], 
                       help="Command to execute")
    parser.add_argument('--project-root', type=Path, default=Path.cwd(), 
                       help="Project root directory")
    parser.add_argument('--name', help="Set project name")
    parser.add_argument('--description', help="Set project description")
    parser.add_argument('--type', help="Set project type")
    
    args = parser.parse_args()
    
    config = ConfigManager(args.project_root)
    
    if args.command == 'show':
        print("\n🤖 Bruce Configuration")
        print("=" * 50)
        info = config.get_project_info()
        print(f"Project: {info['name']}")
        print(f"Description: {info['description']}")
        print(f"Type: {info['type']}")
        print(f"Author: {info['author']}")
        print(f"Config File: {info['config_file'] or 'None (using defaults)'}")
        print(f"Config Loaded: {info['config_loaded']}")
        
        print(f"\n📁 Directories:")
        print(f"Contexts: {config.get_contexts_dir()}")
        print(f"Blueprints: {config.get_blueprints_dir()}")
        print(f"Phases: {config.get_phases_dir()}")
        print(f"Reports: {config.get_reports_dir()}")
        
        print(f"\n🌐 UI Settings:")
        print(f"Title: {config.ui.title}")
        print(f"Theme: {config.ui.theme_color}")
        print(f"Domain: {config.ui.domain}")
        print(f"Port: {config.ui.port}")
    
    elif args.command == 'create':
        config_file = config.create_default_config()
        print(f"✅ Created config file: {config_file}")
        print("💡 Edit the file to customize your project settings")
    
    elif args.command == 'validate':
        if config.validate_config():
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration validation failed")
    
    elif args.command == 'set':
        updates = {}
        if args.name:
            updates['name'] = args.name
        if args.description:
            updates['description'] = args.description
        if args.type:
            updates['type'] = args.type
        
        if updates:
            config.update_project_config(**updates)
            config.save_config()
            print(f"✅ Updated project config: {list(updates.keys())}")
        else:
            print("⚠️  No updates specified")


if __name__ == "__main__":
    main()