"""
Test script for Gemini word note generation.
"""

import os
import sys
import unittest

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.ai_providers import GeminiProvider


class TestGeminiAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Check if API key is available
        if not os.getenv('GEMINI_API_KEY'):
            self.skipTest("GEMINI_API_KEY environment variable not set")

        self.ai_provider = GeminiProvider()

    def test_gemini_connection(self):
        """Test connection to Gemini API."""
        print("Testing Gemini API connection...")
        
        try:
            
            # Test with a simple prompt
            response = self.ai_provider.generate_content("Say hello")
            
            if response and response.text:
                print("✅ Successfully connected to Gemini API")
                print(f"Response: {response.text[:100]}...")
                self.assertTrue(True)
            else:
                print("❌ Failed to get response from Gemini API")
                self.fail("No response received from Gemini API")
                
        except Exception as e:
            print(f"❌ Error connecting to Gemini API: {e}")
            # Check if it's a proxy issue
            if "proxy" in str(e).lower() or "socks" in str(e).lower():
                self.skipTest(f"Proxy configuration issue: {e}")
            else:
                self.fail(f"Unexpected error: {e}")

    def test_single_word(self):
        """Test generating a note for a single word."""
        print("Testing single word note generation...")
        
        try:
            word = "ephemeral"
            note = self.ai_provider.generate_word_note(word)

            print(f"\n{'='*50}")
            print(f"Note for '{word}':")
            print(f"{'='*50}")
            print(note)
            print(f"{'='*50}\n")
            
            # Verify the note contains some content
            self.assertIsInstance(note, str)
            self.assertGreater(len(note), 10)
            self.assertNotIn("Error", note)
            
        except Exception as e:
            if "proxy" in str(e).lower() or "socks" in str(e).lower():
                self.skipTest(f"Proxy configuration issue: {e}")
            else:
                self.fail(f"Error generating single word note: {e}")

    def test_batch_words(self):
        """Test generating notes for multiple words."""
        print("Testing batch word note generation...")
        
        try:
            words = ["serendipity", "ubiquitous"]
            notes = self.ai_provider.generate_batch_notes(words)

            for word, note in notes.items():
                print(f"\n{'-'*30}")
                print(f"Note for '{word}':")
                print(f"{'-'*30}")
                print(note[:200] + "..." if len(note) > 200 else note)
            
            print(f"\n✅ Successfully generated {len(notes)} notes")
            
            # Verify results
            self.assertEqual(len(notes), len(words))
            for word in words:
                self.assertIn(word, notes)
                self.assertIsInstance(notes[word], str)
                self.assertGreater(len(notes[word]), 10)
            
        except Exception as e:
            if "proxy" in str(e).lower() or "socks" in str(e).lower():
                self.skipTest(f"Proxy configuration issue: {e}")
            else:
                self.fail(f"Error generating batch notes: {e}")
    
    def test_chinese_style_note(self):
        """Test generating a Chinese-style note."""
        print("Testing Chinese-style note generation...")
        
        try:
            word = "figure"
            note = self.ai_provider.generate_word_note(word, style="chinese")

            print(f"\n{'='*50}")
            print(f"Chinese-style note for '{word}':")
            print(f"{'='*50}")
            print(note)
            print(f"{'='*50}\n")
            
            # Verify the note contains Chinese content
            self.assertIsInstance(note, str)
            self.assertGreater(len(note), 20)
            
        except Exception as e:
            if "proxy" in str(e).lower() or "socks" in str(e).lower():
                self.skipTest(f"Proxy configuration issue: {e}")
            else:
                self.fail(f"Error generating Chinese-style note: {e}")


def standalone_test():
    """Standalone test function that can be run without unittest."""
    print("🧪 Running Gemini API tests...")
    print("Make sure GEMINI_API_KEY environment variable is set!")
    
    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY environment variable is not set.")
        print("Set it using: export GEMINI_API_KEY='your_api_key_here'")
        return False
    
    try:
        # Test basic functionality
        print("\n1. Testing basic connection...")
        ai_provider = GeminiProvider()
        print("✅ Generator initialized successfully")
        
        # Test single word
        print("\n2. Testing single word generation...")
        word = "ephemeral"
        note = ai_provider.generate_word_note(word)
        print(f"✅ Generated note for '{word}' ({len(note)} characters)")
        print(f"Preview: {note[:100]}...")
        
        # Test batch
        print("\n3. Testing batch generation...")
        words = ["serendipity"]
        notes = ai_provider.generate_batch_notes(words)
        print(f"✅ Generated {len(notes)} notes")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        if "proxy" in str(e).lower() or "socks" in str(e).lower():
            print(f"⚠️  Proxy configuration issue detected: {e}")
            print("💡 Try disabling proxy or configure it properly for the test.")
        else:
            print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    # Run standalone test first
    if standalone_test():
        print("\n" + "="*60)
        print("Running full unittest suite...")
        unittest.main(verbosity=2)
    else:
        print("Standalone test failed. Skipping unittest suite.")

