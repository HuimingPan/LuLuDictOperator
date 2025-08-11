"""
Base AI Provider Interface and Implementations

This module provides a unified interface for different AI providers
to generate word notes and study materials.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List
import time

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model
    
    @abstractmethod
    def generate_word_note(self, word: str, style: str = "chinese") -> str:
        """Generate a word note for the given word"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider"""
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate the API key"""
        pass

class GeminiProvider(AIProvider):
    """Google Gemini AI Provider"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        super().__init__(api_key, model)
        self._generator = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the Gemini generator"""
        try:
            from src.gemini.gemini import GeminiWordNoteGenerator
            self._generator = GeminiWordNoteGenerator(self.api_key)
        except ImportError:
            raise ImportError("Gemini dependencies not installed")
    
    def generate_word_note(self, word: str, style: str = "chinese") -> str:
        """Generate a word note using Gemini"""
        if not self._generator:
            raise RuntimeError("Gemini provider not initialized")
        
        return self._generator.generate_word_note(
            word=word,
            language="en",
            style=style
        )
    
    def get_available_models(self) -> List[str]:
        """Get available Gemini models"""
        return [
            "gemini-2.5-flash",
            "gemini-1.5-flash", 
            "gemini-2.0-flash"
        ]
    
    def validate_api_key(self) -> bool:
        """Validate Gemini API key"""
        try:
            # Try a simple test generation
            test_result = self.generate_word_note("test", "english")
            return bool(test_result and len(test_result) > 0)
        except Exception:
            return False

class OpenAIProvider(AIProvider):
    """OpenAI GPT Provider (Placeholder Implementation)"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        # TODO: Initialize OpenAI client when implemented
    
    def generate_word_note(self, word: str, style: str = "chinese") -> str:
        """Generate a word note using OpenAI GPT"""
        # TODO: Implement OpenAI integration
        raise NotImplementedError("OpenAI provider not yet implemented")
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        return [
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-4-turbo"
        ]
    
    def validate_api_key(self) -> bool:
        """Validate OpenAI API key"""
        # TODO: Implement API key validation
        return False

class ClaudeProvider(AIProvider):
    """Anthropic Claude Provider (Placeholder Implementation)"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet"):
        super().__init__(api_key, model)
        # TODO: Initialize Claude client when implemented
    
    def generate_word_note(self, word: str, style: str = "chinese") -> str:
        """Generate a word note using Claude"""
        # TODO: Implement Claude integration
        raise NotImplementedError("Claude provider not yet implemented")
    
    def get_available_models(self) -> List[str]:
        """Get available Claude models"""
        return [
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku"
        ]
    
    def validate_api_key(self) -> bool:
        """Validate Claude API key"""
        # TODO: Implement API key validation
        return False

class DeepSeekProvider(AIProvider):
    """DeepSeek AI Provider"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        super().__init__(api_key, model)
        self._base_url = "https://api.deepseek.com/v1"
        
    def generate_word_note(self, word: str, style: str = "chinese") -> str:
        """Generate a word note using DeepSeek"""
        import requests
        import json
        
        # Choose the system instruction based on style
        if style.lower() == "chinese":
            system_instruction = """
给出单词的联想词和常用的搭配。其他要求如下：
- 所有联想词单词都是常见词，限定在 CET-4/CET-6 高级词汇范围内。
- 音标遵循美式发音;
- 内容包括常见用法及搭配，形近词/音近词，近义词，反义词，同根词，其他联想词
- 考虑单词全部常用的词义、词性
- 近义词中，需要说明包括目标词在内的词义辨析 
- 其他联想词是与目标单词具有强关联性的单词，是包括除了形近词/音近词，近义词，反义词之后，其他容易共同出现在文本中的词汇。这一类单词不要包括过于简单的单词。
- 返回的内容中，不要使用加粗或者斜体，即不要使用 * 符号。
- 不要出现连续的两个空行。

如对于单词 autonomous，返回：
#用法
1. adj. 自治的，独立的。指拥有自我管理或决策的权力，不受外部控制。
e.g. an autonomous region (自治区)
e.g. autonomous local governments
e.g. The university is an autonomous body within the national education system.
2. adj. 自动的，无人干预的。指机器、系统等无需人工操作或干预即可自行运行或完成任务。
e.g. autonomous vehicles/cars (自动驾驶汽车)
e.g. autonomous robots (自主机器人)
e.g. an autonomous weapon system
3. adj. (个人或组织) 有自主权的，独立的。指能够独立行动或做决策，不受他人或外部因素的支配。
e.g. autonomous decision-making (自主决策)
e.g. an autonomous learner (自主学习者)
e.g. Employees are encouraged to be autonomous in their work.

#联想
1.形近词/音近词:
automatic /ˌɔtəˈmætɪk/ (adj. 自动的；n. 自动装置): 指无需人工操作即可自行运行的。与autonomous相比，automatic更侧重于按预设程序或机制自行完成动作，而autonomous则强调系统或实体具有自我管理、决策或规划的能力，通常涉及更高级的智能或自由度。

2.近义词:
autonomous /ɔˈtɑnəməs/ (adj. 自治的，独立的): 强调实体或系统拥有自我管理、自我决策的权利或能力，不受外部控制。可以用于政治区域、组织机构或智能系统。
independent /ˌɪndɪˈpendənt/ (adj. 独立的): 最广泛的近义词。指不依赖于他人、不受他人控制或影响的。可用于国家、个人、组织、思想等。
self-governing /ˈselfˌɡʌvərnɪŋ/ (adj. 自治的): 直接表示能够自我治理、自我管理，通常用于政治实体或行政区域。与autonomous在政治语境下非常接近。
sovereign /ˈsɑvrən/ (adj. 主权的): 指国家或统治者拥有至高无上的权力，不受外部干涉，强调主权和独立地位。比autonomous和independent更强调国家或政权的终极权力。
self-reliant /ˌself rɪˈlaɪənt/ (adj. 自力更生的): 侧重于个人或群体依靠自身能力解决问题，不依赖外部帮助或支持，强调自给自足和独立应对挑战的能力。

3. 反义词:
dependent /dɪˈpendənt/ (adj. 依赖的，从属的)
subordinate /səˈbɔrdɪnət/ (adj. 从属的，下级的)
controlled /kənˈtroʊld/ (adj. 受控制的)

4. 同根词/派生词
autonomy /ɔˈtɑnəmi/ (n. 自治，自主权)
autonomously /ɔˈtɑnəməsli/ (adv. 自主地)
autocrat /ˈɔtəkræt/ (n. 独裁者)
autocratic /ˌɔtəˈkrætɪk/ (adj. 独裁的)

5. 其他联想词:
robot /ˈroʊbɑt/ (n. 机器人)
vehicle /ˈviːɪkl/ (n. 车辆)
decentralization /ˌdiːˌsentrəlɪˈzeɪʃən/ (n. 分散化，权力下放)
empowerment /ɪmˈpaʊərmənt/ (n. 授权，赋能)
"""
            user_prompt = word
        else:
            system_instruction = """
Create a comprehensive study note for the given word. Please include:
1. Clear definition with part of speech
2. Pronunciation guide (phonetic notation)
3. 2-3 example sentences showing different uses
4. Common collocations or phrases
5. Etymology or word origin (if interesting)
6. Any useful memory tips or mnemonics
7. Related words (synonyms, antonyms)

Format the response in a clear, study-friendly way that would be helpful for language learners.
Keep it concise but informative (around 150-200 words).
Do not use bold or italic formatting.
"""
            user_prompt = f"Generate a comprehensive study note for the word: {word}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self._base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                raise Exception(f"DeepSeek API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"DeepSeek API request failed: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get available DeepSeek models"""
        return [
            "deepseek-chat",
            "deepseek-coder", 
            "deepseek-math"
        ]
    
    def validate_api_key(self) -> bool:
        """Validate DeepSeek API key"""
        try:
            # Try a simple test generation
            test_result = self.generate_word_note("test", "english")
            return bool(test_result and len(test_result) > 0)
        except Exception:
            return False

class AIProviderFactory:
    """Factory for creating AI provider instances"""
    
    _providers = {
        'gemini': GeminiProvider,
        'openai': OpenAIProvider,
        'claude': ClaudeProvider,
        'deepseek': DeepSeekProvider
    }
    
    @classmethod
    def create_provider(cls, provider_type: str, api_key: str, model: str = None) -> AIProvider:
        """Create an AI provider instance"""
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown provider type: {provider_type}")
        
        provider_class = cls._providers[provider_type]
        
        if model:
            return provider_class(api_key, model)
        else:
            return provider_class(api_key)
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, Dict]:
        """Get information about available providers"""
        providers_info = {}
        
        for provider_type, provider_class in cls._providers.items():
            # Create a dummy instance to get model info
            try:
                dummy_instance = provider_class("dummy_key")
                providers_info[provider_type] = {
                    'name': provider_class.__doc__.split(' Provider')[0] if provider_class.__doc__ else provider_type.title(),
                    'models': dummy_instance.get_available_models(),
                    'implemented': provider_type in ['gemini', 'deepseek']  # Gemini and DeepSeek are implemented
                }
            except Exception:
                providers_info[provider_type] = {
                    'name': provider_type.title(),
                    'models': [],
                    'implemented': False
                }
        
        return providers_info
    
    @classmethod
    def validate_provider_key(cls, provider_type: str, api_key: str) -> bool:
        """Validate an API key for a specific provider"""
        try:
            provider = cls.create_provider(provider_type, api_key)
            return provider.validate_api_key()
        except Exception:
            return False

# Batch processing utility
class BatchProcessor:
    """Utility class for batch processing words with rate limiting"""
    
    def __init__(self, provider: AIProvider, delay: float = 10.0):
        self.provider = provider
        self.delay = delay
    
    def process_words(self, words: List[str], style: str = "chinese", 
                     progress_callback: Optional[callable] = None) -> Dict[str, Dict]:
        """Process multiple words with rate limiting"""
        results = {}
        total_words = len(words)
        
        for i, word in enumerate(words):
            try:
                if progress_callback:
                    progress_callback(f"Processing {i+1}/{total_words}: {word}")
                
                note = self.provider.generate_word_note(word, style)
                
                results[word] = {
                    'success': True,
                    'note': note,
                    'timestamp': time.time()
                }
                
                # Rate limiting delay (except for the last word)
                if i < total_words - 1:
                    time.sleep(self.delay)
                    
            except Exception as e:
                results[word] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': time.time()
                }
        
        return results
