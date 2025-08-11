import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
import json
import sys
import os
from config import Config

from src.ai_providers import DeepSeekProvider, AIProviderFactory


class TestDeepSeekProvider(unittest.TestCase):
    """Test cases for DeepSeekProvider"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = Config.DEEPSEEK_API_KEY
        self.model = Config.DEEPSEEK_MODEL
        self.provider = DeepSeekProvider(api_key=self.api_key, model=self.model)
    
    def test_init(self):
        """Test provider initialization"""
        self.assertEqual(self.provider.api_key, self.api_key)
        self.assertEqual(self.provider.model, self.model)
        self.assertEqual(self.provider._base_url, "https://api.deepseek.com/v1")
    
    @patch('ai_providers.requests.post')
    @patch('ai_providers.Config')
    def test_generate_word_note_success(self, mock_config, mock_post):
        """Test successful word note generation"""
        # Mock config
        mock_config.SYSTEM_INSTRUCTION = "Test system instruction"
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '  Test word note content  '
                }
            }]
        }
        mock_post.return_value = mock_response
        
        result = self.provider.generate_word_note("test", "chinese")
        
        # Verify the result
        self.assertEqual(result, "Test word note content")
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Check URL
        self.assertEqual(call_args[0][0], "https://api.deepseek.com/v1/chat/completions")
        
        # Check headers
        expected_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.assertEqual(call_args[1]['headers'], expected_headers)
        
        # Check request data
        request_data = call_args[1]['json']
        self.assertEqual(request_data['model'], self.model)
        self.assertEqual(len(request_data['messages']), 2)
        self.assertEqual(request_data['messages'][0]['role'], 'system')
        self.assertEqual(request_data['messages'][1]['role'], 'user')
        self.assertEqual(request_data['messages'][1]['content'], 'test')
        self.assertEqual(request_data['max_tokens'], 1500)
        self.assertEqual(request_data['temperature'], 1.3)
        self.assertEqual(call_args[1]['timeout'], 30)
    
    @patch('ai_providers.requests.post')
    @patch('ai_providers.Config')
    def test_generate_word_note_api_error(self, mock_config, mock_post):
        """Test word note generation with API error"""
        mock_config.SYSTEM_INSTRUCTION = "Test system instruction"
        
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            self.provider.generate_word_note("test", "chinese")
        
        self.assertIn("DeepSeek API error: 400 - Bad Request", str(context.exception))
    
    @patch('ai_providers.requests.post')
    @patch('ai_providers.Config')
    def test_generate_word_note_request_exception(self, mock_config, mock_post):
        """Test word note generation with request exception"""
        mock_config.SYSTEM_INSTRUCTION = "Test system instruction"
        
        # Mock request exception
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with self.assertRaises(Exception) as context:
            self.provider.generate_word_note("test", "chinese")
        
        self.assertIn("DeepSeek API request failed: Connection failed", str(context.exception))
    
    @patch('ai_providers.requests.post')
    @patch('ai_providers.Config')
    def test_generate_word_note_timeout(self, mock_config, mock_post):
        """Test word note generation with timeout"""
        mock_config.SYSTEM_INSTRUCTION = "Test system instruction"
        
        # Mock timeout exception
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with self.assertRaises(Exception) as context:
            self.provider.generate_word_note("test", "chinese")
        
        self.assertIn("DeepSeek API request failed: Request timed out", str(context.exception))
    
    def test_get_available_models(self):
        """Test getting available models"""
        expected_models = [
            "deepseek-chat",
            "deepseek-coder", 
            "deepseek-math"
        ]
        
        models = self.provider.get_available_models()
        self.assertEqual(models, expected_models)
    
    @patch.object(DeepSeekProvider, 'generate_word_note')
    def test_validate_api_key_success(self, mock_generate):
        """Test successful API key validation"""
        mock_generate.return_value = "Test result"
        
        result = self.provider.validate_api_key()
        
        self.assertTrue(result)
        mock_generate.assert_called_once_with("test", "english")
    
    @patch.object(DeepSeekProvider, 'generate_word_note')
    def test_validate_api_key_empty_result(self, mock_generate):
        """Test API key validation with empty result"""
        mock_generate.return_value = ""
        
        result = self.provider.validate_api_key()
        
        self.assertFalse(result)
    
    @patch.object(DeepSeekProvider, 'generate_word_note')
    def test_validate_api_key_exception(self, mock_generate):
        """Test API key validation with exception"""
        mock_generate.side_effect = Exception("API error")
        
        result = self.provider.validate_api_key()
        
        self.assertFalse(result)
    
    @patch.object(DeepSeekProvider, 'generate_word_note')
    def test_validate_api_key_none_result(self, mock_generate):
        """Test API key validation with None result"""
        mock_generate.return_value = None
        
        result = self.provider.validate_api_key()
        
        self.assertFalse(result)


class TestDeepSeekProviderIntegration(unittest.TestCase):
    """Integration tests for DeepSeekProvider with AIProviderFactory"""
    
    def test_factory_creation(self):
        """Test creating DeepSeekProvider through factory"""
        provider = AIProviderFactory.create_provider(
            'deepseek', 
            'test_api_key', 
            'deepseek-chat'
        )
        
        self.assertIsInstance(provider, DeepSeekProvider)
        self.assertEqual(provider.api_key, 'test_api_key')
        self.assertEqual(provider.model, 'deepseek-chat')
    
    def test_factory_available_providers(self):
        """Test getting available providers info includes DeepSeek"""
        providers_info = AIProviderFactory.get_available_providers()
        
        self.assertIn('deepseek', providers_info)
        deepseek_info = providers_info['deepseek']
        
        self.assertEqual(deepseek_info['name'], 'DeepSeek AI')
        self.assertTrue(deepseek_info['implemented'])
        self.assertIn('deepseek-chat', deepseek_info['models'])
    
    @patch.object(DeepSeekProvider, 'validate_api_key')
    def test_factory_validate_provider_key(self, mock_validate):
        """Test validating provider key through factory"""
        mock_validate.return_value = True
        
        result = AIProviderFactory.validate_provider_key('deepseek', 'test_key')
        
        self.assertTrue(result)
        mock_validate.assert_called_once()


class TestDeepSeekProviderEdgeCases(unittest.TestCase):
    """Edge case tests for DeepSeekProvider"""
    
    def setUp(self):
        self.provider = DeepSeekProvider("test_key", "deepseek-chat")
    
    @patch('ai_providers.requests.post')
    @patch('ai_providers.Config')
    def test_empty_word_input(self, mock_config, mock_post):
        """Test handling empty word input"""
        mock_config.SYSTEM_INSTRUCTION = "Test instruction"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Empty word response'}}]
        }
        mock_post.return_value = mock_response
        
        result = self.provider.generate_word_note("", "chinese")
        
        self.assertEqual(result, "Empty word response")
        # Verify empty string was passed to API
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json']['messages'][1]['content'], '')
    
    @patch('ai_providers.requests.post')
    @patch('ai_providers.Config')
    def test_special_characters_in_word(self, mock_config, mock_post):
        """Test handling special characters in word"""
        mock_config.SYSTEM_INSTRUCTION = "Test instruction"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Special char response'}}]
        }
        mock_post.return_value = mock_response
        
        special_word = "café/résumé@#$%"
        result = self.provider.generate_word_note(special_word, "chinese")
        
        self.assertEqual(result, "Special char response")
        # Verify special characters were preserved
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json']['messages'][1]['content'], special_word)
    
    @patch('ai_providers.requests.post')
    @patch('ai_providers.Config')
    def test_malformed_api_response(self, mock_config, mock_post):
        """Test handling malformed API response"""
        mock_config.SYSTEM_INSTRUCTION = "Test instruction"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': []  # Missing expected structure
        }
        mock_post.return_value = mock_response
        
        with self.assertRaises(Exception):
            self.provider.generate_word_note("test", "chinese")


if __name__ == '__main__':
    unittest.main()
