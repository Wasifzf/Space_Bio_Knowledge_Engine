"""
Enhanced Space Biology Chatbot with Knowledge Graph Integration
===============================================================

This enhanced chatbot combines:
1. Original Pinecone vector search
2. Enhanced Knowledge Graph querying with Groq
3. Intelligent answer synthesis
"""

import os
import json
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
from enhanced_kg_querier import EnhancedKGQuerier
from typing import List, Dict

# Load environment variables
load_dotenv()

class EnhancedSpaceBioChatbot:
    """
    Enhanced chatbot with both vector search and Knowledge Graph capabilities
    """
    
    def __init__(self):
        """Initialize the enhanced chatbot"""
        print("🚀 Initializing Enhanced Space Biology Chatbot...")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        self.index = self.pc.Index(os.getenv('PINECONE_INDEX_NAME', 'spacebio'))
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('BAAI/bge-m3')
        
        # Initialize Groq
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        
        # Initialize Knowledge Graph querier
        self.kg_querier = EnhancedKGQuerier()
        
        # Initialize conversation memory
        self.conversation_history = []
        self.max_history_length = 10  # Keep last 10 exchanges
        
        print("✅ Enhanced chatbot ready!")
    
    def add_to_memory(self, user_query: str, assistant_response: str):
        """Add a conversation exchange to memory"""
        self.conversation_history.append({
            'user': user_query,
            'assistant': assistant_response,
            'timestamp': json.dumps({}).__class__.__name__ # Simple timestamp placeholder
        })
        
        # Keep only the most recent exchanges
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
    
    def get_conversation_context(self) -> str:
        """Get formatted conversation history for context"""
        if not self.conversation_history:
            return ""
        
        context_lines = ["[Previous Conversation Context]"]
        for i, exchange in enumerate(self.conversation_history[-5:], 1):  # Last 5 exchanges
            context_lines.append(f"Exchange {i}:")
            context_lines.append(f"User: {exchange['user'][:200]}...")
            context_lines.append(f"Assistant: {exchange['assistant'][:300]}...")
            context_lines.append("")
        
        return "\n".join(context_lines)
    
    def clear_memory(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_vector_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """Get relevant context from Pinecone vector search"""
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return [match['metadata'] for match in results['matches']]
            
        except Exception as e:
            print(f"⚠️ Vector search error: {e}")
            return []
    
    def get_kg_context(self, query: str) -> Dict:
        """Get relevant context from Knowledge Graph"""
        try:
            return self.kg_querier.enhanced_query(query)
        except Exception as e:
            print(f"⚠️ KG query error: {e}")
            return {'answer': '', 'relevant_triples_count': 0}
    
    def synthesize_answer(self, query: str, vector_context: List[Dict], kg_context: Dict) -> str:
        """Use Groq to synthesize information from both sources with conversation memory"""
        
        # Build conversation context
        conversation_context = self.get_conversation_context()
        
        # Build structured context (vector excerpts + KG answer + minimal provenance)
        parts: List[str] = []
        
        # Add conversation context if available
        if conversation_context:
            parts.append(conversation_context)
            
        if kg_context.get('relevant_triples_count', 0) > 0:
            parts.append("[Knowledge Graph Answer]\n" + kg_context.get('answer', '')[:3000])
            # Optionally include a compact list of top triples
            top_triples = kg_context.get('top_triples') or []
            if top_triples:
                triple_lines = []
                for t in top_triples[:8]:
                    triple_lines.append(f"- {t.get('subject')} --{t.get('predicate')}--> {t.get('object')} ({int(t.get('confidence', 0)*100)}%)")
                parts.append("[Representative Relationships]\n" + "\n".join(triple_lines))
        if vector_context:
            paper_lines = []
            for i, doc in enumerate(vector_context[:5], 1):
                snippet = (doc.get('text') or '')[:300].replace('\n', ' ')
                title = doc.get('title', 'Unknown Title')
                year = doc.get('year', 'Unknown')
                paper_lines.append(f"{i}. {title} ({year}) - {snippet}...")
            parts.append("[Vector Retrieved Excerpts]\n" + "\n".join(paper_lines))
        context = "\n\n".join(parts) if parts else "No additional context retrieved."

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Groq-supported model
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a friendly and knowledgeable AI assistant specialized in space biology research. "
                            "You can handle both casual conversations and in-depth scientific discussions. "
                            "Respond appropriately based on the query type:\n\n"
                            "**For simple greetings or casual queries (like 'hi', 'hello', 'how are you', 'thanks'):**\n"
                            "- Respond warmly and naturally\n"
                            "- Introduce yourself as a space biology research assistant\n"
                            "- Offer to help with specific topics like microgravity effects, space organisms, astronaut health, etc.\n"
                            "- Keep it brief and friendly\n"
                            "- Don't overwhelm with technical details\n\n"
                            "**For scientific research questions:**\n"
                            "Provide comprehensive, detailed responses with clear structure using markdown-style formatting:\n"
                            "1. Start with a clear, bold **summary statement** that captures the essence of the topic\n"
                            "2. Use **bold headers** for main sections (e.g., **Key Mechanisms**, **Research Findings**, **Molecular Details**)\n" 
                            "3. Use bullet points (•) for listing multiple related items with detailed explanations\n"
                            "4. Use numbered lists (1., 2., 3.) for sequential processes or prioritized information\n"
                            "5. Include **bold emphasis** for important terms, concepts, and technical terminology\n"
                            "6. End with a **Conclusion** section that synthesizes the main points and future directions\n\n"
                            "Scientific requirements for detailed responses:\n"
                            "- Provide in-depth explanations of biological mechanisms and pathways\n"
                            "- Include specific experimental details, methodologies, and quantitative findings when available\n"
                            "- Explain the significance and implications of research findings\n"
                            "- Reference previous conversation when relevant for continuity\n"
                            "- Integrate findings across all sources, identifying consensus, contradictions, and key experiments\n"
                            "- Emphasize scientific reasoning, molecular mechanisms, and physiological processes\n"
                            "- Include technical details about experimental conditions, sample sizes, and statistical significance\n"
                            "- Discuss both direct effects and secondary consequences of the phenomena\n"
                            "- Maintain professional but engaging tone with comprehensive coverage\n"
                            "- Highlight knowledge gaps, limitations, and areas needing further research\n"
                            "- Ensure the response flows naturally like a detailed literature review or scientific paper\n"
                            "- Aim for thorough, comprehensive answers that satisfy scientific curiosity\n\n"
                            "DO NOT include citations in the main text - they will be added separately as clickable links."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nCurrent Question: {query}"
                    }
                ],
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️ Answer synthesis failed: {e}")
            
            # Enhanced fallback response with formatting
            fallback = "**Research Summary:**\n\n"
            if kg_context.get('answer'):
                fallback += kg_context['answer'] + "\n\n"
            
            if vector_context:
                fallback += "**Additional Research Context:**\n"
                for i, doc in enumerate(vector_context[:2], 1):
                    fallback += f"{i}. {doc.get('text', '')[:150]}...\n"
                
                # Add sources
                fallback += "\n**📚 Sources:**\n"
                for i, doc in enumerate(vector_context[:2], 1):
                    title = doc.get('title', 'Unknown Title')
                    year = doc.get('year', '')
                    doi = doc.get('doi', '')
                    source_text = f"{i}. **{title}** ({year})"
                    if doi:
                        source_text += f" - [DOI: {doi}](https://doi.org/{doi})"
                    fallback += source_text + "\n"
            
            return fallback
    
    def chat(self, query: str) -> Dict:
        """Enhanced chat function with both vector and KG search plus memory"""
        print(f"🔍 Processing: {query}")
        
        # Get context from both sources
        print("📊 Searching vector database...")
        vector_context = self.get_vector_context(query)
        
        print("🧠 Querying knowledge graph...")
        kg_context = self.get_kg_context(query)
        
        # Synthesize answer (includes conversation memory)
        print("🤖 Generating comprehensive answer...")
        answer = self.synthesize_answer(query, vector_context, kg_context)
        
        # Add clickable source links to the answer
        if vector_context:
            answer += "\n\n**📚 Research Sources:**\n"
            for i, doc in enumerate(vector_context, 1):
                title = doc.get('title', 'Unknown Title')
                year = doc.get('year', '')
                authors = doc.get('authors', '')
                doi = doc.get('doi', '')
                url = doc.get('url', '')
                
                # Create source entry with clickable link
                source_text = f"{i}. **{title}**"
                if authors:
                    # Truncate long author lists
                    author_list = authors[:100] + "..." if len(authors) > 100 else authors
                    source_text += f" - {author_list}"
                if year:
                    source_text += f" ({year})"
                
                # Add clickable link (DOI preferred, then URL)
                if doi and doi.strip():
                    source_text += f" - [📖 Read Paper](https://doi.org/{doi.strip()})"
                elif url and url.strip():
                    source_text += f" - [📖 Read Paper]({url.strip()})"
                
                answer += source_text + "\n"
        
        # Add this exchange to conversation memory
        self.add_to_memory(query, answer)
        
        return {
            'query': query,
            'answer': answer,
            'vector_results': len(vector_context),
            'kg_relationships': kg_context.get('relevant_triples_count', 0),
            'conversation_length': len(self.conversation_history),
            'sources': {
                'vector_context': vector_context,
                'kg_context': kg_context
            }
        }

def main():
    """Demo the enhanced chatbot"""
    print("🚀 Enhanced Space Biology Chatbot Demo")
    print("=" * 50)
    
    try:
        chatbot = EnhancedSpaceBioChatbot()
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        return
    
    # Demo queries
    demo_queries = [
        "How does microgravity affect plant growth?",
        "What are the effects of spaceflight on bone density?",
        "Tell me about bacterial behavior on the International Space Station"
    ]
    
    for query in demo_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 50)
        
        result = chatbot.chat(query)
        
        print(f"💡 Enhanced Answer:\n{result['answer']}")
        print(f"\n📊 Sources: {result['vector_results']} papers, {result['kg_relationships']} KG relationships")
        print("=" * 50)

if __name__ == "__main__":
    main()