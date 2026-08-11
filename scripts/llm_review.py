import os
import glob
from google import genai
from logger import _logger
from hash_utils import get_hash, load_cache, save_cache

LLM_REVIEW_PROMPT = """You are an expert German translator and web developer.
Review the following German HTML translation of an English original. 
If the translation needs improvement (better phrasing, fixing broken HTML, etc.), return the ENTIRE improved German HTML code. 
If the translation is already perfect, return exactly the word "PERFECT". Do NOT wrap your output in markdown code blocks.

English Original:
{en_html}

German Translation:
{de_html}
"""

def get_modified_de_files(cache):
    """
    Finds all German HTML files that have been modified or don't match 
    their hash in the cache, indicating they need an LLM review.
    """
    files_to_review = []
    de_files = glob.glob('de/**/*.html', recursive=True)
    
    for filepath in de_files:
        current_hash = get_hash(filepath)
        if cache.get(filepath) != current_hash:
            _logger.info(f"Hash mismatch or missing for {filepath}, needs review.")
            files_to_review.append(filepath)
        else:
            _logger.info(f"Cache hit for {filepath}, skipping.")
            
    return files_to_review

def review_single_translation(client, de_path, en_path):
    """
    Reviews a single translation file pair using the Gemini API.
    If the LLM suggests improvements, writes the new content back to the German file.
    Returns (success_boolean, new_file_hash).
    """
    if not os.path.exists(de_path) or not os.path.exists(en_path):
        _logger.info(f"Missing EN or DE file for {de_path}")
        return False, None
        
    _logger.info(f"Reviewing translation for {de_path}...")
    with open(en_path, 'r', encoding='utf-8') as f:
        en_html = f.read()
        
    with open(de_path, 'r', encoding='utf-8') as f:
        de_html = f.read()
        
    prompt = LLM_REVIEW_PROMPT.format(en_html=en_html, de_html=de_html)
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
        result = response.text.strip()
        
        # Clean up possible markdown code block formatting
        if result.startswith("```html"):
            result = result[7:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        result = result.strip()
        
        if result != "PERFECT" and result != "":
            with open(de_path, 'w', encoding='utf-8') as f:
                f.write(result)
            _logger.info(f"Applied LLM improvements to {de_path}")
        
        return True, get_hash(de_path)
    except Exception as e:
        _logger.exception(f"Error reviewing {de_path}, {e}")
        return False, None

def review_translations():
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        _logger.warning("No GEMINI_API_KEY set, skipping LLM review.")
        return
        
    client = genai.Client(api_key=api_key)
    
    cache_file = '.llm_review_cache.json'
    cache = load_cache(cache_file)
    
    files_to_review = get_modified_de_files(cache)
    changed_cache = False
    
    for de_path in files_to_review:
        en_path = de_path.replace('de/', 'en/', 1)
        success, new_hash = review_single_translation(client, de_path, en_path)
        
        if success:
            cache[de_path] = new_hash
            changed_cache = True
            
    if changed_cache:
        save_cache(cache, cache_file)

if __name__ == "__main__":
    review_translations()
