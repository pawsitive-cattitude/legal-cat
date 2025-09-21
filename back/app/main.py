from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import uuid
import shutil
import json
import hashlib
from datetime import datetime

from .models import AnalysisResponse, UploadResponse
from .pdf_processor import PDFProcessor
from .llm_analyzer import LLMAnalyzer

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
llm_analyzer = LLMAnalyzer()

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
        
        # Analyze with LLM
        # Use mock analysis for now (comment out for real LLM)
        # analysis_data = llm_analyzer.create_mock_analysis(page_texts, file.filename)
        # For real LLM analysis, uncomment the line below and comment the line above:
        analysis_data = llm_analyzer.analyze_document(page_texts, file.filename)
        
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
