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
        
        # Create the extraction prompt with strict JSON requirements
        extraction_prompt = f"""Extract user information from the following input and return ONLY a valid JSON object with this exact structure:

{{
    "name": "string (first and last name only, no prefixes like 'היי קוראים לי')",
    "id_number": "string (exactly 9 digits)",
    "gender": "string (exactly: 'זכר' or 'נקבה' or 'male' or 'female')",
    "age": "integer (age between 0-120)",
    "hmo_name": "string (exactly: 'מכבי' or 'מאוחדת' or 'כללית' or 'Maccabi' or 'Meuhedet' or 'Clalit')",
    "hmo_card_number": "string (exactly 9 digits)",
    "insurance_tier": "string (exactly: 'זהב' or 'כסף' or 'ארד' or 'Gold' or 'Silver' or 'Bronze')"
}}

CRITICAL RULES:
1. Return ONLY valid JSON, no markdown, no explanations
2. For name: extract only the actual name, remove phrases like "היי קוראים לי", "קוראים לי", "אני", "שמי"
3. For gender: use only the exact values listed above
4. For HMO: use only the exact values listed above  
5. For insurance tier: use only the exact values listed above
6. If a field is not found, set it to null
7. Ensure all string values are properly cleaned and normalized

User input: {user_input}

JSON:"""

        # Call Azure OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a precise data extraction assistant. Always return valid JSON only, with no markdown formatting or additional text. Clean and normalize all extracted values according to the specified rules."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=500
        )
        
        # Extract the response content
        response_text = response.choices[0].message.content.strip()
        logger.info(f"AI extraction response: {response_text[:200]}...")
        
        # Clean the response text to extract pure JSON
        cleaned_response = clean_json_response(response_text)
        if not cleaned_response:
            logger.error("Failed to clean JSON response")
            return None
        
        # Parse JSON with proper error handling
        try:
            extracted_data = json.loads(cleaned_response)
            logger.info(f"Successfully parsed JSON: {extracted_data}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Cleaned response: {cleaned_response}")
            return None
        
        # Validate and normalize the data using structured validation
        validated_data = validate_and_normalize_extracted_data(extracted_data)
        if validated_data:
            logger.info(f"Validated and normalized data: {validated_data}")
            return validated_data
        
        return None
            
    except Exception as e:
        logger.error(f"Error in AI-based extraction: {e}")
        return None


def clean_json_response(response_text: str) -> Optional[str]:
    """Clean the AI response to extract pure JSON"""
    try:
        # Remove markdown code blocks
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.rfind("```")
            if end > start:
                response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.rfind("```")
            if end > start:
                response_text = response_text[start:end].strip()
        
        # Remove any leading/trailing text that's not JSON
        response_text = response_text.strip()
        
        # Find the first { and last } to extract JSON object
        start_brace = response_text.find('{')
        end_brace = response_text.rfind('}')
        
        if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
            json_text = response_text[start_brace:end_brace + 1]
            return json_text
        
        # If no braces found, try to find JSON-like content
        if response_text.startswith('{') and response_text.endswith('}'):
            return response_text
        
        logger.error(f"Could not extract JSON from response: {response_text}")
        return None
        
    except Exception as e:
        logger.error(f"Error cleaning JSON response: {e}")
        return None


def validate_and_normalize_extracted_data(extracted_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate extracted data using structured validation - no language conversion needed"""
    try:
        # Define valid values for each field (both languages are acceptable)
        valid_values = {
            'gender': ['זכר', 'נקבה', 'male', 'female'],
            'hmo_name': ['מכבי', 'מאוחדת', 'כללית', 'Maccabi', 'Meuhedet', 'Clalit'],
            'insurance_tier': ['זהב', 'כסף', 'ארד', 'Gold', 'Silver', 'Bronze']
        }
        
        # Simply validate and return the data as-is (no conversion needed)
        validated_data = {}
        
        # Process each field with minimal validation
        for field, value in extracted_data.items():
            if value is None:
                continue
                
            if field == 'name':
                # Clean name by removing common prefixes
                cleaned_name = clean_name_field(str(value))
                if cleaned_name:
                    validated_data[field] = cleaned_name
                    
            elif field == 'id_number':
                # Validate ID number format
                id_str = str(value).strip()
                if re.match(r'^\d{9}$', id_str):
                    validated_data[field] = id_str
                    
            elif field == 'gender':
                # Just validate that the value is in the allowed list
                gender = str(value).strip()
                if gender in valid_values['gender']:
                    validated_data[field] = gender  # Keep original value
                        
            elif field == 'age':
                # Validate age range
                try:
                    age = int(value)
                    if 0 <= age <= 120:
                        validated_data[field] = age
                except (ValueError, TypeError):
                    pass
                    
            elif field == 'hmo_name':
                # Just validate that the value is in the allowed list
                hmo = str(value).strip()
                if hmo in valid_values['hmo_name']:
                    validated_data[field] = hmo  # Keep original value
                        
            elif field == 'hmo_card_number':
                # Validate HMO card number format
                card_str = str(value).strip()
                if re.match(r'^\d{9}$', card_str):
                    validated_data[field] = card_str
                    
            elif field == 'insurance_tier':
                # Just validate that the value is in the allowed list
                tier = str(value).strip()
                if tier in valid_values['insurance_tier']:
                    validated_data[field] = tier  # Keep original value
        
        logger.info(f"Validated data (no language conversion): {validated_data}")
        return validated_data
        
    except Exception as e:
        logger.error(f"Error validating data: {e}")
        return None


def clean_name_field(name: str) -> Optional[str]:
    """Clean the name field by removing common prefixes and suffixes"""
    try:
        if not name or not name.strip():
            return None
            
        # Remove common Hebrew prefixes
        prefixes_to_remove = [
            r'^היי קוראים לי\s*',
            r'^קוראים לי\s*', 
            r'^אני\s+',
            r'^שמי\s*',
            r'^השם שלי\s*'
        ]
        
        cleaned_name = name.strip()
        for prefix in prefixes_to_remove:
            cleaned_name = re.sub(prefix, '', cleaned_name, flags=re.IGNORECASE)
        
        # Remove common suffixes that might appear after the name
        suffixes_to_remove = [
            r'\s+תז\s*\d+.*$',
            r'\s+אני בן\s+\d+.*$',
            r'\s+זכר.*$',
            r'\s+אני בקופת חולים.*$',
            r'\s+מספר\s+\d+.*$',
            r'\s+זהב.*$'
        ]
        
        for suffix in suffixes_to_remove:
            cleaned_name = re.sub(suffix, '', cleaned_name, flags=re.IGNORECASE)
        
        # Final cleanup
        cleaned_name = cleaned_name.strip()
        
        # Ensure we have a meaningful name (at least 2 characters)
        if len(cleaned_name) >= 2:
            return cleaned_name
            
        return None
        
    except Exception as e:
        logger.error(f"Error cleaning name field: {e}")
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


def format_user_info_for_prompt_context(user_info: Dict[str, Any], language: str = "he") -> str:
    """Format user information for prompt context (uses newlines for AI)"""
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
    
    # Use newlines for prompt context (AI processing)
    if formatted_info:
        return "\n".join(formatted_info)
    else:
        return "לא נאסף מידע על המשתמש עדיין." if language == "he" else "No user information collected yet."


def format_user_info_for_prompt(user_info: Dict[str, Any], language: str = "he") -> str:
    """Format user information for frontend display (uses HTML line breaks)"""
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
        if 'insurance_tier' in user_info:
            formatted_info.append(f"Insurance Tier: {user_info['insurance_tier']}")
    
    # Use HTML line breaks for frontend display
    if formatted_info:
        return "<br>".join(formatted_info)
    else:
        return "לא נאסף מידע על המשתמש עדיין." if language == "he" else "No user information collected yet."


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
