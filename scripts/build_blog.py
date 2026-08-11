import os
import glob
import markdown
import yaml
import json
import hashlib
from logger import _logger

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
  <meta http-equiv="x-ua-compatible" content="ie=edge" />
  <title>{title} - Pablo Schmeiser Blog</title>
  
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/7.1.0/mdb.min.css" />
  <link rel="stylesheet" href="../../../style.css" />
  
  <style>
    .article-content {{ font-size: 1.1rem; line-height: 1.8; color: #cbd5e1; }}
    .article-content h2, .article-content h3 {{ color: #f8fafc; margin-top: 2rem; margin-bottom: 1rem; font-weight: 700; }}
    .article-content p {{ margin-bottom: 1.5rem; }}
  </style>
</head>
<body>
  <!-- Navbar -->
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark glass-navbar fixed-top">
    <div class="container">
      <a class="navbar-brand fw-bold" href="/en/">Pablo Schmeiser</a>
      <button class="navbar-toggler" type="button" data-mdb-collapse-init data-mdb-target="#navbarNav"
        aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <i class="fas fa-bars"></i>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <a class="nav-link" href="/en/">Resume</a>
          </li>
          <li class="nav-item">
            <a class="nav-link active" aria-current="page" href="/en/blog/">Blog</a>
          </li>
          <li class="nav-item ms-3 language-switcher"><a class="nav-link fw-bold" href="/de/blog/posts/{basename}.html"><span class="badge rounded-pill bg-light text-dark">🇩🇪 DE</span></a></li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- Post Header -->
  <div class="hero-section text-center text-white d-flex align-items-center justify-content-center" style="height: 50vh;">
    <div class="hero-content container">
      <span class="badge badge-primary rounded-pill skill-badge mb-3">{category}</span>
      <h1 class="display-4 fw-bold mb-3">{title}</h1>
      <p class="text-muted"><i class="far fa-calendar-alt me-2"></i> {date} &nbsp;&bull;&nbsp; {read_time}</p>
    </div>
  </div>

  <!-- Post Content -->
  <main class="container my-5">
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card glass-card">
          <div class="card-body p-5 article-content">
            {content}
            <hr class="text-white my-5">
            <div class="d-flex justify-content-between align-items-center">
              <a href="/en/blog/" class="btn btn-outline-light btn-rounded"><i class="fas fa-arrow-left me-2"></i> Back to Blog</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
  
  <footer class="bg-dark text-center text-white mt-auto glass-card" style="border-radius: 0;">
    <div class="text-center p-3" style="background-color: rgba(0, 0, 0, 0.2);">
      © 2026 Pablo Schmeiser
    </div>
  </footer>

  <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/7.1.0/mdb.umd.min.js"></script>
</body>
</html>
"""

def get_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def build_blog():
    cache = {}
    if os.path.exists('.build_cache.json'):
        with open('.build_cache.json', 'r', encoding='utf-8') as f:
            cache = json.load(f)

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
        
        final_html = TEMPLATE.format(
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
        with open('.build_cache.json', 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)

if __name__ == "__main__":
    build_blog()
