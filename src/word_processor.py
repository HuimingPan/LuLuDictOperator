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
from src.ai_providers import AIProviderFactory
from config import Config
from datetime import datetime

class WordNoteProcessor:
    """
    Main orchestrator for generating and managing word notes.
    
    This class provides a comprehensive interface for:
    - Retrieving word lists from LuLu Dictionary
    - Generating notes using  AI with rate limiting
    - Uploading generated notes back to LuLu Dictionary
    - Processing individual or batch words
    - Skipping words that already have notes
    """
    
    def __init__(self, luludict_token: str, 
                 ai_provider: str = Config.DEFAULT_AI_PROVIDER,
                 ):
        """
        Initialize the word note processor.
        
        Args:
            luludict_token (str): Authorization token for LuLu Dictionary API
            _api_key (str, optional): Gemini API key. If not provided, 
                                          will try to get from GEMINI_API_KEY environment variable.
        """
        self.luludict_client = LuLuDictClient(luludict_token)
        self.ai_generator = AIProviderFactory.create_provider(ai_provider)

    def process_word_notes(self, 
                          language: str = "en", 
                          max_words: Optional[int] = None, 
                          delay_between_requests: float = 2.0,
                          ai_delay: float = Config.AI_DELAY,
                          skip_existing_notes: bool = True,
                          processing_mode: str = "batch") -> Dict[str, Union[str, int, List]]:
        """
        Complete workflow: retrieve words, generate notes, and upload them.
        
        Args:
            language (str): Language code (default: "en")
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
        words = self.retrieve_word_list(language, max_words)
        
        if not words:
            print("❌ No words found. Exiting.")
            return {"error": "No words retrieved"}
        
        print(f"✅ Found {len(words)} words to process")
        
        # Step 1.1: Filter out words that already have notes (if enabled)
        if skip_existing_notes:
            print(f"\n🔍 Step 1.1: Filtering out words that already have notes...")
            words = self.exclude_words_with_note(words, language)
            
            if not words:
                print("✅ All words already have notes! No processing needed.")
                return {
                    "total_words_checked": len(words),
                    "words_needing_notes": 0,
                    "notes_generated": 0,
                    "successful_uploads": 0,
                    "failed_uploads": 0,
                    "existing_notes": [],
                    "message": "All words already have notes"
                }
            
            print(f"📝 {len(words)} words need notes to be generated")
        
        # Choose processing mode
        if processing_mode == "individual":
            return self._process_words_individually(words, language, ai_delay)
        else:
            return self._process_words_in_batch(words, language, ai_delay, delay_between_requests)

    def _process_words_individually(self, words: List[str], language: str, ai_delay: float) -> Dict:
        """Process words one by one."""
        print(f"\n🔄 Processing words individually with {ai_delay}s delay...")
        
        word_notes = {}
        successful_uploads = []
        failed_uploads = []
        
        for i, word in enumerate(words, 1):
            print(f"\n📝 Processing '{word}' ({i}/{len(words)})...")
            
            try:
                # Process the word
                note = self.ai_generator.generate_word_note(word, language)
                upload_result = self.luludict_client.update_word_note(word, note)
                word_notes[word] = note
                
                if "error" not in upload_result:
                    successful_uploads.append(word)
                    print(f"  ✅ Successfully processed '{word}'")
                else:
                    failed_uploads.append(word)
                    print(f"  ❌ Failed to upload note for '{word}'")
                
                # Add delay between words
                print(f"  ⏳ Waiting {ai_delay}s before next word...")
                time.sleep(ai_delay)

            except Exception as e:
                print(f"  ❌ Error processing '{word}': {e}")
                failed_uploads.append(word)
        
        summary = {
            "total_words_processed": len(words),
            "notes_generated": len(word_notes),
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "word_notes": word_notes
        }
        
        self._print_summary(summary)
        return summary
    
    def _process_words_in_batch(self, words: List[str], language: str, 
                               ai_delay: float, delay_between_requests: float) -> Dict:
        """Process words in batch mode."""
        print(f"\n🔄 Processing words in batch mode...")
        
        # Step 2: Generate notes using Gemini
        print(f"\n🤖 Step 2: Generating notes using Gemini AI...")
        total_words = len(words)
        print(f"🤖 Generating notes for {total_words} words with {ai_delay}s delay between calls...")
        word_notes = self.ai_generator.generate_multiple_words_note(words)
                    
        # Step 3: Upload notes back to LuLu Dictionary
        print(f"\n📝 Step 3: Uploading notes to LuLu Dictionary...")
        try:
            upload_results = self.luludict_client.batch_add_notes(word_notes, language, delay_between_requests)
        except Exception as e:
            print(f"❌ Error uploading notes: {e}")
            return {}        
        # Summary
        successful_uploads = sum(1 for result in upload_results.values() if "error" not in result)
        failed_uploads = len(upload_results) - successful_uploads
        
        summary = {
            "total_words_processed": len(words),
            "notes_generated": len(word_notes),
            "upload_results": upload_results,
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
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
        words_to_process = words.copy()
        words_to_exclude = []
        print(f"🔍 Checking which words already have notes...")

        words_with_notes = self.luludict_client.get_all_words_with_notes(language=language, page_size=600)
        base_time = datetime(2025, 7, 24)

        for word in words_with_notes:
            if word.get("add_time") and datetime.strptime(word["add_time"], "%Y-%m-%dT%H:%M:%SZ") > base_time:
                words_to_exclude.append(word)
                if word['word'] in words_to_process:
                    words_to_process.remove(word["word"])
        print(f"❌ Found {len(words_to_exclude)} words to be excluded from processing")
        print(f"✅ Found {len(words_to_process)} words to be included for processing")
        return words_to_process

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
        if max_words:
            # Calculate how many pages we need
            max_pages = (max_words + words_per_page - 1) // words_per_page
            words = self.luludict_client.get_all_words(language, category_id, max_pages, words_per_page)
            return words[:max_words] if len(words) > max_words else words
        else:
            return self.luludict_client.get_all_words(language, category_id, words_per_page=words_per_page)
    
    def _print_summary(self, summary: Dict) -> None:
        """Print processing summary."""
        print(f"\n✨ Process completed!")
        print(f"📊 Summary:")
        print(f"   - Total words: {summary.get('total_words_processed', 0)}")
        print(f"   - Notes generated: {summary.get('notes_generated', 0)}")
        if isinstance(summary.get('successful_uploads'), list):
            print(f"   - Successful uploads: {len(summary['successful_uploads'])}")
            print(f"   - Failed uploads: {len(summary.get('failed_uploads', []))}")
        else:
            print(f"   - Successful uploads: {summary.get('successful_uploads', 0)}")
            print(f"   - Failed uploads: {summary.get('failed_uploads', 0)}")


def create_processor_from_config(
       ai_provider: str = Config.DEFAULT_AI_PROVIDER,
) -> WordNoteProcessor:
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
        ai_provider=ai_provider,
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

