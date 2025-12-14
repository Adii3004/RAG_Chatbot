"""
Utility functions for RAG Chatbot
"""

from urllib.parse import urlparse
import config

def is_valid_url(url, domain):
    """Check if URL is valid and belongs to same domain"""
    try:
        parsed = urlparse(url)
        is_same_domain = parsed.netloc == domain
        is_valid_scheme = parsed.scheme in ['http', 'https']
        has_bad_extension = any(url.lower().endswith(ext) for ext in config.SKIP_EXTENSIONS)
        
        return is_same_domain and is_valid_scheme and not has_bad_extension
    except:
        return False

def clean_text(text):
    """Clean and normalize text"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return ' '.join(lines)

def truncate_url(url, max_length=50):
    """Truncate URL for display"""
    if len(url) <= max_length:
        return url
    return url[:max_length] + "..."

def format_sources(sources):
    """Format source URLs as markdown links"""
    return [f"[{truncate_url(s)}]({s})" for s in sources]