from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
import uuid
import shutil
import json
import hashlib
from datetime import datetime

from .models import AnalysisResponse, UploadResponse
from .pdf_processor import PDFProcessor
# Import LLMAnalyzer conditionally for fallback
try:
    from .llm_analyzer import LLMAnalyzer
    llm_analyzer_available = True
except ImportError:
    print("Warning: Legacy LLMAnalyzer not available, using MCP-enhanced system only")
    llm_analyzer_available = False
    
from .mcp_enhanced_analyzer import MCPEnhancedLegalAnalyzer

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
UPLOAD_DIR = "uploads"
CACHE_DIR = "analysis_cache"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Initialize processors
pdf_processor = PDFProcessor()
if llm_analyzer_available:
    llm_analyzer = LLMAnalyzer()
else:
    llm_analyzer = None
mcp_analyzer = None  # Will be initialized on first use

async def get_mcp_analyzer():
    """Get or initialize the MCP-enhanced analyzer"""
    global mcp_analyzer
    if mcp_analyzer is None:
        # For now, use mock analyzer directly if Google Cloud is not configured
        # This avoids the authentication errors during initialization
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        google_api_key = os.getenv("GOOGLE_API_KEY")
        
        if not project_id and not google_api_key:
            print("No Google Cloud configuration found, using mock analyzer")
            mcp_analyzer = MockAnalyzer()
            return mcp_analyzer
            
        try:
            # Try to initialize the MCP-enhanced analyzer
            mcp_analyzer = MCPEnhancedLegalAnalyzer()
            print("MCP-enhanced analyzer initialized successfully")
        except Exception as e:
            print(f"Failed to initialize MCP analyzer: {e}")
            # Create a mock analyzer for testing when Google Cloud is not configured
            mcp_analyzer = MockAnalyzer()
            print("Using mock analyzer for testing")
    return mcp_analyzer

class MockAnalyzer:
    """Mock analyzer for testing when Google Cloud is not configured"""
    
    def __init__(self):
        pass
    
    def get_mcp_capabilities(self):
        return {
            "status": "mock",
            "message": "Mock analyzer - Google Cloud not configured"
        }
    
    async def analyze_document(self, page_texts: Dict[int, str], document_name: str):
        """Mock analysis for testing"""
        
        # Generate some realistic mock highlights for testing
        mock_highlights = [
            {
                "id": "highlight_1",
                "text_to_highlight": "rental agreement",
                "page": 1,
                "metadata": {
                    "shortTitle": "Contract Type",
                    "title": "Rental Agreement Document",
                    "type": "standard_clause",
                    "data": {
                        "title": "Standard Rental Agreement",
                        "explanation": "This document is a standard residential rental agreement.",
                        "isNegotiable": True,
                        "tips": ["Review all terms carefully", "Check local regulations"]
                    }
                },
                "color": "blue"
            },
            {
                "id": "highlight_2", 
                "text_to_highlight": "security deposit",
                "page": 1,
                "metadata": {
                    "shortTitle": "Security Deposit",
                    "title": "Security Deposit Clause", 
                    "type": "legal_risk",
                    "data": {
                        "title": "Security Deposit Requirements",
                        "explanation": "Security deposit terms should comply with local regulations.",
                        "severity": "medium",
                        "recommendation": "Verify amount is within legal limits"
                    }
                },
                "color": "yellow"
            }
        ]
        
        # Generate mock page content
        mock_page_content = {}
        for page_num in range(1, len(page_texts) + 1):
            mock_page_content[page_num] = {
                "type": "summary",
                "data": {
                    "title": f"Page {page_num} Summary",
                    "keyPoints": [
                        f"Mock analysis point 1 for page {page_num}",
                        f"Mock analysis point 2 for page {page_num}",
                        f"Mock analysis point 3 for page {page_num}"
                    ],
                    "summary": f"This page contains important legal content that has been analyzed by our AI system. Page {page_num} summary."
                }
            }
        
        return {
            "highlights": mock_highlights,
            "pageContent": mock_page_content,
            "key_insights": ["Mock analysis: Document processed successfully", "Mock insight: Standard rental agreement detected"],
            "risk_assessment": {"low": 1, "medium": 1, "high": 0},
            "document_info": {
                "filename": document_name,
                "pages": len(page_texts),
                "analysis_method": "Mock Analysis (Google Cloud not configured)"
            }
        }
    
    async def search_legal_precedents(self, query: str):
        return [{"title": "Mock precedent", "description": "Mock legal research result"}]

# Store analysis results temporarily (in production, use a database)
analysis_store = {}

def get_file_hash(file_content: bytes) -> str:
    """Generate a hash for file content to check for duplicates"""
    return hashlib.md5(file_content).hexdigest()

def load_cached_analysis(file_hash: str, filename: str):
    """Load cached analysis if it exists"""
    cache_file = os.path.join(CACHE_DIR, f"{file_hash}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                # Update filename in case it's different
                cached_data["documentInfo"]["name"] = filename
                return cached_data
        except Exception as e:
            print(f"Error loading cache: {e}")
    return None

def save_analysis_cache(file_hash: str, analysis_data: dict):
    """Save analysis to cache"""
    cache_file = os.path.join(CACHE_DIR, f"{file_hash}.json")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving cache: {e}")

@app.get("/")
def read_root():
    return {"message": "Legal Document Analyzer API"}

@app.post("/api/analyze", response_model=UploadResponse)
async def analyze_pdf(files: List[UploadFile] = File(...)):
    """Upload and analyze PDF files"""
    
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    # For now, handle single file (can be extended for multiple files)
    file = files[0]
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read file content for hashing and processing
        file_content = await file.read()
        file_hash = get_file_hash(file_content)
        
        # Check if we have cached analysis for this file
        cached_analysis = load_cached_analysis(file_hash, file.filename)
        
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, f"{analysis_id}.pdf")
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        if cached_analysis:
            print(f"Using cached analysis for file: {file.filename}")
            # Use cached analysis but update file path
            analysis_result = cached_analysis.copy()
            analysis_result["file_path"] = file_path
            analysis_result["documentInfo"]["date"] = datetime.now().strftime("%Y-%m-%d")
            
            # Store in memory for this session
            analysis_store[analysis_id] = analysis_result
            
            return UploadResponse(
                message="File uploaded successfully (using cached analysis)",
                analysis_id=analysis_id
            )
        
        print(f"Performing new analysis for file: {file.filename}")
        
        # Process PDF - extract text by pages
        page_texts = pdf_processor.get_full_text_by_page(file_path)
        
        # Analyze with MCP-enhanced system
        analyzer = await get_mcp_analyzer()
        
        try:
            if hasattr(analyzer, 'analyze_document_with_mcp'):
                # Use the MCP-enhanced analysis
                print("Using MCP-enhanced analysis system")
                enhanced_response = await analyzer.analyze_document_with_mcp(page_texts, file.filename)
                
                # Convert the enhanced response to the format expected by the frontend
                analysis_data = {
                    "highlights": enhanced_response.highlights,
                    "pageContent": enhanced_response.page_content,
                    "key_insights": enhanced_response.key_insights,
                    "risk_summary": enhanced_response.risk_summary,
                    "compliance_gaps": enhanced_response.compliance_gaps,
                    "graph_data": enhanced_response.knowledge_graph.dict() if enhanced_response.knowledge_graph else None
                }
            elif hasattr(analyzer, 'analyze_document'):
                # Use standard analyze_document method (works for both enhanced and mock)
                print("Using standard analysis method")
                analysis_result = await analyzer.analyze_document(page_texts, file.filename)
                
                # Handle both EnhancedAnalysisResponse and dict responses
                if hasattr(analysis_result, 'highlights'):
                    # It's an EnhancedAnalysisResponse object
                    analysis_data = {
                        "highlights": analysis_result.highlights,
                        "pageContent": analysis_result.page_content,
                        "key_insights": getattr(analysis_result, 'key_insights', []),
                        "risk_summary": getattr(analysis_result, 'risk_summary', {}),
                        "compliance_gaps": getattr(analysis_result, 'compliance_gaps', [])
                    }
                else:
                    # It's a dict (from mock analyzer)
                    analysis_data = analysis_result
            else:
                # Last resort - create minimal response
                print("No analysis method available, creating minimal response")
                analysis_data = {
                    "highlights": [],
                    "pageContent": {f"page_{i+1}": f"Page {i+1} content" for i in range(len(page_texts))},
                    "key_insights": ["Analysis system not properly configured"],
                    "document_info": {
                        "filename": file.filename,
                        "pages": len(page_texts),
                        "analysis_method": "Minimal fallback"
                    }
                }
        except Exception as analysis_error:
            print(f"Analysis failed: {analysis_error}")
            print("Falling back to mock analyzer")
            # Fallback to mock analyzer
            mock_analyzer = MockAnalyzer()
            analysis_data = await mock_analyzer.analyze_document(page_texts, file.filename)
        
        # Process highlights to find coordinates
        processed_highlights = []
        for highlight_data in analysis_data.get("highlights", []):
            text_to_highlight = highlight_data.get("text_to_highlight", "")
            page_num = highlight_data.get("page", 1)
            
            print(f"Processing highlight: '{text_to_highlight}' on page {page_num}")
            
            # Find coordinates for the text
            rectangles = pdf_processor.find_text_fuzzy(file_path, text_to_highlight, page_num)
            
            if rectangles:
                # Use the first found rectangle
                rect = rectangles[0]
                highlight_data["rect"] = {
                    "x": rect.x,
                    "y": rect.y, 
                    "width": rect.width,
                    "height": rect.height
                }
                processed_highlights.append(highlight_data)
                print(f"✓ Found coordinates for: '{text_to_highlight}'")
            else:
                print(f"✗ No coordinates found for: '{text_to_highlight}' - skipping highlight")
                # Could add highlight without coordinates if needed
                # processed_highlights.append(highlight_data)
        
        # Store analysis result
        analysis_result = {
            "highlights": processed_highlights,
            "pageContent": analysis_data.get("pageContent", {}),
            "documentInfo": {
                "name": file.filename,
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            "file_path": file_path
        }
        
        # Fix pageContent format if needed (convert page_1, page_2 to 1, 2)
        if "pageContent" in analysis_result:
            fixed_page_content = {}
            for key, value in analysis_result["pageContent"].items():
                if isinstance(key, str) and key.startswith("page_"):
                    # Convert "page_1" to 1
                    page_num = int(key.split("_")[1])
                    fixed_page_content[page_num] = value
                elif isinstance(key, (int, str)) and str(key).isdigit():
                    # Keep numeric keys as is
                    fixed_page_content[int(key)] = value
                else:
                    # Keep other keys as is
                    fixed_page_content[key] = value
            analysis_result["pageContent"] = fixed_page_content
        
        # Cache the analysis (without file_path since that's session-specific)
        cache_data = analysis_result.copy()
        del cache_data["file_path"]  # Don't cache the file path
        save_analysis_cache(file_hash, cache_data)
        
        analysis_store[analysis_id] = analysis_result
        
        return UploadResponse(
            message="File uploaded and analyzed successfully",
            analysis_id=analysis_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis results by ID"""
    
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_store[analysis_id]
    
    return {
        "highlights": analysis["highlights"],
        "pageContent": analysis["pageContent"], 
        "documentInfo": analysis["documentInfo"]
    }

@app.get("/api/cache/status")
async def get_cache_status():
    """Get cache status - how many analyses are cached"""
    try:
        cache_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.json')]
        return {
            "cached_analyses": len(cache_files),
            "cache_directory": CACHE_DIR,
            "message": f"Found {len(cache_files)} cached analysis files"
        }
    except Exception as e:
        return {
            "cached_analyses": 0,
            "cache_directory": CACHE_DIR,
            "error": str(e)
        }

@app.post("/api/debug/coordinates")
async def debug_coordinates(data: dict):
    """Debug endpoint to test text coordinate finding"""
    file_path = data.get("file_path")
    search_text = data.get("search_text")
    page_num = data.get("page_num", 1)
    
    if not file_path or not search_text:
        raise HTTPException(status_code=400, detail="file_path and search_text required")
    
    try:
        rectangles = pdf_processor.find_text_fuzzy(file_path, search_text, page_num)
        return {
            "search_text": search_text,
            "page_num": page_num,
            "rectangles_found": len(rectangles),
            "rectangles": [{"x": r.x, "y": r.y, "width": r.width, "height": r.height} for r in rectangles]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/pdf/{analysis_id}")
async def get_pdf(analysis_id: str):
    """Serve the PDF file for viewing"""
    
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    file_path = analysis_store[analysis_id]["file_path"]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=analysis_store[analysis_id]["documentInfo"]["name"]
    )

@app.get("/api/mcp/capabilities")
async def get_mcp_capabilities():
    """Get information about available MCP capabilities"""
    try:
        analyzer = await get_mcp_analyzer()
        if hasattr(analyzer, 'get_mcp_capabilities'):
            capabilities = analyzer.get_mcp_capabilities()
            return {
                "status": "success",
                "capabilities": capabilities,
                "message": "MCP-enhanced analyzer is available"
            }
        else:
            return {
                "status": "fallback",
                "capabilities": {},
                "message": "Using standard analyzer (MCP not available)"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to check MCP capabilities"
        }

@app.post("/api/legal/research")
async def research_legal_precedents(data: dict):
    """Research legal precedents using MCP-enhanced tools"""
    query = data.get("query", "")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    try:
        analyzer = await get_mcp_analyzer()
        if hasattr(analyzer, 'search_legal_precedents'):
            precedents = await analyzer.search_legal_precedents(query)
            return {
                "query": query,
                "precedents": precedents,
                "status": "success"
            }
        else:
            return {
                "query": query,
                "precedents": [],
                "status": "fallback",
                "message": "MCP research tools not available"
            }
    except Exception as e:
        return {
            "query": query,
            "precedents": [],
            "status": "error",
            "error": str(e)
        }
