# KPMG - AI-Powered Document Processing & Healthcare Information System

## Project Overview

This repository contains two sophisticated AI-powered systems developed for KPMG, showcasing advanced document processing and healthcare information management capabilities:

1. **NII (National Insurance Institute) Forms Extractor** - Intelligent document processing for Israeli insurance forms
2. **Healthcare Chatbot** - AI-powered medical services information system for Israeli health funds

Both systems leverage cutting-edge AI technologies including Azure AI services, OpenAI integration, and advanced natural language processing.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        KPMG PROJECT                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              NII Forms Extractor                        │   │
│  │  • Azure Document Intelligence                          │   │
│  │  • Azure OpenAI Integration                             │   │
│  │  • Multi-language Support (Hebrew/English)              │   │
│  │  • Intelligent Data Validation                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Healthcare Chatbot                         │   │
│  │  • RAG-Powered Knowledge Base                          │   │
│  │  • HMO-Specific Information                            │   │
│  │  • Bilingual Interface                                 │   │
│  │  • Microservice Architecture                            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## System 1: NII Forms Extractor

### Purpose
Advanced document processing system for extracting and validating data from **Bituach Leumi Form 283** (National Insurance Institute accident report forms).

### Key Features
- **Intelligent OCR**: Azure Document Intelligence for high-accuracy text extraction
- **AI-Powered Extraction**: Azure OpenAI for intelligent field identification and data extraction
- **Multi-language Support**: Automatic Hebrew/English language detection and processing
- **Comprehensive Validation**: Schema compliance, completeness scoring, and accuracy validation
- **Smart Data Correction**: Automatic phone number formatting and data standardization
- **Modern UI**: Streamlit-based drag-and-drop interface with real-time processing

### Technology Stack
- **Backend**: Python with Azure AI services
- **Frontend**: Streamlit with custom CSS
- **AI Services**: Azure Document Intelligence, Azure OpenAI
- **Validation**: Pydantic models with custom validation rules
- **Data Processing**: Intelligent text extraction and cleaning

---

## System 2: Healthcare Chatbot

### Purpose
AI-powered healthcare information system providing personalized medical services information for users in Israel based on their HMO (Health Maintenance Organization) and insurance details.

### Key Features
- **Intelligent Chat Interface**: Natural language processing for healthcare queries
- **HMO-Specific Information**: Tailored responses for Maccabi, Meuhedet, and Clalit
- **RAG-Powered Search**: Retrieval Augmented Generation for accurate, context-aware responses
- **Bilingual Support**: Hebrew and English interfaces
- **Comprehensive Coverage**: Dental, optometry, pregnancy, alternative medicine, workshops, and communication clinic services
- **Memory Efficient**: Optimized for minimal RAM usage with vector search capabilities

### Technology Stack
- **Backend**: FastAPI with Azure OpenAI integration
- **Frontend**: Streamlit with custom UI components
- **Knowledge Base**: RAG system with FAISS vector search
- **AI Services**: Azure OpenAI embeddings and chat completion
- **Data Processing**: HTML content chunking and vectorization

---

## Getting Started

### Prerequisites
- Python 3.8+
- Azure subscription with AI services (optional)
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

# Edit .env with your Azure credentials (optional)
# If not configured, systems will use fallback mechanisms
```

---

## Running the Systems

### NII Forms Extractor
```bash
cd NII_src
streamlit run app.py
```
- **Access**: http://localhost:8501
- **Features**: Drag-and-drop file upload, real-time processing, validation results

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
├── README.md                    # This file - Project overview
├── requirements.txt             # Core project dependencies
├── env.example                  # Environment variables template
│
├── NII_data/                    # Sample insurance forms (PDFs)
├── NII_src/                     # NII Forms Extractor source code
│   ├── app.py                   # Streamlit main application
│   ├── form_extractor.py        # Core extraction logic
│   ├── validator.py             # Data validation engine
│   ├── config.py                # Configuration and schemas
│   ├── prompt.txt               # AI prompts for extraction
│   └── readme.md                # Detailed NII documentation
│
├── healthcare_chatbot_data/     # Healthcare service HTML files
├── healthcare_chatbot_src/      # Healthcare Chatbot source code
│   ├── main.py                  # FastAPI application entry point
│   ├── api.py                   # API endpoints and chat logic
│   ├── frontend.py              # Streamlit user interface
│   ├── rag_kb.py                # RAG knowledge base implementation
│   ├── models.py                # Data models and schemas
│   ├── config.py                # Configuration and Azure setup
│   ├── prompts.py               # LLM prompts and language definitions
│   ├── utils.py                 # Utility functions
│   └── README.md                # Detailed Healthcare Chatbot documentation
│
└── .venv/                       # Virtual environment (created during setup)
```

---

## Configuration

### Azure AI Services (Optional)
Both systems can work with Azure AI services for enhanced capabilities:

```bash
# Azure Document Intelligence (for NII)
DOCUMENTINTELLIGENCE_ENDPOINT=your_endpoint
DOCUMENTINTELLIGENCE_API_KEY=your_api_key

# Azure OpenAI (for both systems)
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
```

### Fallback Mechanisms
- **NII System**: Falls back to basic text extraction if Azure services unavailable
- **Healthcare Chatbot**: Uses local embeddings and keyword search if Azure OpenAI unavailable

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
python test_system.py
python test_multiple_users.py
```

---

## Performance & Scalability

### NII Forms Extractor
- **Processing Speed**: Real-time document processing
- **Accuracy**: High-precision field extraction with validation
- **Scalability**: Handles multiple document formats and languages

### Healthcare Chatbot
- **Response Time**: Sub-second query responses
- **Memory Usage**: Optimized for minimal RAM usage (<1GB target)
- **Concurrent Users**: Supports multiple simultaneous users
- **Knowledge Base**: 18 optimized chunks covering 6 services × 3 HMOs

---

## Documentation

- **This README**: Project overview and setup instructions
- **NII_src/readme.md**: Detailed NII system documentation
- **healthcare_chatbot_src/README.md**: Detailed Healthcare Chatbot documentation
- **Code Comments**: Comprehensive inline documentation

---

**Version**: 1.0  
**Last Updated**: August 2025  
**Status**: Production Ready with Enhanced Features
