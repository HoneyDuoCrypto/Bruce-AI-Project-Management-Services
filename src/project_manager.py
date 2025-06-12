#!/usr/bin/env python3
"""
Project Discovery and Management for Bruce
Handles multiple project discovery, registration, and switching
Save as: src/project_manager.py
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

class ProjectManager:
    def __init__(self, bruce_home: Path = None):
        """
        Initialize ProjectManager
        
        Args:
            bruce_home: Directory where Bruce system files are stored (defaults to ~/.bruce)
        """
        if bruce_home is None:
            bruce_home = Path.home() / '.bruce'
        
        self.bruce_home = bruce_home
        self.bruce_home.mkdir(exist_ok=True)
        
        # Project registry file
        self.registry_file = self.bruce_home / 'projects.json'
        self.settings_file = self.bruce_home / 'settings.json'
        
        # Load project registry
        self.projects = self._load_project_registry()
        self.settings = self._load_settings()
    
    def _load_project_registry(self) -> Dict[str, Dict[str, Any]]:
        """Load the project registry from disk"""
        if not self.registry_file.exists():
            return {}
        
        try:
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load project registry: {e}")
            return {}
    
    def _save_project_registry(self):
        """Save the project registry to disk"""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.projects, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save project registry: {e}")
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load Bruce settings"""
        if not self.settings_file.exists():
            return {'current_project': None, 'scan_paths': []}
        
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load settings: {e}")
            return {'current_project': None, 'scan_paths': []}
    
    def _save_settings(self):
        """Save Bruce settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save settings: {e}")
    
    def discover_projects(self, scan_paths: List[str] = None) -> List[Dict[str, Any]]:
        """
        Discover Bruce projects by scanning for bruce.yaml files
        
        Args:
            scan_paths: List of paths to scan (defaults to common project locations)
        
        Returns:
            List of discovered project info dictionaries
        """
        if scan_paths is None:
            # Default scan paths
            scan_paths = [
                str(Path.home() / 'Projects'),
                str(Path.home() / 'Development'),
                str(Path.home() / 'projects'),
                str(Path.home() / 'dev'),
                str(Path.home() / 'workspace'),
                str(Path.cwd().parent),  # Parent of current directory
                str(Path.cwd()),         # Current directory
            ]
            
            # Add user-configured scan paths
            scan_paths.extend(self.settings.get('scan_paths', []))
        
        discovered = []
        scanned_paths = set()  # Avoid duplicates
        
        for scan_path in scan_paths:
            try:
                scan_dir = Path(scan_path).expanduser().resolve()
                
                if not scan_dir.exists() or scan_dir in scanned_paths:
                    continue
                
                scanned_paths.add(scan_dir)
                
                # Look for bruce.yaml files
                for bruce_config in scan_dir.rglob('bruce.yaml'):
                    try:
                        project_root = bruce_config.parent
                        project_info = self._analyze_project(project_root)
                        
                        if project_info:
                            discovered.append(project_info)
                            
                    except Exception as e:
                        print(f"Warning: Error analyzing {bruce_config}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Warning: Error scanning {scan_path}: {e}")
                continue
        
        return discovered
    
    def _analyze_project(self, project_root: Path) -> Optional[Dict[str, Any]]:
        """
        Analyze a Bruce project and extract metadata
        
        Args:
            project_root: Path to project directory
        
        Returns:
            Project info dictionary or None if invalid
        """
        bruce_config = project_root / 'bruce.yaml'
        
        if not bruce_config.exists():
            return None
        
        try:
            # Load project configuration
            with open(bruce_config, 'r') as f:
                config = yaml.safe_load(f)
            
            if not config or 'project' not in config:
                return None
            
            project_config = config['project']
            
            # Count tasks and phases
            tasks_count = 0
            phases_count = 0
            
            # Check phases directory
            phases_dir = project_root / config.get('bruce', {}).get('phases_dir', 'phases')
            if phases_dir.exists():
                phase_files = list(phases_dir.glob('phase*_*.yml'))
                phases_count = len(phase_files)
                
                # Count tasks in phase files
                for phase_file in phase_files:
                    try:
                        with open(phase_file, 'r') as f:
                            phase_data = yaml.safe_load(f)
                            if phase_data and 'tasks' in phase_data:
                                tasks_count += len(phase_data['tasks'])
                    except:
                        continue
            
            # Check legacy tasks.yaml
            tasks_file = project_root / config.get('bruce', {}).get('tasks_file', 'tasks.yaml')
            if tasks_file.exists():
                try:
                    with open(tasks_file, 'r') as f:
                        tasks_data = yaml.safe_load(f)
                        if tasks_data and 'tasks' in tasks_data:
                            tasks_count += len(tasks_data['tasks'])
                except:
                    pass
            
            # Get last modified time
            last_modified = max(
                bruce_config.stat().st_mtime,
                phases_dir.stat().st_mtime if phases_dir.exists() else 0
            )
            
            project_id = f"{project_config.get('name', project_root.name)}_{project_root}"
            
            return {
                'id': project_id,
                'name': project_config.get('name', project_root.name),
                'description': project_config.get('description', ''),
                'type': project_config.get('type', 'unknown'),
                'path': str(project_root),
                'config_file': str(bruce_config),
                'tasks_count': tasks_count,
                'phases_count': phases_count,
                'last_modified': datetime.fromtimestamp(last_modified).isoformat(),
                'created': project_config.get('created'),
                'version': config.get('bruce', {}).get('version', '1.0'),
                'web_ui': config.get('web_ui', {}),
                'discovered_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Warning: Error analyzing project at {project_root}: {e}")
            return None
    
    def register_project(self, project_info: Dict[str, Any]) -> bool:
        """
        Register a project in the registry
        
        Args:
            project_info: Project information dictionary
        
        Returns:
            True if registered successfully
        """
        try:
            project_id = project_info['id']
            self.projects[project_id] = project_info
            self._save_project_registry()
            return True
        except Exception as e:
            print(f"Error registering project: {e}")
            return False
    
    def unregister_project(self, project_id: str) -> bool:
        """Remove a project from the registry"""
        try:
            if project_id in self.projects:
                del self.projects[project_id]
                self._save_project_registry()
                return True
            return False
        except Exception as e:
            print(f"Error unregistering project: {e}")
            return False
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project info by ID"""
        return self.projects.get(project_id)
    
    def get_project_by_path(self, project_path: str) -> Optional[Dict[str, Any]]:
        """Get project info by path"""
        project_path = str(Path(project_path).resolve())
        
        for project in self.projects.values():
            if Path(project['path']).resolve() == Path(project_path):
                return project
        return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """Get all registered projects"""
        return list(self.projects.values())
    
    def refresh_projects(self) -> int:
        """
        Refresh project registry by re-discovering all projects
        
        Returns:
            Number of projects found
        """
        discovered = self.discover_projects()
        
        # Update registry with discovered projects
        for project_info in discovered:
            self.register_project(project_info)
        
        # Remove projects that no longer exist
        existing_projects = list(self.projects.keys())
        for project_id in existing_projects:
            project = self.projects[project_id]
            if not Path(project['path']).exists():
                print(f"Removing missing project: {project['name']}")
                self.unregister_project(project_id)
        
        return len(self.projects)
    
    def set_current_project(self, project_id: str) -> bool:
        """Set the current active project"""
        if project_id in self.projects or project_id is None:
            self.settings['current_project'] = project_id
            self._save_settings()
            return True
        return False
    
    def get_current_project(self) -> Optional[Dict[str, Any]]:
        """Get the current active project"""
        current_id = self.settings.get('current_project')
        if current_id:
            return self.projects.get(current_id)
        return None
    
    def add_scan_path(self, path: str) -> bool:
        """Add a path to the scan paths list"""
        try:
            if 'scan_paths' not in self.settings:
                self.settings['scan_paths'] = []
            
            path = str(Path(path).expanduser().resolve())
            if path not in self.settings['scan_paths']:
                self.settings['scan_paths'].append(path)
                self._save_settings()
                return True
            return False
        except Exception as e:
            print(f"Error adding scan path: {e}")
            return False
    
    def remove_scan_path(self, path: str) -> bool:
        """Remove a path from the scan paths list"""
        try:
            if 'scan_paths' not in self.settings:
                return False
            
            path = str(Path(path).expanduser().resolve())
            if path in self.settings['scan_paths']:
                self.settings['scan_paths'].remove(path)
                self._save_settings()
                return True
            return False
        except Exception as e:
            print(f"Error removing scan path: {e}")
            return False
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get detailed status for a project"""
        project = self.get_project(project_id)
        if not project:
            return {'error': 'Project not found'}
        
        try:
            # Re-analyze the project for current status
            current_info = self._analyze_project(Path(project['path']))
            if current_info:
                # Update registry with current info
                self.register_project(current_info)
                return current_info
            else:
                return {'error': 'Project analysis failed'}
        except Exception as e:
            return {'error': f'Status check failed: {e}'}

# Utility functions for CLI integration
def get_project_manager() -> ProjectManager:
    """Get a ProjectManager instance"""
    return ProjectManager()

def discover_and_register_projects() -> int:
    """Discover and register all Bruce projects"""
    pm = get_project_manager()
    return pm.refresh_projects()

def list_available_projects() -> List[Dict[str, Any]]:
    """List all available Bruce projects"""
    pm = get_project_manager()
    return pm.list_projects()

def switch_to_project(project_id: str) -> bool:
    """Switch to a specific project"""
    pm = get_project_manager()
    return pm.set_current_project(project_id)

def get_current_project_info() -> Optional[Dict[str, Any]]:
    """Get current project information"""
    pm = get_project_manager()
    return pm.get_current_project()

if __name__ == "__main__":
    # Demo/testing
    pm = ProjectManager()
    
    print("🔍 Discovering Bruce projects...")
    projects = pm.discover_projects()
    
    print(f"Found {len(projects)} projects:")
    for project in projects:
        print(f"  📁 {project['name']} ({project['tasks_count']} tasks, {project['phases_count']} phases)")
        print(f"     Path: {project['path']}")
        pm.register_project(project)
    
    print(f"\n📋 Registry now contains {len(pm.projects)} projects")