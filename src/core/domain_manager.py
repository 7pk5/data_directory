"""
Domain Manager for Indian Manufacturing Data Collection
Handles domain-specific search query generation and management with LLM enhancement
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

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
