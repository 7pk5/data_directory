# Configuration for the 4 industry domains
DOMAINS = {
    "chemical": {
        "name": "Chemical and Petrochemical",
        "keywords": ["chemical", "petrochemical", "polymer", "fertilizer", "pharmaceutical", "paint", "coating"],
        "priority_sources": ["chemicals.gov.in", "ficci.in", "cii.in", "assocham.org"]
    },
    "shipping": {
        "name": "Shipping",
        "keywords": ["shipping", "maritime", "port", "logistics", "cargo", "freight", "vessel"],
        "priority_sources": ["shipping.gov.in", "shipmin.gov.in", "insa-india.org", "ممو.in"]
    },
    "sports": {
        "name": "Sports Equipment",
        "keywords": ["sports equipment", "fitness", "gymnasium", "athletic", "sporting goods"],
        "priority_sources": ["sai.gov.in", "kheloindia.gov.in", "indiansport.com"]
    },
    "edtech": {
        "name": "EdTech",
        "keywords": ["education technology", "e-learning", "digital education", "online learning", "educational software"],
        "priority_sources": ["education.gov.in", "digitalindia.gov.in", "niepa.ac.in"]
    }
}

# The 29 search prompts to be combined with each domain
SEARCH_PROMPTS = [
    # Companies and Manufacturers
    "companies manufacturers India directory",
    "leading companies India association",
    "top manufacturers India list",
    "Indian companies database",
    "manufacturers directory India contact",
    
    # Industry Associations
    "industry association India",
    "trade association India",
    "chamber of commerce India",
    "manufacturers association India",
    "industry federation India",
    
    # Government and Official Sources
    "government directory India companies",
    "ministry of industry India companies",
    "MSME directory India",
    "industrial development corporation India",
    "export promotion council India",
    
    # Business Directories
    "yellow pages India companies",
    "business directory India",
    "industrial directory India",
    "company profiles India",
    "business listings India",
    
    # Trade and Export
    "exporters directory India",
    "importers directory India",
    "trade directory India",
    "export import database India",
    "international trade India",
    
    # Additional Sources
    "industry reports India companies",
    "market research India companies",
    "industrial clusters India",
    "manufacturing hubs India"
]

# Excel column structure
EXCEL_COLUMNS = [
    "Title",
    "URL", 
    "Domain",
    "Source_Type",
    "Document_Classification",
    "Estimated_Rows",
    "Estimated_Fields", 
    "Data_Coverage_Score",
    "Extraction_Method",
    "Relevance_Score",
    "Contact_Available",
    "Year_Published",
    "Description",
    "Action_Needed"
]
