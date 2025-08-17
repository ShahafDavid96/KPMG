"""
Configuration for the Medical Services ChatBot
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_DEBUG = os.getenv("API_DEBUG", "false").lower() == "true"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "chatbot.log")

# Frontend Configuration
FRONTEND_HOST = os.getenv("FRONTEND_HOST", "localhost")
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "8501"))

# Validation
def validate_config():
    """Validate configuration values"""
    errors = []
    
    if not AZURE_OPENAI_API_KEY:
        errors.append("AZURE_OPENAI_API_KEY is required")
    
    if not AZURE_OPENAI_ENDPOINT:
        errors.append("AZURE_OPENAI_ENDPOINT is required")
    
    if not AZURE_OPENAI_DEPLOYMENT_NAME:
        errors.append("AZURE_OPENAI_DEPLOYMENT_NAME is required")
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")

def validate_configuration():
    """Validate that all required configuration is present"""
    missing_vars = []
    
    if not AZURE_OPENAI_ENDPOINT:
        missing_vars.append("AZURE_OPENAI_ENDPOINT")
    if not AZURE_OPENAI_API_KEY:
        missing_vars.append("AZURE_OPENAI_API_KEY")
    if not AZURE_OPENAI_DEPLOYMENT_NAME:
        missing_vars.append("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if missing_vars:
        error_msg = f"Missing Azure OpenAI configuration: {', '.join(missing_vars)}"
        raise ValueError(error_msg)

# Validate on import
try:
    validate_config()
except ValueError as e:
    print(f"Warning: {e}")
    print("Some features may not work properly without proper configuration")

def get_azure_client():
    """Get Azure OpenAI client"""
    try:
        from openai import AzureOpenAI
        
        if not all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_NAME]):
            return None
        
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        return client
        
    except ImportError:
        print("Warning: openai package not installed. Azure OpenAI features will not work.")
        return None
    except Exception as e:
        print(f"Warning: Could not initialize Azure OpenAI client: {e}")
        return None
