#!/usr/bin/env python3
"""Unit tests for Brain Consolidation Tier 1.

Tests the _archive_resolved_files() function which moves .resolved.* 
and .metadata.json backup files to archive/resolved/.
"""
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Set up test brain path before importing
TEST_DIR = tempfile.mkdtemp(prefix="nucleus_consolidation_test_")
os.environ["NUCLEAR_BRAIN_PATH"] = TEST_DIR


class TestBrainConsolidation(unittest.TestCase):
    """Test cases for brain consolidation feature."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test brain directory structure."""
        cls.brain_path = Path(TEST_DIR)
        cls.ledger_path = cls.brain_path / "ledger"
        cls.ledger_path.mkdir(parents=True, exist_ok=True)
        
        # Create events.jsonl for emit_event
        (cls.ledger_path / "events.jsonl").touch()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test directory."""
        shutil.rmtree(TEST_DIR)
    
    def setUp(self):
        """Reset test files before each test."""
        # Clean up any archive from previous tests
        archive_dir = self.brain_path / "archive" / "resolved"
        if archive_dir.exists():
            shutil.rmtree(archive_dir)
        
        # Clean up any test files
        for f in self.brain_path.glob("*.resolved*"):
            f.unlink()
        for f in self.brain_path.glob("*.metadata.json"):
            f.unlink()
    
    def test_archive_resolved_moves_files(self):
        """Test that .resolved.* files are moved to archive."""
        from mcp_server_nucleus import _archive_resolved_files
        
        # Create test resolved files
        (self.brain_path / "task.md.resolved").write_text("backup 1")
        (self.brain_path / "task.md.resolved.0").write_text("backup 2")
        (self.brain_path / "task.md.resolved.1").write_text("backup 3")
        
        result = _archive_resolved_files()
        
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("files_moved"), 3)
        
        # Verify files are in archive
        archive_dir = Path(result.get("archive_path"))
        self.assertTrue(archive_dir.exists())
        self.assertEqual(len(list(archive_dir.glob("*"))), 3)
        
        # Verify files are no longer in brain root
        self.assertEqual(len(list(self.brain_path.glob("*.resolved*"))), 0)
    
    def test_archive_resolved_creates_directory(self):
        """Test that archive/resolved/ is created if missing."""
        from mcp_server_nucleus import _archive_resolved_files
        
        archive_dir = self.brain_path / "archive" / "resolved"
        self.assertFalse(archive_dir.exists())
        
        # Create one test file
        (self.brain_path / "test.md.resolved").write_text("content")
        
        result = _archive_resolved_files()
        
        self.assertTrue(result.get("success"))
        self.assertTrue(archive_dir.exists())
    
    def test_archive_resolved_skips_primary_files(self):
        """Test that primary files (not .resolved) are NOT moved."""
        from mcp_server_nucleus import _archive_resolved_files
        
        # Create primary file and resolved file
        primary = self.brain_path / "task.md"
        resolved = self.brain_path / "task.md.resolved"
        
        primary.write_text("primary content")
        resolved.write_text("backup content")
        
        result = _archive_resolved_files()
        
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("files_moved"), 1)
        
        # Primary file should still exist
        self.assertTrue(primary.exists())
        # Resolved should be gone
        self.assertFalse(resolved.exists())
    
    def test_archive_handles_metadata_json(self):
        """Test that .metadata.json files are also archived."""
        from mcp_server_nucleus import _archive_resolved_files
        
        # Create metadata files
        (self.brain_path / "task.md.metadata.json").write_text("{}")
        (self.brain_path / "notes.md.metadata.json").write_text("{}")
        
        result = _archive_resolved_files()
        
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("files_moved"), 2)
    
    def test_archive_empty_returns_success(self):
        """Test that archiving with no files returns success with 0 count."""
        from mcp_server_nucleus import _archive_resolved_files
        
        # No files to archive
        result = _archive_resolved_files()
        
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("files_moved"), 0)


if __name__ == "__main__":
    unittest.main()
