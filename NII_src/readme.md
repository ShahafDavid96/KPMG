
# NII: National Insurance Institute Form Extraction & Validation

## Overview

This system processes **Bituach Leumi Form 283** (National Insurance Institute accident report forms) using Azure AI services. It extracts form data through OCR, AI-powered field extraction, and validates the results using Pydantic schemas and business rules.

**Key Capabilities:**
- OCR processing for PDF/Image files
- AI-powered field extraction (Hebrew/English)
- Multi-layer validation with automatic data fixes
- Phone number standardization for Israeli formats

## How to Run

### Setup
```bash
cd NII_src
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Azure credentials
```

### Run Application
```bash
streamlit run app.py
```
Access at: http://localhost:8501

## Architecture & Folder Content

### System Flow
```
User Upload → Azure OCR → Pre-processing → AI Extraction → Validation → Output
```

### Folder Structure
```
NII_src/
├── app.py              # Streamlit frontend
├── form_extractor.py   # OCR + AI extraction pipeline
├── validator.py        # Pydantic validation + business rules
├── config.py           # Azure config + Pydantic schemas
├── prompt.txt          # AI extraction prompts
├── test_validator.py   # Validation testing
└── requirements.txt    # Dependencies
```

### Core Components
- **OCR**: Azure Document Intelligence with Markdown output
- **AI Extraction**: Azure OpenAI GPT-4 for field extraction
- **Validation**: Pydantic schemas + custom business rules
- **Auto-fixes**: Phone number formatting, ID cleaning, data standardization