import os
import glob
import json
import hashlib
from bs4 import BeautifulSoup, NavigableString
from deep_translator import GoogleTranslator
from logger import _logger

def get_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def translate_html():
    glossary = {}
    if os.path.exists('glossary.json'):
        with open('glossary.json', 'r', encoding='utf-8') as f:
            glossary = json.load(f)
            
    cache = {}
    if os.path.exists('.translation_cache.json'):
        with open('.translation_cache.json', 'r', encoding='utf-8') as f:
            cache = json.load(f)
            
    translator = GoogleTranslator(source='en', target='de')
    html_files = glob.glob('en/**/*.html', recursive=True)
    changed = False
    
    for en_path in html_files:
        if 'node_modules' in en_path or '.git' in en_path:
            continue
            
        current_hash = get_hash(en_path)
        de_path = en_path.replace('en/', 'de/', 1)
        
        if cache.get(en_path) == current_hash and os.path.exists(de_path):
            _logger.info(f"Cache hit for {en_path}, skipping translation.")
            continue
            
        _logger.info(f"Translating {en_path} -> {de_path}...")
        changed = True
        
        with open(en_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        de_navbar = soup.find('ul', class_='navbar-nav ms-auto')
        if de_navbar:
            existing_switcher = de_navbar.find('li', class_='language-switcher')
            if existing_switcher:
                existing_switcher.extract()
                
            en_target = '/' + en_path
            new_li = soup.new_tag('li', attrs={'class': 'nav-item ms-3 language-switcher'})
            new_a = soup.new_tag('a', attrs={'class': 'nav-link fw-bold', 'href': en_target})
            new_span = soup.new_tag('span', attrs={'class': 'badge rounded-pill bg-light text-dark'})
            new_span.string = "🇬🇧 EN"
            new_a.append(new_span)
            new_li.append(new_a)
            de_navbar.append(new_li)
        
        for element in soup.find_all(string=True):
            if isinstance(element, NavigableString):
                text = element.strip()
                if text and element.parent.name not in ['script', 'style']:
                    # apply glossary FIRST
                    for eng, ger in glossary.items():
                        text = text.replace(eng, ger)
                    
                    try:
                        translated_text = translator.translate(text)
                        if translated_text:
                            element.replace_with(translated_text)
                    except Exception as e:
                        _logger.exception(f"Translation failed for '{text}', {e}")
        
        os.makedirs(os.path.dirname(de_path), exist_ok=True)
        with open(de_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        cache[en_path] = current_hash
        
    if changed:
        with open('.translation_cache.json', 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)

if __name__ == "__main__":
    translate_html()
