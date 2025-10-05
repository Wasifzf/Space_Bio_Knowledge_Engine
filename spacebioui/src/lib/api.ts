// Allow overriding API base via Vite env variable
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000';

// Backend /chat response model (EnhancedChatResponse)
export interface EnhancedChatResponse {
  answer: string;
  query: string;
  vector_results: number; // number of vector search matches used
  kg_relationships: number; // number of KG relationships leveraged
  sources: {
    vector_context?: Array<Record<string, any>>;
    kg_context?: Record<string, any>;
    [key: string]: any;
  };
}

// Backend /kg/query response model (KGQueryResponse in api.py)
export interface BackendKGQueryResponse {
  query: string;
  answer: string;
  intent: {
    entities?: string[];
    query_type?: string;
    focus_area?: string | null;
    intent_description?: string;
    [key: string]: any;
  };
  relevant_triples_count: number;
  top_triples: Array<{
    subject: string;
    predicate: string;
    object: string;
    confidence: number;
    paper_id?: string;
    title?: string;
    url?: string;
    source_text?: string;
  }>;
}

// Backend /kg/stats response model (KGStatsResponse)
export interface BackendKGStats {
  total_nodes: number;
  total_edges: number;
  node_types: Record<string, number>;
  most_connected_nodes: Array<{ node: string; connections: number }>;
  average_degree: number;
  density: number;
}

// Backend /kg/data simplified response
export interface BackendKGDataSample {
  extraction_info: Record<string, any>;
  total_triples: number;
  sample_triples: Array<Record<string, any>>;
  processed_papers: number;
}

export class APIClient {
  async sendChatMessage(message: string, options?: { top_k?: number; include_kg?: boolean }): Promise<EnhancedChatResponse> {
    const payload: Record<string, any> = { query: message };
    if (options?.top_k) payload.top_k = options.top_k;
    if (options?.include_kg !== undefined) payload.include_kg = options.include_kg;

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Chat API error ${response.status}: ${text}`);
    }
    return response.json();
  }

  async queryKnowledgeGraph(query: string): Promise<BackendKGQueryResponse> {
    const response = await fetch(`${API_BASE_URL}/kg/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`KG Query API error ${response.status}: ${text}`);
    }
    return response.json();
  }

  async getKnowledgeGraphStats(): Promise<BackendKGStats> {
    const response = await fetch(`${API_BASE_URL}/kg/stats`);
    if (!response.ok) {
      throw new Error(`KG Stats API error ${response.status}`);
    }
    return response.json();
  }

  async getKnowledgeGraphData(): Promise<BackendKGDataSample> {
    const response = await fetch(`${API_BASE_URL}/kg/data`);
    if (!response.ok) {
      throw new Error(`KG Data API error ${response.status}`);
    }
    return response.json();
  }

  getKnowledgeGraphVisualizationUrl(): string {
    // This endpoint serves raw HTML; we can embed it directly in an iframe
    return `${API_BASE_URL}/kg/visualization`;
  }
}

export const apiClient = new APIClient();