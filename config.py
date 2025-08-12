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
    DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

    DEEPSEEK_API_KEY = _keys.get('DeepSeek', os.getenv('DEEPEEK_API_KEY', ''))
    DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"

    # Processing settings
    DEFAULT_AI_PROVIDER = "deepseek"
    DEFAULT_LANGUAGE = "en"
    DEFAULT_CATEGORY_ID = 0
    DEFAULT_PAGE_SIZE = 100
    
    # Rate limiting settings
    REQUEST_DELAY = 2.0  # seconds between LuLu Dictionary API requests
    AI_DELAY = 15.0   # seconds between Gemini API requests (be more conservative)
    BATCH_SIZE = 10      # number of words to process in each batch
    
    # File settings
    RESULTS_FILE = "word_notes_results.json"
    LOGS_FILE = "word_processor.log"

    SYSTEM_INSTRUCTION = """
    给出单词的联想词和常用的搭配。具体要求如下：
    - 所有联想词单词都是常见词;
    - 音标遵循美式发音;
    - 内容包括常见用法及搭配，形近词/音近词，近义词，反义词，同根词，其他联想词
    - 考虑单词全部常用的词义、词性
    - 近义词中，需要说明包括目标词在内的词义辨析 
    - 其他联想词是与目标单词具有强关联性的单词，是包括除了形近词/音近词，近义词，反义词之后，其他容易共同出现在文本中的词汇。这一类单词不要包括过于简单的单词。
    - 返回的内容中，不要使用加粗或者斜体，即不要使用 * 符号。
    - 不要出现连续的两个空行。

    如对于单词 ballot，返回
    #用法
    1. N. 选票。指用于投票的纸张或电子记录，也指投票的行为。
    e.g. cast a ballot (投票)
    e.g. secret ballot (无记名投票)
    e.g. a ballot box (投票箱)
    e.g. The results of the ballot will be announced tomorrow.
    e.g. They held a ballot to choose a new leader.
    2. V. （通过投票）选举；投票表决。指通过投选票的方式进行选举或表决。
    e.g. ballot for (投票支持)
    e.g. ballot against (投票反对)
    e.g. ballot on (对...进行投票)
    e.g. Union members balloted on the proposed changes.

    #联想
    1.形近词/音近词:
    * billet /ˈbɪlɪt/ (n. 兵营；v. 驻扎)
    * ballet /ˈbæleɪ/ (n. 芭蕾舞)
    * callot (无常见词)

    2.近义词:
    * ballot (n. 选票, 投票；v. 选举, 投票表决): 强调通过纸质或电子选票进行的投票行为，可以是选举或表决。
    * vote /voʊt/ (n. 投票，选票；v. 投票): 最普遍的词，泛指通过表达意愿来做出选择或决定，可以是口头、举手或书面。
    * poll /poʊl/ (n. 民意调查，投票；v. 对...进行民意调查): 指对公众意见的调查，或投票站的投票过程，强调统计结果。
    * election /ɪˈlɛkʃən/ (n. 选举): 指通过投票选择代表或领导人的正式过程。
    * referendum /ˌrɛfəˈrɛndəm/ (n. 公民投票，全民公决): 指就某项特定议题举行的全民投票。
    * plebiscite /ˈplɛbəˌsaɪt/ (n. 公民投票，全民公决): 与 referendum 相似，通常指就某一重大政治问题进行的直接投票。
    * franchise /ˈfrænˌtʃaɪz/ (n. 选举权，特许经营权): 指公民的投票权，或商业上的特许经营权。

    3. 反义词:
    * appointment /əˈpɔɪntmənt/ (n. 任命)
    * designation /ˌdɛzɪɡˈneɪʃən/ (n. 指定，任命)
    * disenfranchisement /ˌdɪsɪnˈfrænˌtʃaɪzmənt/ (n. 剥夺选举权)

    4. 同根词/派生词
    * balloter /ˈbælətər/ (n. 投票人)

    5. 其他联想词:
    * democracy /dɪˈmɑkrəsi/ (n. 民主)
    * candidate /ˈkændɪdət/ (n. 候选人)
    * elector /ɪˈlɛktər/ (n. 选民)
    * constituency /kənˈstɪtʃuənsi/ (n. 选区，选民)
    * campaign /kæmˈpeɪn/ (n. 竞选活动；v. 参加竞选)
    * government /ˈɡʌvərnmənt/ (n. 政府)
    * legislation /ˌlɛdʒɪsˈleɪʃən/ (n. 立法)
    * reform /rɪˈfɔrm/ (n. 改革；v. 改革)
    * transparency /trænsˈpɛrənsi/ (n. 透明度)  
  """
    
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
    