#!/usr/bin/env python3
"""
Tests for Multi-Phase Task Manager
Save as: tests/test_multi_phase.py
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import yaml
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.task_manager import TaskManager


class TestMultiPhaseTaskManager(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory for testing"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.tm = TaskManager(self.test_dir)
        
        # Create test directories (use exist_ok=True since TaskManager might create them)
        (self.test_dir / "phases").mkdir(exist_ok=True)
        (self.test_dir / "docs").mkdir(exist_ok=True)
        (self.test_dir / "src").mkdir(exist_ok=True)
        
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_load_legacy_tasks(self):
        """Test loading from legacy tasks.yaml"""
        # Create legacy tasks.yaml
        tasks_data = {
            "tasks": [
                {
                    "id": "test-task-1",
                    "description": "Test task 1",
                    "status": "pending"
                }
            ]
        }
        
        with open(self.test_dir / "tasks.yaml", 'w') as f:
            yaml.dump(tasks_data, f)
        
        # Load and verify
        loaded = self.tm.load_tasks()
        self.assertEqual(len(loaded["tasks"]), 1)
        self.assertEqual(loaded["tasks"][0]["id"], "test-task-1")
        self.assertEqual(loaded["tasks"][0]["phase"], 0)  # Default phase
    
    def test_load_phase_files(self):
        """Test loading from phase files"""
        # Create phase file
        phase_data = {
            "phase": {
                "id": 1,
                "name": "Test Phase",
                "description": "Testing phase loading"
            },
            "tasks": [
                {
                    "id": "phase1-task-1",
                    "description": "Phase 1 task",
                    "status": "pending"
                }
            ]
        }
        
        with open(self.test_dir / "phases" / "phase1_test.yml", 'w') as f:
            yaml.dump(phase_data, f)
        
        # Load and verify
        loaded = self.tm.load_tasks()
        self.assertEqual(len(loaded["tasks"]), 1)
        self.assertEqual(loaded["tasks"][0]["id"], "phase1-task-1")
        self.assertEqual(loaded["tasks"][0]["phase"], 1)
        self.assertEqual(loaded["tasks"][0]["phase_name"], "Test Phase")
        self.assertIn("phases", loaded)
        self.assertEqual(loaded["phases"][1]["name"], "Test Phase")
    
    def test_mixed_loading(self):
        """Test loading from both legacy and phase files"""
        # Create legacy task
        legacy_data = {
            "tasks": [{
                "id": "legacy-task",
                "description": "Legacy task",
                "status": "completed"
            }]
        }
        with open(self.test_dir / "tasks.yaml", 'w') as f:
            yaml.dump(legacy_data, f)
        
        # Create phase file
        phase_data = {
            "phase": {"id": 1, "name": "Phase 1"},
            "tasks": [{
                "id": "phase-task",
                "description": "Phase task",
                "status": "pending"
            }]
        }
        with open(self.test_dir / "phases" / "phase1_test.yml", 'w') as f:
            yaml.dump(phase_data, f)
        
        # Load and verify
        loaded = self.tm.load_tasks()
        self.assertEqual(len(loaded["tasks"]), 2)
        
        # Check tasks have correct phases
        tasks_by_id = {t["id"]: t for t in loaded["tasks"]}
        self.assertEqual(tasks_by_id["legacy-task"]["phase"], 0)
        self.assertEqual(tasks_by_id["phase-task"]["phase"], 1)
    
    def test_save_task_updates(self):
        """Test updating tasks preserves file location"""
        # Create phase file
        phase_data = {
            "phase": {"id": 1, "name": "Test Phase"},
            "tasks": [{
                "id": "test-task",
                "description": "Test task",
                "status": "pending"
            }]
        }
        phase_file = self.test_dir / "phases" / "phase1_test.yml"
        with open(phase_file, 'w') as f:
            yaml.dump(phase_data, f)
        
        # Load tasks first to populate metadata
        loaded = self.tm.load_tasks()
        
        # Update task
        self.tm.save_task_updates("test-task", {
            "status": "completed",
            "notes": [{"note": "Task completed"}]
        })
        
        # Verify update saved to correct file
        with open(phase_file, 'r') as f:
            updated = yaml.safe_load(f)
        
        self.assertEqual(updated["tasks"][0]["status"], "completed")
        self.assertIn("notes", updated["tasks"][0])
    
    def test_get_context_multiple_locations(self):
        """Test context retrieval from various locations"""
        # Create test files in different locations
        (self.test_dir / "test1.py").write_text("# Root file")
        (self.test_dir / "docs" / "test2.md").write_text("# Docs file")
        (self.test_dir / "src" / "test3.py").write_text("# Src file")
        
        # Test retrieval
        context = self.tm.get_context([
            "test1.py",
            "test2.md", 
            "test3.py",
            "missing.txt"
        ])
        
        self.assertIn("# Root file", context)
        self.assertIn("# Docs file", context)
        self.assertIn("# Src file", context)
        self.assertIn("missing.txt (NOT FOUND)", context)
    
    def test_phase_progress(self):
        """Test phase progress calculation"""
        # Create mixed tasks
        tasks_data = {
            "tasks": [
                {"id": "t1", "status": "completed", "phase": 0},
                {"id": "t2", "status": "pending", "phase": 0},
                {"id": "t3", "status": "completed", "phase": 1},
                {"id": "t4", "status": "in-progress", "phase": 1},
                {"id": "t5", "status": "pending", "phase": 1},
            ]
        }
        with open(self.test_dir / "tasks.yaml", 'w') as f:
            yaml.dump(tasks_data, f)
        
        # Get progress
        progress = self.tm.get_phase_progress()
        
        # Verify phase 0
        self.assertEqual(progress[0]["total"], 2)
        self.assertEqual(progress[0]["completed"], 1)
        self.assertEqual(progress[0]["percentage"], 50)
        
        # Verify phase 1  
        self.assertEqual(progress[1]["total"], 3)
        self.assertEqual(progress[1]["completed"], 1)
        self.assertEqual(progress[1]["percentage"], 33)
    
    def test_organized_context_files(self):
        """Test context files are organized by phase"""
        # Create a task and start it
        tasks_data = {
            "tasks": [{
                "id": "test-task",
                "description": "Test",
                "phase": 1,
                "context": ["README.md"],
                "output": "test.py",
                "status": "pending"
            }]
        }
        with open(self.test_dir / "tasks.yaml", 'w') as f:
            yaml.dump(tasks_data, f)
        
        # Create context file
        (self.test_dir / "README.md").write_text("# Test README")
        
        # Start task
        self.tm.cmd_start("test-task")
        
        # Verify context file created in correct location
        context_file = self.test_dir / "contexts" / "phase1" / "context_test-task.md"
        self.assertTrue(context_file.exists())
        
        # Verify content
        content = context_file.read_text()
        self.assertIn("**Phase:** 1", content)
        self.assertIn("# Test README", content)


if __name__ == "__main__":
    unittest.main()