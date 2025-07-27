import os
import google.generativeai as genai
from typing import Optional

import os
import google.generativeai as genai
from typing import Optional

# System instruction for Chinese-style word analysis
CHINESE_INSTRUCTION = """
给出单词的联想词和常用的搭配。其他要求如下：
- 所有联想词单词都是常见词，限定在 CET-4/CET-6 词汇范围内。
- 音标遵循美式发音;
- 内容包括常见用法及搭配，形近词/音近词，近义词，反义词，同根词，其他联想词
- 考虑单词全部常用的词义、词性
- 近义词中，需要说明包括目标词在内的词义辨析 
- 其他联想词是与目标单词具有强关联性的单词，是包括除了形近词/音近词，近义词，反义词之后，其他容易共同出现在文本中的词汇。这一类单词不要包括过于简单的单词。
- 返回的内容中，不要使用加粗或者斜体，即不要使用 * 符号。

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

# English instruction for comprehensive word notes
ENGLISH_INSTRUCTION = """
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


class GeminiWordNoteGenerator:
    """A class to generate word notes using Google's Gemini AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini client.
        
        Args:
            api_key (str, optional): Gemini API key. If not provided, 
                                   will try to get from GEMINI_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_word_note(self, word: str, language: str = "en", style: str = "english") -> str:
        """Generate a comprehensive note for a given word.
        
        Args:
            word (str): The word to generate notes for.
            language (str): Language code (default: "en" for English).
            style (str): Note style - "english" for English format, "chinese" for Chinese format.
            
        Returns:
            str: Generated word note containing definition, examples, usage tips, etc.
        """
        
        if style.lower() == "chinese":
            system_instruction = CHINESE_INSTRUCTION
            prompt = word
        else:
            system_instruction = ENGLISH_INSTRUCTION
            prompt = f"Generate a comprehensive study note for the word: {word}"
        
        try:
            # Create a new model instance with system instruction
            model_with_instruction = genai.GenerativeModel(
                'gemini-1.5-flash',
                system_instruction=system_instruction
            )
            
            response = model_with_instruction.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating note for word '{word}': {e}")
            return f"Error generating note for '{word}': {str(e)}"
    
    def generate_batch_notes(self, words: list[str], language: str = "en", style: str = "english") -> dict[str, str]:
        """Generate notes for multiple words.
        
        Args:
            words (list[str]): List of words to generate notes for.
            language (str): Language code (default: "en").
            style (str): Note style - "english" for English format, "chinese" for Chinese format.
            
        Returns:
            dict[str, str]: Dictionary mapping words to their generated notes.
        """
        notes = {}
        total_words = len(words)
        
        for i, word in enumerate(words, 1):
            print(f"Generating note for '{word}' ({i}/{total_words})...")
            notes[word] = self.generate_word_note(word, language, style)
        
        return notes


def get_response(prompt: str, model: str = "gemini-1.5-flash") -> str:
    """Legacy function for backward compatibility.
    Get a response from the Gemini API.

    Args:
        prompt (str): The prompt to send to the model.
        model (str): The model to use for the response.

    Returns:
        str: The response from the Gemini API.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required.")
    
    genai.configure(api_key=api_key)
    model_instance = genai.GenerativeModel(model)
    
    try:
        response = model_instance.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Example usage
    try:
        generator = GeminiWordNoteGenerator()
        
        # Test with a single word
        word = "serendipity"
        note = generator.generate_word_note(word)
        print(f"Note for '{word}':")
        print(note)
        print("\n" + "="*50 + "\n")
        
        # Test with multiple words
        words = ["ephemeral", "ubiquitous", "paradigm"]
        notes = generator.generate_batch_notes(words)
        for word, note in notes.items():
            print(f"Note for '{word}':")
            print(note)
            print("\n" + "-"*30 + "\n")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set your GEMINI_API_KEY environment variable.")

# English instruction for comprehensive word notes
ENGLISH_INSTRUCTION = """
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
class GeminiWordNoteGenerator:
    """A class to generate word notes using Google's Gemini AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client.
        
        Args:
            api_key (str, optional): Gemini API key. If not provided, 
                                   will try to get from GEMINI_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_word_note(self, word: str, language: str = "en", style: str = "english") -> str:
        """
        Generate a comprehensive note for a given word.
        
        Args:
            word (str): The word to generate notes for.
            language (str): Language code (default: "en" for English).
            style (str): Note style - "english" for English format, "chinese" for Chinese format.
            
        Returns:
            str: Generated word note containing definition, examples, usage tips, etc.
        """
        
        if style.lower() == "chinese":
            system_instruction = CHINESE_INSTRUCTION
            prompt = word
        else:
            system_instruction = ENGLISH_INSTRUCTION
            prompt = f"Generate a comprehensive study note for the word: {word}"
        
        try:
            # Create a new model instance with system instruction
            model_with_instruction = genai.GenerativeModel(
                'gemini-1.5-flash',
                system_instruction=system_instruction
            )
            
            response = model_with_instruction.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating note for word '{word}': {e}")
            return f"Error generating note for '{word}': {str(e)}"
    
    def generate_batch_notes(self, words: list[str], language: str = "en") -> dict[str, str]:
        """
        Generate notes for multiple words.
        
        Args:
            words (list[str]): List of words to generate notes for.
            language (str): Language code (default: "en").
            
        Returns:
            dict[str, str]: Dictionary mapping words to their generated notes.
        """
        notes = {}
        total_words = len(words)
        
        for i, word in enumerate(words, 1):
            print(f"Generating note for '{word}' ({i}/{total_words})...")
            notes[word] = self.generate_word_note(word, language)
        
        return notes


def get_response(prompt: str, model: str = "gemini-1.5-flash") -> str:
    """
    Legacy function for backward compatibility.
    Get a response from the Gemini API.

    Args:
        prompt (str): The prompt to send to the model.
        model (str): The model to use for the response.

    Returns:
        str: The response from the Gemini API.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required.")
    
    genai.configure(api_key=api_key)
    model_instance = genai.GenerativeModel(model)
    
    try:
        response = model_instance.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Example usage
    try:
        generator = GeminiWordNoteGenerator()
        
        # Test with a single word
        word = "serendipity"
        note = generator.generate_word_note(word)
        print(f"Note for '{word}':")
        print(note)
        print("\n" + "="*50 + "\n")
        
        # Test with multiple words
        words = ["ephemeral", "ubiquitous", "paradigm"]
        notes = generator.generate_batch_notes(words)
        for word, note in notes.items():
            print(f"Note for '{word}':")
            print(note)
            print("\n" + "-"*30 + "\n")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set your GEMINI_API_KEY environment variable.")