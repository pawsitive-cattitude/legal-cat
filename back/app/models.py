from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum

class HighlightColor(str, Enum):
    RED = "red"
    YELLOW = "yellow" 
    BLUE = "blue"

class HighlightType(str, Enum):
    LEGAL_RISK = "legal_risk"
    COMPLIANCE_ISSUE = "compliance_issue"
    STANDARD_CLAUSE = "standard_clause"
    CUSTOM = "custom"

class PageContentType(str, Enum):
    INTRO = "intro"
    NOTICE = "notice"
    RESOURCES = "resources"
    KEY_POINTS = "key_points"
    SUMMARY = "summary"
    CUSTOM = "custom"

class Rectangle(BaseModel):
    x: float
    y: float
    width: float
    height: float

class HighlightMetadata(BaseModel):
    shortTitle: str
    title: str
    type: HighlightType
    data: Dict[str, Any]

class Highlight(BaseModel):
    id: str
    page: int
    rect: Rectangle
    color: HighlightColor
    metadata: HighlightMetadata

class PageContent(BaseModel):
    type: PageContentType
    data: Dict[str, Any]

class DocumentInfo(BaseModel):
    name: str
    date: str

class AnalysisResponse(BaseModel):
    highlights: List[Highlight]
    pageContent: Dict[int, PageContent]
    documentInfo: DocumentInfo
    
class UploadResponse(BaseModel):
    message: str
    analysis_id: str
    
class TextBlock(BaseModel):
    text: str
    page: int
    bbox: List[float]  # [x0, y0, x1, y1]
