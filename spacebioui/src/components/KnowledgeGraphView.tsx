import { useState, useEffect, useRef } from "react";
import { Network, ZoomIn, ZoomOut, Maximize2, RefreshCw, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { apiClient, BackendKGQueryResponse, BackendKGStats } from "@/lib/api";
import QueryResultGraph from "@/components/QueryResultGraph";

// Derived UI type from backend query response
interface UIQueryResult {
  query: string;
  answer: string;
  intent_description?: string;
  focus_area?: string | null;
  relationships: BackendKGQueryResponse['top_triples'];
  count: number;
}

const KnowledgeGraphView = () => {
  const [stats, setStats] = useState<BackendKGStats | null>(null);
  const [query, setQuery] = useState("");
  const [queryResult, setQueryResult] = useState<UIQueryResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingStats, setIsLoadingStats] = useState(true);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [iframeLoaded, setIframeLoaded] = useState(false);
  const [showGraph, setShowGraph] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  // Auto-load visualization once stats are fetched (only first time)
  useEffect(() => {
    if (!isLoadingStats && stats && !iframeRef.current?.src) {
      loadVisualization();
    }
  }, [isLoadingStats, stats]);

  const loadStats = async () => {
    try {
      const data = await apiClient.getKnowledgeGraphStats();
      setStats(data);
    } catch (error) {
      console.error("Error loading KG stats:", error);
    } finally {
      setIsLoadingStats(false);
    }
  };

  const loadVisualization = async () => {
    if (iframeRef.current) {
      setIsLoading(true);
      setIframeLoaded(false);
      iframeRef.current.src = apiClient.getKnowledgeGraphVisualizationUrl();
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    try {
      const result = await apiClient.queryKnowledgeGraph(query);
      setQueryResult({
        query: result.query,
        answer: result.answer,
        intent_description: result.intent?.intent_description,
        focus_area: result.intent?.focus_area,
        relationships: result.top_triples,
        count: result.relevant_triples_count
      });
    } catch (error) {
      console.error("Error querying KG:", error);
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <section className="py-8 px-6">
      <div className="container mx-auto">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Knowledge Graph</h2>
              <p className="text-muted-foreground">
                Interactive visualization of research connections
              </p>
              {stats && (
                <div className="flex gap-2 mt-2">
                  <Badge variant="secondary">{stats.total_nodes} nodes</Badge>
                  <Badge variant="secondary">{stats.total_edges} edges</Badge>
                  <Badge variant="secondary">Avg deg {stats.average_degree.toFixed(1)}</Badge>
                </div>
              )}
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="icon" 
                onClick={loadVisualization}
                disabled={isLoading}
              >
                {isLoading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Network className="h-4 w-4" />
                )}
              </Button>
              <Button variant="outline" size="icon">
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon">
                <ZoomOut className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Maximize2 className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* KG Query Interface */}
          <div className="mb-4">
            <div className="flex gap-2">
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleQuery()}
                placeholder="Query the knowledge graph (e.g., 'effects of microgravity on bone')"
                className="border-border"
                disabled={isLoading}
              />
              <Button 
                onClick={handleQuery}
                disabled={isLoading || !query.trim()}
                className="cosmic-gradient text-white"
              >
                <Search className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {queryResult && (
            <Card className="mb-4 p-4 border-border bg-card">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold">Query Results</h3>
                <div className="flex gap-2 text-xs">
                  <Button variant={showGraph ? 'default' : 'outline'} size="sm" onClick={() => setShowGraph(true)}>Graph</Button>
                  <Button variant={!showGraph ? 'default' : 'outline'} size="sm" onClick={() => setShowGraph(false)}>Text</Button>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Intent: {queryResult.intent_description || 'N/A'} | Focus: {queryResult.focus_area || 'General'}
              </p>
              {showGraph && queryResult.relationships.length > 0 ? (
                <div className="mb-4">
                  <QueryResultGraph triples={queryResult.relationships as any} height="420px" />
                  <p className="text-xs text-muted-foreground mt-2">
                    Showing top {queryResult.relationships.length} relationships (confidence color coded)
                  </p>
                </div>
              ) : (
                <p className="text-sm mb-3 whitespace-pre-wrap leading-relaxed">{queryResult.answer}</p>
              )}
            </Card>
          )}
          
          <Card className="p-8 min-h-[500px] relative overflow-hidden border-border bg-card">
            {iframeRef.current?.src ? (
              <>
                {!iframeLoaded && (
                  <div className="absolute inset-0 flex items-center justify-center bg-background/60 backdrop-blur-sm z-10">
                    <div className="flex flex-col items-center gap-3">
                      <RefreshCw className="h-6 w-6 animate-spin" />
                      <p className="text-xs text-muted-foreground">Loading visualization...</p>
                    </div>
                  </div>
                )}
                <iframe
                  ref={iframeRef}
                  className="w-full h-full min-h-[500px] border-0"
                  title="Knowledge Graph Visualization"
                  onLoad={() => { setIsLoading(false); setIframeLoaded(true); }}
                />
              </>
            ) : (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center space-y-4 max-w-md">
                  <div className="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center mx-auto nebula-glow">
                    <Network className="w-12 h-12 text-primary animate-pulse" />
                  </div>
                  <h3 className="text-xl font-semibold">Knowledge Graph Visualization</h3>
                  <p className="text-muted-foreground">
                    {isLoadingStats 
                      ? "Loading knowledge graph statistics..." 
                      : "Click the network icon above to load the interactive visualization of research relationships"
                    }
                  </p>
                  {stats && (
                    <div className="grid grid-cols-3 gap-4 pt-4">
                      <div className="space-y-1">
                        <div className="w-4 h-4 rounded-full bg-primary mx-auto" />
                        <p className="text-xs text-muted-foreground">Nodes</p>
                        <p className="text-xs font-medium">{stats.total_nodes}</p>
                      </div>
                      <div className="space-y-1">
                        <div className="w-4 h-4 rounded-full bg-secondary mx-auto" />
                        <p className="text-xs text-muted-foreground">Edges</p>
                        <p className="text-xs font-medium">{stats.total_edges}</p>
                      </div>
                      <div className="space-y-1">
                        <div className="w-4 h-4 rounded-full bg-accent mx-auto" />
                        <p className="text-xs text-muted-foreground">Density</p>
                        <p className="text-xs font-medium">{stats.density.toFixed(4)}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </Card>
        </div>
      </div>
    </section>
  );
};

export default KnowledgeGraphView;
