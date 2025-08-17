
# NII: National Insurance Institute Form Extraction & Validation

## 📋 Project Overview

This application is a sophisticated document processing pipeline that extracts and validates data from **Bituach Leumi Form 283** (National Insurance Institute accident report forms). It uses Azure AI services for OCR and intelligent field extraction, with comprehensive validation and automatic data correction.

## 🚀 Key Features

### **🔍 Intelligent Data Extraction**
- **Azure Document Intelligence** for high-accuracy OCR
- **Azure OpenAI** for intelligent field extraction
- **Multi-language Support** (Hebrew and English)
- **Automatic Language Detection**

### **✅ Comprehensive Validation**
- **Schema Compliance** using Pydantic models
- **Completeness Scoring** (percentage of filled fields)
- **Accuracy Scoring** (rule-based validation)
- **Automatic Data Correction** for phone numbers

### **🎨 Enhanced User Experience**
- **Drag & Drop Interface** for easy file upload
- **Real-time Processing** with progress indicators
- **Professional UI** with clear visual feedback

### **🔧 Smart Data Fixes**
- **Mobile Phone Standardization** (ensures 10 digits starting with 05)
- **Landline Phone Standardization** (ensures 9 digits starting with 0)
- **Automatic Format Correction** for phone numbers
- **Transparent Fix Tracking** with before/after display

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Upload   │───▶│  Azure Document  │───▶│  Azure OpenAI   │
│   (PDF/Images)  │    │   Intelligence   │    │   Field Ext.    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   OCR Text       │    │   Structured    │
                       │   Extraction     │    │   JSON Data     │
                       └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Validation     │    │   Corrected     │
                       │   & Scoring      │    │   Output        │
                       └──────────────────┘    └─────────────────┘
```

## 📱 Phone Number Validation Features

### **Mobile Phone Numbers**
- **Input**: `6502474947` (10 digits, doesn't start with 05)
- **Output**: `0502474947` (10 digits, starts with 05)
- **Logic**: Ensures all mobile numbers are 10 digits starting with 05

### **Landline Phone Numbers**
- **Input**: `23456789` (8 digits, doesn't start with 0)
- **Output**: `023456789` (9 digits, starts with 0)
- **Logic**: Ensures all landline numbers are 9 digits starting with 0

### **Automatic Fixes Applied**
- Removes country codes (e.g., +972)
- Removes formatting characters (dashes, spaces, parentheses)
- Adds leading zeros where needed
- Standardizes to proper Israeli phone number format

## 🛠️ Installation & Setup

### **Prerequisites**
- Python 3.8+
- Azure subscription with:
  - Document Intelligence service
  - OpenAI service
- Valid API keys and endpoints

### **Installation Steps**
```bash
# Clone the repository
git clone <repository-url>
cd NII_src

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Azure credentials
```

### **Environment Variables**
```bash
# Azure Document Intelligence
DOCUMENTINTELLIGENCE_ENDPOINT=your_endpoint
DOCUMENTINTELLIGENCE_API_KEY=your_api_key

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
```

## 🚀 Running the Application

### **Start the Streamlit App**
```bash
streamlit run app.py
```

### **Access the Application**
- **Local URL**: http://localhost:8501
- **Network URL**: http://your-ip:8501

## 📊 Form Schema

### **Personal Information**
- `lastName` / `שם משפחה` - Family name
- `firstName` / `שם פרטי` - First name
- `idNumber` / `מספר זהות` - Israeli ID (9 digits)
- `gender` / `מין` - Gender
- `dateOfBirth` / `תאריך לידה` - Birth date

### **Contact Details**
- `address` - Complete address structure
- `landlinePhone` / `טלפון קווי` - Landline phone (9 digits)
- `mobilePhone` / `טלפון נייד` - Mobile phone (10 digits)

### **Accident Information**
- `dateOfInjury` / `תאריך התאונה` - Injury date
- `timeOfInjury` / `שעת התאונה` - Injury time (HH:MM)
- `accidentLocation` / `מיקום התאונה` - Accident location
- `accidentDescription` / `תיאור התאונה` - Accident description

### **Medical Details**
- `injuredBodyPart` / `איבר פגוע` - Injured body part
- `medicalInstitutionFields` - Medical institution information

## 🔍 Validation Rules

### **Completeness Score**
- Calculates percentage of fields with values
- Excludes empty/null fields from scoring
- Provides overall data completeness assessment

### **Accuracy Score**
- **ID Number Format**: Must be exactly 9 digits
- **Mobile Phone Format**: Must be 10 digits starting with 05
- **Landline Phone Format**: Must be 9 digits starting with 0
- **Postal Code Format**: Must be 7 digits
- **Date Plausibility**: Day (1-31), Month (1-12), Year (1900-2100)
- **Time Format**: Must be HH:MM format

## 📈 Performance Features

### **Memory Efficient**
- **Lazy Loading** of Azure clients
- **Streaming Processing** for large documents
- **Automatic Cleanup** of temporary data

### **Error Handling**
- **Graceful Fallbacks** for API failures
- **User-friendly Error Messages**
- **Detailed Debug Information** when needed
- **Common Solution Suggestions**

## 🔧 Troubleshooting

### **Common Issues**

#### **Authentication Errors**
- Verify Azure API keys are correct
- Check endpoint URLs are valid
- Ensure services are running and accessible

#### **File Processing Errors**
- Use clear, high-quality scans
- Avoid shadows or glare on documents
- PDF format generally works best
- Ensure text is readable

#### **Validation Failures**
- Check field formats match expected schemas
- Verify phone numbers follow Israeli format
- Ensure dates are in valid ranges

### **Debug Tips**
1. **Check Console Logs** for detailed information
2. **Verify File Format** (PDF, JPG, PNG supported)
3. **Test with Sample Documents** first

## 📚 API Reference

### **Main Functions**

#### `process_form(file_stream)`
- **Input**: File stream (PDF/Image)
- **Output**: Tuple of (detected_language, extracted_json)
- **Purpose**: Main processing pipeline

#### `validate_extracted_data(json_string)`
- **Input**: JSON string from extraction
- **Output**: Validation results with scores and fixes
- **Purpose**: Comprehensive data validation

### **Phone Fix Functions**

#### `fix_mobile_phone(phone_number)`
- **Input**: Raw phone number string
- **Output**: Standardized 10-digit mobile number starting with 05
- **Purpose**: Mobile phone standardization

#### `fix_landline_phone(phone_number)`
- **Input**: Raw phone number string
- **Output**: Standardized 9-digit landline number starting with 0
- **Purpose**: Landline phone standardization



**Version**: 2.0  
**Last Updated**: August 2025  
**Status**: Production Ready with Enhanced Features