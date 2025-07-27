import os
import sys
import json
import time
from typing import Optional, Dict, List

from src.word_processor import WordNoteProcessor, create_processor_from_config, save_results
from config import Config


def main():
    """Main function to run the word note processor in individual mode."""
    
    try:
        # Initialize processor using configuration
        processor = create_processor_from_config()
        
        # Process words individually (update_notes.py style)
        print("Processing words individually from your LuLu Dictionary word list...")
        results = processor.process_word_notes(
            language=Config.DEFAULT_LANGUAGE,
            category_id=Config.DEFAULT_CATEGORY_ID,
            max_words=None,  # Process all words or set a limit for testing
            delay_between_requests=Config.REQUEST_DELAY,  # Delay for LuLu Dictionary API
            gemini_delay=15.0,  # 15 second delay between individual word processing
            skip_existing_notes=True,  # Skip words that already have notes
            processing_mode="individual"  # Use individual processing mode
        )
        
        # Save results to file
        save_results(results, "update_notes_results.json")
        
        # Optional: Process specific words individually
        # specific_words = ["serendipity", "ephemeral", "ubiquitous"]
        # print(f"\nProcessing specific words individually: {specific_words}")
        # for word in specific_words:
        #     result = processor.process_specific_word(word)
        #     print(f"Processed '{word}': {result}")
        
    except Exception as e:
        print(f"❌ Error in main process: {e}")
        print("Make sure you have set your GEMINI_API_KEY environment variable.")
        print("You can set it by running: export GEMINI_API_KEY='your_api_key_here'")


if __name__ == "__main__":
    main()