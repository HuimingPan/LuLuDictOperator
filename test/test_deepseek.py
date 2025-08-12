import unittest
import os
from src.ai_providers import DeepSeekProvider
from config import Config

class TestDeepSeekProvider(unittest.TestCase):
    def setUp(self):
        api_key = os.getenv('DEEPSEEK_API_KEY', Config.DEEPSEEK_API_KEY)
        model = getattr(Config, 'DEFAULT_DEEPSEEK_MODEL', 'deepseek-chat')
        if not api_key:
            self.skipTest("DEEPSEEK_API_KEY not set in environment or config.")
        self.provider = DeepSeekProvider(api_key=api_key, model=model)

    def test_generate_word_note(self):
        """Test generating a word note with DeepSeekProvider."""
        note = self.provider.generate_word_note("example")
        self.assertIsInstance(note, str)
        self.assertGreater(len(note), 0)
        print("==========================")
        print(f"Generated note:\n {note}")
        print("==========================")

    def test_get_available_models(self):
        models = self.provider.get_available_models()
        self.assertIsInstance(models, list)
        self.assertIn('deepseek-chat', models)

    def test_validate_api_key(self):
        valid = self.provider.validate_api_key()
        self.assertIsInstance(valid, bool)

if __name__ == "__main__":
    unittest.main()
