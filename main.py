import os
import sys
import json
import time
from typing import Optional, Dict, List

from src.word_processor import WordNoteProcessor, create_processor_from_config, save_results
from config import Config


def main():
    """Main function to run the word note processor."""
    
    try:
        # Initialize processor using configuration
        processor = create_processor_from_config()
        
        # Option 1: Process all words from LuLu Dictionary (batch mode)
        print("Option 1: Processing words from your LuLu Dictionary word list...")
        results = processor.process_word_notes(
            language=Config.DEFAULT_LANGUAGE,
            category_id=Config.DEFAULT_CATEGORY_ID,
            max_words=10,  # Limit for testing - remove or increase for full processing
            delay_between_requests=Config.REQUEST_DELAY,  # Delay for LuLu Dictionary API
            gemini_delay=Config.GEMINI_DELAY,  # Delay between Gemini API calls
            skip_existing_notes=True,  # Skip words that already have notes
            processing_mode="batch"  # Use batch processing mode
        )
        
        # Save results to file
        save_results(results)
        
        # Option 2: Process specific words (uncomment to use)
        # specific_words = ["serendipity", "ephemeral", "ubiquitous"]
        # print(f"\nOption 2: Processing specific words: {specific_words}")
        # specific_results = processor.process_specific_words(
        #     words=specific_words,
        #     gemini_delay=Config.GEMINI_DELAY,
        #     luludict_delay=Config.REQUEST_DELAY
        # )
        # save_results(specific_results, "specific_words_results.json")
        # print("Specific words processing completed!")
        
    except Exception as e:
        print(f"❌ Error in main process: {e}")
        print("Make sure you have set your GEMINI_API_KEY environment variable.")
        print("You can set it by running: export GEMINI_API_KEY='your_api_key_here'")


if __name__ == "__main__":
    main()