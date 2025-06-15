#!/usr/bin/env python3
"""
Task Session Tracker - Enhanced Implementation
Provides real-time session tracking with intelligent change monitoring
Integrates seamlessly with existing Bruce TaskManager system

Save as: src/task_session_tracker.py
"""

import os
import json
import time
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
import threading
import psutil
import yaml

@dataclass
class FileChange:
    """Represents a file modification during session"""
    filepath: str
    change_type: str  # 'created', 'modified', 'deleted'
    timestamp: str
    size_before: int
    size_after: int
    lines_added: int = 0
    lines_removed: int = 0
    
@dataclass
class SessionNote:
    """Contextual note captured during session"""
    timestamp: str
    note: str
    category: str  # 'decision', 'problem', 'solution', 'context'
    file_context: Optional[str] = None

@dataclass
class SessionMetrics:
    """Session performance and activity metrics"""
    start_time: str
    end_time: Optional[str]
    duration_seconds: int
    files_created: int
    files_modified: int
    files_deleted: int
    total_lines_added: int
    total_lines_removed: int
    git_commits: int
    notes_captured: int
    cpu_time_used: float
    memory_peak_mb: float

class TaskSessionTracker:
    """
    Real-time session tracking for Bruce tasks with intelligent monitoring
    
    Features:
    - File change detection and analysis
    - Git integration and commit tracking
    - Contextual note capture
    - Performance metrics
    - Session pause/resume
    - Rich handoff generation
    """
    
    def __init__(self, task_id: str, project_root: Path, task_manager=None):
        self.task_id = task_id
        self.project_root = project_root
        self.task_manager = task_manager
        
        # Session state
        self.session_start = datetime.now()
        self.session_end = None
        self.is_active = False
        self.is_paused = False
        self.pause_start = None
        self.total_pause_time = 0
        
        # Tracking data
        self.file_changes: List[FileChange] = []
        self.session_notes: List[SessionNote] = []
        self.git_commits: List[Dict[str, Any]] = []
        self.file_baselines: Dict[str, Dict] = {}
        
        # Performance monitoring
        self.process = psutil.Process()
        self.start_cpu_time = self.process.cpu_times()
        self.peak_memory = 0
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        # Session file paths
        self.sessions_dir = project_root / "docs" / "sessions" / "active"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.sessions_dir / f"session_{task_id}_{int(time.time())}.json"
        self.context_file = project_root / "contexts" / f"phase3" / f"session_context_{task_id}.md"
        
        # Monitored directories (avoid noise from system files)
        self.monitored_dirs = [
            project_root / "src",
            project_root / "cli", 
            project_root / "templates",
            project_root / "phases",
            project_root / "tests",
            project_root / "docs",
            project_root / "configs"
        ]
        
    def start_session(self):
        """Initialize session tracking with file baseline and monitoring"""
        print(f"🎯 Starting session tracking for task: {self.task_id}")
        
        self.is_active = True
        self.session_start = datetime.now()
        
        # Capture initial file states
        print("📸 Capturing initial file baseline...")
        self._capture_file_baseline()
        
        # Initialize git tracking
        self._capture_initial_git_state()
        
        # Start performance monitoring
        self._start_performance_monitoring()
        
        # Save initial session state
        self._save_session_state()
        
        print(f"✅ Session tracking active. Monitor file: {self.session_file}")
        return True
        
    def pause_session(self):
        """Pause session tracking (useful for breaks/interruptions)"""
        if not self.is_active or self.is_paused:
            return False
            
        self.is_paused = True
        self.pause_start = datetime.now()
        print(f"⏸️  Session paused at {self.pause_start.strftime('%H:%M:%S')}")
        self._save_session_state()
        return True
        
    def resume_session(self):
        """Resume paused session tracking"""
        if not self.is_active or not self.is_paused:
            return False
            
        if self.pause_start:
            pause_duration = (datetime.now() - self.pause_start).total_seconds()
            self.total_pause_time += pause_duration
            
        self.is_paused = False
        self.pause_start = None
        print(f"▶️  Session resumed")
        self._save_session_state()
        return True
        
    def capture_note(self, note: str, category: str = "context", file_context: str = None):
        """Capture contextual note during active session"""
        if not self.is_active:
            return False
            
        session_note = SessionNote(
            timestamp=datetime.now().isoformat(),
            note=note,
            category=category,
            file_context=file_context
        )
        
        self.session_notes.append(session_note)
        print(f"📝 Note captured: [{category.upper()}] {note}")
        self._save_session_state()
        return True
        
    def scan_changes(self):
        """Scan for file changes since session start"""
        if not self.is_active:
            return []
            
        new_changes = []
        
        for monitor_dir in self.monitored_dirs:
            if not monitor_dir.exists():
                continue
                
            for file_path in monitor_dir.rglob("*"):
                if file_path.is_file() and not self._should_ignore_file(file_path):
                    change = self._analyze_file_change(file_path)
                    if change:
                        new_changes.append(change)
                        
        # Update git commits
        self._update_git_commits()
        
        # Save updated state
        if new_changes:
            self.file_changes.extend(new_changes)
            self._save_session_state()
            
        return new_changes
        
    def end_session(self, completion_status: str = "completed", final_note: str = None):
        """Finalize session with comprehensive summary"""
        if not self.is_active:
            return None
            
        print(f"🏁 Ending session for task: {self.task_id}")
        
        # Final scan for changes
        self.scan_changes()
        
        # Add final note if provided
        if final_note:
            self.capture_note(final_note, "completion")
            
        # Stop monitoring
        self.is_active = False
        self.session_end = datetime.now()
        self.stop_monitoring.set()
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2)
            
        # Generate final metrics
        metrics = self._generate_session_metrics()
        
        # Generate comprehensive handoff document
        handoff_doc = self._generate_handoff_document(completion_status, metrics)
        
        # Save final session state
        session_data = self._get_session_data()
        session_data['completion_status'] = completion_status
        session_data['metrics'] = asdict(metrics)
        session_data['handoff_document'] = handoff_doc
        
        # Move from active to completed sessions
        completed_dir = self.project_root / "docs" / "sessions" / "completed"
        completed_dir.mkdir(parents=True, exist_ok=True)
        
        final_session_file = completed_dir / f"session_{self.task_id}_{self.session_start.strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(final_session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
            
        # Save handoff document
        handoff_file = completed_dir / f"handoff_{self.task_id}_{self.session_start.strftime('%Y%m%d_%H%M%S')}.md"
        with open(handoff_file, 'w') as f:
            f.write(handoff_doc)
            
        # Clean up active session file
        if self.session_file.exists():
            self.session_file.unlink()
            
        print(f"✅ Session completed: {final_session_file.name}")
        print(f"📋 Handoff document: {handoff_file.name}")
        
        return {
            'session_file': str(final_session_file),
            'handoff_file': str(handoff_file),
            'metrics': asdict(metrics),
            'handoff_document': handoff_doc
        }
        
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status and metrics"""
        if not self.is_active:
            return {'active': False}
            
        current_time = datetime.now()
        
        # Calculate active duration (excluding pauses)
        if self.is_paused and self.pause_start:
            active_duration = (self.pause_start - self.session_start).total_seconds() - self.total_pause_time
            current_status = "paused"
        else:
            active_duration = (current_time - self.session_start).total_seconds() - self.total_pause_time
            current_status = "active"
            
        # Get current memory usage
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = max(self.peak_memory, current_memory)
        
        return {
            'active': True,
            'status': current_status,
            'task_id': self.task_id,
            'start_time': self.session_start.isoformat(),
            'active_duration_seconds': int(active_duration),
            'active_duration_formatted': str(timedelta(seconds=int(active_duration))),
            'total_pause_time_seconds': int(self.total_pause_time),
            'files_changed': len(self.file_changes),
            'notes_captured': len(self.session_notes),
            'git_commits': len(self.git_commits),
            'current_memory_mb': round(current_memory, 2),
            'peak_memory_mb': round(self.peak_memory, 2),
            'last_activity': self.file_changes[-1].timestamp if self.file_changes else None
        }
        
    # Private helper methods
    def _capture_file_baseline(self):
        """Capture initial state of all monitored files"""
        for monitor_dir in self.monitored_dirs:
            if not monitor_dir.exists():
                continue
                
            for file_path in monitor_dir.rglob("*"):
                if file_path.is_file() and not self._should_ignore_file(file_path):
                    try:
                        stat = file_path.stat()
                        self.file_baselines[str(file_path)] = {
                            'size': stat.st_size,
                            'mtime': stat.st_mtime,
                            'checksum': self._calculate_file_checksum(file_path),
                            'line_count': self._count_lines(file_path) if file_path.suffix in ['.py', '.yaml', '.yml', '.md', '.txt'] else 0
                        }
                    except (OSError, PermissionError):
                        continue
                        
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored from tracking"""
        ignore_patterns = [
            '__pycache__', '.pyc', '.git', '.gitignore', 
            'node_modules', '.DS_Store', 'Thumbs.db',
            '.pytest_cache', '.coverage', '*.log'
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in ignore_patterns)
        
    def _analyze_file_change(self, file_path: Path) -> Optional[FileChange]:
        """Analyze if file has changed and return change details"""
        file_str = str(file_path)
        
        try:
            current_stat = file_path.stat()
            current_checksum = self._calculate_file_checksum(file_path)
            current_lines = self._count_lines(file_path) if file_path.suffix in ['.py', '.yaml', '.yml', '.md', '.txt'] else 0
            
            baseline = self.file_baselines.get(file_str)
            
            if baseline is None:
                # New file created
                change = FileChange(
                    filepath=str(file_path.relative_to(self.project_root)),
                    change_type='created',
                    timestamp=datetime.now().isoformat(),
                    size_before=0,
                    size_after=current_stat.st_size,
                    lines_added=current_lines
                )
                
                # Update baseline
                self.file_baselines[file_str] = {
                    'size': current_stat.st_size,
                    'mtime': current_stat.st_mtime,
                    'checksum': current_checksum,
                    'line_count': current_lines
                }
                return change
                
            elif baseline['checksum'] != current_checksum:
                # File modified
                lines_diff = current_lines - baseline['line_count']
                
                change = FileChange(
                    filepath=str(file_path.relative_to(self.project_root)),
                    change_type='modified',
                    timestamp=datetime.now().isoformat(),
                    size_before=baseline['size'],
                    size_after=current_stat.st_size,
                    lines_added=max(0, lines_diff),
                    lines_removed=max(0, -lines_diff)
                )
                
                # Update baseline
                baseline.update({
                    'size': current_stat.st_size,
                    'mtime': current_stat.st_mtime,
                    'checksum': current_checksum,
                    'line_count': current_lines
                })
                return change
                
        except (OSError, PermissionError):
            pass
            
        return None
        
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (OSError, PermissionError):
            return ""
            
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except (OSError, UnicodeDecodeError):
            return 0
            
    def _capture_initial_git_state(self):
        """Capture initial git state"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                self.initial_git_commit = result.stdout.strip()
            else:
                self.initial_git_commit = None
        except FileNotFoundError:
            self.initial_git_commit = None
            
    def _update_git_commits(self):
        """Check for new git commits since session start"""
        if not self.initial_git_commit:
            return
            
        try:
            # Get commits since session start
            result = subprocess.run([
                "git", "log", "--oneline", "--since", self.session_start.isoformat()
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                commit_lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                
                # Update git commits list
                new_commits = []
                for line in commit_lines:
                    if line:
                        parts = line.split(' ', 1)
                        if len(parts) == 2:
                            commit_hash, message = parts
                            commit_data = {
                                'hash': commit_hash,
                                'message': message,
                                'timestamp': datetime.now().isoformat()
                            }
                            if commit_data not in self.git_commits:
                                new_commits.append(commit_data)
                                
                self.git_commits.extend(new_commits)
                
        except FileNotFoundError:
            pass
            
    def _start_performance_monitoring(self):
        """Start background thread for performance monitoring"""
        def monitor():
            while not self.stop_monitoring.wait(30):  # Check every 30 seconds
                try:
                    current_memory = self.process.memory_info().rss / 1024 / 1024
                    self.peak_memory = max(self.peak_memory, current_memory)
                except psutil.NoSuchProcess:
                    break
                    
        self.monitoring_thread = threading.Thread(target=monitor, daemon=True)
        self.monitoring_thread.start()
        
    def _generate_session_metrics(self) -> SessionMetrics:
        """Generate comprehensive session metrics"""
        end_time = self.session_end or datetime.now()
        duration = (end_time - self.session_start).total_seconds() - self.total_pause_time
        
        # Calculate CPU time used
        try:
            current_cpu_time = self.process.cpu_times()
            cpu_time_used = (current_cpu_time.user - self.start_cpu_time.user + 
                           current_cpu_time.system - self.start_cpu_time.system)
        except psutil.NoSuchProcess:
            cpu_time_used = 0
            
        # Aggregate file statistics
        files_created = sum(1 for change in self.file_changes if change.change_type == 'created')
        files_modified = sum(1 for change in self.file_changes if change.change_type == 'modified')
        files_deleted = sum(1 for change in self.file_changes if change.change_type == 'deleted')
        
        total_lines_added = sum(change.lines_added for change in self.file_changes)
        total_lines_removed = sum(change.lines_removed for change in self.file_changes)
        
        return SessionMetrics(
            start_time=self.session_start.isoformat(),
            end_time=end_time.isoformat(),
            duration_seconds=int(duration),
            files_created=files_created,
            files_modified=files_modified,
            files_deleted=files_deleted,
            total_lines_added=total_lines_added,
            total_lines_removed=total_lines_removed,
            git_commits=len(self.git_commits),
            notes_captured=len(self.session_notes),
            cpu_time_used=cpu_time_used,
            memory_peak_mb=self.peak_memory
        )
        
    def _generate_handoff_document(self, completion_status: str, metrics: SessionMetrics) -> str:
        """Generate comprehensive Claude handoff document"""
        
        handoff = f"""# 🤝 Task Session Handoff: {self.task_id}

**Session Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Task Status:** {completion_status.upper()}
**Duration:** {str(timedelta(seconds=metrics.duration_seconds))}

## 📊 Session Summary

### Performance Metrics
- **Active Time:** {str(timedelta(seconds=metrics.duration_seconds))}
- **Files Created:** {metrics.files_created}
- **Files Modified:** {metrics.files_modified}
- **Lines Added:** {metrics.total_lines_added:,}
- **Lines Removed:** {metrics.total_lines_removed:,}
- **Git Commits:** {metrics.git_commits}
- **Peak Memory:** {metrics.memory_peak_mb:.1f} MB
- **CPU Time:** {metrics.cpu_time_used:.2f}s

### File Changes Summary
"""
        
        # Group file changes by type
        if self.file_changes:
            handoff += "\n**Files Modified:**\n"
            for change in self.file_changes:
                if change.change_type == 'modified':
                    handoff += f"- `{change.filepath}` (+{change.lines_added}/-{change.lines_removed} lines)\n"
                    
            created_files = [c for c in self.file_changes if c.change_type == 'created']
            if created_files:
                handoff += "\n**Files Created:**\n"
                for change in created_files:
                    handoff += f"- `{change.filepath}` ({change.lines_added} lines)\n"
        else:
            handoff += "- No file changes detected\n"
            
        # Add git commits
        if self.git_commits:
            handoff += f"\n### Git Commits ({len(self.git_commits)})\n"
            for commit in self.git_commits[-5:]:  # Show last 5 commits
                handoff += f"- `{commit['hash']}`: {commit['message']}\n"
                
        # Add session notes by category
        if self.session_notes:
            handoff += f"\n### Session Notes ({len(self.session_notes)})\n"
            
            categories = {}
            for note in self.session_notes:
                if note.category not in categories:
                    categories[note.category] = []
                categories[note.category].append(note)
                
            for category, notes in categories.items():
                handoff += f"\n**{category.title()} Notes:**\n"
                for note in notes:
                    timestamp = datetime.fromisoformat(note.timestamp).strftime('%H:%M')
                    handoff += f"- [{timestamp}] {note.note}\n"
                    if note.file_context:
                        handoff += f"  - Context: `{note.file_context}`\n"
                        
        # Add context for next session
        handoff += f"""
## 🎯 Context for Next Session

### Current State
The task `{self.task_id}` has been marked as **{completion_status}**.

### Key Accomplishments
"""
        
        if metrics.files_created > 0:
            handoff += f"- Created {metrics.files_created} new files\n"
        if metrics.files_modified > 0:
            handoff += f"- Modified {metrics.files_modified} existing files\n"
        if metrics.total_lines_added > 0:
            handoff += f"- Added {metrics.total_lines_added:,} lines of code/content\n"
        if metrics.git_commits > 0:
            handoff += f"- Made {metrics.git_commits} git commits\n"
            
        # Add decision trail from notes
        decision_notes = [n for n in self.session_notes if n.category == 'decision']
        if decision_notes:
            handoff += f"\n### Key Decisions Made\n"
            for note in decision_notes:
                handoff += f"- {note.note}\n"
                
        # Add any problems encountered
        problem_notes = [n for n in self.session_notes if n.category == 'problem']
        if problem_notes:
            handoff += f"\n### Problems Encountered\n"
            for note in problem_notes:
                handoff += f"- {note.note}\n"
                
        handoff += f"""
### Ready for Next Session
This task session has been completed and all context captured. The next Claude session can continue with full understanding of what was accomplished and any decisions made.

**Session tracking data saved to:** `docs/sessions/completed/`
**Integration points verified:** TaskManager session tracking active

---
*Generated by Bruce Task Session Tracker v1.0*
"""
        
        return handoff
        
    def _get_session_data(self) -> Dict[str, Any]:
        """Get complete session data for serialization"""
        return {
            'task_id': self.task_id,
            'start_time': self.session_start.isoformat(),
            'end_time': self.session_end.isoformat() if self.session_end else None,
            'is_active': self.is_active,
            'is_paused': self.is_paused,
            'total_pause_time_seconds': self.total_pause_time,
            'file_changes': [asdict(change) for change in self.file_changes],
            'session_notes': [asdict(note) for note in self.session_notes],
            'git_commits': self.git_commits,
            'peak_memory_mb': self.peak_memory
        }
        
    def _save_session_state(self):
        """Save current session state to file"""
        if self.is_active:
            with open(self.session_file, 'w') as f:
                json.dump(self._get_session_data(), f, indent=2, default=str)


# Integration functions for existing Bruce system
def get_active_session(task_id: str, project_root: Path) -> Optional[TaskSessionTracker]:
    """Get active session for task if exists"""
    sessions_dir = project_root / "docs" / "sessions" / "active"
    
    if not sessions_dir.exists():
        return None
        
    for session_file in sessions_dir.glob(f"session_{task_id}_*.json"):
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
                
            if session_data.get('is_active', False):
                # Reconstruct session tracker
                tracker = TaskSessionTracker(task_id, project_root)
                tracker.session_start = datetime.fromisoformat(session_data['start_time'])
                tracker.is_active = session_data['is_active']
                tracker.is_paused = session_data.get('is_paused', False)
                tracker.total_pause_time = session_data.get('total_pause_time_seconds', 0)
                tracker.peak_memory = session_data.get('peak_memory_mb', 0)
                
                # Restore file changes
                for change_data in session_data.get('file_changes', []):
                    tracker.file_changes.append(FileChange(**change_data))
                    
                # Restore notes
                for note_data in session_data.get('session_notes', []):
                    tracker.session_notes.append(SessionNote(**note_data))
                    
                tracker.git_commits = session_data.get('git_commits', [])
                tracker.session_file = session_file
                
                return tracker
                
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
            
    return None

def list_completed_sessions(project_root: Path, task_id: str = None) -> List[Dict[str, Any]]:
    """List completed sessions for project or specific task"""
    completed_dir = project_root / "docs" / "sessions" / "completed"
    
    if not completed_dir.exists():
        return []
        
    sessions = []
    pattern = f"session_{task_id}_*" if task_id else "session_*"
    
    for session_file in completed_dir.glob(f"{pattern}.json"):
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
                
            summary = {
                'task_id': session_data['task_id'],
                'session_file': str(session_file),
                'start_time': session_data['start_time'],
                'end_time': session_data.get('end_time'),
                'completion_status': session_data.get('completion_status', 'unknown'),
                'duration_seconds': session_data.get('metrics', {}).get('duration_seconds', 0),
                'files_modified': len(session_data.get('file_changes', [])),
                'notes_captured': len(session_data.get('session_notes', []))
            }
            
            sessions.append(summary)
            
        except (json.JSONDecodeError, KeyError):
            continue
            
    return sorted(sessions, key=lambda x: x['start_time'], reverse=True)