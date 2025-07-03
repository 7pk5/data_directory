import requests
import time
import logging
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
import validators
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def get_page_info(self, url: str) -> Dict:
        """
        Get basic information about a webpage without full content download
        """
        if not validators.url(url):
            return {"error": "Invalid URL"}
        
        try:
            # Make HEAD request first to get headers
            response = self.session.head(url, timeout=10, allow_redirects=True)
            
            page_info = {
                "url": url,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', ''),
                "content_length": response.headers.get('content-length', 0),
                "server": response.headers.get('server', ''),
                "last_modified": response.headers.get('last-modified', ''),
                "accessible": response.status_code == 200
            }
            
            # Determine file type
            page_info["file_type"] = self._determine_file_type(
                page_info["content_type"], 
                url
            )
            
            return page_info
            
        except requests.RequestException as e:
            logger.error(f"Error accessing {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "accessible": False,
                "file_type": "unknown"
            }
    
    def get_page_content(self, url: str, max_size: int = 1024*1024) -> Tuple[str, Dict]:
        """
        Get page content with size limits for analysis
        """
        try:
            response = self.session.get(url, timeout=15, stream=True)
            response.raise_for_status()
            
            # Check content size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > max_size:
                return "", {"error": "Content too large"}
            
            # Read content with size limit
            content = ""
            size = 0
            for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
                if chunk:
                    content += chunk
                    size += len(chunk.encode('utf-8'))
                    if size > max_size:
                        break
            
            return content, {
                "size": size,
                "encoding": response.encoding,
                "content_type": response.headers.get('content-type', '')
            }
            
        except Exception as e:
            logger.error(f"Error getting content from {url}: {str(e)}")
            return "", {"error": str(e)}
    
    def _determine_file_type(self, content_type: str, url: str) -> str:
        """
        Determine file type from content-type header and URL
        """
        content_type = content_type.lower()
        url_lower = url.lower()
        
        if 'pdf' in content_type or url_lower.endswith('.pdf'):
            return "PDF"
        elif 'excel' in content_type or 'spreadsheet' in content_type or \
             url_lower.endswith(('.xlsx', '.xls')):
            return "Excel"
        elif 'csv' in content_type or url_lower.endswith('.csv'):
            return "CSV"
        elif 'json' in content_type or url_lower.endswith('.json'):
            return "JSON/API"
        elif 'xml' in content_type or url_lower.endswith('.xml'):
            return "XML"
        elif 'html' in content_type or 'text/html' in content_type:
            return "Web Page"
        else:
            return "Unknown"
