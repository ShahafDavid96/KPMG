# KPMG - AI-Powered Document Processing & Healthcare Information System

## Project Overview

This repository contains two AI-powered systems developed for KPMG:

1. **NII (National Insurance Institute) Forms Extractor** - Document processing for Israeli insurance forms
2. **Healthcare Chatbot** - Medical services information system for Israeli health funds

Both systems use Azure AI services for enhanced capabilities.

---

## System 1: NII Forms Extractor

### Purpose
Document processing system for extracting and validating data from **Bituach Leumi Form 283** (National Insurance Institute accident report forms).

### Key Features
- **OCR Processing**: Azure Document Intelligence for text extraction
- **Field Extraction**: Azure OpenAI for intelligent field identification
- **Multi-language Support**: Hebrew and English form processing
- **Data Validation**: Schema compliance and completeness scoring
- **Phone Number Correction**: Automatic formatting for Israeli phone numbers
- **Web Interface**: Streamlit-based drag-and-drop interface

### Technology Stack
- **Backend**: Python with Azure AI services
- **Frontend**: Streamlit
- **AI Services**: Azure Document Intelligence, Azure OpenAI
- **Validation**: Pydantic models

---

## System 2: Healthcare Chatbot

### Purpose
Healthcare information system providing medical services information for users in Israel based on their HMO and insurance details.

### Key Features
- **Chat Interface**: Natural language processing for healthcare queries
- **HMO-Specific Information**: Responses for Maccabi, Meuhedet, and Clalit
- **RAG Search**: Retrieval Augmented Generation for context-aware responses
- **Bilingual Support**: Hebrew and English interfaces
- **Service Coverage**: Dental, optometry, pregnancy, alternative medicine, workshops, communication clinic

### Technology Stack
- **Backend**: FastAPI with Azure OpenAI integration
- **Frontend**: Streamlit
- **Knowledge Base**: RAG system with FAISS vector search
- **AI Services**: Azure OpenAI embeddings and chat completion

---

## Getting Started

### Prerequisites
- Python 3.8+
- Azure subscription with AI services
- Git

### Installation

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd KPMG
```

#### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Install NII-specific dependencies
cd NII_src
pip install -r requirements.txt

# Install Healthcare Chatbot dependencies
cd ../healthcare_chatbot_src
pip install -r requirements.txt
```

#### 4. Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env with your Azure credentials
```

---

## Running the Systems

### NII Forms Extractor
```bash
cd NII_src
streamlit run app.py
```
- **Access**: http://localhost:8501

### Healthcare Chatbot
```bash
# Terminal 1: Start the API backend
cd healthcare_chatbot_src
python main.py

# Terminal 2: Start the frontend
cd healthcare_chatbot_src
streamlit run frontend.py
```
- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Project Structure

```
KPMG/
├── README.md                    # Project overview
├── requirements.txt             # Core dependencies
├── env.example                  # Environment template
│
├── NII_data/                    # Sample insurance forms
├── NII_src/                     # NII Forms Extractor
│   ├── app.py                   # Streamlit application
│   ├── form_extractor.py        # Core extraction logic
│   ├── validator.py             # Data validation
│   ├── config.py                # Configuration
│   ├── prompt.txt               # AI prompts
│   └── readme.md                # Detailed documentation
│
├── healthcare_chatbot_data/     # Healthcare service files
├── healthcare_chatbot_src/      # Healthcare Chatbot
│   ├── main.py                  # FastAPI entry point
│   ├── api.py                   # API endpoints
│   ├── frontend.py              # Streamlit interface
│   ├── rag_kb.py                # RAG knowledge base
│   ├── models.py                # Data models
│   ├── config.py                # Configuration
│   ├── prompts.py               # LLM prompts
│   ├── utils.py                 # Utility functions
│   └── README.md                # Detailed documentation
│
└── .venv/                       # Virtual environment
```

---

## Configuration

### Azure AI Services
Both systems require Azure AI services:

```bash
# Azure Document Intelligence (for NII)
DOCUMENTINTELLIGENCE_ENDPOINT=your_endpoint
DOCUMENTINTELLIGENCE_API_KEY=your_api_key

# Azure OpenAI (for both systems)
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
```

---

## Testing

### NII System Testing
```bash
cd NII_src
python test_validator.py
python test_simple.py
```

### Healthcare Chatbot Testing
```bash
cd healthcare_chatbot_src
cd tests
python test_all.py
```

---

## Documentation

- **This README**: Project overview and setup instructions
- **NII_src/readme.md**: Detailed NII system documentation
- **healthcare_chatbot_src/README.md**: Detailed Healthcare Chatbot documentation

---

**Version**: 1.0  
**Last Updated**: August 2025
