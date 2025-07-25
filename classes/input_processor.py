"""
Universal Input Processor for ThreatPathMapper
Handles URLs, HTML, PDF, and text files
"""

import os
import re
import requests
from urllib.parse import urlparse
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import fitz  # PyMuPDF, already in requirements as fitz==0.0.1.dev2
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from inscriptis import get_text
    INSCRIPTIS_AVAILABLE = True
except ImportError:
    INSCRIPTIS_AVAILABLE = False


class InputProcessor:
    """Universal input processor for multiple file formats and URLs"""
    
    def __init__(self, user_agent: str = "ThreatPathMapper CTI Analyzer 1.0"):
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def process_input(self, input_path: str) -> Optional[str]:
        """
        Universal input processor that handles:
        - URLs (http/https)
        - Local files (.txt, .html, .pdf)
        - Raw text strings
        
        Returns extracted text content or None if processing failed
        """
        try:
            # Check if input is a URL
            if self._is_url(input_path):
                return self._process_url(input_path)
            
            # Check if input is a local file path
            elif os.path.exists(input_path):
                return self._process_file(input_path)
            
            # Treat as raw text
            else:
                return input_path.strip() if input_path.strip() else None
                
        except Exception as e:
            print(f"Error processing input '{input_path}': {str(e)}")
            return None
    
    def _is_url(self, text: str) -> bool:
        """Check if text is a valid URL"""
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except:
            return False
    
    def _process_url(self, url: str) -> Optional[str]:
        """Process URL and extract text content"""
        try:
            print(f"Fetching content from URL: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            
            # Handle PDF URLs
            if 'application/pdf' in content_type:
                return self._extract_pdf_from_bytes(response.content)
            
            # Handle HTML content
            elif 'text/html' in content_type or 'text/xml' in content_type:
                return self._extract_html_text(response.text)
            
            # Handle plain text
            elif 'text/plain' in content_type:
                return response.text.strip()
            
            # Default: try HTML parsing
            else:
                return self._extract_html_text(response.text)
                
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {str(e)}")
            return None
        except Exception as e:
            print(f"Error processing URL content: {str(e)}")
            return None
    
    def _process_file(self, file_path: str) -> Optional[str]:
        """Process local file based on extension"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        try:
            if extension == '.txt':
                return self._extract_text_file(file_path)
            elif extension in ['.html', '.htm']:
                return self._extract_html_file(file_path)
            elif extension == '.pdf':
                return self._extract_pdf_file(file_path)
            else:
                # Try to read as text file
                print(f"Unknown extension {extension}, trying as text file")
                return self._extract_text_file(file_path)
                
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return None
    
    def _extract_text_file(self, file_path: str) -> str:
        """Extract text from .txt file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read().strip()
    
    def _extract_html_file(self, file_path: str) -> Optional[str]:
        """Extract text from HTML file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        return self._extract_html_text(html_content)
    
    def _extract_html_text(self, html_content: str) -> Optional[str]:
        """Extract clean text from HTML content"""
        # Try inscriptis first (better formatting preservation)
        if INSCRIPTIS_AVAILABLE:
            try:
                text = get_text(html_content)
                if text.strip():
                    return text.strip()
            except:
                pass
        
        # Fall back to BeautifulSoup
        if BS4_AVAILABLE:
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    script.decompose()
                
                # Extract text
                text = soup.get_text(separator=' ', strip=True)
                
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text)
                return text.strip() if text.strip() else None
                
            except Exception as e:
                print(f"BeautifulSoup HTML parsing failed: {e}")
        
        # Fallback: basic HTML tag removal
        try:
            # Remove HTML tags
            clean = re.compile('<.*?>')
            text = re.sub(clean, ' ', html_content)
            
            # Clean up whitespace and decode HTML entities
            import html
            text = html.unescape(text)
            text = re.sub(r'\s+', ' ', text)
            return text.strip() if text.strip() else None
            
        except Exception as e:
            print(f"Basic HTML cleaning failed: {e}")
            return None
    
    def _extract_pdf_file(self, file_path: str) -> Optional[str]:
        """Extract text from PDF file"""
        # Try PyMuPDF first (better performance and accuracy)
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
                
                if text.strip():
                    return text.strip()
            except Exception as e:
                print(f"PyMuPDF PDF extraction failed: {e}")
        
        # Fall back to PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                text = ""
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                
                if text.strip():
                    return text.strip()
            except Exception as e:
                print(f"PyPDF2 extraction failed: {e}")
        
        print("No PDF libraries available for extraction")
        return None
    
    def _extract_pdf_from_bytes(self, pdf_bytes: bytes) -> Optional[str]:
        """Extract text from PDF bytes (from URL)"""
        try:
            # Save bytes to temporary file and process
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_bytes)
                tmp_path = tmp_file.name
            
            try:
                text = self._extract_pdf_file(tmp_path)
                return text
            finally:
                os.unlink(tmp_path)  # Clean up temp file
                
        except Exception as e:
            print(f"Error processing PDF bytes: {e}")
            return None
    
    def get_input_type(self, input_path: str) -> str:
        """Determine the type of input"""
        if self._is_url(input_path):
            return "url"
        elif os.path.exists(input_path):
            ext = Path(input_path).suffix.lower()
            if ext == '.pdf':
                return "pdf"
            elif ext in ['.html', '.htm']:
                return "html"
            elif ext == '.txt':
                return "text"
            else:
                return "file"
        else:
            return "text"


def test_input_processor():
    """Test function for the input processor"""
    processor = InputProcessor()
    
    # Test cases
    test_cases = [
        "This is a simple text input",
        "https://httpbin.org/html",  # Test URL
        "/path/to/nonexistent.txt",  # Test non-existent file
    ]
    
    for test_input in test_cases:
        print(f"\nTesting: {test_input}")
        result = processor.process_input(test_input)
        print(f"Type: {processor.get_input_type(test_input)}")
        print(f"Result: {'Success' if result else 'Failed'}")
        if result and len(result) < 200:
            print(f"Content: {result[:100]}...")


if __name__ == "__main__":
    test_input_processor()