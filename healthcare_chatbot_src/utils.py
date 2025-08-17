"""
Utility functions for the Medical Services ChatBot
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional
from models import ChatMessage

logger = logging.getLogger(__name__)


def extract_user_info_from_conversation(conversation_history: List[Any]) -> Optional[Dict[str, Any]]:
    """Extract user information from conversation history using AI prompt"""
    try:
        logger.info("DEBUG: extract_user_info_from_conversation called with prompt-based approach")
        
        # Look for ALL user messages in the conversation
        user_messages = []
        for msg in conversation_history:
            if hasattr(msg, 'role') and msg.role == "user":
                # It's a ChatMessage object
                user_messages.append(msg)
            elif isinstance(msg, dict) and msg.get('role') == 'user':
                # It's a dictionary
                user_messages.append(msg)
        
        if not user_messages:
            logger.info("DEBUG: No user messages found")
            return None
        
        # Combine ALL user messages into one text for extraction
        all_user_content = []
        for msg in user_messages:
            if hasattr(msg, 'content'):
                # It's a ChatMessage object
                all_user_content.append(msg.content)
            elif isinstance(msg, dict):
                # It's a dictionary
                all_user_content.append(msg.get('content', ''))
        
        # Combine all user messages into one text
        message_content = " ".join(all_user_content)
        logger.info(f"DEBUG: Combined message content: {message_content[:100]}...")
        
        # Use AI prompt to extract information
        extracted_info = extract_info_with_ai_prompt(message_content)
        
        if extracted_info:
            logger.info(f"Extracted user info: {extracted_info}")
            return extracted_info
        
        logger.info("No user info extracted from message")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting user info: {e}")
        return None


def extract_info_with_ai_prompt(user_input: str) -> Optional[Dict[str, Any]]:
    """Use AI prompt to extract user information from input text"""
    try:
        # Import Azure client here to avoid circular imports
        from config import get_azure_client
        
        client = get_azure_client()
        if not client:
            logger.error("Azure OpenAI client not available")
            return None
        
        # Create the extraction prompt
        extraction_prompt = f"""Given the following user input, extract the user information and return ONLY a valid JSON object with the following structure:

{{
    "name": "string (first and last name)",
    "id_number": "string (9-digit ID number)",
    "gender": "string (male/female or זכר/נקבה)",
    "age": "integer (age between 0-120)",
    "hmo_name": "string (HMO name: מכבי/מאוחדת/כללית or Maccabi/Meuhedet/Clalit)",
    "hmo_card_number": "string (9-digit card number)",
    "insurance_tier": "string (Gold/Silver/Bronze or זהב/כסף/ארד)"
}}

Rules:
1. If a field is not found, set it to null
2. For name, extract only the actual name (not "היי קוראים לי" or similar phrases)
3. For HMO name, use only the standard names listed above
4. For insurance tier, use only the standard tiers listed above
5. Return ONLY the JSON, no other text

User input: {user_input}

JSON:"""

        # Call Azure OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts user information from text and returns it in JSON format. Always return valid JSON only."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=500
        )
        
        # Extract the response content
        response_text = response.choices[0].message.content.strip()
        logger.info(f"AI extraction response: {response_text[:200]}...")
        
        # Try to parse the JSON response
        try:
            # Remove any markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            extracted_data = json.loads(response_text)
            
            # Validate and clean the extracted data
            cleaned_data = {}
            
            # Clean name - remove extra text
            if extracted_data.get('name'):
                name = str(extracted_data['name']).strip()
                # Remove common prefixes/suffixes
                name = re.sub(r'^(היי קוראים לי|קוראים לי|אני|שמי)\s*', '', name)
                name = re.sub(r'\s+(תז|אני בן|זכר|אני בקופת חולים|מספר|זהב).*$', '', name)
                cleaned_data['name'] = name.strip()
            
            # Clean other fields
            if extracted_data.get('id_number'):
                cleaned_data['id_number'] = str(extracted_data['id_number']).strip()
            
            if extracted_data.get('gender'):
                gender = str(extracted_data['gender']).strip().lower()
                # Normalize gender values
                if gender in ['male', 'm', 'זכר']:
                    cleaned_data['gender'] = 'זכר'
                elif gender in ['female', 'f', 'נקבה']:
                    cleaned_data['gender'] = 'נקבה'
                else:
                    cleaned_data['gender'] = extracted_data['gender']
            
            if extracted_data.get('age') is not None:
                try:
                    age = int(extracted_data['age'])
                    if 0 <= age <= 120:
                        cleaned_data['age'] = age
                except (ValueError, TypeError):
                    pass
            
            if extracted_data.get('hmo_name'):
                hmo = str(extracted_data['hmo_name']).strip()
                # Normalize HMO names
                hmo_lower = hmo.lower()
                if 'maccabi' in hmo_lower or 'מכבי' in hmo:
                    cleaned_data['hmo_name'] = 'מכבי'
                elif 'meuhedet' in hmo_lower or 'מאוחדת' in hmo:
                    cleaned_data['hmo_name'] = 'מאוחדת'
                elif 'clalit' in hmo_lower or 'כללית' in hmo:
                    cleaned_data['hmo_name'] = 'כללית'
                else:
                    cleaned_data['hmo_name'] = hmo
            
            if extracted_data.get('hmo_card_number'):
                cleaned_data['hmo_card_number'] = str(extracted_data['hmo_card_number']).strip()
            
            if extracted_data.get('insurance_tier'):
                tier = str(extracted_data['insurance_tier']).strip()
                # Normalize insurance tiers
                tier_lower = tier.lower()
                if 'gold' in tier_lower or 'זהב' in tier:
                    cleaned_data['insurance_tier'] = 'זהב'
                elif 'silver' in tier_lower or 'כסף' in tier:
                    cleaned_data['insurance_tier'] = 'כסף'
                elif 'bronze' in tier_lower or 'ארד' in tier:
                    cleaned_data['insurance_tier'] = 'ארד'
                else:
                    cleaned_data['insurance_tier'] = tier
            
            logger.info(f"Cleaned extracted data: {cleaned_data}")
            return cleaned_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            return None
            
    except Exception as e:
        logger.error(f"Error in AI-based extraction: {e}")
        return None


def is_user_info_complete(user_info: Dict[str, Any]) -> bool:
    """Check if all required user information is complete"""
    required_fields = [
        'name', 'id_number', 'gender', 'age', 
        'hmo_name', 'hmo_card_number', 'insurance_tier'
    ]
    
    # Check if all required fields are present and not empty
    missing_fields = []
    for field in required_fields:
        if field not in user_info or not user_info[field]:
            missing_fields.append(field)
    
    if missing_fields:
        logger.info(f"Missing fields: {missing_fields}")
        logger.info(f"Available fields: {list(user_info.keys())}")
        return False
    
    # Additional validation
    try:
        # Validate ID number (9 digits)
        if not re.match(r'^\d{9}$', str(user_info['id_number'])):
            return False
        
        # Validate age (0-120)
        age = int(user_info['age'])
        if not (0 <= age <= 120):
            return False
        
        # Validate HMO card number (9 digits)
        if not re.match(r'^\d{9}$', str(user_info['hmo_card_number'])):
            return False
        
        # Validate HMO name - More flexible
        valid_hmo_names = ['מכבי', 'מאוחדת', 'כללית', 'maccabi', 'meuhedet', 'clalit']
        hmo_name = str(user_info['hmo_name']).lower()
        if not any(valid_hmo in hmo_name for valid_hmo in [hmo.lower() for hmo in valid_hmo_names]):
            return False
        
        # Validate insurance tier - More flexible
        valid_tiers = ['זהב', 'כסף', 'ארד', 'gold', 'silver', 'bronze']
        tier_name = str(user_info['insurance_tier']).lower()
        if not any(valid_tier in tier_name for valid_tier in [tier.lower() for tier in valid_tiers]):
            return False
        
        return True
        
    except (ValueError, TypeError):
        return False


def format_user_info_for_prompt(user_info: Dict[str, Any], language: str = "he") -> str:
    """Format user information for prompt context"""
    if not user_info:
        if language == "he":
            return "לא נאסף מידע על המשתמש עדיין."
        else:
            return "No user information collected yet."
    
    # Format based on language
    if language == "he":
        # Hebrew format
        formatted_info = []
        
        if 'name' in user_info:
            formatted_info.append(f"שם: {user_info['name']}")
        if 'id_number' in user_info:
            formatted_info.append(f"מספר תעודת זהות: {user_info['id_number']}")
        if 'gender' in user_info:
            formatted_info.append(f"מגדר: {user_info['gender']}")
        if 'age' in user_info:
            formatted_info.append(f"גיל: {user_info['age']}")
        if 'hmo_name' in user_info:
            formatted_info.append(f"קופת חולים: {user_info['hmo_name']}")
        if 'hmo_card_number' in user_info:
            formatted_info.append(f"מספר כרטיס: {user_info['hmo_card_number']}")
        if 'insurance_tier' in user_info:
            formatted_info.append(f"רמת ביטוח: {user_info['insurance_tier']}")
    else:
        # English format
        formatted_info = []
        
        if 'name' in user_info:
            formatted_info.append(f"Name: {user_info['name']}")
        if 'id_number' in user_info:
            formatted_info.append(f"ID Number: {user_info['id_number']}")
        if 'gender' in user_info:
            formatted_info.append(f"Gender: {user_info['gender']}")
        if 'age' in user_info:
            formatted_info.append(f"Age: {user_info['age']}")
        if 'hmo_name' in user_info:
            formatted_info.append(f"HMO: {user_info['hmo_name']}")
        if 'hmo_card_number' in user_info:
            formatted_info.append(f"Card Number: {user_info['hmo_card_number']}")
        if 'insurance_tier' in user_info:
            formatted_info.append(f"Insurance Tier: {user_info['insurance_tier']}")
    
    return "\n".join(formatted_info) if formatted_info else (
        "לא נאסף מידע על המשתמש עדיין." if language == "he" else "No user information collected yet."
    )


def format_conversation_history(conversation_history: List[Any]) -> str:
    """Format conversation history for prompts"""
    try:
        formatted_messages = []
        for msg in conversation_history:
            if hasattr(msg, 'dict'):
                # It's a ChatMessage object
                formatted_messages.append(msg.dict())
            elif isinstance(msg, dict):
                # It's already a dictionary
                formatted_messages.append(msg)
            else:
                # Fallback
                formatted_messages.append({
                    "role": getattr(msg, "role", "unknown"),
                    "content": getattr(msg, "content", str(msg)),
                    "timestamp": getattr(msg, "timestamp", None)
                })
        
        return json.dumps(formatted_messages, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error formatting conversation history: {e}")
        return "[]"


def validate_phase(phase: str) -> bool:
    """Validate that the phase is valid"""
    valid_phases = ["info_collection", "validation", "qa"]
    return phase in valid_phases


def validate_language(language: str) -> bool:
    """Validate that the language is supported"""
    valid_languages = ["he", "en"]
    return language in valid_languages


def sanitize_input(text: str) -> str:
    """Basic input sanitization"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = text.replace("<script>", "").replace("</script>", "")
    text = text.replace("javascript:", "")
    
    # Limit length
    if len(text) > 1000:
        text = text[:1000]
    
    return text.strip()


def get_error_message(language: str, error_type: str) -> str:
    """Get localized error messages"""
    error_messages = {
        "he": {
            "technical_error": "מצטער, יש בעיה טכנית. אנא נסה שוב מאוחר יותר.",
            "invalid_input": "הקלט שהוזן אינו תקין. אנא נסה שוב.",
            "service_unavailable": "השירות אינו זמין כרגע. אנא נסה שוב מאוחר יותר."
        },
        "en": {
            "technical_error": "Sorry, there's a technical issue. Please try again later.",
            "invalid_input": "The input provided is invalid. Please try again.",
            "service_unavailable": "The service is currently unavailable. Please try again later."
        }
    }
    
    return error_messages.get(language, {}).get(error_type, "An error occurred")


def safe_log_text(text: str, max_length: int = 200) -> str:
    """Safely log text that may contain Hebrew or special characters"""
    try:
        if not text:
            return "[Empty content]"
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        # Try to encode as ASCII (safe for logging)
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        
        if safe_text:
            return safe_text
        else:
            # If no ASCII content, return length info
            return f"[Content with special characters - length: {len(text)}]"
            
    except Exception:
        return f"[Content logging failed - length: {len(text)}]"
