"""
Configuration file for LuLu Dictionary Word Note Generator.
"""

import os
import json
from typing import Optional

class Config:
    """Configuration settings for the application."""
    
    # Load API keys from keys.json file
    _keys = {}
    try:
        with open('keys.json', 'r', encoding='utf-8') as f:
            _keys = json.load(f)
    except FileNotFoundError:
        print("⚠️ Warning: keys.json file not found. Please create it from keys.json.example")
    except json.JSONDecodeError:
        print("❌ Error: keys.json file is not valid JSON format")

    # LuLu Dictionary API settings
    LULUDICT_BASE_URL = "https://api.frdic.com/api/open/v1"
    LULUDICT_TOKEN = _keys.get('LuLuDict', os.getenv('LULUDICT_TOKEN', ''))
    
    # Gemini API settings
    GEMINI_API_KEY = _keys.get('Gemini', os.getenv('GEMINI_API_KEY', ''))
    GEMINI_MODEL = "gemini-2.5-flash"
    
    # Processing settings
    DEFAULT_LANGUAGE = "en"
    DEFAULT_CATEGORY_ID = 0
    DEFAULT_PAGE_SIZE = 100
    
    # Rate limiting settings
    REQUEST_DELAY = 2.0  # seconds between LuLu Dictionary API requests
    GEMINI_DELAY = 15.0   # seconds between Gemini API requests (be more conservative)
    BATCH_SIZE = 10      # number of words to process in each batch
    
    # File settings
    RESULTS_FILE = "word_notes_results.json"
    LOGS_FILE = "word_processor.log"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings."""
        if not cls.GEMINI_API_KEY:
            print("❌ 错误：未设置 Gemini API 密钥。")
            print("请在 keys.json 文件中设置 'gemini_api_key' 字段")
            print("或者使用环境变量：export GEMINI_API_KEY='your_api_key_here'")
            return False
        
        if not cls.LULUDICT_TOKEN:
            print("❌ 错误：未配置 LuLu 词典令牌。")
            print("请在 keys.json 文件中设置 'luludict_token' 字段")
            return False
        
        return True
    
    @classmethod
    def get_gemini_api_key(cls) -> Optional[str]:
        """Get Gemini API key from keys.json or environment variable."""
        return cls.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
    
    @classmethod
    def get_luludict_token(cls) -> Optional[str]:
        """Get LuLu Dictionary token from keys.json or environment variable."""
        return cls.LULUDICT_TOKEN or os.getenv('LULUDICT_TOKEN')
    
    @classmethod
    def reload_keys(cls):
        """Reload keys from keys.json file."""
        try:
            with open('keys.json', 'r', encoding='utf-8') as f:
                cls._keys = json.load(f)
                cls.GEMINI_API_KEY = cls._keys.get('Gemini', os.getenv('GEMINI_API_KEY', ''))
                cls.LULUDICT_TOKEN = cls._keys.get('LuLuDict', os.getenv('LULUDICT_TOKEN', ''))
                print("✅ API 密钥已重新加载")
        except FileNotFoundError:
            print("❌ 错误：找不到 keys.json 文件")
        except json.JSONDecodeError:
            print("❌ 错误：keys.json 文件格式无效")
