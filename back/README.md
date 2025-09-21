# Legal Cat Backend

Advanced legal document analysis system using Google's Agent Development Kit (ADK), Model Context Protocol (MCP), and RAG technology.

## Features

- **Multi-Agent Analysis**: Specialized AI agents for different legal analysis tasks
- **Graph-Ready RAG**: Retrieval-Augmented Generation with knowledge graph capabilities
- **MCP Integration**: Extensible tool system using Model Context Protocol
- **Real-time Processing**: Fast PDF analysis with coordinate-based highlighting
- **Scalable Architecture**: Built on Google Cloud with Vertex AI

## Architecture

The system consists of several key components:

1. **Google ADK Multi-Agent System**: Specialized agents for legal analysis
   - Legal Context Agent: Document classification and jurisdiction analysis
   - Clause Analysis Agent: Contract clause identification and analysis
   - Risk Assessment Agent: Legal risk identification and scoring
   - Compliance Agent: Regulatory compliance checking
   - Research Agent: Legal precedent and case law research

2. **RAG System**: Vertex AI-powered retrieval with graph structure
   - Legal document chunking with metadata
   - Vector embeddings for semantic search
   - Graph relationships between legal concepts

3. **MCP Server**: Standardized tool interface
   - PDF text extraction
   - Document indexing
   - Knowledge graph building
   - External legal database integration

## Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Set Up Google Cloud

Follow the detailed setup guide: [GOOGLE_CLOUD_SETUP.md](./GOOGLE_CLOUD_SETUP.md)

Quick setup:
```bash
# Copy environment template
cp .env.example .env

# Edit with your Google Cloud project details
# GOOGLE_CLOUD_PROJECT=your-project-id
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### 3. Run the Server

```bash
uv run uvicorn app.main:app --reload
```

## API Endpoints

### Core Analysis
- `POST /api/analyze` - Upload and analyze PDF documents
- `GET /api/analysis/{analysis_id}` - Retrieve analysis results
- `GET /api/pdf/{analysis_id}` - Serve PDF files

### MCP Enhanced Features
- `GET /api/mcp/capabilities` - Check MCP tool availability
- `POST /api/legal/research` - Research legal precedents

### Utilities
- `GET /api/cache/status` - Check analysis cache status
- `POST /api/debug/coordinates` - Debug text coordinate finding

## Environment Variables

See `.env.example` for all available configuration options:

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Optional
GOOGLE_API_KEY=your-legacy-api-key  # For fallback only
CHROMA_PERSIST_DIRECTORY=./chroma_db
LEGAL_DOCS_PATH=/tmp/legal_docs
```

## Development

### Project Structure

```
app/
├── main.py                    # FastAPI application
├── models.py                  # Pydantic models
├── pdf_processor.py           # PDF text extraction
├── graph_models.py            # Knowledge graph data models
├── rag_system.py              # RAG implementation
├── mcp_server.py              # MCP server implementation
├── agent_analyzer.py          # Multi-agent system
├── mcp_enhanced_analyzer.py   # MCP-integrated analyzer
└── database.py                # Database utilities
```

### Running Tests

```bash
# Run system tests
uv run python test_system.py

# Test MCP capabilities
uv run python -c "
from app.mcp_enhanced_analyzer import MCPEnhancedLegalAnalyzer
import asyncio
import json

async def test():
    analyzer = MCPEnhancedLegalAnalyzer()
    print(json.dumps(analyzer.get_mcp_capabilities(), indent=2))

asyncio.run(test())
"
```

### Adding New Agents

1. Define the agent in `agent_analyzer.py`:
```python
self.my_agent = LlmAgent(
    name="my_legal_specialist",
    model="gemini-2.0-flash",
    instruction="Your specialized instructions...",
    tools=[relevant_tools]
)
```

2. Add to the coordinator logic
3. Update the analysis response format

### Adding MCP Tools

1. Implement tools in `mcp_server.py`
2. Register in the MCP toolset
3. Configure in agent tool lists

## Deployment

### Local Development
```bash
uv run uvicorn app.main:app --reload
```

### Docker
```bash
docker build -t legal-cat-backend .
docker run -p 8000:8000 legal-cat-backend
```

### Google Cloud Run
```bash
gcloud run deploy legal-cat-backend \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

## Monitoring and Debugging

### Health Checks
- Server health: `GET /`
- MCP status: `GET /api/mcp/capabilities`
- Cache status: `GET /api/cache/status`

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Performance
- Analysis results are cached by file hash
- ChromaDB provides fast vector similarity search
- Async processing for multi-agent coordination

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the [troubleshooting guide](./GOOGLE_CLOUD_SETUP.md#troubleshooting)
- Review the [API documentation](http://localhost:8000/docs)
- Open an issue on GitHub
