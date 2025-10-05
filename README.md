# Space Biology Knowledge Graph Platform

A comprehensive research platform for exploring space biology through advanced knowledge graph technology, vector databases, and conversational AI. This system enables researchers to query, visualize, and analyze relationships between biological phenomena in space environments.

## Overview

The Space Biology Knowledge Graph Platform integrates multiple data sources and cutting-edge technologies to provide researchers with an intuitive interface for exploring complex relationships in space biology research. The platform combines semantic search, knowledge graph visualization, and conversational AI to deliver contextual, comprehensive answers to scientific queries.

## Features

### Core Capabilities
- **Intelligent Conversational Interface**: AI-powered chatbot specializing in space biology research with conversation memory
- **Knowledge Graph Visualization**: Interactive network visualization of biological relationships and research connections
- **Vector-Based Semantic Search**: Advanced similarity search across research papers and publications
- **Multi-Modal Query Processing**: Combines vector search and knowledge graph querying for comprehensive results
- **Memory-Enabled Conversations**: Maintains conversation context for follow-up questions and detailed discussions

### Advanced Features
- **Fullscreen Interface Modes**: Dedicated fullscreen views for both chat and graph visualization
- **Source Attribution**: Clickable links to original research papers and publications
- **Memory Management**: Conversation history with manual clearing capabilities
- **Responsive Design**: Modern React-based frontend with shadcn/ui components
- **Real-time Updates**: Live data visualization and instant query responses

## Architecture

### Backend Components
- **Enhanced Space Bio Chatbot**: Core conversational AI with Groq LLM integration
- **Knowledge Graph Manager**: Handles graph construction, querying, and relationship extraction
- **Vector Database Interface**: Manages semantic search and similarity matching
- **FastAPI Server**: RESTful API endpoints for all platform functionality

### Frontend Components
- **React Application**: Modern TypeScript-based single-page application
- **Chat Interface**: Conversational UI with markdown rendering and fullscreen support
- **Knowledge Graph View**: Interactive network visualization using vis.js
- **Search Filters**: Advanced filtering and query refinement tools

### Data Processing Pipeline
- **Text Processing**: Document parsing and content extraction
- **Knowledge Extraction**: Automated relationship and entity extraction
- **Vector Embeddings**: Sentence transformer-based semantic encoding
- **Graph Construction**: Automated knowledge graph building from research papers

## Technology Stack

### Backend Technologies
- **Python 3.11+**: Core runtime environment
- **FastAPI**: High-performance web framework
- **Groq**: Large language model API for natural language processing
- **Sentence Transformers**: Semantic embedding generation
- **Pinecone**: Vector database for similarity search
- **NetworkX**: Graph analysis and manipulation
- **PyVis**: Graph visualization generation

### Frontend Technologies
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality React component library
- **Vis.js**: Network visualization library

### Development Tools
- **UV Package Manager**: Fast Python dependency management
- **ESLint**: JavaScript/TypeScript code linting
- **Bun**: JavaScript runtime and package manager

## Installation

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- Git

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Space Bio"
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Configure environment variables**
   Edit `.env` file with your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENVIRONMENT=your_pinecone_environment
   ```

### Backend Installation

1. **Create Python virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize data**
   ```bash
   python kg_extractor.py
   python text_processor.py
   ```

### Frontend Installation

1. **Navigate to frontend directory**
   ```bash
   cd spacebioui
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

## Usage

### Development Mode

1. **Start the backend server**
   ```bash
   python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend development server**
   ```bash
   cd spacebioui
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Quick Start Script

Use the provided PowerShell script for streamlined development:
```bash
./start_dev.ps1
```

Options:
```bash
./start_dev.ps1 -ApiPort 9000    # Custom API port
./start_dev.ps1 -NoFrontend      # Backend only
./start_dev.ps1 -NoBackend       # Frontend only
```

## API Documentation

### Chat Endpoints
- `POST /chat` - Process chat queries with enhanced context
- `GET /chat/memory-status` - Retrieve conversation memory status
- `POST /chat/clear-memory` - Clear conversation history

### Knowledge Graph Endpoints
- `POST /kg/query` - Query the knowledge graph
- `GET /kg/stats` - Retrieve graph statistics
- `GET /kg/visualization` - Interactive graph visualization
- `GET /kg/data` - Sample triples and metadata

### System Endpoints
- `GET /` - Health check and system summary
- `GET /docs` - Interactive API documentation

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM services | Yes |
| `PINECONE_API_KEY` | Pinecone API key for vector search | Yes |
| `PINECONE_ENVIRONMENT` | Pinecone environment setting | Yes |
| `PINECONE_INDEX_NAME` | Pinecone index name | No (default: spacebio) |
| `EMBEDDING_MODEL` | Sentence transformer model | No (default: BAAI/bge-m3) |

### Frontend Configuration

Create `spacebioui/.env` for frontend settings:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Data Sources

The platform processes and analyzes research papers from various space biology domains:
- Microgravity effects on biological systems
- Space radiation and its biological impacts
- Plant growth and development in space environments
- Microbial behavior in space conditions
- Astronaut health and physiological adaptations

## Project Structure

```
├── api.py                           # FastAPI application and routes
├── enhanced_space_bio_chatbot.py    # Core chatbot functionality
├── kg_manager.py                    # Knowledge graph management
├── kg_visualizer.py                 # Graph visualization generation
├── kg_extractor.py                  # Knowledge extraction pipeline
├── text_processor.py               # Document processing utilities
├── requirements.txt                 # Python dependencies
├── start_dev.ps1                    # Development startup script
├── spacebioui/                      # React frontend application
│   ├── src/
│   │   ├── components/              # React components
│   │   ├── pages/                   # Application pages
│   │   ├── lib/                     # Utility functions
│   │   └── hooks/                   # Custom React hooks
│   ├── package.json                 # Node.js dependencies
│   └── vite.config.ts              # Vite configuration
└── lib/                             # Static assets and libraries
```

## Development Guidelines

### Code Standards
- Follow PEP 8 for Python code style
- Use TypeScript for all frontend development
- Maintain comprehensive test coverage
- Document all API endpoints and functions
- Follow semantic versioning for releases

### Testing

#### Backend Testing
```bash
python -m pytest tests/
```

#### Frontend Testing
```bash
cd spacebioui
npm run test
```

### Building for Production

#### Frontend Build
```bash
cd spacebioui
npm run build
```

#### Production Deployment
```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Chat returns 503 | Components not initialized | Check backend startup logs, verify API keys |
| CORS error | Backend origin mismatch | Confirm backend URL and CORS settings |
| Visualization blank | Graph HTML not generated | Ensure triples file exists, check `/kg/visualization` |
| 500 on `/chat` | Vector index or API error | Verify Pinecone index and API keys |

### API Testing

Test the API endpoints directly:
```bash
curl http://localhost:8000/
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"How does microgravity affect plants?"}'
```

## Security Considerations

### Production Deployment
- Restrict CORS origins to specific domains
- Implement rate limiting
- Add authentication for sensitive endpoints
- Use environment-specific API keys
- Enable structured logging
- Implement proper error handling

### API Key Management
- Never commit API keys to version control
- Use different keys for development and production
- Rotate keys regularly
- Monitor API usage and quotas

## Contributing

### Getting Started
1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Submit a pull request with detailed description

### Issue Reporting
- Use the GitHub issue tracker
- Provide detailed reproduction steps
- Include environment information
- Attach relevant logs or screenshots

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

This platform builds upon research and technologies from the space biology community, including NASA publications and academic research in microgravity effects on biological systems. Special thanks to the open-source community for the foundational technologies that make this platform possible.
