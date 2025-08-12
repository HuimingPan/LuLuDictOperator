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
    GEMINI_DELAY = 15.0   # seconds between Gemini API requests (be more conservative)
    BATCH_SIZE = 10      # number of words to process in each batch
    
    # File settings
    RESULTS_FILE = "word_notes_results.json"
    LOGS_FILE = "word_processor.log"

    SYSTEM_INSTRUCTION = """
    给出单词的联想词和常用的搭配。其他要求如下：
    - 所有联想词单词都是常见词，限定在 CET-4/CET-6 高级词汇范围内。
    - 音标遵循美式发音;
    - 内容包括常见用法及搭配，形近词/音近词，近义词，反义词，同根词，其他联想词
    - 考虑单词全部常用的词义、词性
    - 近义词中，需要说明包括目标词在内的词义辨析 
    - 其他联想词是与目标单词具有强关联性的单词，是包括除了形近词/音近词，近义词，反义词之后，其他容易共同出现在文本中的词汇。这一类单词不要包括过于简单的单词。
    - 返回的内容中，不要使用加粗或者斜体，即不要使用 * 符号。
    - 不要出现连续的两个空行。

    如对于单词 figure，返回：
    #用法
    1. N. 数字，数目。代表数量、顺序等的符号。
    e.g. in figures (用数字表示)
    e.g. sales figures (销售数据)
    e.g. budget figures (预算数据)
    e.g. unemployment figures (失业数据)
    e.g. Write the amount in words and figures.
    2. N. 人物。指一个特定的人，尤指重要或有名望的人。
    e.g. high-profile/prominent/public/historical/political figure
    e.g. She's a leading figure in the fashion world.
    e.g. a stick figure (火柴人, 简笔画小人)
    3. N. 身材，体形。指人的身体的形状或轮廓。
    e.g. a slim/slender/full figure (苗条的/丰满的身材)
    e.g. She has a slender figure.
    4. N. 图形，图表。用于说明信息或数据的视觉表示。
    e.g. Please refer to Figure 3 for more details.
    5. VT. 认为，估计。在思考后得出结论或判断。
    e.g. figure in (考虑在内, 参与)
    e.g. figure on (指望, 预计)
    e.g. I figured he'd be late.
    6. VT. 计算。通过数学运算确定数量。
    e.g. figure out (弄懂, 算出)
    e.g. Can you figure out the total cost?
    7. VI. 出现，扮演角色。在某事中起到作用或参与。
    e.g. figure prominently (显著地出现)
    e.g. He figures prominently in the story.

    #联想
    1.形近词/音近词:
    finger /ˈfɪŋɡər/ (n. 手指；v. 用手指触摸)
    disfigure /dɪsˈfɪɡjər/ (v. 损毁...的外形)

    2.近义词:
    figure (n. 数字, 人物, 身材, 图形；v. 认为, 计算, 出现): 含义广泛，作为名词可以指代数字、人物、图形或体形；作为动词可以表示思考、计算或在某事中扮演角色。
    number /ˈnʌmbər/ (n. 数字, 数量): 主要指用来计数或表示数量的符号或概念。
    digit /ˈdɪdʒɪt/ (n. 数字, 位): 特指阿拉伯数字0到9中的任一个。

    3. 反义词:
    ignore /ɪɡˈnɔr/ (v. 忽视) (与 figure '认为' 相对)
    unknown /ˌʌnˈnoʊn/ (n. 未知数) (与 figure '数字' 相对)

    4. 同根词/派生词
    figuration /ˌfɪɡjəˈreɪʃən/ (n. 形状, 图案)
    figurative /ˈfɪɡjərətɪv/ (adj. 比喻的, 象征的)
    figuring /ˈfɪɡjərɪŋ/ (n. 计算, 估计)

    5. 其他联想词:
    chart /tʃɑrt/ (n. 图表)
    diagram /ˈdaɪəˌɡræm/ (n. 图解)
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
    