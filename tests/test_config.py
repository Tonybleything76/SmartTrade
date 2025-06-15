"""
Unit tests for configuration management
"""

import unittest
from unittest.mock import patch
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import get_config, Config


class TestConfiguration(unittest.TestCase):
    """Test configuration management"""
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'SERPAPI_API_KEY': 'test_serpapi_key',
        'LINKEDIN_ACCESS_TOKEN': 'test_linkedin_token'
    })
    def test_config_initialization(self):
        """Test configuration initialization with environment variables"""
        config = get_config()
        self.assertIsInstance(config, Config)
        self.assertEqual(config.openai_api_key, 'test_openai_key')
        self.assertEqual(config.serpapi_api_key, 'test_serpapi_key')
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = get_config()
        validation = config.validate()
        self.assertIsInstance(validation, dict)
        self.assertIn("valid", validation)
    
    def test_config_to_dict(self):
        """Test configuration serialization"""
        config = get_config()
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertIn("content_generation", config_dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)