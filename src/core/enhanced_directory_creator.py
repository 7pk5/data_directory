"""
Enhanced Directory Creator with LLM Integration
Creates structured Excel files in the exact format requested by user
"""

import pandas as pd
import logging
from typing import List, Dict
from datetime import datetime
import os
from src.core.gemini_analyzer import GeminiAnalyzer, StructuredDataPoint
from config.config import OUTPUT_DIR

logger = logging.getLogger(__name__)

class EnhancedDirectoryCreator:
    """Creates Excel directories with LLM-enhanced structured analysis"""
    
    def __init__(self, output_dir: str = OUTPUT_DIR, use_llm: bool = True):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize Gemini analyzer if requested
        self.llm_analyzer = None
        if use_llm:
            try:
                self.llm_analyzer = GeminiAnalyzer()
                if self.llm_analyzer and self.llm_analyzer.enabled:
                    logger.info("🤖 Enhanced directory creation with LLM analysis")
                else:
                    logger.warning("⚠️ LLM not available, using standard analysis")
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {e}")
    
    def create_structured_directory(self, domain_name: str, search_results: List[Dict]) -> str:
        """Create Excel directory in the exact user-specified format"""
        logger.info(f"Creating structured directory for domain: {domain_name}")
        
        # Process all search results into structured format
        structured_data = []
        
        for query_result in search_results:
            domain_key = self._get_domain_key(domain_name)
            
            for result in query_result.get("results", []):
                try:
                    # Use LLM analysis if available, otherwise fallback
                    if self.llm_analyzer and self.llm_analyzer.enabled:
                        structured_point = self.llm_analyzer.analyze_search_result_with_llm(
                            {
                                'title': result.title if hasattr(result, 'title') else str(result),
                                'link': result.url if hasattr(result, 'url') else '',
                                'snippet': result.data_description if hasattr(result, 'data_description') else ''
                            },
                            domain_key,
                            result
                        )
                    else:
                        # Fallback to standard conversion
                        structured_point = self._convert_to_structured_format(result, domain_key)
                    
                    structured_data.append(structured_point)
                    
                except Exception as e:
                    logger.error(f"Error processing result: {e}")
                    continue
        
        # Create DataFrame in exact format requested
        df_data = []
        for point in structured_data:
            df_data.append({
                'Industry': point.industry,
                'Sector': point.sector,
                'Document title': point.document_title,
                'Data Link': point.data_link,
                'Format': point.format,
                'Action Required': point.action_required,
                'Datapoints Contained': point.datapoints_contained,
                'No. of Datapoints': point.no_of_datapoints,
                'Coverage': point.coverage,
                'Source': point.source,
                'Year': point.year,
                'Additional comment': point.additional_comment
            })
        
        # Create Excel file
        filename = f"{domain_name.replace(' ', '_')}_Structured_Directory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        if df_data:
            df = pd.DataFrame(df_data)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Main structured data sheet
                df.to_excel(writer, sheet_name='Manufacturing_Data_Directory', index=False)
                self._format_structured_sheet(writer, 'Manufacturing_Data_Directory')
                
                # Summary statistics sheet
                summary_data = self._create_summary_statistics(df, domain_name)
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary_Statistics', index=False)
                
                # Query metadata sheet
                query_data = self._create_query_metadata(search_results)
                query_df = pd.DataFrame(query_data)
                query_df.to_excel(writer, sheet_name='Search_Metadata', index=False)
        
        logger.info(f"Structured directory created: {filepath}")
        return filepath
    
    def _get_domain_key(self, domain_name: str) -> str:
        """Convert domain name to key"""
        mapping = {
            "Chemical and Petrochemical": "Chemical_Petrochemical",
            "Shipping": "Shipping",
            "Sports Equipment": "Sports_Equipment",
            "EdTech": "EdTech"
        }
        return mapping.get(domain_name, domain_name.replace(" ", "_"))
    
    def _convert_to_structured_format(self, result, domain_key: str) -> StructuredDataPoint:
        """Convert standard analysis to structured format"""
        # Extract information from result object
        if hasattr(result, 'title'):
            title = result.title
            url = result.url
            doc_type = result.document_type.value if hasattr(result.document_type, 'value') else str(result.document_type)
            extraction_method = result.extraction_method.value if hasattr(result.extraction_method, 'value') else str(result.extraction_method)
            estimated_rows = result.estimated_rows
            data_description = result.data_description
        else:
            # Fallback for different result formats
            title = str(result)
            url = ""
            doc_type = "Website"
            extraction_method = "Website Crawling"
            estimated_rows = 100
            data_description = "Company Information"
        
        # Map document type to format
        format_mapping = {
            "PDF": "PDF",
            "Excel": "Excel", 
            "Web Page": "Website",
            "API": "API",
            "Database": "Website",
            "Directory": "Website"
        }
        
        # Map extraction method to action required
        action_mapping = {
            "Manual Download": "PDF Download",
            "Web Scraping": "Website Crawling", 
            "API Call": "API Integration",
            "Registration Required": "Registration Required",
            "Paid Access": "Manual",
            "Form Submission": "Manual"
        }
        
        # Domain mapping
        domain_mapping = {
            "Chemical_Petrochemical": "Chemical & Petrochemical",
            "Shipping": "Shipping & Logistics",
            "Sports_Equipment": "Sports Equipment Manufacturing",
            "EdTech": "Educational Technology"
        }
        
        return StructuredDataPoint(
            industry=domain_mapping.get(domain_key, domain_key),
            sector="General",
            document_title=title,
            data_link=url,
            format=format_mapping.get(doc_type, "Website"),
            action_required=action_mapping.get(extraction_method, "Website Crawling"),
            datapoints_contained=data_description,
            no_of_datapoints=estimated_rows,
            coverage="All India",
            source=url.split('/')[2] if '//' in url else "Unknown",
            year="Unknown",
            additional_comment="Standard analysis - LLM enhancement recommended"
        )
    
    def _create_summary_statistics(self, df: pd.DataFrame, domain_name: str) -> List[Dict]:
        """Create summary statistics for the domain"""
        stats = []
        
        if not df.empty:
            # Basic counts
            stats.extend([
                {"Metric": "Domain Analyzed", "Value": domain_name},
                {"Metric": "Total Data Sources", "Value": len(df)},
                {"Metric": "Unique Sources", "Value": df['Source'].nunique()},
                {"Metric": "", "Value": ""},  # Separator
            ])
            
            # Format distribution
            format_counts = df['Format'].value_counts()
            stats.append({"Metric": "Format Distribution", "Value": ""})
            for format_type, count in format_counts.items():
                stats.append({"Metric": f"  - {format_type}", "Value": count})
            
            stats.append({"Metric": "", "Value": ""})  # Separator
            
            # Action required distribution
            action_counts = df['Action Required'].value_counts()
            stats.append({"Metric": "Action Required Distribution", "Value": ""})
            for action, count in action_counts.items():
                stats.append({"Metric": f"  - {action}", "Value": count})
            
            stats.append({"Metric": "", "Value": ""})  # Separator
            
            # Data volume estimates
            total_datapoints = df['No. of Datapoints'].sum()
            avg_datapoints = df['No. of Datapoints'].mean()
            
            stats.extend([
                {"Metric": "Estimated Total Data Points", "Value": f"{total_datapoints:,}"},
                {"Metric": "Average Data Points per Source", "Value": f"{avg_datapoints:.0f}"},
                {"Metric": "Coverage Analysis", "Value": ""},
            ])
            
            # Coverage distribution
            coverage_counts = df['Coverage'].value_counts()
            for coverage, count in coverage_counts.items():
                stats.append({"Metric": f"  - {coverage}", "Value": count})
        
        # Add generation info
        stats.extend([
            {"Metric": "", "Value": ""},
            {"Metric": "Report Generated", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"Metric": "Analysis Method", "Value": "LLM Enhanced" if self.llm_analyzer and self.llm_analyzer.enabled else "Standard"}
        ])
        
        return stats
    
    def _create_query_metadata(self, search_results: List[Dict]) -> List[Dict]:
        """Create query metadata information"""
        metadata = []
        
        for i, query_result in enumerate(search_results, 1):
            metadata.append({
                "Query Number": i,
                "Search Query": query_result.get("query", ""),
                "Query Type": query_result.get("query_type", ""),
                "Total Results": query_result.get("total_results", 0),
                "Relevant Results": query_result.get("relevant_results", 0),
                "Status": query_result.get("status", ""),
                "Source": query_result.get("source", "standard")
            })
        
        return metadata
    
    def _format_structured_sheet(self, writer, sheet_name: str):
        """Format the structured data sheet"""
        workbook = writer.book
        worksheet = workbook[sheet_name]
        
        # Define column widths for better readability
        column_widths = {
            'A': 20,  # Industry
            'B': 25,  # Sector
            'C': 40,  # Document title
            'D': 50,  # Data Link
            'E': 12,  # Format
            'F': 20,  # Action Required
            'G': 30,  # Datapoints Contained
            'H': 18,  # No. of Datapoints
            'I': 15,  # Coverage
            'J': 20,  # Source
            'K': 10,  # Year
            'L': 40   # Additional comment
        }
        
        # Set column widths
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width
        
        # Style header row
        for cell in worksheet[1]:
            cell.font = cell.font.copy(bold=True)
    
    def create_master_structured_directory(self, all_domain_results: Dict[str, List[Dict]]) -> str:
        """Create master directory with all domains in structured format"""
        logger.info("Creating master structured directory with all domains")
        
        filename = f"Manufacturing_Master_Directory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            all_data = []
            
            for domain_name, search_results in all_domain_results.items():
                # Process each domain
                domain_key = self._get_domain_key(domain_name)
                
                for query_result in search_results:
                    for result in query_result.get("results", []):
                        try:
                            if self.llm_analyzer and self.llm_analyzer.enabled:
                                structured_point = self.llm_analyzer.analyze_search_result_with_llm(
                                    {
                                        'title': result.title if hasattr(result, 'title') else str(result),
                                        'link': result.url if hasattr(result, 'url') else '',
                                        'snippet': result.data_description if hasattr(result, 'data_description') else ''
                                    },
                                    domain_key,
                                    result
                                )
                            else:
                                structured_point = self._convert_to_structured_format(result, domain_key)
                            
                            all_data.append({
                                'Industry': structured_point.industry,
                                'Sector': structured_point.sector,
                                'Document title': structured_point.document_title,
                                'Data Link': structured_point.data_link,
                                'Format': structured_point.format,
                                'Action Required': structured_point.action_required,
                                'Datapoints Contained': structured_point.datapoints_contained,
                                'No. of Datapoints': structured_point.no_of_datapoints,
                                'Coverage': structured_point.coverage,
                                'Source': structured_point.source,
                                'Year': structured_point.year,
                                'Additional comment': structured_point.additional_comment
                            })
                        except Exception as e:
                            logger.error(f"Error processing result for master directory: {e}")
            
            # Create master sheet
            if all_data:
                df = pd.DataFrame(all_data)
                df.to_excel(writer, sheet_name='All_Manufacturing_Data', index=False)
                self._format_structured_sheet(writer, 'All_Manufacturing_Data')
                
                # Create domain-wise sheets
                for domain_name in all_domain_results.keys():
                    domain_data = df[df['Industry'] == self._get_domain_display_name(domain_name)]
                    if not domain_data.empty:
                        sheet_name = domain_name.replace(' ', '_').replace('&', 'and')[:31]
                        domain_data.to_excel(writer, sheet_name=sheet_name, index=False)
                        self._format_structured_sheet(writer, sheet_name)
        
        logger.info(f"Master structured directory created: {filepath}")
        return filepath
    
    def _get_domain_display_name(self, domain_key: str) -> str:
        """Convert domain key to display name"""
        mapping = {
            "Chemical_Petrochemical": "Chemical & Petrochemical",
            "Shipping": "Shipping & Logistics", 
            "Sports_Equipment": "Sports Equipment Manufacturing",
            "EdTech": "Educational Technology"
        }
        return mapping.get(domain_key, domain_key)
