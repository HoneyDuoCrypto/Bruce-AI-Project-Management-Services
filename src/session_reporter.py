#!/usr/bin/env python3
"""
Session Reporter for Bruce Task Management
Generates detailed session reports for task handoffs and analysis
Save as: src/session_reporter.py
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

class SessionReporter:
    """Generate comprehensive session reports for tasks"""
    
    def __init__(self, task_manager):
        self.task_manager = task_manager
        self.project_root = task_manager.project_root
    
    def generate_session_report(self, task_id: str) -> str:
        """Generate detailed session report for handoffs"""
        summary = self.task_manager.get_session_summary(task_id)
        sessions = self.task_manager.get_task_sessions(task_id)
        tasks_data = self.task_manager.load_tasks()
        
        # Find task details
        task = next((t for t in tasks_data.get("tasks", []) if t["id"] == task_id), None)
        if not task:
            return f"Task {task_id} not found"
        
        report = f"""# 📊 Session Report: {task_id}

**Task:** {task.get('description', 'No description')}
**Phase:** {task.get('phase', 0)} - {task.get('phase_name', 'Unknown')}
**Status:** {task.get('status', 'pending')}

## 📈 Session Summary

- **Total Sessions:** {summary['total_sessions']}
- **Total Time Spent:** {summary['total_duration_formatted']}
- **Files Modified:** {summary['total_files_modified']}
- **Git Commits:** {summary['total_commits']}

"""
        
        # Add file change summary
        if summary['files_modified']:
            report += "## 📁 Files Changed\n\n"
            for file_path in sorted(summary['files_modified']):
                relative_path = self._get_relative_path(file_path)
                report += f"- `{relative_path}`\n"
            report += "\n"
        
        # Add commit summary
        if summary['commits']:
            report += "## 🔄 Git Commits\n\n"
            for commit in summary['commits']:
                report += f"- {commit}\n"
            report += "\n"
        
        # Add session timeline
        report += "## ⏱️ Session Timeline\n\n"
        
        for i, session in enumerate(sessions):
            session_num = i + 1
            start_time = datetime.fromisoformat(session['start_time'])
            
            report += f"### Session {session_num}\n\n"
            report += f"- **Started:** {start_time.strftime('%Y-%m-%d %I:%M %p')}\n"
            
            if session.get('end_time'):
                end_time = datetime.fromisoformat(session['end_time'])
                duration = timedelta(seconds=int(session['duration_seconds']))
                report += f"- **Ended:** {end_time.strftime('%Y-%m-%d %I:%M %p')}\n"
                report += f"- **Duration:** {duration}\n"
            else:
                report += f"- **Status:** 🔴 Active Session\n"
            
            # Files changed in this session
            files_changed = len(session.get('files_modified', []))
            files_created = len(session.get('files_created', []))
            files_deleted = len(session.get('files_deleted', []))
            
            if files_changed or files_created or files_deleted:
                report += f"- **Changes:** "
                changes = []
                if files_changed:
                    changes.append(f"{files_changed} modified")
                if files_created:
                    changes.append(f"{files_created} created")
                if files_deleted:
                    changes.append(f"{files_deleted} deleted")
                report += ", ".join(changes) + "\n"
            
            # Session notes
            if session.get('session_notes'):
                report += "- **Notes:**\n"
                for note in session['session_notes']:
                    timestamp = datetime.fromisoformat(note['timestamp'])
                    report += f"  - [{timestamp.strftime('%I:%M %p')}] {note['note']}\n"
            
            report += "\n"
        
        # Add recommendations
        report += self._generate_recommendations(summary, sessions)
        
        return report
    
    def generate_handoff_supplement(self, task_id: str) -> str:
        """Generate session supplement for Claude handoff reports"""
        summary = self.task_manager.get_session_summary(task_id)
        
        if summary['total_sessions'] == 0:
            return ""
        
        supplement = f"""
## 🔄 Work Session Information

**Time Investment:** {summary['total_duration_formatted']} across {summary['total_sessions']} session(s)
**Code Changes:** {summary['total_files_modified']} files modified
**Version Control:** {summary['total_commits']} commits made
"""
        
        # Add last session info if available
        if summary.get('last_session'):
            last = summary['last_session']
            if last.get('session_notes'):
                supplement += "\n**Last Session Notes:**\n"
                for note in last['session_notes'][-3:]:  # Last 3 notes
                    supplement += f"- {note['note']}\n"
        
        # Key files for handoff
        if summary['files_modified']:
            supplement += "\n**Key Modified Files:**\n"
            for file_path in list(summary['files_modified'])[:5]:  # Top 5 files
                relative_path = self._get_relative_path(file_path)
                supplement += f"- `{relative_path}`\n"
        
        return supplement
    
    def generate_phase_session_summary(self, phase_id: int) -> str:
        """Generate session summary for an entire phase"""
        tasks_data = self.task_manager.load_tasks()
        phase_tasks = [t for t in tasks_data.get("tasks", []) if t.get("phase") == phase_id]
        
        total_time = 0
        total_sessions = 0
        total_files = set()
        total_commits = []
        
        report = f"## 📊 Phase {phase_id} Session Statistics\n\n"
        
        for task in phase_tasks:
            summary = self.task_manager.get_session_summary(task['id'])
            if summary['total_sessions'] > 0:
                total_time += summary['total_duration_seconds']
                total_sessions += summary['total_sessions']
                total_files.update(summary['files_modified'])
                total_commits.extend(summary['commits'])
        
        if total_sessions == 0:
            report += "No work sessions recorded for this phase yet.\n"
            return report
        
        total_duration = timedelta(seconds=int(total_time))
        
        report += f"- **Total Time:** {total_duration}\n"
        report += f"- **Total Sessions:** {total_sessions}\n"
        report += f"- **Files Touched:** {len(total_files)}\n"
        report += f"- **Commits Made:** {len(total_commits)}\n"
        report += f"- **Average Session:** {timedelta(seconds=int(total_time/total_sessions))}\n"
        
        # Task breakdown
        report += "\n### Task Time Breakdown\n\n"
        
        task_times = []
        for task in phase_tasks:
            summary = self.task_manager.get_session_summary(task['id'])
            if summary['total_sessions'] > 0:
                task_times.append((
                    task['id'],
                    summary['total_duration_seconds'],
                    summary['total_sessions']
                ))
        
        # Sort by time spent
        task_times.sort(key=lambda x: x[1], reverse=True)
        
        for task_id, duration_seconds, sessions in task_times:
            duration = timedelta(seconds=int(duration_seconds))
            percentage = (duration_seconds / total_time) * 100
            report += f"- **{task_id}**: {duration} ({percentage:.1f}%) - {sessions} session(s)\n"
        
        return report
    
    def _get_relative_path(self, file_path: str) -> str:
        """Get relative path from project root"""
        try:
            return str(Path(file_path).relative_to(self.project_root))
        except:
            return file_path
    
    def _generate_recommendations(self, summary: Dict[str, Any], sessions: List[Dict[str, Any]]) -> str:
        """Generate recommendations based on session patterns"""
        recommendations = "## 💡 Observations & Recommendations\n\n"
        
        if summary['total_sessions'] == 0:
            recommendations += "- No sessions recorded yet for this task\n"
            return recommendations
        
        avg_duration = summary['total_duration_seconds'] / summary['total_sessions']
        avg_duration_td = timedelta(seconds=int(avg_duration))
        
        # Session duration insights
        if avg_duration < 1800:  # Less than 30 minutes
            recommendations += f"- **Short Sessions:** Average session is {avg_duration_td}. Consider longer focused work blocks.\n"
        elif avg_duration > 14400:  # More than 4 hours
            recommendations += f"- **Long Sessions:** Average session is {avg_duration_td}. Consider breaking work into smaller chunks.\n"
        else:
            recommendations += f"- **Good Session Length:** Average session is {avg_duration_td} (optimal range).\n"
        
        # File change patterns
        if summary['total_files_modified'] > 10:
            recommendations += f"- **Wide Impact:** {summary['total_files_modified']} files modified. Ensure comprehensive testing.\n"
        elif summary['total_files_modified'] == 0 and summary['total_sessions'] > 0:
            recommendations += "- **No File Changes:** Sessions recorded but no files modified. Was this planning/research?\n"
        
        # Commit patterns
        commits_per_session = summary['total_commits'] / summary['total_sessions'] if summary['total_sessions'] > 0 else 0
        if commits_per_session < 0.5:
            recommendations += "- **Low Commit Frequency:** Consider committing changes more frequently.\n"
        elif commits_per_session > 5:
            recommendations += "- **High Commit Frequency:** Good granular version control.\n"
        
        # Active session check
        active_sessions = [s for s in sessions if s.get('is_active')]
        if active_sessions:
            recommendations += "- **⚠️ Active Session:** There's currently an active session that hasn't been closed.\n"
        
        return recommendations
    
    def export_session_data(self, task_id: str, output_path: Optional[Path] = None) -> Path:
        """Export session data to JSON for external analysis"""
        if output_path is None:
            output_path = self.task_manager.reports_dir / f"session_export_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        sessions = self.task_manager.get_task_sessions(task_id)
        summary = self.task_manager.get_session_summary(task_id)
        
        export_data = {
            "task_id": task_id,
            "export_timestamp": datetime.now().isoformat(),
            "summary": summary,
            "sessions": sessions
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return output_path


def main():
    """Test session reporter functionality"""
    from task_manager import TaskManager
    
    tm = TaskManager()
    reporter = SessionReporter(tm)
    
    # Example: Generate report for a task
    task_id = "implement-task-session-tracking"
    
    print("Generating session report...")
    report = reporter.generate_session_report(task_id)
    print(report)
    
    print("\nGenerating handoff supplement...")
    supplement = reporter.generate_handoff_supplement(task_id)
    print(supplement)


if __name__ == "__main__":
    main()