import requests
import time
import logging
from typing import List, Dict, Optional
from serpapi import GoogleSearch
from config.config import SERPAPI_KEY, SEARCH_DELAY, MAX_RETRIES, RESULTS_PER_QUERY

logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self):
        if not SERPAPI_KEY:
            raise ValueError("SERPAPI_KEY not found in environment variables")
        self.api_key = SERPAPI_KEY
        
    def search_google(self, query: str, domain: str) -> List[Dict]:
        """
        Search Google using SerpAPI for a given query and domain
        """
        logger.info(f"Searching for: {query}")
        
        search_params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": RESULTS_PER_QUERY,
            "gl": "in",  # India
            "hl": "en"   # English
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                search = GoogleSearch(search_params)
                results = search.get_dict()
                
                if "organic_results" in results:
                    processed_results = []
                    for result in results["organic_results"]:
                        processed_result = {
                            "title": result.get("title", ""),
                            "url": result.get("link", ""),
                            "snippet": result.get("snippet", ""),
                            "domain": self._extract_domain(result.get("link", "")),
                            "position": result.get("position", 0),
                            "query": query,
                            "search_domain": domain
                        }
                        processed_results.append(processed_result)
                    
                    logger.info(f"Found {len(processed_results)} results for query: {query}")
                    time.sleep(SEARCH_DELAY)  # Rate limiting
                    return processed_results
                
            except Exception as e:
                logger.error(f"Search attempt {attempt + 1} failed: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All search attempts failed for query: {query}")
                    return []
        
        return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return ""
    
    def search_domain_queries(self, domain: str, prompts: List[str], domain_keywords: List[str]) -> List[Dict]:
        """
        Generate and execute all search queries for a specific domain
        """
        all_results = []
        
        for prompt in prompts:
            # Combine domain keywords with prompt
            for keyword in domain_keywords:
                query = f"{keyword} {prompt}"
                results = self.search_google(query, domain)
                all_results.extend(results)
        
        logger.info(f"Total results collected for {domain}: {len(all_results)}")
        return all_results
