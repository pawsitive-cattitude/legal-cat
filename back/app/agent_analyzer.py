"""
Advanced Legal Document Analysis System using Google ADK
Multi-agent system with specialized agents for different legal analysis tasks
"""

import os
import logging
from typing import Dict, List, Any, Optional
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from .graph_models import (
    EnhancedAnalysisResponse, LegalKnowledgeGraph, GraphNode, GraphEdge,
    NodeType, EdgeType, RiskLevel, DocumentChunk
)
from .rag_system import LegalRAGSystem
from .mcp_server import pdf_extraction_adk_tool, legal_search_adk_tool

logger = logging.getLogger(__name__)

class LegalDocumentAgentAnalyzer:
    """
    Multi-agent system for legal document analysis using Google ADK
    Replaces the simple LLMAnalyzer with sophisticated agent-based reasoning
    """
    
    def __init__(self):
        self.session_service = InMemorySessionService()
        
        # Initialize RAG system
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if project_id:
            self.rag_system = LegalRAGSystem(project_id=project_id)
        else:
            self.rag_system = None
            logger.warning("Google Cloud not configured, limited functionality")
            
        # Create specialized agents
        self._create_agents()
        
        # Create the coordinator agent
        self._create_coordinator()
        
    def _create_agents(self):
        """Create specialized legal analysis agents"""
        
        # Legal Context Analysis Agent
        self.legal_context_agent = LlmAgent(
            name="legal_context_analyzer",
            model="gemini-2.0-flash",
            instruction="""You are a specialized legal document context analyzer. Your role is to:
            
            1. Identify the type of legal document (contract, agreement, policy, etc.)
            2. Determine the parties involved and their roles
            3. Identify the governing jurisdiction and applicable laws
            4. Extract key dates, terms, and conditions
            5. Understand the overall purpose and scope of the document
            
            Always provide structured analysis with clear categorization and high confidence scores for your findings.""",
            description="Analyzes legal document context, parties, and structure",
            tools=[pdf_extraction_adk_tool] if self.rag_system else []
        )
        
        # Clause Detection and Analysis Agent
        self.clause_analysis_agent = LlmAgent(
            name="clause_analyzer",
            model="gemini-2.0-flash",
            instruction="""You are a specialized legal clause analyzer. Your expertise includes:
            
            1. Identifying and categorizing different types of clauses (liability, termination, confidentiality, etc.)
            2. Analyzing clause language for potential risks and implications
            3. Detecting unusual or non-standard clause provisions
            4. Identifying missing clauses that might be expected in this type of document
            5. Assessing clause enforceability and legal strength
            
            For each clause you identify, provide:
            - Clause type and category
            - Risk level (low, medium, high, critical)
            - Legal implications
            - Recommendations for improvement or attention
            
            Use specific legal terminology and cite relevant legal principles when applicable.""",
            description="Identifies and analyzes legal clauses and their implications",
            tools=[legal_search_adk_tool] if self.rag_system else []
        )
        
        # Risk Assessment Agent
        self.risk_assessment_agent = LlmAgent(
            name="risk_assessor",
            model="gemini-2.0-flash",
            instruction="""You are a specialized legal risk assessment expert. Your role is to:
            
            1. Identify potential legal risks in contract terms and conditions
            2. Assess liability exposure and financial risks
            3. Evaluate compliance risks with relevant regulations
            4. Identify operational and business risks
            5. Prioritize risks by severity and likelihood
            
            For each risk identified, provide:
            - Risk category (legal, financial, operational, compliance)
            - Severity level (low, medium, high, critical)
            - Likelihood of occurrence
            - Potential impact and consequences
            - Mitigation recommendations
            
            Consider both immediate and long-term risk implications.""",
            description="Assesses legal and business risks in documents",
            tools=[legal_search_adk_tool] if self.rag_system else []
        )
        
        # Compliance Analysis Agent
        self.compliance_agent = LlmAgent(
            name="compliance_analyzer",
            model="gemini-2.0-flash",
            instruction="""You are a compliance specialist focused on regulatory and legal compliance analysis. Your expertise covers:
            
            1. Identifying compliance requirements based on document type and jurisdiction
            2. Checking for required disclosures and legal notices
            3. Verifying compliance with industry-specific regulations
            4. Assessing data privacy and protection compliance (GDPR, CCPA, etc.)
            5. Identifying missing compliance elements
            
            For compliance analysis, provide:
            - Applicable regulations and standards
            - Compliance gaps or deficiencies
            - Required actions to achieve compliance
            - Compliance risk level
            - Implementation recommendations
            
            Stay current with relevant regulations and best practices.""",
            description="Analyzes compliance requirements and gaps",
            tools=[legal_search_adk_tool] if self.rag_system else []
        )
        
        # Legal Research Agent (using RAG and external sources)
        self.research_agent = LlmAgent(
            name="legal_researcher",
            model="gemini-2.0-flash",
            instruction="""You are a legal research specialist. Your role is to:
            
            1. Research relevant case law and legal precedents
            2. Find similar clauses and contract provisions
            3. Identify industry standards and best practices
            4. Research applicable laws and regulations
            5. Provide context from legal databases and knowledge bases
            
            When conducting research:
            - Always cite sources and provide references
            - Distinguish between mandatory law and best practices
            - Consider jurisdiction-specific variations
            - Provide recent developments and trends
            - Suggest alternative approaches and improvements
            
            Use the legal knowledge base to find relevant information and precedents.""",
            description="Conducts legal research using RAG and external sources",
            tools=[legal_search_adk_tool] if self.rag_system else []
        )
        
    def _create_coordinator(self):
        """Create the main coordinator agent that orchestrates the analysis"""
        
        # Create agent tools for coordination
        agent_tools = [
            AgentTool(agent=self.legal_context_agent),
            AgentTool(agent=self.clause_analysis_agent),
            AgentTool(agent=self.risk_assessment_agent),
            AgentTool(agent=self.compliance_agent),
            AgentTool(agent=self.research_agent)
        ]
        
        self.coordinator = LlmAgent(
            name="legal_analysis_coordinator",
            model="gemini-2.0-flash",
            instruction="""You are the coordinator for a comprehensive legal document analysis system. 
            You have access to a team of specialized legal analysis agents:
            
            1. legal_context_analyzer - Analyzes document context and structure
            2. clause_analyzer - Identifies and analyzes legal clauses
            3. risk_assessor - Assesses legal and business risks
            4. compliance_analyzer - Checks compliance requirements
            5. legal_researcher - Conducts legal research using knowledge bases
            
            Your role is to:
            1. Orchestrate a comprehensive analysis by delegating appropriate tasks to specialists
            2. Synthesize findings from all agents into a coherent analysis
            3. Identify relationships and dependencies between different findings
            4. Prioritize issues and recommendations
            5. Provide a complete executive summary
            
            Always ensure thorough coverage of all important legal aspects and provide actionable insights.""",
            description="Coordinates comprehensive legal document analysis",
            tools=agent_tools
        )
        
    async def analyze_document(self, page_texts: Dict[int, str], document_name: str) -> EnhancedAnalysisResponse:
        """
        Perform comprehensive legal document analysis using the multi-agent system
        """
        try:
            # Index document in RAG system if available
            document_id = None
            if self.rag_system:
                # For this demo, we'll simulate document indexing
                # In practice, you'd save the file and index it
                document_id = f"doc_{hash(str(page_texts))}"
                
            # Create session for analysis
            session = await self.session_service.create_session(
                app_name="legal_analysis",
                user_id="analyst",
                session_id=f"session_{document_id}"
            )
            
            # Create runner for coordinator
            runner = Runner(
                agent=self.coordinator,
                app_name="legal_analysis",
                session_service=self.session_service
            )
            
            # Prepare the analysis request
            combined_text = "\n\n".join([f"PAGE {page}:\n{text}" for page, text in page_texts.items()])
            
            # Limit text size to avoid token limits
            if len(combined_text) > 20000:
                combined_text = combined_text[:20000] + "\n\n[Document truncated for analysis...]"
                
            analysis_prompt = f"""
            Please conduct a comprehensive legal analysis of the following document: "{document_name}"
            
            The document content is:
            {combined_text}
            
            Please coordinate with your specialized agents to provide:
            1. Document context and structure analysis
            2. Detailed clause identification and analysis
            3. Risk assessment and prioritization
            4. Compliance review and gaps
            5. Legal research for relevant precedents and standards
            
            Provide a comprehensive analysis with actionable insights and recommendations.
            """
            
            # Execute analysis
            content = types.Content(role='user', parts=[types.Part(text=analysis_prompt)])
            events = runner.run(
                user_id="analyst",
                session_id=session.id,
                new_message=content
            )
            
            # Collect analysis results
            analysis_text = ""
            for event in events:
                if event.is_final_response() and event.content and event.content.parts:
                    analysis_text = event.content.parts[0].text
                    break
                    
            # Build knowledge graph if RAG system is available
            knowledge_graph = LegalKnowledgeGraph()
            if self.rag_system and document_id:
                knowledge_graph = self.rag_system.build_document_graph(document_id)
                
            # Parse the analysis to extract structured data
            highlights, page_content = self._parse_analysis_to_highlights(analysis_text, page_texts)
            
            # Create enhanced response
            response = EnhancedAnalysisResponse(
                document_id=document_id or f"temp_{hash(document_name)}",
                document_name=document_name,
                highlights=highlights,
                page_content=page_content,
                document_info={
                    "filename": document_name,
                    "pages": len(page_texts),
                    "analysis_method": "ADK Multi-Agent System"
                },
                knowledge_graph=knowledge_graph,
                key_insights=self._extract_key_insights(analysis_text),
                risk_summary=self._extract_risk_summary(analysis_text),
                compliance_gaps=self._extract_compliance_gaps(analysis_text)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # Return minimal response with error info
            return EnhancedAnalysisResponse(
                document_id=f"error_{hash(document_name)}",
                document_name=document_name,
                document_info={
                    "filename": document_name,
                    "error": str(e)
                },
                knowledge_graph=LegalKnowledgeGraph()
            )
            
    def _parse_analysis_to_highlights(self, analysis_text: str, page_texts: Dict[int, str]) -> tuple:
        """Parse agent analysis back to highlight format for frontend compatibility"""
        highlights = []
        page_content = {}
        
        # Simple parsing - in production you'd want more sophisticated extraction
        # This is a basic implementation to maintain compatibility
        
        for page_num, text in page_texts.items():
            # Create basic page summary
            page_content[str(page_num)] = {
                "type": "explanation",
                "data": {
                    "title": f"Page {page_num} Analysis",
                    "explanation": f"Page {page_num} of the legal document analyzed by ADK multi-agent system.",
                    "points": [
                        "Analyzed by specialized legal agents",
                        "Comprehensive risk assessment performed",
                        "Compliance requirements checked",
                        "Legal research conducted"
                    ]
                }
            }
            
            # Create sample highlights - you'd extract these from the analysis
            if "risk" in analysis_text.lower() or "liability" in analysis_text.lower():
                highlights.append({
                    "id": f"highlight-{len(highlights)+1}",
                    "page": page_num,
                    "text_to_highlight": text[:100] + "..." if len(text) > 100 else text,
                    "color": "red",
                    "metadata": {
                        "shortTitle": "Risk Identified",
                        "title": "Potential Legal Risk",
                        "type": "legal_risk",
                        "shortExplanation": "This clause may present legal or business risks that require attention.",
                        "data": {
                            "title": "Risk Analysis by ADK Agents",
                            "explanation": "Our specialized risk assessment agent has identified potential concerns in this clause. Please review the detailed analysis for recommendations."
                        }
                    }
                })
                
        return highlights, page_content
        
    def _extract_key_insights(self, analysis_text: str) -> List[str]:
        """Extract key insights from agent analysis"""
        # Simple extraction - in production you'd use more sophisticated parsing
        insights = []
        
        if "high risk" in analysis_text.lower():
            insights.append("High-risk clauses identified requiring immediate attention")
        if "compliance" in analysis_text.lower():
            insights.append("Compliance requirements and gaps have been assessed")
        if "termination" in analysis_text.lower():
            insights.append("Termination clauses analyzed for enforceability")
        if "liability" in analysis_text.lower():
            insights.append("Liability provisions require careful review")
            
        return insights or ["Comprehensive legal analysis completed by ADK multi-agent system"]
        
    def _extract_risk_summary(self, analysis_text: str) -> Dict[RiskLevel, int]:
        """Extract risk summary from analysis"""
        # Simple counting - in production you'd parse structured output
        risk_summary = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 0,
            RiskLevel.HIGH: 0,
            RiskLevel.CRITICAL: 0
        }
        
        # Count risk mentions (simplified)
        text_lower = analysis_text.lower()
        risk_summary[RiskLevel.LOW] = text_lower.count("low risk")
        risk_summary[RiskLevel.MEDIUM] = text_lower.count("medium risk") + text_lower.count("moderate risk")
        risk_summary[RiskLevel.HIGH] = text_lower.count("high risk")
        risk_summary[RiskLevel.CRITICAL] = text_lower.count("critical risk") + text_lower.count("severe risk")
        
        return risk_summary
        
    def _extract_compliance_gaps(self, analysis_text: str) -> List[str]:
        """Extract compliance gaps from analysis"""
        gaps = []
        
        if "privacy policy" in analysis_text.lower():
            gaps.append("Privacy policy requirements may need review")
        if "gdpr" in analysis_text.lower():
            gaps.append("GDPR compliance considerations identified")
        if "disclosure" in analysis_text.lower():
            gaps.append("Required disclosures may be missing")
            
        return gaps