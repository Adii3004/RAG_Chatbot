"""
RAG chatbot module for answer generation
"""

import google.generativeai as genai
import config

class RAGChatbot:
    """RAG-based chatbot using Google Gemini"""
    
    def __init__(self, knowledge_base, api_key):
        self.kb = knowledge_base
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            config.GEMINI_MODEL,
            generation_config={
                'temperature': config.TEMPERATURE,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': config.MAX_OUTPUT_TOKENS,
            }
        )
    
    def generate_answer(self, query):
        """Generate answer using RAG pipeline"""
        try:
            # Retrieve relevant chunks
            results = self.kb.search(query, top_k=config.TOP_K_RESULTS)
            
            if not results:
                return "I couldn't find relevant information to answer your question. Try asking something else about the website.", []
            
            # Build context from retrieved chunks
            context_parts = [r['chunk'] for r in results]
            context = "\n\n".join(context_parts)
            
            # Create prompt
            prompt = self._build_prompt(context, query)
            
            # Generate response
            response = self.model.generate_content(prompt)
            answer = response.text
            
            # Extract unique source URLs
            sources = list(set([r['metadata']['url'] for r in results]))
            
            return answer, sources
            
        except Exception as e:
            return f"Error generating response: {str(e)}", []
    
    def _build_prompt(self, context, query):
        """Build optimized prompt for Gemini"""
        return f"""You are a helpful AI assistant that answers questions based on website content.

Website Content:
{context}

User Question: {query}

Instructions:
- Provide a comprehensive and detailed answer based on the website content above
- Include specific details, features, benefits, and relevant information
- Structure your response clearly with proper explanations
- Cover all relevant aspects mentioned in the content
- Be informative and thorough
- Only use information from the provided content
- If information is not available in the content, state that clearly

Detailed Answer:"""