# WordNoteProcessor Library

A unified, reusable library for generating comprehensive word notes using Google's Gemini AI and managing them in LuLu Dictionary. This library consolidates all word processing functionality into a single, powerful, and flexible module.

## 🎯 Overview

The `WordNoteProcessor` library provides a complete solution for:
- **Smart word retrieval** from LuLu Dictionary API with filtering capabilities
- **AI-powered note generation** using Google's Gemini 2.5 Flash model  
- **Flexible processing modes** (batch vs individual) for different use cases
- **Intelligent error handling** and recovery mechanisms
- **Rate limiting protection** to respect API limits
- **Comprehensive result tracking** with detailed success/failure reporting

## 📁 Project Structure

```
LuLuDictOperator/
├── src/
│   ├── word_processor.py      # 🆕 Unified WordNoteProcessor library
│   ├── luludict/
│   │   └── client.py          # LuLu Dictionary API client
│   └── gemini/
│       └── tools.py           # Gemini AI note generator
├── main.py                    # 🔄 Entry point for batch processing
├── update_notes.py            # 🔄 Entry point for individual processing
├── examples.py                # 🆕 Comprehensive usage examples
├── config.py                  # 🔄 Centralized configuration with Config class
└── README_LIBRARY.md          # This file
```

## 🚀 Quick Start

### API Key Setup (Important!)

**Security First**: This project uses `keys.json` file to store sensitive API keys securely.

1. **Create keys file:**
```bash
cp keys.json.example keys.json
```

2. **Edit keys.json with your API keys:**
```json
{
    "gemini_api_key": "your_gemini_api_key_here",
    "luludict_token": "your_luludict_token_here"
}
```

3. **Get Gemini API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)

### Basic Usage

```python
from src.word_processor import create_processor_from_config

# Create processor from configuration (loads from keys.json)
processor = create_processor_from_config()

# Process words in batch mode (fast processing)
results = processor.process_word_notes(
    max_words=10,
    processing_mode="batch",
    gemini_delay=3.0,
    skip_existing_notes=True
)

print(f"✅ Processed {results['total_words_processed']} words")
print(f"📝 Generated {results['notes_generated']} notes")
print(f"⬆️ Uploaded {results['successful_uploads']} notes")
```

### Advanced Usage

```python
from src.word_processor import WordNoteProcessor, save_results
from config import Config

# Verify configuration first
if not Config.validate():
    print("Please configure your API keys in keys.json")
    exit(1)

# Create processor with custom settings
processor = WordNoteProcessor(
    luludict_token=Config.LULUDICT_TOKEN,
    gemini_api_key=Config.GEMINI_API_KEY
)

# Individual processing with custom delays for careful processing
results = processor.process_word_notes(
    max_words=5,
    processing_mode="individual",
    gemini_delay=5.0,
    skip_existing_notes=True
)

# Save results with custom filename
save_results(results, "my_custom_results.json")
```

## 🔧 Processing Modes

### 1. Batch Mode (`processing_mode="batch"`)
- **Best for**: Large datasets, faster processing
- **Behavior**: Generates all notes first, then uploads all at once
- **Pros**: Faster, less API calls
- **Cons**: Less control, stops completely if any error occurs

```python
results = processor.process_word_notes(
    processing_mode="batch",
    max_words=100,
    gemini_delay=2.0
)
```

### 2. Individual Mode (`processing_mode="individual"`)
- **Best for**: Careful processing, error recovery
- **Behavior**: Processes each word completely before moving to the next
- **Pros**: Better error handling, can skip failed words
- **Cons**: Slower, more API calls

```python
results = processor.process_word_notes(
    processing_mode="individual",
    max_words=50,
    gemini_delay=5.0
)
```

## 📚 Library Functions

### Core Classes

#### `WordNoteProcessor`
Main class for processing word notes with comprehensive functionality.

**Constructor:**
```python
WordNoteProcessor(luludict_token: str, gemini_api_key: Optional[str] = None)
```

**Key Methods:**
- `process_word_notes()` - Complete workflow with batch/individual modes
- `process_specific_words()` - Process a custom list of words
- `process_specific_word()` - Process a single word with full details
- `exclude_words_with_note()` - Smart filtering of words with existing notes
- `retrieve_word_list()` - Get word list from LuLu Dictionary with pagination
- `generate_notes_for_words()` - Batch note generation using Gemini AI
- `upload_notes_to_luludict()` - Batch upload notes to LuLu Dictionary

**Properties:**
- `luludict_client` - Access to LuLu Dictionary API client
- `gemini_generator` - Access to Gemini AI note generator

### Utility Functions

#### `create_processor_from_config()`
Creates a processor instance using centralized settings from the Config class.

```python
processor = create_processor_from_config()
```

**Features:**
- Automatic API key detection from environment variables
- Pre-configured with optimal settings
- Validates configuration before creation

#### `save_results(results, filename=None)`
Saves processing results to a JSON file with detailed formatting.

```python
save_results(results, "my_results.json")  # Custom filename
save_results(results)  # Uses Config.RESULTS_FILE default
```

**Features:**
- Pretty-printed JSON output
- Automatic timestamp inclusion
- Error handling for file operations

## ⚙️ Configuration

The library uses the centralized `Config` class for all settings:

### API Configuration
```python
# Configuration automatically loads from keys.json file
# File format:
# {
#     "gemini_api_key": "your_key_here",
#     "luludict_token": "your_token_here"
# }

# Fallback to environment variables if keys.json doesn't exist
Config.LULUDICT_TOKEN = "loaded from keys.json or LULUDICT_TOKEN env var"
Config.GEMINI_API_KEY = "loaded from keys.json or GEMINI_API_KEY env var"
Config.GEMINI_MODEL = "gemini-2.5-flash"      # Latest Gemini model

# Validate configuration
Config.validate()  # Returns True if all keys are present

# Reload keys if you update keys.json
Config.reload_keys()
```

### Rate Limiting Settings
```python
# Recommended production values
Config.REQUEST_DELAY = 2.0   # LuLu Dictionary API delay (seconds)
Config.GEMINI_DELAY = 15.0   # Gemini API delay (seconds) - conservative
Config.BATCH_SIZE = 10       # Words per processing batch
```

### Processing Configuration
```python
# Method parameters for process_word_notes()
processor.process_word_notes(
    language="en",                    # Language code (ISO 639-1)
    category_id=0,                   # LuLu category (0 = all categories)
    max_words=None,                  # Word limit (None = unlimited)
    delay_between_requests=2.0,      # LuLu API delay override
    gemini_delay=15.0,              # Gemini API delay override
    skip_existing_notes=True,        # Skip words with existing notes
    processing_mode="batch"          # "batch" (fast) or "individual" (careful)
)
```

### File Output Settings
```python
Config.RESULTS_FILE = "word_notes_results.json"  # Default output file
Config.LOGS_FILE = "word_processor.log"          # Log file location
```

## 📖 Usage Examples

### Example 1: Batch Processing
```python
from src.word_processor import create_processor_from_config, save_results

processor = create_processor_from_config()

results = processor.process_word_notes(
    max_words=20,
    processing_mode="batch",
    gemini_delay=3.0,
    skip_existing_notes=True
)

save_results(results)
```

### Example 2: Individual Processing
```python
results = processor.process_word_notes(
    max_words=10,
    processing_mode="individual",
    gemini_delay=5.0,
    skip_existing_notes=True
)
```

### Example 3: Specific Words
```python
words = ["serendipity", "ephemeral", "ubiquitous"]
results = processor.process_specific_words(
    words=words,
    gemini_delay=2.0
)
```

### Example 4: Single Word
```python
result = processor.process_specific_word("paradigm")
print(f"Note: {result['word_notes']}")
```

### Example 5: Check Existing Notes
```python
words = processor.retrieve_word_list(max_words=20)
words_without_notes = processor.exclude_words_with_note(words)
print(f"{len(words_without_notes)} words need notes")
```

## 🛡️ Error Handling

The library includes comprehensive error handling and recovery mechanisms:

### API Error Management
- **Gemini API failures**: Graceful degradation with detailed error messages
- **LuLu Dictionary errors**: Automatic retry logic with exponential backoff
- **Network timeouts**: Configurable timeout settings with fallback behavior
- **Rate limiting**: Built-in delays with automatic adjustment

### Processing Error Recovery
- **Individual mode**: Continues processing despite individual word failures
- **Batch mode**: Provides detailed failure analysis and partial results
- **Configuration validation**: Pre-flight checks before processing begins
- **Resource management**: Automatic cleanup and memory management

### Error Reporting
```python
# Detailed error information in results
{
    "failed_uploads": ["word1", "word2"],
    "error_details": {
        "word1": "Rate limit exceeded",
        "word2": "Network timeout"
    },
    "processing_errors": [...],
    "configuration_errors": [...]
}
```

## 📊 Return Formats

### Batch Mode Results
```python
{
    "total_words_processed": 10,
    "notes_generated": 8,
    "successful_uploads": 7,
    "failed_uploads": 1,
    "upload_results": {...},
    "word_notes": {...}
}
```

### Individual Mode Results
```python
{
    "total_words_processed": 10,
    "notes_generated": 8,
    "successful_uploads": ["word1", "word2", ...],
    "failed_uploads": ["word3"],
    "existing_notes": ["word4", "word5"],
    "word_notes": {...}
}
```

## 🎯 Migration Guide

### From `main.py`
```python
# Old way
processor = WordNoteProcessor(token, api_key)
results = processor.process_word_notes(max_words=10)

# New way
from src.word_processor import create_processor_from_config
processor = create_processor_from_config()
results = processor.process_word_notes(
    max_words=10,
    processing_mode="batch"
)
```

### From `update_notes.py`
```python
# Old way
# Custom individual processing logic

# New way
results = processor.process_word_notes(
    processing_mode="individual",
    gemini_delay=15.0
)
```

## 🧪 Testing and Examples

### Run Complete Test Suite
```bash
# Run all examples and demonstrations
python examples.py

# Run unit tests  
python -m pytest test/

# Test configuration
python -c "from config import Config; print('✅ Config valid' if Config.validate() else '❌ Config invalid')"
```

### Quick Validation
```bash
# Test basic functionality
python -c "
from src.word_processor import create_processor_from_config
processor = create_processor_from_config()
print('✅ Library loaded successfully')
"
```

### Performance Testing
```bash
# Test with limited words for performance analysis
python -c "
from src.word_processor import create_processor_from_config
import time
start = time.time()
processor = create_processor_from_config()
results = processor.process_word_notes(max_words=3, processing_mode='batch')
print(f'⏱️ Processed 3 words in {time.time()-start:.2f} seconds')
"
```

## 🔧 Customization

The library is designed to be flexible. You can:

1. **Custom delays**: Adjust `gemini_delay` and `delay_between_requests`
2. **Custom processing**: Use individual methods for specific workflows
3. **Custom configuration**: Create processor instances with specific settings
4. **Custom filtering**: Use `exclude_words_with_note()` for smart processing

## 🎉 Benefits of the Unified Library

1. **DRY Principle**: No code duplication between files
2. **Flexibility**: Two processing modes for different needs
3. **Maintainability**: Single source of truth for word processing logic
4. **Reusability**: Easy to use in different scripts and contexts
5. **Comprehensive**: Includes all features from both original files
6. **Well-documented**: Clear documentation and examples
