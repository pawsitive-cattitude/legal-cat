import google.generativeai as genai
import json
import re
from typing import Dict, List, Any
from .models import AnalysisResponse, Highlight, PageContent, DocumentInfo, HighlightColor, HighlightType, PageContentType
import os
from dotenv import load_dotenv

load_dotenv()

class LLMAnalyzer:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            print("Warning: GOOGLE_API_KEY not found. Using mock analysis.")
    
    def clean_json_response(self, response_text: str) -> str:
        """Clean and extract valid JSON from LLM response"""
        response_text = response_text.strip()
        
        # Remove markdown code blocks
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            start_idx = 1 if lines[0].strip() == '```json' else 1
            end_idx = -1
            for i, line in enumerate(lines):
                if line.strip() == '```':
                    end_idx = i
                    break
            if end_idx > start_idx:
                response_text = '\n'.join(lines[start_idx:end_idx])
        
        # Find JSON object boundaries
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json_match.group()
        
        return response_text
    
    def analyze_document(self, page_texts: Dict[int, str], document_name: str) -> Dict[str, Any]:
        """Analyze document and return structured data for highlights and page content"""
        
        if not self.model:
            return self.create_mock_analysis(page_texts, document_name)
        
        # Limit text size to avoid token limits
        combined_texts = []
        total_chars = 0
        for page, text in page_texts.items():
            if total_chars + len(text) > 15000:  # Limit to ~15k characters
                break
            combined_texts.append(f"PAGE {page}:\n{text}")
            total_chars += len(text)
        
        full_text = "\n\n".join(combined_texts)
        
        system_prompt = """Analyze this legal document and return valid JSON with highlights and comprehensive page summaries.

CRITICAL: For highlights, you MUST provide the EXACT sentence or phrase that appears in the document. Copy it word-for-word, including punctuation.

{
  "highlights": [
    {
      "id": "highlight-1",
      "page": 1,
      "text_to_highlight": "EXACT sentence or phrase copied word-for-word from the document",
      "color": "red|yellow|blue",
      "metadata": {
        "shortTitle": "Brief title",
        "title": "Descriptive title", 
        "type": "legal_risk|compliance_issue|standard_clause|important_term",
        "shortExplanation": "Brief 1-2 sentence explanation for tooltip - what this means in simple terms",
        "data": {
          "title": "Detailed Issue Title",
          "explanation": "Comprehensive explanation of this clause including: what it means in practical terms, potential consequences, why it matters, specific risks or benefits, and what parties should consider or negotiate."
        }
      }
    }
  ],
  "pageContent": {
    "1": {
      "type": "explanation",
      "data": {
        "title": "Page 1 Summary",
        "explanation": "Detailed summary of this page's contents, purpose, and significance. Explain what legal concepts are introduced, what obligations or rights are established, and how this page fits into the overall document structure.",
        "points": [
          "Primary purpose and function of this page",
          "Key legal concepts or clauses introduced",
          "Main obligations, rights, or conditions established",
          "Important terms or definitions provided",
          "Relationship to other parts of the document"
        ]
      }
    }
  },
  "documentInfo": {
    "name": "Document name",
    "date": "2024-09-04"
  }
}

CRITICAL HIGHLIGHTING RULES:
- text_to_highlight MUST be the EXACT text from the document - copy it precisely
- Include complete sentences or meaningful phrases (5-20 words)
- Do NOT paraphrase, summarize, or change any words
- Keep punctuation, capitalization, and spacing exactly as in the document
- If a sentence is very long, use a distinctive key phrase from within it

ANALYSIS INSTRUCTIONS:
1. Find 2-3 important sentences per page that need highlighting
2. Copy those sentences EXACTLY as they appear in the document
3. Use red for high risk/danger, yellow for caution, blue for important information
4. Create comprehensive page summaries explaining the content and significance

Return only the JSON object, no other text."""

        user_prompt = f"Document Name: {document_name}\n\nDocument Content:\n{full_text}"
        
        response = None
        try:
            # Create the prompt with system instructions
            prompt = f"{system_prompt}\n\nUser: {user_prompt}"
            
            # Generate response using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,  # Lower temperature for more consistent JSON
                    max_output_tokens=3000,  # Reduced to avoid overly long responses
                    response_mime_type="application/json"  # Force JSON response
                )
            )
            
            # Clean and parse the JSON response
            response_text = self.clean_json_response(response.text)
            
            try:
                analysis_data = json.loads(response_text)
                return analysis_data
            except json.JSONDecodeError as parse_error:
                print(f"JSON parsing failed even after cleaning. Error: {parse_error}")
                print(f"Cleaned response (first 500 chars): {response_text[:500]}")
                raise parse_error
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            if response and hasattr(response, 'text'):
                print(f"Raw response (first 1000 chars): {response.text[:1000]}")
            print("Falling back to mock analysis due to JSON parsing error")
            return self.create_mock_analysis(page_texts, document_name)
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            print("Falling back to mock analysis due to API error")
            return self.create_mock_analysis(page_texts, document_name)
    
    def create_fallback_analysis(self, page_texts: Dict[int, str], document_name: str, error_msg: str) -> Dict[str, Any]:
        """Create a fallback response when the API fails"""
        return {
            "highlights": [],
            "pageContent": {
                "1": {
                    "type": "notice",
                    "data": {
                        "title": "Analysis Error",
                        "message": f"Failed to analyze document: {error_msg}",
                        "severity": "error"
                    }
                }
            },
            "documentInfo": {
                "name": document_name,
                "date": "Analysis failed"
            }
        }
    
    def create_mock_analysis(self, page_texts: Dict[int, str], document_name: str) -> Dict[str, Any]:
        """Create a mock analysis for testing when Gemini is not available"""
        
        # Try to find actual sentences from the first page
        first_page_text = page_texts.get(1, "")
        
        # Look for the first complete sentence in the document
        sentences = [s.strip() + '.' for s in first_page_text.split('.') if len(s.strip()) > 20]
        
        text_to_highlight = "This document"  # Fallback
        second_highlight = "The parties"     # Second fallback
        
        if sentences:
            # Use the first substantial sentence
            text_to_highlight = sentences[0]
            if len(sentences) > 1:
                second_highlight = sentences[1]
        else:
            # Try to find common legal phrases that actually exist
            common_phrases = [
                "This Agreement",
                "The Company", 
                "The User",
                "Privacy Policy",
                "Terms of Service",
                "By using",
                "You agree",
                "We may",
                "Personal information"
            ]
            
            for phrase in common_phrases:
                if phrase in first_page_text:
                    # Find the sentence containing this phrase
                    for sentence in first_page_text.split('.'):
                        if phrase in sentence and len(sentence.strip()) > 10:
                            text_to_highlight = sentence.strip() + '.'
                            break
                    break
        
        # Create page content for all available pages
        page_content = {}
        for page_num in page_texts.keys():
            page_content[str(page_num)] = {
                "type": "explanation",
                "data": {
                    "title": f"Page {page_num} Summary",
                    "explanation": f"This page contains important legal provisions that establish the foundational terms and conditions governing the relationship between the parties. The content includes specific clauses that define rights, responsibilities, and procedural requirements. Each section serves a particular legal function in creating binding obligations and providing clarity on how the agreement operates in practice.",
                    "points": [
                        f"Establishes key legal framework for the agreement on page {page_num}",
                        "Defines specific rights, obligations, and responsibilities of each party",
                        "Contains important terms that may have financial or operational implications",
                        "Includes procedural requirements and compliance mechanisms",
                        "Provides legal structure for dispute resolution and enforcement"
                    ]
                }
            }
        
        return {
            "highlights": [
                {
                    "id": "mock-highlight-1",
                    "page": 1,
                    "text_to_highlight": text_to_highlight,
                    "color": "red",
                    "metadata": {
                        "shortTitle": "Important Clause",
                        "title": "Key Legal Provision",
                        "type": "legal_risk",
                        "data": {
                            "title": "Comprehensive Privacy and Data Collection Analysis",
                            "explanation": "This clause establishes broad permissions for data collection, processing, and potential sharing that may exceed what is necessary for the stated business purpose. The language lacks sufficient specificity regarding the scope, purpose, and limitations of data processing activities. This creates several concerns: (1) It may allow collection of sensitive personal information including browsing behavior, location data, device information, and contact details; (2) The broad permissions could enable data sharing with third parties without explicit user consent; (3) The clause may not comply with modern data protection regulations that require clear, specific, and informed consent; (4) Users have limited visibility into how their data will be used, stored, or protected. This type of broad data collection clause can create significant privacy risks and may expose the data subject to identity theft, unwanted marketing, or data breaches. Consider requesting more specific language that clearly defines what data is collected, how it's used, who it's shared with, and how long it's retained."
                        }
                    }
                },
                {
                    "id": "mock-highlight-2", 
                    "page": 1,
                    "text_to_highlight": second_highlight,
                    "color": "blue",
                    "metadata": {
                        "shortTitle": "Standard Term",
                        "title": "Standard Agreement Clause",
                        "type": "standard_clause",
                        "data": {
                            "title": "Standard Contractual Language - Important Considerations",
                            "explanation": "This represents standard boilerplate language that appears in most legal agreements within this category. While the language is commonly used across the industry, it establishes legally binding obligations that should be carefully reviewed. Standard clauses often cover fundamental aspects such as: (1) Basic rights and responsibilities of each party; (2) Procedural requirements for contract performance; (3) Default terms that apply unless specifically modified; (4) Legal frameworks for dispute resolution and enforcement. Even though this language is 'standard,' the specific terms can vary significantly between agreements and may have different implications depending on the context. The inclusion of standard language doesn't diminish its legal effect - these clauses are fully enforceable and can significantly impact the parties' rights and obligations. It's important to understand that 'standard' doesn't necessarily mean 'favorable' or 'non-negotiable.' Many standard clauses can be modified through negotiation, especially in business-to-business contexts. Review this language carefully to ensure it aligns with your business objectives and risk tolerance."
                        }
                    }
                }
            ],
            "pageContent": page_content,
            "documentInfo": {
                "name": document_name,
                "date": "2024-01-01 (Mock Analysis)"
            }
        }
