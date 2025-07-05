# 🏭  Data Directory Collection System

## 🌟 Overview
An intelligent web-based system for collecting and analyzing company data from any industry sector in India. Features both a command-line interface and a beautiful web interface built with Streamlit.

## ✨ Features
- **🌐 Web Interface**: Beautiful Streamlit frontend for easy use
- **🔍 Smart Search**: AI-powered query generation for any industry domain
- **🆓 Free Operation**: Works without paid APIs using intelligent free search
- **🤖 LLM Enhancement**: Optional Gemini AI for smarter queries and analysis
- **📊 Excel Output**: Professional business-ready directories
- **🌍 India-Focused**: All searches target Indian companies and associations
- **🎯 Custom Domains**: Enter any industry - EdTech, Automotive, Healthcare, etc.

## 🚀 Quick Start

### Option 1: Web Interface (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt


### Option 2: Command Line
```bash
python src/main.py
```

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
