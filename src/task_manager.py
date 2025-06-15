#!/usr/bin/env python3
"""
Enhanced Task Manager with Multi-Phase Support, Enhanced Context, Config System, and Session Tracking
Save as: src/task_manager.py
"""

import yaml
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
import shutil
import re
import sys
import time
import hashlib

# Import config manager
try:
    from src.config_manager import ConfigManager
except ImportError:
    # Fallback if config manager not available
    print("⚠️  Config manager not found, using hardcoded paths")
    ConfigManager = None

class TaskSession:
    """Represents a work session on a task"""
    def __init__(self, task_id: str, project_root: Path):
        self.task_id = task_id
        self.project_root = project_root
        self.start_time = datetime.now()
        self.end_time = None
        self.files_modified = set()
        self.files_created = set()
        self.files_deleted = set()
        self.git_commits = []
        self.context_snapshots = []
        self.file_checksums = {}  # Track file content changes
        self.session_notes = []
        self.is_active = True
        
        # Capture initial state
        self._capture_initial_state()
    
    def _capture_initial_state(self):
        """Capture initial file states for change detection"""
        # Track Python, YAML, and markdown files
        patterns = ['**/*.py', '**/*.yaml', '**/*.yml', '**/*.md']
        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                if not any(part.startswith('.') for part in file_path.parts):
                    try:
                        self.file_checksums[str(file_path)] = self._get_file_checksum(file_path)
                    except Exception:
                        pass
    
    def _get_file_checksum(self, file_path: Path) -> str:
        """Get MD5 checksum of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def capture_changes(self):
        """Detect and record file changes during session"""
        current_checksums = {}
        patterns = ['**/*.py', '**/*.yaml', '**/*.yml', '**/*.md']
        
        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                if not any(part.startswith('.') for part in file_path.parts):
                    try:
                        current_checksums[str(file_path)] = self._get_file_checksum(file_path)
                    except Exception:
                        pass
        
        # Find modified files
        for file_path, old_checksum in self.file_checksums.items():
            if file_path in current_checksums:
                if current_checksums[file_path] != old_checksum:
                    self.files_modified.add(file_path)
            else:
                self.files_deleted.add(file_path)
        
        # Find new files
        for file_path in current_checksums:
            if file_path not in self.file_checksums:
                self.files_created.add(file_path)
        
        # Update checksums
        self.file_checksums = current_checksums
        
        # Capture git commits if any
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", f"--since={self.start_time.isoformat()}", "--"],
                capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                self.git_commits = [c for c in commits if c]
        except Exception:
            pass
    
    def add_note(self, note: str):
        """Add a timestamped note to the session"""
        self.session_notes.append({
            "timestamp": datetime.now().isoformat(),
            "note": note
        })
    
    def capture_context_snapshot(self, context: str):
        """Capture a context snapshot during the session"""
        self.context_snapshots.append({
            "timestamp": datetime.now().isoformat(),
            "context": context
        })
    
    def end_session(self):
        """End the session and capture final state"""
        self.end_time = datetime.now()
        self.is_active = False
        self.capture_changes()
    
    def get_duration(self) -> timedelta:
        """Get session duration"""
        end = self.end_time or datetime.now()
        return end - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for storage"""
        return {
            "task_id": self.task_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.get_duration().total_seconds(),
            "files_modified": list(self.files_modified),
            "files_created": list(self.files_created),
            "files_deleted": list(self.files_deleted),
            "git_commits": self.git_commits,
            "context_snapshots": self.context_snapshots,
            "session_notes": self.session_notes,
            "is_active": self.is_active
        }

class TaskManager:
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        
        # Load configuration
        if ConfigManager:
            self.config = ConfigManager(self.project_root)
            
            # Use config-driven paths
            self.tasks_file = self.config.get_tasks_file()
            self.phases_dir = self.config.get_phases_dir()
            self.contexts_dir = self.config.get_contexts_dir()
            self.docs_dir = self.config.get_blueprints_dir().parent  # docs/
            self.reports_dir = self.config.get_reports_dir()
            
            # Validate configuration
            if not self.config.validate_config():
                print("⚠️  Config validation failed, but continuing")
                
            print(f"📋 Loaded config for: {self.config.project.name}")
        else:
            # Fallback to hardcoded paths
            self.config = None
            self.tasks_file = self.project_root / "tasks.yaml"
            self.phases_dir = self.project_root / "phases"
            self.contexts_dir = self.project_root / "contexts"
            self.docs_dir = self.project_root / "docs"
            self.reports_dir = self.project_root / "claude_reports"
        
        # Session tracking
        self.sessions_dir = self.project_root / "bruce_sessions"
        self.sessions_dir.mkdir(exist_ok=True)
        self.active_sessions = {}  # task_id -> TaskSession
        self.session_history = self._load_session_history()
        
        # Common paths
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"
        
        # Create directories if they don't exist
        self.phases_dir.mkdir(exist_ok=True)
        self.contexts_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
    
    def _load_session_history(self) -> Dict[str, List[Dict]]:
        """Load session history from disk"""
        history_file = self.sessions_dir / "session_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading session history: {e}")
        return {}
    
    def _save_session_history(self):
        """Save session history to disk"""
        history_file = self.sessions_dir / "session_history.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.session_history, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving session history: {e}")
    
    def start_task_session(self, task_id: str) -> TaskSession:
        """Start a new work session for a task"""
        # End any existing session for this task
        if task_id in self.active_sessions:
            self.end_task_session(task_id)
        
        # Create new session
        session = TaskSession(task_id, self.project_root)
        self.active_sessions[task_id] = session
        
        # Add session start note
        session.add_note("Task session started")
        
        # Save session file
        self._save_active_session(task_id)
        
        return session
    
    def end_task_session(self, task_id: str, notes: str = None) -> Optional[TaskSession]:
        """End a work session for a task"""
        if task_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[task_id]
        
        # Add final notes if provided
        if notes:
            session.add_note(notes)
        
        # End session and capture final changes
        session.end_session()
        
        # Store in history
        if task_id not in self.session_history:
            self.session_history[task_id] = []
        self.session_history[task_id].append(session.to_dict())
        
        # Save history
        self._save_session_history()
        
        # Save final session state
        self._save_session_archive(session)
        
        # Remove from active sessions
        del self.active_sessions[task_id]
        
        # Clean up active session file
        active_file = self.sessions_dir / f"active_{task_id}.json"
        if active_file.exists():
            active_file.unlink()
        
        return session
    
    def _save_active_session(self, task_id: str):
        """Save active session state to disk"""
        if task_id not in self.active_sessions:
            return
        
        session = self.active_sessions[task_id]
        active_file = self.sessions_dir / f"active_{task_id}.json"
        
        try:
            with open(active_file, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving active session: {e}")
    
    def _save_session_archive(self, session: TaskSession):
        """Archive completed session"""
        timestamp = session.start_time.strftime("%Y%m%d_%H%M%S")
        archive_file = self.sessions_dir / f"session_{session.task_id}_{timestamp}.json"
        
        try:
            with open(archive_file, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception as e:
            print(f"⚠️  Error archiving session: {e}")
    
    def get_task_sessions(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a task"""
        sessions = []
        
        # Add active session if exists
        if task_id in self.active_sessions:
            sessions.append(self.active_sessions[task_id].to_dict())
        
        # Add historical sessions
        if task_id in self.session_history:
            sessions.extend(self.session_history[task_id])
        
        return sessions
    
    def get_session_summary(self, task_id: str) -> Dict[str, Any]:
        """Get summary of all sessions for a task"""
        sessions = self.get_task_sessions(task_id)
        
        if not sessions:
            return {
                "total_sessions": 0,
                "total_duration_seconds": 0,
                "total_files_modified": 0,
                "total_commits": 0
            }
        
        total_duration = sum(s.get("duration_seconds", 0) for s in sessions)
        all_files_modified = set()
        all_commits = []
        
        for session in sessions:
            all_files_modified.update(session.get("files_modified", []))
            all_commits.extend(session.get("git_commits", []))
        
        return {
            "total_sessions": len(sessions),
            "total_duration_seconds": total_duration,
            "total_duration_formatted": str(timedelta(seconds=int(total_duration))),
            "total_files_modified": len(all_files_modified),
            "total_commits": len(all_commits),
            "files_modified": list(all_files_modified),
            "commits": all_commits,
            "last_session": sessions[-1] if sessions else None
        }
    
    def track_session_changes(self, task_id: str):
        """Manually trigger change tracking for active session"""
        if task_id in self.active_sessions:
            session = self.active_sessions[task_id]
            session.capture_changes()
            self._save_active_session(task_id)
            return session
        return None
    
    def add_session_note(self, task_id: str, note: str):
        """Add a note to active session"""
        if task_id in self.active_sessions:
            session = self.active_sessions[task_id]
            session.add_note(note)
            self._save_active_session(task_id)
            return True
        return False
    
    def restore_active_sessions(self):
        """Restore active sessions from disk (on startup)"""
        for active_file in self.sessions_dir.glob("active_*.json"):
            try:
                with open(active_file, 'r') as f:
                    session_data = json.load(f)
                
                task_id = session_data["task_id"]
                if session_data.get("is_active", False):
                    # Recreate session object
                    session = TaskSession(task_id, self.project_root)
                    session.start_time = datetime.fromisoformat(session_data["start_time"])
                    session.files_modified = set(session_data.get("files_modified", []))
                    session.files_created = set(session_data.get("files_created", []))
                    session.files_deleted = set(session_data.get("files_deleted", []))
                    session.git_commits = session_data.get("git_commits", [])
                    session.context_snapshots = session_data.get("context_snapshots", [])
                    session.session_notes = session_data.get("session_notes", [])
                    
                    self.active_sessions[task_id] = session
                    print(f"✅ Restored active session for task: {task_id}")
            except Exception as e:
                print(f"⚠️  Error restoring session from {active_file}: {e}")
        
    def get_project_info(self):
        """Get project information from config"""
        if self.config:
            return self.config.get_project_info()
        else:
            return {
                'name': 'Bruce Project',
                'description': 'AI-assisted project management',
                'type': 'general',
                'author': 'Bruce User',
                'config_loaded': False,
                'config_file': None
            }
        
    def load_tasks(self) -> Dict[str, Any]:
        """Load tasks from tasks.yaml AND phases/*.yml files"""
        all_tasks = {"tasks": []}
        
        # Load original tasks.yaml (backward compatibility)
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and data.get("tasks"):
                        # Add phase 0 to legacy tasks if not specified
                        for task in data["tasks"]:
                            if "phase" not in task:
                                task["phase"] = 0
                        all_tasks["tasks"].extend(data["tasks"])
            except Exception as e:
                print(f"Warning: Could not load {self.tasks_file.name}: {e}")
        
        # Load phase files
        if self.phases_dir.exists():
            for phase_file in sorted(self.phases_dir.glob("phase*_*.yml")):
                try:
                    with open(phase_file, 'r') as f:
                        phase_data = yaml.safe_load(f)
                        
                        # Extract phase info
                        phase_info = phase_data.get("phase", {})
                        phase_id = phase_info.get("id", "unknown")
                        phase_name = phase_info.get("name", "Unknown Phase")
                        
                        # Add phase metadata to tasks
                        if phase_data.get("tasks"):
                            for task in phase_data["tasks"]:
                                task["phase"] = phase_id
                                task["phase_name"] = phase_name
                                task["phase_file"] = phase_file.name
                            all_tasks["tasks"].extend(phase_data["tasks"])
                            
                        # Store phase metadata
                        if "phases" not in all_tasks:
                            all_tasks["phases"] = {}
                        all_tasks["phases"][str(phase_id)] = {
                            "name": phase_name,
                            "description": phase_info.get("description", ""),
                            "file": phase_file.name,
                            "task_count": len(phase_data.get("tasks", []))
                        }
                except Exception as e:
                    print(f"Warning: Could not load {phase_file}: {e}")
        
        return all_tasks
    
    def save_task_updates(self, task_id: str, updates: Dict[str, Any]):
        """Save task updates to the appropriate file"""
        tasks_data = self.load_tasks()
        
        for task in tasks_data.get("tasks", []):
            if task["id"] == task_id:
                # Update task
                task.update(updates)
                
                # Determine which file to save to
                if task.get("phase_file"):
                    # Save to phase file
                    phase_file = self.phases_dir / task["phase_file"]
                    self._update_phase_file(phase_file, task_id, task)
                else:
                    # Save to legacy tasks.yaml
                    self._update_legacy_tasks(task_id, task)
                break
    
    def _update_phase_file(self, phase_file: Path, task_id: str, updated_task: Dict):
        """Update a task in a phase file"""
        with open(phase_file, 'r') as f:
            phase_data = yaml.safe_load(f)
        
        # Update the specific task
        for i, task in enumerate(phase_data.get("tasks", [])):
            if task["id"] == task_id:
                # Preserve phase metadata in task
                phase_meta = {
                    "phase": updated_task.get("phase"),
                    "phase_name": updated_task.get("phase_name"),
                    "phase_file": updated_task.get("phase_file")
                }
                # Remove phase metadata before saving
                clean_task = {k: v for k, v in updated_task.items() 
                             if k not in ["phase", "phase_name", "phase_file"]}
                phase_data["tasks"][i] = clean_task
                break
        
        # Save back to file
        with open(phase_file, 'w') as f:
            yaml.dump(phase_data, f, default_flow_style=False, indent=2, sort_keys=False)
    
    def _update_legacy_tasks(self, task_id: str, updated_task: Dict):
        """Update a task in legacy tasks.yaml"""
        with open(self.tasks_file, 'r') as f:
            tasks_data = yaml.safe_load(f) or {"tasks": []}
        
        # Update the specific task
        for i, task in enumerate(tasks_data.get("tasks", [])):
            if task["id"] == task_id:
                # Remove phase metadata if it's a legacy task
                clean_task = {k: v for k, v in updated_task.items() 
                             if k not in ["phase_name", "phase_file"]}
                tasks_data["tasks"][i] = clean_task
                break
        
        # Save back to file
        with open(self.tasks_file, 'w') as f:
            yaml.dump(tasks_data, f, default_flow_style=False, indent=2, sort_keys=False)
    
    def get_context(self, context_paths: List[str]) -> str:
        """Retrieve context from specified paths - handles multiple locations"""
        context_content = []
        
        for path in context_paths:
            # Try multiple locations
            locations = [
                self.project_root / path,  # Direct path
                self.docs_dir / path,       # In docs/
                self.src_dir / path,        # In src/
                Path(path)                  # Absolute path
            ]
            
            found = False
            for location in locations:
                if location.exists() and location.is_file():
                    with open(location, 'r') as f:
                        content = f.read()
                        
                        # Handle section references (e.g., file.py#section)
                        if '#' in path:
                            section = path.split('#')[1]
                            # Simple section extraction (looks for function/class)
                            lines = content.split('\n')
                            section_content = []
                            in_section = False
                            
                            for line in lines:
                                if f"def {section}" in line or f"class {section}" in line:
                                    in_section = True
                                elif in_section and (line.startswith('def ') or 
                                                    line.startswith('class ') or 
                                                    line.strip() == ''):
                                    if line.strip() != '':
                                        break
                                
                                if in_section:
                                    section_content.append(line)
                            
                            content = '\n'.join(section_content) if section_content else content
                        
                        context_content.append(f"=== {path} ===\n{content}\n")
                        found = True
                        break
            
            if not found:
                context_content.append(f"=== {path} (NOT FOUND) ===\n")
                print(f"Warning: Context file not found: {path}")
        
        return "\n".join(context_content)
    
    def find_related_tasks(self, task_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find tasks related to the given task"""
        tasks_data = self.load_tasks()
        current_task = None
        
        # Find current task
        for task in tasks_data.get("tasks", []):
            if task["id"] == task_id:
                current_task = task
                break
        
        if not current_task:
            return []
        
        # Score other tasks for relevance
        related_tasks = []
        
        for task in tasks_data.get("tasks", []):
            if task["id"] == task_id or task.get("status") != "completed":
                continue
            
            score = 0
            
            # Same phase = high relevance
            if task.get("phase") == current_task.get("phase"):
                score += 10
            
            # Check for keyword matches in description
            current_keywords = set(re.findall(r'\w+', current_task.get("description", "").lower()))
            task_keywords = set(re.findall(r'\w+', task.get("description", "").lower()))
            
            # Remove common words
            common_words = {"the", "a", "an", "and", "or", "for", "to", "in", "of", "with", "from"}
            current_keywords -= common_words
            task_keywords -= common_words
            
            # Score based on keyword overlap
            if current_keywords and task_keywords:
                overlap = len(current_keywords & task_keywords)
                score += overlap * 2
            
            # Check if current task depends on this one
            if current_task.get("depends_on") and task["id"] in current_task.get("depends_on", []):
                score += 15
            
            # Check if they share dependencies
            if current_task.get("depends_on") and task.get("depends_on"):
                shared_deps = set(current_task["depends_on"]) & set(task["depends_on"])
                score += len(shared_deps) * 3
            
            if score > 0:
                related_tasks.append({
                    "task": task,
                    "score": score
                })
        
        # Sort by score and return top N
        related_tasks.sort(key=lambda x: x["score"], reverse=True)
        return [rt["task"] for rt in related_tasks[:limit]]
    
    def extract_decisions_from_task(self, task_id: str) -> List[str]:
        """Extract decisions from a task's context file"""
        decisions = []
        
        # Find context file
        tasks_data = self.load_tasks()
        task = next((t for t in tasks_data.get("tasks", []) if t["id"] == task_id), None)
        
        if not task:
            return decisions
        
        # Check phase-specific context
        phase = task.get("phase", 0)
        context_file = self.contexts_dir / f"phase{phase}" / f"context_{task_id}.md"
        
        # Fallback to legacy location
        if not context_file.exists():
            context_file = self.project_root / f".task_context_{task_id}.md"
        
        if not context_file.exists():
            return decisions
        
        # Read and extract decisions
        try:
            with open(context_file, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                # Look for decision indicators
                if any(keyword in line.lower() for keyword in 
                       ['decision:', 'decided to', 'chose', 'approach:', 'strategy:', 
                        'because', 'rationale:', 'reason:']):
                    # Clean up the line
                    line = re.sub(r'^[-*#]+\s*', '', line)  # Remove bullet points
                    if line and len(line) > 10:  # Meaningful content
                        decisions.append(line)
        
        except Exception as e:
            print(f"Error extracting decisions from {task_id}: {e}")
        
        return decisions
    
    def generate_architecture_context(self, task_id: str) -> str:
        """Generate architecture diagram showing where task fits"""
        tasks_data = self.load_tasks()
        task = next((t for t in tasks_data.get("tasks", []) if t["id"] == task_id), None)
        
        if not task:
            return ""
        
        # Get project name from config
        project_name = self.get_project_info()['name']
        
        # Determine which component this task affects
        task_desc = task.get("description", "").lower()
        task_output = task.get("output", "").lower()
        task_id_lower = task_id.lower()
        
        # More specific component detection - order matters!
        component = "Unknown Component"
        combined_text = task_desc + " " + task_output + " " + task_id_lower
        
        # Check most specific patterns first
        if "session" in combined_text and "tracking" in combined_text:
            component = "Session Tracking System"
        elif "context" in combined_text and "enhance" in combined_text:
            component = "Context System"
        elif any(term in combined_text for term in ["blueprint", "generator"]) and "context" not in combined_text:
            component = "Blueprint Generator"
        elif any(term in combined_text for term in ["cli", "command", "task.py"]):
            component = "CLI Interface"
        elif any(term in combined_text for term in ["web", "ui", "dashboard", "complete.py"]):
            component = "Web Dashboard"
        elif any(term in combined_text for term in ["taskmanager", "task manager", "task_manager"]):
            component = "TaskManager Core"
        elif any(term in combined_text for term in ["config", "bruce.yaml", "configuration"]):
            component = "Configuration System"
        
        # Generate simple ASCII diagram
        diagram = f"""
## Architecture Context: Where This Task Fits

Current Task: {task_id}
Component: {component}
Project: {project_name}

System Overview:
┌─────────────────────┐     ┌─────────────────────┐
│   CLI Interface     │     │   Web Dashboard     │
│  (hdw-task.py)     │     │  (hdw_complete.py)  │
└──────────┬──────────┘     └──────────┬──────────┘
           │                           │
           └─────────┬─────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   TaskManager Core    │{' ← YOU ARE HERE' if component == 'TaskManager Core' else ''}
         │  (task_manager.py)    │
         └───────────┬───────────┘
                     │
        ┌────────────┼────────────────────┐
        │            │                    │
        ▼            ▼                    ▼
┌─────────────┐ ┌─────────────┐ ┌──────────────────┐
│ Config Sys  │ │Context Sys  │ │Session Tracking  │{' ← YOU ARE HERE' if component == 'Session Tracking System' else ''}
│(config mgr) │{' ← YOU ARE HERE' if component == 'Configuration System' else ''} │(contexts/) │{' ← YOU ARE HERE' if component == 'Context System' else ''} │ (sessions/)      │
└─────────────┘ └─────────────┘ └──────────────────┘
                                           │
                                           ▼
                                 ┌─────────────────┐
                                 │Blueprint Gen    │{' ← YOU ARE HERE' if component == 'Blueprint Generator' else ''}
                                 │(blueprints)     │
                                 └─────────────────┘

Data Flow:
1. User triggers task via CLI/Web
2. TaskManager processes request  
3. Session Tracking monitors work
4. Config System provides settings
5. Context System generates/reads context
6. Work happens (YOU!)
7. Session captures changes
8. Blueprint Generator creates documentation
"""
        
        # Add component-specific notes
        if component == "CLI Interface":
            diagram = diagram.replace("│   CLI Interface     │", "│   CLI Interface     │ ← YOU ARE HERE")
        elif component == "Web Dashboard":
            diagram = diagram.replace("│   Web Dashboard     │", "│   Web Dashboard     │ ← YOU ARE HERE")
        
        return diagram
    
    def generate_enhanced_context(self, task_id: str) -> str:
        """Generate enhanced context with related tasks, architecture, and decisions"""
        tasks_data = self.load_tasks()
        task = next((t for t in tasks_data.get("tasks", []) if t["id"] == task_id), None)
        
        if not task:
            return f"Task {task_id} not found"
        
        # Get project info
        project_info = self.get_project_info()
        
        # Build enhanced context
        context_parts = []
        
        # 1. Basic task information
        context_parts.append(f"# Context for Task: {task_id}\n")
        context_parts.append(f"**Project:** {project_info['name']}")
        context_parts.append(f"**Phase:** {task.get('phase', 0)} - {task.get('phase_name', 'Legacy')}")
        context_parts.append(f"**Description:** {task['description']}")
        context_parts.append(f"**Expected Output:** {task.get('output', 'Not specified')}\n")
        
        if task.get('acceptance_criteria'):
            context_parts.append("**Acceptance Criteria:**")
            for criteria in task['acceptance_criteria']:
                context_parts.append(f"- {criteria}")
            context_parts.append("")
        
        if task.get('depends_on'):
            context_parts.append(f"**Dependencies:** {', '.join(task['depends_on'])}\n")
        
        # 2. Session tracking information
        session_summary = self.get_session_summary(task_id)
        if session_summary["total_sessions"] > 0:
            context_parts.append("## Previous Work Sessions\n")
            context_parts.append(f"**Total Sessions:** {session_summary['total_sessions']}")
            context_parts.append(f"**Total Time Spent:** {session_summary['total_duration_formatted']}")
            context_parts.append(f"**Files Modified:** {session_summary['total_files_modified']}")
            context_parts.append(f"**Commits Made:** {session_summary['total_commits']}")
            
            if session_summary["last_session"]:
                last = session_summary["last_session"]
                context_parts.append(f"\n**Last Session:**")
                context_parts.append(f"- Started: {last['start_time'][:19]}")
                if last.get('end_time'):
                    context_parts.append(f"- Duration: {timedelta(seconds=int(last['duration_seconds']))}")
                context_parts.append("")
        
        # 3. Configuration context
        if self.config:
            context_parts.append("## Project Configuration\n")
            context_parts.append(f"- **Config loaded:** {'Yes' if project_info['config_loaded'] else 'No (using defaults)'}")
            context_parts.append(f"- **Project type:** {project_info['type']}")
            context_parts.append(f"- **Contexts directory:** {self.config.bruce.contexts_dir}")
            context_parts.append(f"- **Blueprints directory:** {self.config.bruce.blueprints_dir}")
            context_parts.append("")
        
        # 4. Architecture context
        arch_context = self.generate_architecture_context(task_id)
        if arch_context:
            context_parts.append(arch_context)
        
        # 5. Related completed tasks
        related_tasks = self.find_related_tasks(task_id)
        if related_tasks:
            context_parts.append("## Related Completed Tasks\n")
            context_parts.append("These completed tasks might provide useful context:\n")
            
            for related_task in related_tasks:
                context_parts.append(f"### {related_task['id']}: {related_task['description']}")
                context_parts.append(f"- **Output:** {related_task.get('output', 'Not specified')}")
                context_parts.append(f"- **Status:** {related_task.get('status', 'unknown')}")
                
                # Include key decisions from related task
                decisions = self.extract_decisions_from_task(related_task['id'])
                if decisions:
                    context_parts.append("- **Key Decisions:**")
                    for decision in decisions[:2]:  # Limit to 2 most relevant
                        context_parts.append(f"  - {decision}")
                
                context_parts.append("")
        
        # 6. Decision history from phase
        context_parts.append("## Decision History\n")
        context_parts.append("Key decisions from this phase that may impact your work:\n")
        
        phase_tasks = [t for t in tasks_data.get("tasks", []) 
                      if t.get("phase") == task.get("phase") and 
                      t.get("status") == "completed"]
        
        all_decisions = []
        for phase_task in phase_tasks:
            decisions = self.extract_decisions_from_task(phase_task["id"])
            for decision in decisions:
                all_decisions.append(f"- **{phase_task['id']}:** {decision}")
        
        if all_decisions:
            # Show up to 5 most relevant decisions
            for decision in all_decisions[:5]:
                context_parts.append(decision)
        else:
            context_parts.append("- No previous decisions found in this phase")
        
        context_parts.append("")
        
        # 7. Original context files
        context_parts.append("## Context Documentation:\n")
        if task.get("context"):
            context = self.get_context(task["context"])
            context_parts.append(context)
        else:
            context_parts.append("No additional context files specified.\n")
        
        return "\n".join(context_parts)
    
    def cmd_start(self, task_id: str, enhanced: bool = True):
        """Start working on a task - with optional enhanced context and session tracking"""
        tasks_data = self.load_tasks()
        task = None
        
        for t in tasks_data.get("tasks", []):
            if t["id"] == task_id:
                task = t
                break
        
        if not task:
            print(f"❌ Task '{task_id}' not found")
            return
        
        project_info = self.get_project_info()
        print(f"🚀 Starting task: {task_id}")
        print(f"📁 Project: {project_info['name']}")
        if task.get("phase"):
            print(f"📁 Phase {task['phase']}: {task.get('phase_name', 'Unknown')}")
        print(f"📝 Description: {task['description']}")
        
        # Start session tracking
        session = self.start_task_session(task_id)
        print(f"⏱️  Session tracking started at {session.start_time.strftime('%I:%M %p')}")
        
        # Update status
        self.save_task_updates(task_id, {
            "status": "in-progress",
            "updated": datetime.now().isoformat(),
            "notes": task.get("notes", []) + [{
                "timestamp": datetime.now().isoformat(),
                "note": f"Task started with session tracking"
            }]
        })
        
        # Create organized context file
        phase_dir = self.contexts_dir / f"phase{task.get('phase', 0)}"
        phase_dir.mkdir(exist_ok=True)
        
        context_file = phase_dir / f"context_{task_id}.md"
        
        # Generate context (enhanced or basic)
        if enhanced:
            print("✨ Generating enhanced context with related tasks and architecture...")
            context_content = self.generate_enhanced_context(task_id)
        else:
            # Original basic context
            context_content = f"# Context for Task: {task_id}\n\n"
            context_content += f"**Project:** {project_info['name']}\n"
            context_content += f"**Phase:** {task.get('phase', 0)} - {task.get('phase_name', 'Legacy')}\n"
            context_content += f"**Description:** {task['description']}\n\n"
            context_content += f"**Expected Output:** {task.get('output', 'Not specified')}\n\n"
            
            if task.get('acceptance_criteria'):
                context_content += "**Acceptance Criteria:**\n"
                for criteria in task['acceptance_criteria']:
                    context_content += f"- {criteria}\n"
                context_content += "\n"
            
            if task.get('depends_on'):
                context_content += f"**Dependencies:** {', '.join(task['depends_on'])}\n\n"
            
            context_content += "## Context Documentation:\n\n"
            
            if task.get("context"):
                context = self.get_context(task["context"])
                context_content += context
            else:
                context_content += "No context files specified.\n"
        
        # Save context file
        with open(context_file, 'w') as f:
            f.write(context_content)
        
        # Add context snapshot to session
        session.capture_context_snapshot(context_content[:500] + "...")  # First 500 chars
        
        print(f"✓ Context saved to: {context_file}")
        print(f"\n💡 Ready for implementation!")
        print(f"   Session is being tracked - all changes will be monitored")
        print(f"   Use 'hdw-task commit {task_id}' when complete")
    
    def get_phase_progress(self) -> Dict[int, Dict[str, Any]]:
        """Calculate progress for each phase"""
        tasks_data = self.load_tasks()
        phase_progress = {}
        
        # Initialize phases
        for phase_id, phase_info in tasks_data.get("phases", {}).items():
            try:
                phase_id_int = int(phase_id)
                phase_progress[phase_id_int] = {
                    "name": phase_info["name"],
                    "total": 0,
                    "completed": 0,
                    "in_progress": 0,
                    "pending": 0,
                    "blocked": 0
                }
            except (ValueError, TypeError):
                continue
        
        # Count tasks by phase and status
        for task in tasks_data.get("tasks", []):
            phase = task.get("phase", 0)
            if phase not in phase_progress:
                phase_progress[phase] = {
                    "name": "Legacy Tasks",
                    "total": 0,
                    "completed": 0,
                    "in_progress": 0,
                    "pending": 0,
                    "blocked": 0
                }
            
            phase_progress[phase]["total"] += 1
            status = task.get("status", "pending")
            status_key = status.replace('-', '_')  # Convert in-progress to in_progress
            if status_key in phase_progress[phase]:
                phase_progress[phase][status_key] += 1
        
        # Calculate percentages
        for phase_id, progress in phase_progress.items():
            if progress["total"] > 0:
                progress["percentage"] = (progress["completed"] / progress["total"]) * 100
            else:
                progress["percentage"] = 0
        
        return phase_progress

# Create backward-compatible wrapper functions
def main():
    """Maintain CLI compatibility with enhanced features"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bruce Task Management CLI")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # ... (keep existing CLI structure, just use TaskManager class)
    
    args = parser.parse_args()
    
    # Initialize enhanced task manager
    task_manager = TaskManager(args.project_root)
    
    # Restore any active sessions
    task_manager.restore_active_sessions()
    
    # Route commands to TaskManager methods
    # (Implementation continues with existing CLI structure...)

if __name__ == "__main__":
    print("This is the enhanced task manager library with session tracking.")
    print("Import and use the TaskManager class in your code.")
    print("Or update hdw-task.py to use this implementation.")