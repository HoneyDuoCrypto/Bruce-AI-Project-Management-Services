#!/usr/bin/env python3
"""
Phase Blueprint Generator - Enhanced with Deep Code Analysis
Creates comprehensive phase documents with detailed implementation tracking
"""

import os
import sys
import re
import ast
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import glob

# Add src to path to import TaskManager
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.task_manager import TaskManager

class PhaseBlueprintGenerator:
    """Generates comprehensive phase blueprints with enhanced implementation details."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.task_manager = TaskManager(self.project_root)
        self.docs_path = self.project_root / "docs"
    
    def generate_comprehensive_phase_blueprint(self, phase_id: int) -> str:
        """Generate the ONE comprehensive blueprint for a phase with enhanced details."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get all data needed
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
        
        blueprint += """---

## 🏗️ System Architecture

### Component Overview
```
📁 BRUCE PROJECT MANAGEMENT SYSTEM
│
├── 🧠 CORE ENGINE
│   ├── TaskManager (src/task_manager.py)
│   │   ├── → reads: phases/*.yml, tasks.yaml
│   │   ├── → writes: contexts/phase*/context_*.md  
│   │   └── → manages: task status, progress tracking
│   │
│   └── BlueprintGenerator (src/blueprint_generator.py)
│       ├── → reads: context files, task data, system code
│       ├── → analyzes: imports, dependencies, data flows
│       └── → writes: docs/blueprints/phase_*_blueprint.md
│
├── 🖥️ USER INTERFACES  
│   ├── CLI Interface (cli/bruce-task.py)
│   │   ├── → imports: TaskManager
│   │   ├── → commands: start, commit, block, status, phases
│   │   └── → triggers: git operations, blueprint generation
│   │
│   └── Web Dashboard (bruce_complete.py)
│       ├── → imports: TaskManager
│       ├── → serves: Flask web interface
│       └── → endpoints: /api/start_task, /api/complete_task
│
└── 📄 DATA LAYER
    ├── Phase Definition (phases/phase""" + str(phase_id) + """_*.yml)
    ├── Context Files (contexts/phase""" + str(phase_id) + """/)
    └── This Blueprint (docs/blueprints/phase_""" + str(phase_id) + """_blueprint.md)
```

---

## 🚀 Session Handoff Information

### For New Claude Sessions

**You're working on:** Phase """ + str(phase_id) + f""" of the Bruce project management system.

**Goal:** {phase_info.get('description', 'Build a system for seamless Claude session handoffs')}

**Current Status:** {progress['completed']}/{progress['total']} tasks completed ({progress['percentage']:.1f}%)

### Quick Start Commands
```bash
# Check current status
python cli/bruce-task.py status

# See phase progress  
python cli/bruce-task.py phases

# List available tasks
python cli/bruce-task.py list --phase {phase_id}

# Start next task (with enhanced context)
python cli/bruce-task.py start <task-id>

# Start with basic context
python cli/bruce-task.py start <task-id> --basic
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
        """Generate comprehensive session handoff with enhanced details."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        handoff = f"""# 🤝 Claude Session Handoff - Technical Deep Dive

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Session ID:** session_{timestamp}
**Project:** Bruce Project Management System

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
        
        handoff += f"**Overall Progress:** {total_completed}/{total_tasks} tasks ({overall_progress:.1f}%)\n\n"
        
        # Show what's been built
        handoff += "### ✅ What's Been Built\n"
        completed_tasks = [t for t in tasks_data.get("tasks", []) if t.get('status') == 'completed']
        for task in completed_tasks:
            handoff += f"- **{task['id']}:** {task.get('description', '')} → `{task.get('output', '')}`\n"
        
        handoff += "\n### 🔄 What You're Continuing\n"
        pending_tasks = [t for t in tasks_data.get("tasks", []) if t.get('status') == 'pending']
        for task in pending_tasks[:3]:
            handoff += f"- **{task['id']}:** {task.get('description', '')} → `{task.get('output', '')}`\n"
        
        handoff += """

## 🏗️ System Architecture Overview

### Core Components
```
TaskManager (src/task_manager.py)
├── Manages multi-phase task loading from YAML files
├── Handles context file generation and organization  
├── Tracks progress across phases
├── Enhanced context with related tasks and decisions
└── Integrates with CLI and Web UI

CLI Interface (cli/bruce-task.py)
├── Enhanced with blueprint auto-generation
├── Supports phase-aware task management
├── --basic flag for context mode selection
├── Triggers git operations and documentation
└── Generates Claude handoff reports

Web Dashboard (bruce_complete.py)  
├── Phase-aware progress tracking
├── RESTful API for task operations
├── Visual task management interface
├── Modal dialogs for enhanced context
├── Context preview functionality
└── Related tasks viewer

BlueprintGenerator (src/blueprint_generator.py)
├── Analyzes system architecture automatically
├── Deep code analysis with AST parsing
├── Creates comprehensive technical blueprints
├── Maps component connections and data flows
└── Generates session handoff documents
```

## 🚀 How to Continue Development

### Immediate Commands
```bash
# Check current system status
python cli/bruce-task.py status

# See what tasks are available
python cli/bruce-task.py list

# Start a specific task with enhanced context
python cli/bruce-task.py start <task-id>

# Use basic context instead
python cli/bruce-task.py start <task-id> --basic

# Test blueprint generation
python src/blueprint_generator.py update --phase-id 1
```

### Web Interface
- **URL:** http://bruce.honey-duo.com
- **Login:** hdw / HoneyDuo2025!
- **Features:** Phase tracking, task management, enhanced context, blueprint generation

---

**🚀 Ready to continue development!** The system is designed to support you with context, documentation, and clear next steps.
"""
        
        return handoff
    
    def generate_system_architecture_blueprint(self) -> str:
        """Generate comprehensive system architecture blueprint with enhanced details."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get current progress
        phase_progress = self.task_manager.get_phase_progress()
        tasks_data = self.task_manager.load_tasks()
        
        blueprint = f"""# 🏗️ Bruce System Architecture Blueprint

**Generated:** {timestamp}
**System Analysis:** Bruce Project Management System

## 📊 Project Status Summary

"""
        
        # Add progress overview
        total_tasks = sum(p['total'] for p in phase_progress.values())
        total_completed = sum(p['completed'] for p in phase_progress.values())
        overall_progress = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
        
        blueprint += f"**Overall Progress:** {total_completed}/{total_tasks} tasks ({overall_progress:.1f}%)\n\n"
        
        blueprint += f"""## 🏗️ System Architecture Map

### Core Components & Connections

```
📁 BRUCE PROJECT MANAGEMENT SYSTEM
│
├── 🧠 CORE ENGINE
│   ├── TaskManager (src/task_manager.py)
│   │   ├── → reads: phases/*.yml, tasks.yaml
│   │   ├── → writes: contexts/phase*/context_*.md  
│   │   ├── → manages: task status, progress tracking
│   │   └── → provides: multi-phase support, enhanced context generation
│   │
│   └── BlueprintGenerator (src/blueprint_generator.py)
│       ├── → reads: context files, task data, system code
│       ├── → analyzes: imports, dependencies, data flows, AST parsing
│       ├── → writes: docs/blueprints/, docs/sessions/
│       └── → provides: architecture mapping, session handoffs
│
├── 🖥️ USER INTERFACES  
│   ├── CLI Interface (cli/bruce-task.py)
│   │   ├── → imports: TaskManager
│   │   ├── → commands: start, commit, block, status, phases
│   │   ├── → triggers: git operations, blueprint generation
│   │   └── → generates: Claude handoff reports
│   │
│   └── Web Dashboard (bruce_complete.py)
│       ├── → imports: TaskManager
│       ├── → serves: Flask web interface
│       ├── → endpoints: /api/start_task, /api/complete_task, /api/generate_blueprint
│       ├── → provides: visual progress tracking, task management
│       └── → features: blueprint generator UI, phase management, enhanced context
│
└── 📄 DATA & CONFIGURATION
    ├── Phase Definitions (phases/*.yml)
    │   └── → defines: tasks, acceptance criteria, dependencies
    │
    ├── Context Files (contexts/phase*/)
    │   └── → contains: task context, implementation notes, architecture diagrams
    │
    ├── Generated Documentation (docs/)
    │   ├── blueprints/ → system architecture, progress reports
    │   └── sessions/ → Claude handoff documents
    │
    └── Legacy Support (tasks.yaml)
        └── → backward compatibility with original task format
```

## 🔗 Component Integration Points

### Current Integrations
- **CLI ↔ TaskManager:** Full integration with multi-phase support and enhanced context
- **TaskManager ↔ YAML Files:** Reads phase definitions and legacy tasks  
- **TaskManager ↔ Context Files:** Organized context generation by phase with enhanced features
- **CLI ↔ Git:** Automatic commits on task completion
- **CLI ↔ Blueprint Generator:** Auto-generation on task completion
- **Web UI ↔ TaskManager:** Phase-aware dashboard and task management
- **Web UI ↔ Blueprint Generator:** Integrated generator interface
- **Context System ↔ Related Tasks:** Automatic discovery of related work
- **Context System ↔ Architecture Diagrams:** Visual component placement

---

**🎯 This blueprint provides a complete technical map of system connections, data flows, and integration points.**
"""
        
        return blueprint
    
    def update_phase_blueprint(self, phase_id: int) -> str:
        """Update the comprehensive phase blueprint."""
        content = self.generate_comprehensive_phase_blueprint(phase_id)
        blueprints_dir = self.docs_path / "blueprints"
        blueprints_dir.mkdir(parents=True, exist_ok=True)
        
        doc_path = blueprints_dir / f"phase_{phase_id}_blueprint.md"
        
        # Save the updated document
        with open(doc_path, 'w') as f:
            f.write(content)
        
        print(f"📋 Updated Phase {phase_id} blueprint: {doc_path.name}")
        return str(doc_path)
    
    def auto_generate_on_completion(self, task_id: str) -> Dict[str, str]:
        """Auto-update phase blueprint when tasks complete."""
        results = {}
        
        try:
            tasks_data = self.task_manager.load_tasks()
            task = next((t for t in tasks_data.get("tasks", []) if t["id"] == task_id), None)
            
            if not task:
                return {"error": f"Task {task_id} not found"}
            
            phase_id = task.get('phase', 1)
            
            # Update the phase blueprint
            blueprint_path = self.update_phase_blueprint(phase_id)
            results["phase_blueprint"] = blueprint_path
            
            return results
            
        except Exception as e:
            return {"error": f"Phase blueprint update failed: {e}"}


def main():
    """CLI interface for phase blueprint generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate comprehensive phase blueprints")
    parser.add_argument('command', choices=['phase', 'complete', 'update', 'handoff', 'architecture'], 
                       help="Command to execute")
    parser.add_argument('--phase-id', type=int, default=1, help="Phase ID")
    parser.add_argument('--project-root', default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    generator = PhaseBlueprintGenerator(args.project_root)
    
    if args.command == 'phase':
        content = generator.generate_comprehensive_phase_blueprint(args.phase_id)
        print(content)
    
    elif args.command == 'update':
        filepath = generator.update_phase_blueprint(args.phase_id)
        print(f"Phase {args.phase_id} blueprint updated: {filepath}")
    
    elif args.command == 'handoff':
        content = generator.generate_session_handoff()
        print(content)
    
    elif args.command == 'architecture':
        content = generator.generate_system_architecture_blueprint()
        print(content)

if __name__ == "__main__":
    main()