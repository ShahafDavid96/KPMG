# Medical Services ChatBot - Healthcare Information System

## 🏥 General Explanation

This project is a **microservice-based healthcare chatbot system** designed to provide personalized medical services information for users in Israel. The system helps users understand their healthcare coverage, available services, and benefits based on their HMO (Health Maintenance Organization) and insurance tier.

### **Key Features:**
- **Bilingual Support**: Hebrew and English interfaces
- **Personalized Responses**: Tailored information based on user's HMO and insurance details
- **RAG-Powered**: Uses Retrieval Augmented Generation for accurate, context-aware responses
- **Memory Efficient**: Optimized to handle large healthcare datasets with minimal RAM usage
- **Real-time Chat**: Interactive conversation flow with natural language processing

### **What It Does:**
1. **Information Collection**: Gathers user's healthcare details (HMO, insurance tier, personal info)
2. **Service Queries**: Answers questions about available medical services, coverage, and benefits
3. **HMO-Specific Information**: Provides targeted information for Maccabi, Meuhedet, and Clalit
4. **Multi-Service Support**: Covers dental, optometry, pregnancy, alternative medicine, workshops, and communication clinic services

---

## 🏗️ Microservice Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Streamlit Web Interface                    │   │
│  │  • Hebrew/English Language Support                     │   │
│  │  • Real-time Chat Interface                           │   │
│  │  • User Information Collection                         │   │
│  │  • Conversation History Management                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP Requests
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend                            │   │
│  │  • RESTful API Endpoints                               │   │
│  │  • Chat Processing & Response Generation               │   │
│  │  • User Information Validation                         │   │
│  │  • Conversation State Management                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Internal Calls
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE BASE LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              RAG Knowledge Base                         │   │
│  │  • HMO-Based Chunking (18 chunks total)                │   │
│  │  • Vector Embeddings (Azure OpenAI + Fallback)         │   │
│  │  • FAISS Vector Search Index                           │   │
│  │  • HTML Data Processing & Cleaning                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Data Access
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Healthcare Service Files                   │   │
│  │  • 6 HTML Service Files                                │   │
│  │  • 3 Chunks per File (HMO-based)                       │   │
│  │  • Coverage: Dental, Optometry, Pregnancy, etc.        │   │
│  │  • HMOs: Maccabi, Meuhedet, Clalit                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### **Architecture Components:**

#### **Frontend (Streamlit)**
- **Purpose**: User interface and interaction
- **Features**: Language switching, conversation display, input handling
- **Technology**: Streamlit with custom CSS and JavaScript

#### **API Layer (FastAPI)**
- **Purpose**: Backend logic and API endpoints
- **Features**: Chat processing, user validation, response generation
- **Technology**: FastAPI with Azure OpenAI integration

#### **Knowledge Base (RAG)**
- **Purpose**: Information retrieval and storage
- **Features**: Vector search, HMO filtering, content chunking
- **Technology**: FAISS, Azure OpenAI embeddings, custom chunking

#### **Data Layer**
- **Purpose**: Raw healthcare service information
- **Content**: HTML files with service details, pricing, and coverage
- **Structure**: 6 services × 3 HMOs = 18 total chunks

---

## 🚀 Installation and Run Instructions

### **Prerequisites**
- Python 3.8+
- pip package manager
- Access to Azure OpenAI (optional, fallback available)

### **1. Clone and Setup**
```bash
# Clone the repository
git clone <repository-url>
cd Home-Assignment-GenAI-KPMG/healthcare_chatbot_src

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Configuration**
```bash
# Copy and configure environment variables
cp config.py.example config.py

# Edit config.py with your Azure OpenAI credentials (optional)
# If not configured, the system will use fallback embeddings
```

### **3. Run the System**

#### **Option A: Using Start Scripts**
```bash
# Windows
start_system.bat

# Linux/Mac
./start_system.sh

# Python (cross-platform)
python start_system.py
```

#### **Option B: Manual Start**
```bash
# Terminal 1: Start the API backend
python main.py

# Terminal 2: Start the frontend
streamlit run frontend.py
```

### **4. Access the Application**
- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### **5. System Testing**
```bash
# Run comprehensive system tests
python test_system.py

# Test specific components
python -c "from rag_kb import RAGKB; kb = RAGKB(); print(kb.get_stats())"
```

### **6. Usage Flow**
1. **Open Frontend**: Navigate to http://localhost:8501
2. **Select Language**: Choose Hebrew or English
3. **Provide Information**: Enter your healthcare details
4. **Ask Questions**: Query about services, coverage, and benefits
5. **Get Responses**: Receive personalized, HMO-specific information

### **7. Troubleshooting**

#### **Common Issues:**
- **Port Already in Use**: Change ports in `main.py` and `frontend.py`
- **Azure OpenAI Errors**: System automatically falls back to local embeddings
- **Memory Issues**: System is optimized for minimal RAM usage (target: <1GB)

#### **Health Checks:**
```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Check knowledge base status
curl http://localhost:8000/api/v1/chat -X POST -H "Content-Type: application/json" -d '{"message": "test"}'
```

### **8. System Requirements**
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: 100MB for application + data
- **Network**: Internet access for Azure OpenAI (optional)
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

---

## 📁 Project Structure
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
├── test_system.py       # Comprehensive system testing
├── start_system.py      # System startup orchestration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

The system is designed to be **production-ready** with proper error handling, logging, and fallback mechanisms. It provides a robust foundation for healthcare information services while maintaining simplicity and efficiency.
