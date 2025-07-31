# LuLu Dictionary Word Note Generator - Web Application

A comprehensive web application for generating word notes using multiple AI providers including Google Gemini, OpenAI GPT, and Anthropic Claude.

## Features

### 🚀 Multi-Provider AI Support
- **Google Gemini**: Fully implemented with multiple models
- **DeepSeek AI**: Fully implemented with chat, coder, and math models
- **OpenAI GPT**: Framework ready (implementation pending)
- **Anthropic Claude**: Framework ready (implementation pending)

### 📝 Word Processing
- **Single Word Generation**: Generate detailed notes for individual words
- **Batch Processing**: Process multiple words with rate limiting
- **Multiple Note Styles**: Chinese comprehensive format or English concise format

### 🔗 LuLu Dictionary Integration
- Import word lists directly from your LuLu Dictionary account
- Seamless integration with existing vocabulary management

### 🎨 Modern Web Interface
- Responsive Bootstrap-based design
- Real-time processing status updates
- History tracking and management
- Export capabilities

## Quick Start

### 1. Install Dependencies
```bash
./start_web.sh
```

### 2. Configure API Keys
1. Copy `keys.json.example` to `keys.json`
2. Add your API keys:
```json
{
  "gemini": "your-gemini-api-key",
  "luludict": "your-luludict-token",
  "deepseek": "your-deepseek-api-key",
  "openai": "your-openai-api-key",
  "anthropic": "your-anthropic-api-key"
}
```

### 3. Start the Application
```bash
python3 app.py
```

Visit `http://localhost:5000` in your browser.

## API Keys Setup

### Google Gemini
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to `keys.json` under the `"gemini"` field

### LuLu Dictionary
1. Visit [LuLu Dictionary API](https://api.frdic.com)
2. Get your API token
3. Add it to `keys.json` under the `"luludict"` field

### DeepSeek AI
1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Create a new API key
3. Add it to `keys.json` under the `"deepseek"` field

### OpenAI (Optional)
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to `keys.json` under the `"openai"` field

### Anthropic Claude (Optional)
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create a new API key
3. Add it to `keys.json` under the `"anthropic"` field

## Usage Guide

### Single Word Processing
1. Navigate to the home page
2. Enter a word in the "Single Word Generator" section
3. Select your preferred AI provider and model
4. Choose note style (Chinese comprehensive or English concise)
5. Click "Generate Note"

### Batch Processing
1. Use the "Batch Word Generator" section
2. Enter multiple words (comma or line separated)
3. Configure provider, model, style, and delay settings
4. Click "Start Batch Processing"
5. Monitor progress in real-time

### LuLu Dictionary Integration
1. Configure your LuLu Dictionary token in settings
2. Use the "LuLu Dictionary Integration" section
3. Set category ID and word limit
4. Click "Load Words" to import into batch processor

## Configuration

### Note Styles

#### Chinese Style (Comprehensive)
- Detailed usage examples with collocations
- Synonym and antonym analysis with distinctions
- Related words and word families
- Comprehensive coverage in Chinese

#### English Style (Concise)
- Clear definitions with part of speech
- Pronunciation guide
- Example sentences
- Etymology and memory tips
- Focused and study-friendly format

### Rate Limiting
Different providers have different rate limits:
- **Gemini**: 15 requests/minute (recommended 10s delay)
- **OpenAI**: Varies by plan
- **Claude**: Varies by plan

## Architecture

### Backend Components
- **Flask Web Server**: Main application server
- **AI Provider System**: Extensible provider interface
- **Task Queue**: Background processing with threading
- **LuLu Dictionary Client**: API integration

### Frontend Components
- **Bootstrap UI**: Responsive design framework
- **Real-time Updates**: AJAX-based status polling
- **History Management**: Local processing history
- **Export Functions**: JSON and text export

### File Structure
```
├── app.py                 # Main Flask application
├── config.py             # Application configuration
├── web_config.py         # Web-specific configuration
├── start_web.sh          # Startup script
├── requirements.txt      # Python dependencies
├── keys.json            # API keys (user-created)
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Home page
│   ├── settings.html   # Settings page
│   └── history.html    # History page
├── static/             # Static assets
│   └── style.css      # Custom CSS
└── src/
    ├── ai_providers/   # AI provider system
    ├── gemini/        # Gemini integration
    └── luludict/      # LuLu Dictionary integration
```

## Development

### Adding New AI Providers
1. Create a new provider class in `src/ai_providers/`
2. Inherit from `AIProvider` base class
3. Implement required methods:
   - `generate_word_note()`
   - `get_available_models()`
   - `validate_api_key()`
4. Register in `AIProviderFactory`

### Extending Functionality
- Add new note styles in provider implementations
- Extend the task queue system for new processing types
- Add new export formats in the frontend

## Security

### Production Deployment
1. Set `FLASK_ENV=production`
2. Use a secure secret key
3. Configure HTTPS
4. Set up proper firewall rules
5. Use environment variables for sensitive data

### API Key Security
- Keys are stored locally in `keys.json`
- Never commit `keys.json` to version control
- Use environment variables in production
- Rotate keys regularly

## Troubleshooting

### Common Issues

#### "Import error: flask"
```bash
pip install flask
```

#### "API key not configured"
1. Check `keys.json` exists and is valid JSON
2. Verify API key is correct
3. Test API key with provider's test endpoint

#### "Provider not yet implemented"
Currently only Gemini is fully implemented. OpenAI and Claude support is planned.

### Debug Mode
Set `FLASK_DEBUG=1` environment variable for detailed error messages.

## License

This project is part of the LuLu Dictionary Word Note Generator suite.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the configuration guide
3. Create an issue in the repository
