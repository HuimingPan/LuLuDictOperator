import os
import google.generativeai as genai
from typing import Optional
import time
from config import Config

# System instruction for Chinese-style word analysis
CHINESE_INSTRUCTION = """
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
    
    def __init__(self, api_key: Optional[str] = Config.GEMINI_API_KEY, gemini_model: str = Config.GEMINI_MODEL):
        """
        Initialize the Gemini client.
        
        Args:
            api_key (str, optional): Gemini API key. If not provided, 
                                   will try to get from GEMINI_API_KEY environment variable.
        """
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(gemini_model)
    
    def generate_word_note(self, word: str, language: str = "en", style: str = "Chinese") -> str:
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
                'gemini-2.5-flash',
                system_instruction=system_instruction
            )
            
            response = model_with_instruction.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating note for word '{word}': {e}")
            raise Exception
    
    def generate_batch_notes(self, words: list[str], language: str = "en", style: str = "chinese",
                             delay: int = 10) -> dict[str, str]:
        """
        Generate notes for multiple words.
        
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
            try:
                notes[word] = self.generate_word_note(word, language, style)
                time.sleep(delay)
            except Exception as e:
                print(f"Error generating note for '{word}': {e}")
                return notes
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
