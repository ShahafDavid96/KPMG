"""
FastAPI routes and endpoints for the Medical Services ChatBot
"""

import time
import logging
from fastapi import APIRouter, HTTPException, Depends
from models import ChatRequest, ChatResponse, HealthStatus, ServicesList
from rag_kb import RAGKB
from prompts import get_prompt, get_suggested_questions
from utils import (
    extract_user_info_from_conversation, 
    is_user_info_complete, 
    format_user_info_for_prompt,
    format_conversation_history,
    get_error_message,
    safe_log_text
)
from config import get_azure_client, validate_configuration, AZURE_OPENAI_DEPLOYMENT_NAME

logger = logging.getLogger(__name__)
router = APIRouter()

# Global knowledge base instance (initialized during startup)
_knowledge_base = None


def get_knowledge_base():
    """Get the global knowledge base instance"""
    global _knowledge_base
    if _knowledge_base is None:
        logger.warning("Knowledge base not initialized, creating new instance")
        _knowledge_base = RAGKB(use_azure_embeddings=True)
    
    return _knowledge_base


def set_knowledge_base(kb_instance):
    """Set the global knowledge base instance (called during startup)"""
    global _knowledge_base
    _knowledge_base = kb_instance
    logger.info("Global knowledge base instance set")


@router.get("/", response_model=dict)
async def root():
    """Health check endpoint"""
    return {"message": "Medical Services ChatBot API is running", "status": "healthy"}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    try:
        start_time = time.time()
        logger.info(f"Received chat request for phase: {request.phase}")
        
        # Check if Azure OpenAI is configured
        azure_client = get_azure_client()
        if not azure_client:
            error_msg = "Azure OpenAI is not configured. Please set the required environment variables."
            logger.error(error_msg)
            raise HTTPException(status_code=503, detail=error_msg)
        
        # Get appropriate system prompt based on phase and language
        system_prompt = get_prompt(request.phase, request.language)
        
        # Information collection phase
        if request.phase == "info_collection":
            # Extract any information the user might have provided
            extracted_info = extract_user_info_from_conversation(request.conversation_history)
            
            # Debug logging
            logger.info(f"DEBUG: Extracted info: {extracted_info}")
            logger.info(f"DEBUG: Current phase: {request.phase}")
            
            # Check if we have complete information
            if extracted_info and is_user_info_complete(extracted_info):
                logger.info(f"DEBUG: User info is complete, transitioning to QA phase")
                # Create UserInfo object from extracted data
                try:
                    # Split name into first and last name
                    name_parts = extracted_info.get('name', '').split()
                    first_name = name_parts[0] if name_parts else ''
                    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                    
                    from models import UserInfo
                    user_info = UserInfo(
                        first_name=first_name,
                        last_name=last_name,
                        id_number=extracted_info['id_number'],
                        gender=extracted_info['gender'],
                        age=extracted_info['age'],
                        hmo_name=extracted_info['hmo_name'],
                        hmo_card_number=extracted_info['hmo_card_number'],
                        insurance_tier=extracted_info['insurance_tier']
                    )
                    
                    # Transition to QA phase - make it language-aware
                    if request.language == "he":
                        response_text = f"מעולה! הנה סיכום המידע שלך:\n\n{format_user_info_for_prompt(extracted_info, request.language)}\n\nאיך אני יכול לעזור לך היום?"
                    else:
                        response_text = f"Excellent! Here is a summary of your information:\n\n{format_user_info_for_prompt(extracted_info, request.language)}\n\nHow can I help you today?"
                    
                    logger.info(f"DEBUG: Created UserInfo object: {user_info}")
                    logger.info(f"DEBUG: Transitioning to QA phase with response: {response_text[:100]}...")
                    
                    return ChatResponse(
                        response=response_text,
                        phase="qa",
                        user_info=user_info,
                        user_info_complete=True
                    )
                    
                except Exception as e:
                    logger.error(f"Error creating UserInfo: {e}")
                    # Continue with information collection
            else:
                logger.info(f"DEBUG: User info is NOT complete. Extracted: {extracted_info}")
                if extracted_info:
                    logger.info(f"DEBUG: Missing fields: {[field for field in ['name', 'id_number', 'gender', 'age', 'hmo_name', 'hmo_card_number', 'insurance_tier'] if field not in extracted_info or not extracted_info[field]]}")
            
            # If information is not complete, ask for all missing information
            collected_info = format_user_info_for_prompt(extracted_info, request.language) if extracted_info else ""
            
            prompt_context = system_prompt.format(
                conversation_history=format_conversation_history(request.conversation_history),
                collected_info=collected_info,
                user_message=request.message
            )
        else:
            # QA phase
            user_info_str = format_user_info_for_prompt(request.user_info, request.language)
            
            # Use global knowledge base instance (embeddings already created during startup)
            knowledge_base = get_knowledge_base()
            logger.info(f"Using pre-initialized knowledge base for vector RAG search")
            
            # Get knowledge base stats for debugging
            kb_stats = knowledge_base.get_stats()
            logger.info(f"Knowledge base stats: {kb_stats}")
            
            medical_services_info = knowledge_base.search_services(
                request.message, 
                request.user_info.hmo_name if request.user_info else None,
                request.user_info.insurance_tier if request.user_info else None,
                top_k=3,  # Get top 3 most relevant chunks
                language=request.language  # Pass language for proper formatting
            )
            
            # Log the extracted information for debugging
            logger.info(f"User query: {request.message}")
            logger.info(f"User info: {user_info_str}")
            logger.info(f"Vector RAG results length: {len(medical_services_info)}")
            
            # Safe logging for Hebrew text
            safe_preview = safe_log_text(medical_services_info, max_length=200)
            logger.info(f"Vector RAG results preview: {safe_preview}")
            
            prompt_context = system_prompt.format(
                user_info=user_info_str,
                medical_services_info=medical_services_info,
                conversation_history=format_conversation_history(request.conversation_history),
                user_message=request.message
            )
        
        # Call Azure OpenAI
        try:
            # Get the model name safely
            model_name = None
            if hasattr(azure_client, 'deployment_name'):
                model_name = azure_client.deployment_name
            elif hasattr(azure_client, 'deployment'):
                model_name = azure_client.deployment
            else:
                model_name = AZURE_OPENAI_DEPLOYMENT_NAME
            
            logger.info(f"Using Azure OpenAI model: {model_name}")
            
            response = azure_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": prompt_context},
                    {"role": "user", "content": request.message}
                ],
                max_tokens=1000,
                temperature=0.4  # Lower temperature for more factual responses
            )
            
            bot_response = response.choices[0].message.content
            logger.info(f"Azure OpenAI response received successfully, length: {len(bot_response)}")
            
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Azure client attributes: {dir(azure_client)}")
            bot_response = get_error_message(request.language, "technical_error")
        
        # Determine if user info collection is complete
        user_info_complete = False
        if request.user_info:
            # Convert UserInfo to dict for validation
            user_info_dict = {
                'name': f"{request.user_info.first_name} {request.user_info.last_name}".strip(),
                'id_number': request.user_info.id_number,
                'gender': request.user_info.gender,
                'age': request.user_info.age,
                'hmo_name': request.user_info.hmo_name,
                'hmo_card_number': request.user_info.hmo_card_number,
                'insurance_tier': request.user_info.insurance_tier
            }
            user_info_complete = is_user_info_complete(user_info_dict)
        elif request.phase == "info_collection":
            # Check if we can extract complete info from conversation
            extracted_info = extract_user_info_from_conversation(request.conversation_history)
            if extracted_info:
                user_info_complete = is_user_info_complete(extracted_info)
        
        # Determine current phase
        current_phase = request.phase
        if user_info_complete and request.phase == "info_collection":
            current_phase = "qa"
        
        # Generate suggested questions for QA phase
        suggested_questions = None
        if current_phase == "qa" and request.user_info:
            suggested_questions = get_suggested_questions(request.language)
        
        response_time = time.time() - start_time
        logger.info(f"Chat response generated in {response_time:.2f} seconds")
        
        return ChatResponse(
            response=bot_response,
            phase=current_phase,
            user_info_complete=user_info_complete,
            suggested_questions=suggested_questions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services", response_model=ServicesList)
async def get_available_services():
    """Get list of available medical services"""
    try:
        knowledge_base = get_knowledge_base()
        services = knowledge_base.get_all_services()
        return ServicesList(services=services)
    except Exception as e:
        logger.error(f"Error getting services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    try:
        knowledge_base = get_knowledge_base()
        kb_stats = knowledge_base.get_stats()
        
        return HealthStatus(
            status="healthy",
            timestamp=time.time(),
            knowledge_base_loaded=knowledge_base.is_loaded(),
            azure_openai_configured=bool(get_azure_client()),
            vector_rag_available=kb_stats.get('embeddings_ready', False),
            total_chunks=kb_stats.get('total_chunks', 0),
            total_services=kb_stats.get('total_services', 0)
        )
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))
