"""
Configuration settings for RAG Chatbot
"""

# Crawler Settings
MAX_CRAWL_DEPTH = 2
MAX_PAGES = 50
CRAWL_TIMEOUT = 8
CRAWL_DELAY = 0.3

# Chunking Settings
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
MIN_CHUNK_SIZE = 100

# Embedding Settings
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
EMBEDDING_BATCH_SIZE = 32

# RAG Settings
TOP_K_RESULTS = 5
GEMINI_MODEL = 'gemini-2.5-flash'
MAX_OUTPUT_TOKENS = 2048
TEMPERATURE = 0.7

# UI Settings
PAGE_TITLE = "RAG Website Chatbot"
PAGE_ICON = "🤖"

# Skip these file extensions when crawling
SKIP_EXTENSIONS = [
    '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg',
    '.css', '.js', '.zip', '.exe', '.mp4', '.mp3',
    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
]

# Skip these HTML elements
SKIP_ELEMENTS = ['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']