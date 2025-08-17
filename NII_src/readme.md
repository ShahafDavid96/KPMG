
# NII: National Insurance Institute Form Extraction & Validation

## Project Overview

This application processes and extracts data from **Bituach Leumi Form 283** (National Insurance Institute accident report forms). It uses Azure AI services for OCR and field extraction, with validation and data correction.

## Key Features

### Data Extraction
- **Azure Document Intelligence** for OCR text extraction
- **Azure OpenAI** for intelligent field extraction
- **Multi-language Support** (Hebrew and English)
- **Language Detection** using Azure services

### Intelligent Pre-processing
- **Markdown Content Cleaning**: Removes formatting that interferes with AI extraction
- **Checkbox Normalization**: Converts various checkbox formats (☐, ☑, ☒, [ ], [x]) to standard markers
- **Semantic Text Markers**: Adds intelligent markers for complex form relationships
  - Job Type Identification: "כאשר עבדתי ב" + occupation patterns
  - Work Location Markers: "סוג העבודה" section identification
  - Medical Field Markers: Health fund options and accident nature detection
- **Hebrew Text Processing**: Handles OCR spacing issues and word boundary restoration
- **Context-Aware Cleaning**: Preserves important form structure while removing noise

### Data Validation
- **Schema Compliance** using Pydantic models
- **Completeness Scoring** (percentage of filled fields)
- **Accuracy Scoring** (rule-based validation)
- **Phone Number Correction** for Israeli phone numbers

### User Interface
- **Drag & Drop Interface** for file upload
- **Processing Indicators** for user feedback
- **Results Display** with validation scores

### Phone Number Features
- **Mobile Phone**: Ensures 10 digits starting with 05
- **Landline Phone**: Ensures 9 digits starting with 0
- **Format Correction**: Removes country codes and formatting characters

### Technical Sophistication
- **Intelligent Pre-processing**: Advanced regex-based text cleaning and semantic markers
- **Dual Language Detection**: Azure OCR + OpenAI fallback for robust language identification
- **Smart Text Markers**: Context-aware markers for complex form fields (job type, work location, medical)
- **Comprehensive Validation**: Pydantic schema validation + custom business rules + automatic fixes
- **Data Quality Pipeline**: Multi-stage validation with detailed error reporting and auto-correction

## System Architecture

The NII system uses a sophisticated multi-stage pipeline with intelligent pre-processing, dual language detection, and comprehensive post-processing validation.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Upload   │───▶│  Azure Document  │───▶│  OCR Text       │
│   (PDF/Images)  │    │   Intelligence   │    │   Extraction    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Language       │    │   Pre-processing│
                       │   Detection      │    │   & Markers     │
                       │   (Azure+OpenAI) │    │   (Regex+Rules) │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Azure OpenAI   │    │   Language      │
                       │   Field Ext.     │    │   Mapping       │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Pydantic       │    │   Phone Number  │
                       │   Validation     │    │   Auto-fixes    │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Scoring        │    │   Final         │
                       │   (Complete+     │    │   Output        │
                       │    Accuracy)     │    │   (JSON)        │
                       └──────────────────┘    └─────────────────┘
```

### **Pipeline Stages Explained:**

#### **1. Document Processing**
- **Azure Document Intelligence**: OCR with Markdown output for better structure
- **Multi-format Support**: PDF, JPG, JPEG, PNG files
- **Language Detection**: Azure OCR + OpenAI fallback for Hebrew/English

#### **2. Intelligent Pre-processing**
- **Markdown Cleaning**: Removes formatting that confuses AI extraction
- **Checkbox Normalization**: Converts various checkbox formats to standard markers
- **Smart Text Markers**: Adds semantic markers for job type, work location, medical fields
- **Hebrew Text Processing**: Handles OCR spacing issues and word boundaries

#### **3. AI-Powered Extraction**
- **Azure OpenAI GPT-4**: Intelligent field extraction using structured prompts
- **Schema Compliance**: Ensures output matches Pydantic models exactly
- **Language Agnostic**: Works with both Hebrew and English forms

#### **4. Post-processing & Validation**
- **Pydantic Schema Validation**: Type safety and structure validation
- **Custom Business Rules**: Domain-specific validation (ID numbers, phone formats)
- **Automatic Data Fixes**: Phone number formatting, postal code cleaning
- **Comprehensive Scoring**: Completeness and accuracy metrics

#### **5. Data Quality Assurance**
- **Phone Number Fixes**: Mobile (05XXXXXXXX) and landline (0XXXXXXXX) standardization
- **ID Number Validation**: 9-digit Israeli ID format enforcement
- **Address Structure**: Nested object validation with postal code formatting
- **Date/Time Normalization**: Consistent format enforcement

### **Data Flow & Transformations**

#### **Input → OCR Stage**
```
PDF/Image → Azure Document Intelligence → Markdown OCR Text
```

#### **OCR → Pre-processing Stage**
```
Raw OCR → clean_markdown_content() → Enhanced Markers → Cleaned Text
```

#### **Pre-processing → AI Extraction Stage**
```
Cleaned Text + Smart Markers → Azure OpenAI → Structured JSON
```

#### **AI Output → Validation Stage**
```
Raw JSON → Pydantic Schema Validation → Business Rule Checking → Auto-fixes
```

#### **Validation → Final Output**
```
Validated Data + Fixes Applied → Completeness/Accuracy Scoring → Final JSON
```

### **Example Data Transformation**
```
Input: "☒ במפעל" (Checked checkbox)
↓
Pre-processing: "CHECKED_ACCIDENT_LOCATION: במפעל"
↓
AI Extraction: {"accidentLocation": "במפעל"}
↓
Validation: Passes (valid Hebrew text)
↓
Final Output: {"accidentLocation": "במפעל", "validation": "passed"}
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Azure subscription with:
  - Document Intelligence service
  - OpenAI service
- Valid API keys and endpoints

### Installation Steps
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

### Environment Variables
```bash
# Azure Document Intelligence
DOCUMENTINTELLIGENCE_ENDPOINT=your_endpoint
DOCUMENTINTELLIGENCE_API_KEY=your_api_key

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
```

## Running the Application

### Start the Streamlit App
```bash
streamlit run app.py
```

### Access the Application
- **Local URL**: http://localhost:8501
- **Network URL**: http://your-ip:8501

## Form Schema

### Personal Information
- `lastName` / `שם משפחה` - Family name
- `firstName` / `שם פרטי` - First name
- `idNumber` / `מספר זהות` - Israeli ID (9 digits)
- `gender` / `מין` - Gender
- `dateOfBirth` / `תאריך לידה` - Birth date

### Contact Details
- `address` - Complete address structure
- `landlinePhone` / `טלפון קווי` - Landline phone (9 digits)
- `mobilePhone` / `טלפון נייד` - Mobile phone (10 digits)

### Accident Information
- `dateOfInjury` / `תאריך התאונה` - Injury date
- `timeOfInjury` / `שעת התאונה` - Injury time (HH:MM)
- `accidentLocation` / `מיקום התאונה` - Accident location
- `accidentDescription` / `תיאור התאונה` - Accident description

### Medical Details
- `injuredBodyPart` / `איבר פגוע` - Injured body part
- `medicalInstitutionFields` - Medical institution information

## Validation Rules

The NII system implements a sophisticated multi-layer validation approach that ensures data quality at every stage.

### **Layer 1: Pydantic Schema Validation**
- **Type Safety**: Ensures all fields have correct data types (string, int, nested objects)
- **Structure Compliance**: Validates that all required fields exist and are properly nested
- **Default Values**: Automatically applies default values for missing optional fields
- **Schema Enforcement**: Prevents malformed data from entering the system

### **Layer 2: Business Rule Validation**
- **ID Number Format**: Must be exactly 9 digits, no letters, not all zeros
- **Mobile Phone Format**: Must be 10 digits starting with 05, auto-fixes common formats
- **Landline Phone Format**: Must be 9 digits starting with 0, handles extensions
- **Postal Code Format**: Must be 7 digits, auto-cleans non-digit characters
- **Date Plausibility**: Day (1-31), Month (1-12), Year (1900-2100)
- **Time Format**: Must be HH:MM format, auto-converts various input formats

### **Layer 3: Automatic Data Correction**
- **Phone Number Standardization**: Converts international formats to Israeli standards
- **ID Number Cleaning**: Removes non-digit characters and truncates to 9 digits
- **Postal Code Fixing**: Cleans and standardizes postal code format
- **Time Format Normalization**: Converts various time inputs to HH:MM format

### **Layer 4: Comprehensive Scoring**
- **Completeness Score**: Percentage of fields with meaningful values
- **Accuracy Score**: Rule-based validation with detailed violation reporting
- **Data Quality Metrics**: Detailed breakdown of validation failures and fixes applied

## API Reference

### Main Functions

#### `process_form(file_stream)`
- **Input**: File stream (PDF/Image)
- **Output**: Tuple of (detected_language, extracted_json)
- **Purpose**: Main processing pipeline

#### `validate_extracted_data(json_string)`
- **Input**: JSON string from extraction
- **Output**: Validation results with scores and fixes
- **Purpose**: Data validation

### Phone Fix Functions

#### `fix_mobile_phone(phone_number)`
- **Input**: Raw phone number string
- **Output**: Standardized 10-digit mobile number starting with 05

#### `fix_landline_phone(phone_number)`
- **Input**: Raw phone number string
- **Output**: Standardized 9-digit landline number starting with 0

## Troubleshooting

### Common Issues

#### Authentication Errors
- Verify Azure API keys are correct
- Check endpoint URLs are valid
- Ensure services are running and accessible

#### File Processing Errors
- Use clear, high-quality scans
- Avoid shadows or glare on documents
- PDF format generally works best
- Ensure text is readable

#### Validation Failures
- Check field formats match expected schemas
- Verify phone numbers follow Israeli format
- Ensure dates are in valid ranges

### Debug Tips
1. **Check Console Logs** for detailed information
2. **Verify File Format** (PDF, JPG, PNG supported)
3. **Test with Sample Documents** first

**Version**: 2.0  
**Last Updated**: August 2025