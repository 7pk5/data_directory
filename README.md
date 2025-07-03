# Intelligent Data Collection for Indian Manufacturing Sector

## Overview
This project automates the collection and analysis of company and association data from the Indian manufacturing sector across 4 key domains: Chemical & Petrochemical, Shipping, Sports Equipment, and EdTech.

## Features
- **Automated Web Searching**: Uses SerpAPI to perform intelligent Google searches
- **Smart Content Analysis**: AI-powered classification of search results
- **Multi-format Support**: Handles PDFs, Excel files, web pages, and APIs
- **Data Quality Assessment**: Estimates data coverage and extraction difficulty
- **Excel Output**: Organized results in domain-specific sheets

## Project Structure
```
├── src/
│   ├── config/          # Configuration files
│   ├── scraper/         # Web scraping modules
│   ├── analyzer/        # Data analysis and classification
│   ├── excel_handler/   # Excel output management
│   └── utils/           # Utility functions
├── data/
│   ├── raw/             # Raw search results
│   ├── processed/       # Analyzed data
│   └── output/          # Final Excel files
├── config/              # Domain and prompt configurations
└── logs/                # Application logs
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   Create a `.env` file :
   ```
      # API Configuration
      GEMINI_API_KEY=your_gemini_api_key_here

      # Search Configuration  
      RESULTS_PER_QUERY=15
      SEARCH_DELAY=1
      MAX_RETRIES=3

      # Data Analysis Configuration
      RELEVANCE_THRESHOLD=0.6
      MIN_DATA_ROWS=10

   ```

3. **Run the Application**:
   ```bash
   python main.py
   ```

## Usage
1. Select the domain to search (Chemical, Shipping, Sports, EdTech)
2. The system will generate 29 search queries for the selected domain
3. Automated searching and data collection begins
4. Results are analyzed and classified intelligently
5. Final data is exported to Excel with domain-specific sheets

## Output Format
Each Excel sheet contains:
- Title, URL, Domain, Source Type
- Document Classification
- Data Coverage Estimates
- Extraction Recommendations
- Contact Information
- Relevance Scores
