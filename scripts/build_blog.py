import os
import glob
import markdown
import yaml
from logger import _logger
from hash_utils import get_hash, load_cache, save_cache

def build_blog():
    """
    Main orchestration function to build blog posts from markdown files.
    
    Reads markdown files from 'en/blog/posts/', extracts YAML frontmatter,
    converts markdown to HTML, and injects it into a predefined template.
    Only processes files that have been modified since the last build
    by comparing file hashes against a local cache.
    """
    cache_file = '.build_cache.json'
    cache = load_cache(cache_file)
    
    template_path = 'templates/blog_post.html'
    if not os.path.exists(template_path):
        _logger.error(f"Template {template_path} not found.")
        return
        
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    md_files = glob.glob('en/blog/posts/*.md')
    changed = False
    
    for filepath in md_files:
        current_hash = get_hash(filepath)
        out_filepath = filepath.replace('.md', '.html')
        
        if cache.get(filepath) == current_hash and os.path.exists(out_filepath):
            _logger.info(f"Cache hit for {filepath}, skipping build.")
            continue
            
        changed = True
        _logger.info(f"Building {filepath} -> {out_filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if content.startswith('---'):
            _, fm, body = content.split('---', 2)
            meta = yaml.safe_load(fm)
        else:
            meta = {}
            body = content
            
        html_content = markdown.markdown(body)
        basename = os.path.splitext(os.path.basename(filepath))[0]
        
        final_html = template.format(
            title=meta.get('title', 'Blog Post'),
            category=meta.get('category', 'General'),
            date=meta.get('date', ''),
            read_time=meta.get('read_time', ''),
            content=html_content,
            basename=basename
        )
        
        with open(out_filepath, 'w', encoding='utf-8') as f:
            f.write(final_html)
            
        cache[filepath] = current_hash
        _logger.info(f"Built {out_filepath}")
        
    if changed:
        save_cache(cache, cache_file)

if __name__ == "__main__":
    build_blog()
