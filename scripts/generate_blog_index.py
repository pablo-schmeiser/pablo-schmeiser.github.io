import os
import glob
import yaml
import json
from datetime import datetime
from bs4 import BeautifulSoup
from logger import _logger
from hash_utils import get_hash, load_cache, save_cache
def extract_metadata(html_path):
    """
    Extracts title, category, date/read_time string, and excerpt from a generated HTML blog post.
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    title_tag = soup.select_one('.hero-content h1')
    title = title_tag.get_text(strip=True) if title_tag else "Untitled"
    
    cat_tag = soup.select_one('.hero-content .skill-badge')
    category = cat_tag.get_text(strip=True) if cat_tag else "General"
    
    date_tag = soup.select_one('.hero-content .text-muted')
    date_time_str = date_tag.get_text(strip=True) if date_tag else ""
    
    article_content = soup.select_one('.article-content')
    excerpt = ""
    if article_content:
        p_tag = article_content.find('p')
        if p_tag:
            excerpt = p_tag.get_text(strip=True)
            
    return {
        "title": title,
        "category": category,
        "date_time_str": date_time_str,
        "excerpt": excerpt
    }
def get_sorting_date(md_path):
    """
    Reads the markdown file's frontmatter to get the exact date for sorting.
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm = parts[1]
            try:
                meta = yaml.safe_load(fm)
                date_str = meta.get('date', '')
                if date_str:
                    # Attempt to parse common formats like "Aug 11, 2026" or "2026-08-11"
                    try:
                        return datetime.strptime(date_str, "%b %d, %Y")
                    except ValueError:
                        try:
                            return datetime.strptime(date_str, "%Y-%m-%d")
                        except ValueError:
                            pass
            except Exception as e:
                _logger.warning(f"Could not parse yaml in {md_path}: {e}")
                
    return datetime.min
def generate_index_for_lang(lang, posts, template):
    """
    Generates the index.html file for the specified language using the sorted posts data.
    """
    page_title = "Blog" if lang == "en" else "Blog"
    page_description = "My latest thoughts, tutorials, and technical deep-dives." if lang == "en" else "Meine neuesten Gedanken, Tutorials und technischen Deep-Dives."
    other_lang = "de" if lang == "en" else "en"
    other_lang_flag = "🇩🇪 DE" if lang == "en" else "🇬🇧 EN"
    
    posts_html = ""
    for post in posts:
        meta = post[lang]
        if not meta:
            continue
            
        link = f"/{lang}/blog/posts/{post['basename']}.html"
        posts_html += f"""
            <div class="col">
              <a href="{link}" class="post-link">
                <div class="card glass-card h-100 post-card">
                  <div class="card-body p-4">
                    <span class="badge badge-primary rounded-pill skill-badge mb-3">{meta['category']}</span>
                    <h4 class="card-title fw-bold text-white mb-3">{meta['title']}</h4>
                    <p class="card-text card-text-excerpt text-muted mb-4">{meta['excerpt']}</p>
                    <div class="mt-auto">
                      <small class="text-primary"><i class="far fa-calendar-alt me-1"></i> {meta['date_time_str']}</small>
                    </div>
                  </div>
                </div>
              </a>
            </div>
        """
        
    final_html = template.format(
        lang=lang,
        page_title=page_title,
        page_description=page_description,
        other_lang=other_lang,
        other_lang_flag=other_lang_flag,
        posts=posts_html
    )
    
    out_dir = f"{lang}/blog"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    _logger.info(f"Generated {out_path} with {len(posts)} posts.")
def generate_blog_index():
    template_path = 'templates/blog_index.html'
    if not os.path.exists(template_path):
        _logger.error(f"Template {template_path} not found.")
        return
        
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    md_files = glob.glob('en/blog/posts/*.md')
    
    # Check cache to see if we need to regenerate
    # We will hash all md files and their translated html counterparts
    cache_file = '.blog_index_cache.json'
    cache = load_cache(cache_file)
    
    current_hashes = {}
    for md_path in md_files:
        current_hashes[md_path] = get_hash(md_path)
        
        basename = os.path.splitext(os.path.basename(md_path))[0]
        en_html = f"en/blog/posts/{basename}.html"
        de_html = f"de/blog/posts/{basename}.html"
        
        if os.path.exists(en_html):
            current_hashes[en_html] = get_hash(en_html)
        if os.path.exists(de_html):
            current_hashes[de_html] = get_hash(de_html)
            
    if cache == current_hashes and os.path.exists('en/blog/index.html') and os.path.exists('de/blog/index.html'):
        _logger.info("Cache hit for all blog files, skipping index generation.")
        return
    _logger.info("Changes detected, generating blog indexes...")
    
    posts_data = []
    
    for md_path in md_files:
        basename = os.path.splitext(os.path.basename(md_path))[0]
        sort_date = get_sorting_date(md_path)
        
        en_html = f"en/blog/posts/{basename}.html"
        de_html = f"de/blog/posts/{basename}.html"
        
        en_meta = extract_metadata(en_html) if os.path.exists(en_html) else None
        de_meta = extract_metadata(de_html) if os.path.exists(de_html) else None
        
        if en_meta:
            posts_data.append({
                "basename": basename,
                "sort_date": sort_date,
                "en": en_meta,
                "de": de_meta
            })
            
    # Sort chronologically (newest first)
    posts_data.sort(key=lambda x: x['sort_date'], reverse=True)
    
    generate_index_for_lang("en", posts_data, template)
    generate_index_for_lang("de", posts_data, template)
    
    save_cache(current_hashes, cache_file)
    
if __name__ == "__main__":
    generate_blog_index()

