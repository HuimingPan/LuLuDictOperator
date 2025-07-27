"""
Word Note Processor Library

A comprehensive library for generating word notes using Gemini AI and managing them 
in LuLu Dictionary. This module combines the functionality from both main.py and 
update_notes.py into a reusable library.
"""

import os
import sys
import json
import time
from typing import Optional, Dict, List, Union

from src.luludict.client import LuLuDictClient
from src.gemini.tools import GeminiWordNoteGenerator
from config import Config


class WordNoteProcessor:
    """
    Main orchestrator for generating and managing word notes.
    
    This class provides a comprehensive interface for:
    - Retrieving word lists from LuLu Dictionary
    - Generating notes using Gemini AI with rate limiting
    - Uploading generated notes back to LuLu Dictionary
    - Processing individual or batch words
    - Skipping words that already have notes
    """
    
    def __init__(self, luludict_token: str, gemini_api_key: Optional[str] = None):
        """
        Initialize the word note processor.
        
        Args:
            luludict_token (str): Authorization token for LuLu Dictionary API
            gemini_api_key (str, optional): Gemini API key. If not provided, 
                                          will try to get from GEMINI_API_KEY environment variable.
        """
        self.luludict_client = LuLuDictClient(luludict_token)
        self.gemini_generator = GeminiWordNoteGenerator(gemini_api_key)
        
    def process_word_notes(self, 
                          language: str = "en", 
                          category_id: int = 0, 
                          max_words: Optional[int] = None, 
                          delay_between_requests: float = 2.0,
                          gemini_delay: float = 15.0,
                          skip_existing_notes: bool = True,
                          processing_mode: str = "batch") -> Dict[str, Union[str, int, List]]:
        """
        Complete workflow: retrieve words, generate notes, and upload them.
        
        Args:
            language (str): Language code (default: "en")
            category_id (int): Category ID for word list (default: 0)
            max_words (int, optional): Maximum number of words to process
            delay_between_requests (float): Delay between LuLu API requests in seconds
            gemini_delay (float): Delay between Gemini API calls in seconds
            skip_existing_notes (bool): Whether to skip words that already have notes
            processing_mode (str): "batch" for batch processing, "individual" for one-by-one processing
            
        Returns:
            Dict[str, Union[str, int, List]]: Results summary
        """
        print("🚀 Starting word note generation process...")
        
        # Step 1: Retrieve word list
        print("\n📚 Step 1: Retrieving word list from LuLu Dictionary...")
        words = self.retrieve_word_list(language, category_id, max_words)
        
        if not words:
            print("❌ No words found. Exiting.")
            return {"error": "No words retrieved"}
        
        print(f"✅ Found {len(words)} words to process")
        
        # # Step 1.5: Filter out words that already have notes (if enabled)
        # if skip_existing_notes:
        #     print(f"\n🔍 Step 1.5: Filtering out words that already have notes...")
        #     words = self.exclude_words_with_note(words, language)
            
        #     if not words:
        #         print("✅ All words already have notes! No processing needed.")
        #         return {
        #             "total_words_checked": len(words),
        #             "words_needing_notes": 0,
        #             "notes_generated": 0,
        #             "successful_uploads": 0,
        #             "failed_uploads": 0,
        #             "existing_notes": [],
        #             "message": "All words already have notes"
        #         }
            
        #     print(f"📝 {len(words)} words need notes to be generated")
        
        # Choose processing mode
        if processing_mode == "individual":
            return self._process_words_individually(words, language, gemini_delay)
        else:
            return self._process_words_in_batch(words, language, gemini_delay, delay_between_requests)
    
    def _process_words_individually(self, words: List[str], language: str, gemini_delay: float) -> Dict:
        """Process words one by one (update_notes.py style)."""
        print(f"\n🔄 Processing words individually with {gemini_delay}s delay...")
        
        word_notes = {}
        successful_uploads = []
        failed_uploads = []
        existing_notes = []
        
        for i, word in enumerate(words, 1):
            print(f"\n📝 Processing '{word}' ({i}/{len(words)})...")
            
            try:
                # Check if word already has a note
                if self.luludict_client.get_word_note(word, language):
                    print(f"  ⏭️  '{word}' already has a note, skipping...")
                    existing_notes.append(word)
                    continue
                
                # Process the word
                result = self.process_specific_word(word, language)
                word_notes[word] = result["word_notes"]
                
                if "error" not in result["upload_results"]:
                    successful_uploads.append(word)
                    print(f"  ✅ Successfully processed '{word}'")
                else:
                    failed_uploads.append(word)
                    print(f"  ❌ Failed to upload note for '{word}'")
                
                # Add delay between words
                if i < len(words):
                    print(f"  ⏳ Waiting {gemini_delay}s before next word...")
                    time.sleep(gemini_delay)
                    
            except Exception as e:
                print(f"  ❌ Error processing '{word}': {e}")
                failed_uploads.append(word)
        
        summary = {
            "total_words_processed": len(words),
            "notes_generated": len(word_notes),
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "existing_notes": existing_notes,
            "word_notes": word_notes
        }
        
        self._print_summary(summary)
        return summary
    
    def _process_words_in_batch(self, words: List[str], language: str, 
                               gemini_delay: float, delay_between_requests: float) -> Dict:
        """Process words in batch mode (main.py style)."""
        print(f"\n🔄 Processing words in batch mode...")
        
        # Step 2: Generate notes using Gemini
        print(f"\n🤖 Step 2: Generating notes using Gemini AI...")
        word_notes = self.generate_notes_for_words(words, language, gemini_delay)
        
        # Step 3: Upload notes back to LuLu Dictionary
        print(f"\n📝 Step 3: Uploading notes to LuLu Dictionary...")
        upload_results = self.upload_notes_to_luludict(word_notes, language, delay_between_requests)
        
        # Summary
        successful_uploads = sum(1 for result in upload_results.values() if "error" not in result)
        failed_uploads = len(upload_results) - successful_uploads
        
        summary = {
            "total_words_processed": len(words),
            "notes_generated": len(word_notes),
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "upload_results": upload_results,
            "word_notes": word_notes
        }
        
        self._print_summary(summary)
        return summary
    
    def exclude_words_with_note(self, words: List[str], language: str = "en") -> List[str]:
        """
        Filter out words that already have notes in LuLu Dictionary.
        
        Args:
            words (List[str]): List of words to filter
            language (str): Language code (default: "en")
            
        Returns:
            List[str]: Words that don't have notes yet
        """
        words_without_notes = []
        
        print(f"🔍 Checking which words already have notes...")
        for i, word in enumerate(words, 1):
            print(f"Checking '{word}' ({i}/{len(words)})...")
            
            try:
                word_details = self.luludict_client.get_word_note(word, language)
                
                # Check if the word already has a note
                if word_details and "data" in word_details:
                    existing_note = word_details["data"].get("note", "").strip()
                    if existing_note:
                        print(f"  ⏭️  '{word}' already has a note, skipping...")
                    else:
                        print(f"  ✅ '{word}' needs a note")
                        words_without_notes.append(word)
                else:
                    # If we can't get details, include the word to be safe
                    print(f"  ⚠️  Couldn't check '{word}', including anyway...")
                    words_without_notes.append(word)
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ Error checking '{word}': {e}")
                # Include the word if we can't check
                words_without_notes.append(word)
        
        print(f"📋 Found {len(words_without_notes)} words that need notes out of {len(words)} total")
        return words_without_notes
    
    def retrieve_word_list(self, 
                          language: str = "en", 
                          category_id: int = 0, 
                          max_words: Optional[int] = None,
                          words_per_page: int = 600) -> List[str]:
        """
        Retrieve word list from LuLu Dictionary.
        
        Args:
            language (str): Language code (default: "en")
            category_id (int): Category ID for word list (default: 0)
            max_words (int, optional): Maximum number of words to retrieve
            words_per_page (int): Number of words per page (default: 200)
            
        Returns:
            List[str]: List of words from LuLu Dictionary
        """
        try:
            if max_words:
                # Calculate how many pages we need
                max_pages = (max_words + words_per_page - 1) // words_per_page
                words = self.luludict_client.get_all_words(language, category_id, max_pages, words_per_page)
                return words[:max_words] if len(words) > max_words else words
            else:
                return self.luludict_client.get_all_words(language, category_id, words_per_page=words_per_page)
        except Exception as e:
            print(f"❌ Error retrieving word list: {e}")
            return []
    
    def generate_notes_for_words(self, 
                               words: List[str], 
                               language: str = "en", 
                               gemini_delay: float = 15.0,
                               stop_on_error: bool = True) -> Dict[str, str]:
        """
        Generate notes for a list of words using Gemini with rate limiting.
        
        Args:
            words (List[str]): List of words to generate notes for
            language (str): Language code (default: "en")
            gemini_delay (float): Delay between Gemini API calls in seconds
            stop_on_error (bool): Whether to stop processing on first error
            
        Returns:
            Dict[str, str]: Dictionary mapping words to their generated notes
        """
        notes = {}
        total_words = len(words)
        
        print(f"🤖 Generating notes for {total_words} words with {gemini_delay}s delay between calls...")
        
        for i, word in enumerate(words, 1):
            print(f"📝 Generating note for '{word}' ({i}/{total_words})...")
            
            try:
                note = self.gemini_generator.generate_word_note(word, language)
                notes[word] = note
                print(f"  ✅ Generated note for '{word}' ({len(note)} characters)")
                
                # Add delay between Gemini API calls (except for the last word)
                if i < total_words:
                    print(f"  ⏳ Waiting {gemini_delay}s before next API call...")
                    time.sleep(gemini_delay)
                    
            except Exception as e:
                print(f"  ❌ Error generating note for '{word}': {e}")
                if stop_on_error:
                    print(f"  ❌ Stopping processing of subsequent words.")
                    break
                else:
                    notes[word] = f"Error: {str(e)}"
        
        successful_notes = sum(1 for note in notes.values() if not note.startswith("Error:"))
        print(f"🎉 Generated {successful_notes} successful notes out of {i}/{total_words} words")
        
        return notes
    
    def upload_notes_to_luludict(self, 
                                word_notes: Dict[str, str], 
                                language: str = "en", 
                                delay: float = 2.0) -> Dict[str, Dict]:
        """
        Upload generated notes to LuLu Dictionary.
        
        Args:
            word_notes (Dict[str, str]): Dictionary mapping words to notes
            language (str): Language code (default: "en")
            delay (float): Delay between upload requests in seconds
            
        Returns:
            Dict[str, Dict]: Upload results for each word
        """
        try:
            return self.luludict_client.batch_add_notes(word_notes, language, delay)
        except Exception as e:
            print(f"❌ Error uploading notes: {e}")
            return {}
    
    def process_specific_words(self, 
                             words: List[str], 
                             language: str = "en", 
                             gemini_delay: float = 2.0, 
                             luludict_delay: float = 1.0) -> Dict[str, Union[Dict, str]]:
        """
        Process specific words instead of retrieving from word list.
        
        Args:
            words (List[str]): List of specific words to process
            language (str): Language code (default: "en")
            gemini_delay (float): Delay between Gemini API calls in seconds
            luludict_delay (float): Delay between LuLu Dictionary API calls in seconds
            
        Returns:
            Dict[str, Union[Dict, str]]: Processing results
        """
        print(f"🚀 Processing {len(words)} specific words...")
        
        # Generate notes
        print("🤖 Generating notes using Gemini AI...")
        word_notes = self.generate_notes_for_words(words, language, gemini_delay, stop_on_error=False)
        
        # Upload notes
        print("📝 Uploading notes to LuLu Dictionary...")
        upload_results = self.upload_notes_to_luludict(word_notes, language, luludict_delay)
        
        return {
            "word_notes": word_notes,
            "upload_results": upload_results
        }
    
    def process_specific_word(self, word: str, language: str = "en") -> Dict[str, Union[str, Dict]]:
        """
        Process a specific single word.
        
        Args:
            word (str): The word to process
            language (str): Language code (default: "en")
            
        Returns:
            Dict[str, Union[str, Dict]]: Processing result for the word
        """
        print(f"🚀 Processing '{word}'")
        
        try:
            # Generate note
            print("🤖 Generating note using Gemini AI...")
            word_note = self.gemini_generator.generate_word_note(word, language)
            
            # Upload note
            print("📝 Uploading note to LuLu Dictionary...")
            upload_result = self.luludict_client.update_word_note(word, word_note)
            
            return {
                "word_notes": word_note,
                "upload_results": upload_result
            }
            
        except Exception as e:
            print(f"❌ Error processing '{word}': {e}")
            return {
                "word_notes": f"Error: {str(e)}",
                "upload_results": {"error": str(e)}
            }
    
    def get_word_note(self, word: str, language: str = "en") -> Optional[str]:
        """
        Get existing note for a word from LuLu Dictionary.
        
        Args:
            word (str): The word to check
            language (str): Language code (default: "en")
            
        Returns:
            Optional[str]: Existing note if found, None otherwise
        """
        try:
            return self.luludict_client.get_word_note(word, language)
        except Exception as e:
            print(f"❌ Error getting note for '{word}': {e}")
            return None
    
    def _print_summary(self, summary: Dict) -> None:
        """Print processing summary."""
        print(f"\n✨ Process completed!")
        print(f"📊 Summary:")
        print(f"   - Total words: {summary.get('total_words_processed', 0)}")
        print(f"   - Notes generated: {summary.get('notes_generated', 0)}")
        
        if isinstance(summary.get('successful_uploads'), list):
            print(f"   - Successful uploads: {len(summary['successful_uploads'])}")
            print(f"   - Failed uploads: {len(summary.get('failed_uploads', []))}")
            print(f"   - Existing notes: {len(summary.get('existing_notes', []))}")
        else:
            print(f"   - Successful uploads: {summary.get('successful_uploads', 0)}")
            print(f"   - Failed uploads: {summary.get('failed_uploads', 0)}")


def create_processor_from_config() -> WordNoteProcessor:
    """
    Create a WordNoteProcessor instance using configuration settings.
    
    Returns:
        WordNoteProcessor: Configured processor instance
        
    Raises:
        ValueError: If configuration validation fails
    """
    if not Config.validate():
        raise ValueError("Configuration validation failed. Please check your settings.")
    
    return WordNoteProcessor(
        luludict_token=Config.LULUDICT_TOKEN,
        gemini_api_key=Config.get_gemini_api_key()
    )


def save_results(results: Dict, filename: Optional[str] = None) -> str:
    """
    Save processing results to a JSON file.
    
    Args:
        results (Dict): Results dictionary to save
        filename (str, optional): Output filename. If not provided, uses Config.RESULTS_FILE
        
    Returns:
        str: Path to the saved file
    """
    output_file = filename or Config.RESULTS_FILE
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to '{output_file}'")
    return output_file
