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
    format_user_info_for_prompt_context,
    format_conversation_history,
    get_error_message,
    safe_log_text
)
from config import get_azure_client, validate_configuration, AZURE_OPENAI_DEPLOYMENT_NAME
import os

logger = logging.getLogger(__name__)
router = APIRouter()

# Debug: Log which utils module is being imported
import utils
logger.info(f"DEBUG: Imported utils module from: {utils.__file__}")
logger.info(f"DEBUG: Utils module content preview: {dir(utils)[:10]}")

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
            # Create a conversation history that includes the current message
            current_conversation = request.conversation_history + [{"role": "user", "content": request.message}]
            
            # Extract any information the user might have provided
            extracted_info = extract_user_info_from_conversation(current_conversation)
            
            # Debug logging
            logger.info(f"DEBUG: Extracted info: {extracted_info}")
            logger.info(f"DEBUG: Current phase: {request.phase}")
            
            # Check if we have complete information
            if extracted_info and is_user_info_complete(extracted_info):
                logger.info(f"DEBUG: User info is complete, transitioning to validation phase")
                
                # Instead of going directly to QA, go to validation first
                validation_response = format_user_info_for_prompt(extracted_info, request.language)
                
                if request.language == "he":
                    response_text = f"מעולה! הנה סיכום המידע שלך:\n\n{validation_response}\n\nהאם המידע הזה נכון? אם כן, אני אמשיך לעזור לך. אם לא, אנא תקן את הטעויות."
                else:
                    response_text = f"Excellent! Here is a summary of your information:\n\n{validation_response}\n\nIs this information correct? If yes, I'll continue to help you. If not, please correct any errors."
                
                logger.info(f"DEBUG: Transitioning to validation phase with response: {response_text[:100]}...")
                
                return ChatResponse(
                    response=response_text,
                    phase="validation",  # New validation phase
                    user_info=None,  # Not complete yet, needs validation
                    user_info_complete=False
                )
                
            else:
                logger.info(f"DEBUG: User info is NOT complete. Extracted: {extracted_info}")
                if extracted_info:
                    logger.info(f"DEBUG: Missing fields: {[field for field in ['name', 'id_number', 'gender', 'age', 'hmo_name', 'hmo_card_number', 'insurance_tier'] if field not in extracted_info or not extracted_info[field]]}")
            
            # If information is not complete, ask for all missing information
            collected_info = format_user_info_for_prompt_context(extracted_info, request.language) if extracted_info else ""
            
            prompt_context = system_prompt.format(
                conversation_history=format_conversation_history(request.conversation_history),
                collected_info=collected_info,
                user_message=request.message
            )
            
            # Generate response using Azure OpenAI
            try:
                response = azure_client.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4o"),
                    messages=[
                        {"role": "system", "content": prompt_context},
                        {"role": "user", "content": request.message}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                
                response_text = response.choices[0].message.content
                
                return ChatResponse(
                    response=response_text,
                    phase="info_collection",
                    user_info=None,
                    user_info_complete=False
                )
                
            except Exception as e:
                logger.error(f"Azure OpenAI API error: {e}")
                logger.error(f"Error type: {type(e).__name__}")
                logger.error(f"Azure client attributes: {dir(azure_client)}")
                
                # Fallback response
                if request.language == "he":
                    fallback_response = "מצטער, יש בעיה טכנית. בוא ננסה שוב או נחכה רגע."
                else:
                    fallback_response = "Sorry, there's a technical issue. Let's try again or wait a moment."
                
                return ChatResponse(
                    response=fallback_response,
                    phase="info_collection",
                    user_info=None,
                    user_info_complete=False
                )
        elif request.phase == "validation":
            # New validation phase
            logger.info(f"DEBUG: In validation phase")
            
            # In validation phase, we should have the extracted info from the previous phase
            # We need to re-extract it from the conversation history since we don't store it between requests
            extracted_info = extract_user_info_from_conversation(request.conversation_history)
            
            if not extracted_info or not is_user_info_complete(extracted_info):
                logger.info(f"DEBUG: Information incomplete in validation phase, going back to info collection")
                # Go back to information collection phase
                if request.language == "he":
                    response_text = "אני מבין שהמידע לא שלם. בוא נמשיך לאסוף את המידע החסר בצורה ידידותית."
                else:
                    response_text = "I understand the information is incomplete. Let's continue collecting the missing information in a friendly way."
                
                return ChatResponse(
                    response=response_text,
                    phase="info_collection",  # Go back to info collection
                    user_info=None,
                    user_info_complete=False
                )
            
            # Check if user is confirming the information
            user_message_lower = request.message.lower()
            confirmation_indicators = {
                "he": ["כן", "נכון", "בסדר", "אוקיי", "מעולה", "טוב", "נכון", "אמת", "אמתי"],
                "en": ["yes", "correct", "right", "okay", "ok", "good", "true", "accurate", "perfect"]
            }
            
            is_confirmed = any(indicator in user_message_lower for indicator in confirmation_indicators[request.language])
            
            if is_confirmed:
                logger.info(f"DEBUG: User confirmed information, transitioning to QA phase")
                
                # Clean the extracted data before creating UserInfo object
                cleaned_info = {}
                
                # Clean HMO name - extract only the valid HMO part
                hmo_name = extracted_info.get('hmo_name', '')
                valid_hmos = ['מכבי', 'מאוחדת', 'כללית', 'Maccabi', 'Meuhedet', 'Clalit']
                cleaned_hmo = None
                for valid_hmo in valid_hmos:
                    if valid_hmo.lower() in hmo_name.lower():
                        cleaned_hmo = valid_hmo
                        break
                
                if not cleaned_hmo:
                    # Fallback: use the first valid HMO found in the text
                    for valid_hmo in valid_hmos:
                        if valid_hmo in hmo_name:
                            cleaned_hmo = valid_hmo
                            break
                
                cleaned_info['hmo_name'] = cleaned_hmo or 'מכבי'  # Default fallback
                
                # Clean insurance tier - extract only the valid tier part
                insurance_tier = extracted_info.get('insurance_tier', '')
                valid_tiers = ['זהב', 'כסף', 'ארד', 'Gold', 'Silver', 'Bronze']
                cleaned_tier = None
                for valid_tier in valid_tiers:
                    if valid_tier.lower() in insurance_tier.lower():
                        cleaned_tier = valid_tier
                        break
                
                if not cleaned_tier:
                    # Fallback: use the first valid tier found in the text
                    for valid_tier in valid_tiers:
                        if valid_tier in insurance_tier:
                            cleaned_tier = valid_tier
                            break
                
                cleaned_info['insurance_tier'] = cleaned_tier or 'זהב'  # Default fallback
                
                # Clean other fields
                cleaned_info['id_number'] = str(extracted_info.get('id_number', '')).strip()
                cleaned_info['age'] = int(extracted_info.get('age', 0))
                cleaned_info['gender'] = str(extracted_info.get('gender', '')).strip()
                cleaned_info['hmo_card_number'] = str(extracted_info.get('hmo_card_number', '')).strip()
                
                # Split name into first and last name
                name_parts = extracted_info.get('name', '').split()
                first_name = name_parts[0] if name_parts else ''
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                
                logger.info(f"DEBUG: Cleaned info for UserInfo creation: {cleaned_info}")
                
                # Create UserInfo object from cleaned data
                try:
                    from models import UserInfo
                    user_info = UserInfo(
                        first_name=first_name,
                        last_name=last_name,
                        id_number=cleaned_info['id_number'],
                        gender=cleaned_info['gender'],
                        age=cleaned_info['age'],
                        hmo_name=cleaned_info['hmo_name'],
                        hmo_card_number=cleaned_info['hmo_card_number'],
                        insurance_tier=cleaned_info['insurance_tier']
                    )
                    
                    # Transition to QA phase
                    if request.language == "he":
                        response_text = f"מעולה! המידע אומת בהצלחה. איך אני יכול לעזור לך היום?"
                    else:
                        response_text = f"Excellent! Information verified successfully. How can I help you today?"
                    
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
                    # If UserInfo creation fails, provide a helpful error message
                    if request.language == "he":
                        error_response = "מצטער, יש בעיה בעיבוד המידע. אנא נסה שוב או פנה לתמיכה."
                    else:
                        error_response = "Sorry, there's an issue processing the information. Please try again or contact support."
                    
                    return ChatResponse(
                        response=error_response,
                        phase="validation",
                        user_info=None,
                        user_info_complete=False
                    )
            else:
                # User needs to correct information or confirmation unclear
                if request.language == "he":
                    response_text = "אני מבין שהמידע צריך תיקון. בוא נתקן אותו יחד בצורה ידידותית."
                else:
                    response_text = "I understand the information needs correction. Let's fix it together in a friendly way."
                
                return ChatResponse(
                    response=response_text,
                    phase="info_collection",  # Go back to info collection
                    user_info=None,
                    user_info_complete=False
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
