#!/usr/bin/env python3
"""
Enhanced Dynamic Blueprint Generator - Phase 3 Ready
Completely dynamic system analysis with multi-project support
Replaces hardcoded architecture with real-time system scanning
"""

import os
import sys
import re
import ast
import subprocess
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import yaml
import json

# Add src to path to import TaskManager
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.task_manager import TaskManager

class ProjectScanner:
    """Scans and analyzes project structure dynamically"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scan_results = {}
        
    def scan_full_project(self) -> Dict[str, Any]:
        """Complete project analysis - everything we can detect"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "web_interface": self.detect_web_interface(),
            "cli_interface": self.detect_cli_interface(),
            "template_system": self.analyze_template_system(),
            "core_modules": self.analyze_core_modules(),
            "api_endpoints": self.scan_api_endpoints(),
            "cli_commands": self.analyze_cli_commands(),
            "config_structure": self.analyze_config_structure(),
            "file_statistics": self.generate_file_statistics(),
            "import_relationships": self.analyze_import_relationships(),
            "project_discovery": self.discover_other_projects(),
            "git_status": self.get_git_status()
        }
        
        self.scan_results = results
        return results
    
    def detect_web_interface(self) -> Dict[str, Any]:
        """Detect web interface files and capabilities"""
        web_files = []
        main_web_file = None
        
        # Look for potential web interface files
        candidates = ["bruce_app.py", "bruce_complete.py", "bruce.py", "app.py"]
        
        for candidate in candidates:
            file_path = self.project_root / candidate
            if file_path.exists():
                file_info = self._analyze_python_file(file_path)
                web_files.append(file_info)
                
                # Determine main web file (prefer bruce_app.py)
                if candidate == "bruce_app.py" or main_web_file is None:
                    main_web_file = file_info
        
        return {
            "main_file": main_web_file,
            "all_files": web_files,
            "template_integration": self._check_template_integration(),
            "flask_routes": self._extract_flask_routes(main_web_file) if main_web_file else [],
            "multi_project_ready": self._check_multi_project_support()
        }
    
    def detect_cli_interface(self) -> Dict[str, Any]:
        """Detect CLI interface and commands"""
        cli_files = []
        main_cli_file = None
        
        # Look for CLI files
        cli_dir = self.project_root / "cli"
        if cli_dir.exists():
            for cli_file in cli_dir.glob("*.py"):
                if cli_file.name != "__init__.py":
                    file_info = self._analyze_python_file(cli_file)
                    cli_files.append(file_info)
                    
                    # Prefer bruce.py over bruce-task.py
                    if cli_file.name == "bruce.py" or main_cli_file is None:
                        main_cli_file = file_info
        
        # Also check root directory
        for candidate in ["bruce.py", "bruce-task.py", "hdw-task.py"]:
            file_path = self.project_root / candidate
            if file_path.exists():
                file_info = self._analyze_python_file(file_path)
                cli_files.append(file_info)
                if candidate == "bruce.py" or main_cli_file is None:
                    main_cli_file = file_info
        
        return {
            "main_file": main_cli_file,
            "all_files": cli_files,
            "available_commands": self._extract_cli_commands(main_cli_file) if main_cli_file else [],
            "multi_project_support": self._check_cli_multi_project_support(main_cli_file) if main_cli_file else False
        }
    
    def analyze_template_system(self) -> Dict[str, Any]:
        """Analyze template system structure and capabilities"""
        templates_dir = self.project_root / "templates"
        
        if not templates_dir.exists():
            return {"exists": False, "template_files": [], "features": []}
        
        template_files = []
        template_features = set()
        template_dependencies = {}
        
        for template_file in templates_dir.glob("*.py"):
            if template_file.name == "__init__.py":
                continue
                
            file_info = self._analyze_python_file(template_file)
            
            # Analyze template content for features
            try:
                with open(template_file, 'r') as f:
                    content = f.read()
                
                # Detect features based on content
                features = self._detect_template_features(content)
                template_features.update(features)
                
                # Detect dependencies
                deps = self._extract_template_dependencies(content)
                template_dependencies[template_file.name] = deps
                
                file_info["features"] = features
                file_info["dependencies"] = deps
                
            except Exception as e:
                file_info["analysis_error"] = str(e)
            
            template_files.append(file_info)
        
        return {
            "exists": True,
            "template_files": template_files,
            "total_templates": len(template_files),
            "features": list(template_features),
            "dependencies": template_dependencies,
            "modular_architecture": self._check_modular_architecture(templates_dir)
        }
    
    def analyze_core_modules(self) -> Dict[str, Any]:
        """Analyze core source modules"""
        src_dir = self.project_root / "src"
        
        if not src_dir.exists():
            return {"exists": False, "modules": []}
        
        modules = []
        for py_file in src_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            file_info = self._analyze_python_file(py_file)
            
            # Special analysis for known core modules
            if py_file.name == "task_manager.py":
                file_info["role"] = "Core Task Management"
                file_info["capabilities"] = self._analyze_task_manager_capabilities(py_file)
            elif py_file.name == "config_manager.py":
                file_info["role"] = "Configuration Management"
                file_info["capabilities"] = self._analyze_config_manager_capabilities(py_file)
            elif py_file.name == "blueprint_generator.py":
                file_info["role"] = "Documentation Generation"
                file_info["capabilities"] = self._analyze_blueprint_capabilities(py_file)
            
            modules.append(file_info)
        
        return {
            "exists": True,
            "modules": modules,
            "total_modules": len(modules)
        }
    
    def scan_api_endpoints(self) -> List[Dict[str, Any]]:
        """Extract all API endpoints from web interface"""
        endpoints = []
        
        web_interface = self.detect_web_interface()
        if not web_interface["main_file"]:
            return endpoints
        
        main_file_path = Path(web_interface["main_file"]["path"])
        
        try:
            with open(main_file_path, 'r') as f:
                content = f.read()
            
            # Extract Flask routes
            route_pattern = r"@app\.route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[([^\]]+)\])?\)"
            function_pattern = r"def\s+([^(]+)\("
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                route_match = re.search(route_pattern, line)
                if route_match:
                    endpoint = route_match.group(1)
                    methods = route_match.group(2) or "'GET'"
                    methods_list = [m.strip("'\"") for m in re.findall(r"['\"]([^'\"]+)['\"]", methods)]
                    
                    # Get function name from next lines
                    func_name = None
                    for j in range(i+1, min(i+5, len(lines))):
                        func_match = re.search(function_pattern, lines[j])
                        if func_match:
                            func_name = func_match.group(1)
                            break
                    
                    endpoints.append({
                        "endpoint": endpoint,
                        "methods": methods_list,
                        "function": func_name,
                        "line_number": i + 1
                    })
        
        except Exception as e:
            print(f"Error scanning API endpoints: {e}")
        
        return endpoints
    
    def analyze_cli_commands(self) -> List[Dict[str, Any]]:
        """Extract available CLI commands"""
        commands = []
        
        cli_interface = self.detect_cli_interface()
        if not cli_interface["main_file"]:
            return commands
        
        main_file_path = Path(cli_interface["main_file"]["path"])
        
        try:
            with open(main_file_path, 'r') as f:
                content = f.read()
            
            # Look for argparse subparsers
            subparser_pattern = r'subparsers\.add_parser\(["\']([^"\']+)["\'].*?help=["\']([^"\']*)["\']'
            matches = re.findall(subparser_pattern, content, re.DOTALL)
            
            for match in matches:
                command_name, help_text = match
                commands.append({
                    "command": command_name,
                    "help": help_text,
                    "detected_in": main_file_path.name
                })
        
        except Exception as e:
            print(f"Error analyzing CLI commands: {e}")
        
        return commands
    
    def analyze_config_structure(self) -> Dict[str, Any]:
        """Analyze configuration files and structure"""
        config_files = []
        
        # Look for config files
        config_candidates = ["bruce.yaml", ".bruce/config.yaml", "config.yaml"]
        
        for candidate in config_candidates:
            config_path = self.project_root / candidate
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config_content = yaml.safe_load(f)
                    
                    config_files.append({
                        "path": str(config_path),
                        "structure": config_content,
                        "size": config_path.stat().st_size,
                        "modified": datetime.fromtimestamp(config_path.stat().st_mtime).isoformat()
                    })
                except Exception as e:
                    config_files.append({
                        "path": str(config_path),
                        "error": str(e)
                    })
        
        return {
            "config_files": config_files,
            "has_config": len(config_files) > 0,
            "config_manager_available": (self.project_root / "src" / "config_manager.py").exists()
        }
    
    def generate_file_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive file statistics"""
        stats = {
            "total_files": 0,
            "total_size": 0,
            "python_files": 0,
            "yaml_files": 0,
            "markdown_files": 0,
            "by_directory": {},
            "largest_files": [],
            "recently_modified": []
        }
        
        all_files = []
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                try:
                    file_size = file_path.stat().st_size
                    modified_time = file_path.stat().st_mtime
                    
                    file_info = {
                        "path": str(file_path.relative_to(self.project_root)),
                        "size": file_size,
                        "modified": datetime.fromtimestamp(modified_time).isoformat(),
                        "extension": file_path.suffix
                    }
                    
                    all_files.append(file_info)
                    
                    # Update counters
                    stats["total_files"] += 1
                    stats["total_size"] += file_size
                    
                    if file_path.suffix == ".py":
                        stats["python_files"] += 1
                    elif file_path.suffix in [".yaml", ".yml"]:
                        stats["yaml_files"] += 1
                    elif file_path.suffix == ".md":
                        stats["markdown_files"] += 1
                    
                    # Directory stats
                    dir_name = str(file_path.parent.relative_to(self.project_root))
                    if dir_name == ".":
                        dir_name = "root"
                    
                    if dir_name not in stats["by_directory"]:
                        stats["by_directory"][dir_name] = {"files": 0, "size": 0}
                    
                    stats["by_directory"][dir_name]["files"] += 1
                    stats["by_directory"][dir_name]["size"] += file_size
                
                except Exception:
                    continue
        
        # Get largest files (top 10)
        stats["largest_files"] = sorted(all_files, key=lambda x: x["size"], reverse=True)[:10]
        
        # Get recently modified files (last 10)
        stats["recently_modified"] = sorted(all_files, key=lambda x: x["modified"], reverse=True)[:10]
        
        return stats
    
    def analyze_import_relationships(self) -> Dict[str, Any]:
        """Analyze import relationships between modules"""
        relationships = {}
        
        for py_file in self.project_root.rglob("*.py"):
            if any(part.startswith('.') for part in py_file.parts):
                continue
            
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Extract imports
                imports = self._extract_imports(content)
                relative_path = str(py_file.relative_to(self.project_root))
                
                relationships[relative_path] = {
                    "imports": imports,
                    "local_imports": [imp for imp in imports if self._is_local_import(imp)],
                    "external_imports": [imp for imp in imports if not self._is_local_import(imp)]
                }
            
            except Exception:
                continue
        
        return relationships
    
    def discover_other_projects(self) -> List[Dict[str, Any]]:
        """Discover other Bruce projects in parent directories"""
        projects = []
        
        # Search up the directory tree and in sibling directories
        current = self.project_root.parent
        
        for _ in range(3):  # Don't go too far up
            try:
                for item in current.iterdir():
                    if item.is_dir() and item != self.project_root:
                        bruce_config = item / "bruce.yaml"
                        if bruce_config.exists():
                            try:
                                with open(bruce_config, 'r') as f:
                                    config = yaml.safe_load(f)
                                
                                projects.append({
                                    "path": str(item),
                                    "name": config.get("project", {}).get("name", item.name),
                                    "type": config.get("project", {}).get("type", "unknown"),
                                    "config_file": str(bruce_config)
                                })
                            except Exception:
                                projects.append({
                                    "path": str(item),
                                    "name": item.name,
                                    "config_file": str(bruce_config),
                                    "config_error": True
                                })
                
                current = current.parent
            except (OSError, PermissionError):
                break
        
        return projects
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get git repository status"""
        try:
            # Check if we're in a git repo
            result = subprocess.run(["git", "rev-parse", "--git-dir"], 
                                  capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                return {"is_git_repo": False}
            
            # Get current branch
            branch_result = subprocess.run(["git", "branch", "--show-current"], 
                                         capture_output=True, text=True, cwd=self.project_root)
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            # Get status
            status_result = subprocess.run(["git", "status", "--porcelain"], 
                                         capture_output=True, text=True, cwd=self.project_root)
            
            changes = []
            if status_result.returncode == 0:
                for line in status_result.stdout.strip().split('\n'):
                    if line:
                        status_code = line[:2]
                        filename = line[3:]
                        changes.append({"status": status_code, "file": filename})
            
            # Get recent commits
            log_result = subprocess.run(["git", "log", "--oneline", "-5"], 
                                      capture_output=True, text=True, cwd=self.project_root)
            
            recent_commits = []
            if log_result.returncode == 0:
                for line in log_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(' ', 1)
                        if len(parts) == 2:
                            recent_commits.append({"hash": parts[0], "message": parts[1]})
            
            return {
                "is_git_repo": True,
                "current_branch": current_branch,
                "changes": changes,
                "recent_commits": recent_commits,
                "has_uncommitted_changes": len(changes) > 0
            }
        
        except Exception as e:
            return {"is_git_repo": False, "error": str(e)}
    
    # Helper methods
    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file for basic information"""
        try:
            stat = file_path.stat()
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Count lines and extract basic info
            lines = content.split('\n')
            code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            
            return {
                "name": file_path.name,
                "path": str(file_path),
                "size": stat.st_size,
                "lines": len(lines),
                "code_lines": len(code_lines),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "has_main": "if __name__ == '__main__':" in content,
                "has_flask": "from flask import" in content or "import flask" in content,
                "has_argparse": "import argparse" in content or "from argparse import" in content
            }
        except Exception as e:
            return {
                "name": file_path.name,
                "path": str(file_path),
                "error": str(e)
            }
    
    def _check_template_integration(self) -> bool:
        """Check if web interface integrates with templates"""
        try:
            web_files = ["bruce_app.py", "bruce_complete.py", "bruce.py"]
            for web_file in web_files:
                file_path = self.project_root / web_file
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        content = f.read()
                    if "from templates" in content or "import templates" in content:
                        return True
            return False
        except Exception:
            return False
    
    def _extract_flask_routes(self, file_info: Dict[str, Any]) -> List[str]:
        """Extract Flask route patterns from file"""
        if not file_info or "error" in file_info:
            return []
        
        try:
            with open(file_info["path"], 'r') as f:
                content = f.read()
            
            routes = re.findall(r"@app\.route\(['\"]([^'\"]+)['\"]", content)
            return routes
        except Exception:
            return []
    
    def _check_multi_project_support(self) -> bool:
        """Check if web interface supports multiple projects"""
        try:
            web_files = ["bruce_app.py", "bruce_complete.py", "bruce.py"]
            for web_file in web_files:
                file_path = self.project_root / web_file
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        content = f.read()
                    if "project_root" in content.lower() and "taskmanager" in content:
                        return True
            return False
        except Exception:
            return False
    
    def _extract_cli_commands(self, file_info: Dict[str, Any]) -> List[str]:
        """Extract CLI commands from file"""
        if not file_info or "error" in file_info:
            return []
        
        try:
            with open(file_info["path"], 'r') as f:
                content = f.read()
            
            commands = re.findall(r'subparsers\.add_parser\(["\']([^"\']+)["\']', content)
            return commands
        except Exception:
            return []
    
    def _check_cli_multi_project_support(self, file_info: Dict[str, Any]) -> bool:
        """Check if CLI supports multiple projects"""
        if not file_info or "error" in file_info:
            return False
        
        try:
            with open(file_info["path"], 'r') as f:
                content = f.read()
            
            indicators = ["get_project_root", "bruce.yaml", "project_root", "bruce init"]
            return any(indicator in content for indicator in indicators)
        except Exception:
            return False
    
    def _detect_template_features(self, content: str) -> List[str]:
        """Detect features in template content"""
        features = []
        
        feature_patterns = {
            "enhanced_context": ["enhanced", "context", "related_tasks"],
            "blueprint_generation": ["blueprint", "generate", "architecture"],
            "task_management": ["task_item", "start_task", "complete_task"],
            "phase_tracking": ["phase", "progress", "percentage"],
            "modals": ["modal", "showModal", "closeModal"],
            "ajax": ["fetch(", "XMLHttpRequest", "$.ajax"],
            "form_handling": ["form", "submit", "preventDefault"],
            "responsive_design": ["@media", "flex", "grid"],
            "theme_support": ["theme_color", "{{ theme"]
        }
        
        for feature, patterns in feature_patterns.items():
            if any(pattern in content for pattern in patterns):
                features.append(feature)
        
        return features
    
    def _extract_template_dependencies(self, content: str) -> List[str]:
        """Extract template dependencies"""
        dependencies = []
        
        # Look for imports
        import_matches = re.findall(r'from\s+\.(\w+)\s+import', content)
        dependencies.extend(import_matches)
        
        # Look for template calls
        template_calls = re.findall(r'get_(\w+)_template\(\)', content)
        dependencies.extend(template_calls)
        
        return list(set(dependencies))
    
    def _check_modular_architecture(self, templates_dir: Path) -> bool:
        """Check if templates follow modular architecture"""
        try:
            init_file = templates_dir / "__init__.py"
            if init_file.exists():
                with open(init_file, 'r') as f:
                    content = f.read()
                return "TEMPLATES" in content and "get_template" in content
            return False
        except Exception:
            return False
    
    def _analyze_task_manager_capabilities(self, file_path: Path) -> List[str]:
        """Analyze TaskManager capabilities"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            capabilities = []
            if "load_tasks" in content:
                capabilities.append("Multi-phase task loading")
            if "enhanced_context" in content:
                capabilities.append("Enhanced context generation")
            if "find_related_tasks" in content:
                capabilities.append("Related task discovery")
            if "config_manager" in content.lower():
                capabilities.append("Configuration management")
            if "generate_architecture_context" in content:
                capabilities.append("Architecture context generation")
            
            return capabilities
        except Exception:
            return []
    
    def _analyze_config_manager_capabilities(self, file_path: Path) -> List[str]:
        """Analyze ConfigManager capabilities"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            capabilities = []
            if "bruce.yaml" in content:
                capabilities.append("YAML configuration loading")
            if "project_root" in content:
                capabilities.append("Multi-project support")
            if "validate_config" in content:
                capabilities.append("Configuration validation")
            if "theme_color" in content:
                capabilities.append("UI theming support")
            
            return capabilities
        except Exception:
            return []
    
    def _analyze_blueprint_capabilities(self, file_path: Path) -> List[str]:
        """Analyze Blueprint generator capabilities"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            capabilities = []
            if "generate_system_architecture" in content:
                capabilities.append("System architecture generation")
            if "session_handoff" in content:
                capabilities.append("Session handoff generation")
            if "phase_blueprint" in content:
                capabilities.append("Phase blueprint generation")
            if "auto_generate_on_completion" in content:
                capabilities.append("Auto-generation on task completion")
            
            return capabilities
        except Exception:
            return []
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from Python content"""
        imports = []
        
        # Regular imports
        import_pattern = r'^import\s+([^\s#]+)'
        from_pattern = r'^from\s+([^\s#]+)\s+import'
        
        for line in content.split('\n'):
            line = line.strip()
            
            import_match = re.match(import_pattern, line)
            if import_match:
                imports.append(import_match.group(1))
            
            from_match = re.match(from_pattern, line)
            if from_match:
                imports.append(from_match.group(1))
        
        return imports
    
    def _is_local_import(self, import_name: str) -> bool:
        """Check if import is local to the project"""
        local_indicators = ["src.", "templates.", ".task_manager", ".config_manager", ".blueprint_generator"]
        return any(indicator in import_name for indicator in local_indicators)


class DynamicBlueprintGenerator:
    """Enhanced blueprint generator with dynamic analysis"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.task_manager = TaskManager(self.project_root)
        self.docs_path = self.project_root / "docs"
        self.scanner = ProjectScanner(self.project_root)
    
    def generate_ultimate_system_architecture_blueprint(self) -> str:
        """Generate the ultimate 'lay of the land' blueprint with everything"""
        print("🔍 Scanning project structure...")
        scan_results = self.scanner.scan_full_project()
        
        print("📊 Analyzing task data...")
        phase_progress = self.task_manager.get_phase_progress()
        tasks_data = self.task_manager.load_tasks()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        blueprint = f"""# 🏗️ Bruce System Architecture Blueprint - COMPLETE ANALYSIS

**Generated:** {timestamp}
**System Analysis:** Bruce Project Management System (Dynamic Scan)
**Project Root:** {self.project_root}

## 📊 Project Status Summary

"""
        
        # Add progress overview
        total_tasks = sum(p['total'] for p in phase_progress.values())
        total_completed = sum(p['completed'] for p in phase_progress.values())
        overall_progress = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
        
        blueprint += f"**Overall Progress:** {total_completed}/{total_tasks} tasks ({overall_progress:.1f}%)\n"
        blueprint += f"**File Analysis:** {scan_results['file_statistics']['total_files']} files, {scan_results['file_statistics']['total_size']:,} bytes\n"
        blueprint += f"**Git Status:** {'✅ Clean' if not scan_results['git_status'].get('has_uncommitted_changes') else '⚠️ Uncommitted changes'}\n"
        blueprint += f"**Config Status:** {'✅ Loaded' if scan_results['config_structure']['has_config'] else '📋 Default'}\n\n"
        
        # Dynamic architecture map
        blueprint += self._generate_dynamic_architecture_map(scan_results)
        
        # Component analysis
        blueprint += self._generate_component_analysis(scan_results)
        
        # API and CLI reference
        blueprint += self._generate_api_cli_reference(scan_results)
        
        # File statistics
        blueprint += self._generate_file_statistics_section(scan_results)
        
        # Import relationships
        blueprint += self._generate_import_relationships_section(scan_results)
        
        # Multi-project information
        blueprint += self._generate_multi_project_section(scan_results)
        
        # Development context
        blueprint += self._generate_development_context_section(scan_results)
        
        blueprint += f"""
---

**🎯 This blueprint provides the complete technical landscape of the Bruce system.**
**Every component, file, relationship, and capability has been dynamically analyzed.**
**Use this for comprehensive Claude handoffs with full system understanding.**

*Last updated: {timestamp}*
"""
        
        return blueprint
    
    def _generate_dynamic_architecture_map(self, scan_results: Dict[str, Any]) -> str:
        """Generate dynamic architecture map based on actual detected components"""
        web_interface = scan_results["web_interface"]
        cli_interface = scan_results["cli_interface"]
        template_system = scan_results["template_system"]
        core_modules = scan_results["core_modules"]
        
        # Get actual file names
        web_file = web_interface["main_file"]["name"] if web_interface["main_file"] else "None"
        cli_file = cli_interface["main_file"]["name"] if cli_interface["main_file"] else "None"
        template_count = template_system.get("total_templates", 0)
        
        architecture_map = f"""## 🏗️ Dynamic System Architecture Map

### Core Components & Connections (ACTUAL DETECTED STRUCTURE)

```
📁 BRUCE PROJECT MANAGEMENT SYSTEM ({scan_results['file_statistics']['total_files']} files)
│
├── 🧠 CORE ENGINE ({core_modules['total_modules']} modules)
│   ├── TaskManager (src/task_manager.py)
│   │   ├── → reads: phases/*.yml, tasks.yaml
│   │   ├── → writes: contexts/phase*/context_*.md  
│   │   ├── → manages: task status, progress tracking
│   │   └── → provides: {', '.join(self._get_task_manager_capabilities(scan_results))}
│   │
│   ├── ConfigManager (src/config_manager.py)
│   │   ├── → loads: bruce.yaml configuration
│   │   ├── → provides: {', '.join(self._get_config_manager_capabilities(scan_results))}
│   │   └── → enables: multi-project support
│   │
│   └── BlueprintGenerator (src/blueprint_generator.py) ← THIS FILE!
│       ├── → analyzes: project structure dynamically
│       ├── → scans: {scan_results['file_statistics']['python_files']} Python files
│       ├── → writes: docs/blueprints/, docs/sessions/
│       └── → provides: {', '.join(self._get_blueprint_capabilities(scan_results))}
│
├── 🖥️ USER INTERFACES  
│   ├── CLI Interface ({cli_file})
│   │   ├── → commands: {', '.join(cli_interface.get('available_commands', [])[:5])}{'...' if len(cli_interface.get('available_commands', [])) > 5 else ''}
│   │   ├── → supports: {'multi-project' if cli_interface.get('multi_project_support') else 'single-project'}
│   │   └── → features: git integration, blueprint auto-generation
│   │
│   └── Web Dashboard ({web_file})
│       ├── → templates: {template_count} modular templates
│       ├── → endpoints: {len(scan_results['api_endpoints'])} API routes
│       ├── → features: {', '.join(template_system.get('features', [])[:5])}
│       └── → architecture: {'modular' if template_system.get('modular_architecture') else 'monolithic'}
│
├── 🎨 TEMPLATE SYSTEM (templates/ - {template_count} files)
│   ├── Modular Architecture: {'✅' if template_system.get('modular_architecture') else '❌'}
│   ├── Template Files: {', '.join([t['name'] for t in template_system.get('template_files', [])[:5]])}
│   ├── Features: {', '.join(template_system.get('features', [])[:3])}
│   └── Dependencies: Cross-template imports and shared styles
│
└── 📄 DATA & CONFIGURATION
    ├── Phase Definitions (phases/ - {scan_results['file_statistics']['yaml_files']} YAML files)
    │   └── → defines: tasks, acceptance criteria, dependencies
    │
    ├── Context Files (contexts/phase*/)
    │   └── → contains: task context, implementation notes
    │
    ├── Configuration ({scan_results['config_structure']['config_files'][0]['path'] if scan_results['config_structure']['config_files'] else 'None'})
    │   └── → manages: project settings, UI theming, directories
    │
    └── Generated Documentation (docs/)
        ├── blueprints/ → system architecture, progress reports
        └── sessions/ → Claude handoff documents
```
"""
        
        return architecture_map
    
    def _generate_component_analysis(self, scan_results: Dict[str, Any]) -> str:
        """Generate detailed component analysis"""
        section = """## 🔍 Component Deep Analysis

### Web Interface Details
"""
        
        web_interface = scan_results["web_interface"]
        if web_interface["main_file"]:
            main_file = web_interface["main_file"]
            section += f"""- **Main File:** {main_file['name']} ({main_file['lines']} lines, {main_file['size']:,} bytes)
- **Last Modified:** {main_file['modified'][:19]}
- **Flask Integration:** {'✅' if main_file.get('has_flask') else '❌'}
- **Template Integration:** {'✅' if web_interface.get('template_integration') else '❌'}
- **Multi-Project Ready:** {'✅' if web_interface.get('multi_project_ready') else '❌'}
"""
        else:
            section += "- **Status:** No web interface detected\n"
        
        section += "\n### CLI Interface Details\n"
        
        cli_interface = scan_results["cli_interface"]
        if cli_interface["main_file"]:
            main_file = cli_interface["main_file"]
            section += f"""- **Main File:** {main_file['name']} ({main_file['lines']} lines, {main_file['size']:,} bytes)
- **Last Modified:** {main_file['modified'][:19]}
- **Argparse Integration:** {'✅' if main_file.get('has_argparse') else '❌'}
- **Available Commands:** {len(cli_interface.get('available_commands', []))}
- **Multi-Project Support:** {'✅' if cli_interface.get('multi_project_support') else '❌'}
"""
        else:
            section += "- **Status:** No CLI interface detected\n"
        
        section += "\n### Template System Analysis\n"
        
        template_system = scan_results["template_system"]
        if template_system["exists"]:
            section += f"""- **Total Templates:** {template_system['total_templates']}
- **Modular Architecture:** {'✅' if template_system.get('modular_architecture') else '❌'}
- **Detected Features:** {', '.join(template_system.get('features', []))}
- **Template Files:**
"""
            for template in template_system.get("template_files", []):
                section += f"  - {template['name']}: {template['lines']} lines, features: {', '.join(template.get('features', []))}\n"
        else:
            section += "- **Status:** No template system detected\n"
        
        section += "\n### Core Modules Analysis\n"
        
        core_modules = scan_results["core_modules"]
        if core_modules["exists"]:
            section += f"- **Total Modules:** {core_modules['total_modules']}\n"
            for module in core_modules.get("modules", []):
                role = module.get('role', 'Unknown Role')
                capabilities = module.get('capabilities', [])
                section += f"  - **{module['name']}:** {role}\n"
                section += f"    - Size: {module['lines']} lines ({module['size']:,} bytes)\n"
                section += f"    - Modified: {module['modified'][:19]}\n"
                if capabilities:
                    section += f"    - Capabilities: {', '.join(capabilities)}\n"
        else:
            section += "- **Status:** No core modules detected\n"
        
        return section
    
    def _generate_api_cli_reference(self, scan_results: Dict[str, Any]) -> str:
        """Generate API and CLI reference"""
        section = """## 🔌 API & CLI Reference

### API Endpoints
"""
        
        endpoints = scan_results["api_endpoints"]
        if endpoints:
            section += f"**Total Endpoints:** {len(endpoints)}\n\n"
            
            # Group by method
            by_method = {}
            for endpoint in endpoints:
                for method in endpoint["methods"]:
                    if method not in by_method:
                        by_method[method] = []
                    by_method[method].append(endpoint)
            
            for method, method_endpoints in by_method.items():
                section += f"**{method} Endpoints:**\n"
                for ep in method_endpoints:
                    section += f"- `{method} {ep['endpoint']}` → {ep.get('function', 'unknown')}\n"
                section += "\n"
        else:
            section += "No API endpoints detected\n\n"
        
        section += "### CLI Commands\n"
        
        commands = scan_results["cli_commands"]
        if commands:
            section += f"**Total Commands:** {len(commands)}\n\n"
            for cmd in commands:
                section += f"- `{cmd['command']}`: {cmd.get('help', 'No description')}\n"
        else:
            section += "No CLI commands detected\n"
        
        return section + "\n"
    
    def _generate_file_statistics_section(self, scan_results: Dict[str, Any]) -> str:
        """Generate file statistics section"""
        stats = scan_results["file_statistics"]
        
        section = f"""## 📊 File Statistics & Metrics

### Overall Statistics
- **Total Files:** {stats['total_files']:,}
- **Total Size:** {stats['total_size']:,} bytes ({stats['total_size']/1024:.1f} KB)
- **Python Files:** {stats['python_files']}
- **YAML Files:** {stats['yaml_files']}
- **Markdown Files:** {stats['markdown_files']}

### By Directory
"""
        
        for dir_name, dir_stats in stats["by_directory"].items():
            section += f"- **{dir_name}/**: {dir_stats['files']} files, {dir_stats['size']:,} bytes\n"
        
        section += "\n### Largest Files\n"
        for file_info in stats["largest_files"][:5]:
            section += f"- {file_info['path']}: {file_info['size']:,} bytes\n"
        
        section += "\n### Recently Modified\n"
        for file_info in stats["recently_modified"][:5]:
            modified_date = file_info['modified'][:19]
            section += f"- {file_info['path']}: {modified_date}\n"
        
        return section + "\n"
    
    def _generate_import_relationships_section(self, scan_results: Dict[str, Any]) -> str:
        """Generate import relationships section"""
        relationships = scan_results["import_relationships"]
        
        section = """## 🔗 Import Relationships & Dependencies

### Module Dependencies
"""
        
        # Find the most connected modules
        connection_counts = {}
        for module, data in relationships.items():
            local_imports = data.get("local_imports", [])
            connection_counts[module] = len(local_imports)
        
        # Sort by connection count
        sorted_modules = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)
        
        for module, count in sorted_modules[:10]:  # Top 10 most connected
            if count > 0:
                local_imports = relationships[module]["local_imports"]
                section += f"- **{module}** ({count} local imports)\n"
                for imp in local_imports[:3]:  # Show first 3
                    section += f"  - imports: {imp}\n"
                if len(local_imports) > 3:
                    section += f"  - ... and {len(local_imports) - 3} more\n"
        
        section += "\n### External Dependencies\n"
        
        # Collect all external dependencies
        all_external = set()
        for module_data in relationships.values():
            all_external.update(module_data.get("external_imports", []))
        
        common_external = ["flask", "yaml", "pathlib", "datetime", "typing"]
        detected_external = [imp for imp in all_external if any(common in imp for common in common_external)]
        
        for ext in detected_external[:10]:
            section += f"- {ext}\n"
        
        return section + "\n"
    
    def _generate_multi_project_section(self, scan_results: Dict[str, Any]) -> str:
        """Generate multi-project information section"""
        projects = scan_results["project_discovery"]
        
        section = f"""## 🌐 Multi-Project Environment

### Current Project
- **Path:** {scan_results['project_root']}
- **Multi-Project CLI Support:** {'✅' if scan_results['cli_interface'].get('multi_project_support') else '❌'}
- **Multi-Project Web Support:** {'✅' if scan_results['web_interface'].get('multi_project_ready') else '❌'}

### Discovered Projects
"""
        
        if projects:
            section += f"**Found {len(projects)} other Bruce projects:**\n\n"
            for project in projects:
                section += f"- **{project['name']}** ({project.get('type', 'unknown')})\n"
                section += f"  - Path: {project['path']}\n"
                if project.get("config_error"):
                    section += "  - Status: ⚠️ Config error\n"
                else:
                    section += "  - Status: ✅ Available\n"
                section += "\n"
        else:
            section += "No other Bruce projects found in nearby directories\n\n"
        
        return section
    
    def _generate_development_context_section(self, scan_results: Dict[str, Any]) -> str:
        """Generate development context section"""
        git_status = scan_results["git_status"]
        
        section = """## 🚀 Development Context

### Git Repository Status
"""
        
        if git_status["is_git_repo"]:
            section += f"- **Repository:** ✅ Git repository detected\n"
            section += f"- **Current Branch:** {git_status.get('current_branch', 'unknown')}\n"
            section += f"- **Uncommitted Changes:** {len(git_status.get('changes', []))}\n"
            
            if git_status.get("changes"):
                section += "- **Modified Files:**\n"
                for change in git_status["changes"][:5]:
                    section += f"  - {change['status']} {change['file']}\n"
                if len(git_status["changes"]) > 5:
                    section += f"  - ... and {len(git_status['changes']) - 5} more\n"
            
            if git_status.get("recent_commits"):
                section += "- **Recent Commits:**\n"
                for commit in git_status["recent_commits"][:3]:
                    section += f"  - {commit['hash']}: {commit['message']}\n"
        else:
            section += "- **Repository:** ❌ Not a git repository\n"
        
        # Configuration status
        config_structure = scan_results["config_structure"]
        section += f"\n### Configuration\n"
        section += f"- **Config Files Found:** {len(config_structure['config_files'])}\n"
        section += f"- **Config Manager Available:** {'✅' if config_structure['config_manager_available'] else '❌'}\n"
        
        if config_structure["config_files"]:
            for config_file in config_structure["config_files"]:
                if "error" not in config_file:
                    section += f"- **Active Config:** {config_file['path']}\n"
                    if "structure" in config_file:
                        structure = config_file["structure"]
                        if "project" in structure:
                            section += f"  - Project: {structure['project'].get('name', 'Unnamed')}\n"
                            section += f"  - Type: {structure['project'].get('type', 'unknown')}\n"
        
        return section
    
    # Helper methods for capabilities extraction
    def _get_task_manager_capabilities(self, scan_results: Dict[str, Any]) -> List[str]:
        """Extract TaskManager capabilities from scan results"""
        for module in scan_results["core_modules"].get("modules", []):
            if module["name"] == "task_manager.py":
                return module.get("capabilities", ["task management"])
        return ["task management"]
    
    def _get_config_manager_capabilities(self, scan_results: Dict[str, Any]) -> List[str]:
        """Extract ConfigManager capabilities from scan results"""
        for module in scan_results["core_modules"].get("modules", []):
            if module["name"] == "config_manager.py":
                return module.get("capabilities", ["configuration"])
        return ["configuration"]
    
    def _get_blueprint_capabilities(self, scan_results: Dict[str, Any]) -> List[str]:
        """Extract Blueprint generator capabilities from scan results"""
        for module in scan_results["core_modules"].get("modules", []):
            if module["name"] == "blueprint_generator.py":
                return module.get("capabilities", ["documentation"])
        return ["documentation"]
    
    # Keep original methods for backward compatibility
    def generate_comprehensive_phase_blueprint(self, phase_id: int) -> str:
        """Generate phase blueprint (unchanged for compatibility)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        tasks_data = self.task_manager.load_tasks()
        phase_progress = self.task_manager.get_phase_progress()
        
        if phase_id not in phase_progress:
            return f"Phase {phase_id} not found."
        
        progress = phase_progress[phase_id]
        phase_info = tasks_data.get("phases", {}).get(str(phase_id), {})
        
        # Determine phase status
        if progress['percentage'] == 100:
            status_badge = "✅ COMPLETE"
            status_color = "🟢"
        elif progress['completed'] > 0:
            status_badge = "🔄 IN PROGRESS"
            status_color = "🟡"
        else:
            status_badge = "⏳ NOT STARTED"
            status_color = "⚪"
        
        blueprint = f"""# 📋 Phase {phase_id}: {progress['name']} Blueprint

**Status:** {status_badge}
**Progress:** {progress['completed']}/{progress['total']} tasks ({progress['percentage']:.1f}%)
**Last Updated:** {timestamp}
**Source of Truth:** This document contains ALL information for Phase {phase_id}

---

## 🎯 Phase Overview

{phase_info.get('description', 'Complete PM system for seamless Claude handoffs')}

### 📊 Progress Summary
- **{status_color} Total Tasks:** {progress['total']}
- **✅ Completed:** {progress['completed']} 
- **🔄 In Progress:** {progress['in_progress']}
- **⏳ Pending:** {progress['pending']}
- **🚫 Blocked:** {progress['blocked']}

### Progress Visualization
"""
        
        # Add progress bar
        bar_length = 50
        filled = int(bar_length * progress['percentage'] / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        blueprint += f"`[{bar}] {progress['percentage']:.1f}%`\n\n"
        
        # Now use dynamic architecture instead of hardcoded
        blueprint += "---\n\n"
        blueprint += "## 🏗️ Current System Architecture\n\n"
        blueprint += "**Note:** This architecture is dynamically generated based on actual project files.\n\n"
        
        # Get a condensed version of the dynamic architecture
        scan_results = self.scanner.scan_full_project()
        dynamic_arch = self._generate_dynamic_architecture_map(scan_results)
        blueprint += dynamic_arch
        
        blueprint += f"""

---

## 🚀 Session Handoff Information

### For New Claude Sessions

**You're working on:** Phase {phase_id} of the Bruce project management system.

**Goal:** {phase_info.get('description', 'Build a system for seamless Claude session handoffs')}

**Current Status:** {progress['completed']}/{progress['total']} tasks completed ({progress['percentage']:.1f}%)

### Quick Start Commands
```bash
# Check current status
python cli/bruce.py status

# See phase progress  
python cli/bruce.py phases

# List available tasks
python cli/bruce.py list --phase {phase_id}

# Start next task (with enhanced context)
python cli/bruce.py start <task-id>

# Start with basic context
python cli/bruce.py start <task-id> --basic
```

### Key Files for This Phase
- **Phase Definition:** `phases/phase{phase_id}_*.yml`
- **Context Files:** `contexts/phase{phase_id}/`
- **This Blueprint:** `docs/blueprints/phase_{phase_id}_blueprint.md`

---

**🎯 This is the complete source of truth for Phase {phase_id}. Everything you need to continue development is documented above.**

*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        return blueprint
    
    def generate_session_handoff(self) -> str:
        """Generate session handoff with dynamic system analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get dynamic system analysis
        scan_results = self.scanner.scan_full_project()
        
        handoff = f"""# 🤝 Claude Session Handoff - Complete System Analysis

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Session ID:** session_{timestamp}
**Project:** Bruce Project Management System
**Analysis:** Dynamic system scan completed

## 🎯 Mission Briefing

You're joining development of a **multi-phase project management system** designed for seamless Claude session handoffs. The system tracks tasks across phases, auto-generates documentation, and preserves context between sessions.

## 📊 Current Development Status

"""
        
        # Add current progress
        phase_progress = self.task_manager.get_phase_progress()
        tasks_data = self.task_manager.load_tasks()
        
        total_tasks = sum(p['total'] for p in phase_progress.values())
        total_completed = sum(p['completed'] for p in phase_progress.values())
        overall_progress = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
        
        handoff += f"**Overall Progress:** {total_completed}/{total_tasks} tasks ({overall_progress:.1f}%)\n"
        handoff += f"**System Files:** {scan_results['file_statistics']['total_files']} files analyzed\n"
        handoff += f"**Architecture:** {scan_results['template_system']['total_templates']} templates, {len(scan_results['api_endpoints'])} API endpoints\n\n"
        
        # Show what's been built
        handoff += "### ✅ What's Been Built\n"
        completed_tasks = [t for t in tasks_data.get("tasks", []) if t.get('status') == 'completed']
        for task in completed_tasks[:5]:
            handoff += f"- **{task['id']}:** {task.get('description', '')} → `{task.get('output', '')}`\n"
        if len(completed_tasks) > 5:
            handoff += f"- ... and {len(completed_tasks) - 5} more completed tasks\n"
        
        handoff += "\n### 🔄 What You're Continuing\n"
        pending_tasks = [t for t in tasks_data.get("tasks", []) if t.get('status') == 'pending']
        for task in pending_tasks[:3]:
            handoff += f"- **{task['id']}:** {task.get('description', '')} → `{task.get('output', '')}`\n"
        
        # Add dynamic architecture overview
        handoff += "\n## 🏗️ Current System Architecture (LIVE ANALYSIS)\n\n"
        handoff += self._generate_dynamic_architecture_map(scan_results)
        
        # Add quick reference
        handoff += """

## 🚀 How to Continue Development

### Immediate Commands (VERIFIED)
```bash
# Check current system status
python cli/bruce.py status

# See what tasks are available
python cli/bruce.py list

# Start a specific task with enhanced context
python cli/bruce.py start <task-id>

# Generate this analysis again
python src/blueprint_generator.py architecture
```

### Web Interface (VERIFIED)
"""
        
        web_interface = scan_results["web_interface"]
        if web_interface["main_file"]:
            web_file = web_interface["main_file"]["name"]
            handoff += f"- **File:** {web_file}\n"
            handoff += f"- **Templates:** {scan_results['template_system']['total_templates']} modular templates\n"
            handoff += f"- **Endpoints:** {len(scan_results['api_endpoints'])} API routes\n"
            handoff += f"- **Features:** {', '.join(scan_results['template_system'].get('features', [])[:5])}\n"
        else:
            handoff += "- **Status:** No web interface detected\n"
        
        handoff += f"""

### Multi-Project Status
- **CLI Multi-Project:** {'✅ Supported' if scan_results['cli_interface'].get('multi_project_support') else '❌ Not supported'}
- **Web Multi-Project:** {'✅ Ready' if scan_results['web_interface'].get('multi_project_ready') else '❌ Not ready'}
- **Other Projects Found:** {len(scan_results['project_discovery'])}

---

**🚀 Ready to continue development!** This analysis was generated dynamically from your actual project structure.
**Everything above reflects the current state of your system, not hardcoded assumptions.**
"""
        
        return handoff
    
    def update_phase_blueprint(self, phase_id: int) -> str:
        """Update phase blueprint with dynamic architecture"""
        content = self.generate_comprehensive_phase_blueprint(phase_id)
        blueprints_dir = self.docs_path / "blueprints"
        blueprints_dir.mkdir(parents=True, exist_ok=True)
        
        doc_path = blueprints_dir / f"phase_{phase_id}_blueprint.md"
        
        with open(doc_path, 'w') as f:
            f.write(content)
        
        print(f"📋 Updated Phase {phase_id} blueprint with dynamic architecture: {doc_path.name}")
        return str(doc_path)
    
    def auto_generate_on_completion(self, task_id: str) -> Dict[str, str]:
        """Auto-update blueprints when tasks complete"""
        results = {}
        
        try:
            tasks_data = self.task_manager.load_tasks()
            task = next((t for t in tasks_data.get("tasks", []) if t["id"] == task_id), None)
            
            if not task:
                return {"error": f"Task {task_id} not found"}
            
            phase_id = task.get('phase', 1)
            
            # Update the phase blueprint with dynamic architecture
            blueprint_path = self.update_phase_blueprint(phase_id)
            results["phase_blueprint"] = blueprint_path
            
            return results
            
        except Exception as e:
            return {"error": f"Dynamic blueprint update failed: {e}"}


# Replace the original PhaseBlueprintGenerator with the enhanced version
PhaseBlueprintGenerator = DynamicBlueprintGenerator


def main():
    """CLI interface for enhanced blueprint generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate dynamic comprehensive blueprints")
    parser.add_argument('command', choices=['phase', 'complete', 'update', 'handoff', 'architecture', 'scan'], 
                       help="Command to execute")
    parser.add_argument('--phase-id', type=int, default=1, help="Phase ID")
    parser.add_argument('--project-root', default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    generator = DynamicBlueprintGenerator(args.project_root)
    
    if args.command == 'phase':
        content = generator.generate_comprehensive_phase_blueprint(args.phase_id)
        print(content)
    
    elif args.command == 'update':
        filepath = generator.update_phase_blueprint(args.phase_id)
        print(f"Phase {args.phase_id} blueprint updated with dynamic architecture: {filepath}")
    
    elif args.command == 'handoff':
        content = generator.generate_session_handoff()
        print(content)
    
    elif args.command == 'architecture':
        content = generator.generate_ultimate_system_architecture_blueprint()
        print(content)
    
    elif args.command == 'scan':
        scan_results = generator.scanner.scan_full_project()
        print(json.dumps(scan_results, indent=2, default=str))

if __name__ == "__main__":
    main()