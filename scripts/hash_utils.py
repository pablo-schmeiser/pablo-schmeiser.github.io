import os
import json
import hashlib

def get_hash(filepath):
    """Calculates the MD5 hash of a file's contents."""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def load_cache(cache_file):
    """Loads a JSON cache file from disk, returning an empty dictionary if it doesn't exist."""
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache, cache_file):
    """Saves the given cache dictionary to a JSON file."""
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)
