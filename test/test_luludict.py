import unittest
from src.luludict.client import LuLuDictClient
from config import Config

class TestLuluDict(unittest.TestCase):
    def setUp(self):
        self.client = LuLuDictClient(Config.LULUDICT_TOKEN)

    def test_add_note(self):
        """Test adding a note to a word."""
        word = "example"
        note = "This is a test note."
        response = self.client.add_word_note(word, note)
        
        self.assertIn("success", response)
        self.assertTrue(response["success"])
        self.assertIn("message", response)
        self.assertEqual(response["message"], "Note added successfully.")
    
    def test_get_page_word_list(self):
        words = self.client.get_page_word_list(language="en", category_id=0, page=1, page_size=10)
        
        words_list = [word["word"] for word in words.get("data", []) if isinstance(word, dict)]
        self.assertIsInstance(words, dict)
        self.assertIn("data", words)
        self.assertIsInstance(words["data"], list)
        self.assertEqual(len(words_list), 10)

    def test_get_all_words(self):
        """Test retrieving all words."""
        words = self.client.get_all_words(language="en", category_id=0, words_per_page=200)
        
        self.assertIsInstance(words, list)
        self.assertGreater(len(words), 0)
        self.assertIsInstance(words[0], str)

    def test_get_word_note(self):
        """Test retrieving a note for a specific word."""
        word = "beak"
        note = self.client.get_word_note(word, language="en")
        print(note['data'])
        print(note['data']['note'])
        self.assertIsInstance(note, dict)
        self.assertIn("word", note)
        self.assertEqual(note["word"], word)
        self.assertIn("note", note)
        self.assertIsInstance(note["note"], str)
    
    def test_update_word_note(self):
        """Test updating a note for a word."""
        word = "example"
        new_note = "This is an updated test note."
        response = self.client.update_word_note(word, new_note)
        self.assertIsInstance(response, dict)
        self.assertIn("message", response)
        self.assertIn("成功", response["message"])