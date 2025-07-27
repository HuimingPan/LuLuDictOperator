#!/usr/bin/env python3
"""
Example usage of the WordNoteProcessor library.

This script demonstrates different ways to use the unified WordNoteProcessor library
for generating and managing word notes with Gemini AI and LuLu Dictionary.
"""

import sys
import os
from typing import List

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.word_processor import WordNoteProcessor, create_processor_from_config, save_results
from config import Config


def example_batch_processing():
    """Example: Process words in batch mode (faster but less control)."""
    print("🔄 Example 1: Batch Processing")
    print("=" * 50)
    
    try:
        processor = create_processor_from_config()
        
        results = processor.process_word_notes(
            max_words=5,
            gemini_delay=3.0,
            processing_mode="batch",
            skip_existing_notes=True
        )
        
        save_results(results, "example_batch_results.json")
        print("✅ Batch processing completed!\n")
        
    except Exception as e:
        print(f"❌ Error in batch processing: {e}\n")


def example_individual_processing():
    """Example: Process words individually (more control, slower)."""
    print("🔄 Example 2: Individual Processing")
    print("=" * 50)
    
    try:
        processor = create_processor_from_config()
        
        results = processor.process_word_notes(
            max_words=3,
            gemini_delay=2.0,
            processing_mode="individual",
            skip_existing_notes=True
        )
        
        save_results(results, "example_individual_results.json")
        print("✅ Individual processing completed!\n")
        
    except Exception as e:
        print(f"❌ Error in individual processing: {e}\n")


def example_specific_words():
    """Example: Process specific words."""
    print("🔄 Example 3: Specific Words Processing")
    print("=" * 50)
    
    try:
        processor = create_processor_from_config()
        
        # Process a list of specific words
        words = ["serendipity", "ephemeral"]
        results = processor.process_specific_words(
            words=words,
            gemini_delay=2.0,
            luludict_delay=1.0
        )
        
        save_results(results, "example_specific_results.json")
        print("✅ Specific words processing completed!\n")
        
    except Exception as e:
        print(f"❌ Error in specific words processing: {e}\n")


def example_single_word():
    """Example: Process a single word."""
    print("🔄 Example 4: Single Word Processing")
    print("=" * 50)
    
    try:
        processor = create_processor_from_config()
        
        # Process a single word
        word = "ubiquitous"
        result = processor.process_specific_word(word)
        
        print(f"📝 Processed '{word}':")
        print(f"Note: {result['word_notes'][:100]}...")
        print(f"Upload result: {result['upload_results']}")
        print("✅ Single word processing completed!\n")
        
    except Exception as e:
        print(f"❌ Error in single word processing: {e}\n")


def example_check_existing_notes():
    """Example: Check which words already have notes."""
    print("🔄 Example 5: Check Existing Notes")
    print("=" * 50)
    
    try:
        processor = create_processor_from_config()
        
        # Get some words
        words = processor.retrieve_word_list(max_words=10)
        if words:
            words_without_notes = processor.exclude_words_with_note(words[:5])
            
            print(f"📋 Checked {len(words[:5])} words")
            print(f"📝 {len(words_without_notes)} words need notes")
            print(f"✅ {len(words[:5]) - len(words_without_notes)} words already have notes")
        
        print("✅ Note checking completed!\n")
        
    except Exception as e:
        print(f"❌ Error in note checking: {e}\n")


def example_custom_configuration():
    """Example: Use custom configuration."""
    print("🔄 Example 6: Custom Configuration")
    print("=" * 50)
    
    try:
        # Create processor with custom settings
        processor = WordNoteProcessor(
            luludict_token=Config.LULUDICT_TOKEN,
            gemini_api_key=Config.get_gemini_api_key()
        )
        
        # Use very conservative delays
        results = processor.process_word_notes(
            max_words=2,
            gemini_delay=5.0,      # 5 second delay
            delay_between_requests=3.0,  # 3 second delay
            processing_mode="batch"
        )
        
        print("✅ Custom configuration processing completed!\n")
        
    except Exception as e:
        print(f"❌ Error in custom configuration: {e}\n")


def main():
    """Run all examples."""
    print("🚀 WordNoteProcessor Library Examples")
    print("=" * 50)
    print("This script demonstrates various ways to use the WordNoteProcessor library.")
    print("Make sure your GEMINI_API_KEY environment variable is set!\n")
    
    # Check configuration
    if not Config.validate():
        print("❌ Configuration validation failed. Please check your settings.")
        return
    
    # Run examples (uncomment the ones you want to test)
    
    # Example 1: Batch processing (recommended for large datasets)
    example_batch_processing()
    
    # Example 2: Individual processing (recommended for careful processing)
    # example_individual_processing()
    
    # Example 3: Process specific words
    # example_specific_words()
    
    # Example 4: Process a single word
    # example_single_word()
    
    # Example 5: Check existing notes
    # example_check_existing_notes()
    
    # Example 6: Custom configuration
    # example_custom_configuration()
    
    print("🎉 Examples completed!")
    print("\n📚 Usage Tips:")
    print("- Use 'batch' mode for faster processing of many words")
    print("- Use 'individual' mode for careful processing with better error handling")
    print("- Adjust gemini_delay based on your API rate limits")
    print("- Set skip_existing_notes=True to avoid reprocessing words")
    print("- Use process_specific_words() for testing with known words")


if __name__ == "__main__":
    main()
