"""
Intelligent Search Engine for Manufacturing Data Collection
Handles search queries and result analysis using SerpAPI
"""

import time
import logging
from typing import List, Dict, Optional

# Try importing SerpAPI with error handling
try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    print("⚠️  SerpAPI not installed. Install with: pip install google-search-results")
    SERPAPI_AVAILABLE = False
    GoogleSearch = None

from src.core.data_analyzer import DataSourceAnalyzer, DataSourceAnalysis
from config.config import SERPAPI_KEY, SEARCH_DELAY, MAX_RETRIES, RESULTS_PER_QUERY

logger = logging.getLogger(__name__)

class SearchEngine:
    """Intelligent search engine for discovering manufacturing data sources"""
    
    def __init__(self, api_key: Optional[str] = None):
        if not SERPAPI_AVAILABLE:
            raise ImportError("SerpAPI not available. Install with: pip install google-search-results")
        
        self.api_key = api_key or SERPAPI_KEY
        if not self.api_key:
            raise ValueError("SerpAPI key is required. Set SERPAPI_KEY environment variable.")
        
        self.analyzer = DataSourceAnalyzer()
        self.search_count = 0
        self.max_results = RESULTS_PER_QUERY
    
    def search_query(self, query: str, target_domain: str, location: str = "India") -> Dict:
        """Execute a single search query and analyze results"""
        logger.info(f"Searching: {query}")
        
        try:
            # Execute search
            search_results = self._execute_search(query, location)
            
            if not search_results or 'organic_results' not in search_results:
                logger.warning(f"No results found for query: {query}")
                return self._create_empty_result(query, target_domain)
            
            # Analyze each result
            analyzed_results = []
            for result in search_results['organic_results'][:self.max_results]:
                try:
                    analysis = self.analyzer.analyze_search_result(result, target_domain)
                    analyzed_results.append(analysis)
                except Exception as e:
                    logger.error(f"Error analyzing result: {e}")
                    continue
            
            # Filter and sort results
            filtered_results = self._filter_results(analyzed_results)
            
            # Create query result summary
            query_result = {
                "query": query,
                "target_domain": target_domain,
                "total_results": len(search_results['organic_results']),
                "analyzed_results": len(analyzed_results),
                "relevant_results": len(filtered_results),
                "results": filtered_results,
                "search_metadata": {
                    "search_time": search_results.get('search_metadata', {}).get('total_time_taken', 0),
                    "results_available": search_results.get('search_information', {}).get('total_results', 0)
                }
            }
            
            # Add delay between searches
            time.sleep(SEARCH_DELAY)
            self.search_count += 1
            
            return query_result
            
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return self._create_error_result(query, target_domain, str(e))
    
    def _execute_search(self, query: str, location: str) -> Optional[Dict]:
        """Execute search using SerpAPI with retry logic"""
        if not SERPAPI_AVAILABLE or not GoogleSearch:
            raise ImportError("SerpAPI not available")
        
        for attempt in range(MAX_RETRIES):
            try:
                search = GoogleSearch({
                    "q": query,
                    "location": location,
                    "api_key": self.api_key,
                    "num": self.max_results,
                    "start": 0
                })
                
                results = search.get_dict()
                return results
                
            except Exception as e:
                logger.warning(f"Search attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise e
        
        return None
    
    def _filter_results(self, results: List[DataSourceAnalysis]) -> List[DataSourceAnalysis]:
        """Filter results based on relevance and quality"""
        # Filter by minimum relevance score
        min_relevance = 0.3
        filtered = [r for r in results if r.relevance_score >= min_relevance]
        
        # Sort by confidence score (descending)
        filtered.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Remove duplicates based on domain
        seen_domains = set()
        unique_results = []
        for result in filtered:
            if result.domain not in seen_domains:
                unique_results.append(result)
                seen_domains.add(result.domain)
        
        return unique_results
    
    def _create_empty_result(self, query: str, target_domain: str) -> Dict:
        """Create empty result structure"""
        return {
            "query": query,
            "target_domain": target_domain,
            "total_results": 0,
            "analyzed_results": 0,
            "relevant_results": 0,
            "results": [],
            "search_metadata": {
                "search_time": 0,
                "results_available": 0
            },
            "status": "no_results"
        }
    
    def _create_error_result(self, query: str, target_domain: str, error_msg: str) -> Dict:
        """Create error result structure"""
        return {
            "query": query,
            "target_domain": target_domain,
            "total_results": 0,
            "analyzed_results": 0,
            "relevant_results": 0,
            "results": [],
            "search_metadata": {
                "search_time": 0,
                "results_available": 0
            },
            "status": "error",
            "error_message": error_msg
        }
    
    def batch_search(self, queries: List[Dict], target_domain: str) -> List[Dict]:
        """Execute multiple search queries for a domain"""
        logger.info(f"Starting batch search for {len(queries)} queries in domain: {target_domain}")
        
        results = []
        for i, query_info in enumerate(queries, 1):
            logger.info(f"Processing query {i}/{len(queries)}")
            
            try:
                result = self.search_query(
                    query_info['search_query'], 
                    target_domain
                )
                result.update({
                    "query_id": query_info['query_id'],
                    "prompt_template": query_info['prompt_template'],
                    "query_type": query_info['query_type']
                })
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to process query {i}: {e}")
                results.append(self._create_error_result(
                    query_info['search_query'], 
                    target_domain, 
                    str(e)
                ))
        
        logger.info(f"Completed batch search. Processed {len(results)} queries.")
        return results
    
    def get_search_stats(self) -> Dict:
        """Get search statistics"""
        return {
            "total_searches": self.search_count,
            "max_results_per_query": self.max_results,
            "search_delay": SEARCH_DELAY
        }
