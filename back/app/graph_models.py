from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum
import uuid

class NodeType(str, Enum):
    """Types of nodes in the legal knowledge graph"""
    DOCUMENT = "document"
    CLAUSE = "clause"
    LEGAL_CONCEPT = "legal_concept"
    RISK = "risk"
    COMPLIANCE_REQUIREMENT = "compliance_requirement"
    TERM = "term"
    PARTY = "party"
    OBLIGATION = "obligation"
    RIGHT = "right"

class EdgeType(str, Enum):
    """Types of relationships between nodes"""
    CONTAINS = "contains"
    REFERENCES = "references"
    IMPLEMENTS = "implements"
    CONFLICTS_WITH = "conflicts_with"
    DEPENDS_ON = "depends_on"
    DEFINES = "defines"
    APPLIES_TO = "applies_to"
    CREATES_RISK = "creates_risk"
    MITIGATES = "mitigates"
    SIMILAR_TO = "similar_to"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class GraphNode(BaseModel):
    """A node in the legal knowledge graph"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: NodeType
    label: str
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    risk_level: Optional[RiskLevel] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    page_number: Optional[int] = None
    document_id: Optional[str] = None
    
class GraphEdge(BaseModel):
    """An edge in the legal knowledge graph"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str  # Node ID
    target: str  # Node ID
    relationship: EdgeType
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LegalKnowledgeGraph(BaseModel):
    """Complete legal knowledge graph for a document or corpus"""
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def add_node(self, node: GraphNode) -> str:
        """Add a node and return its ID"""
        self.nodes.append(node)
        return node.id
        
    def add_edge(self, edge: GraphEdge) -> str:
        """Add an edge and return its ID"""
        self.edges.append(edge)
        return edge.id
        
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
        
    def get_neighbors(self, node_id: str) -> List[GraphNode]:
        """Get all neighboring nodes"""
        neighbors = []
        for edge in self.edges:
            if edge.source == node_id:
                target = self.get_node(edge.target)
                if target:
                    neighbors.append(target)
            elif edge.target == node_id:
                source = self.get_node(edge.source)
                if source:
                    neighbors.append(source)
        return neighbors

class DocumentChunk(BaseModel):
    """A chunk of a legal document with embeddings and metadata"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    embedding: Optional[List[float]] = None
    document_id: str
    page_number: int
    chunk_index: int
    start_char: int
    end_char: int
    
    # Legal-specific metadata
    clause_type: Optional[str] = None
    legal_concepts: List[str] = Field(default_factory=list)
    mentioned_parties: List[str] = Field(default_factory=list)
    risk_indicators: List[str] = Field(default_factory=list)
    compliance_requirements: List[str] = Field(default_factory=list)
    
    # Graph connectivity hints
    related_chunks: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    
class RAGSearchResult(BaseModel):
    """Result from RAG search with graph context"""
    chunk: DocumentChunk
    similarity_score: float
    graph_context: Optional[LegalKnowledgeGraph] = None
    related_concepts: List[str] = Field(default_factory=list)

class EnhancedAnalysisResponse(BaseModel):
    """Enhanced analysis response with graph data"""
    document_id: str
    document_name: str
    
    # Traditional analysis results
    highlights: List[Any] = Field(default_factory=list)
    page_content: Dict[str, Any] = Field(default_factory=dict)
    document_info: Dict[str, Any] = Field(default_factory=dict)
    
    # New graph-based results
    knowledge_graph: LegalKnowledgeGraph
    key_insights: List[str] = Field(default_factory=list)
    risk_summary: Dict[RiskLevel, int] = Field(default_factory=dict)
    compliance_gaps: List[str] = Field(default_factory=list)
    
    # RAG-enhanced context
    relevant_precedents: List[RAGSearchResult] = Field(default_factory=list)
    similar_clauses: List[RAGSearchResult] = Field(default_factory=list)