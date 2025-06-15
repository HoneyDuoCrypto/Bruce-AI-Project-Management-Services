# 🏗️ Bruce System Architecture Blueprint - COMPLETE ANALYSIS

**Generated:** 2025-06-15 01:32:13
**System Analysis:** Bruce Project Management System (Dynamic Scan)
**Project Root:** /home/honey-duo-wealth/Bruce

## 📊 Project Status Summary

**Overall Progress:** 12/25 tasks (48.0%)
**File Analysis:** 106 files, 1,095,513 bytes
**Git Status:** ⚠️ Uncommitted changes
**Config Status:** ✅ Loaded

## 🏗️ Dynamic System Architecture Map

### Core Components & Connections (ACTUAL DETECTED STRUCTURE)

```
📁 BRUCE PROJECT MANAGEMENT SYSTEM (106 files)
│
├── 🧠 CORE ENGINE (5 modules)
│   ├── TaskManager (src/task_manager.py)
│   │   ├── → reads: phases/*.yml, tasks.yaml
│   │   ├── → writes: contexts/phase*/context_*.md  
│   │   ├── → manages: task status, progress tracking
│   │   └── → provides: Multi-phase task loading, Enhanced context generation, Related task discovery, Configuration management, Architecture context generation
│   │
│   ├── ConfigManager (src/config_manager.py)
│   │   ├── → loads: bruce.yaml configuration
│   │   ├── → provides: YAML configuration loading, Multi-project support, Configuration validation, UI theming support
│   │   └── → enables: multi-project support
│   │
│   └── BlueprintGenerator (src/blueprint_generator.py) ← THIS FILE!
│       ├── → analyzes: project structure dynamically
│       ├── → scans: 19 Python files
│       ├── → writes: docs/blueprints/, docs/sessions/
│       └── → provides: System architecture generation, Session handoff generation, Phase blueprint generation, Auto-generation on task completion
│
├── 🖥️ USER INTERFACES  
│   ├── CLI Interface (bruce.py)
│   │   ├── → commands: init, status, list, start, commit...
│   │   ├── → supports: multi-project
│   │   └── → features: git integration, blueprint auto-generation
│   │
│   └── Web Dashboard (bruce_app.py)
│       ├── → templates: 9 modular templates
│       ├── → endpoints: 27 API routes
│       ├── → features: blueprint_generation, enhanced_context, responsive_design, phase_tracking, theme_support
│       └── → architecture: modular
│
├── 🎨 TEMPLATE SYSTEM (templates/ - 9 files)
│   ├── Modular Architecture: ✅
│   ├── Template Files: generator.py, reports.py, help.py, phases.py, styles.py
│   ├── Features: blueprint_generation, enhanced_context, responsive_design
│   └── Dependencies: Cross-template imports and shared styles
│
└── 📄 DATA & CONFIGURATION
    ├── Phase Definitions (phases/ - 5 YAML files)
    │   └── → defines: tasks, acceptance criteria, dependencies
    │
    ├── Context Files (contexts/phase*/)
    │   └── → contains: task context, implementation notes
    │
    ├── Configuration (/home/honey-duo-wealth/Bruce/bruce.yaml)
    │   └── → manages: project settings, UI theming, directories
    │
    └── Generated Documentation (docs/)
        ├── blueprints/ → system architecture, progress reports
        └── sessions/ → Claude handoff documents
```
## 🔍 Component Deep Analysis

### Web Interface Details
- **Main File:** bruce_app.py (1326 lines, 49,731 bytes)
- **Last Modified:** 2025-06-15T01:31:54
- **Flask Integration:** ✅
- **Template Integration:** ✅
- **Multi-Project Ready:** ❌

### CLI Interface Details
- **Main File:** bruce.py (896 lines, 31,770 bytes)
- **Last Modified:** 2025-06-13T14:44:10
- **Argparse Integration:** ✅
- **Available Commands:** 10
- **Multi-Project Support:** ✅

### Template System Analysis
- **Total Templates:** 9
- **Modular Architecture:** ✅
- **Detected Features:** blueprint_generation, enhanced_context, responsive_design, phase_tracking, theme_support, ajax, modals, task_management, form_handling
- **Template Files:**
  - generator.py: 340 lines, features: enhanced_context, blueprint_generation, phase_tracking, ajax, form_handling, responsive_design
  - reports.py: 321 lines, features: blueprint_generation, phase_tracking, ajax, form_handling, responsive_design
  - help.py: 380 lines, features: enhanced_context, blueprint_generation, phase_tracking, modals, ajax, form_handling, responsive_design, theme_support
  - phases.py: 249 lines, features: phase_tracking, ajax, form_handling, responsive_design, theme_support
  - styles.py: 459 lines, features: enhanced_context, phase_tracking, modals, form_handling, responsive_design, theme_support
  - tasks.py: 474 lines, features: enhanced_context, blueprint_generation, task_management, phase_tracking, modals, ajax, responsive_design, theme_support
  - config.py: 324 lines, features: enhanced_context, blueprint_generation, phase_tracking, ajax, form_handling, responsive_design, theme_support
  - dashboard.py: 299 lines, features: phase_tracking, ajax, form_handling, responsive_design
  - manage.py: 898 lines, features: enhanced_context, blueprint_generation, phase_tracking, ajax, form_handling, responsive_design, theme_support

### Core Modules Analysis
- **Total Modules:** 5
  - **bruce_init.py:** Unknown Role
    - Size: 378 lines (12,498 bytes)
    - Modified: 2025-06-11T17:45:31
  - **blueprint_generator.py:** Documentation Generation
    - Size: 1420 lines (59,657 bytes)
    - Modified: 2025-06-15T01:19:24
    - Capabilities: System architecture generation, Session handoff generation, Phase blueprint generation, Auto-generation on task completion
  - **task_manager.py:** Core Task Management
    - Size: 668 lines (28,966 bytes)
    - Modified: 2025-06-11T16:37:44
    - Capabilities: Multi-phase task loading, Enhanced context generation, Related task discovery, Configuration management, Architecture context generation
  - **config_manager.py:** Configuration Management
    - Size: 317 lines (11,703 bytes)
    - Modified: 2025-06-11T13:29:17
    - Capabilities: YAML configuration loading, Multi-project support, Configuration validation, UI theming support
  - **utils.py:** Unknown Role
    - Size: 2 lines (54 bytes)
    - Modified: 2025-06-14T22:05:45
## 🔌 API & CLI Reference

### API Endpoints
**Total Endpoints:** 27

**GET Endpoints:**
- `GET /` → dashboard
- `GET /tasks` → tasks
- `GET /phases` → phases
- `GET /manage` → manage
- `GET /generator` → generator
- `GET /reports` → reports
- `GET /config` → config_info
- `GET /help` → help_page
- `GET /api/discover_projects` → api_discover_projects
- `GET /api/current_project_info` → api_current_project_info
- `GET /api/project_health_check` → project_health_check
- `GET /api/validate_config` → validate_config
- `GET /api/preview_context/<task_id>` → preview_context
- `GET /api/related_tasks/<task_id>` → related_tasks
- `GET /health` → health_check

**POST Endpoints:**
- `POST /api/switch_project` → api_switch_project
- `POST /api/create_config` → create_config
- `POST /api/add_task` → add_task
- `POST /api/add_phase` → add_phase
- `POST /api/edit_task` → edit_task
- `POST /api/preview_blueprint` → preview_blueprint
- `POST /api/import_blueprint` → import_blueprint
- `POST /api/start_task` → start_task
- `POST /api/complete_task` → complete_task
- `POST /api/block_task` → block_task
- `POST /api/generate_blueprint` → generate_blueprint
- `POST /api/generate_report` → generate_report

### CLI Commands
**Total Commands:** 10

- `init`: Initialize Bruce in current directory
- `status`: Show project status
- `list`: List tasks
- `start`: Start a task
- `commit`: Complete and commit a task
- `block`: Block a task
- `phases`: Show phase progress
- `ui`: Start web interface
- `add-task`: Add new task to phase
- `add-phase`: Add new phase

## 📊 File Statistics & Metrics

### Overall Statistics
- **Total Files:** 106
- **Total Size:** 1,095,513 bytes (1069.8 KB)
- **Python Files:** 19
- **YAML Files:** 5
- **Markdown Files:** 52

### By Directory
- **root/**: 5 files, 181,514 bytes
- **src/**: 6 files, 129,088 bytes
- **claude_reports/**: 13 files, 14,220 bytes
- **templates/**: 10 files, 176,358 bytes
- **phases/**: 4 files, 28,326 bytes
- **cli/**: 1 files, 31,770 bytes
- **tests/**: 2 files, 7,980 bytes
- **contexts/phase3/**: 1 files, 3,525 bytes
- **src/__pycache__/**: 4 files, 138,211 bytes
- **templates/__pycache__/**: 10 files, 179,714 bytes
- **docs/blueprints/**: 26 files, 97,492 bytes
- **docs/sessions/**: 24 files, 107,315 bytes

### Largest Files
- bruce.py.bak: 129,338 bytes
- src/__pycache__/blueprint_generator.cpython-312.pyc: 70,282 bytes
- src/blueprint_generator.py: 59,657 bytes
- bruce_app.py: 49,731 bytes
- templates/__pycache__/manage.cpython-312.pyc: 42,681 bytes

### Recently Modified
- bruce_app.py: 2025-06-15T01:31:54
- src/__pycache__/blueprint_generator.cpython-312.pyc: 2025-06-15T01:19:33
- src/blueprint_generator.py: 2025-06-15T01:19:24
- docs/blueprints/architecture_blueprint_20250615_0113.md: 2025-06-15T01:13:17
- templates/__pycache__/help.cpython-312.pyc: 2025-06-15T01:00:07

## 🔗 Import Relationships & Dependencies

### Module Dependencies
- **bruce_app.py** (10 local imports)
  - imports: src.task_manager
  - imports: templates.dashboard
  - imports: templates.tasks
  - ... and 7 more
- **cli/bruce.py** (2 local imports)
  - imports: src.task_manager
  - imports: src.blueprint_generator
- **src/blueprint_generator.py** (1 local imports)
  - imports: src.task_manager
- **src/task_manager.py** (1 local imports)
  - imports: src.config_manager
- **tests/test_utils.py** (1 local imports)
  - imports: src.utils
- **tests/test_multi_phase.py** (1 local imports)
  - imports: src.task_manager

### External Dependencies
- flask
- yaml
- pathlib
- datetime
- typing

## 🌐 Multi-Project Environment

### Current Project
- **Path:** /home/honey-duo-wealth/Bruce
- **Multi-Project CLI Support:** ✅
- **Multi-Project Web Support:** ❌

### Discovered Projects
**Found 1 other Bruce projects:**

- **TestProject** (ai-assisted)
  - Path: /home/honey-duo-wealth/TestProject
  - Status: ✅ Available

## 🚀 Development Context

### Git Repository Status
- **Repository:** ✅ Git repository detected
- **Current Branch:** master
- **Uncommitted Changes:** 12
- **Modified Files:**
  - M  ruce_app.py
  -  M templates/__init__.py
  -  M templates/config.py
  -  M templates/dashboard.py
  -  M templates/generator.py
  - ... and 7 more
- **Recent Commits:**
  - f0c26f8:  Debugging UI Features
  - 80f1c89: Added UI features for multi project support to all templates and bruce_app.py
  - f06ad52: Major architectural refactor: Modular bruce_app.py with template system

### Configuration
- **Config Files Found:** 1
- **Config Manager Available:** ✅
- **Active Config:** /home/honey-duo-wealth/Bruce/bruce.yaml
  - Project: Bruce Project
  - Type: general

---

**🎯 This blueprint provides the complete technical landscape of the Bruce system.**
**Every component, file, relationship, and capability has been dynamically analyzed.**
**Use this for comprehensive Claude handoffs with full system understanding.**

*Last updated: 2025-06-15 01:32:13*
