import fitz  # PyMuPDF
from typing import List, Dict, Any
from .models import TextBlock, Rectangle
import re

class PDFProcessor:
    def __init__(self):
        pass
    
    def extract_text_with_coordinates(self, pdf_path: str) -> List[TextBlock]:
        """Extract text blocks with their coordinates from PDF"""
        doc = fitz.open(pdf_path)
        text_blocks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")
            
            for block in blocks["blocks"]:
                if "lines" in block:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:  # Only non-empty text
                                text_blocks.append(TextBlock(
                                    text=text,
                                    page=page_num + 1,
                                    bbox=span["bbox"]  # [x0, y0, x1, y1]
                                ))
        
        doc.close()
        return text_blocks
    
    def get_full_text_by_page(self, pdf_path: str) -> Dict[int, str]:
        """Get full text content organized by page"""
        doc = fitz.open(pdf_path)
        page_texts = {}
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            page_texts[page_num + 1] = text
            
        doc.close()
        return page_texts
    
    def find_text_coordinates(self, pdf_path: str, search_text: str, page_num: int) -> List[Rectangle]:
        """Find coordinates of specific text on a page"""
        doc = fitz.open(pdf_path)
        rectangles = []
        
        if page_num <= len(doc):
            page = doc[page_num - 1]
            text_instances = page.search_for(search_text)
            
            for rect in text_instances:
                rectangles.append(Rectangle(
                    x=rect.x0,
                    y=rect.y0, 
                    width=rect.x1 - rect.x0,
                    height=rect.y1 - rect.y0
                ))
        
        doc.close()
        return rectangles
    
    def find_text_fuzzy(self, pdf_path: str, search_text: str, page_num: int, similarity_threshold: float = 0.9) -> List[Rectangle]:
        """Find text with exact and fuzzy matching for sentences"""
        doc = fitz.open(pdf_path)
        rectangles = []
        
        print(f"Searching for: '{search_text}' on page {page_num}")
        
        if page_num <= len(doc):
            page = doc[page_num - 1]
            
            # First try exact search
            exact_matches = page.search_for(search_text)
            if exact_matches:
                print(f"✓ Found EXACT match for: '{search_text}'")
                for rect in exact_matches:
                    # Expand bounding box for better coverage
                    padding_x = max(2, (rect.x1 - rect.x0) * 0.02)  # 2% padding or minimum 2px
                    padding_y = max(1, (rect.y1 - rect.y0) * 0.1)   # 10% padding or minimum 1px
                    
                    # Add small vertical offset to compensate for coordinate system differences
                    y_offset = 25  # Move highlight down by 3 pixels
                    x_offset = 1.5
                    
                    rectangles.append(Rectangle(
                        x=max(0, rect.x0 - padding_x + x_offset),
                        y=max(0, rect.y0 - padding_y + y_offset),
                        width=(rect.x1 - rect.x0) + (2 * padding_x),
                        height=(rect.y1 - rect.y0) + (2 * padding_y)
                    ))
                doc.close()
                return rectangles
            
            # If no exact match, try with cleaned text (remove extra spaces, etc.)
            clean_search = re.sub(r'\s+', ' ', search_text.strip())
            clean_exact_matches = page.search_for(clean_search)
            if clean_exact_matches:
                print(f"✓ Found EXACT match after cleaning for: '{clean_search}'")
                for rect in clean_exact_matches:
                    # Expand bounding box for better coverage
                    padding_x = max(2, (rect.x1 - rect.x0) * 0.02)  # 2% padding or minimum 2px
                    padding_y = max(1, (rect.y1 - rect.y0) * 0.1)   # 10% padding or minimum 1px
                    
                    # Add small vertical offset to compensate for coordinate system differences
                    y_offset = 3  # Move highlight down by 3 pixels
                    
                    rectangles.append(Rectangle(
                        x=max(0, rect.x0 - padding_x),
                        y=max(0, rect.y0 - padding_y + y_offset),
                        width=(rect.x1 - rect.x0) + (2 * padding_x),
                        height=(rect.y1 - rect.y0) + (2 * padding_y)
                    ))
                doc.close()
                return rectangles
            
            # Try searching for parts of the sentence
            print(f"No exact match found, trying sentence parts...")
            
            # Split into meaningful chunks and try each
            if len(search_text.split()) > 3:
                words = search_text.split()
                # Try first half and second half
                chunks = [
                    ' '.join(words[:len(words)//2]),
                    ' '.join(words[len(words)//2:]),
                    ' '.join(words[:min(6, len(words))]),  # First 6 words
                    ' '.join(words[-min(6, len(words)):])  # Last 6 words
                ]
                
                for chunk in chunks:
                    if len(chunk.strip()) > 3:
                        chunk_matches = page.search_for(chunk)
                        if chunk_matches:
                            print(f"✓ Found partial match for chunk: '{chunk}'")
                            for rect in chunk_matches:
                                # Expand bounding box for better coverage
                                padding_x = max(2, (rect.x1 - rect.x0) * 0.02)  # 2% padding or minimum 2px
                                padding_y = max(1, (rect.y1 - rect.y0) * 0.1)   # 10% padding or minimum 1px
                                
                                # Add small vertical offset to compensate for coordinate system differences
                                y_offset = 3  # Move highlight down by 3 pixels
                                
                                rectangles.append(Rectangle(
                                    x=max(0, rect.x0 - padding_x),
                                    y=max(0, rect.y0 - padding_y + y_offset),
                                    width=(rect.x1 - rect.x0) + (2 * padding_x),
                                    height=(rect.y1 - rect.y0) + (2 * padding_y)
                                ))
                            doc.close()
                            return rectangles
            
            # Last resort: fuzzy matching at line level
            print(f"Trying fuzzy line matching...")
            rectangles = self._fuzzy_line_search(page, search_text, similarity_threshold)
            
            if rectangles:
                print(f"✓ Found fuzzy match")
            else:
                print(f"✗ No match found for: '{search_text}'")
        
        doc.close()
        return rectangles
    
    def _fuzzy_line_search(self, page, search_text: str, threshold: float) -> List[Rectangle]:
        """Fallback fuzzy search at line level"""
        rectangles = []
        blocks = page.get_text("dict")
        clean_search = re.sub(r'\s+', ' ', search_text.lower().strip())
        search_words = clean_search.split()
        
        best_match = None
        best_score = 0
        
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    line_rects = []
                    
                    for span in line["spans"]:
                        span_text = span["text"]
                        line_text += span_text
                        line_rects.append(span["bbox"])
                    
                    clean_line = re.sub(r'\s+', ' ', line_text.lower().strip())
                    score = self._calculate_match_score(clean_search, clean_line, search_words)
                    
                    if score > threshold and score > best_score:
                        best_score = score
                        if line_rects:
                            min_x = min(rect[0] for rect in line_rects)
                            min_y = min(rect[1] for rect in line_rects)
                            max_x = max(rect[2] for rect in line_rects)
                            max_y = max(rect[3] for rect in line_rects)
                            
                            best_match = Rectangle(
                                x=max(0, min_x - 2),  # Add small padding
                                y=max(0, min_y - 1 + 3),  # Add small padding + vertical offset
                                width=(max_x - min_x) + 4,  # Expand width
                                height=(max_y - min_y) + 2  # Expand height
                            )
        
        if best_match:
            rectangles.append(best_match)
        
        return rectangles
    
    def _calculate_match_score(self, search_text: str, line_text: str, search_words: List[str]) -> float:
        """Calculate match score using multiple strategies"""
        # Strategy 1: Direct substring match
        if search_text in line_text:
            return 1.0
        
        # Strategy 2: Word-based similarity
        line_words = line_text.split()
        word_matches = sum(1 for word in search_words if word in line_words)
        word_score = word_matches / len(search_words) if search_words else 0
        
        # Strategy 3: Partial word matches
        partial_score = 0
        for search_word in search_words:
            for line_word in line_words:
                if len(search_word) > 3 and search_word in line_word:
                    partial_score += 0.5
                elif len(line_word) > 3 and line_word in search_word:
                    partial_score += 0.5
        
        partial_score = min(partial_score / len(search_words), 1.0) if search_words else 0
        
        # Strategy 4: Character-based similarity (for very short matches)
        char_score = self._similarity(search_text, line_text)
        
        # Return the best score
        return max(word_score, partial_score, char_score)

    def _similarity(self, text1: str, text2: str) -> float:
        """Simple similarity calculation"""
        # Simple word-based similarity
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
