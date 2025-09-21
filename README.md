# Legal Cat 🐱⚖️

Advanced legal document analysis system powered by Google's Agent Development Kit (ADK), Model Context Protocol (MCP), and graph-ready RAG technology.

## ✨ Features

- **🤖 Multi-Agent Analysis**: Specialized AI agents for comprehensive legal document analysis
- **🕸️ Graph-Ready RAG**: Knowledge graphs showing relationships between legal clauses and concepts
- **🔧 MCP Integration**: Extensible tool system using Model Context Protocol
- **📍 Precise Highlighting**: Coordinate-based PDF highlighting with fuzzy text matching
- **⚡ Real-time Processing**: Fast analysis with intelligent caching
- **☁️ Google Cloud Integration**: Powered by Vertex AI and Google ADK

## 🏗️ Architecture

### Backend (Python + FastAPI)
- **Google ADK Multi-Agent System**: 5 specialized legal analysis agents
- **Vertex AI RAG**: Advanced retrieval with legal metadata
- **MCP Server**: Standardized tool interface for extensibility
- **ChromaDB**: Local vector storage for development

### Frontend (Next.js + TypeScript)
- Interactive PDF viewer with highlighting
- Real-time analysis results
- Graph visualization of legal relationships
- Responsive modern UI

## 🚀 Quick Start

### Prerequisites
- **uv** (Python package manager)
- **bun** (JavaScript package manager) 
- **Google Cloud Project** with Vertex AI enabled

### 1. Backend Setup

```bash
cd back/
./setup.sh  # Automated setup script
```

Or manually:
```bash
cd back/
uv sync
cp .env.example .env
# Edit .env with your Google Cloud details
uv run uvicorn app.main:app --reload
```

### 2. Frontend Setup

```bash
cd front/
bun install
bun dev
```

### 3. Google Cloud Setup

Follow the detailed guide: [`back/GOOGLE_CLOUD_SETUP.md`](./back/GOOGLE_CLOUD_SETUP.md)

## 📚 Documentation

- **Backend**: [`back/README.md`](./back/README.md) - API documentation and architecture
- **Google Cloud Setup**: [`back/GOOGLE_CLOUD_SETUP.md`](./back/GOOGLE_CLOUD_SETUP.md) - Authentication and deployment
- **Frontend**: [`front/README.md`](./front/README.md) - UI components and styling

## 🔗 API Endpoints

- `POST /api/analyze` - Upload and analyze legal documents
- `GET /api/mcp/capabilities` - Check MCP tool availability  
- `POST /api/legal/research` - Research legal precedents
- `GET /docs` - Interactive API documentation

## 🛠️ Development

### Technologies Used

**Backend:**
- Google Agent Development Kit (ADK)
- Model Context Protocol (MCP)
- Vertex AI & ChromaDB
- FastAPI & Pydantic
- PyMuPDF for PDF processing

**Frontend:**
- Next.js 14 with App Router
- TypeScript & Tailwind CSS
- PDF.js for document viewing
- D3.js for graph visualization

### Project Structure

```
legal-cat/
├── back/           # Python backend
│   ├── app/        # FastAPI application
│   ├── .env.example
│   └── setup.sh    # Automated setup
├── front/          # Next.js frontend
│   ├── src/        # React components
│   └── public/     # Static assets
└── README.md       # This file
```

## 🧪 Testing

```bash
# Backend tests
cd back/
uv run python test_system.py

# Frontend tests  
cd front/
bun test
```

## 🚀 Deployment

### Local Development
```bash
# Backend
cd back/ && uv run uvicorn app.main:app --reload

# Frontend  
cd front/ && bun dev
```

### Production
- **Backend**: Google Cloud Run
- **Frontend**: Vercel or static hosting
- **Authentication**: Google Cloud IAM

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

Built with ❤️ using **uv** and **bun** for the best developer experience.