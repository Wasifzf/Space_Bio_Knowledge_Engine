"""
Enhanced Knowledge Graph Query System with Groq Integration
===========================================================

This enhanced version uses Groq LLM to:
1. Better understand user queries and extract entities
2. Filter and rank relevant results
3. Generate more natural, contextual answers
"""

import json
import networkx as nx
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict
import re
from difflib import SequenceMatcher
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EnhancedKGQuerier:
    """
    Enhanced Knowledge Graph Querier with Groq LLM integration
    """
    
    def __init__(self, triples_file: str = "pinecone_extracted_triples.json"):
        """Initialize with triples data and Groq client"""
        self.triples_file = triples_file
        self.graph = nx.DiGraph()
        self.triples_data = None
        self.entity_aliases = {}
        
        # Initialize Groq client
        try:
            self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            self.groq_available = True
            print("✅ Groq LLM integration enabled")
        except Exception as e:
            print(f"⚠️ Groq not available: {e}")
            self.groq_available = False
        
        # Load and build graph
        self.load_triples()
        self.build_query_graph()
        self.build_entity_aliases()
    
    def load_triples(self):
        """Load triples from JSON file"""
        try:
            with open(self.triples_file, 'r') as f:
                self.triples_data = json.load(f)
            print(f"✅ Loaded {len(self.triples_data['triples'])} triples for enhanced querying")
        except FileNotFoundError:
            print(f"❌ File {self.triples_file} not found!")
            return
        except Exception as e:
            print(f"❌ Error loading triples: {e}")
            return
    
    def build_query_graph(self):
        """Build NetworkX graph optimized for querying"""
        if not self.triples_data:
            return
        
        for triple in self.triples_data['triples']:
            subject = triple['subject']
            predicate = triple['predicate']
            obj = triple['object']
            
            # Add edge with full metadata for querying
            self.graph.add_edge(subject, obj, 
                              predicate=predicate,
                              confidence=triple['confidence'],
                              paper_id=triple['paper_id'],
                              title=triple['title'],
                              url=triple['url'],
                              source_text=triple['source_text'])
    
    def build_entity_aliases(self):
        """Build aliases for entities to handle variations in naming"""
        for node in self.graph.nodes():
            aliases = set()
            aliases.add(node.lower())
            
            # Add variations
            clean_name = re.sub(r'(^the |^a |^an | response$| activity$| level$)', '', node.lower())
            if clean_name != node.lower():
                aliases.add(clean_name)
            
            aliases.add(re.sub(r'[-\s_]', '', node.lower()))
            aliases.add(node.lower().replace(' ', '-'))
            aliases.add(node.lower().replace('-', ' '))
            
            self.entity_aliases[node] = aliases
    
    def groq_extract_entities_and_intent(self, query: str) -> Dict:
        """Use Groq to extract entities and understand query intent"""
        if not self.groq_available:
            return self.fallback_entity_extraction(query)
        
        # Get all available entities from our graph
        available_entities = list(self.graph.nodes())
        
        prompt = f"""
You are an expert at analyzing scientific queries about space biology research.

Available entities in our knowledge graph include (sample): {', '.join(available_entities[:50])}...

User Query: "{query}"

Please analyze this query and extract:
1. Main entities mentioned (find the closest matches from available entities)
2. Query type (what_affects, what_does_affect, connection, summary, or general)
3. Specific focus area (e.g., "plants", "bone", "immune system", "bacteria")

Respond in JSON format:
{{
    "entities": ["entity1", "entity2"],
    "query_type": "what_does_affect",
    "focus_area": "plants",
    "intent_description": "User wants to know how microgravity affects plants specifically"
}}
"""
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
        except Exception as e:
            print(f"⚠️ Groq extraction failed: {e}")
        
        return self.fallback_entity_extraction(query)
    
    def fallback_entity_extraction(self, query: str) -> Dict:
        """Fallback entity extraction without Groq"""
        query_lower = query.lower()
        
        # Simple pattern matching
        entities = []
        focus_area = None
        
        # Look for known entities
        for entity in self.graph.nodes():
            if entity.lower() in query_lower:
                entities.append(entity)
        
        # Determine query type
        if any(phrase in query_lower for phrase in ['what affects', 'what influences']):
            query_type = 'what_affects'
        elif any(phrase in query_lower for phrase in ['what does', 'how does']):
            query_type = 'what_does_affect'
        elif 'tell me about' in query_lower or 'summary' in query_lower:
            query_type = 'summary'
        else:
            query_type = 'general'
        
        # Look for focus areas
        focus_keywords = {
            'plants': ['plant', 'plants', 'arabidopsis', 'flora'],
            'bone': ['bone', 'bones', 'skeleton', 'skeletal'],
            'immune': ['immune', 'immunity', 'immunological'],
            'muscle': ['muscle', 'muscles', 'muscular'],
            'bacteria': ['bacteria', 'bacterial', 'microbial']
        }
        
        for area, keywords in focus_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                focus_area = area
                break
        
        return {
            'entities': entities,
            'query_type': query_type,
            'focus_area': focus_area,
            'intent_description': f"User query about {focus_area or 'general topic'}"
        }
    
    def find_relevant_triples(self, entities: List[str], focus_area: str = None) -> List[Dict]:
        """Find triples relevant to the entities and focus area"""
        relevant_triples = []
        
        for triple in self.triples_data['triples']:
            subject = triple['subject'].lower()
            obj = triple['object'].lower()
            predicate = triple['predicate'].lower()
            
            # Check if any entity is involved
            entity_match = False
            for entity in entities:
                if entity.lower() in subject or entity.lower() in obj:
                    entity_match = True
                    break
            
            # Check focus area relevance
            focus_match = True
            if focus_area:
                focus_keywords = {
                    'plants': ['plant', 'arabidopsis', 'root', 'leaf', 'seed', 'growth'],
                    'bone': ['bone', 'skeleton', 'skeletal', 'osteo', 'calcium'],
                    'immune': ['immune', 'immunity', 'antibody', 'lymph', 'cytokine'],
                    'muscle': ['muscle', 'muscular', 'fiber', 'contraction', 'atrophy'],
                    'bacteria': ['bacteria', 'bacterial', 'microbial', 'pathogen']
                }
                
                keywords = focus_keywords.get(focus_area, [])
                if keywords:
                    focus_match = any(keyword in subject or keyword in obj or keyword in predicate 
                                    for keyword in keywords)
            
            if entity_match and focus_match:
                relevant_triples.append(triple)
        
        # Sort by confidence
        relevant_triples.sort(key=lambda x: x['confidence'], reverse=True)
        return relevant_triples
    
    def groq_generate_answer(self, query: str, intent: Dict, relevant_triples: List[Dict]) -> str:
        """Use Groq to generate a natural answer from the relevant triples"""
        if not self.groq_available or not relevant_triples:
            return self.fallback_answer_generation(query, relevant_triples)
        
        # Prepare context from triples
        context_triples = []
        for triple in relevant_triples[:10]:  # Limit to top 10
            context_triples.append({
                'relationship': f"{triple['subject']} {triple['predicate']} {triple['object']}",
                'confidence': triple['confidence'],
                'source': triple['title'][:50] + "..."
            })
        
        prompt = f"""
You are a space biology research expert. A user asked: "{query}"

Based on the following knowledge relationships extracted from research papers, provide a comprehensive and natural answer:

Knowledge Relationships:
{json.dumps(context_triples, indent=2)}

Query Intent: {intent.get('intent_description', 'General inquiry')}
Focus Area: {intent.get('focus_area', 'General')}

Please provide a natural, informative answer that:
1. Directly addresses the user's question
2. Uses the provided relationships as evidence
3. Is written in a conversational, accessible tone
4. Mentions specific research findings when relevant
5. If the focus area is specific (like plants), make sure to address that specifically

If the available data doesn't directly answer the question, acknowledge this and provide the best available related information.
"""
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️ Groq answer generation failed: {e}")
            return self.fallback_answer_generation(query, relevant_triples)
    
    def fallback_answer_generation(self, query: str, relevant_triples: List[Dict]) -> str:
        """Fallback answer generation without Groq"""
        if not relevant_triples:
            return "I couldn't find specific information to answer your question in the current knowledge base."
        
        answer = f"Based on the research data, here are the relevant findings:\n\n"
        
        for i, triple in enumerate(relevant_triples[:5], 1):
            answer += f"{i}. {triple['subject']} {triple['predicate']} {triple['object']}\n"
            answer += f"   (Confidence: {triple['confidence']}, Source: {triple['title'][:50]}...)\n\n"
        
        if len(relevant_triples) > 5:
            answer += f"... and {len(relevant_triples) - 5} more related findings."
        
        return answer
    
    def enhanced_query(self, query: str) -> Dict:
        """Enhanced query processing with Groq integration"""
        print(f"🔄 Processing query with Groq assistance...")
        
        # Step 1: Extract entities and intent using Groq
        intent = self.groq_extract_entities_and_intent(query)
        print(f"🎯 Intent: {intent.get('intent_description', 'General query')}")
        if intent.get('focus_area'):
            print(f"🔬 Focus area: {intent['focus_area']}")
        
        # Step 2: Find relevant triples
        relevant_triples = self.find_relevant_triples(
            intent.get('entities', []), 
            intent.get('focus_area')
        )
        
        print(f"📊 Found {len(relevant_triples)} relevant relationships")
        
        # Step 3: Generate enhanced answer using Groq
        answer = self.groq_generate_answer(query, intent, relevant_triples)
        
        return {
            'query': query,
            'intent': intent,
            'relevant_triples_count': len(relevant_triples),
            'answer': answer,
            'top_triples': relevant_triples[:5]  # Include top results for reference
        }

def main():
    """Demo the enhanced querier"""
    print("🚀 Enhanced Knowledge Graph Querier with Groq")
    print("=" * 60)
    
    querier = EnhancedKGQuerier()
    
    if not querier.triples_data:
        print("❌ No data available!")
        return
    
    # Test queries
    test_queries = [
        "How does microgravity affect plants?",
        "What affects bone density in space?",
        "Tell me about bacterial behavior on the International Space Station",
        "How does radiation impact immune function?"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 40)
        
        result = querier.enhanced_query(query)
        print(f"💡 Enhanced Answer:\n{result['answer']}")
        print("=" * 60)

if __name__ == "__main__":
    main()