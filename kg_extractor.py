"""
Knowledge Graph Extraction Module
Uses Groq LLM for entity and relation extraction from text chunks.
"""

import os
import re
import json
from typing import List, Dict, Tuple, Any, Optional
from dotenv import load_dotenv
from groq import Groq
from text_processor import TextProcessor

# Load environment variables
load_dotenv()


class KGExtractor:
    """
    Extracts entities and relations from text using Groq LLM for Knowledge Graph construction.
    """
    
    def __init__(self, groq_api_key: str = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize the KG extractor.
        
        Args:
            groq_api_key: Groq API key (defaults to environment variable)
            model: Groq model to use for extraction
        """
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required")
        
        self.client = Groq(api_key=self.groq_api_key)
        self.text_processor = TextProcessor()
    
    def extract_triples_from_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Extract entity-relation-entity triples from text using Groq.
        
        Args:
            text: Text content to extract triples from
            metadata: Additional metadata about the text
            
        Returns:
            List of extracted triples with metadata
        """
        system_prompt = """You are an expert in space biology, biomedical research, and knowledge extraction. 

Your task is to extract structured knowledge triples from scientific text in the format:
(Subject, Predicate, Object)

INSTRUCTIONS:
1. Extract only factual relationships explicitly stated in the text
2. Use clear, standardized terms for entities (e.g., "Microgravity" not "micro-gravity")
3. Use informative predicates that capture the relationship (e.g., "affects", "causes", "reduces", "increases")
4. Focus on key entities: organisms, biological processes, environmental conditions, molecular components
5. Return ONLY the triples in JSON format as shown below
6. Extract 3-8 triples per text chunk

OUTPUT FORMAT:
{
  "triples": [
    {
      "subject": "Entity1",
      "predicate": "relationship",
      "object": "Entity2",
      "confidence": 0.9
    }
  ]
}

EXAMPLE:
{
  "triples": [
    {
      "subject": "Microgravity",
      "predicate": "affects",
      "object": "Bone Density",
      "confidence": 0.95
    },
    {
      "subject": "Mice",
      "predicate": "exposed_to",
      "object": "Microgravity",
      "confidence": 0.9
    }
  ]
}"""

        user_prompt = f"""Extract knowledge triples from this space biology text:

TEXT:
{text}

Provide the output in the exact JSON format specified."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                # Remove markdown code blocks if present
                if content.startswith("```"):
                    content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                
                parsed_response = json.loads(content)
                triples = parsed_response.get("triples", [])
                
                # Add metadata to each triple
                enriched_triples = []
                for triple in triples:
                    enriched_triple = {
                        **triple,
                        "source_text": text[:200] + "..." if len(text) > 200 else text,
                        **(metadata or {})
                    }
                    enriched_triples.append(enriched_triple)
                
                return enriched_triples
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
                print(f"Raw response: {content}")
                return self._fallback_extraction(text, metadata)
                
        except Exception as e:
            print(f"Error in Groq API call: {e}")
            return self._fallback_extraction(text, metadata)
    
    def _fallback_extraction(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Fallback extraction using simple patterns when Groq fails.
        
        Args:
            text: Text to extract from
            metadata: Metadata to include
            
        Returns:
            List of simple extracted triples
        """
        # Simple pattern-based extraction
        triples = []
        
        # Common space biology patterns
        if "microgravity" in text.lower():
            if "bone" in text.lower():
                triples.append({
                    "subject": "Microgravity",
                    "predicate": "affects",
                    "object": "Bone Density",
                    "confidence": 0.7,
                    "extraction_method": "fallback"
                })
            if "plant" in text.lower() or "arabidopsis" in text.lower():
                triples.append({
                    "subject": "Plants",
                    "predicate": "grown_in",
                    "object": "Microgravity",
                    "confidence": 0.7,
                    "extraction_method": "fallback"
                })
        
        # Add metadata
        for triple in triples:
            triple.update({
                "source_text": text[:200] + "..." if len(text) > 200 else text,
                **(metadata or {})
            })
        
        return triples
    
    def process_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple documents to extract triples.
        
        Args:
            documents: List of documents with text and metadata
            
        Returns:
            List of all extracted triples
        """
        all_triples = []
        
        for doc in documents:
            print(f"Processing document: {doc.get('title', 'Unknown')[:50]}...")
            
            # Create chunks from the document
            chunks = self.text_processor.chunk_text(
                doc.get('text', ''),
                {k: v for k, v in doc.items() if k != 'text'}
            )
            
            # Extract triples from each chunk
            for chunk in chunks:
                chunk_text = chunk['text']
                chunk_metadata = {k: v for k, v in chunk.items() if k != 'text'}
                
                triples = self.extract_triples_from_text(chunk_text, chunk_metadata)
                all_triples.extend(triples)
                
                print(f"  Extracted {len(triples)} triples from chunk {chunk['chunk_id']}")
        
        return all_triples
    
    def filter_and_deduplicate_triples(self, triples: List[Dict[str, Any]], 
                                     min_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """
        Filter and deduplicate extracted triples.
        
        Args:
            triples: List of extracted triples
            min_confidence: Minimum confidence threshold
            
        Returns:
            Filtered and deduplicated triples
        """
        # Filter by confidence
        filtered_triples = [
            t for t in triples 
            if t.get('confidence', 0) >= min_confidence
        ]
        
        # Deduplicate based on subject-predicate-object
        seen_triples = set()
        deduplicated = []
        
        for triple in filtered_triples:
            key = (
                triple['subject'].lower().strip(),
                triple['predicate'].lower().strip(),
                triple['object'].lower().strip()
            )
            
            if key not in seen_triples:
                seen_triples.add(key)
                deduplicated.append(triple)
        
        return deduplicated
    
    def extract_from_pinecone_matches(self, matches: List[Dict], query: str) -> List[Dict[str, Any]]:
        """
        Extract triples from Pinecone search results.
        
        Args:
            matches: Pinecone search results
            query: Original search query for context
            
        Returns:
            List of extracted triples
        """
        all_triples = []
        
        for match in matches:
            metadata = match.get('metadata', {})
            text = metadata.get('text', '')
            
            if text:
                # Add query context to metadata
                enriched_metadata = {
                    **metadata,
                    'search_query': query,
                    'match_score': match.get('score', 0)
                }
                
                triples = self.extract_triples_from_text(text, enriched_metadata)
                all_triples.extend(triples)
        
        return self.filter_and_deduplicate_triples(all_triples)


# Demo and testing
if __name__ == "__main__":
    # Initialize extractor
    try:
        extractor = KGExtractor()
        
        # Get sample data
        processor = TextProcessor()
        sample_docs = processor.prepare_sample_data()
        
        print("=== Knowledge Graph Extraction Demo ===\n")
        
        # Extract from first document
        doc = sample_docs[0]
        print(f"Extracting from: {doc['title']}")
        print(f"Text: {doc['text'][:200]}...\n")
        
        # Extract triples
        triples = extractor.extract_triples_from_text(doc['text'], {
            'paper_id': doc['paper_id'],
            'title': doc['title']
        })
        
        print(f"Extracted {len(triples)} triples:\n")
        for i, triple in enumerate(triples, 1):
            print(f"{i}. ({triple['subject']}) --[{triple['predicate']}]--> ({triple['object']})")
            print(f"   Confidence: {triple.get('confidence', 'N/A')}")
            print()
        
    except Exception as e:
        print(f"Demo failed: {e}")
        print("Make sure GROQ_API_KEY environment variable is set")