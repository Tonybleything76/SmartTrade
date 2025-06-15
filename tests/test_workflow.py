"""
Unit tests for workflow management
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow import ContentWorkflow, WorkflowStatus


class TestContentWorkflow(unittest.TestCase):
    """Test ContentWorkflow functionality"""
    
    def setUp(self):
        self.workflow = ContentWorkflow()
    
    def test_initialization(self):
        """Test workflow initialization"""
        self.assertEqual(self.workflow.current_status, WorkflowStatus.IDLE)
        self.assertIsNotNone(self.workflow.config)
        self.assertIsNone(self.workflow.current_run_id)
    
    def test_workflow_status_enum(self):
        """Test workflow status enumeration"""
        statuses = [status.value for status in WorkflowStatus]
        expected_statuses = [
            "idle", "initializing", "researching", "generating", 
            "editing", "scheduling", "completed", "failed", "paused"
        ]
        for expected in expected_statuses:
            self.assertIn(expected, statuses)
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key',
        'SERPAPI_API_KEY': 'test_key'
    })
    def test_system_validation(self):
        """Test system configuration validation"""
        validation = self.workflow.validate_system_configuration()
        self.assertIsInstance(validation, dict)
        self.assertIn("valid", validation)
    
    def test_workflow_status_retrieval(self):
        """Test workflow status retrieval"""
        status = self.workflow.get_workflow_status()
        self.assertIsInstance(status, dict)
        self.assertIn("current_status", status)
    
    def test_manual_request_queue(self):
        """Test manual request queue management"""
        request_data = {"type": "test_request"}
        request_id = self.workflow.queue_manual_request(request_data)
        self.assertIsInstance(request_id, str)
        self.assertTrue(self.workflow.has_manual_requests())
    
    def test_workflow_history(self):
        """Test workflow history management"""
        history = self.workflow.get_workflow_history(limit=10)
        self.assertIsInstance(history, list)


if __name__ == "__main__":
    unittest.main(verbosity=2)