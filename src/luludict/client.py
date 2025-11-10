import requests
import json
from typing import Optional, List, Dict, Any
import time
from config import Config

class LuLuDictClient:
    """A client for interacting with the LuLu Dictionary API."""
    
    def __init__(self, authorization_token: str=Config.LULUDICT_TOKEN, base_url: str = "https://api.frdic.com/api/open/v1"):
        """
        Initialize the LuLu Dict client.
        
        Args:
            authorization_token (str): Authorization token for the API.
            base_url (str): Base URL for the API.
        """
        self.authorization_token = authorization_token
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Authorization': authorization_token,
            'Content-Type': 'application/json'
        })
    
    def get_page_word_list(self, language: str = "en", category_id: int = 0, 
                     page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """
        Retrieve word list from LuLu Dictionary.
        
        Args:
            language (str): Language code (default: "en").
            category_id (int): Category ID (default: 0).
            page (int): Page number (default: 1).
            page_size (int): Number of words per page (default: 100).
            
        Returns:
            Dict[str, Any]: API response containing word list.
        """
        url = f"{self.base_url}/studylist/words"
        params = {
            "language": language,
            "category_id": category_id,
            "page": page,
            "page_size": page_size
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving word list: {e}")
            return {"error": str(e)}
    
    def get_all_words(self, language: str = "en", 
                     category_id: int = 0, 
                     max_pages: Optional[int] = None,
                     words_per_page: int = 100) -> List[str]:
        """
        Retrieve all words from all pages.
        
        Args:
            language (str): Language code.
            category_id (int): Category ID.
            max_pages (int, optional): Maximum number of pages to fetch.
            
        Returns:
            List[str]: List of all words.
        """
        all_words = []
        words_data = []
        page = 0
        
        try:
            while True:
                if max_pages and page > max_pages:
                    break
                    
                print(f"Fetching page {page}...")
                response = self.get_page_word_list(language, category_id, page, page_size=words_per_page)

                if "error" in response:
                    print(f"Error on page {page}: {response['error']}")
                    break
                
                # Extract words from response (adjust based on actual API response structure)
                page_words_data = response.get("data", [])
                if not page_words_data:
                    #No more words found on subsequent pages
                    break
                print(f"Found {len(page_words_data)} words on page {page}")

                words_data.extend(page_words_data)
                page += 1
                time.sleep(2)  # Rate limiting
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving words: {e}")
            return []

        # sort by star
        words_data = sorted(words_data, key=lambda x: x.get("star", ""), reverse=True)
        all_words = [word.get("word") for word in words_data if isinstance(word, dict)]
        print(f"Total words retrieved: {len(all_words)}")
        return all_words

    def update_word_star(self, word: str, star: int, language: str = "en") -> Dict[str, Any]:
        """Update the star rating for a word.

        Args:
            word (str): Target word to update.
            star (int): Desired star rating (0-5).
            language (str): Language code for the word list.

        Returns:
            Dict[str, Any]: API response or error information.
        """

        if not word:
            return {"error": "Word must be provided."}

        if not isinstance(star, int) or not (0 <= star <= 5):
            return {"error": "Star rating must be an integer between 0 and 5."}

        payload = {
            "language": language,
            "word": word,
            "star": star
        }

        endpoints = [
            f"{self.base_url}/studylist/word/star",
            f"{self.base_url}/studylist/word"
        ]

        last_error: Optional[str] = None

        for url in endpoints:
            try:
                response = self.session.post(url, json=payload)
                response.raise_for_status()

                try:
                    data = response.json() if response.content else {}
                except ValueError:
                    data = {"raw": response.text}

                return {
                    "success": True,
                    "message": data.get("message"),
                    "data": data,
                    "endpoint": url
                }
            except requests.exceptions.HTTPError as http_error:
                status_code = getattr(http_error.response, "status_code", None)
                if status_code in {404, 405}:
                    last_error = f"Endpoint {url} returned status {status_code}"
                    continue
                last_error = str(http_error)
                break
            except requests.exceptions.RequestException as request_error:
                last_error = str(request_error)
                break

        return {"error": last_error or "Failed to update word star."}
    
    def add_word_note(self, word: str, note: str, language: str = "en") -> Dict[str, Any]:
        """
        Add a note to a word in LuLu Dictionary.
        
        Args:
            word (str): The word to add note to.
            note (str): The note content.
            language (str): Language code.
            
        Returns:
            Dict[str, Any]: API response.
        """
        url = f"{self.base_url}/studylist/note"
        
        payload = json.dumps({
            "language": "en",
            "word": word,
            "note": note
            })

        try:
            response = self.session.post(url, data=payload)
            response.raise_for_status()
            if response.json()["message"]=='成功保存笔记':
                return {"success": True, "message": "Note added successfully."}
        except requests.exceptions.RequestException as e:
            print(f"Error adding note for word '{word}': {e}")
            return {"error": str(e)}
    
    def update_word_note(self, word: str, note: str, language: str = "en") -> Dict[str, Any]:
        """
        Update a note for a word in LuLu Dictionary.
        
        Args:
            word (str): The word to update note for.
            note (str): The new note content.
            language (str): Language code.
            
        Returns:
            Dict[str, Any]: API response.
        """
        url = f"{self.base_url}/studylist/note"
        payload = {
            "word": word,
            "language": language,
            "note": note
        }
        
        try:
            response = self.session.post(url=url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error updating note for word '{word}': {e}")
            return {"error": str(e)}
    
    def get_word_note(self, word: str, language: str = "en") -> Dict[str, Any]:
        """
        Get detailed information about a word.
        
        Args:
            word (str): The word to get details for.
            language (str): Language code.
            
        Returns:
            Dict[str, Any]: Word details from API.
        """
        url = f"{self.base_url}/studylist/note"
        params = {"language": language,
                  "word": word}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return False
            # print(f"Error getting details for word '{word}': {e}")
            # return {"error": str(e)}

    def get_page_word_with_notes(self, page: int = 1, 
                           page_size: int = 200, language: str = "en"):
        """
        Retrieve all word notes from LuLu Dictionary.
        
        Args:
            max_pages (int, optional): Maximum number of pages to fetch.
            page_size (int): Number of notes per page.
            
        Returns:
            List[Dict[str, Any]]: List of word notes.
        """
        all_notes = []
        url = f"{self.base_url}/studylist/notes"
        # ?language=en&page=0&page_size=100
        print(f"Fetching notes for page {page}...")
        params = {
            "language": language,
            "page": page,
            "page_size": page_size
        }
    
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving word list: {e}")
            return {"error": str(e)}
            
    def get_all_words_with_notes(self, max_pages: Optional[int] = None,
                                page_size: int = 600, language: str = "en") -> List[str]:
        """
        Retrieve all words with notes from LuLu Dictionary.
        
        Args:
            max_pages (int, optional): Maximum number of pages to fetch.
            page_size (int): Number of words per page.
            language (str): Language code.
            
        Returns:
            List[str]: List of words with notes.
        """
        all_words = []
        page = 0
        while True:
            if max_pages and page > max_pages:
                break

            print(f"Fetching words with notes for page {page}...")
            words = self.get_page_word_with_notes(page=page, page_size=page_size, language=language)
            page_words = [item.get("word") for item in words.get("data", []) if isinstance(item, dict)]
            if not page_words:
                print(f"No more words found on page {page}")
                break
            all_words.extend(words.get("data", []))
            print(f"Found {len(page_words)} words with notes on page {page}")

            page += 1
            time.sleep(2)

        return all_words

    def batch_add_notes(self, word_notes: Dict[str, str], language: str = "en",
                       delay: float = 1.0) -> Dict[str, Dict[str, Any]]:
        """
        Add notes to multiple words with rate limiting.
        
        Args:
            word_notes (Dict[str, str]): Dictionary mapping words to their notes.
            language (str): Language code.
            delay (float): Delay between requests in seconds.
            
        Returns:
            Dict[str, Dict[str, Any]]: Results for each word.
        """
        results = {}
        total_words = len(word_notes)
        
        for i, (word, note) in enumerate(word_notes.items(), 1):
            print(f"Adding note for '{word}' ({i}/{total_words})...")
            result = self.add_word_note(word, note, language)
            results[word] = result
            
            if i < total_words:  # Don't delay after the last word
                time.sleep(delay)
        
        return results
