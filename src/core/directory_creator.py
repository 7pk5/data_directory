"""
Excel Directory Creator for Manufacturing Data Collection
Creates structured Excel files with search results and metadata
"""

import pandas as pd
import logging
from typing import List, Dict
from datetime import datetime
import os
from src.core.data_analyzer import DataSourceAnalysis
from config.config import OUTPUT_DIR

logger = logging.getLogger(__name__)

class DirectoryCreator:
    """Creates Excel directories of manufacturing data sources"""
    
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_domain_directory(self, domain_name: str, search_results: List[Dict]) -> str:
        """Create Excel directory for a specific domain"""
        logger.info(f"Creating directory for domain: {domain_name}")
        
        # Prepare data for Excel
        directory_data = []
        summary_data = []
        
        for query_result in search_results:
            query_summary = {
                "Query ID": query_result.get("query_id", ""),
                "Search Query": query_result.get("query", ""),
                "Query Type": query_result.get("query_type", ""),
                "Total Results": query_result.get("total_results", 0),
                "Relevant Results": query_result.get("relevant_results", 0),
                "Status": query_result.get("status", "success")
            }
            summary_data.append(query_summary)
            
            # Process individual results
            for result in query_result.get("results", []):
                if isinstance(result, DataSourceAnalysis):
                    directory_entry = self._create_directory_entry(result, query_result)
                    directory_data.append(directory_entry)
        
        # Create Excel file
        filename = f"{domain_name.replace(' ', '_')}_Data_Directory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main directory sheet
            if directory_data:
                directory_df = pd.DataFrame(directory_data)
                directory_df.to_excel(writer, sheet_name='Data_Sources', index=False)
                self._format_directory_sheet(writer, 'Data_Sources')
            
            # Query summary sheet
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Query_Summary', index=False)
                self._format_summary_sheet(writer, 'Query_Summary')
            
            # Statistics sheet
            stats_data = self._create_statistics(directory_data, summary_data, domain_name)
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        logger.info(f"Directory created: {filepath}")
        return filepath
    
    def _create_directory_entry(self, analysis: DataSourceAnalysis, query_result: Dict) -> Dict:
        """Create a directory entry from analysis result"""
        return {
            "ID": f"{query_result.get('query_id', '')}_{hash(analysis.url) % 1000}",
            "Title": analysis.title,
            "URL": analysis.url,
            "Domain": analysis.domain,
            "Document Type": analysis.document_type.value,
            "Relevance Score": analysis.relevance_score,
            "Confidence Score": analysis.confidence_score,
            "Estimated Rows": analysis.estimated_rows,
            "Estimated Fields": analysis.estimated_fields,
            "Extraction Method": analysis.extraction_method.value,
            "Data Description": analysis.data_description,
            "Contact Fields Available": "Yes" if analysis.contact_fields_available else "No",
            "Year Published": analysis.year_published or "Unknown",
            "Source Organization": analysis.source_organization,
            "Requires Payment": "Yes" if analysis.requires_payment else "No",
            "Data Freshness": analysis.data_freshness,
            "Search Query": query_result.get("query", ""),
            "Query Type": query_result.get("query_type", ""),
            "Date Analyzed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Recommended Action": self._get_recommended_action(analysis),
            "Priority": self._get_priority(analysis),
            "Notes": self._generate_notes(analysis)
        }
    
    def _get_recommended_action(self, analysis: DataSourceAnalysis) -> str:
        """Get recommended action based on analysis"""
        if analysis.extraction_method.value == "Manual Download":
            return "Download and extract data manually"
        elif analysis.extraction_method.value == "Web Scraping":
            return "Develop web scraper"
        elif analysis.extraction_method.value == "API Call":
            return "Integrate API"
        elif analysis.extraction_method.value == "Registration Required":
            return "Register and then extract"
        elif analysis.extraction_method.value == "Paid Access":
            return "Evaluate cost vs benefit"
        else:
            return "Manual investigation required"
    
    def _get_priority(self, analysis: DataSourceAnalysis) -> str:
        """Get priority level based on analysis"""
        score = (analysis.relevance_score + analysis.confidence_score) / 2
        
        if score >= 0.8:
            return "High"
        elif score >= 0.6:
            return "Medium"
        else:
            return "Low"
    
    def _generate_notes(self, analysis: DataSourceAnalysis) -> str:
        """Generate notes for the data source"""
        notes = []
        
        if analysis.contact_fields_available:
            notes.append("Contains contact information")
        
        if analysis.estimated_rows > 1000:
            notes.append("Large dataset")
        
        if analysis.requires_payment:
            notes.append("Paid access required")
        
        if analysis.data_freshness == "Recent":
            notes.append("Recent data")
        
        return "; ".join(notes) if notes else "No special notes"
    
    def _create_statistics(self, directory_data: List[Dict], summary_data: List[Dict], domain_name: str) -> List[Dict]:
        """Create statistics summary"""
        stats = []
        
        if directory_data:
            df = pd.DataFrame(directory_data)
            
            # Basic statistics
            stats.extend([
                {"Metric": "Domain", "Value": domain_name},
                {"Metric": "Total Data Sources Found", "Value": len(directory_data)},
                {"Metric": "Average Relevance Score", "Value": f"{df['Relevance Score'].mean():.2f}"},
                {"Metric": "Average Confidence Score", "Value": f"{df['Confidence Score'].mean():.2f}"},
                {"Metric": "High Priority Sources", "Value": len(df[df['Priority'] == 'High'])},
                {"Metric": "Medium Priority Sources", "Value": len(df[df['Priority'] == 'Medium'])},
                {"Metric": "Low Priority Sources", "Value": len(df[df['Priority'] == 'Low'])},
                {"Metric": "", "Value": ""},  # Separator
            ])
            
            # Document type distribution
            doc_types = df['Document Type'].value_counts()
            stats.append({"Metric": "Document Types Found", "Value": ""})
            for doc_type, count in doc_types.items():
                stats.append({"Metric": f"  - {doc_type}", "Value": count})
            
            stats.append({"Metric": "", "Value": ""})  # Separator
            
            # Extraction method distribution
            extraction_methods = df['Extraction Method'].value_counts()
            stats.append({"Metric": "Extraction Methods", "Value": ""})
            for method, count in extraction_methods.items():
                stats.append({"Metric": f"  - {method}", "Value": count})
            
            stats.append({"Metric": "", "Value": ""})  # Separator
            
            # Data size estimates
            total_estimated_rows = df['Estimated Rows'].sum()
            stats.extend([
                {"Metric": "Total Estimated Data Rows", "Value": f"{total_estimated_rows:,}"},
                {"Metric": "Average Fields per Source", "Value": f"{df['Estimated Fields'].mean():.1f}"},
                {"Metric": "Sources with Contact Data", "Value": len(df[df['Contact Fields Available'] == 'Yes'])},
                {"Metric": "Free Access Sources", "Value": len(df[df['Requires Payment'] == 'No'])},
            ])
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            total_queries = len(summary_df)
            successful_queries = len(summary_df[summary_df['Status'] == 'success'])
            
            stats.extend([
                {"Metric": "", "Value": ""},  # Separator
                {"Metric": "Search Statistics", "Value": ""},
                {"Metric": "Total Queries Executed", "Value": total_queries},
                {"Metric": "Successful Queries", "Value": successful_queries},
                {"Metric": "Success Rate", "Value": f"{(successful_queries/total_queries*100):.1f}%" if total_queries > 0 else "0%"},
            ])
        
        # Add timestamp
        stats.append({"Metric": "", "Value": ""})
        stats.append({"Metric": "Report Generated", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        
        return stats
    
    def _format_directory_sheet(self, writer, sheet_name: str):
        """Format the main directory sheet"""
        workbook = writer.book
        worksheet = workbook[sheet_name]
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _format_summary_sheet(self, writer, sheet_name: str):
        """Format the query summary sheet"""
        workbook = writer.book
        worksheet = workbook[sheet_name]
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def create_master_directory(self, all_domain_results: Dict[str, List[Dict]]) -> str:
        """Create a master directory with all domains"""
        logger.info("Creating master directory with all domains")
        
        filename = f"Manufacturing_Data_Master_Directory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for domain_name, search_results in all_domain_results.items():
                # Create data for this domain
                directory_data = []
                
                for query_result in search_results:
                    for result in query_result.get("results", []):
                        if isinstance(result, DataSourceAnalysis):
                            directory_entry = self._create_directory_entry(result, query_result)
                            directory_data.append(directory_entry)
                
                if directory_data:
                    directory_df = pd.DataFrame(directory_data)
                    sheet_name = domain_name.replace(' ', '_').replace('&', 'and')[:31]  # Excel sheet name limit
                    directory_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    self._format_directory_sheet(writer, sheet_name)
        
        logger.info(f"Master directory created: {filepath}")
        return filepath
