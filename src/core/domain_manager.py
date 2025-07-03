"""
Domain Manager for Indian Manufacturing Data Collection
Handles domain-specific search query generation and management with LLM enhancement
"""

import logging
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re

# Import Gemini analyzer with fallback
try:
    from .gemini_analyzer import GeminiAnalyzer
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    GeminiAnalyzer = None

logger = logging.getLogger(__name__)

@dataclass
class Domain:
    """Represents a manufacturing domain with search configurations"""
    name: str
    keywords: List[str]
    specific_terms: List[str]
    state_variations: bool = True

class DomainManager:
    """Manages domains and generates targeted search queries with LLM enhancement"""
    
    def __init__(self, use_llm: bool = True):
        self.domains = self._initialize_domains()
        self.base_prompts = self._get_base_prompts()
        self.indian_states = self._get_indian_states()
        
        # Initialize Gemini analyzer if available and requested
        self.llm_analyzer = None
        if use_llm and GEMINI_AVAILABLE and GeminiAnalyzer:
            try:
                self.llm_analyzer = GeminiAnalyzer()
                if self.llm_analyzer.enabled:
                    logger.info("🤖 Gemini LLM integration enabled")
                else:
                    logger.warning("⚠️ Gemini LLM disabled (no API key)")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
        else:
            logger.info("📝 Using standard query generation (no LLM)")
    
    def _initialize_domains(self) -> Dict[str, Domain]:
        """Initialize all manufacturing domains with specific keywords"""
        return {
            "Chemical_Petrochemical": Domain(
                name="Chemical and Petrochemical",
                keywords=["chemical", "petrochemical", "pharmaceutical", "polymer", "fertilizer"],
                specific_terms=["chemical manufacturing", "petrochemical industry", "chemical companies"]
            ),
            "Shipping": Domain(
                name="Shipping",
                keywords=["shipping", "logistics", "maritime", "port", "cargo", "freight"],
                specific_terms=["shipping companies", "maritime industry", "logistics providers"]
            ),
            "Sports_Equipment": Domain(
                name="Sports Equipment",
                keywords=["sports equipment", "fitness", "athletics", "sports goods", "recreational"],
                specific_terms=["sports manufacturing", "fitness equipment", "sports goods industry"]
            ),
            "EdTech": Domain(
                name="EdTech",
                keywords=["edtech", "educational technology", "e-learning", "digital education"],
                specific_terms=["edtech companies", "educational software", "learning platforms"]
            )
        }
    
    def _get_base_prompts(self) -> List[str]:
        """Get the 29 base search prompts"""
        return [
            "Companies in the {domain} sector list India",
            "List of companies in {domain} industry in India", 
            "{domain} companies in India pdf",
            "Database of {domain} companies in India",
            "{domain} manufactures in India",
            "Small {domain} companies in India",
            "{domain} industry database",
            "List of {domain} companies with email id",
            "{domain} Database",
            "Indian {domain} companies database",
            "{domain} companies associations",
            "Associations in {domain} industry",
            "{domain} franchises in India",
            "{domain} industry exhibition list",
            "Exhibitions and tradeshow database of {domain} industry",
            "Exhibition list pdf for {domain} industry",
            "All India {domain} manufacturers data",
            "Companies data {domain}",
            "{domain} factories in India pdf",
            "{domain} Export companies list",
            "{domain} companies directory",
            "{domain} directory product list pdf",
            "{domain} companies contact details with email id",
            "Top 500 {domain} manufacturers list India",
            "B2b {domain} companies list",
            "All {domain} list {state}",  # State-specific
            "All India {domain} contact with phone number",
            "Exhibition directory /exhibition catalogue {domain}",
            "List of companies in {domain} 2025"
        ]
    
    def _get_indian_states(self) -> List[str]:
        """Get list of major Indian states for state-specific searches"""
        return [
            "West Bengal", "Maharashtra", "Gujarat", "Tamil Nadu", "Karnataka",
            "Andhra Pradesh", "Telangana", "Uttar Pradesh", "Rajasthan", "Punjab",
            "Haryana", "Madhya Pradesh", "Odisha", "Kerala", "Bihar"
        ]
    
    def generate_queries_for_domain(self, domain_key: str, query_count: int = 20, use_llm_only: bool = True) -> List[Dict]:
        """Generate search queries for a specific domain using LLM intelligence"""
        if domain_key not in self.domains:
            raise ValueError(f"Domain {domain_key} not found")
        
        domain = self.domains[domain_key]
        queries = []
        
        if use_llm_only and self.llm_analyzer and self.llm_analyzer.enabled:
            # Use only LLM-generated queries (smarter approach)
            try:
                llm_queries = self.llm_analyzer.generate_smart_queries(domain_key, query_count)
                queries.extend(llm_queries)
                logger.info(f"Generated {len(llm_queries)} LLM-powered queries for {domain.name}")
            except Exception as e:
                logger.error(f"LLM query generation failed: {e}")
                # Fallback to basic queries
                queries = self._generate_basic_queries(domain_key, domain, query_count)
        else:
            # Use basic rule-based queries
            queries = self._generate_basic_queries(domain_key, domain, query_count)
        
        logger.info(f"Generated {len(queries)} total queries for domain: {domain.name}")
        return queries
    
    def _generate_basic_queries(self, domain_key: str, domain, query_count: int) -> List[Dict]:
        """Generate basic queries when LLM is not available"""
        queries = []
        industry = domain.name
        
        # Create basic queries appropriate for the domain
        basic_templates = [
            f"{industry} companies in India",
            f"{industry} directory India",
            f"{industry} associations India",
            f"{industry} database with contact details",
            f"{industry} organizations list India",
            f"{industry} service providers India",
            f"{industry} market research India",
            f"{industry} industry report India",
            f"{industry} trade bodies India",
            f"{industry} professional networks India"
        ]
        
        # Extend if needed
        while len(basic_templates) < query_count:
            basic_templates.extend([
                f"{industry} companies {state} India" for state in ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune"]
            ])
        
        for i, template in enumerate(basic_templates[:query_count]):
            queries.append({
                "query_id": f"{domain_key}_basic_{i+1}",
                "domain": domain.name,
                "search_query": template,
                "query_type": "basic",
                "source": "rule_based"
            })
        
        return queries
    
    def _generate_base_queries(self, domain_key: str, domain) -> List[Dict]:
        """Generate the original base queries"""
        queries = []
        
        # Generate regular queries
        for i, prompt in enumerate(self.base_prompts, 1):
            if "{state}" in prompt:
                # Generate state-specific queries
                for state in self.indian_states:
                    query = prompt.format(domain=domain.keywords[0], state=state)
                    queries.append({
                        "query_id": f"{domain_key}_state_{len(queries)+1}",
                        "domain": domain.name,
                        "prompt_template": prompt,
                        "search_query": query,
                        "query_type": "state_specific",
                        "state": state,
                        "prompt_number": i
                    })
            else:
                # Try different keyword variations
                for keyword in domain.keywords[:2]:  # Use top 2 keywords to avoid too many queries
                    query = prompt.format(domain=keyword)
                    queries.append({
                        "query_id": f"{domain_key}_{len(queries)+1}",
                        "domain": domain.name,
                        "prompt_template": prompt,
                        "search_query": query,
                        "query_type": "general",
                        "keyword_used": keyword,
                        "prompt_number": i
                    })
        return queries
    
    def get_all_domains(self) -> List[str]:
        """Get list of all available domain keys"""
        return list(self.domains.keys())
    
    def get_domain_info(self, domain_key: str) -> Domain:
        """Get domain information"""
        if domain_key not in self.domains:
            raise ValueError(f"Domain {domain_key} not found")
        return self.domains[domain_key]
    
    def estimate_total_queries(self) -> Dict[str, int]:
        """Estimate total queries for each domain"""
        estimates = {}
        for domain_key in self.domains:
            # Regular prompts (28) * 2 keywords + state prompts (1) * 15 states
            regular_prompts = 28 * 2  # 56
            state_prompts = 1 * len(self.indian_states)  # 15
            estimates[domain_key] = regular_prompts + state_prompts
        
        return estimates
    
    def add_custom_domain(self, domain_key: str, domain_name: str, keywords: List[str], specific_terms: Optional[List[str]] = None) -> str:
        """Add a custom domain dynamically"""
        if specific_terms is None:
            specific_terms = []
        
        # Create a new Domain object
        custom_domain = Domain(
            name=domain_name,
            keywords=keywords,
            specific_terms=specific_terms,
            state_variations=True
        )
        
        # Add to domains dictionary
        self.domains[domain_key] = custom_domain
        
        # Add domain context for LLM if available
        if self.llm_analyzer and self.llm_analyzer.enabled:
            # Add to domain contexts if it exists
            if hasattr(self.llm_analyzer, 'domain_contexts'):
                self.llm_analyzer.domain_contexts[domain_key] = {
                    "industry": domain_name,
                    "key_sectors": keywords,
                    "associations": [],
                    "data_types": ["Companies", "Organizations", "Directories", "Industry data"],
                    "search_focus": f"{domain_name.lower()} companies India, {', '.join(keywords[:3])}"
                }
        
        logger.info(f"Added custom domain: {domain_name} with key: {domain_key}")
        return domain_key
    
    def generate_custom_domain_queries(self, domain_name: str, keywords: List[str], additional_context: str = "", query_count: int = 20) -> List[Dict]:
        """Generate queries for a custom domain using LLM"""
        # Create temporary domain key
        temp_domain_key = f"custom_{domain_name.lower().replace(' ', '_')}"
        
        # Add as temporary domain
        custom_domain_key = self.add_custom_domain(temp_domain_key, domain_name, keywords)
        
        # Generate queries using existing method
        if self.llm_analyzer and self.llm_analyzer.enabled:
            try:
                # Create enhanced prompt for custom domain
                prompt = f"""
                Generate {query_count} highly effective search queries for finding companies, organizations, and data sources in the {domain_name} industry in India.
                
                Domain: {domain_name}
                Keywords: {', '.join(keywords)}
                Additional Context: {additional_context}
                
                Focus on:
                - Indian companies and manufacturers in {domain_name}
                - Industry associations and trade bodies
                - Export-import directories
                - Business directories and catalogs
                - Contact databases with company details
                - Industry reports and market research
                - Professional networks and organizations
                
                Make each query specific to India and designed to find comprehensive business information.
                Format as a numbered list with one query per line.
                """
                
                if (hasattr(self.llm_analyzer, 'model') and 
                    self.llm_analyzer.model and 
                    hasattr(self.llm_analyzer.model, 'generate_content')):
                    
                    response = self.llm_analyzer.model.generate_content(prompt)
                    if response and hasattr(response, 'text'):
                        queries = self._parse_custom_llm_response(response.text, domain_name, temp_domain_key)
                        return queries[:query_count]
                
            except Exception as e:
                logger.error(f"Custom LLM query generation failed: {e}")
        
        # Fallback to basic queries
        return self._generate_basic_custom_queries(domain_name, keywords, query_count)
    
    def _parse_custom_llm_response(self, response_text: str, domain_name: str, domain_key: str) -> List[Dict]:
        """Parse LLM response for custom domain queries"""
        queries = []
        lines = response_text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                # Remove numbering and bullet points
                line = re.sub(r'^\d+\.?\s*', '', line)
                line = re.sub(r'^\*\s*', '', line)
                line = re.sub(r'^-\s*', '', line)
                
                if line:
                    queries.append({
                        "query_id": f"{domain_key}_llm_{i+1}",
                        "domain": domain_name,
                        "search_query": line,
                        "query_type": "custom_llm_generated",
                        "source": "gemini_custom"
                    })
        
        return queries
    
    def _generate_basic_custom_queries(self, domain_name: str, keywords: List[str], query_count: int) -> List[Dict]:
        """Generate basic queries for custom domain"""
        queries = []
        
        # Basic templates
        templates = [
            f"{domain_name} companies in India",
            f"{domain_name} manufacturers India",
            f"{domain_name} directory India",
            f"{domain_name} associations India",
            f"{domain_name} database India",
            f"{domain_name} exporters India",
            f"{domain_name} industry India",
            f"{domain_name} suppliers India",
            f"{domain_name} organizations India",
            f"{domain_name} trade directory India"
        ]
        
        # Add keyword variations
        for keyword in keywords[:3]:
            templates.extend([
                f"{keyword} companies India",
                f"{keyword} directory India",
                f"{keyword} associations India"
            ])
        
        # Add location-specific queries
        major_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune"]
        for city in major_cities[:3]:
            templates.append(f"{domain_name} companies {city}")
        
        # Ensure enough queries
        while len(templates) < query_count:
            templates.extend([
                f"{domain_name} business directory",
                f"{domain_name} trade associations",
                f"{domain_name} export data India"
            ])
        
        for i, template in enumerate(templates[:query_count]):
            queries.append({
                "query_id": f"custom_basic_{i+1}",
                "domain": domain_name,
                "search_query": template,
                "query_type": "basic_custom",
                "source": "rule_based_custom"
            })
        
        return queries
