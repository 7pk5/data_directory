import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # Add Gemini API key

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/application.log'),
        logging.StreamHandler()
    ]
)

# Search Configuration
RESULTS_PER_QUERY = 15  # Top 15-18 results per query
SEARCH_DELAY = 1  # Delay between searches (seconds)
MAX_RETRIES = 3

# Data Analysis Configuration
RELEVANCE_THRESHOLD = 0.6  # Minimum relevance score to include result
MIN_DATA_ROWS = 10  # Minimum estimated rows to be considered valuable

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)
