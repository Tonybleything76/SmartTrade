"""
Unit tests for Multi-Agent AI Content System agents
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent, AgentCommunicationHub
from agents.orchestration import OrchestrationAgent
from agents.trend_researcher import TrendResearcherAgent
from agents.content_developer import ContentDeveloperAgent
from agents.content_editor import ContentEditorAgent
from agents.scheduler import SchedulerAgent
from agents.distribution import DistributionAgent
from agents.roadmap_generator import RoadmapGeneratorAgent


class TestBaseAgent(unittest.TestCase):
    """Test BaseAgent functionality"""
    
    def setUp(self):
        self.agent = BaseAgent("Test Agent", "Test Role", ["test_tool"])
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.name, "Test Agent")
        self.assertEqual(self.agent.role, "Test Role")
        self.assertEqual(self.agent.tools, ["test_tool"])
        self.assertIsNotNone(self.agent.agent_id)
    
    def test_state_management(self):
        """Test agent state management"""
        self.agent.update_state("test_key", "test_value")
        self.assertEqual(self.agent.get_state("test_key"), "test_value")
        self.assertIsNone(self.agent.get_state("nonexistent", None))
    
    def test_response_creation(self):
        """Test response format"""
        response = self.agent.create_response(True, {"data": "test"})
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["data"], "test")
        
        error_response = self.agent.create_response(False, error="Test error")
        self.assertFalse(error_response["success"])
        self.assertEqual(error_response["error"], "Test error")


class TestAgentCommunicationHub(unittest.TestCase):
    """Test AgentCommunicationHub functionality"""
    
    def setUp(self):
        self.hub = AgentCommunicationHub()
        self.agent = BaseAgent("Test Agent", "Test Role")
    
    def test_agent_registration(self):
        """Test agent registration"""
        self.hub.register_agent(self.agent)
        self.assertIn("Test Agent", self.hub.agents)
    
    def test_agent_status(self):
        """Test agent status retrieval"""
        self.hub.register_agent(self.agent)
        status = self.hub.get_agent_status()
        self.assertIn("Test Agent", status["agents"])


class TestOrchestrationAgent(unittest.TestCase):
    """Test OrchestrationAgent functionality"""
    
    def setUp(self):
        self.agent = OrchestrationAgent()
    
    def test_initialization(self):
        """Test orchestration agent initialization"""
        self.assertEqual(self.agent.name, "Orchestration Agent")
        self.assertEqual(self.agent.role, "Chief Content Officer / Workflow Manager")
    
    def test_pipeline_execution(self):
        """Test pipeline execution task"""
        task_data = {"task_type": "run_pipeline"}
        response = self.agent.execute_task(task_data)
        self.assertIsInstance(response, dict)
        self.assertIn("success", response)


class TestTrendResearcherAgent(unittest.TestCase):
    """Test TrendResearcherAgent functionality"""
    
    def setUp(self):
        self.agent = TrendResearcherAgent()
    
    def test_initialization(self):
        """Test trend researcher initialization"""
        self.assertEqual(self.agent.name, "Trend Researcher Agent")
        self.assertEqual(self.agent.role, "AI Trends Analyst")
        self.assertIn("Business Optimization", self.agent.topic_categories)
    
    @patch.dict(os.environ, {'SERPAPI_API_KEY': 'test_key'})
    def test_research_task(self):
        """Test trend research task structure"""
        task_data = {
            "task_type": "research_trends",
            "topics": ["AI Innovation"]
        }
        # Test that task doesn't crash on execution
        response = self.agent.execute_task(task_data)
        self.assertIsInstance(response, dict)


class TestContentDeveloperAgent(unittest.TestCase):
    """Test ContentDeveloperAgent functionality"""
    
    def setUp(self):
        self.agent = ContentDeveloperAgent()
    
    def test_initialization(self):
        """Test content developer initialization"""
        self.assertEqual(self.agent.name, "Content Developer Agent")
        self.assertEqual(self.agent.role, "AI-Powered Copywriter")
        self.assertIn("business_optimization", self.agent.post_templates)
    
    def test_template_selection(self):
        """Test template selection logic"""
        trend = {"category": "Business Optimization", "title": "Test Trend"}
        template = self.agent.select_template_type(trend)
        self.assertIsInstance(template, str)
    
    def test_reading_time_calculation(self):
        """Test reading time calculation"""
        text = "This is a test content with multiple words to calculate reading time."
        reading_time = self.agent.calculate_reading_time(text)
        self.assertIsInstance(reading_time, int)
        self.assertGreater(reading_time, 0)


class TestContentEditorAgent(unittest.TestCase):
    """Test ContentEditorAgent functionality"""
    
    def setUp(self):
        self.agent = ContentEditorAgent()
    
    def test_initialization(self):
        """Test content editor initialization"""
        self.assertEqual(self.agent.name, "Content Editor Agent")
        self.assertEqual(self.agent.role, "Fact Checker / Brand Editor")
    
    def test_technical_validation(self):
        """Test technical requirements validation"""
        content_text = "Test content with **bold** formatting"
        components = {"hook": "Test hook", "hashtags": ["#AI", "#Business"]}
        validation = self.agent.validate_technical_requirements(content_text, components)
        self.assertIsInstance(validation, dict)
        self.assertIn("valid", validation)


class TestSchedulerAgent(unittest.TestCase):
    """Test SchedulerAgent functionality"""
    
    def setUp(self):
        self.agent = SchedulerAgent()
    
    def test_initialization(self):
        """Test scheduler initialization"""
        self.assertEqual(self.agent.name, "Scheduler Agent")
        self.assertEqual(self.agent.role, "Automation Specialist / Calendar Coordinator")
    
    def test_slot_availability(self):
        """Test scheduling slot availability check"""
        from datetime import datetime, timedelta
        future_time = datetime.now() + timedelta(hours=1)
        is_occupied = self.agent.is_slot_occupied(future_time)
        self.assertIsInstance(is_occupied, bool)


class TestDistributionAgent(unittest.TestCase):
    """Test DistributionAgent functionality"""
    
    def setUp(self):
        self.agent = DistributionAgent()
    
    def test_initialization(self):
        """Test distribution agent initialization"""
        self.assertEqual(self.agent.name, "Distribution Agent")
        self.assertEqual(self.agent.role, "Platform Publisher / Social Media Manager")
    
    def test_content_optimization(self):
        """Test content optimization for platforms"""
        content = {
            "text": "Test content for optimization",
            "hashtags": ["#AI", "#Business"]
        }
        optimized = self.agent.optimize_content_for_platform(content, "linkedin")
        self.assertIsInstance(optimized, dict)
        self.assertIn("text", optimized)


class TestRoadmapGeneratorAgent(unittest.TestCase):
    """Test RoadmapGeneratorAgent functionality"""
    
    def setUp(self):
        self.agent = RoadmapGeneratorAgent()
    
    def test_initialization(self):
        """Test roadmap generator initialization"""
        self.assertEqual(self.agent.name, "Roadmap Generator Agent")
        self.assertEqual(self.agent.role, "Strategic Planning Specialist / AI Transformation Architect")
        self.assertIn("business_optimization", self.agent.roadmap_frameworks)
    
    def test_framework_selection(self):
        """Test roadmap framework selection"""
        objectives = ["Optimize business processes", "Improve efficiency"]
        context = {"industry": "consulting"}
        framework = self.agent.select_roadmap_framework(objectives, context)
        self.assertIn(framework, self.agent.roadmap_frameworks.keys())
    
    def test_deliverables_extraction(self):
        """Test deliverables extraction from phases"""
        phases = [
            {"deliverables": ["Phase 1 Report", "Initial Assessment"]},
            {"deliverables": ["Implementation Plan", "Training Materials"]}
        ]
        deliverables = self.agent.extract_deliverables_from_phases(phases)
        self.assertEqual(len(deliverables), 4)
        self.assertIn("Phase 1 Report", deliverables)


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestBaseAgent,
        TestAgentCommunicationHub,
        TestOrchestrationAgent,
        TestTrendResearcherAgent,
        TestContentDeveloperAgent,
        TestContentEditorAgent,
        TestSchedulerAgent,
        TestDistributionAgent,
        TestRoadmapGeneratorAgent
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)