"""
Knowledge base module for embeddings and semantic search
"""

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import streamlit as st
import config

class KnowledgeBase:
    """Manages document embeddings and semantic search"""
    
    def __init__(self):
        self.chunks = []
        self.metadata = []
        self.index = None
        self.model = None
        
    @staticmethod
    @st.cache_resource
    def load_model():
        """Load sentence transformer model (cached)"""
        return SentenceTransformer(config.EMBEDDING_MODEL)
    
    def chunk_text(self, text, chunk_size=None, overlap=None):
        """Split text into overlapping chunks"""
        chunk_size = chunk_size or config.CHUNK_SIZE
        overlap = overlap or config.CHUNK_OVERLAP
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk) > config.MIN_CHUNK_SIZE:
                chunks.append(chunk)
        
        return chunks
    
    def build(self, pages_content, progress_callback=None):
        """Build knowledge base from crawled pages"""
        try:
            if progress_callback:
                progress_callback("🧠 Loading embedding model...")
            
            self.model = self.load_model()
            
            all_chunks = []
            all_metadata = []
            
            if progress_callback:
                progress_callback(f"✂️ Chunking {len(pages_content)} pages...")
            
            # Process each page
            for idx, page in enumerate(pages_content):
                page_text = f"Title: {page['title']}\n"
                if page['headings']:
                    page_text += f"Topics: {', '.join(page['headings'][:5])}\n"
                page_text += page['content']
                
                chunks = self.chunk_text(page_text)
                
                for chunk in chunks:
                    all_chunks.append(chunk)
                    all_metadata.append({
                        'url': page['url'],
                        'title': page['title']
                    })
                
                if progress_callback and (idx + 1) % 5 == 0:
                    progress_callback(f"✂️ Processed {idx + 1}/{len(pages_content)} pages...")
            
            if not all_chunks:
                return False
            
            if progress_callback:
                progress_callback(f"🔢 Generating embeddings for {len(all_chunks)} chunks...")
            
            # Generate embeddings in batches
            all_embeddings = []
            batch_size = config.EMBEDDING_BATCH_SIZE
            
            for i in range(0, len(all_chunks), batch_size):
                batch = all_chunks[i:i + batch_size]
                embeddings = self.model.encode(batch, show_progress_bar=False)
                all_embeddings.append(embeddings)
                
                if progress_callback and (i // batch_size + 1) % 5 == 0:
                    progress_callback(f"🔢 Embedded {min(i + batch_size, len(all_chunks))}/{len(all_chunks)} chunks...")
            
            all_embeddings = np.vstack(all_embeddings)
            
            if progress_callback:
                progress_callback("🗂️ Building FAISS index...")
            
            # Build FAISS index
            dimension = all_embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(all_embeddings.astype('float32'))
            
            self.chunks = all_chunks
            self.metadata = all_metadata
            
            if progress_callback:
                progress_callback(f"✅ Knowledge base ready with {len(all_chunks)} chunks!")
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Error: {str(e)}")
            return False
    
    def search(self, query, top_k=None):
        """Search for relevant chunks using semantic similarity"""
        top_k = top_k or config.TOP_K_RESULTS
        
        if self.model is None or self.index is None:
            return []
        
        try:
            query_embedding = self.model.encode([query])
            distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            results = []
            for idx, dist in zip(indices[0], distances[0]):
                if idx < len(self.chunks):
                    results.append({
                        'chunk': self.chunks[idx],
                        'metadata': self.metadata[idx],
                        'score': float(dist)
                    })
            
            return results
        except:
            return []