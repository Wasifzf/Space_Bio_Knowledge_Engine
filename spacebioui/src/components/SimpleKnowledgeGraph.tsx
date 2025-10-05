import { useState } from "react";
import VisualKnowledgeGraph from "./VisualKnowledgeGraph";

interface Node {
  id: string;
  label: string;
  type: 'subject' | 'object' | 'predicate';
}

interface Edge {
  id: string;
  from: string;
  to: string;
  label: string;
  confidence?: number;
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

const SimpleKnowledgeGraph = () => {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });

  const convertToGraphData = (apiResult: any): GraphData => {
    if (!apiResult?.top_triples || !Array.isArray(apiResult.top_triples)) {
      return { nodes: [], edges: [] };
    }

    const nodes: Node[] = [];
    const edges: Edge[] = [];
    const nodeIds = new Set<string>();

    apiResult.top_triples.forEach((triple: any, index: number) => {
      const subjectId = `subject_${triple.subject.replace(/\s+/g, '_')}`;
      const objectId = `object_${triple.object.replace(/\s+/g, '_')}`;
      const predicateId = `predicate_${triple.predicate.replace(/\s+/g, '_')}_${index}`;

      // Add subject node
      if (!nodeIds.has(subjectId)) {
        nodes.push({
          id: subjectId,
          label: triple.subject,
          type: 'subject'
        });
        nodeIds.add(subjectId);
      }

      // Add object node
      if (!nodeIds.has(objectId)) {
        nodes.push({
          id: objectId,
          label: triple.object,
          type: 'object'
        });
        nodeIds.add(objectId);
      }

      // Add predicate as intermediate node
      nodes.push({
        id: predicateId,
        label: triple.predicate,
        type: 'predicate'
      });

      // Add edges: subject -> predicate -> object
      edges.push({
        id: `edge_${index}_1`,
        from: subjectId,
        to: predicateId,
        label: "relates_to",
        confidence: triple.confidence
      });

      edges.push({
        id: `edge_${index}_2`,
        from: predicateId,
        to: objectId,
        label: "describes",
        confidence: triple.confidence
      });
    });

    return { nodes, edges };
  };

  const handleQuery = async () => {
    if (!query.trim()) return;
    setIsLoading(true);
    setError(null);
    setResult(null);
    setGraphData({ nodes: [], edges: [] });
    
    try {
      const response = await fetch('http://localhost:8000/kg/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      setResult(data);
      
      // Convert API response to graph data
      const graphData = convertToGraphData(data);
      setGraphData(graphData);
    } catch (error) {
      console.error("Error querying KG:", error);
      setError(error instanceof Error ? error.message : "Unknown error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200 h-full">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
          <span className="text-white text-sm">🕸️</span>
        </div>
        <h3 className="text-xl font-semibold">Knowledge Graph</h3>
      </div>
      
      <div className="space-y-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Query the knowledge graph..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
          />
          <button
            onClick={handleQuery}
            disabled={isLoading || !query.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "..." : "Search"}
          </button>
        </div>
        
        {/* Visual Knowledge Graph */}
        <div className="border border-gray-200 rounded-lg p-4">
          {isLoading ? (
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
              <div className="text-center text-gray-500">
                <div className="animate-spin text-2xl mb-2">⚡</div>
                <p>Generating knowledge graph...</p>
              </div>
            </div>
          ) : (
            <VisualKnowledgeGraph data={graphData} width={650} height={400} />
          )}
        </div>
        
        {/* Text Results */}
        <div className="h-48 bg-gray-50 rounded border border-gray-200 p-4 overflow-y-auto">
          {error && (
            <div className="text-red-600 text-sm">
              <p><strong>Error:</strong> {error}</p>
              <p className="mt-2">Make sure the backend is running on port 8000</p>
            </div>
          )}
          
          {result && (
            <div className="space-y-3">
              <div className="text-sm">
                <p><strong>Query:</strong> {result.query}</p>
                <p><strong>Answer:</strong> {result.answer}</p>
                {result.intent && (
                  <p><strong>Intent:</strong> {result.intent.intent_description}</p>
                )}
                <p><strong>Relationships found:</strong> {result.relevant_triples_count}</p>
              </div>
              
              {result.top_triples && result.top_triples.length > 0 && (
                <div className="space-y-2">
                  <p className="font-semibold text-sm">Top Relationships:</p>
                  {result.top_triples.slice(0, 3).map((triple: any, idx: number) => (
                    <div key={idx} className="bg-white p-2 rounded border text-xs">
                      <p><strong>{triple.subject}</strong> → <em>{triple.predicate}</em> → <strong>{triple.object}</strong></p>
                      {triple.confidence && (
                        <p className="text-gray-600">Confidence: {(triple.confidence * 100).toFixed(1)}%</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          
          {!result && !error && !isLoading && (
            <div className="text-center text-gray-500 flex items-center justify-center h-full">
              <div>
                <div className="text-4xl mb-2">📊</div>
                <p>Query Results</p>
                <p className="text-sm">Text analysis and details will appear here</p>
              </div>
            </div>
          )}
          
          {isLoading && (
            <div className="text-center text-gray-500 flex items-center justify-center h-full">
              <div>
                <div className="animate-spin text-2xl mb-2">⚡</div>
                <p>Analyzing query...</p>
              </div>
            </div>
          )}
        </div>
        
        <div className="text-sm text-gray-600">
          <p><strong>Status:</strong> {error ? "❌ Disconnected" : "✅ Ready"} - NASA space biology knowledge graph</p>
          <p><strong>Backend:</strong> http://localhost:8000</p>
        </div>
      </div>
    </div>
  );
};

export default SimpleKnowledgeGraph;