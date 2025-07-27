# LuLu Dictionary Word Note Generator

A comprehensive Python project that automatically generates detailed word notes using Google's Gemini AI and seamlessly manages them in your LuLu Dictionary word list.

## ✨ Features

- 📚 **Smart word retrieval** from LuLu Dictionary API with filtering
- 🤖 **AI-powered note generation** using Gemini AI including:
  - Clear definitions and meanings
  - Parts of speech identification  
  - Pronunciation guides (IPA notation)
  - Contextual example sentences
  - Common collocations and phrases
  - Etymology and word origins
  - Memory tips for retention
- 📝 **Automated note upload** back to LuLu Dictionary
- ⚡ **Dual processing modes**: Batch (fast) and Individual (careful)
- 🛡️ **Smart filtering** to skip words with existing notes
- � **Rate limiting** with configurable delays for API protection
- 🔧 **Unified library architecture** for easy reuse and customization
- 📊 **Comprehensive result tracking** with detailed success/failure reporting

## 📁 Project Structure

```
LuLuDictOperator/
├── main.py                    # Entry point for batch processing
├── update_notes.py            # Entry point for individual processing  
├── examples.py                # Usage examples and demonstrations
├── config.py                  # Centralized configuration with Config class
├── requirements.txt           # Python dependencies
├── setup.sh                   # Setup and installation script
├── src/
│   ├── word_processor.py      # 🆕 Unified WordNoteProcessor library
│   ├── luludict/
│   │   └── client.py          # LuLu Dictionary API client
│   └── gemini/
│       └── tools.py           # Gemini AI note generator with rate limiting
├── test/
│   └── test_gemini.py         # Test files
├── README.md                  # This file
└── README_LIBRARY.md          # Detailed library documentation
```

## 🚀 Quick Setup

### 1. Clone and Install

```bash
git clone <repository-url>
cd LuLuDictOperator
./setup.sh  # Automated setup (recommended)
```

Or install manually:

```bash
pip install -r requirements.txt
```

### 2. Get Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Set it as an environment variable:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

**Note**: Your LuLu Dictionary token is pre-configured in `config.py`

## 🎯 Usage

### Option 1: Quick Start - Batch Processing (Recommended)

```bash
python main.py
```

**What it does:**
- Retrieves your word list from LuLu Dictionary
- Generates notes for words without existing notes
- Processes words in efficient batches
- Uploads all notes at once
- Saves results to `word_notes_results.json`

### Option 2: Careful Processing - Individual Mode

```bash
python update_notes.py
```

**What it does:**
- Processes each word individually 
- Better error recovery and detailed progress
- Skips failed words and continues
- Ideal for large datasets or unreliable connections

### Option 3: Advanced Usage with Library

```python
from src.word_processor import create_processor_from_config, save_results

# Quick setup using config
processor = create_processor_from_config()

# Batch processing (fast)
results = processor.process_word_notes(
    max_words=20,
    processing_mode="batch",
    gemini_delay=3.0,
    skip_existing_notes=True
)

# Individual processing (careful)
results = processor.process_word_notes(
    max_words=10,
    processing_mode="individual", 
    gemini_delay=5.0
)

# Process specific words
specific_words = ["serendipity", "ubiquitous", "ephemeral"]
results = processor.process_specific_words(specific_words)

# Save results
save_results(results)
```

### Option 4: Run Examples

```bash
python examples.py
```

Demonstrates various usage patterns and processing modes.

## ⚙️ Configuration

The project uses a centralized `Config` class in `config.py` for all settings:

### API Settings
```python
# Automatically configured
LULUDICT_TOKEN = "your_luludict_token"  # Pre-configured
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # Set via environment
GEMINI_MODEL = "gemini-2.5-flash"  # Latest model
```

### Processing Settings
```python
# Rate limiting (recommended values)
REQUEST_DELAY = 2.0   # LuLu Dictionary API delay
GEMINI_DELAY = 15.0   # Gemini API delay (conservative)
BATCH_SIZE = 10       # Words per batch

# Processing defaults
DEFAULT_LANGUAGE = "en"
DEFAULT_CATEGORY_ID = 0  # All categories
```

### Method Parameters
```python
processor.process_word_notes(
    language="en",                    # Language code
    category_id=0,                   # LuLu category (0 = all)
    max_words=None,                  # Word limit (None = unlimited)
    delay_between_requests=2.0,      # LuLu API delay
    gemini_delay=15.0,              # Gemini API delay  
    skip_existing_notes=True,        # Skip words with notes
    processing_mode="batch"          # "batch" or "individual"
)
```

## 📊 Processing Modes

### 🚀 Batch Mode (`processing_mode="batch"`)
**Best for**: Large datasets, faster processing
- Generates all notes first, then uploads all at once
- **Pros**: Faster execution, fewer API calls
- **Cons**: Stops completely if any error occurs

### 🔍 Individual Mode (`processing_mode="individual"`)  
**Best for**: Careful processing, error recovery
- Processes each word completely before moving to next
- **Pros**: Better error handling, continues on failures
- **Cons**: Slower, more API calls

## 📈 Results and Output

### Batch Mode Results
```json
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
```json
{
    "total_words_processed": 10,
    "notes_generated": 8,
    "successful_uploads": ["word1", "word2"],
    "failed_uploads": ["word3"],
    "existing_notes": ["word4", "word5"],
    "word_notes": {...}
}
```

## 🔍 Example Generated Note

```
Word: serendipity

**Definition:** The occurrence of pleasant or valuable discoveries by accident or chance.

**Part of Speech:** Noun

**Pronunciation:** /ˌsɛrənˈdɪpɪti/

**Example Sentences:**
1. Finding that rare book was pure serendipity.
2. The scientific breakthrough was a result of serendipity rather than planned research.

**Collocations:** pure serendipity, happy serendipity, by serendipity

**Etymology:** Coined by Horace Walpole in 1754, derived from the Persian fairy tale "The Three Princes of Serendip."

**Memory Tip:** Think "serene dip" - a peaceful, unexpected dive into good fortune.
```

## 🛠️ Advanced Features

### Smart Word Filtering
- Automatically skips words that already have notes
- Configurable through `skip_existing_notes` parameter
- Saves time and API calls

### Rate Limiting Protection
- Built-in delays between API calls
- Configurable delays for both APIs
- Prevents rate limit violations

### Error Recovery
- Individual mode continues processing despite failures
- Detailed error reporting and logging
- Graceful handling of network issues

### Flexible Output
- JSON results with detailed statistics
- Configurable output file locations
- Easy integration with other tools

## 🧪 Testing and Examples

### Run Built-in Examples
```bash
python examples.py  # Demonstrates all processing modes
```

### Test Individual Components
```bash
python -m pytest test/  # Run test suite
```

### Debug Mode
Add detailed logging by modifying the Config class or using print statements.

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Import errors** | Run from project root directory |
| **API key errors** | Set `GEMINI_API_KEY` environment variable |
| **Rate limiting** | Increase `gemini_delay` in config |
| **No words found** | Verify LuLu Dictionary token and API access |
| **Network timeouts** | Use individual mode for better error recovery |

### Quick Fixes

```bash
# Check API key
echo $GEMINI_API_KEY

# Set API key
export GEMINI_API_KEY="your_api_key_here"

# Test configuration
python -c "from config import Config; print(Config.validate())"

# Run with minimal words for testing
python main.py  # Uses max_words=10 by default
```

## 📚 Documentation

- **README.md** (this file): Main project overview
- **README_LIBRARY.md**: Detailed library documentation  
- **examples.py**: Working code examples
- **config.py**: Configuration reference

## 🚀 Getting Started Checklist

- [ ] Clone repository
- [ ] Run `./setup.sh` or install requirements manually
- [ ] Set `GEMINI_API_KEY` environment variable
- [ ] Test with `python examples.py`
- [ ] Run `python main.py` for batch processing
- [ ] Check `word_notes_results.json` for results

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`python -m pytest test/`)
6. Submit a pull request

## 📄 License

This project is for educational and personal use. Please respect API usage terms and rate limits.
