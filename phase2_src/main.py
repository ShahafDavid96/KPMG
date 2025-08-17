"""
Main entry point for the Medical Services ChatBot
"""

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router
from config import validate_configuration, get_azure_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Medical Services ChatBot API",
    description="Microservice-based chatbot for Israeli health funds medical services",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Root redirect to API docs
@app.get("/")
async def root():
    """Redirect to API documentation"""
    return {"message": "Medical Services ChatBot API", "docs": "/docs"}


def create_app():
    """Create and configure the FastAPI application"""
    try:
        # Validate configuration
        validate_configuration()
        logger.info("Application configuration validated successfully")
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Medical Services ChatBot API...")
    
    # Check Azure OpenAI configuration
    azure_client = get_azure_client()
    if azure_client:
        logger.info("Azure OpenAI is configured and ready.")
    else:
        logger.warning("Azure OpenAI is not configured. Some features may not work properly.")
    
    # Initialize RAG knowledge base
    try:
        logger.info("Initializing RAG knowledge base...")
        from rag_kb import RAGKB
        
        # Use RAG with exactly 3 chunks per file (18 total)
        kb = RAGKB(use_azure_embeddings=True)
        
        # Set the global knowledge base instance for the API
        from api import set_knowledge_base
        set_knowledge_base(kb)
        
        # Log knowledge base status
        stats = kb.get_stats()
        logger.info(f"Knowledge base initialized successfully:")
        logger.info(f"  - Total services: {stats['total_services']}")
        logger.info(f"  - Total chunks: {stats['total_chunks']}")
        logger.info(f"  - Total embeddings: {stats['total_embeddings']}")
        logger.info(f"  - FAISS index available: {stats['has_faiss_index']}")
        logger.info(f"  - Embeddings ready: {stats['embeddings_ready']}")
        
        if stats['embeddings_ready']:
            logger.info("Vector RAG system ready with exactly 18 chunks!")
        else:
            logger.warning("Vector RAG system not available")
            
    except Exception as e:
        logger.error(f"Error initializing knowledge base: {e}")
        logger.warning("System will continue with limited functionality")
    
    logger.info("Medical Services ChatBot API startup complete!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Medical Services ChatBot API...")


if __name__ == "__main__":
    try:
        # Create the application
        app = create_app()
        
        # Start the server
        logger.info("Starting Medical Services ChatBot API...")
        logger.info("Frontend will be available at: http://localhost:8501")
        logger.info("Backend API will be available at: http://localhost:8000")
        logger.info("API Documentation will be available at: http://localhost:8000/docs")
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        logger.error("Please check the error messages above and fix any configuration issues.")
        exit(1)
