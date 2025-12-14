import streamlit as st
from urllib.parse import urlparse
import time

# Import custom modules
from crawler import WebsiteCrawler
from knowledge_base import KnowledgeBase
from rag_chatbot import RAGChatbot
import config

# Page configuration
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
    }
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if 'knowledge_base' not in st.session_state:
        st.session_state.knowledge_base = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'crawled_url' not in st.session_state:
        st.session_state.crawled_url = None
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None
    if 'pages_crawled' not in st.session_state:
        st.session_state.pages_crawled = 0

init_session_state()

# Header
st.markdown('<h1 class="main-header">RAG Website Chatbot</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Ask intelligent questions about any website using AI</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## Configuration")
    
    # API Key Input
    with st.expander("API Key Setup", expanded=not st.session_state.api_key):
        st.markdown("**Get your FREE Gemini API key:**")
        st.markdown("1. Visit [Google AI Studio](https://aistudio.google.com/apikey)")
        st.markdown("2. Sign in and create API key")
        st.markdown("3. Paste it below")
        
        api_key_input = st.text_input(
            "Enter API Key",
            type="password",
            value=st.session_state.api_key if st.session_state.api_key else "",
            placeholder="AIzaSy..."
        )
        
        if api_key_input:
            st.session_state.api_key = api_key_input
            st.success("API Key saved!")
        else:
            st.warning("API key required to continue")
    
    st.markdown("---")
    
    # Website URL Input
    st.markdown("### Website to Analyze")
    website_url = st.text_input(
        "Enter URL",
        placeholder="https://example.com",
        label_visibility="collapsed"
    )
    
    # Crawl Button
    crawl_disabled = not website_url or not st.session_state.api_key
    
    if st.button("Start Crawling", type="primary", disabled=crawl_disabled):
        try:
            parsed = urlparse(website_url)
            if not parsed.scheme or not parsed.netloc:
                st.error("Please enter a valid URL with http:// or https://")
            else:
                # Reset previous data
                st.session_state.knowledge_base = None
                st.session_state.chat_history = []
                
                with st.spinner("Processing..."):
                    status_placeholder = st.empty()
                    
                    # Crawl website
                    status_placeholder.info("Initializing crawler...")
                    crawler = WebsiteCrawler(website_url)
                    pages = crawler.crawl(lambda msg: status_placeholder.info(msg))
                    
                    if not pages:
                        status_placeholder.error("No pages could be crawled")
                        st.error("The website might be blocking automated access. Try a different site.")
                    else:
                        st.session_state.pages_crawled = len(pages)
                        
                        # Build knowledge base
                        kb = KnowledgeBase()
                        success = kb.build(pages, lambda msg: status_placeholder.info(msg))
                        
                        if success:
                            st.session_state.knowledge_base = kb
                            st.session_state.crawled_url = website_url
                            status_placeholder.success(f"Successfully indexed {len(pages)} pages!")
                            time.sleep(1.5)
                            status_placeholder.empty()
                            st.rerun()
                        else:
                            status_placeholder.error("Failed to build knowledge base")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Status Display
    if st.session_state.knowledge_base:
        st.markdown("---")
        st.markdown("### Status")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Pages", st.session_state.pages_crawled, delta="Crawled")
        with col2:
            st.metric("Chunks", len(st.session_state.knowledge_base.chunks), delta="Indexed")
        
        st.success("Ready to chat!")
        
        if st.session_state.crawled_url:
            st.info(f"**Source:** {st.session_state.crawled_url[:40]}...")
        
        if st.button("Reset & Start Over", use_container_width=True):
            st.session_state.knowledge_base = None
            st.session_state.chat_history = []
            st.session_state.crawled_url = None
            st.session_state.pages_crawled = 0
            st.rerun()
    
    # Help Section
    st.markdown("---")
    with st.expander("Quick Tips"):
        st.markdown("""
        **Best Practices:**
        - Start with small sites (< 50 pages)
        - First crawl takes longer (model download)
        - Use specific questions for better answers
        - Check sources for verification
        
        **Example Sites:**
        - `https://example.com` (test)
        - `https://www.python.org` (docs)
        - Any public website
        """)
    
    with st.expander("ℹAbout"):
        st.markdown("""
        **RAG Website Chatbot v1.0**
        
        Built with:
        - Google Gemini AI
        - Semantic Search (FAISS)
        - Sentence Transformers
        - Streamlit
        
        [GitHub](https://github.com) | [Docs](https://github.com)
        """)

# Main Content Area
if st.session_state.knowledge_base is None:
    # Welcome Screen
    st.markdown("## Welcome!")
    st.markdown("Get started by entering your API key and website URL in the sidebar.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Features")
        st.markdown("""
        - Smart web crawling
        - AI-powered answers
        - Source citations
        - Fast & accurate
        """)
    
    with col2:
        st.markdown("### How It Works")
        st.markdown("""
        1. Enter API key
        2. Provide website URL
        3. Crawl & index content
        4. Ask questions
        """)
    
    with col3:
        st.markdown("### Use Cases")
        st.markdown("""
        - Research websites
        - Extract information
        - Analyze content
        - Quick Q&A
        """)
    
    st.markdown("---")
    
    # Example Queries
    st.markdown("### Example Questions You Can Ask")
    st.info("""
    - "What services does this company offer?"
    - "What are the main features of their product?"
    - "How can I contact customer support?"
    - "What is the pricing structure?"
    - "What are the company's values?"
    """)
    
    # Visual Guide
    st.markdown("### Quick Start Guide")
    tab1, tab2, tab3 = st.tabs(["Step 1: API Key", "Step 2: Crawl", "Step 3: Chat"])
    
    with tab1:
        st.markdown("""
        **Get Your Free API Key**
        1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
        2. Sign in with your Google account
        3. Click "Create API Key"
        4. Copy and paste in the sidebar
        
        **Free Tier:** 1,500 requests/day
        """)
    
    with tab2:
        st.markdown("""
        **Crawl a Website**
        1. Enter any website URL
        2. Click "Start Crawling"
        3. Wait 30-60 seconds
        4. Knowledge base will be built
        
        **Fast:** Processes up to 50 pages
        """)
    
    with tab3:
        st.markdown("""
        **Chat with AI**
        1. Type your question
        2. Get AI-powered answer
        3. View source citations
        4. Ask follow-up questions
        
        **Accurate:** Answers from actual content
        """)

else:
    # Chat Interface
    st.markdown("## Chat Interface")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("View Sources"):
                    for idx, source in enumerate(message["sources"], 1):
                        st.markdown(f"{idx}. [{source}]({source})")
    
    # Chat input
    query = st.chat_input("Ask me anything about the website...")
    
    if query:
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": query
        })
        
        with st.chat_message("user"):
            st.markdown(query)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing and generating answer..."):
                try:
                    chatbot = RAGChatbot(
                        st.session_state.knowledge_base,
                        st.session_state.api_key
                    )
                    answer, sources = chatbot.generate_answer(query)
                    
                    st.markdown(answer)
                    
                    if sources:
                        with st.expander("View Sources"):
                            for idx, source in enumerate(sources, 1):
                                st.markdown(f"{idx}. [{source}]({source})")
                    
                    # Save to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg
                    })

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p style='font-size: 0.8rem;'>RAG Chatbot v1.0 | Free & Open Source</p>
    </div>
    """,
    unsafe_allow_html=True
)