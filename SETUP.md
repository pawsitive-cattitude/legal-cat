# Legal Document Analyzer Setup Guide

## 🚀 Complete Flow Overview

**Upload PDF → AI Analysis → Interactive Viewing**

1. User uploads PDF on `/analyze`
2. Backend extracts text and coordinates
3. LLM analyzes content and identifies issues
4. Backend finds coordinates for highlighted text
5. User views results on `/analyze/view` with interactive highlights and tooltips

## 🛠️ Backend Setup

1. **Install Dependencies:**

```bash
cd back
uv sync  # This will install all dependencies from pyproject.toml
```

2. **Set up Environment:**

```bash
# Create .env file in /back directory with:
OPENAI_API_KEY=your_openai_api_key_here
```

3. **Start Backend Server:**

```bash
cd back
uv run uvicorn app.main:app --reload
```

Backend runs on: http://localhost:8000

## 🎯 Frontend Setup

1. **Install Dependencies (if needed):**

```bash
cd front
bun install
```

2. **Start Frontend:**

```bash
cd front
bun run dev
```

Frontend runs on: http://localhost:3000

## 📊 API Endpoints

- `POST /api/analyze` - Upload PDF and get analysis
- `GET /api/analysis/{id}` - Get analysis results
- `GET /api/pdf/{id}` - Serve PDF file for viewing

## 🔄 Complete Flow

### 1. Upload (`/analyze`)

- User drags/drops PDF file
- File uploaded to backend with progress tracking
- Backend processes PDF → extracts text → sends to LLM
- LLM returns structured analysis data
- Backend finds coordinates for highlights
- Returns analysis ID

### 2. View (`/analyze/view?id=xxx`)

- Fetch analysis data using analysis ID
- Convert LLM data to React components using factory functions
- Display PDF with interactive highlights and page content
- Hover over highlights → show tooltips
- Scroll pages → show relevant content

## 🧠 LLM Output Structure

The LLM generates simple structured data:

```json
{
  "highlights": [
    {
      "id": "unique-id",
      "page": 1,
      "text_to_highlight": "exact text from PDF",
      "color": "red",
      "metadata": {
        "shortTitle": "GDPR Issue",
        "title": "Data Collection Risk",
        "type": "legal_risk",
        "data": {
          "title": "Data Collection Risk",
          "explanation": "This clause allows...",
          "severity": "high",
          "article": "GDPR Art. 6(1)(a)",
          "recommendation": "Add explicit consent..."
        }
      }
    }
  ],
  "pageContent": {
    "1": {
      "type": "intro",
      "data": {
        "title": "Analysis Complete",
        "description": "Found 3 issues requiring attention"
      }
    }
  }
}
```

## 🎨 Component Types Available

### Highlight Types:

- `legal_risk` - Legal violations/risks with severity
- `compliance_issue` - Regulatory compliance problems
- `standard_clause` - Standard but notable clauses
- `custom` - Simple explanations

### Page Content Types:

- `intro` - Welcome/introduction sections
- `notice` - Alerts/warnings with action buttons
- `key_points` - Bullet point summaries
- `resources` - Links, downloads, references
- `summary` - Multi-section summaries

## 🚨 Troubleshooting

1. **Backend Import Errors**: Run `uv sync` to install dependencies
2. **PDF Processing Issues**: Ensure PyMuPDF is installed correctly
3. **LLM Errors**: Check OpenAI API key in .env file
4. **CORS Issues**: Backend configured for localhost:3000
5. **File Upload Fails**: Check upload directory permissions

## 🔧 Development Notes

- Uses PyMuPDF for PDF text extraction and coordinate finding
- Fuzzy text matching for highlight positioning
- Component factory pattern for reusable UI elements
- TypeScript types for full type safety
- Real-time upload progress tracking
- Temporary in-memory storage (use database in production)

## 🎯 Next Steps for Production

1. Replace in-memory storage with database (PostgreSQL/MongoDB)
2. Add user authentication
3. Implement file cleanup/retention policies
4. Add support for multiple LLM providers
5. Add batch processing for multiple documents
6. Implement caching for common analyses
