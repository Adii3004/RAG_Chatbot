# RAG-Based Website Chatbot

**An intelligent chatbot that answers questions about any website using RAG (Retrieval-Augmented Generation)**

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)

---

## Overview

RAG Website Chatbot is a production-ready application that:
- Crawls any website and extracts content
- Builds a searchable knowledge base using AI embeddings
- Answers questions using Google Gemini LLM with source citations
- Provides a modern, user-friendly interface
- **Completely FREE** to use (no credit card needed)

### What is RAG?

**Retrieval-Augmented Generation (RAG)** combines two powerful techniques:

1. **Retrieval** - Finding relevant information from a knowledge base using semantic search
2. **Generation** - Using a Large Language Model (LLM) to create natural, contextual answers

This approach ensures answers are:
- Grounded in actual content (not hallucinated)
- Accurate and verifiable
- Cited with sources

---

## Features

### Core Capabilities

- **Smart Web Crawling**
  - BFS (Breadth-First Search) algorithm
  - 2-level depth traversal
  - URL deduplication
  - Extracts title, headings, and main text
  - Skips non-content elements (nav, footer, ads)

- **Semantic Search**
  - AI-powered embeddings (384 dimensions)
  - FAISS vector database for fast similarity search
  - Top-K retrieval for relevant context

- **Natural Language Q&A**
  - Powered by Google Gemini 2.5 Flash (FREE tier)
  - Context-aware responses
  - Handles follow-up questions
  - Detailed, informative answers

- **Source Citations**
  - Every answer includes reference URLs
  - Transparent and verifiable
  - Clickable source links

- **Performance Optimized**
  - Model caching for faster subsequent runs
  - Batch embedding generation
  - Efficient chunking strategy
  - Sub-5-second query responses

- **Modern UI**
  - Beautiful gradient styling
  - Responsive design
  - Real-time progress tracking
  - Intuitive chat interface
  - Help tooltips and guides

### Technical Features

- **Modular Architecture** - Separate files for crawler, KB, and RAG logic
- **Session Management** - Preserves chat history and state
- **Error Handling** - Graceful handling of failed pages, timeouts, API errors
- **Configuration** - Easy customization via `config.py`
- **Progress Tracking** - Real-time status updates during processing
- **Caching** - Loads embedding model only once

---

## Architecture

### System Architecture Diagram
```
┌────────────────────────────────────────────────────────┐
│                    USER INPUT (URL)                    │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│                  WEB CRAWLER MODULE                    │
│  ┌───────────────────────────────────────────────────┐ │
│  │  • BFS Traversal (Max Depth: 2 levels)            │ │
│  │  • HTML Parsing (BeautifulSoup4)                  │ │
│  │  • Content Extraction (Title, Headings, Text)     │ │
│  │  • URL Validation & Deduplication                 │ │
│  │  • Error Handling (Timeouts, 404s, etc.)          │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼ Pages Data
┌────────────────────────────────────────────────────────┐
│               KNOWLEDGE BASE MODULE                    │
│  ┌───────────────────────────────────────────────────┐ │
│  │  STEP 1: Text Chunking                            │ │
│  │    • Chunk Size: 600 words                        │ │
│  │    • Overlap: 100 words                           │ │
│  │    • Strategy: Sliding Window                     │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │  STEP 2: Embedding Generation                     │ │
│  │    • Model: all-MiniLM-L6-v2                      │ │
│  │    • Dimensions: 384                              │ │
│  │    • Batch Size: 32 chunks at a time              │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │  STEP 3: Vector Indexing                          │ │
│  │    • Library: FAISS (Facebook AI)                 │ │
│  │    • Index Type: IndexFlatL2                      │ │
│  │    • Distance Metric: L2 (Euclidean)              │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼ Vector Index (In-Memory)
┌────────────────────────────────────────────────────────┐
│                    USER QUESTION                       │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│                   RAG PIPELINE                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  STEP 1: Query Embedding                          │ │
│  │    • Convert user question to 384-dim vector      │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │  STEP 2: Semantic Search                          │ │
│  │    • Search FAISS index                           │ │
│  │    • Retrieve Top-5 similar chunks                │ │
│  │    • Rank by similarity score                     │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │  STEP 3: Context Assembly                         │ │
│  │    • Combine retrieved chunks                     │ │
│  │    • Add metadata (titles, URLs)                  │ │
│  │    • Build coherent context                       │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │  STEP 4: Prompt Construction                      │ │
│  │    • Context + User Query → LLM Prompt            │ │
│  │    • Add instructions (answer from context only)  │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │  STEP 5: LLM Generation                           │ │
│  │    • Model: Google Gemini 2.5 Flash               │ │
│  │    • Temperature: 0.7                             │ │
│  │    • Max Tokens: 2048                             │ │
│  │    • Generate detailed answer                     │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│              RESPONSE + SOURCE CITATIONS               │
│  • AI-generated answer (comprehensive)                 │
│  • Source URLs (clickable links)                       │
│  • Confidence indicators                               │
└────────────────────────────────────────────────────────┘
```

### Data Flow Explanation

1. **Input Phase**
   - User provides website URL in the sidebar
   - URL is validated (must start with http:// or https://)

2. **Crawling Phase**
   - BFS algorithm starts from base URL
   - Extracts content from each page (title, headings, text)
   - Follows links to discover new pages (up to 2 levels)
   - Maximum 50 pages to prevent overload
   - 0.3 second delay between requests (respectful crawling)

3. **Knowledge Base Building**
   - Text is split into 600-word chunks with 100-word overlap
   - Each chunk is converted to a 384-dimensional vector
   - Vectors are stored in FAISS index for fast search
   - Metadata (URL, title) is preserved for each chunk

4. **Query Phase**
   - User types a question in the chat interface
   - Question is converted to a 384-dimensional vector
   - FAISS finds the 5 most similar chunks (semantic search)
   - Chunks are assembled into context

5. **Generation Phase**
   - Context + question sent to Gemini API
   - LLM generates a detailed, contextual answer
   - Only uses information from the provided context
   - Returns answer with source URLs

---

## Installation

### Prerequisites

Before you begin, ensure you have:
- **Python 3.9 or higher** installed ([Download here](https://www.python.org/downloads/))
- **pip** package manager (comes with Python)
- **Google Gemini API key** (free, no credit card needed)

### Step 1: Get API Key

1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API Key" button
4. Copy the key (starts with `AIzaSy...`)
5. Save it somewhere safe

**Free Tier Limits:**
- 1,500 requests per day
- 15 requests per minute
- 1 million token context window
- No credit card required

### Step 2: Clone Repository
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/rag-chatbot.git

# Navigate to project directory
cd rag-chatbot
```

### Step 3: Create Virtual Environment

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your terminal
```

**Mac/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your terminal
```

### Step 4: Install Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# This will install:
# - streamlit (web framework)
# - google-generativeai (Gemini API)
# - sentence-transformers (embeddings)
# - faiss-cpu (vector search)
# - beautifulsoup4 (HTML parsing)
# - requests (HTTP client)
```

**Installation takes 2-3 minutes**

### Step 5: Run the Application
```bash
# Start the Streamlit app
streamlit run app.py

# App will automatically open in your browser
# If not, navigate to: http://localhost:8501
```

---

## Usage

### Quick Start Guide

#### Step 1: Launch the Application

#### Step 2: Configure API Key

#### Step 3: Enter Website URL

#### Step 4: Start Crawling

#### Step 5: Ask Questions

#### Step 6: Continue Chatting

## Configuration

### Project Structure
```
rag-chatbot/
│
├── app.py                  # Main Streamlit application (UI)
├── crawler.py              # Web crawling logic (BFS algorithm)
├── knowledge_base.py       # Embeddings and vector search
├── rag_chatbot.py          # RAG pipeline implementation
├── config.py               # Configuration settings
├── utils.py                # Helper functions
│
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── DEPLOYMENT_GUIDE.md    # Deployment instructions
├── .gitignore             # Git ignore rules
└── LICENSE                # MIT License
```

### Configuration File (config.py)
```python
# Crawler Settings
MAX_CRAWL_DEPTH = 2        # How deep to crawl (1-3 recommended)
MAX_PAGES = 50             # Maximum pages to crawl
CRAWL_TIMEOUT = 8          # Request timeout in seconds
CRAWL_DELAY = 0.3          # Delay between requests

# Chunking Settings
CHUNK_SIZE = 600           # Words per chunk
CHUNK_OVERLAP = 100        # Overlapping words between chunks
MIN_CHUNK_SIZE = 100       # Minimum chunk size to keep

# Embedding Settings
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'  # Sentence transformer model
EMBEDDING_BATCH_SIZE = 32              # Batch size for encoding

# RAG Settings
TOP_K_RESULTS = 5          # Number of chunks to retrieve
GEMINI_MODEL = 'gemini-2.5-flash'  # Gemini model to use
MAX_OUTPUT_TOKENS = 2048   # Max tokens in response
TEMPERATURE = 0.7          # Creativity (0-1)
```

### Customization Options

#### For Faster Processing
```python
# Edit config.py
MAX_PAGES = 20             # Fewer pages
CHUNK_SIZE = 400           # Smaller chunks
TOP_K_RESULTS = 3          # Fewer retrievals
```

**Effect:**
- Crawl time: 15-30 seconds (vs 30-60)
- Memory usage: ~400MB (vs ~800MB)
- Query time: ~2-3 seconds (vs 3-5)

#### For Better Accuracy
```python
# Edit config.py
CHUNK_SIZE = 800           # Larger chunks (more context)
CHUNK_OVERLAP = 150        # More overlap (better continuity)
TOP_K_RESULTS = 7          # More context for LLM
```

**Effect:**
- More comprehensive answers
- Better context preservation
- Slightly slower (5-6 seconds per query)

#### For Deeper Crawling
```python
# Edit config.py
MAX_CRAWL_DEPTH = 3        # Go 3 levels deep
MAX_PAGES = 100            # Process more pages
```

**Effect:**
- More comprehensive knowledge base
- Longer crawl time (90-120 seconds)
- More memory usage (~1.5GB)

---
