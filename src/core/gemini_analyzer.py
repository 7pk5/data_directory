"""
Gemini LLM Integration for Intelligent Manufacturing Data Analysis
Provides context-aware analysis and structured output formatting
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# Import Google Generative AI with comprehensive error handling
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
    logger.info("Google Generative AI imported successfully")
except ImportError as e:
    logger.warning(f"Google Generative AI not available: {e}")
    GENAI_AVAILABLE = False
    genai = None
except Exception as e:
    logger.warning(f"Google Generative AI import issue: {e}")
    GENAI_AVAILABLE = False
    genai = None
    
from config.config import GEMINI_API_KEY

@dataclass
class StructuredDataPoint:
    """Structured data point in the required format"""
    industry: str
    sector: str
    document_title: str
    data_link: str
    format: str
    action_required: str
    datapoints_contained: str
    no_of_datapoints: int
    coverage: str
    source: str
    year: str
    additional_comment: str

class GeminiAnalyzer:
    """Gemini-powered intelligent data analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini analyzer"""
        self.api_key = api_key or GEMINI_API_KEY
        self.enabled = False
        self.model = None
        
        if not GENAI_AVAILABLE:
            logger.warning("Google Generative AI not available. Install with: pip install google-generativeai")
            return
            
        if not self.api_key:
            logger.warning("Gemini API key not provided. LLM features will be disabled.")
            return
        
        try:
            # Try to configure and initialize Gemini with dynamic attribute access
            if genai:
                # Use getattr for safer access to methods that may not exist
                configure_func = getattr(genai, 'configure', None)
                if configure_func:
                    configure_func(api_key=self.api_key)
                    
                model_class = getattr(genai, 'GenerativeModel', None)
                if model_class:
                    # Try different model names based on API version
                    model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'models/gemini-pro']
                    
                    for model_name in model_names:
                        try:
                            self.model = model_class(model_name)
                            self.enabled = True
                            logger.info(f"Gemini LLM initialized successfully with model: {model_name}")
                            break
                        except Exception as model_error:
                            logger.debug(f"Failed to initialize model {model_name}: {model_error}")
                            continue
                    
                    if not self.enabled:
                        logger.warning("Could not initialize any Gemini model")
                        self.enabled = False
                else:
                    logger.warning("GenerativeModel class not available")
                    self.enabled = False
            else:
                logger.warning("genai module not available")
                self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.enabled = False
        
        # Domain-specific context (initialize regardless of LLM status)
        self.domain_contexts = self._get_domain_contexts()
        self.association_patterns = self._get_association_patterns()
        
    def _get_domain_contexts(self) -> Dict[str, Dict]:
        """Get comprehensive domain context for intelligent analysis"""
        return {
            "Chemical_Petrochemical": {
                "industry": "Chemical & Petrochemical",
                "key_sectors": ["Pharmaceuticals", "Specialty Chemicals", "Petrochemicals", "Fertilizers", "Paints & Coatings", "Polymers", "Agrochemicals"],
                "associations": ["Indian Chemical Council (ICC)", "Pharmaceutical Export Promotion Council", "All India Plastic Manufacturers Association", "Federation of Indian Chambers of Commerce"],
                "data_types": ["Manufacturing facilities", "Export-import data", "Company directories", "Trade associations", "Regulatory compliance"],
                "search_focus": "chemical manufacturing companies, pharmaceutical exporters, petrochemical plants, chemical associations India, specialty chemicals directory"
            },
            "Shipping": {
                "industry": "Shipping & Logistics",
                "key_sectors": ["Maritime Transport", "Port Operations", "Freight Forwarding", "Container Shipping", "Warehousing", "Supply Chain"],
                "associations": ["Indian National Shipowners Association (INSA)", "Container Shipping Lines Association", "Federation of Freight Forwarders Associations", "Shipping Corporation of India"],
                "data_types": ["Shipping companies", "Port directories", "Logistics providers", "Freight forwarders", "Maritime services"],
                "search_focus": "shipping companies India, maritime transport, port operators, logistics providers, freight forwarders directory"
            },
            "Sports_Equipment": {
                "industry": "Sports Equipment Manufacturing",
                "key_sectors": ["Cricket Equipment", "Football & Hockey Gear", "Fitness Equipment", "Outdoor Sports", "Athletic Wear", "Gymnasium Equipment"],
                "associations": ["Sports Goods Export Promotion Council", "All India Sports Goods Manufacturers Federation", "Indian Olympic Association", "Sports Authority of India"],
                "data_types": ["Sports equipment manufacturers", "Export data", "Sports associations", "Equipment suppliers", "Athletic gear companies"],
                "search_focus": "sports equipment manufacturers India, sports goods exporters, athletic equipment suppliers, sports associations directory"
            },
            "EdTech": {
                "industry": "Educational Technology",
                "key_sectors": ["E-Learning Platforms", "Educational Software", "Digital Content", "Learning Management Systems", "Online Training", "Virtual Classrooms"],
                "associations": ["Internet and Mobile Association of India", "Educational Technology Association", "National Association of Software and Services Companies", "Indian Chamber of Commerce"],
                "data_types": ["EdTech companies", "Educational platforms", "Digital learning providers", "Training organizations", "Technology solutions"],
                "search_focus": "edtech companies India, educational technology providers, e-learning platforms, digital education solutions, online training providers"
            }
        }
    
    def _get_association_patterns(self) -> Dict[str, List[str]]:
        """Patterns to identify industry associations"""
        return {
            "association_keywords": [
                "association", "federation", "council", "chamber", "society", "organization",
                "board", "institute", "authority", "commission", "confederation"
            ],
            "company_keywords": [
                "company", "corporation", "limited", "ltd", "private", "pvt", "industries",
                "manufacturers", "enterprises", "group", "international"
            ],
            "directory_keywords": [
                "directory", "list", "database", "registry", "catalog", "index", "listing"
            ]
        }
    
    def generate_smart_queries(self, domain_key: str, query_count: int = 20) -> List[Dict]:
        """Generate intelligent, domain-specific search queries using Gemini"""
        if not self.enabled:
            logger.warning("Gemini not available, using basic query generation")
            return self._fallback_query_generation(domain_key, query_count)
        
        try:
            domain_context = self.domain_contexts.get(domain_key, {})
            industry_type = self._get_industry_type(domain_key)
            
            # Create smart, domain-aware prompt for Gemini
            prompt = self._create_domain_specific_prompt(domain_context, industry_type, query_count)
            
            if self.model and hasattr(self.model, 'generate_content'):
                try:
                    response = self.model.generate_content(prompt)
                    if response and hasattr(response, 'text'):
                        enhanced_queries = self._parse_gemini_queries(response.text, domain_key, query_count)
                        logger.info(f"Generated {len(enhanced_queries)} enhanced queries for {domain_key}")
                        return enhanced_queries
                    else:
                        logger.warning("Invalid response from Gemini model")
                        return self._fallback_query_generation(domain_key, query_count)
                except Exception as e:
                    logger.error(f"Error generating content with Gemini: {e}")
                    return self._fallback_query_generation(domain_key, query_count)
            else:
                logger.warning("Model not available for content generation")
                return self._fallback_query_generation(domain_key, query_count)
            
        except Exception as e:
            logger.error(f"Gemini query generation failed: {e}")
            return self._fallback_query_generation(domain_key, query_count)
    
    def _get_industry_type(self, domain_key: str) -> str:
        """Determine the industry type for appropriate query generation"""
        manufacturing_domains = ["Chemical_Petrochemical", "Sports_Equipment"]
        service_domains = ["EdTech", "Shipping"]
        
        if domain_key in manufacturing_domains:
            return "manufacturing"
        elif domain_key in service_domains:
            return "services"
        else:
            return "general"
    
    def _create_domain_specific_prompt(self, domain_context: Dict, industry_type: str, query_count: int) -> str:
        """Create domain-specific prompts based on industry type"""
        
        industry = domain_context.get('industry', 'Unknown')
        sectors = ', '.join(domain_context.get('key_sectors', []))
        
        if industry_type == "services":
            # For service industries like EdTech, focus on companies, platforms, providers
            prompt = f"""
            Generate {query_count} specific search queries to find comprehensive data about the {industry} sector in India.

            Industry: {industry}
            Key Sectors: {sectors}

            Generate search queries that will find:
            1. Companies and service providers in this sector
            2. Industry associations and trade bodies
            3. Company directories with contact information  
            4. Government registrations and certifications
            5. Industry reports and market research
            6. Trade shows, conferences, and exhibitions
            7. Startup databases and investment information
            8. Professional networks and communities
            9. Regulatory bodies and compliance requirements
            10. Educational institutions and training providers

            Focus specifically on:
            - Service companies, platforms, and technology providers
            - Software and digital solution providers  
            - Consulting and professional services
            - Training and education providers
            - Industry networks and communities

            IMPORTANT:
            - Focus on INDIA market only
            - Do NOT use manufacturing terms like "manufacturers", "factories", "production"
            - Use appropriate terms like "companies", "providers", "platforms", "services"
            - Include specific Indian organizations and associations
            - Target specific data sources like directories, databases, reports

            Format each query as: "search query text"
            Make queries specific and actionable for finding business data.
            """
            
        elif industry_type == "manufacturing":
            # For manufacturing industries, focus on manufacturers, exporters, suppliers
            prompt = f"""
            Generate {query_count} specific search queries to find comprehensive data about the {industry} manufacturing sector in India.

            Industry: {industry}
            Key Sectors: {sectors}

            Generate search queries that will find:
            1. Manufacturing companies and production facilities
            2. Export-import data and trade statistics
            3. Industry associations and trade bodies
            4. Company directories with contact information
            5. Government registrations and certifications
            6. Supplier and vendor databases
            7. Trade shows and exhibitions
            8. Quality certifications and standards
            9. Raw material suppliers and distributors
            10. Manufacturing clusters and industrial zones

            Focus specifically on:
            - Manufacturing companies and production units
            - Exporters and importers
            - Suppliers and distributors
            - Industrial associations and trade bodies
            - Government regulatory databases

            IMPORTANT:
            - Focus on INDIA market only
            - Use manufacturing-specific terms appropriately
            - Include specific Indian organizations and associations
            - Target specific data sources like directories, databases, reports

            Format each query as: "search query text"
            Make queries specific and actionable for finding business data.
            """
        else:
            # General prompt for other industries
            prompt = f"""
            Generate {query_count} specific search queries to find comprehensive business data about the {industry} sector in India.

            Industry: {industry}
            Key Sectors: {sectors}

            Generate search queries that will find:
            1. Companies and organizations in this sector
            2. Industry associations and trade bodies
            3. Company directories with contact information
            4. Government registrations and databases
            5. Industry reports and market research
            6. Trade shows and exhibitions
            7. Professional networks and communities
            8. Regulatory compliance requirements
            9. Investment and funding information
            10. Educational and training resources

            IMPORTANT:
            - Focus on INDIA market only
            - Use industry-appropriate terminology
            - Include specific Indian organizations
            - Target actionable data sources

            Format each query as: "search query text"
            """
        
        return prompt
    
    def _parse_gemini_queries(self, response_text: str, domain_key: str, max_queries: int = 20) -> List[Dict]:
        """Parse Gemini response to extract queries"""
        queries = []
        lines = response_text.split('\n')
        
        for i, line in enumerate(lines):
            if len(queries) >= max_queries:
                break
                
            # Extract queries from quotes or numbered lists
            query_match = re.search(r'"([^"]+)"', line)
            if query_match:
                query = query_match.group(1)
            elif re.match(r'^\d+\.\s*(.+)', line):
                match = re.match(r'^\d+\.\s*(.+)', line)
                if match:
                    query = match.group(1)
                else:
                    continue
            else:
                continue
            
            if len(query) > 10:  # Valid query
                queries.append({
                    "query_id": f"{domain_key}_gemini_{len(queries)+1}",
                    "domain": domain_key,
                    "search_query": query,
                    "query_type": "gemini_enhanced",
                    "source": "llm_generated"
                })
        
        return queries[:max_queries]  # Ensure we don't exceed the limit
    
    def _fallback_query_generation(self, domain_key: str, query_count: int = 20) -> List[Dict]:
        """Fallback query generation when Gemini is not available"""
        domain_context = self.domain_contexts.get(domain_key, {})
        industry = domain_context.get('industry', domain_key)
        industry_type = self._get_industry_type(domain_key)
        
        # Create domain-appropriate queries
        if industry_type == "services":
            # For service industries like EdTech
            base_terms = [
                f"{industry} companies in India",
                f"{industry} service providers India",
                f"{industry} platforms and solutions India",
                f"{industry} startups and companies India",
                f"{industry} associations and organizations India",
                f"{industry} directory with contact details",
                f"{industry} industry report India",
                f"{industry} market research India",
                f"{industry} conferences and events India",
                f"{industry} training and certification providers India"
            ]
        elif industry_type == "manufacturing":
            # For manufacturing industries
            base_terms = [
                f"{industry} manufacturers in India",
                f"{industry} exporters and suppliers India",
                f"{industry} companies database India",
                f"{industry} industry associations India",
                f"{industry} export import data India",
                f"{industry} trade directory India",
                f"{industry} manufacturing clusters India",
                f"{industry} suppliers contact details India",
                f"{industry} exhibitions and trade shows India",
                f"{industry} regulatory compliance India"
            ]
        else:
            # General fallback
            base_terms = [
                f"{industry} companies in India",
                f"{industry} organizations India",
                f"{industry} directory India",
                f"{industry} associations India",
                f"{industry} database India"
            ]
        
        queries = []
        for i, term in enumerate(base_terms[:query_count]):
            queries.append({
                "query_id": f"{domain_key}_fallback_{i+1}",
                "domain": domain_key,
                "search_query": term,
                "query_type": "fallback_enhanced",
                "source": "rule_based"
            })
        
        return queries
    
    def analyze_search_result_with_llm(self, result: Dict, domain_key: str, original_analysis) -> StructuredDataPoint:
        """Analyze search result using Gemini for structured output"""
        if not self.enabled:
            return self._convert_to_structured_format(result, domain_key, original_analysis)
        
        try:
            domain_context = self.domain_contexts.get(domain_key, {})
            
            prompt = f"""
            Analyze this search result for the {domain_context.get('industry')} sector and provide structured analysis:

            Search Result:
            - Title: {result.get('title', '')}
            - URL: {result.get('link', '')}
            - Description: {result.get('snippet', '')}

            Domain Context: {domain_context.get('industry')}
            Key Sectors: {', '.join(domain_context.get('key_sectors', []))}

            Please analyze and provide EXACTLY these fields:
            1. INDUSTRY: {domain_context.get('industry')}
            2. SECTOR: (Which specific sector within the industry - choose from: {', '.join(domain_context.get('key_sectors', []))})
            3. DOCUMENT_TITLE: (Clean, descriptive title)
            4. DATA_LINK: {result.get('link', '')}
            5. FORMAT: (Website/PDF/Excel/Word/API - determine from URL and content)
            6. ACTION_REQUIRED: (Website Crawling/PDF Download/Manual Copy/API Integration/Registration Required)
            7. DATAPOINTS_CONTAINED: (What type of data: company names, contact details, financial data, etc.)
            8. NO_OF_DATAPOINTS: (Estimated number - be specific, e.g., 150, 500, 1200)
            9. COVERAGE: (Geographic scope: All India/State-specific/Regional/City-specific)
            10. SOURCE: (Organization or website name)
            11. YEAR: (Publication year if mentioned, otherwise 'Unknown')
            12. ADDITIONAL_COMMENT: (Relevance, data quality, special notes)

            Respond in this exact format:
            INDUSTRY: [value]
            SECTOR: [value]
            DOCUMENT_TITLE: [value]
            DATA_LINK: [value]
            FORMAT: [value]
            ACTION_REQUIRED: [value]
            DATAPOINTS_CONTAINED: [value]
            NO_OF_DATAPOINTS: [value]
            COVERAGE: [value]
            SOURCE: [value]
            YEAR: [value]
            ADDITIONAL_COMMENT: [value]
            """
            
            if self.model and hasattr(self.model, 'generate_content'):
                try:
                    response = self.model.generate_content(prompt)
                    if response and hasattr(response, 'text'):
                        return self._parse_structured_response(response.text, result, domain_key)
                    else:
                        logger.warning("Invalid response from Gemini model")
                        return self._convert_to_structured_format(result, domain_key, original_analysis)
                except Exception as e:
                    logger.error(f"Error generating content with Gemini: {e}")
                    return self._convert_to_structured_format(result, domain_key, original_analysis)
            else:
                logger.warning("Model not available for content generation")
                return self._convert_to_structured_format(result, domain_key, original_analysis)
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return self._convert_to_structured_format(result, domain_key, original_analysis)
    
    def _parse_structured_response(self, response_text: str, result: Dict, domain_key: str) -> StructuredDataPoint:
        """Parse Gemini structured response"""
        try:
            fields = {}
            for line in response_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    fields[key.strip().lower().replace('_', '')] = value.strip()
            
            return StructuredDataPoint(
                industry=fields.get('industry', self.domain_contexts.get(domain_key, {}).get('industry', domain_key)),
                sector=fields.get('sector', 'General'),
                document_title=fields.get('documenttitle', result.get('title', 'Unknown')),
                data_link=fields.get('datalink', result.get('link', '')),
                format=fields.get('format', 'Website'),
                action_required=fields.get('actionrequired', 'Website Crawling'),
                datapoints_contained=fields.get('datapointscontained', 'Company Information'),
                no_of_datapoints=self._extract_number(fields.get('noofdatapoints', '100')),
                coverage=fields.get('coverage', 'All India'),
                source=fields.get('source', 'Unknown'),
                year=fields.get('year', 'Unknown'),
                additional_comment=fields.get('additionalcomment', 'Requires further analysis')
            )
            
        except Exception as e:
            logger.error(f"Failed to parse structured response: {e}")
            return self._convert_to_structured_format(result, domain_key, None)
    
    def _extract_number(self, text: str) -> int:
        """Extract number from text"""
        numbers = re.findall(r'\d+', str(text))
        return int(numbers[0]) if numbers else 100
    
    def _convert_to_structured_format(self, result: Dict, domain_key: str, original_analysis) -> StructuredDataPoint:
        """Convert basic analysis to structured format"""
        domain_context = self.domain_contexts.get(domain_key, {})
        
        # Determine format from URL
        url = result.get('link', '').lower()
        if '.pdf' in url:
            format_type = 'PDF'
            action = 'PDF Download'
        elif any(ext in url for ext in ['.xlsx', '.xls']):
            format_type = 'Excel'
            action = 'PDF Download'
        elif 'api' in url:
            format_type = 'API'
            action = 'API Integration'
        else:
            format_type = 'Website'
            action = 'Website Crawling'
        
        # Estimate datapoints
        title_text = result.get('title', '').lower()
        snippet_text = result.get('snippet', '').lower()
        
        datapoints = 100  # Default
        if any(word in title_text + snippet_text for word in ['comprehensive', 'complete', 'all']):
            datapoints = 1000
        elif any(word in title_text + snippet_text for word in ['directory', 'database']):
            datapoints = 500
        
        return StructuredDataPoint(
            industry=domain_context.get('industry', domain_key),
            sector=domain_context.get('key_sectors', ['General'])[0],
            document_title=result.get('title', 'Unknown'),
            data_link=result.get('link', ''),
            format=format_type,
            action_required=action,
            datapoints_contained='Company Information, Contact Details',
            no_of_datapoints=datapoints,
            coverage='All India',
            source=result.get('link', '').split('/')[2] if '//' in result.get('link', '') else 'Unknown',
            year='Unknown',
            additional_comment='Standard analysis - LLM enhancement available'
        )
