"""
Enhanced FastAPI Web Service for Space Biology Chatbot with Knowledge Graph
Provides RESTful API endpoints for the space biology research chatbot with KG integration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import asyncio
from contextlib import asynccontextmanager
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our enhanced chatbot and KG components
from enhanced_space_bio_chatbot import EnhancedSpaceBioChatbot
from enhanced_kg_querier import EnhancedKGQuerier
from kg_visualizer import KnowledgeGraphVisualizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
chatbot_instance = None
kg_querier_instance = None
kg_visualizer_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize components on startup and cleanup on shutdown."""
    global chatbot_instance, kg_querier_instance, kg_visualizer_instance
    try:
        logger.info("Initializing Enhanced Space Biology Chatbot...")
        chatbot_instance = EnhancedSpaceBioChatbot()
        
        logger.info("Initializing Knowledge Graph Querier...")
        kg_querier_instance = EnhancedKGQuerier()
        
        logger.info("Initializing Knowledge Graph Visualizer...")
        kg_visualizer_instance = KnowledgeGraphVisualizer()
        
        logger.info("✅ All components initialized successfully!")
        yield
    except Exception as e:
        logger.error(f"❌ Failed to initialize components: {e}")
        raise
    finally:
        logger.info("Shutting down services...")

# Create FastAPI app
app = FastAPI(
    title="Enhanced Space Biology Research API with Knowledge Graph",
    description="Advanced chatbot API with Knowledge Graph integration for space biology research",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware for web frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving the knowledge graph visualization
app.mount("/static", StaticFiles(directory="."), name="static")

# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Request model for enhanced chat endpoint."""
    query: str = Field(..., min_length=1, max_length=1000, description="The user's question about space biology")
    top_k: Optional[int] = Field(default=3, ge=1, le=10, description="Number of vector documents to retrieve")
    include_kg: Optional[bool] = Field(default=True, description="Include Knowledge Graph analysis")

class EnhancedChatResponse(BaseModel):
    """Enhanced response model with KG integration."""
    answer: str = Field(..., description="The comprehensive chatbot response")
    query: str = Field(..., description="The original query")
    vector_results: int = Field(..., description="Number of vector search results used")
    kg_relationships: int = Field(..., description="Number of KG relationships found")
    sources: Dict[str, Any] = Field(..., description="Detailed source information")

class KGQueryRequest(BaseModel):
    """Request model for Knowledge Graph queries."""
    query: str = Field(..., min_length=1, max_length=500, description="Natural language query for the KG")

class KGQueryResponse(BaseModel):
    """Response model for Knowledge Graph queries."""
    query: str = Field(..., description="The original query")
    answer: str = Field(..., description="The KG-generated answer")
    intent: Dict[str, Any] = Field(..., description="Extracted query intent and entities")
    relevant_triples_count: int = Field(..., description="Number of relevant relationships found")
    top_triples: List[Dict[str, Any]] = Field(..., description="Top relevant knowledge triples")

class KGStatsResponse(BaseModel):
    """Response model for Knowledge Graph statistics."""
    total_nodes: int
    total_edges: int
    node_types: Dict[str, int]
    most_connected_nodes: List[Dict[str, Any]]
    average_degree: float
    density: float

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    message: str
    version: str = "2.0.0"
    components: Dict[str, str]

# API Endpoints

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with API information."""
    return HealthResponse(
        status="healthy",
        message="Enhanced Space Biology Research API with Knowledge Graph is running! Visit /docs for documentation.",
        components={
            "chatbot": "Enhanced vector + KG chatbot",
            "knowledge_graph": "776 extracted relationships",
            "visualization": "Interactive graph available"
        }
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check for all components."""
    components_status = {}
    
    if chatbot_instance is None:
        components_status["chatbot"] = "❌ Not initialized"
    else:
        components_status["chatbot"] = "✅ Ready"
    
    if kg_querier_instance is None:
        components_status["kg_querier"] = "❌ Not initialized"
    else:
        components_status["kg_querier"] = "✅ Ready"
    
    if kg_visualizer_instance is None:
        components_status["kg_visualizer"] = "❌ Not initialized"
    else:
        components_status["kg_visualizer"] = "✅ Ready"
    
    overall_status = "healthy" if all("✅" in status for status in components_status.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        message="Component status check completed",
        components=components_status
    )

@app.post("/chat", response_model=EnhancedChatResponse)
async def enhanced_chat(request: ChatRequest):
    """
    Enhanced chat endpoint with Knowledge Graph integration.
    
    - **query**: Your question about space biology research
    - **top_k**: Number of vector documents to retrieve (default: 3)
    - **include_kg**: Whether to include Knowledge Graph analysis (default: true)
    
    Returns a comprehensive answer combining vector search and Knowledge Graph insights.
    """
    if chatbot_instance is None:
        raise HTTPException(status_code=503, detail="Enhanced chatbot service not initialized")
    
    try:
        logger.info(f"Processing enhanced query: {request.query[:100]}...")
        
        # Process using enhanced chatbot with both vector and KG
        result = chatbot_instance.chat(request.query)
        
        logger.info(f"Enhanced query processed. Vector results: {result['vector_results']}, KG relationships: {result['kg_relationships']}")
        
        return EnhancedChatResponse(
            answer=result['answer'],
            query=result['query'],
            vector_results=result['vector_results'],
            kg_relationships=result['kg_relationships'],
            sources=result['sources']
        )
        
    except Exception as e:
        logger.error(f"Error processing enhanced query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/chat/clear-memory")
async def clear_chat_memory():
    """
    Clear the chatbot's conversation memory.
    
    Useful for starting fresh conversations or when switching topics.
    """
    if chatbot_instance is None:
        raise HTTPException(status_code=503, detail="Enhanced chatbot service not initialized")
    
    try:
        chatbot_instance.clear_memory()
        return {"message": "Conversation memory cleared successfully", "status": "success"}
        
    except Exception as e:
        logger.error(f"Error clearing memory: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")

@app.get("/chat/memory-status")
async def get_memory_status():
    """
    Get information about the current conversation memory status.
    
    Returns the number of stored conversation exchanges and memory usage.
    """
    if chatbot_instance is None:
        raise HTTPException(status_code=503, detail="Enhanced chatbot service not initialized")
    
    try:
        return {
            "conversation_length": len(chatbot_instance.conversation_history),
            "max_history_length": chatbot_instance.max_history_length,
            "memory_enabled": True,
            "last_exchange_preview": (
                {
                    "user": chatbot_instance.conversation_history[-1]["user"][:100] + "..." if len(chatbot_instance.conversation_history[-1]["user"]) > 100 else chatbot_instance.conversation_history[-1]["user"],
                    "assistant": chatbot_instance.conversation_history[-1]["assistant"][:150] + "..." if len(chatbot_instance.conversation_history[-1]["assistant"]) > 150 else chatbot_instance.conversation_history[-1]["assistant"]
                } if chatbot_instance.conversation_history else None
            )
        }
        
    except Exception as e:
        logger.error(f"Error getting memory status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting memory status: {str(e)}")

@app.post("/kg/query", response_model=KGQueryResponse)
async def knowledge_graph_query(request: KGQueryRequest):
    """
    Query the Knowledge Graph with natural language.
    
    - **query**: Natural language question (e.g., "What affects bone density?", "Tell me about microgravity")
    
    Returns KG-specific insights and relationships.
    """
    if kg_querier_instance is None:
        raise HTTPException(status_code=503, detail="Knowledge Graph querier not initialized")
    
    try:
        logger.info(f"Processing KG query: {request.query[:100]}...")
        
        result = kg_querier_instance.enhanced_query(request.query)
        
        return KGQueryResponse(
            query=result['query'],
            answer=result['answer'],
            intent=result['intent'],
            relevant_triples_count=result['relevant_triples_count'],
            top_triples=result['top_triples']
        )
        
    except Exception as e:
        logger.error(f"Error processing KG query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing KG query: {str(e)}")

@app.get("/kg/stats", response_model=KGStatsResponse)
async def knowledge_graph_stats():
    """Get Knowledge Graph statistics and overview."""
    if kg_visualizer_instance is None:
        raise HTTPException(status_code=503, detail="Knowledge Graph visualizer not initialized")
    
    try:
        # Ensure graph is built (original visualizer does not auto-build)
        if kg_visualizer_instance.graph.number_of_nodes() == 0:
            kg_visualizer_instance.build_graph()

        raw_stats = kg_visualizer_instance.get_graph_statistics()

        # Handle case where a string was returned (no data)
        if isinstance(raw_stats, str):
            raise HTTPException(status_code=500, detail=raw_stats)

        # Robust formatting for most_connected_nodes supporting multiple shapes
        formatted_nodes = []
        raw_nodes = raw_stats.get('most_connected_nodes', [])[:10]
        for item in raw_nodes:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                node, connections = item[0], item[1]
            elif isinstance(item, dict) and 'node' in item and 'connections' in item:
                node, connections = item['node'], item['connections']
            else:
                node, connections = str(item), 0
            formatted_nodes.append({"node": node, "connections": int(connections)})

        return KGStatsResponse(
            total_nodes=raw_stats.get('total_nodes', 0),
            total_edges=raw_stats.get('total_edges', 0),
            node_types=raw_stats.get('node_types', {}),
            most_connected_nodes=formatted_nodes,
            average_degree=raw_stats.get('average_degree', 0.0),
            density=raw_stats.get('density', 0.0)
        )
        
    except Exception as e:
        logger.error(f"Error getting KG stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting KG statistics: {str(e)}")

@app.get("/kg/visualization")
async def get_knowledge_graph_visualization():
    """Serve the interactive Knowledge Graph visualization."""
    viz_file = "space_bio_knowledge_graph.html"
    
    if not os.path.exists(viz_file):
        # Generate visualization if it doesn't exist
        if kg_visualizer_instance is None:
            raise HTTPException(status_code=503, detail="Knowledge Graph visualizer not initialized")
        
        try:
            kg_visualizer_instance.build_graph()
            viz_file = kg_visualizer_instance.create_pyvis_visualization(viz_file)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating visualization: {str(e)}")
    
    return FileResponse(viz_file, media_type='text/html')

@app.get("/kg/data")
async def get_knowledge_graph_data():
    """Get raw Knowledge Graph data for custom visualizations."""
    if kg_visualizer_instance is None:
        raise HTTPException(status_code=503, detail="Knowledge Graph visualizer not initialized")
    
    try:
        # Load the triples data
        with open("pinecone_extracted_triples.json", 'r') as f:
            data = json.load(f)
        
        return {
            "extraction_info": data["extraction_info"],
            "total_triples": len(data["triples"]),
            "sample_triples": data["triples"][:10],  # Return first 10 as sample
            "processed_papers": len(data["processed_papers"])
        }
        
    except Exception as e:
        logger.error(f"Error getting KG data: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting KG data: {str(e)}")

@app.get("/info")
async def api_info():
    """Get comprehensive information about the Enhanced API capabilities."""
    return {
        "api_name": "Enhanced Space Biology Research API",
        "version": "2.0.0",
        "description": "AI-powered chatbot with Knowledge Graph integration for space biology research",
        "capabilities": [
            "Enhanced vector + Knowledge Graph search",
            "Natural language KG queries",
            "Interactive graph visualization",
            "Research relationship discovery",
            "Contextual answer synthesis",
            "Research provenance tracking"
        ],
        "endpoints": {
            "/chat": "Enhanced chatbot with KG integration",
            "/kg/query": "Direct Knowledge Graph queries",
            "/kg/stats": "Knowledge Graph statistics",
            "/kg/visualization": "Interactive graph visualization",
            "/kg/data": "Raw KG data access"
        },
        "knowledge_graph": {
            "total_relationships": "776 extracted triples",
            "papers_processed": "160 research papers",
            "node_types": "9 categories (species, conditions, etc.)",
            "visualization": "Interactive PyVis graph"
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error", 
            "detail": "An unexpected error occurred",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )