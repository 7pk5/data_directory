"""
Enhanced Main Application for Intelligent Manufacturing Data Collection
Orchestrates the entire data discovery and directory creation process with LLM integration
"""

import logging
import sys
import os
import re
from typing import Dict, List, Optional
import re

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.domain_manager import DomainManager
from src.core.enhanced_directory_creator import EnhancedDirectoryCreator
from config.config import SERPAPI_KEY

logger = logging.getLogger(__name__)

class ManufacturingDataCollector:
    """Enhanced main application class with LLM integration"""
    
    def __init__(self, use_free_search: bool = True, use_llm: bool = True):
        """Initialize the enhanced data collector"""
        self.use_llm = use_llm
        self.use_free_search = use_free_search
        
        # Initialize with LLM support
        self.domain_manager = DomainManager(use_llm=use_llm)
        
        # Initialize search engine (free or paid)
        if use_free_search:
            logger.info("🆓 Using FREE search methods (no API keys required)")
            from src.core.free_search_engine import FreeSearchEngine
            self.search_engine = FreeSearchEngine()
        else:
            # Fallback to paid SerpAPI if needed
            try:
                from src.core.search_engine import SearchEngine
                self.search_engine = SearchEngine()
            except Exception as e:
                logger.warning(f"SerpAPI not available, switching to free search: {e}")
                from src.core.free_search_engine import FreeSearchEngine
                self.search_engine = FreeSearchEngine()
        
        # Use enhanced directory creator
        self.directory_creator = EnhancedDirectoryCreator(use_llm=use_llm)
        self.collected_data = {}
    
    def run_interactive_mode(self):
        """Run the application in interactive mode"""
        print("🏭 Enhanced Manufacturing Data Collection System")
        print("=" * 55)
        
        # Show search and LLM status
        search_type = "🆓 FREE Search" if self.use_free_search else "💰 Paid SerpAPI"
        llm_status = "🤖 LLM Enhanced" if self.use_llm else "📝 Standard Mode"
        print(f"Search Mode: {search_type}")
        print(f"Analysis Mode: {llm_status}")
        
        # Show available domains
        domains = self.domain_manager.get_all_domains()
        print("\n📋 Available Domains:")
        for i, domain_key in enumerate(domains, 1):
            domain_info = self.domain_manager.get_domain_info(domain_key)
            print(f"{i}. {domain_info.name}")
        
        print(f"{len(domains) + 1}. Custom Domain Entry")
        print(f"{len(domains) + 2}. Process All Domains")
        print(f"{len(domains) + 3}. Show Query Estimates")
        if self.use_llm:
            print(f"{len(domains) + 4}. LLM Enhancement Demo")
        
        while True:
            try:
                choice = input(f"\n🎯 Choose option (1-{len(domains) + 3}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    print("👋 Goodbye!")
                    break
                
                choice_num = int(choice)
                
                if choice_num == len(domains) + 1:
                    # Custom domain entry
                    self.process_custom_domain()
                elif choice_num == len(domains) + 2:
                    # Process all domains
                    self.process_all_domains()
                elif choice_num == len(domains) + 3:
                    # Show query estimates
                    self.show_query_estimates()
                elif choice_num == len(domains) + 4 and self.use_llm:
                    # LLM Enhancement Demo
                    self.show_llm_demo()
                elif 1 <= choice_num <= len(domains):
                    # Process specific domain
                    domain_key = domains[choice_num - 1]
                    self.process_domain(domain_key)
                else:
                    print("❌ Invalid choice. Please try again.")
                
            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\n👋 Process interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print(f"❌ An error occurred: {e}")
    
    def process_domain(self, domain_key: str) -> str:
        """Process a single domain and create directory"""
        domain_info = self.domain_manager.get_domain_info(domain_key)
        print(f"\n🔍 Processing Domain: {domain_info.name}")
        print("-" * 40)
        
        # Ask user for number of queries
        query_count = self._get_query_count()
        
        # Generate queries
        print(f"📝 Generating {query_count} smart search queries...")
        queries = self.domain_manager.generate_queries_for_domain(domain_key, query_count=query_count)
        print(f"✅ Generated {len(queries)} queries")
        
        # Execute searches
        print(f"🔎 Starting search process...")
        search_results = self.search_engine.batch_search(queries, domain_key)
        
        # Show search summary
        total_sources = sum(len(result.get('results', [])) for result in search_results)
        successful_queries = sum(1 for result in search_results if result.get('status') != 'error')
        
        print(f"📊 Search completed:")
        print(f"   - Queries executed: {len(search_results)}")
        print(f"   - Successful queries: {successful_queries}")
        print(f"   - Data sources found: {total_sources}")
        
        # Create directory
        print("📁 Creating structured Excel directory...")
        directory_path = self.directory_creator.create_structured_directory(
            domain_info.name, 
            search_results
        )
        
        # Store results
        self.collected_data[domain_key] = search_results
        
        print(f"✅ Directory created: {directory_path}")
        return directory_path
    
    def process_all_domains(self):
        """Process all domains sequentially"""
        print(f"\n🚀 Processing All Domains")
        print("=" * 40)
        
        domains = self.domain_manager.get_all_domains()
        completed_domains = {}
        
        for i, domain_key in enumerate(domains, 1):
            domain_info = self.domain_manager.get_domain_info(domain_key)
            print(f"\n[{i}/{len(domains)}] Processing: {domain_info.name}")
            
            try:
                directory_path = self.process_domain(domain_key)
                completed_domains[domain_info.name] = self.collected_data[domain_key]
                print(f"✅ Completed: {domain_info.name}")
                
            except Exception as e:
                logger.error(f"Failed to process domain {domain_key}: {e}")
                print(f"❌ Failed to process {domain_info.name}: {e}")
        
        # Create master directory
        if completed_domains:
            print(f"\n📋 Creating master structured directory...")
            master_path = self.directory_creator.create_master_structured_directory(completed_domains)
            print(f"✅ Master directory created: {master_path}")
        
        # Show final summary
        self.show_final_summary(completed_domains)
    
    def show_query_estimates(self):
        """Show estimated queries for each domain"""
        print(f"\n📊 Query Estimates")
        print("-" * 30)
        print("With the new LLM-powered approach:")
        print("• You can choose any number of queries (recommended: 15-25)")
        print("• Each query is intelligently crafted for the specific industry")
        print("• Queries are India-focused and domain-appropriate")
        print()
        
        domains = self.domain_manager.get_all_domains()
        for domain_key in domains:
            domain_info = self.domain_manager.get_domain_info(domain_key)
            print(f"{domain_info.name}: User-defined (recommend 20 queries)")
        
        print(f"\nEstimated time per query: ~4 seconds (free search)")
        print("Example: 20 queries = ~1.5 minutes per domain")
        
        # Show cost info
        if self.use_free_search:
            print("💰 Cost: FREE! Using free search methods 🎉")
        else:
            print("💰 Cost: No SerpAPI costs with free search!")
    
    
    def show_final_summary(self, completed_domains: Dict):
        """Show final summary of all processed domains"""
        print(f"\n📈 Final Summary")
        print("=" * 30)
        
        total_sources = 0
        total_queries = 0
        
        for domain_name, search_results in completed_domains.items():
            domain_sources = sum(len(result.get('results', [])) for result in search_results)
            domain_queries = len(search_results)
            
            print(f"\n{domain_name}:")
            print(f"  - Queries: {domain_queries}")
            print(f"  - Sources found: {domain_sources}")
            
            total_sources += domain_sources
            total_queries += domain_queries
        
        print(f"\n🎯 Overall Totals:")
        print(f"   - Total queries executed: {total_queries}")
        print(f"   - Total data sources found: {total_sources}")
        print(f"   - Domains processed: {len(completed_domains)}")
        
        # Show search engine stats
        stats = self.search_engine.get_search_stats()
        print(f"   - Search engine calls: {stats['total_searches']}")
    
    def process_single_query(self, query: str, domain_key: str) -> Dict:
        """Process a single query for testing purposes"""
        domain_info = self.domain_manager.get_domain_info(domain_key)
        result = self.search_engine.search_query(query, domain_key)
        return result
    
    def _get_query_count(self) -> int:
        """Ask user for number of queries to execute"""
        while True:
            try:
                print("\n🔢 How many search queries would you like to execute?")
                print("   Recommended: 15-25 queries for good coverage")
                print("   Maximum: 50 queries (for comprehensive search)")
                
                user_input = input("Enter number of queries (default: 20): ").strip()
                
                if not user_input:
                    return 20  # Default
                
                query_count = int(user_input)
                
                if query_count < 1:
                    print("❌ Please enter a positive number")
                    continue
                elif query_count > 100:
                    print("❌ Maximum 100 queries allowed")
                    continue
                else:
                    return query_count
                    
            except ValueError:
                print("❌ Please enter a valid number")
                continue
    
    def process_custom_domain(self):
        """Process a custom domain entered by the user"""
        print(f"\n🆕 Custom Domain Entry")
        print("-" * 30)
        
        # Get custom domain details from user
        domain_name = input("Enter the domain/industry name: ").strip()
        if not domain_name:
            print("❌ Domain name cannot be empty")
            return
        
        # Get keywords for the domain
        print("\nEnter keywords related to this domain (separated by commas):")
        keywords_input = input("Keywords: ").strip()
        if not keywords_input:
            print("❌ Keywords cannot be empty")
            return
        
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        
        # Get additional context (optional)
        print("\nEnter additional context or specific terms (optional):")
        additional_context = input("Additional context: ").strip()
        
        # Get number of queries
        query_count = self._get_query_count()
        
        print(f"\n🔍 Processing Custom Domain: {domain_name}")
        print("-" * 40)
        
        # Generate optimized queries using LLM
        if self.use_llm and hasattr(self.domain_manager, 'llm_analyzer') and self.domain_manager.llm_analyzer and self.domain_manager.llm_analyzer.enabled:
            print("🤖 Using LLM to generate optimized queries...")
            queries = self.domain_manager.generate_custom_domain_queries(domain_name, keywords, additional_context, query_count)
        else:
            print("📝 Generating standard queries...")
            queries = self.domain_manager._generate_basic_custom_queries(domain_name, keywords, query_count)
        
        print(f"✅ Generated {len(queries)} optimized queries")
        
        # Execute searches
        print(f"🔎 Starting search process...")
        # Create a temporary domain key for this custom domain
        custom_domain_key = f"custom_{domain_name.lower().replace(' ', '_')}"
        search_results = self.search_engine.batch_search(queries, custom_domain_key)
        
        # Show search summary
        total_sources = sum(len(result.get('results', [])) for result in search_results)
        successful_queries = sum(1 for result in search_results if result.get('status') != 'error')
        
        print(f"📊 Search completed:")
        print(f"   - Queries executed: {len(search_results)}")
        print(f"   - Successful queries: {successful_queries}")
        print(f"   - Data sources found: {total_sources}")
        
        # Create directory
        print("📁 Creating structured Excel directory...")
        directory_path = self.directory_creator.create_structured_directory(
            domain_name, 
            search_results
        )
        
        # Store results
        self.collected_data[custom_domain_key] = search_results
        
        print(f"✅ Custom domain directory created: {directory_path}")
        return directory_path
    
    def show_llm_demo(self):
        """Show LLM enhancement capabilities"""
        print(f"\n🤖 LLM Enhancement Demo")
        print("-" * 30)
        
        if not self.use_llm:
            print("❌ LLM is not enabled for this session")
            return
        
        if not hasattr(self.domain_manager, 'llm_analyzer') or not self.domain_manager.llm_analyzer:
            print("❌ LLM analyzer not available")
            return
        
        if not self.domain_manager.llm_analyzer.enabled:
            print("❌ LLM is not properly configured (check API key)")
            return
        
        print("✅ LLM is active and ready!")
        print("\n🔍 LLM Capabilities:")
        print("• Smart query generation based on domain context")
        print("• Industry-specific keyword optimization")
        print("• India-focused search strategies")
        print("• Adaptive query formulation")
        print("• Context-aware search terms")
        
        # Demo with a sample domain
        print(f"\n📋 Demo: Generating 5 smart queries for 'Textile Manufacturing'")
        try:
            sample_queries = self.domain_manager.generate_custom_domain_queries(
                "Textile Manufacturing", 
                ["textile", "fabric", "garment"], 
                "Focus on cotton and silk textile manufacturers",
                5
            )
            
            print("Generated queries:")
            for i, query in enumerate(sample_queries, 1):
                print(f"  {i}. {query['search_query']}")
                
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"❌ Demo failed: {e}")

def main():
    """Main entry point"""
    print("🏭 Enhanced Manufacturing Data Collection System")
    print("=======================================================")
    print("🆓 Using FREE search methods - No API keys required!")
    print()
    
    try:
        # Initialize the collector with FREE search by default
        collector = ManufacturingDataCollector(use_free_search=True)
        
        # Run interactive mode
        collector.run_interactive_mode()
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        print(f"❌ Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
