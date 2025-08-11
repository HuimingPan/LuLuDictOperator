"""
Flask Web Application for LuLu Dictionary Word Note Generator
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from typing import Dict, List, Optional
import threading
import queue

from src.word_processor import WordNoteProcessor, create_processor_from_config
from src.gemini.tools import GeminiWordNoteGenerator
from src.luludict.client import LuLuDictClient
from src.ai_providers import AIProviderFactory, BatchProcessor
from config import Config

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global variables for task management
task_queue = queue.Queue()
task_results = {}
task_status = {}

# Available AI providers
AI_PROVIDERS = AIProviderFactory.get_available_providers()

class AIProviderFactory:
    """Factory class to create AI providers based on selection"""
    
    @staticmethod
    def create_provider(provider_type: str, api_key: str, model: str = None):
        """Create an AI provider instance"""
        # Use the new AI provider system
        from src.ai_providers import AIProviderFactory as NewFactory
        return NewFactory.create_provider(provider_type, api_key, model)

def load_api_keys():
    """Load API keys from keys.json file"""
    try:
        with open('keys.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_api_keys(keys_data):
    """Save API keys to keys.json file"""
    try:
        with open('keys.json', 'w', encoding='utf-8') as f:
            json.dump(keys_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving keys: {e}")
        return False

def background_worker():
    """Background worker to process tasks"""
    while True:
        try:
            task = task_queue.get()
            if task is None:
                break
            
            task_id = task['id']
            print(f"Processing task {task_id}: {task.get('type', 'unknown')}")
            task_status[task_id] = 'processing'
            
            try:
                # Process the task based on type
                if task['type'] == 'batch_process':
                    result = process_batch_words(task)
                elif task['type'] == 'single_word':
                    result = process_single_word(task)
                else:
                    result = {'error': 'Unknown task type'}
                
                task_results[task_id] = result
                task_status[task_id] = 'completed'
                print(f"Task {task_id} completed successfully")
                
            except Exception as e:
                print(f"Task {task_id} failed: {str(e)}")
                task_results[task_id] = {'error': str(e)}
                task_status[task_id] = 'failed'
            
            task_queue.task_done()
            
        except Exception as e:
            print(f"Background worker error: {e}")

def process_batch_words(task):
    """Process multiple words in batch"""
    try:
        # Create processor with selected provider
        provider_type = task.get('provider', 'gemini')
        api_key = task.get('api_key')
        model = task.get('model')
        
        # Create AI provider using the factory
        try:
            ai_provider = AIProviderFactory.create_provider(provider_type, api_key, model)
        except NotImplementedError:
            return {'error': f'Provider {provider_type} not yet implemented'}
        
        # Use BatchProcessor for better handling
        batch_processor = BatchProcessor(
            provider=ai_provider,
            delay=task.get('delay', 10)
        )
        
        def progress_callback(message):
            task_status[task['id']] = message
        
        words = task.get('words', [])
        results = batch_processor.process_words(
            words=words,
            style=task.get('style', 'chinese'),
            progress_callback=progress_callback
        )
        
        # Convert results to expected format
        formatted_results = {}
        for word, result in results.items():
            if result['success']:
                formatted_results[word] = {
                    'success': True,
                    'note': result['note'],
                    'timestamp': datetime.fromtimestamp(result['timestamp']).isoformat()
                }
            else:
                formatted_results[word] = {
                    'success': False,
                    'error': result['error'],
                    'timestamp': datetime.fromtimestamp(result['timestamp']).isoformat()
                }
        
        return {'success': True, 'results': formatted_results}
        
    except Exception as e:
        return {'error': str(e)}

def process_single_word(task):
    """Process a single word"""
    try:
        provider_type = task.get('provider', 'gemini')
        api_key = task.get('api_key')
        model = task.get('model')
        word = task.get('word')
        
        # Create AI provider using the factory
        try:
            ai_provider = AIProviderFactory.create_provider(provider_type, api_key, model)
        except NotImplementedError:
            return {'error': f'Provider {provider_type} not yet implemented'}
        
        note = ai_provider.generate_word_note(
            word, 
            style=task.get('style', 'chinese')
        )
        
        return {
            'success': True,
            'word': word,
            'note': note,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {'error': str(e)}

# Start background worker
worker_thread = threading.Thread(target=background_worker, daemon=True)
worker_thread.start()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html', providers=AI_PROVIDERS)

@app.route('/api/keys')
def get_api_keys():
    """Get current API keys status"""
    keys = load_api_keys()
    status = {}
    
    for provider, config in AI_PROVIDERS.items():
        status[provider] = {
            'configured': bool(keys.get(provider) or os.getenv(f"{provider.upper()}_API_KEY")),
            'name': config['name'],
            'implemented': config.get('implemented', False)
        }
    
    return jsonify(status)

@app.route('/api/keys', methods=['POST'])
def save_keys():
    """Save API keys"""
    try:
        keys_data = load_api_keys()
        
        # Update with new keys from form
        for provider in AI_PROVIDERS.keys():
            key_field = f"{provider}_key"
            if key_field in request.json:
                keys_data[provider] = request.json[key_field]
        
        # Also save LuLu Dictionary key if provided
        if 'luludict_key' in request.json:
            keys_data['luludict'] = request.json['luludict_key']
        
        if save_api_keys(keys_data):
            return jsonify({'success': True, 'message': 'API keys saved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save API keys'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/generate', methods=['POST'])
def generate_word_note():
    """Generate word note using selected AI provider"""
    try:
        data = request.json
        word = data.get('word', '').strip()
        provider = data.get('provider', 'gemini')
        model = data.get('model', AI_PROVIDERS[provider]['models'][0])
        style = data.get('style', 'chinese')
        
        if not word:
            return jsonify({'success': False, 'message': 'Word is required'})
        
        # Get API key
        keys = load_api_keys()
        api_key = keys.get(provider) or os.getenv(f"{provider.upper()}_API_KEY")
        
        if not api_key:
            return jsonify({'success': False, 'message': f'API key for {provider} not configured'})
        
        # Create task
        task_id = f"single_{int(time.time())}"
        task = {
            'id': task_id,
            'type': 'single_word',
            'word': word,
            'provider': provider,
            'model': model,
            'style': style,
            'api_key': api_key
        }
        
        task_queue.put(task)
        task_status[task_id] = 'queued'
        
        return jsonify({'success': True, 'task_id': task_id})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/batch', methods=['POST'])
def batch_generate():
    """Generate notes for multiple words"""
    try:
        data = request.json
        words_text = data.get('words', '').strip()
        provider = data.get('provider', 'gemini')
        model = data.get('model', AI_PROVIDERS[provider]['models'][0])
        style = data.get('style', 'chinese')
        delay = float(data.get('delay', 10))
        
        if not words_text:
            return jsonify({'success': False, 'message': 'Words list is required'})
        
        # Parse words
        words = [word.strip() for word in words_text.replace(',', '\n').split('\n') if word.strip()]
        
        if not words:
            return jsonify({'success': False, 'message': 'No valid words found'})
        
        # Get API key
        keys = load_api_keys()
        api_key = keys.get(provider) or os.getenv(f"{provider.upper()}_API_KEY")
        
        if not api_key:
            return jsonify({'success': False, 'message': f'API key for {provider} not configured'})
        
        # Create task
        task_id = f"batch_{int(time.time())}"
        task = {
            'id': task_id,
            'type': 'batch_process',
            'words': words,
            'provider': provider,
            'model': model,
            'style': style,
            'delay': delay,
            'api_key': api_key
        }
        
        task_queue.put(task)
        task_status[task_id] = 'queued'
        
        return jsonify({'success': True, 'task_id': task_id, 'word_count': len(words)})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/task/<task_id>')
def get_task_status(task_id):
    """Get task status and results"""
    status = task_status.get(task_id, 'not_found')
    result = task_results.get(task_id)
    
    print(f"Task status check - ID: {task_id}, Status: {status}, Has result: {result is not None}")
    
    return jsonify({
        'task_id': task_id,
        'status': status,
        'result': result
    })

@app.route('/settings')
def settings():
    """Settings page"""
    keys = load_api_keys()
    return render_template('settings.html', providers=AI_PROVIDERS, keys=keys)

@app.route('/history')
def history():
    """Processing history page"""
    return render_template('history.html')

@app.route('/api/luludict/words')
def get_luludict_words():
    """Get words from LuLu Dictionary"""
    try:
        keys = load_api_keys()
        luludict_token = keys.get('luludict') or os.getenv('LULUDICT_TOKEN')
        
        if not luludict_token:
            return jsonify({'success': False, 'message': 'LuLu Dictionary token not configured'})
        
        client = LuLuDictClient(luludict_token)
        category_id = request.args.get('category_id', 0, type=int)
        page_size = request.args.get('page_size', 50, type=int)
        
        words = client.get_word_list(
            language='en',
            category_id=category_id,
            page_size=min(page_size, 100)  # Limit page size
        )
        
        return jsonify({'success': True, 'words': words})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/test/provider/<provider>')
def test_provider_direct(provider):
    """Direct test endpoint for AI providers"""
    try:
        # Get API key
        keys = load_api_keys()
        api_key = keys.get(provider) or os.getenv(f"{provider.upper()}_API_KEY")
        
        if not api_key:
            return jsonify({'success': False, 'message': f'API key for {provider} not configured'})
        
        # Test word
        test_word = "test"
        
        # Create AI provider
        try:
            ai_provider = AIProviderFactory.create_provider(provider, api_key)
            
            # Generate note directly (no background task)
            note = ai_provider.generate_word_note(test_word, "english")
            
            return jsonify({
                'success': True, 
                'provider': provider,
                'word': test_word,
                'note': note,
                'message': f'{provider} provider working correctly'
            })
            
        except NotImplementedError:
            return jsonify({'success': False, 'message': f'Provider {provider} not yet implemented'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Provider test failed: {str(e)}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
