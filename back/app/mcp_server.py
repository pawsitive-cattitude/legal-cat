"""
MCP Server for Legal Document Analysis Tools
Exposes PDF processing, RAG retrieval, and analysis capabilities
via the Model Context Protocol for use by ADK agents and other clients
"""

import asyncio
import json
import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# MCP Server Imports
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# Our legal analysis tools
from .pdf_processor import PDFProcessor
from .rag_system import LegalRAGSystem
from .graph_models import DocumentChunk, RAGSearchResult, LegalKnowledgeGraph

# ADK Tool Conversion Utility
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalDocumentMCPServer:
    """MCP Server that exposes legal document analysis tools"""
    
    def __init__(self):
        # Initialize our components
        self.pdf_processor = PDFProcessor()
        
        # Initialize RAG system if Google Cloud is configured
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if project_id:
            self.rag_system = LegalRAGSystem(
                project_id=project_id,
                location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
            )
        else:
            self.rag_system = None
            logger.warning("Google Cloud project not configured, RAG features disabled")
            
        # Create the MCP server
        self.app = Server("legal-document-mcp-server")
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.app.list_tools()
        async def list_tools() -> List[mcp_types.Tool]:
            """List all available legal document tools"""
            tools = []
            
            # PDF Processing Tool
            tools.append(mcp_types.Tool(
                name="extract_pdf_text",
                description="Extract text from PDF legal documents by page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the PDF file to process"
                        }
                    },
                    "required": ["file_path"]
                }
            ))
            
            # RAG Indexing Tool
            if self.rag_system:
                tools.append(mcp_types.Tool(
                    name="index_legal_document",
                    description="Index a legal document for RAG retrieval and graph analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the legal document to index"
                            }
                        },
                        "required": ["file_path"]
                    }
                ))
                
                # RAG Search Tool
                tools.append(mcp_types.Tool(
                    name="search_legal_knowledge",
                    description="Search legal knowledge base for relevant clauses and concepts",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Legal query or question to search for"
                            },
                            "document_id": {
                                "type": "string",
                                "description": "Optional: limit search to specific document"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ))
                
                # Graph Building Tool
                tools.append(mcp_types.Tool(
                    name="build_document_graph",
                    description="Build a knowledge graph for a legal document showing relationships between clauses",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_id": {
                                "type": "string",
                                "description": "Document ID to build graph for"
                            }
                        },
                        "required": ["document_id"]
                    }
                ))
                
            return tools
            
        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[mcp_types.Content]:
            """Execute a tool call"""
            logger.info(f"MCP Server: Executing tool '{name}' with args: {arguments}")
            
            try:
                if name == "extract_pdf_text":
                    return await self._extract_pdf_text(arguments)
                elif name == "index_legal_document":
                    return await self._index_legal_document(arguments)
                elif name == "search_legal_knowledge":
                    return await self._search_legal_knowledge(arguments)
                elif name == "build_document_graph":
                    return await self._build_document_graph(arguments)
                else:
                    error_text = json.dumps({"error": f"Tool '{name}' not implemented"})
                    return [mcp_types.TextContent(type="text", text=error_text)]
                    
            except Exception as e:
                logger.error(f"Error executing tool '{name}': {e}")
                error_text = json.dumps({"error": f"Failed to execute tool '{name}': {str(e)}"})
                return [mcp_types.TextContent(type="text", text=error_text)]
                
    async def _extract_pdf_text(self, arguments: dict) -> List[mcp_types.Content]:
        """Extract text from PDF"""
        file_path = arguments["file_path"]
        
        if not os.path.exists(file_path):
            error_text = json.dumps({"error": f"File not found: {file_path}"})
            return [mcp_types.TextContent(type="text", text=error_text)]
            
        try:
            page_texts = self.pdf_processor.extract_text_by_page(file_path)
            result = {
                "status": "success",
                "file_path": file_path,
                "pages": len(page_texts),
                "page_texts": page_texts
            }
            return [mcp_types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            error_text = json.dumps({"error": f"Failed to extract PDF text: {str(e)}"})
            return [mcp_types.TextContent(type="text", text=error_text)]
            
    async def _index_legal_document(self, arguments: dict) -> List[mcp_types.Content]:
        """Index a legal document for RAG"""
        if not self.rag_system:
            error_text = json.dumps({"error": "RAG system not available - Google Cloud not configured"})
            return [mcp_types.TextContent(type="text", text=error_text)]
            
        file_path = arguments["file_path"]
        
        if not os.path.exists(file_path):
            error_text = json.dumps({"error": f"File not found: {file_path}"})
            return [mcp_types.TextContent(type="text", text=error_text)]
            
        try:
            document_id = self.rag_system.index_document(file_path)
            result = {
                "status": "success",
                "document_id": document_id,
                "file_path": file_path,
                "message": "Document successfully indexed for RAG retrieval"
            }
            return [mcp_types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            error_text = json.dumps({"error": f"Failed to index document: {str(e)}"})
            return [mcp_types.TextContent(type="text", text=error_text)]
            
    async def _search_legal_knowledge(self, arguments: dict) -> List[mcp_types.Content]:
        """Search the legal knowledge base"""
        if not self.rag_system:
            error_text = json.dumps({"error": "RAG system not available - Google Cloud not configured"})
            return [mcp_types.TextContent(type="text", text=error_text)]
            
        query = arguments["query"]
        document_id = arguments.get("document_id")
        top_k = arguments.get("top_k", 5)
        
        try:
            search_results = self.rag_system.search(
                query=query,
                document_id=document_id,
                top_k=top_k
            )
            
            # Convert results to JSON-serializable format
            results_data = []
            for result in search_results:
                results_data.append({
                    "content": result.chunk.content,
                    "similarity_score": result.similarity_score,
                    "document_id": result.chunk.document_id,
                    "page_number": result.chunk.page_number,
                    "chunk_index": result.chunk.chunk_index,
                    "clause_type": result.chunk.clause_type,
                    "legal_concepts": result.chunk.legal_concepts,
                    "risk_indicators": result.chunk.risk_indicators,
                    "related_concepts": result.related_concepts
                })
                
            result = {
                "status": "success",
                "query": query,
                "results_count": len(results_data),
                "results": results_data
            }
            return [mcp_types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            error_text = json.dumps({"error": f"Failed to search knowledge base: {str(e)}"})
            return [mcp_types.TextContent(type="text", text=error_text)]
            
    async def _build_document_graph(self, arguments: dict) -> List[mcp_types.Content]:
        """Build knowledge graph for a document"""
        if not self.rag_system:
            error_text = json.dumps({"error": "RAG system not available - Google Cloud not configured"})
            return [mcp_types.TextContent(type="text", text=error_text)]
            
        document_id = arguments["document_id"]
        
        try:
            graph = self.rag_system.build_document_graph(document_id)
            
            # Convert graph to JSON-serializable format
            graph_data = {
                "nodes": [
                    {
                        "id": node.id,
                        "type": node.type.value,
                        "label": node.label,
                        "content": node.content,
                        "metadata": node.metadata,
                        "risk_level": node.risk_level.value if node.risk_level else None,
                        "confidence": node.confidence,
                        "page_number": node.page_number,
                        "document_id": node.document_id
                    }
                    for node in graph.nodes
                ],
                "edges": [
                    {
                        "id": edge.id,
                        "source": edge.source,
                        "target": edge.target,
                        "relationship": edge.relationship.value,
                        "confidence": edge.confidence,
                        "metadata": edge.metadata
                    }
                    for edge in graph.edges
                ]
            }
            
            result = {
                "status": "success",
                "document_id": document_id,
                "graph": graph_data,
                "stats": {
                    "nodes": len(graph_data["nodes"]),
                    "edges": len(graph_data["edges"])
                }
            }
            return [mcp_types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            error_text = json.dumps({"error": f"Failed to build document graph: {str(e)}"})
            return [mcp_types.TextContent(type="text", text=error_text)]
            
    async def run_stdio(self):
        """Run the MCP server with stdio transport"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Legal Document MCP Server: Starting...")
            await self.app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=self.app.name,
                    server_version="1.0.0",
                    capabilities=self.app.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
            logger.info("Legal Document MCP Server: Finished")

# ADK Tool wrappers for the MCP tools
def extract_pdf_text_tool(file_path: str) -> dict:
    """ADK tool wrapper for PDF text extraction"""
    processor = PDFProcessor()
    try:
        page_texts = processor.extract_text_by_page(file_path)
        return {
            "status": "success",
            "file_path": file_path,
            "pages": len(page_texts),
            "page_texts": page_texts
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

def search_legal_knowledge_tool(query: str, document_id: Optional[str] = None, top_k: int = 5) -> dict:
    """ADK tool wrapper for legal knowledge search"""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        return {"status": "error", "error_message": "Google Cloud project not configured"}
        
    try:
        rag_system = LegalRAGSystem(project_id=project_id)
        search_results = rag_system.search(query=query, document_id=document_id, top_k=top_k)
        
        results_data = []
        for result in search_results:
            results_data.append({
                "content": result.chunk.content,
                "similarity_score": result.similarity_score,
                "document_id": result.chunk.document_id,
                "page_number": result.chunk.page_number,
                "legal_concepts": result.chunk.legal_concepts,
                "related_concepts": result.related_concepts
            })
            
        return {
            "status": "success",
            "query": query,
            "results_count": len(results_data),
            "results": results_data
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

# Create ADK function tools for internal use
pdf_extraction_adk_tool = FunctionTool(extract_pdf_text_tool)
legal_search_adk_tool = FunctionTool(search_legal_knowledge_tool)

async def main():
    """Main function to run the MCP server"""
    server = LegalDocumentMCPServer()
    
    try:
        await server.run_stdio()
    except KeyboardInterrupt:
        logger.info("MCP Server stopped by user")
    except Exception as e:
        logger.error(f"MCP Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())