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
    """Extract user information from conversation history"""
    try:
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
        
        # Safe logging for Hebrew content
        try:
            safe_preview = message_content[:100].encode('ascii', 'ignore').decode('ascii')
            if safe_preview:
                logger.info(f"Combined user content from {len(user_messages)} messages: {safe_preview}...")
            else:
                logger.info(f"Combined user content from {len(user_messages)} messages: [Hebrew content - length: {len(message_content)}]")
        except Exception:
            logger.info(f"Combined user content from {len(user_messages)} messages: [Content length: {len(message_content)}]")
        
        # Try to extract information using various patterns
        extracted_info = {}
        
        # Extract name patterns (Hebrew and English) - More flexible
        name_patterns = [
            r'שם[:\s]+([^\n\r,]+)',  # Hebrew: "שם: משה כהן"
            r'name[:\s]+([^\n\r,]+)',  # English: "name: Moshe Cohen"
            r'שם פרטי[:\s]+([^\n\r,]+)',  # Hebrew: "שם פרטי: משה"
            r'first name[:\s]+([^\n\r,]+)',  # English: "first name: Moshe"
            r'שם משפחה[:\s]+([^\n\r,]+)',  # Hebrew: "שם משפחה: כהן"
            r'last name[:\s]+([^\n\r,]+)',  # English: "last name: Cohen"
            r'קוראים לי[:\s]*([^\n\r,]+)',  # Hebrew: "קוראים לי משה כהן"
            r'my name is[:\s]*([^\n\r,]+)',  # English: "my name is Moshe Cohen"
            r'אני[:\s]*([^\n\r,]+)',  # Hebrew: "אני משה כהן"
            r'i am[:\s]*([^\n\r,]+)',  # English: "i am Moshe Cohen"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message_content, re.IGNORECASE)
            if match:
                extracted_info['name'] = match.group(1).strip()
                break
        
        # Extract ID number patterns - More flexible
        id_patterns = [
            r'תעודת זהות[:\s]*(\d{9})',  # Hebrew: "תעודת זהות: 123456789"
            r'id[:\s]*(\d{9})',  # English: "id: 123456789"
            r'מספר[:\s]*(\d{9})',  # Hebrew: "מספר: 123456789"
            r'number[:\s]*(\d{9})',  # English: "number: 123456789"
            r'ת.ז[:\s]*(\d{9})',  # Hebrew: "ת.ז: 123456789"
            r'תז[:\s]*(\d{9})',  # Hebrew: "תז: 123456789"
            r'(\d{9})',  # Any 9-digit number (fallback)
        ]
        
        for pattern in id_patterns:
            match = re.search(pattern, message_content, re.IGNORECASE)
            if match:
                extracted_info['id_number'] = match.group(1)
                break
        
        # Extract gender patterns
        gender_patterns = [
            r'מגדר[:\s]+([^\n\r,]+)',  # Hebrew: "מגדר: זכר"
            r'gender[:\s]+([^\n\r,]+)',  # English: "gender: male"
            r'זכר|נקבה',  # Hebrew: "זכר" or "נקבה"
            r'male|female',  # English: "male" or "female"
        ]
        
        for pattern in gender_patterns:
            match = re.search(pattern, message_content, re.IGNORECASE)
            if match:
                extracted_info['gender'] = match.group(1) if ':' in pattern else match.group(0)
                break
        
        # Extract age patterns - More flexible Hebrew
        age_patterns = [
            r'גיל[:\s]*(\d{1,3})',  # Hebrew: "גיל: 25"
            r'age[:\s]*(\d{1,3})',  # English: "age: 25"
            r'בן[:\s]*(\d{1,3})',  # Hebrew: "בן 25" (son of 25)
            r'בת[:\s]*(\d{1,3})',  # Hebrew: "בת 25" (daughter of 25)
            r'(\d{1,3})\s*שנה',  # Hebrew: "25 שנה" (25 years)
            r'(\d{1,3})\s*years?',  # English: "25 years"
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, message_content, re.IGNORECASE)
            if match:
                age = int(match.group(1))
                if 0 <= age <= 120:
                    extracted_info['age'] = age
                break
        
        # Extract HMO patterns - More flexible
        hmo_patterns = [
            r'קופת חולים[:\s]+([^\n\r,]+)',  # Hebrew: "קופת חולים: מכבי"
            r'hmo[:\s]+([^\n\r,]+)',  # English: "hmo: Maccabi"
            r'קופה[:\s]+([^\n\r,]+)',  # Hebrew: "קופה: מכבי"
            r'fund[:\s]+([^\n\r,]+)',  # English: "fund: Maccabi"
            r'מכבי|מאוחדת|כללית',  # Hebrew HMO names
            r'maccabi|meuhedet|clalit',  # English HMO names
        ]
        
        for pattern in hmo_patterns:
            match = re.search(pattern, message_content, re.IGNORECASE)
            if match:
                extracted_info['hmo_name'] = match.group(1) if ':' in pattern else match.group(0)
                break
        
        # Extract HMO card number patterns - More flexible
        card_patterns = [
            r'כרטיס[:\s]*(\d{9})',  # Hebrew: "כרטיס: 123456789"
            r'card[:\s]*(\d{9})',  # English: "card: 123456789"
            r'מספר כרטיס[:\s]*(\d{9})',  # Hebrew: "מספר כרטיס: 123456789"
            r'כרטיס קופה[:\s]*(\d{9})',  # Hebrew: "כרטיס קופה: 123456789"
            r'קופת חולים כרטיס[:\s]*(\d{9})',  # Hebrew: "קופת חולים כרטיס: 123456789"
        ]
        
        # Try to find card number with specific patterns first
        for pattern in card_patterns:
            match = re.search(pattern, message_content, re.IGNORECASE)
            if match:
                extracted_info['hmo_card_number'] = match.group(1)
                break
        
        # If no specific pattern found, try to find second 9-digit number
        if 'hmo_card_number' not in extracted_info and 'id_number' in extracted_info:
            # Find all 9-digit numbers
            all_numbers = re.findall(r'(\d{9})', message_content)
            if len(all_numbers) >= 2:
                # First number is ID, second is card number
                extracted_info['hmo_card_number'] = all_numbers[1]
        
        # Extract insurance tier patterns
        tier_patterns = [
            r'ביטוח[:\s]+([^\n\r,]+)',  # Hebrew: "ביטוח: זהב"
            r'insurance[:\s]+([^\n\r,]+)',  # English: "insurance: Gold"
            r'רמה[:\s]+([^\n\r,]+)',  # Hebrew: "רמה: זהב"
            r'level[:\s]+([^\n\r,]+)',  # English: "level: Gold"
            r'זהב|כסף|ארד',  # Hebrew tiers
            r'gold|silver|bronze',  # English tiers
        ]
        
        for pattern in tier_patterns:
            match = re.search(pattern, message_content, re.IGNORECASE)
            if match:
                extracted_info['insurance_tier'] = match.group(1) if ':' in pattern else match.group(0)
                break
        
        # If we found some information, return it
        if extracted_info:
            logger.info(f"Extracted user info: {extracted_info}")
            return extracted_info
        
        # Special case: Check if this looks like a complete summary
        # This handles cases where the user says "here's my info" or similar
        summary_indicators = [
            r'הנה.*המידע',  # Hebrew: "הנה המידע"
            r'here.*info',  # English: "here is the info"
            r'סיכום.*מידע',  # Hebrew: "סיכום המידע"
            r'summary.*info',  # English: "summary of info"
        ]
        
        for pattern in summary_indicators:
            if re.search(pattern, message_content, re.IGNORECASE):
                logger.info("Detected summary format, attempting comprehensive extraction")
                # Try to extract any remaining information
                return extracted_info
        
        # Safe logging for Hebrew content
        try:
            safe_preview = message_content[:100].encode('ascii', 'ignore').decode('ascii')
            if safe_preview:
                logger.info(f"No user info extracted from message: {safe_preview}...")
            else:
                logger.info(f"No user info extracted from message: [Hebrew content - length: {len(message_content)}]")
        except Exception:
            logger.info(f"No user info extracted from message: [Content length: {len(message_content)}]")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting user info: {e}")
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
    valid_phases = ["info_collection", "qa"]
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
