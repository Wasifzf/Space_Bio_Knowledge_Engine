"""
Knowledge Graph Infrastructure
Supports both Neo4j (production) and NetworkX (development/prototyping) backends.
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import networkx as nx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("Warning: Neo4j driver not available. Using NetworkX backend only.")


class KnowledgeGraphBase(ABC):
    """
    Abstract base class for Knowledge Graph implementations.
    """
    
    @abstractmethod
    def add_triple(self, subject: str, predicate: str, obj: str, metadata: Dict[str, Any] = None):
        """Add a triple to the knowledge graph."""
        pass
    
    @abstractmethod
    def query_entity(self, entity: str) -> List[Dict[str, Any]]:
        """Query all relationships for an entity."""
        pass
    
    @abstractmethod
    def query_relation(self, subject: str, predicate: str) -> List[str]:
        """Query objects for a specific subject-predicate pair."""
        pass
    
    @abstractmethod
    def get_graph_stats(self) -> Dict[str, int]:
        """Get basic statistics about the graph."""
        pass


class NetworkXKnowledgeGraph(KnowledgeGraphBase):
    """
    Knowledge Graph implementation using NetworkX for development and prototyping.
    """
    
    def __init__(self):
        """Initialize the NetworkX-based knowledge graph."""
        self.graph = nx.MultiDiGraph()  # Allow multiple edges between nodes
        self.metadata_store = {}  # Store metadata for edges
    
    def add_triple(self, subject: str, predicate: str, obj: str, metadata: Dict[str, Any] = None):
        """
        Add a triple to the knowledge graph.
        
        Args:
            subject: Subject entity
            predicate: Relationship/predicate
            obj: Object entity
            metadata: Additional metadata for the relationship
        """
        # Normalize entity names
        subject = subject.strip().title()
        obj = obj.strip().title()
        predicate = predicate.strip().lower().replace(" ", "_")
        
        # Add nodes if they don't exist
        if not self.graph.has_node(subject):
            self.graph.add_node(subject, entity_type="entity")
        if not self.graph.has_node(obj):
            self.graph.add_node(obj, entity_type="entity")
        
        # Add edge with predicate as edge attribute
        edge_id = self.graph.add_edge(subject, obj, predicate=predicate)
        
        # Store metadata if provided
        if metadata:
            edge_key = (subject, obj, predicate)
            if edge_key not in self.metadata_store:
                self.metadata_store[edge_key] = []
            self.metadata_store[edge_key].append(metadata)
    
    def query_entity(self, entity: str) -> List[Dict[str, Any]]:
        """
        Query all relationships for an entity.
        
        Args:
            entity: Entity to query
            
        Returns:
            List of relationships involving the entity
        """
        entity = entity.strip().title()
        relationships = []
        
        if not self.graph.has_node(entity):
            return relationships
        
        # Outgoing relationships (entity as subject)
        for neighbor in self.graph.successors(entity):
            edge_data = self.graph.get_edge_data(entity, neighbor)
            for edge_key, edge_attrs in edge_data.items():
                predicate = edge_attrs.get('predicate', 'related_to')
                relationships.append({
                    'subject': entity,
                    'predicate': predicate,
                    'object': neighbor,
                    'direction': 'outgoing'
                })
        
        # Incoming relationships (entity as object)
        for neighbor in self.graph.predecessors(entity):
            edge_data = self.graph.get_edge_data(neighbor, entity)
            for edge_key, edge_attrs in edge_data.items():
                predicate = edge_attrs.get('predicate', 'related_to')
                relationships.append({
                    'subject': neighbor,
                    'predicate': predicate,
                    'object': entity,
                    'direction': 'incoming'
                })
        
        return relationships
    
    def query_relation(self, subject: str, predicate: str) -> List[str]:
        """
        Query objects for a specific subject-predicate pair.
        
        Args:
            subject: Subject entity
            predicate: Relationship/predicate
            
        Returns:
            List of object entities
        """
        subject = subject.strip().title()
        predicate = predicate.strip().lower().replace(" ", "_")
        objects = []
        
        if not self.graph.has_node(subject):
            return objects
        
        for neighbor in self.graph.successors(subject):
            edge_data = self.graph.get_edge_data(subject, neighbor)
            for edge_key, edge_attrs in edge_data.items():
                if edge_attrs.get('predicate') == predicate:
                    objects.append(neighbor)
        
        return objects
    
    def get_graph_stats(self) -> Dict[str, int]:
        """
        Get basic statistics about the graph.
        
        Returns:
            Dictionary with graph statistics
        """
        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'density': round(nx.density(self.graph), 4)
        }
    
    def find_paths(self, start_entity: str, end_entity: str, max_length: int = 3) -> List[List[str]]:
        """
        Find paths between two entities.
        
        Args:
            start_entity: Starting entity
            end_entity: Target entity
            max_length: Maximum path length
            
        Returns:
            List of paths (each path is a list of entities)
        """
        start_entity = start_entity.strip().title()
        end_entity = end_entity.strip().title()
        
        if not (self.graph.has_node(start_entity) and self.graph.has_node(end_entity)):
            return []
        
        try:
            paths = list(nx.all_simple_paths(
                self.graph, start_entity, end_entity, cutoff=max_length
            ))
            return paths[:10]  # Limit to first 10 paths
        except nx.NetworkXNoPath:
            return []
    
    def get_neighbors(self, entity: str, max_neighbors: int = 10) -> List[Dict[str, Any]]:
        """
        Get neighboring entities and their relationships.
        
        Args:
            entity: Entity to get neighbors for
            max_neighbors: Maximum number of neighbors to return
            
        Returns:
            List of neighbor information
        """
        entity = entity.strip().title()
        neighbors = []
        
        if not self.graph.has_node(entity):
            return neighbors
        
        # Get all neighbors (both successors and predecessors)
        all_neighbors = set(self.graph.successors(entity)) | set(self.graph.predecessors(entity))
        
        for neighbor in list(all_neighbors)[:max_neighbors]:
            neighbor_info = {
                'entity': neighbor,
                'relationships': []
            }
            
            # Get relationships
            if self.graph.has_edge(entity, neighbor):
                edge_data = self.graph.get_edge_data(entity, neighbor)
                for edge_key, edge_attrs in edge_data.items():
                    predicate = edge_attrs.get('predicate', 'related_to')
                    neighbor_info['relationships'].append({
                        'predicate': predicate,
                        'direction': 'outgoing'
                    })
            
            if self.graph.has_edge(neighbor, entity):
                edge_data = self.graph.get_edge_data(neighbor, entity)
                for edge_key, edge_attrs in edge_data.items():
                    predicate = edge_attrs.get('predicate', 'related_to')
                    neighbor_info['relationships'].append({
                        'predicate': predicate,
                        'direction': 'incoming'
                    })
            
            neighbors.append(neighbor_info)
        
        return neighbors
    
    def export_to_file(self, filename: str):
        """Export the graph to a JSON file."""
        graph_data = {
            'nodes': [{'id': node, **attrs} for node, attrs in self.graph.nodes(data=True)],
            'edges': [
                {
                    'source': source,
                    'target': target,
                    'predicate': attrs.get('predicate', 'related_to')
                }
                for source, target, attrs in self.graph.edges(data=True)
            ],
            'metadata': self.metadata_store
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
    
    def visualize(self, filename: str = "knowledge_graph.html", max_nodes: int = 50):
        """
        Create an interactive visualization of the knowledge graph.
        
        Args:
            filename: Output HTML filename
            max_nodes: Maximum number of nodes to include in visualization
        """
        try:
            from pyvis.network import Network
            
            # Create a subset if graph is too large
            if self.graph.number_of_nodes() > max_nodes:
                # Get the most connected nodes
                degree_centrality = nx.degree_centrality(self.graph)
                top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
                subgraph = self.graph.subgraph([node for node, _ in top_nodes])
            else:
                subgraph = self.graph
            
            # Create pyvis network
            net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
            
            # Add nodes
            for node in subgraph.nodes():
                net.add_node(node, label=node, title=node)
            
            # Add edges
            for source, target, data in subgraph.edges(data=True):
                predicate = data.get('predicate', 'related_to')
                net.add_edge(source, target, label=predicate, title=predicate)
            
            # Configure physics
            net.set_options("""
            var options = {
              "physics": {
                "enabled": true,
                "stabilization": {"iterations": 100}
              }
            }
            """)
            
            net.save_graph(filename)
            print(f"Knowledge graph visualization saved to {filename}")
            
        except ImportError:
            print("pyvis not available. Install with: pip install pyvis")


class Neo4jKnowledgeGraph(KnowledgeGraphBase):
    """
    Knowledge Graph implementation using Neo4j database.
    """
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j database URI
            user: Username
            password: Password
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver not available. Install with: pip install neo4j")
        
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Test connection
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            print("✅ Connected to Neo4j database")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close the database connection."""
        if hasattr(self, 'driver'):
            self.driver.close()
    
    def add_triple(self, subject: str, predicate: str, obj: str, metadata: Dict[str, Any] = None):
        """Add a triple to Neo4j."""
        query = """
        MERGE (s:Entity {name: $subject})
        MERGE (o:Entity {name: $object})
        MERGE (s)-[r:RELATION {type: $predicate}]->(o)
        SET r.metadata = $metadata
        """
        
        with self.driver.session() as session:
            session.run(query, subject=subject, object=obj, predicate=predicate, metadata=metadata or {})
    
    def query_entity(self, entity: str) -> List[Dict[str, Any]]:
        """Query all relationships for an entity in Neo4j."""
        query = """
        MATCH (e:Entity {name: $entity})
        OPTIONAL MATCH (e)-[r]->(other)
        RETURN e.name as subject, type(r) as predicate, other.name as object, 'outgoing' as direction
        UNION
        MATCH (e:Entity {name: $entity})
        OPTIONAL MATCH (other)-[r]->(e)
        RETURN other.name as subject, type(r) as predicate, e.name as object, 'incoming' as direction
        """
        
        relationships = []
        with self.driver.session() as session:
            result = session.run(query, entity=entity)
            for record in result:
                if record["predicate"]:  # Skip None relationships
                    relationships.append({
                        'subject': record["subject"],
                        'predicate': record["predicate"],
                        'object': record["object"],
                        'direction': record["direction"]
                    })
        
        return relationships
    
    def query_relation(self, subject: str, predicate: str) -> List[str]:
        """Query objects for a subject-predicate pair in Neo4j."""
        query = """
        MATCH (s:Entity {name: $subject})-[r:RELATION {type: $predicate}]->(o:Entity)
        RETURN o.name as object
        """
        
        objects = []
        with self.driver.session() as session:
            result = session.run(query, subject=subject, predicate=predicate)
            objects = [record["object"] for record in result]
        
        return objects
    
    def get_graph_stats(self) -> Dict[str, int]:
        """Get statistics from Neo4j."""
        with self.driver.session() as session:
            node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
            edge_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
        
        return {
            'nodes': node_count,
            'edges': edge_count,
            'density': round(edge_count / (node_count * (node_count - 1)) if node_count > 1 else 0, 4)
        }


class KnowledgeGraphManager:
    """
    Manager class that provides a unified interface for different KG backends.
    """
    
    def __init__(self, backend: str = "networkx", **kwargs):
        """
        Initialize the knowledge graph manager.
        
        Args:
            backend: Backend type ("networkx" or "neo4j")
            **kwargs: Additional arguments for backend initialization
        """
        self.backend_type = backend
        
        if backend == "networkx":
            self.kg = NetworkXKnowledgeGraph()
        elif backend == "neo4j":
            self.kg = Neo4jKnowledgeGraph(**kwargs)
        else:
            raise ValueError(f"Unsupported backend: {backend}")
    
    def add_triples_from_extraction(self, triples: List[Dict[str, Any]]):
        """
        Add triples from extraction results to the knowledge graph.
        
        Args:
            triples: List of extracted triples with metadata
        """
        for triple in triples:
            subject = triple.get('subject', '')
            predicate = triple.get('predicate', '')
            obj = triple.get('object', '')
            
            if subject and predicate and obj:
                # Extract metadata (excluding the core triple data)
                metadata = {k: v for k, v in triple.items() 
                           if k not in ['subject', 'predicate', 'object']}
                
                self.kg.add_triple(subject, predicate, obj, metadata)
    
    def answer_query_with_kg(self, query: str) -> Dict[str, Any]:
        """
        Answer a query using the knowledge graph.
        
        Args:
            query: Natural language query
            
        Returns:
            Structured answer with KG information
        """
        # Simple keyword-based query processing
        query_lower = query.lower()
        
        # Extract potential entities from query
        entities = []
        graph_stats = self.kg.get_graph_stats()
        
        if graph_stats['nodes'] == 0:
            return {
                'answer': "Knowledge graph is empty. No information available.",
                'entities_found': [],
                'relationships': [],
                'paths': []
            }
        
        # Common entity patterns in space biology
        entity_patterns = [
            'microgravity', 'bone density', 'mice', 'plants', 'arabidopsis',
            'immune system', 'radiation', 'astronauts', 'spaceflight',
            'gene expression', 'osteoclast', 'osteoblast'
        ]
        
        for pattern in entity_patterns:
            if pattern in query_lower:
                entities.append(pattern.title())
        
        # Get information for found entities
        relationships = []
        paths = []
        
        for entity in entities:
            entity_rels = self.kg.query_entity(entity)
            relationships.extend(entity_rels)
        
        # Find paths between entities if multiple found
        if len(entities) >= 2:
            paths = self.kg.find_paths(entities[0], entities[1]) if hasattr(self.kg, 'find_paths') else []
        
        return {
            'answer': self._format_kg_answer(entities, relationships, paths),
            'entities_found': entities,
            'relationships': relationships,
            'paths': paths,
            'graph_stats': graph_stats
        }
    
    def _format_kg_answer(self, entities: List[str], relationships: List[Dict], paths: List[List[str]]) -> str:
        """Format KG information into a natural language answer."""
        if not entities:
            return "No relevant entities found in the knowledge graph."
        
        answer_parts = []
        
        # Report found entities
        if len(entities) == 1:
            answer_parts.append(f"Found information about {entities[0]} in the knowledge graph:")
        else:
            entity_list = ", ".join(entities[:-1]) + f" and {entities[-1]}"
            answer_parts.append(f"Found information about {entity_list} in the knowledge graph:")
        
        # Report relationships
        if relationships:
            answer_parts.append("\nKey relationships:")
            for rel in relationships[:5]:  # Limit to first 5 relationships
                direction_arrow = "→" if rel['direction'] == 'outgoing' else "←"
                answer_parts.append(f"• {rel['subject']} {direction_arrow}[{rel['predicate']}]→ {rel['object']}")
        
        # Report paths between entities
        if paths:
            answer_parts.append(f"\nConnections between entities:")
            for path in paths[:3]:  # Limit to first 3 paths
                path_str = " → ".join(path)
                answer_parts.append(f"• {path_str}")
        
        return "\n".join(answer_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the knowledge graph."""
        stats = self.kg.get_graph_stats()
        stats['backend'] = self.backend_type
        return stats


# Demo and testing
if __name__ == "__main__":
    print("=== Knowledge Graph Infrastructure Demo ===\n")
    
    # Initialize KG manager with NetworkX backend
    kg_manager = KnowledgeGraphManager(backend="networkx")
    
    # Add some sample triples
    sample_triples = [
        {
            'subject': 'Microgravity',
            'predicate': 'affects',
            'object': 'Bone Density',
            'confidence': 0.95,
            'source': 'demo'
        },
        {
            'subject': 'Mice',
            'predicate': 'exposed_to',
            'object': 'Microgravity',
            'confidence': 0.9,
            'source': 'demo'
        },
        {
            'subject': 'Arabidopsis',
            'predicate': 'grows_in',
            'object': 'Microgravity',
            'confidence': 0.85,
            'source': 'demo'
        },
        {
            'subject': 'Space Radiation',
            'predicate': 'damages',
            'object': 'Immune System',
            'confidence': 0.88,
            'source': 'demo'
        }
    ]
    
    print("Adding sample triples to knowledge graph...")
    kg_manager.add_triples_from_extraction(sample_triples)
    
    # Display stats
    stats = kg_manager.get_stats()
    print(f"Knowledge Graph Stats: {stats}")
    
    # Test queries
    test_queries = [
        "What affects bone density?",
        "How does microgravity affect mice?",
        "What happens to plants in space?"
    ]
    
    print("\n" + "="*50)
    print("Testing Knowledge Graph Queries:")
    print("="*50)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 30)
        result = kg_manager.answer_query_with_kg(query)
        print(result['answer'])
    
    # Create visualization
    if hasattr(kg_manager.kg, 'visualize'):
        kg_manager.kg.visualize("demo_kg.html")