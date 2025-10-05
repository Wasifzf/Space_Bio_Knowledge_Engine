"""
Text Preprocessing Module for Knowledge Graph Construction
Handles text chunking, cleaning, and preparation for entity extraction.
"""

import re
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pandas as pd


class TextProcessor:
    """
    Handles text preprocessing for Knowledge Graph construction.
    """
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the text processor.
        
        Args:
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize the text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove or replace special characters that might interfere with processing
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)
        
        # Ensure sentences end properly
        text = re.sub(r'([a-z])([A-Z])', r'\1. \2', text)
        
        return text
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split text into chunks with metadata.
        
        Args:
            text: Text content to chunk
            metadata: Additional metadata to attach to each chunk
            
        Returns:
            List of chunks with metadata
        """
        if metadata is None:
            metadata = {}
        
        # Clean the text first
        cleaned_text = self.clean_text(text)
        
        if not cleaned_text:
            return []
        
        # Split into chunks
        chunks = self.text_splitter.split_text(cleaned_text)
        
        # Add metadata to each chunk
        chunk_list = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                "text": chunk,
                "chunk_id": i,
                "token_count": len(chunk.split()),
                **metadata  # Include original metadata
            }
            chunk_list.append(chunk_data)
        
        return chunk_list
    
    def process_dataframe(self, df: pd.DataFrame, text_column: str = "text") -> List[Dict[str, Any]]:
        """
        Process a pandas DataFrame with text content.
        
        Args:
            df: DataFrame containing text data
            text_column: Name of the column containing text content
            
        Returns:
            List of processed chunks with metadata
        """
        all_chunks = []
        
        for index, row in df.iterrows():
            # Extract text content
            text_content = str(row.get(text_column, ""))
            
            # Create metadata from other columns
            metadata = {
                col: str(row[col]) if pd.notna(row[col]) else ""
                for col in df.columns if col != text_column
            }
            metadata["source_row"] = index
            
            # Process the text
            chunks = self.chunk_text(text_content, metadata)
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def prepare_sample_data(self) -> List[Dict[str, Any]]:
        """
        Create sample space biology text data for demonstration.
        
        Returns:
            List of sample documents with metadata
        """
        sample_data = [
            {
                "paper_id": "spacebio_001",
                "title": "Effects of Microgravity on Bone Density in Mice",
                "url": "https://example.com/paper1",
                "year": "2023",
                "section": "abstract",
                "text": """
                Microgravity environments, such as those experienced during spaceflight, 
                significantly affect bone metabolism in mammals. This study examined the 
                effects of simulated microgravity on bone density in laboratory mice over 
                a 30-day period. Mice exposed to microgravity conditions showed a 15% 
                reduction in bone mineral density compared to ground controls. The 
                reduction was most pronounced in weight-bearing bones such as the femur 
                and tibia. Gene expression analysis revealed upregulation of osteoclast 
                activity markers and downregulation of osteoblast function genes. These 
                findings suggest that microgravity disrupts the normal balance between 
                bone formation and bone resorption, leading to accelerated bone loss.
                """
            },
            {
                "paper_id": "spacebio_002",
                "title": "Plant Growth and Development in Microgravity",
                "url": "https://example.com/paper2", 
                "year": "2023",
                "section": "abstract",
                "text": """
                The growth and development of plants in microgravity conditions present 
                unique challenges and opportunities for space agriculture. Arabidopsis 
                thaliana seedlings were grown aboard the International Space Station 
                for 60 days to investigate gravitropic responses and morphological 
                changes. Plants exhibited altered root growth patterns, with roots 
                showing random directional growth rather than typical downward 
                geotropism. Leaf development was accelerated, but overall plant height 
                was reduced by 20% compared to ground controls. Molecular analysis 
                revealed changes in auxin transport genes and cell wall modification 
                enzymes. Despite these morphological changes, photosynthetic efficiency 
                remained comparable to terrestrial controls.
                """
            },
            {
                "paper_id": "spacebio_003",
                "title": "Immune System Response to Space Radiation",
                "url": "https://example.com/paper3",
                "year": "2024", 
                "section": "abstract",
                "text": """
                Exposure to cosmic radiation during long-duration spaceflight poses 
                significant health risks to astronauts. This study investigated the 
                effects of simulated space radiation on immune system function in 
                human cell cultures. T-lymphocytes exposed to galactic cosmic ray 
                analogs showed decreased proliferation and altered cytokine production. 
                DNA damage markers were elevated in irradiated cells, with evidence 
                of impaired DNA repair mechanisms. The combination of radiation and 
                microgravity stress led to increased apoptosis in immune cells. These 
                findings highlight the need for effective radiation shielding and 
                countermeasures for future deep space missions.
                """
            }
        ]
        
        return sample_data
    
    def extract_entities_from_text(self, text: str) -> List[str]:
        """
        Basic entity extraction using simple patterns.
        This is a simple version - the Groq integration will be more sophisticated.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            List of potential entities
        """
        # Simple patterns for space biology entities
        patterns = [
            r'\b(?:microgravity|spaceflight|space radiation|cosmic ray|weightlessness)\b',
            r'\b(?:mice|mouse|rats|rat|astronauts|humans)\b',
            r'\b(?:bone density|bone loss|muscle atrophy|immune system)\b',
            r'\b(?:Arabidopsis|plants|seedlings|roots|leaves)\b',
            r'\b(?:gene expression|DNA damage|cell culture|apoptosis)\b',
            r'\b(?:osteoclast|osteoblast|T-lymphocytes|cytokines)\b'
        ]
        
        entities = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend([match.lower() for match in matches])
        
        return list(set(entities))  # Remove duplicates


# Example usage and testing
if __name__ == "__main__":
    # Initialize processor
    processor = TextProcessor(chunk_size=300, chunk_overlap=30)
    
    # Test with sample data
    sample_data = processor.prepare_sample_data()
    
    print("=== Text Processing Demo ===\n")
    
    for doc in sample_data:
        print(f"Processing: {doc['title']}")
        print(f"Original text length: {len(doc['text'])} characters")
        
        # Create chunks
        chunks = processor.chunk_text(doc['text'], {
            "paper_id": doc["paper_id"],
            "title": doc["title"],
            "url": doc["url"],
            "year": doc["year"],
            "section": doc["section"]
        })
        
        print(f"Generated {len(chunks)} chunks")
        
        # Show first chunk
        if chunks:
            first_chunk = chunks[0]
            print(f"First chunk ({first_chunk['token_count']} tokens):")
            print(f"  {first_chunk['text'][:150]}...")
            
            # Extract simple entities
            entities = processor.extract_entities_from_text(first_chunk['text'])
            print(f"  Entities found: {entities}")
        
        print("-" * 60)