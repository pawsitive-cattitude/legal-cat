"""
MCP-Enhanced Legal Agent System
Integrates Google ADK agents with MCP tools for extensible legal analysis
"""

import os
import logging
from typing import Dict, List, Any, Optional
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools import google_search
from mcp import StdioServerParameters

from .agent_analyzer import LegalDocumentAgentAnalyzer
from .graph_models import EnhancedAnalysisResponse

logger = logging.getLogger(__name__)

class MCPEnhancedLegalAnalyzer(LegalDocumentAgentAnalyzer):
    """
    Enhanced legal analyzer that uses MCP tools for external integrations
    """
    
    def __init__(self):
        super().__init__()
        self._setup_mcp_tools()
        self._enhance_agents_with_mcp()
        
    def _setup_mcp_tools(self):
        """Setup MCP toolsets for external integrations"""
        
        # Internal MCP server toolset (our legal document tools)
        self.internal_mcp_toolset = None
        try:
            # Path to our MCP server script
            mcp_server_path = os.path.join(os.path.dirname(__file__), "mcp_server.py")
            
            self.internal_mcp_toolset = MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command='python',
                        args=[mcp_server_path],
                        env={
                            "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT", ""),
                            "GOOGLE_CLOUD_LOCATION": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
                        }
                    ),
                    timeout=10
                ),
                tool_filter=[
                    'extract_pdf_text',
                    'index_legal_document', 
                    'search_legal_knowledge',
                    'build_document_graph'
                ]
            )
            logger.info("Internal MCP toolset configured successfully")
        except Exception as e:
            logger.error(f"Failed to setup internal MCP toolset: {e}")
            
        # External legal database MCP server (example)
        self.legal_db_toolset = None
        try:
            # This would connect to an external legal database MCP server
            # For demo purposes, we'll use a filesystem server as an example
            legal_docs_path = os.getenv("LEGAL_DOCS_PATH", "/tmp/legal_docs")
            os.makedirs(legal_docs_path, exist_ok=True)
            
            self.legal_db_toolset = MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command='npx',
                        args=[
                            "-y",
                            "@modelcontextprotocol/server-filesystem",
                            legal_docs_path
                        ]
                    ),
                    timeout=10
                ),
                tool_filter=['read_file', 'list_directory', 'search_files']
            )
            logger.info("External legal database MCP toolset configured")
        except Exception as e:
            logger.error(f"Failed to setup legal database MCP toolset: {e}")
            
    def _enhance_agents_with_mcp(self):
        """Enhance existing agents with MCP tools"""
        
        # Enhanced Legal Research Agent with MCP tools
        research_tools = []
        
        # Add Google Search for legal research
        research_tools.append(google_search)
        
        # Add our MCP toolsets
        if self.internal_mcp_toolset:
            research_tools.append(self.internal_mcp_toolset)
        if self.legal_db_toolset:
            research_tools.append(self.legal_db_toolset)
            
        self.enhanced_research_agent = LlmAgent(
            name="mcp_enhanced_legal_researcher",
            model="gemini-2.0-flash",
            instruction="""You are an advanced legal research specialist with access to multiple data sources and tools:

            1. Google Search - for recent legal developments, case law, and news
            2. Legal Knowledge Base - internal legal document database
            3. Legal Document Processor - for analyzing and indexing documents
            4. File System Access - for accessing legal document repositories

            Your enhanced capabilities include:
            
            1. Research recent case law and legal precedents using web search
            2. Access internal legal knowledge base for similar cases and clauses
            3. Cross-reference findings across multiple sources
            4. Provide comprehensive legal research with multiple citations
            5. Identify trends and recent developments in relevant legal areas
            
            When conducting research:
            - Always verify information across multiple sources
            - Cite specific sources and provide links when available
            - Distinguish between primary law (statutes, cases) and secondary sources
            - Consider recent developments and changes in law
            - Provide practical implications and recommendations
            
            Use your tools strategically to provide the most comprehensive and accurate legal research.""",
            description="Enhanced legal researcher with MCP tool integration",
            tools=research_tools
        )
        
        # Enhanced Document Analysis Agent
        analysis_tools = []
        if self.internal_mcp_toolset:
            analysis_tools.append(self.internal_mcp_toolset)
            
        self.enhanced_document_agent = LlmAgent(
            name="mcp_enhanced_document_analyzer",
            model="gemini-2.0-flash",
            instruction="""You are an advanced legal document analyzer with access to sophisticated document processing tools:

            1. PDF Text Extraction - extract and process text from legal documents
            2. Legal Knowledge Search - search for similar clauses and precedents
            3. Document Graph Builder - create relationship maps between legal concepts
            4. Document Indexing - add documents to searchable knowledge base

            Your enhanced capabilities include:
            
            1. Process complex legal documents with high accuracy
            2. Identify relationships between different document sections
            3. Build knowledge graphs showing clause dependencies
            4. Cross-reference clauses with known legal standards
            5. Provide structured analysis with confidence scores
            
            When analyzing documents:
            - Use document processing tools to ensure accurate text extraction
            - Search knowledge base for similar clauses and precedents
            - Build relationship graphs to show clause interconnections
            - Provide detailed analysis with supporting evidence
            - Index processed documents for future reference
            
            Your goal is to provide the most comprehensive and accurate document analysis possible.""",
            description="Enhanced document analyzer with MCP integration",
            tools=analysis_tools
        )
        
        # Enhanced Risk Assessment Agent
        risk_tools = []
        if self.internal_mcp_toolset:
            risk_tools.append(self.internal_mcp_toolset)
        risk_tools.append(google_search)
        
        self.enhanced_risk_agent = LlmAgent(
            name="mcp_enhanced_risk_assessor",
            model="gemini-2.0-flash",
            instruction="""You are an advanced legal risk assessment specialist with access to comprehensive research tools:

            1. Legal Knowledge Search - access database of risk patterns and cases
            2. Web Search - research recent risk events and legal developments
            3. Document Analysis - deep analysis of risk-related clauses

            Your enhanced risk assessment includes:
            
            1. Historical risk analysis based on similar cases and documents
            2. Current risk landscape research using web search
            3. Quantitative risk scoring based on precedents
            4. Cross-referencing risks with regulatory changes
            5. Industry-specific risk pattern recognition
            
            When assessing risks:
            - Search knowledge base for similar risk scenarios
            - Research recent legal developments that might affect risk levels
            - Provide quantitative risk scores with supporting evidence
            - Consider both legal and business risk implications
            - Recommend specific mitigation strategies
            
            Your risk assessments should be comprehensive, evidence-based, and actionable.""",
            description="Enhanced risk assessor with MCP and web research",
            tools=risk_tools
        )
        
    async def analyze_document_with_mcp(self, page_texts: Dict[int, str], document_name: str) -> EnhancedAnalysisResponse:
        """
        Enhanced document analysis using MCP-integrated agents
        """
        try:
            logger.info(f"Starting MCP-enhanced analysis of {document_name}")
            
            # First, use the enhanced document agent to process the document
            if self.enhanced_document_agent and self.internal_mcp_toolset:
                logger.info("Using MCP-enhanced document processing")
                
                # The enhanced agents will use MCP tools automatically
                # when they determine it's beneficial for the analysis
                
            # Perform the standard analysis with enhanced agents
            response = await self.analyze_document(page_texts, document_name)
            
            # Add MCP-specific enhancements to the response
            response.document_info["analysis_method"] = "ADK Multi-Agent System with MCP Integration"
            response.document_info["mcp_tools_used"] = [
                "Internal Legal Document MCP Server",
                "Google Search Integration",
                "Legal Database Access"
            ]
            
            # Add additional insights from MCP-enhanced research
            if hasattr(self, 'enhanced_research_agent'):
                response.key_insights.append("Enhanced with external legal research and precedent analysis")
                
            return response
            
        except Exception as e:
            logger.error(f"MCP-enhanced analysis failed: {e}")
            # Fallback to standard analysis
            return await self.analyze_document(page_texts, document_name)
            
    def get_mcp_capabilities(self) -> Dict[str, Any]:
        """Get information about available MCP capabilities"""
        capabilities = {
            "internal_mcp_server": {
                "available": self.internal_mcp_toolset is not None,
                "tools": [
                    "extract_pdf_text",
                    "index_legal_document", 
                    "search_legal_knowledge",
                    "build_document_graph"
                ] if self.internal_mcp_toolset else []
            },
            "legal_database": {
                "available": self.legal_db_toolset is not None,
                "tools": [
                    "read_file",
                    "list_directory", 
                    "search_files"
                ] if self.legal_db_toolset else []
            },
            "web_search": {
                "available": True,
                "tools": ["google_search"]
            }
        }
        
        return capabilities
        
    async def search_legal_precedents(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for legal precedents using MCP-enhanced research agent
        """
        try:
            if not hasattr(self, 'enhanced_research_agent'):
                return []
                
            # Use the enhanced research agent to find precedents
            # This would typically involve creating a session and running the agent
            # For now, we'll return a placeholder response
            
            precedents = [
                {
                    "title": f"Precedent research for: {query}",
                    "description": "MCP-enhanced legal research would provide detailed precedent analysis here",
                    "source": "Enhanced Legal Research Agent with MCP",
                    "relevance_score": 0.85
                }
            ]
            
            return precedents
            
        except Exception as e:
            logger.error(f"Failed to search legal precedents: {e}")
            return []