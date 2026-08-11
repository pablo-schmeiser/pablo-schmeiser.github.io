import os
import glob
import json
import hashlib
from google import genai

def get_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_modified_de_files():
    cache = {}
    if os.path.exists('.llm_review_cache.json'):
        with open('.llm_review_cache.json', 'r', encoding='utf-8') as f:
            cache = json.load(f)
            
    files_to_review = []
    de_files = glob.glob('de/**/*.html', recursive=True)
    
    for filepath in de_files:
        current_hash = get_hash(filepath)
        if cache.get(filepath) != current_hash:
            files_to_review.append(filepath)
            
    return files_to_review, cache

def review_translations():
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("No GEMINI_API_KEY set, skipping LLM review.")
        return
        
    client = genai.Client(api_key=api_key)
    files_to_review, cache = get_modified_de_files()
    
    changed_cache = False
    
    for de_path in files_to_review:
        en_path = de_path.replace('de/', 'en/', 1)
        if not os.path.exists(de_path) or not os.path.exists(en_path):
            continue
            
        print(f"Reviewing translation for {de_path}...")
        with open(en_path, 'r', encoding='utf-8') as f:
            en_html = f.read()
            
        with open(de_path, 'r', encoding='utf-8') as f:
            de_html = f.read()
            
        prompt = f"""You are an expert German translator and web developer.
Review the following German HTML translation of an English original. 
If the translation needs improvement (better phrasing, fixing broken HTML, etc.), return the ENTIRE improved German HTML code. 
If the translation is already perfect, return exactly the word "PERFECT". Do NOT wrap your output in markdown code blocks.

English Original:
{en_html}

German Translation:
{de_html}
"""
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            result = response.text.strip()
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
                print(f"Applied LLM improvements to {de_path}")
            
            # Update cache with the final hash (whether changed or not)
            cache[de_path] = get_hash(de_path)
            changed_cache = True
        except Exception as e:
            print(f"Error reviewing {de_path}: {e}")
            
    if changed_cache:
        with open('.llm_review_cache.json', 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)

if __name__ == "__main__":
    review_translations()
