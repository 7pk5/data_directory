# Quick Start Guide

## 🚀 **Run the Application**

### **Option 1: Simple Run**
```bash
python src/main.py
```

### **Option 2: With Custom Settings**
1. Copy `.env.template` to `.env`
2. Add your Gemini API key 
3. Run: `python src/main.py`

## 📋 **Usage Steps**

1. **Choose Domain**: Select from Chemical, Shipping, Sports Equipment, or EdTech
2. **Set Query Count**: Choose 5-50 queries (recommended: 15-25)
3. **Wait for Results**: System will generate smart queries and search
4. **Get Excel File**: Find your structured directory in `data/output/`

## 📊 **Expected Output**

Excel file with columns:
- Industry, Sector, Document Title, Data Link, Format
- Action Required, Datapoints Contained, No. of Datapoints  
- Coverage, Source, Year, Additional Comment

## 💡 **Tips**

- **Start Small**: Try 5-10 queries for testing
- **Be Patient**: Each query takes ~4 seconds for respectful searching
- **Check Output**: Files saved in `data/output/` directory
- **No API Needed**: Works completely free without any API keys

## 🆓 **Cost**: FREE!
No API costs, no subscriptions, no limits!
