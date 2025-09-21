import os
import logging
from typing import List, Dict, Optional, Any
from google.cloud import aiplatform
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag
import chromadb
from chromadb.config import Settings
import uuid
from .graph_models import DocumentChunk, RAGSearchResult, LegalKnowledgeGraph, GraphNode, NodeType
from .pdf_processor import PDFProcessor
import json
import re

logger = logging.getLogger(__name__)

class LegalRAGSystem:
    """
    Advanced RAG system for legal documents using Vertex AI RAG Engine
    with graph-ready structure for relationship mapping
    """
    
    def __init__(self, 
                 project_id: str,
                 location: str = "us-central1",
                 rag_corpus_name: Optional[str] = None):
        """
        Initialize the Legal RAG system
        
        Args:
            project_id: Google Cloud project ID
            location: Google Cloud location
            rag_corpus_name: Name of existing RAG corpus, if None will create new
        """
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        
        # Initialize local vector store for development/testing
        self.chroma_client = chromadb.Client(Settings(
            persist_directory="./vector_store",
            is_persistent=True
        ))
        
        self.collection = self.chroma_client.get_or_create_collection(
            name="legal_documents",
            metadata={"description": "Legal document chunks with graph metadata"}
        )
        
        # RAG corpus setup
        self.rag_corpus = None
        self.rag_retrieval_tool = None
        if rag_corpus_name:
            self._setup_vertex_rag(rag_corpus_name)
        
        self.pdf_processor = PDFProcessor()
        
    def _setup_vertex_rag(self, corpus_name: str):
        """Setup Vertex AI RAG corpus"""
        try:
            self.rag_corpus = f"projects/{self.project_id}/locations/{self.location}/ragCorpora/{corpus_name}"
            
            self.rag_retrieval_tool = VertexAiRagRetrieval(
                name='retrieve_legal_documents',
                description='Retrieve relevant legal documents and clauses from the knowledge base',
                rag_resources=[
                    rag.RagResource(rag_corpus=self.rag_corpus)
                ],
                similarity_top_k=10,
                vector_distance_threshold=0.6,
            )
            logger.info(f"Connected to Vertex AI RAG corpus: {corpus_name}")
        except Exception as e:
            logger.error(f"Failed to setup Vertex AI RAG: {e}")
            
    def _extract_legal_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract legal-specific metadata from text chunk
        This is where we identify legal concepts for graph building
        """
        metadata = {
            "clause_type": None,
            "legal_concepts": [],
            "mentioned_parties": [],
            "risk_indicators": [],
            "compliance_requirements": []
        }
        
        # Clause type detection patterns
        clause_patterns = {
            "confidentiality": r"\b(confidential|non-disclosure|proprietary|trade secret)\b",
            "liability": r"\b(liable|liability|damages|indemnif|limitation of liability)\b",
            "termination": r"\b(terminate|termination|end|expire|dissolution)\b",
            "payment": r"\b(payment|compensation|fee|salary|remuneration)\b",
            "intellectual_property": r"\b(intellectual property|copyright|patent|trademark|ip)\b",
            "governing_law": r"\b(governing law|jurisdiction|venue|applicable law)\b",
            "force_majeure": r"\b(force majeure|act of god|unforeseeable)\b",
            "dispute_resolution": r"\b(dispute|arbitration|mediation|litigation)\b"
        }
        
        text_lower = text.lower()
        
        # Detect clause types
        for clause_type, pattern in clause_patterns.items():
            if re.search(pattern, text_lower):
                metadata["clause_type"] = clause_type
                break
                
        # Extract legal concepts
        legal_concepts = [
            "privacy", "gdpr", "compliance", "audit", "security", "breach",
            "contract", "agreement", "license", "warranty", "representation",
            "obligation", "right", "duty", "responsibility"
        ]
        
        for concept in legal_concepts:
            if concept in text_lower:
                metadata["legal_concepts"].append(concept)
                
        # Extract party references
        party_patterns = [
            r"\b(company|corporation|llc|inc|ltd|party|parties)\b",
            r"\b(client|customer|vendor|supplier|contractor)\b",
            r"\b(employee|employer|worker|staff)\b"
        ]
        
        for pattern in party_patterns:
            matches = re.findall(pattern, text_lower)
            metadata["mentioned_parties"].extend(matches)
            
        # Risk indicators
        risk_patterns = [
            "shall not", "prohibited", "penalty", "breach", "violation",
            "unlimited liability", "personal guarantee", "indemnification"
        ]
        
        for risk in risk_patterns:
            if risk in text_lower:
                metadata["risk_indicators"].append(risk)
                
        # Compliance requirements
        compliance_patterns = [
            "must comply", "shall ensure", "required to", "mandatory",
            "audit", "report", "documentation", "record keeping"
        ]
        
        for compliance in compliance_patterns:
            if compliance in text_lower:
                metadata["compliance_requirements"].append(compliance)
                
        return metadata
        
    def _chunk_document(self, document_text: str, document_id: str, page_number: int) -> List[DocumentChunk]:
        """
        Intelligent chunking of legal documents
        Tries to preserve clause boundaries and legal concepts
        """
        chunks = []
        
        # Split by double newlines first (paragraph boundaries)
        paragraphs = document_text.split('\n\n')
        
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for paragraph in paragraphs:
            # If adding this paragraph would make chunk too long, save current chunk
            if len(current_chunk) + len(paragraph) > 1000 and current_chunk:
                chunk_end = current_start + len(current_chunk)
                
                # Extract metadata for this chunk
                metadata = self._extract_legal_metadata(current_chunk)
                
                chunk = DocumentChunk(
                    content=current_chunk.strip(),
                    document_id=document_id,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    start_char=current_start,
                    end_char=chunk_end,
                    **metadata
                )
                chunks.append(chunk)
                
                current_chunk = paragraph
                current_start = chunk_end
                chunk_index += 1
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                    
        # Add final chunk
        if current_chunk:
            metadata = self._extract_legal_metadata(current_chunk)
            chunk = DocumentChunk(
                content=current_chunk.strip(),
                document_id=document_id,
                page_number=page_number,
                chunk_index=chunk_index,
                start_char=current_start,
                end_char=current_start + len(current_chunk),
                **metadata
            )
            chunks.append(chunk)
            
        return chunks
        
    def index_document(self, file_path: str) -> str:
        """
        Index a legal document for RAG retrieval
        Returns document_id
        """
        try:
            # Extract text from PDF
            page_texts = self.pdf_processor.extract_text_by_page(file_path)
            document_id = str(uuid.uuid4())
            
            all_chunks = []
            
            # Process each page
            for page_num, text in page_texts.items():
                if text.strip():  # Only process non-empty pages
                    page_chunks = self._chunk_document(text, document_id, page_num)
                    all_chunks.extend(page_chunks)
                    
            # Store chunks in vector database
            for chunk in all_chunks:
                # For ChromaDB storage
                self.collection.add(
                    documents=[chunk.content],
                    metadatas=[{
                        "document_id": chunk.document_id,
                        "page_number": chunk.page_number,
                        "chunk_index": chunk.chunk_index,
                        "clause_type": chunk.clause_type,
                        "legal_concepts": json.dumps(chunk.legal_concepts),
                        "risk_indicators": json.dumps(chunk.risk_indicators),
                        "compliance_requirements": json.dumps(chunk.compliance_requirements)
                    }],
                    ids=[chunk.id]
                )
                
            logger.info(f"Indexed document {document_id} with {len(all_chunks)} chunks")
            return document_id
            
        except Exception as e:
            logger.error(f"Failed to index document: {e}")
            raise
            
    def search(self, query: str, document_id: Optional[str] = None, top_k: int = 5) -> List[RAGSearchResult]:
        """
        Search for relevant chunks using vector similarity
        """
        try:
            # Build filter for specific document if requested
            where_filter = {}
            if document_id:
                where_filter["document_id"] = document_id
                
            # Search in ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter if where_filter else None
            )
            
            search_results = []
            
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Reconstruct DocumentChunk
                    chunk = DocumentChunk(
                        id=results['ids'][0][i],
                        content=doc,
                        document_id=metadata['document_id'],
                        page_number=metadata['page_number'],
                        chunk_index=metadata['chunk_index'],
                        clause_type=metadata.get('clause_type'),
                        legal_concepts=json.loads(metadata.get('legal_concepts', '[]')),
                        risk_indicators=json.loads(metadata.get('risk_indicators', '[]')),
                        compliance_requirements=json.loads(metadata.get('compliance_requirements', '[]'))
                    )
                    
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    similarity_score = 1.0 - distance
                    
                    search_results.append(RAGSearchResult(
                        chunk=chunk,
                        similarity_score=similarity_score,
                        related_concepts=chunk.legal_concepts
                    ))
                    
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return []
            
    def get_related_chunks(self, chunk_id: str, relationship_type: str = "similar") -> List[RAGSearchResult]:
        """
        Find chunks related to a given chunk
        This is crucial for building the knowledge graph
        """
        try:
            # Get the original chunk
            chunk_result = self.collection.get(ids=[chunk_id])
            if not chunk_result['documents']:
                return []
                
            original_content = chunk_result['documents'][0]
            original_metadata = chunk_result['metadatas'][0]
            
            # Search for similar content
            similar_results = self.search(original_content, top_k=10)
            
            # Filter out the original chunk and apply relationship logic
            related = []
            for result in similar_results:
                if result.chunk.id != chunk_id:
                    # Add relationship-specific logic here
                    if relationship_type == "similar" and result.similarity_score > 0.7:
                        related.append(result)
                    elif relationship_type == "references" and any(
                        concept in result.chunk.legal_concepts 
                        for concept in json.loads(original_metadata.get('legal_concepts', '[]'))
                    ):
                        related.append(result)
                        
            return related[:5]  # Limit to top 5 related chunks
            
        except Exception as e:
            logger.error(f"Failed to find related chunks: {e}")
            return []
            
    def build_document_graph(self, document_id: str) -> LegalKnowledgeGraph:
        """
        Build a knowledge graph for a specific document
        This creates the graph structure your frontend can visualize
        """
        graph = LegalKnowledgeGraph()
        
        try:
            # Get all chunks for this document
            chunks_result = self.collection.get(
                where={"document_id": document_id}
            )
            
            if not chunks_result['documents']:
                return graph
                
            # Create nodes for each chunk and legal concept
            chunk_nodes = {}
            concept_nodes = {}
            
            for i, (doc, metadata) in enumerate(zip(chunks_result['documents'], chunks_result['metadatas'])):
                chunk_id = chunks_result['ids'][i]
                
                # Create chunk node
                chunk_node = GraphNode(
                    id=f"chunk_{chunk_id}",
                    type=NodeType.CLAUSE,
                    label=f"Clause {metadata['chunk_index']} (Page {metadata['page_number']})",
                    content=doc[:200] + "..." if len(doc) > 200 else doc,
                    page_number=metadata['page_number'],
                    document_id=document_id,
                    metadata={
                        "clause_type": metadata.get('clause_type'),
                        "full_content": doc
                    }
                )
                graph.add_node(chunk_node)
                chunk_nodes[chunk_id] = chunk_node.id
                
                # Create concept nodes and relationships
                legal_concepts = json.loads(metadata.get('legal_concepts', '[]'))
                for concept in legal_concepts:
                    concept_key = f"concept_{concept}"
                    if concept_key not in concept_nodes:
                        concept_node = GraphNode(
                            id=concept_key,
                            type=NodeType.LEGAL_CONCEPT,
                            label=concept.replace('_', ' ').title(),
                            metadata={"concept_type": concept}
                        )
                        graph.add_node(concept_node)
                        concept_nodes[concept_key] = concept_node.id
                        
                    # Create edge from chunk to concept
                    from .graph_models import GraphEdge, EdgeType
                    edge = GraphEdge(
                        source=chunk_node.id,
                        target=concept_nodes[concept_key],
                        relationship=EdgeType.IMPLEMENTS,
                        confidence=0.8
                    )
                    graph.add_edge(edge)
                    
            # Find relationships between chunks
            for chunk_id in chunk_nodes:
                related_chunks = self.get_related_chunks(chunk_id, "similar")
                for related in related_chunks:
                    if related.chunk.id in chunk_nodes:
                        edge = GraphEdge(
                            source=chunk_nodes[chunk_id],
                            target=chunk_nodes[related.chunk.id],
                            relationship=EdgeType.SIMILAR_TO,
                            confidence=related.similarity_score
                        )
                        graph.add_edge(edge)
                        
            return graph
            
        except Exception as e:
            logger.error(f"Failed to build document graph: {e}")
            return graph