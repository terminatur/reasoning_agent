"""
File: src/tools/pdf_parser.py
Purpose: PDF document parsing tool for extracting text content from PDF files and URLs
Functionality: Downloads PDFs, extracts text content, handles metadata extraction, and formats citations
Update Trigger: When PDF parsing requirements change, new extraction features are needed, or citation formats are updated
Last Modified: 2024-06-24
"""
from typing import Any, Dict, List, Optional
import requests
import tempfile
import os
from datetime import datetime
from urllib.parse import urlparse, urljoin
import re

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

from ..config import config
from ..models import ToolSchema, Citation

class PDFParserTool:
    """
    PDF parsing tool for extracting text content from PDF documents.
    Supports both file paths and URLs.
    """
    
    def __init__(self):
        self.max_pages = config.PDF_MAX_PAGES
        self.description = "Extract text content from PDF documents via file path or URL"
        
        if not PYPDF_AVAILABLE:
            print("Warning: pypdf not available. PDF parsing functionality will be limited.")
    
    def get_schema(self) -> ToolSchema:
        """Return the tool schema for the agent to understand how to use this tool."""
        return ToolSchema(
            name="pdf_parser",
            description="Extract text content from PDF documents",
            parameters={
                "source": {
                    "type": "string",
                    "description": "PDF file path or URL to parse"
                },
                "max_pages": {
                    "type": "integer",
                    "description": "Maximum number of pages to extract (default: 50)",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 50
                },
                "extract_metadata": {
                    "type": "boolean",
                    "description": "Whether to extract PDF metadata",
                    "default": True
                },
                "page_range": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "integer", "minimum": 1},
                        "end": {"type": "integer", "minimum": 1}
                    },
                    "description": "Specific page range to extract (optional)"
                }
            },
            required_parameters=["source"]
        )
    
    def validate_input(self, source: str, **kwargs) -> None:
        """Validate input parameters."""
        if not source or not source.strip():
            raise ValueError("Source cannot be empty")
        
        max_pages = kwargs.get("max_pages", 50)
        if not isinstance(max_pages, int) or max_pages < 1 or max_pages > 200:
            raise ValueError("max_pages must be an integer between 1 and 200")
        
        page_range = kwargs.get("page_range")
        if page_range:
            if not isinstance(page_range, dict):
                raise ValueError("page_range must be a dictionary with 'start' and 'end' keys")
            
            start = page_range.get("start")
            end = page_range.get("end")
            
            if start and end and start > end:
                raise ValueError("page_range start cannot be greater than end")
    
    def execute(self, source: str, **kwargs) -> Dict[str, Any]:
        """Execute PDF parsing and return extracted content."""
        # Validate inputs
        self.validate_input(source, **kwargs)
        
        if not PYPDF_AVAILABLE:
            return {
                "error": "PDF parsing not available. Please install pypdf: pip install pypdf",
                "content": "",
                "metadata": {},
                "citation": {}
            }
        
        try:
            # Determine if source is URL or file path
            if self._is_url(source):
                pdf_path = self._download_pdf(source)
                cleanup_file = True
            else:
                pdf_path = source
                cleanup_file = False
                
                # Check if file exists
                if not os.path.exists(pdf_path):
                    return {
                        "error": f"File not found: {pdf_path}",
                        "content": "",
                        "metadata": {},
                        "citation": {}
                    }
            
            # Extract content from PDF
            result = self._extract_pdf_content(pdf_path, **kwargs)
            
            # Add source information
            result["source"] = source
            result["source_type"] = "URL" if self._is_url(source) else "file"
            
            # Generate citation
            result["citation"] = self._generate_citation(source, result.get("metadata", {}))
            
            # Cleanup temporary file if downloaded
            if cleanup_file and os.path.exists(pdf_path):
                os.unlink(pdf_path)
            
            return result
            
        except Exception as e:
            return {
                "error": f"PDF parsing failed: {str(e)}",
                "content": "",
                "metadata": {},
                "citation": {}
            }
    
    def _is_url(self, source: str) -> bool:
        """Check if source is a URL."""
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _download_pdf(self, url: str) -> str:
        """Download PDF from URL to temporary file."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Check if content is actually a PDF
            content_type = response.headers.get("content-type", "").lower()
            if "pdf" not in content_type and not url.lower().endswith(".pdf"):
                # Try to detect PDF by content
                if not response.content.startswith(b"%PDF"):
                    raise ValueError("URL does not appear to contain a PDF document")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(response.content)
                return temp_file.name
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download PDF: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing PDF download: {str(e)}")
    
    def _extract_pdf_content(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """Extract text content and metadata from PDF."""
        try:
            reader = PdfReader(pdf_path)
            
            # Extract metadata
            metadata = {}
            extract_metadata = kwargs.get("extract_metadata", True)
            if extract_metadata and reader.metadata:
                metadata = {
                    "title": reader.metadata.get("/Title", ""),
                    "author": reader.metadata.get("/Author", ""),
                    "subject": reader.metadata.get("/Subject", ""),
                    "creator": reader.metadata.get("/Creator", ""),
                    "producer": reader.metadata.get("/Producer", ""),
                    "creation_date": reader.metadata.get("/CreationDate", ""),
                    "modification_date": reader.metadata.get("/ModDate", "")
                }
            
            # Determine page range
            total_pages = len(reader.pages)
            max_pages = min(kwargs.get("max_pages", 50), total_pages)
            
            page_range = kwargs.get("page_range")
            if page_range:
                start_page = max(0, page_range.get("start", 1) - 1)  # Convert to 0-based
                end_page = min(total_pages, page_range.get("end", total_pages))
            else:
                start_page = 0
                end_page = min(max_pages, total_pages)
            
            # Extract text from pages
            text_content = []
            extracted_pages = []
            
            for page_num in range(start_page, end_page):
                try:
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():  # Only add non-empty pages
                        text_content.append(f"--- Page {page_num + 1} ---\n{text}\n")
                        extracted_pages.append(page_num + 1)
                
                except Exception as e:
                    print(f"Warning: Could not extract text from page {page_num + 1}: {e}")
                    continue
            
            full_text = "\n".join(text_content)
            
            # Clean up text
            cleaned_text = self._clean_text(full_text)
            
            return {
                "content": cleaned_text,
                "metadata": metadata,
                "page_info": {
                    "total_pages": total_pages,
                    "extracted_pages": extracted_pages,
                    "page_range_requested": f"{start_page + 1}-{end_page}"
                },
                "word_count": len(cleaned_text.split()),
                "character_count": len(cleaned_text),
                "extraction_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to extract PDF content: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text content."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove form feeds and other control characters
        text = re.sub(r'[\x0c\x0b\x0e\x0f]', ' ', text)
        
        # Normalize line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def _generate_citation(self, source: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate citation information for the PDF."""
        title = metadata.get("title", "")
        author = metadata.get("author", "")
        
        # If no title in metadata, try to extract from URL or filename
        if not title:
            if self._is_url(source):
                title = os.path.basename(urlparse(source).path)
            else:
                title = os.path.basename(source)
            
            # Remove file extension
            title = os.path.splitext(title)[0]
        
        citation = Citation(
            source_url=source if self._is_url(source) else None,
            title=title or "Untitled Document",
            author=author or None,
            publication_date=self._parse_pdf_date(metadata.get("creation_date")),
            accessed_date=datetime.now(),
            snippet="",  # Could add first few sentences here
            relevance_score=0.8  # PDFs are generally high-quality sources
        )
        
        return citation.dict()
    
    def _parse_pdf_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse PDF date format to datetime object."""
        if not date_str:
            return None
        
        try:
            # PDF dates are often in format: D:YYYYMMDDHHmmSSOHH'mm'
            if date_str.startswith("D:"):
                date_str = date_str[2:]  # Remove D: prefix
            
            # Extract just the date part (YYYYMMDD)
            if len(date_str) >= 8:
                date_part = date_str[:8]
                return datetime.strptime(date_part, "%Y%m%d")
            
            return None
        except Exception:
            return None
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """Alternative entry point for backward compatibility."""
        source = kwargs.get("source", "")
        return self.execute(source, **kwargs)
