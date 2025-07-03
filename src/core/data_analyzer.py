"""
Data Source Analyzer for Manufacturing Data Collection
Intelligently analyzes web search results to determine document type, relevance, and extraction method
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Types of documents found in search results"""
    PDF = "PDF"
    EXCEL = "Excel"
    WEB_PAGE = "Web Page"
    API = "API"
    DATABASE = "Database"
    DIRECTORY = "Directory"
    UNKNOWN = "Unknown"

class ExtractionMethod(Enum):
    """Recommended extraction methods"""
    MANUAL_DOWNLOAD = "Manual Download"
    WEB_SCRAPING = "Web Scraping"
    API_CALL = "API Call"
    FORM_SUBMISSION = "Form Submission"
    PAID_ACCESS = "Paid Access"
    REGISTRATION_REQUIRED = "Registration Required"
    NOT_ACCESSIBLE = "Not Accessible"

@dataclass
class DataSourceAnalysis:
    """Analysis result for a data source"""
    url: str
    title: str
    domain: str
    document_type: DocumentType
    relevance_score: float
    estimated_rows: int
    estimated_fields: int
    extraction_method: ExtractionMethod
    data_description: str
    contact_fields_available: bool
    year_published: Optional[str]
    source_organization: str
    requires_payment: bool
    data_freshness: str
    confidence_score: float

class DataSourceAnalyzer:
    """Analyzes search results to understand data sources"""
    
    def __init__(self):
        self.domain_keywords = self._get_domain_keywords()
        self.quality_indicators = self._get_quality_indicators()
        self.document_patterns = self._get_document_patterns()
    
    def _get_domain_keywords(self) -> Dict[str, List[str]]:
        """Keywords that indicate relevance to each domain"""
        return {
            "Chemical_Petrochemical": [
                "chemical", "petrochemical", "pharmaceutical", "polymer", "fertilizer",
                "refinery", "chemicals", "pharma", "coating", "paint", "resin", "catalyst",
                "specialty chemicals", "fine chemicals", "bulk chemicals", "agrochemicals"
            ],
            "Shipping": [
                "shipping", "logistics", "maritime", "port", "cargo", "freight",
                "vessel", "container", "marine", "transport", "supply chain", "warehousing",
                "forwarding", "customs", "import", "export", "fleet"
            ],
            "Sports_Equipment": [
                "sports", "fitness", "athletics", "equipment", "gear", "recreation",
                "sporting goods", "exercise", "outdoor", "games", "gymnasium", "playground",
                "cricket", "football", "badminton", "tennis", "hockey"
            ],
            "EdTech": [
                "edtech", "education", "learning", "e-learning", "digital education",
                "educational technology", "online learning", "training", "lms", "mooc",
                "virtual classroom", "educational software", "learning management"
            ]
        }
    
    def _get_quality_indicators(self) -> Dict[str, List[str]]:
        """Indicators of high-quality data sources"""
        return {
            "high_quality": [
                "database", "directory", "list", "registry", "association",
                "government", "official", "certified", "verified", "comprehensive"
            ],
            "contact_data": [
                "email", "phone", "contact", "address", "details", "directory"
            ],
            "recent": [
                "2024", "2025", "latest", "updated", "current", "recent"
            ],
            "extensive": [
                "complete", "comprehensive", "all", "entire", "full", "detailed"
            ]
        }
    
    def _get_document_patterns(self) -> Dict[DocumentType, List[str]]:
        """URL and content patterns for different document types"""
        return {
            DocumentType.PDF: [".pdf", "pdf", "document", "report"],
            DocumentType.EXCEL: [".xlsx", ".xls", "excel", "spreadsheet"],
            DocumentType.WEB_PAGE: ["html", "htm", "web", "site"],
            DocumentType.API: ["api", "json", "xml", "rest"],
            DocumentType.DATABASE: ["database", "db", "data"],
            DocumentType.DIRECTORY: ["directory", "listing", "catalog"]
        }
    
    def analyze_search_result(self, result: Dict, target_domain: str) -> DataSourceAnalysis:
        """Analyze a single search result"""
        url = result.get('link', '')
        title = result.get('title', '')
        snippet = result.get('snippet', '')
        
        # Determine document type
        doc_type = self._determine_document_type(url, title, snippet)
        
        # Calculate relevance score
        relevance = self._calculate_relevance(title, snippet, target_domain)
        
        # Estimate data size
        rows, fields = self._estimate_data_size(title, snippet, doc_type)
        
        # Determine extraction method
        extraction_method = self._determine_extraction_method(url, title, snippet, doc_type)
        
        # Extract metadata
        metadata = self._extract_metadata(title, snippet, url)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(doc_type, relevance, extraction_method)
        
        return DataSourceAnalysis(
            url=url,
            title=title,
            domain=urlparse(url).netloc,
            document_type=doc_type,
            relevance_score=relevance,
            estimated_rows=rows,
            estimated_fields=fields,
            extraction_method=extraction_method,
            data_description=self._generate_description(title, snippet),
            contact_fields_available=self._has_contact_fields(title, snippet),
            year_published=metadata.get('year'),
            source_organization=metadata.get('organization') or '',
            requires_payment=self._requires_payment(title, snippet),
            data_freshness=metadata.get('freshness') or 'Unknown',
            confidence_score=confidence
        )
    
    def _determine_document_type(self, url: str, title: str, snippet: str) -> DocumentType:
        """Determine the type of document from URL and content"""
        text = f"{url} {title} {snippet}".lower()
        
        if any(pattern in text for pattern in ['.pdf', 'pdf']):
            return DocumentType.PDF
        elif any(pattern in text for pattern in ['.xlsx', '.xls', 'excel']):
            return DocumentType.EXCEL
        elif any(pattern in text for pattern in ['api', 'json', 'xml']):
            return DocumentType.API
        elif any(pattern in text for pattern in ['database', 'db']):
            return DocumentType.DATABASE
        elif any(pattern in text for pattern in ['directory', 'listing']):
            return DocumentType.DIRECTORY
        else:
            return DocumentType.WEB_PAGE
    
    def _calculate_relevance(self, title: str, snippet: str, target_domain: str) -> float:
        """Calculate relevance score (0-1)"""
        text = f"{title} {snippet}".lower()
        
        # Get domain-specific keywords
        keywords = self.domain_keywords.get(target_domain, [])
        
        # Handle empty keywords list to prevent division by zero
        if not keywords:
            # Use basic scoring for custom domains without predefined keywords
            keyword_score = 0.5  # Default neutral score
        else:
            # Count keyword matches
            keyword_matches = sum(1 for keyword in keywords if keyword in text)
            keyword_score = min(keyword_matches / len(keywords), 1.0)
        
        # Check for quality indicators
        quality_matches = sum(1 for indicator in self.quality_indicators["high_quality"] if indicator in text)
        quality_score = min(quality_matches / 3, 1.0)
        
        # Check for Indian context
        india_keywords = ["india", "indian", "bharath", "bharat"]
        india_score = 1.0 if any(keyword in text for keyword in india_keywords) else 0.3
        
        # Weighted relevance score
        relevance = (keyword_score * 0.5) + (quality_score * 0.3) + (india_score * 0.2)
        
        return round(relevance, 2)
    
    def _estimate_data_size(self, title: str, snippet: str, doc_type: DocumentType) -> Tuple[int, int]:
        """Estimate number of rows and fields in the data source"""
        text = f"{title} {snippet}".lower()
        
        # Extract numbers from text with better filtering
        numbers = []
        for match in re.findall(r'\d+', text):
            num = int(match)
            # Filter reasonable company/data counts (between 10 and 100,000)
            if 10 <= num <= 100000:
                numbers.append(num)
        
        # Base estimates by document type
        base_estimates = {
            DocumentType.PDF: (100, 8),
            DocumentType.EXCEL: (500, 12),
            DocumentType.WEB_PAGE: (50, 6),
            DocumentType.API: (1000, 15),
            DocumentType.DATABASE: (2000, 20),
            DocumentType.DIRECTORY: (300, 10),
            DocumentType.UNKNOWN: (50, 5)
        }
        
        base_rows, base_fields = base_estimates[doc_type]
        
        # Adjust based on content indicators
        if any(word in text for word in ["comprehensive", "complete", "all", "entire", "full"]):
            base_rows = int(base_rows * 3)
            base_fields = int(base_fields * 1.5)
        
        if any(word in text for word in ["top", "major", "leading"]):
            base_rows = min(base_rows, 200)
        
        # State-specific searches typically have fewer results
        if any(state in text for state in ["gujarat", "maharashtra", "tamil nadu", "karnataka"]):
            base_rows = int(base_rows * 0.7)
        
        # If specific numbers are mentioned, use the largest reasonable one
        if numbers:
            largest_number = max(numbers)
            base_rows = largest_number
        
        return int(base_rows), int(base_fields)
    
    def _determine_extraction_method(self, url: str, title: str, snippet: str, doc_type: DocumentType) -> ExtractionMethod:
        """Determine the best extraction method"""
        text = f"{url} {title} {snippet}".lower()
        
        # Check for access restrictions
        if any(word in text for word in ["login", "register", "subscription", "premium"]):
            return ExtractionMethod.REGISTRATION_REQUIRED
        
        if any(word in text for word in ["paid", "purchase", "buy", "price"]):
            return ExtractionMethod.PAID_ACCESS
        
        # Check for API indicators
        if doc_type == DocumentType.API or "api" in text:
            return ExtractionMethod.API_CALL
        
        # PDF and Excel files
        if doc_type in [DocumentType.PDF, DocumentType.EXCEL]:
            return ExtractionMethod.MANUAL_DOWNLOAD
        
        # Web pages and directories
        if doc_type in [DocumentType.WEB_PAGE, DocumentType.DIRECTORY, DocumentType.DATABASE]:
            return ExtractionMethod.WEB_SCRAPING
        
        return ExtractionMethod.WEB_SCRAPING
    
    def _extract_metadata(self, title: str, snippet: str, url: str) -> Dict[str, Optional[str]]:
        """Extract metadata like year, organization, freshness"""
        text = f"{title} {snippet}".lower()
        
        # Extract year
        year_match = re.search(r'20(2[0-9]|1[0-9])', text)
        year = year_match.group() if year_match else None
        
        # Extract organization
        domain = urlparse(url).netloc
        organization = domain.replace('www.', '').replace('.com', '').replace('.org', '').replace('.in', '')
        
        # Determine freshness
        freshness = "Unknown"
        if any(word in text for word in ["2024", "2025", "latest", "current"]):
            freshness = "Recent"
        elif any(word in text for word in ["2022", "2023"]):
            freshness = "Moderate"
        elif any(word in text for word in ["2020", "2021"]):
            freshness = "Old"
        
        return {
            'year': year,
            'organization': organization,
            'freshness': freshness
        }
    
    def _has_contact_fields(self, title: str, snippet: str) -> bool:
        """Check if the source likely contains contact information"""
        text = f"{title} {snippet}".lower()
        contact_indicators = self.quality_indicators["contact_data"]
        return any(indicator in text for indicator in contact_indicators)
    
    def _requires_payment(self, title: str, snippet: str) -> bool:
        """Check if the source requires payment"""
        text = f"{title} {snippet}".lower()
        payment_indicators = ["paid", "premium", "subscription", "purchase", "buy", "price"]
        return any(indicator in text for indicator in payment_indicators)
    
    def _generate_description(self, title: str, snippet: str) -> str:
        """Generate a concise description of the data source"""
        # Extract key phrases and create description
        key_words = []
        text = f"{title} {snippet}".lower()
        
        if "directory" in text:
            key_words.append("Company Directory")
        if "list" in text:
            key_words.append("Company List")
        if "database" in text:
            key_words.append("Database")
        if "association" in text:
            key_words.append("Industry Association")
        if "export" in text:
            key_words.append("Export Companies")
        
        if not key_words:
            key_words.append("Company Data")
        
        return " | ".join(key_words)
    
    def _calculate_confidence(self, doc_type: DocumentType, relevance: float, extraction_method: ExtractionMethod) -> float:
        """Calculate overall confidence score"""
        type_score = {
            DocumentType.DATABASE: 0.9,
            DocumentType.DIRECTORY: 0.8,
            DocumentType.EXCEL: 0.85,
            DocumentType.PDF: 0.7,
            DocumentType.API: 0.95,
            DocumentType.WEB_PAGE: 0.6,
            DocumentType.UNKNOWN: 0.3
        }
        
        method_score = {
            ExtractionMethod.API_CALL: 0.9,
            ExtractionMethod.MANUAL_DOWNLOAD: 0.8,
            ExtractionMethod.WEB_SCRAPING: 0.7,
            ExtractionMethod.REGISTRATION_REQUIRED: 0.5,
            ExtractionMethod.PAID_ACCESS: 0.4,
            ExtractionMethod.NOT_ACCESSIBLE: 0.1
        }
        
        confidence = (type_score.get(doc_type, 0.5) * 0.4 + 
                     relevance * 0.4 + 
                     method_score.get(extraction_method, 0.5) * 0.2)
        
        return round(confidence, 2)
