import os
import glob
import json
from bs4 import BeautifulSoup, NavigableString
from deep_translator import GoogleTranslator
from logger import _logger
from hash_utils import get_hash, load_cache, save_cache

def update_navbar(soup, en_path):
    """
    Modifies the language switcher in the navbar of a translated HTML file
    to point back to its English counterpart.
    """
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

def translate_nodes(soup, translator, glossary):
    """
    Iterates through all text nodes in the BeautifulSoup object,
    applies the glossary replacements, and translates the text using GoogleTranslator.
    """
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

def process_file(en_path, de_path, translator, glossary):
    """
    Reads an English HTML file, translates its content to German,
    updates the navbar, and writes the resulting HTML to the target path.
    """
    _logger.info(f"Translating {en_path} -> {de_path}...")
    
    with open(en_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    update_navbar(soup, en_path)
    translate_nodes(soup, translator, glossary)
    
    os.makedirs(os.path.dirname(de_path), exist_ok=True)
    with open(de_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

def translate_html():
    glossary = {}
    if os.path.exists('glossary.json'):
        with open('glossary.json', 'r', encoding='utf-8') as f:
            glossary = json.load(f)
            
    cache_file = '.translation_cache.json'
    cache = load_cache(cache_file)
            
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
            
        process_file(en_path, de_path, translator, glossary)
        cache[en_path] = current_hash
        changed = True
        
    if changed:
        save_cache(cache, cache_file)

if __name__ == "__main__":
    translate_html()
