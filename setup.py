"""
Setup and Installation Script for Manufacturing Data Collection System
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file template"""
    env_content = """# SerpAPI Configuration
SERPAPI_KEY=your_serpapi_key_here

# Search Configuration
RESULTS_PER_QUERY=15
SEARCH_DELAY=1
MAX_RETRIES=3

# Data Analysis Configuration
RELEVANCE_THRESHOLD=0.6
MIN_DATA_ROWS=10
"""
    
    env_path = Path(".env")
    if not env_path.exists():
        with open(env_path, "w") as f:
            f.write(env_content)
        print("✅ Created .env file template")
        print("📝 Please edit .env file and add your SerpAPI key")
    else:
        print("📋 .env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = [
        "data/raw",
        "data/processed", 
        "data/output",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        "requests",
        "beautifulsoup4", 
        "pandas",
        "openpyxl",
        "google-search-results",  # serpapi package
        "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Install them with: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def main():
    """Main setup function"""
    print("🏭  Data Directory Collection System - Setup")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    print("\n🎯 Setup Complete!")
    print("-" * 20)
    
    if not deps_ok:
        print("⚠️  Please install missing dependencies first")
        print("Run: pip install -r requirements.txt")
    else:
        print("✅ System ready to use")
        print("🚀 Run the system with: python src/main.py")

if __name__ == "__main__":
    main()
