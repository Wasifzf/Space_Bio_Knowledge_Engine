"""
Knowledge Graph Visualizer using NetworkX + PyVis
=================================================

This module creates interactive visualizations of the extracted knowledge triples
from space biology research papers, allowing for exploration and querying.
"""

import json
import networkx as nx
from pyvis.network import Network
import re
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter
import webbrowser
import os

class KnowledgeGraphVisualizer:
    """
    Creates and visualizes knowledge graphs from extracted triples
    """
    
    def __init__(self, triples_file: str = "pinecone_extracted_triples.json"):
        """Initialize with triples data"""
        self.triples_file = triples_file
        self.graph = nx.DiGraph()  # Directed graph for relationships
        self.triples_data = None
        self.node_types = {}
        self.edge_metadata = {}
        
        # Load the triples data
        self.load_triples()
        
        # Color scheme for different node types
        self.node_colors = {
            'species': '#FF6B6B',      # Red for biological species
            'condition': '#4ECDC4',     # Teal for conditions/treatments
            'measurement': '#45B7D1',   # Blue for measurements/results
            'location': '#96CEB4',      # Green for locations
            'substance': '#FFEAA7',     # Yellow for chemicals/substances
            'process': '#DDA0DD',       # Purple for biological processes
            'disease': '#FF7675',       # Salmon for diseases/pathology
            'technology': '#74B9FF',    # Light blue for technology/equipment
            'unknown': '#DCDDE1'        # Gray for unclassified
        }
    
    def load_triples(self):
        """Load triples from JSON file"""
        try:
            with open(self.triples_file, 'r') as f:
                self.triples_data = json.load(f)
            print(f"✅ Loaded {len(self.triples_data['triples'])} triples from {len(self.triples_data['processed_papers'])} papers")
        except FileNotFoundError:
            print(f"❌ File {self.triples_file} not found!")
            return
        except Exception as e:
            print(f"❌ Error loading triples: {e}")
            return
    
    def classify_node_type(self, node: str) -> str:
        """
        Classify nodes into types based on common patterns in space biology research
        """
        node_lower = node.lower()
        
        # Species and organisms
        species_patterns = [
            'mice', 'mouse', 'rat', 'human', 'astronaut', 'arabidopsis', 
            'drosophila', 'cell', 'bacteria', 'virus', 'organism', 'species',
            'klebsiella', 'enterobacteriales', 'lactobacillus', 'bacillus',
            'microbe', 'microorganism', 'pathogen'
        ]
        
        # Conditions and treatments
        condition_patterns = [
            'microgravity', 'weightless', 'space', 'radiation', 'cosmic',
            'hypergravity', 'centrifuge', 'simulated', 'flight', 'mission',
            'unloading', 'loading', 'stress', 'environment', 'exposure'
        ]
        
        # Measurements and results
        measurement_patterns = [
            'density', 'expression', 'level', 'rate', 'activity', 'function',
            'response', 'change', 'adaptation', 'growth', 'development',
            'concentration', 'volume', 'mass', 'weight', 'size', 'count'
        ]
        
        # Anatomical locations and body parts
        location_patterns = [
            'bone', 'muscle', 'heart', 'brain', 'liver', 'kidney', 'lung',
            'blood', 'tissue', 'organ', 'cell', 'membrane', 'nucleus',
            'gastrointestinal', 'tract', 'nasopharynx', 'skeleton'
        ]
        
        # Substances and chemicals
        substance_patterns = [
            'protein', 'gene', 'dna', 'rna', 'hormone', 'enzyme', 'chemical',
            'molecule', 'compound', 'drug', 'antibiotic', 'calcium', 'oxygen',
            'glucose', 'insulin', 'collagen', 'cytokine'
        ]
        
        # Biological processes
        process_patterns = [
            'metabolism', 'synthesis', 'degradation', 'signaling', 'transport',
            'regulation', 'transcription', 'translation', 'replication',
            'differentiation', 'proliferation', 'apoptosis', 'inflammation'
        ]
        
        # Diseases and pathology
        disease_patterns = [
            'disease', 'pathology', 'infection', 'cancer', 'tumor', 'syndrome',
            'disorder', 'dysfunction', 'injury', 'damage', 'toxicity',
            'resistance', 'virulence'
        ]
        
        # Technology and equipment
        technology_patterns = [
            'system', 'device', 'equipment', 'platform', 'instrument',
            'sensor', 'monitor', 'station', 'satellite', 'spacecraft'
        ]
        
        # Check patterns
        for pattern in species_patterns:
            if pattern in node_lower:
                return 'species'
        
        for pattern in condition_patterns:
            if pattern in node_lower:
                return 'condition'
        
        for pattern in measurement_patterns:
            if pattern in node_lower:
                return 'measurement'
        
        for pattern in location_patterns:
            if pattern in node_lower:
                return 'location'
        
        for pattern in substance_patterns:
            if pattern in node_lower:
                return 'substance'
        
        for pattern in process_patterns:
            if pattern in node_lower:
                return 'process'
        
        for pattern in disease_patterns:
            if pattern in node_lower:
                return 'disease'
        
        for pattern in technology_patterns:
            if pattern in node_lower:
                return 'technology'
        
        return 'unknown'
    
    def build_graph(self):
        """Build NetworkX graph from triples"""
        if not self.triples_data:
            print("❌ No triples data available!")
            return
        
        print("🔨 Building NetworkX graph...")
        
        for triple in self.triples_data['triples']:
            subject = triple['subject']
            predicate = triple['predicate']
            obj = triple['object']
            
            # Classify node types
            if subject not in self.node_types:
                self.node_types[subject] = self.classify_node_type(subject)
            if obj not in self.node_types:
                self.node_types[obj] = self.classify_node_type(obj)
            
            # Add nodes with attributes
            self.graph.add_node(subject, 
                              node_type=self.node_types[subject],
                              color=self.node_colors[self.node_types[subject]])
            
            self.graph.add_node(obj, 
                              node_type=self.node_types[obj],
                              color=self.node_colors[self.node_types[obj]])
            
            # Add edge with metadata
            edge_key = f"{subject}_{predicate}_{obj}"
            self.edge_metadata[edge_key] = {
                'paper_id': triple['paper_id'],
                'title': triple['title'],
                'url': triple['url'],
                'confidence': triple['confidence'],
                'source_text': triple['source_text'][:100] + "...",  # Truncate for display
                'extraction_date': triple['extraction_date']
            }
            
            self.graph.add_edge(subject, obj, 
                              label=predicate,
                              title=f"Relation: {predicate}\nConfidence: {triple['confidence']}\nPaper: {triple['title'][:50]}...",
                              confidence=triple['confidence'],
                              paper_id=triple['paper_id'])
        
        # Print graph statistics
        print(f"✅ Graph built successfully!")
        print(f"📊 Nodes: {self.graph.number_of_nodes()}")
        print(f"📊 Edges: {self.graph.number_of_edges()}")
        
        # Print node type distribution
        type_counts = Counter(self.node_types.values())
        print(f"📈 Node Type Distribution:")
        for node_type, count in type_counts.most_common():
            print(f"   {node_type}: {count} nodes")
    
    def create_pyvis_visualization(self, output_file: str = "knowledge_graph.html", 
                                 width: str = "100%", height: str = "800px"):
        """Create interactive PyVis visualization"""
        if self.graph.number_of_nodes() == 0:
            print("❌ No graph to visualize! Build graph first.")
            return
        
        print("🎨 Creating PyVis visualization...")
        
        # Create PyVis network
        net = Network(width=width, height=height, 
                     bgcolor="#222222", font_color="white",
                     directed=True)
        
        # Configure physics for better layout
        net.set_options("""
        var options = {
          "physics": {
            "enabled": true,
            "stabilization": {"iterations": 100},
            "barnesHut": {
              "gravitationalConstant": -8000,
              "centralGravity": 0.3,
              "springLength": 95,
              "springConstant": 0.04,
              "damping": 0.09
            }
          }
        }
        """)
        
        # Add nodes with enhanced styling
        for node in self.graph.nodes():
            node_type = self.node_types.get(node, 'unknown')
            color = self.node_colors[node_type]
            
            # Size based on degree (connections)
            degree = self.graph.degree(node)
            size = min(50, max(10, degree * 3))
            
            net.add_node(node, 
                        label=node,
                        color=color,
                        size=size,
                        title=f"Type: {node_type}\nConnections: {degree}",
                        font={'size': 12})
        
        # Add edges with enhanced styling
        for edge in self.graph.edges(data=True):
            source, target, data = edge
            
            # Edge color based on confidence
            confidence = data.get('confidence', 0.5)
            if confidence >= 0.9:
                edge_color = "#00FF00"  # Green for high confidence
            elif confidence >= 0.7:
                edge_color = "#FFFF00"  # Yellow for medium confidence
            else:
                edge_color = "#FF6600"  # Orange for lower confidence
            
            net.add_edge(source, target,
                        label=data.get('label', ''),
                        color=edge_color,
                        width=2,
                        title=data.get('title', ''))
        
        # Save visualization
        net.save_graph(output_file)
        print(f"✅ Interactive visualization saved as '{output_file}'")
        
        # Create legend
        self.create_legend(output_file)
        
        return output_file
    
    def create_legend(self, html_file: str):
        """Add a legend to the HTML file"""
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        legend_html = """
        <div id="legend" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.8); color: white; padding: 15px; border-radius: 5px; font-family: Arial; z-index: 1000;">
            <h3 style="margin-top: 0;">Knowledge Graph Legend</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                <div><span style="color: #FF6B6B;">•</span> Species/Organisms</div>
                <div><span style="color: #4ECDC4;">•</span> Conditions/Treatments</div>
                <div><span style="color: #45B7D1;">•</span> Measurements/Results</div>
                <div><span style="color: #96CEB4;">•</span> Anatomical Locations</div>
                <div><span style="color: #FFEAA7;">•</span> Substances/Chemicals</div>
                <div><span style="color: #DDA0DD;">•</span> Biological Processes</div>
                <div><span style="color: #FF7675;">•</span> Diseases/Pathology</div>
                <div><span style="color: #74B9FF;">•</span> Technology/Equipment</div>
            </div>
            <div style="margin-top: 10px;">
                <div><span style="color: #00FF00;">—</span> High Confidence (≥0.9)</div>
                <div><span style="color: #FFFF00;">—</span> Medium Confidence (≥0.7)</div>
                <div><span style="color: #FF6600;">—</span> Lower Confidence (<0.7)</div>
            </div>
            <div style="margin-top: 10px; font-size: 12px;">
                Node size = number of connections<br>
                Hover for details • Drag to explore
            </div>
        </div>
        """
        
        # Insert legend after body tag
        content = content.replace('<body>', f'<body>{legend_html}')
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def get_graph_statistics(self):
        """Get comprehensive graph statistics"""
        if self.graph.number_of_nodes() == 0:
            return "No graph data available"
        
        stats = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_types': dict(Counter(self.node_types.values())),
            'most_connected_nodes': [],
            'average_degree': 0,
            'density': nx.density(self.graph)
        }
        
        # Calculate degree statistics
        degrees = dict(self.graph.degree())
        if degrees:
            stats['average_degree'] = sum(degrees.values()) / len(degrees)
            # Get top 10 most connected nodes
            sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
            stats['most_connected_nodes'] = sorted_nodes[:10]
        
        return stats

def main():
    """Main function to demonstrate the visualizer"""
    print("🚀 Knowledge Graph Visualizer Demo")
    print("=" * 50)
    
    # Create visualizer
    visualizer = KnowledgeGraphVisualizer()
    
    if not visualizer.triples_data:
        print("❌ No triples data found. Run the extractor first!")
        return
    
    # Build graph
    visualizer.build_graph()
    
    # Get statistics
    stats = visualizer.get_graph_statistics()
    print(f"\n📊 Graph Statistics:")
    print(f"   Total Nodes: {stats['total_nodes']}")
    print(f"   Total Edges: {stats['total_edges']}")
    print(f"   Average Connections per Node: {stats['average_degree']:.2f}")
    print(f"   Graph Density: {stats['density']:.4f}")
    
    print(f"\n🔝 Most Connected Concepts:")
    for node, degree in stats['most_connected_nodes'][:5]:
        print(f"   {node}: {degree} connections")
    
    # Create visualization
    output_file = visualizer.create_pyvis_visualization()
    
    # Open in browser
    if os.path.exists(output_file):
        print(f"🌐 Opening visualization in browser...")
        webbrowser.open(f"file://{os.path.abspath(output_file)}")
    
    print(f"\n✅ Visualization complete! Open '{output_file}' to explore your Knowledge Graph.")

if __name__ == "__main__":
    main()