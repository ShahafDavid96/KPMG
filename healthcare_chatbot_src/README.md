# Medical Services ChatBot - Healthcare Information System

## Project Overview

A **microservice-based healthcare chatbot system** that provides personalized medical services information for users in Israel. The system helps users understand their healthcare coverage, available services, and benefits based on their HMO and insurance tier.

### Key Features
- **Bilingual Support**: Hebrew and English interfaces
- **Personalized Responses**: Tailored information based on user's HMO and insurance details
- **RAG-Powered**: Uses Retrieval Augmented Generation for accurate responses
- **Real-time Chat**: Interactive conversation flow with natural language processing

### What It Does
1. **Information Collection**: Gathers user's healthcare details (HMO, insurance tier, personal info)
2. **Service Queries**: Answers questions about available medical services, coverage, and benefits
3. **HMO-Specific Information**: Provides targeted information for Maccabi, Meuhedet, and Clalit
4. **Multi-Service Support**: Covers dental, optometry, pregnancy, alternative medicine, workshops, and communication clinic services

---

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI       │    │   RAG Knowledge │
│   Frontend      │◄──►│   Backend       │◄──►│   Base          │
│   (UI/UX)       │    │   (API/Logic)   │    │   (Vector DB)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Components
- **Frontend**: Streamlit web interface with language support
- **Backend**: FastAPI server handling chat logic and user validation
- **Knowledge Base**: RAG system with FAISS vector search for healthcare data

---

## Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
```bash
# Clone and navigate
cd healthcare_chatbot_src

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Running the System
```bash
# Terminal 1: Start the API backend
python main.py

# Terminal 2: Start the frontend
streamlit run frontend.py
```

### Access
- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Usage Flow
1. **Open Frontend**: Navigate to http://localhost:8501
2. **Select Language**: Choose Hebrew or English
3. **Provide Information**: Enter your healthcare details
4. **Ask Questions**: Query about services, coverage, and benefits
5. **Get Responses**: Receive personalized, HMO-specific information

---

## Project Structure
```
healthcare_chatbot_src/
├── main.py              # FastAPI application entry point
├── api.py               # API endpoints and chat logic
├── rag_kb.py            # RAG knowledge base implementation
├── frontend.py          # Streamlit user interface
├── utils.py             # Utility functions and text processing
├── prompts.py           # LLM prompts and language definitions
├── models.py            # Data models and schemas
├── config.py            # Configuration and Azure client setup
├── requirements.txt     # Python dependencies
└── tests/               # Test suite
```

---

## Testing
```bash
# Run comprehensive tests
cd tests
python test_all.py
```

The system provides a foundation for healthcare information services while maintaining simplicity and efficiency.
