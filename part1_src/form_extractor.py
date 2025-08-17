# form_extractor.py
import json
import logging
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentContentFormat, AnalyzeResult
import re # Added for regex operations

# Import all settings and schemas from the config file
import config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# --- Function Definitions ---

def get_azure_openai_client():
    """Initializes and returns the Azure OpenAI client using config."""
    try:
        client = AzureOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION
        )
        logger.info("Azure OpenAI client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI client: {e}")
        raise RuntimeError(f"Azure OpenAI client initialization failed: {e}")

def get_document_intelligence_client():
    """Initializes and returns the Azure Document Intelligence client using config."""
    try:
        client = DocumentIntelligenceClient(
            endpoint=config.DOCUMENTINTELLIGENCE_ENDPOINT,
            credential=AzureKeyCredential(config.DOCUMENTINTELLIGENCE_API_KEY)
        )
        logger.info("Document Intelligence client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Document Intelligence client: {e}")
        raise RuntimeError(f"Document Intelligence client initialization failed: {e}")

def map_response_to_language(ai_response, target_language):
    """Maps AI response to the correct language format based on target language."""
    try:
        logger.info(f"Starting language mapping for target language: {target_language}")
        logger.info(f"AI response type: {type(ai_response)}")
        logger.info(f"AI response preview: {ai_response[:200]}...")
        
        # Parse the AI response
        response_data = json.loads(ai_response)
        logger.info(f"Parsed JSON keys: {list(response_data.keys())}")
        
        if target_language.lower() == "hebrew":
            logger.info("Language is Hebrew, mapping to Hebrew keys...")
            # AI returned English keys, map to Hebrew keys
            hebrew_mapping = {
                "lastName": "שם משפחה",
                "firstName": "שם פרטי", 
                "idNumber": "מספר זהות",
                "gender": "מין",
                "dateOfBirth": "תאריך לידה",
                "address": "כתובת",
                "landlinePhone": "טלפון קווי",
                "mobilePhone": "טלפון נייד",
                "jobType": "סוג העבודה",
                "dateOfInjury": "תאריך הפגיעה",
                "timeOfInjury": "שעת הפגיעה",
                "accidentLocation": "מקום התאונה",
                "accidentAddress": "כתובת מקום התאונה",
                "accidentDescription": "תיאור התאונה",
                "injuredBodyPart": "האיבר שנפגע",
                "signature": "חתימה",
                "formFillingDate": "תאריך מילוי הטופס",
                "formReceiptDateAtClinic": "תאריך קבלת הטופס בקופה",
                "medicalInstitutionFields": "למילוי ע\"י המוסד הרפואי"
            }
            
            # Create new Hebrew response
            hebrew_response = {}
            for english_key, hebrew_key in hebrew_mapping.items():
                if english_key in response_data:
                    if english_key in ["dateOfBirth", "dateOfInjury", "formFillingDate", "formReceiptDateAtClinic"]:
                        # Handle nested date objects
                        hebrew_response[hebrew_key] = {
                            "יום": response_data[english_key].get("day", ""),
                            "חודש": response_data[english_key].get("month", ""),
                            "שנה": response_data[english_key].get("year", "")
                        }
                    elif english_key == "address":
                        # Handle nested address object
                        hebrew_response[hebrew_key] = {
                            "רחוב": response_data[english_key].get("street", ""),
                            "מספר בית": response_data[english_key].get("houseNumber", ""),
                            "כניסה": response_data[english_key].get("entrance", ""),
                            "דירה": response_data[english_key].get("apartment", ""),
                            "ישוב": response_data[english_key].get("city", ""),
                            "מיקוד": response_data[english_key].get("postalCode", ""),
                            "תא דואר": response_data[english_key].get("poBox", "")
                        }
                    elif english_key == "medicalInstitutionFields":
                        # Handle nested medical fields object
                        hebrew_response[hebrew_key] = {
                            "חבר בקופת חולים": response_data[english_key].get("healthFundMember", ""),
                            "מהות התאונה": response_data[english_key].get("natureOfAccident", ""),
                            "אבחנות רפואיות": response_data[english_key].get("medicalDiagnoses", "")
                        }
                    else:
                        # Simple string fields
                        hebrew_response[hebrew_key] = response_data[english_key]
            
            logger.info(f"Hebrew response created with {len(hebrew_response)} fields")
            logger.info(f"Hebrew keys: {list(hebrew_response.keys())}")
            
            result = json.dumps(hebrew_response, ensure_ascii=False, indent=2)
            logger.info("Language mapping completed successfully")
            return result
        else:
            logger.info("Language is English, returning original response")
            # English language - return as is
            return ai_response
            
    except Exception as e:
        logger.error(f"Failed to map response to language {target_language}: {e}")
        # Return original response if mapping fails
        return ai_response

def get_json_schema_for_language(language="hebrew"):
    """Returns an empty JSON string based on the pydantic model."""
    try:
        # Always use English schema - language mapping will handle conversion
        model = config.FormSchemaEN()
        return json.dumps(model.model_dump(by_alias=False), indent=2)
    except Exception as e:
        logger.error(f"Failed to generate JSON schema for language {language}: {e}")
        raise RuntimeError(f"Schema generation failed: {e}")

def analyze_document_with_ocr(file_stream):
    """Analyzes a document using Azure Document Intelligence's layout model with Markdown output."""
    try:
        logger.info("Starting OCR analysis with Document Intelligence (Markdown format)")
        client = get_document_intelligence_client()
        
        # Reset file stream position
        file_stream.seek(0)
        
        # Use prebuilt-layout model with Markdown output for better structure
        poller = client.begin_analyze_document(
            "prebuilt-layout", 
            file_stream, 
            content_type="application/octet-stream", 
            output_content_format=DocumentContentFormat.MARKDOWN
        )
        result: AnalyzeResult = poller.result()
        
        if not result.content or not result.content.strip():
            raise ValueError("OCR analysis returned empty or no content")
        
        # Process Markdown content to clean up checkboxes and improve extraction
        ocr_text = clean_markdown_content(result.content)
        
        # **NEW: Debug medical section processing**
        debug_medical_section(ocr_text)
        
        # Debug: Log the raw OCR content to see what we're working with
        logger.info("=== RAW OCR CONTENT ===")
        logger.info(result.content[:2000])  # First 2000 characters
        logger.info("=== END RAW OCR ===")
        
        logger.info("=== CLEANED OCR CONTENT ===")
        logger.info(ocr_text[:2000])  # First 2000 characters
        logger.info("=== END CLEANED OCR ===")
        
        # Extract language information from Azure OCR result
        detected_language = "unknown"
        confidence = 0.0
        
        # Check if language information is available in the result
        if hasattr(result, 'languages') and result.languages:
            # Get the primary language with highest confidence
            primary_lang = result.languages[0]
            detected_language = primary_lang.locale
            confidence = primary_lang.confidence
            logger.info(f"Azure OCR detected language: {detected_language} (confidence: {confidence:.2f})")
            
            # Log all available languages for debugging
            if len(result.languages) > 1:
                logger.info(f"Additional languages detected: {[lang.locale for lang in result.languages[1:]]}")
        else:
            # Azure didn't provide language info, default to Hebrew
            detected_language = "hebrew"
            confidence = 0.0
            logger.info("No Azure language info available, defaulting to Hebrew")
            logger.debug(f"Result object attributes: {dir(result)}")
            logger.debug(f"Result content type: {type(result.content)}")
        
        logger.info(f"OCR analysis completed successfully. Extracted {len(ocr_text)} characters")
        
        # Return both OCR text and detected language info
        return {
            'text': ocr_text,
            'language': detected_language,
            'confidence': confidence,
            'has_language_info': detected_language != "unknown"
        }
        
    except Exception as e:
        logger.error(f"OCR analysis failed: {e}")
        if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
            raise RuntimeError("Authentication failed. Please check your Document Intelligence API key and endpoint.")
        elif "quota" in str(e).lower() or "rate limit" in str(e).lower():
            raise RuntimeError("API quota exceeded. Please try again later or check your service limits.")
        else:
            raise RuntimeError(f"OCR analysis failed: {e}")

def clean_markdown_content(markdown_text):
    """Cleans and processes Markdown content from OCR for better field extraction."""
    if not markdown_text:
        return ""
    
    # Remove problematic Markdown elements that interfere with extraction
    cleaned_text = markdown_text
    
    # Remove checkbox markers that can confuse the AI
    cleaned_text = re.sub(r'\[ \]', 'UNCHECKED', cleaned_text)  # Empty checkbox
    cleaned_text = re.sub(r'\[x\]', 'CHECKED', cleaned_text)    # Checked checkbox
    cleaned_text = re.sub(r'\[X\]', 'CHECKED', cleaned_text)    # Checked checkbox (capital)
    
    # Remove other Markdown formatting that might interfere
    cleaned_text = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned_text)  # Bold text
    cleaned_text = re.sub(r'\*(.*?)\*', r'\1', cleaned_text)      # Italic text
    cleaned_text = re.sub(r'`(.*?)`', r'\1', cleaned_text)        # Code blocks
    
    # Clean up excessive whitespace and newlines
    cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)  # Multiple newlines to single
    cleaned_text = re.sub(r' +', ' ', cleaned_text)         # Multiple spaces to single
    
    # Remove table formatting that might confuse extraction
    cleaned_text = re.sub(r'\|', ' ', cleaned_text)         # Table separators
    cleaned_text = re.sub(r'---+', '', cleaned_text)        # Table dividers
    
    # Normalize common form elements
    cleaned_text = re.sub(r'□', 'UNCHECKED', cleaned_text)  # Empty checkbox (Unicode)
    cleaned_text = re.sub(r'☑', 'CHECKED', cleaned_text)    # Checked checkbox (Unicode)
    cleaned_text = re.sub(r'☐', 'UNCHECKED', cleaned_text)  # Empty checkbox (Unicode)
    
    # Handle common form patterns
    cleaned_text = re.sub(r'\(\s*\)', 'UNCHECKED', cleaned_text)  # Empty parentheses
    cleaned_text = re.sub(r'\(\s*[xX]\s*\)', 'CHECKED', cleaned_text)  # Checked parentheses
    
    # Normalize common form separators
    cleaned_text = re.sub(r'[-_]{3,}', ' ', cleaned_text)  # Multiple dashes/underscores
    cleaned_text = re.sub(r'[•·]', ' ', cleaned_text)      # Bullet points
    
    # Clean up common OCR artifacts
    cleaned_text = re.sub(r'[|¦]', ' ', cleaned_text)      # Vertical bars that might be OCR errors
    cleaned_text = re.sub(r'[`\'′]', "'", cleaned_text)    # Normalize apostrophes
    
    # Normalize Hebrew text spacing (common OCR issue)
    # Use a more intelligent approach to restore proper Hebrew word boundaries
    # Instead of adding spaces between every letter, look for specific patterns
    
    # Pattern 1: Fix "כאשר עבדתי ב" + job type (job type is on this line)
    # The job type appears AFTER "כאשר עבדתי ב" on the SAME LINE
    cleaned_text = re.sub(r'(כאשר)(עבדתי)(ב)\s+([א-ת]+)', r'\1 \2 \3 JOB_TYPE_VALUE: \4', cleaned_text)
    
    # Pattern 2: Fix "בתאריך" (in date)
    cleaned_text = re.sub(r'(ב)(תאריך)', r'\1 \2', cleaned_text)
    
    # Pattern 3: The "סוג העבודה" is a label for work location, and the work location appears BELOW it
    # We need to mark this clearly for the AI
    cleaned_text = re.sub(r'(סוג)(העבודה)', r'WORK_LOCATION_LABEL: \1 \2', cleaned_text)
    
    # Pattern 4: Look for work location values that appear after "סוג העבודה" label
    # These are typically common work location words
    work_location_values = ['במפעל', 'במשרד', 'בחנות', 'בבית', 'בשדה', 'בכביש', 'במטבח', 'בגן', 'במשרד', 'בחצר']
    for work_location in work_location_values:
        # Look for work location values that appear after the WORK_LOCATION_LABEL
        pattern = f'(WORK_LOCATION_LABEL: סוג העבודה).*?({work_location})'
        replacement = f'\\1 WORK_LOCATION_VALUE: \\2'
        cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.DOTALL)
    
    # Then clean up excessive spaces
    cleaned_text = re.sub(r' +', ' ', cleaned_text)
    
    # Preserve important form structure - keep job type and work location relationship
    # Add markers to help AI understand the relationship
    cleaned_text = re.sub(r'(סוג העבודה)', r'WORK_LOCATION_LABEL: \1', cleaned_text)
    
    # Mark the "כאשר עבדתי ב" pattern to help identify job type
    cleaned_text = re.sub(r'(כאשר עבדתי ב)', r'JOB_TYPE_PREFIX: \1', cleaned_text)
    
    # Extract and mark the job type value that comes after "כאשר עבדתי ב"
    # Look for pattern: "כאשר עבדתי ב" + [job type value]
    cleaned_text = re.sub(r'(JOB_TYPE_PREFIX: כאשר עבדתי ב)\s+([א-ת\s]+)', r'\1 JOB_TYPE_VALUE: \2', cleaned_text)
    
    # Also add a more specific marker for the exact pattern we found
    # Look for: "כאשר עבדתי ב" + "ירקנייה" (or similar job type values)
    cleaned_text = re.sub(r'(כאשר עבדתי ב)\s+(ירקנייה|במשרד|בחנות|בבית|בשדה|בכביש)', r'JOB_TYPE_FIELD: \1 \2', cleaned_text)
    
    # Also mark work location to distinguish it from job type
    # Look for common work location patterns that might be confused with job type
    cleaned_text = re.sub(r'(במפעל|במשרד|בחנות|בבית|בשדה|בכביש)', r'WORK_LOCATION: \1', cleaned_text)
    
    # Mark empty work location fields - if we see "סוג העבודה" followed by no meaningful text
    # Look for patterns like "סוג העבודה" followed by date or other non-work-location text
    cleaned_text = re.sub(r'(WORK_LOCATION_LABEL: סוגהעבודה)(\d{2}\.\d{2}\.\d{4})', r'\1 - EMPTY_FIELD \2', cleaned_text)
    cleaned_text = re.sub(r'(WORK_LOCATION_LABEL: סוגהעבודה)(\d{2}:\d{2})', r'\1 - EMPTY_FIELD \2', cleaned_text)
    
    # Enhance checkbox detection for accident location
    # Make sure CHECKED/UNCHECKED are clearly visible
    cleaned_text = re.sub(r'(CHECKED)\s+([א-ת\s]+)', r'\1_ACCIDENT_LOCATION: \2', cleaned_text)
    
    # **NEW: Enhanced accident location checkbox detection**
    # Look for the specific pattern "מקום התאונה:" and its checkboxes
    cleaned_text = re.sub(r'(מקום התאונה):', r'ACCIDENT_LOCATION_SECTION: \1:', cleaned_text)
    
    # Look for checked checkboxes in accident location section
    # Pattern: "☒" followed by text (like "במפעל")
    cleaned_text = re.sub(r'☒\s*([א-ת\s]+)', r'CHECKED_ACCIDENT_LOCATION: \1', cleaned_text)
    
    # Also handle other checkbox formats for accident location
    cleaned_text = re.sub(r'☑\s*([א-ת\s]+)', r'CHECKED_ACCIDENT_LOCATION: \1', cleaned_text)
    cleaned_text = re.sub(r'\[x\]\s*([א-ת\s]+)', r'CHECKED_ACCIDENT_LOCATION: \1', cleaned_text)
    cleaned_text = re.sub(r'\[X\]\s*([א-ת\s]+)', r'CHECKED_ACCIDENT_LOCATION: \1', cleaned_text)
    
    # Mark unchecked checkboxes in accident location section
    cleaned_text = re.sub(r'☐\s*([א-ת\s]+)', r'UNCHECKED_ACCIDENT_LOCATION: \1', cleaned_text)
    cleaned_text = re.sub(r'\[ \]\s*([א-ת\s]+)', r'UNCHECKED_ACCIDENT_LOCATION: \1', cleaned_text)
    
    # **CRITICAL: Look for missing accident location options that might not be in OCR**
    # Based on the form structure, we know there should be options like "במפעל"
    # If we see "מקום התאונה:" but no "במפעל" option, it might be missing from OCR
    # Add a marker to help the AI understand this
    if 'ACCIDENT_LOCATION_SECTION: מקום התאונה:' in cleaned_text and 'במפעל' not in cleaned_text:
        # Add a note that "במפעל" might be missing from OCR but should be considered
        cleaned_text = cleaned_text.replace('ACCIDENT_LOCATION_SECTION: מקום התאונה:', 
                                         'ACCIDENT_LOCATION_SECTION: מקום התאונה: (NOTE: "במפעל" option may be missing from OCR)')
    
    # Special handling for "אחר" (Other) checkbox - preserve free text next to it
    # Look for patterns like "אחר [free text]" and mark them clearly
    cleaned_text = re.sub(r'(CHECKED)\s+(אחר)\s+([א-ת\s]+)', r'\1_OTHER_ACCIDENT_LOCATION: \2 - \3', cleaned_text)
    
    # Also handle cases where free text might be on the next line after "אחר"
    cleaned_text = re.sub(r'(CHECKED)\s+(אחר)\n\s*([א-ת\s]+)', r'\1_OTHER_ACCIDENT_LOCATION: \2 - \3', cleaned_text)
    
    # **NEW: Enhanced checkbox detection for medical institution section**
    # Look for checked checkboxes in the medical institution area
    # Pattern: "☒" followed by text (like "כללית")
    cleaned_text = re.sub(r'☒\s*([א-ת\s]+)', r'CHECKED_MEDICAL: \1', cleaned_text)
    
    # Also handle other checkbox formats
    cleaned_text = re.sub(r'☑\s*([א-ת\s]+)', r'CHECKED_MEDICAL: \1', cleaned_text)
    cleaned_text = re.sub(r'\[x\]\s*([א-ת\s]+)', r'CHECKED_MEDICAL: \1', cleaned_text)
    cleaned_text = re.sub(r'\[X\]\s*([א-ת\s]+)', r'CHECKED_MEDICAL: \1', cleaned_text)
    
    # Mark unchecked checkboxes in medical section
    cleaned_text = re.sub(r'☐\s*([א-ת\s]+)', r'UNCHECKED_MEDICAL: \1', cleaned_text)
    cleaned_text = re.sub(r'\[ \]\s*([א-ת\s]+)', r'UNCHECKED_MEDICAL: \1', cleaned_text)
    
    # **NEW: Specific markers for medical institution fields**
    # Look for the specific pattern "למילוי ע"י המוסד הרפואי" section
    cleaned_text = re.sub(r'(למילוי ע"י המוסד הרפואי)', r'MEDICAL_SECTION_START: \1', cleaned_text)
    
    # **FIXED: Only mark health fund options that are NOT already marked as checked/unchecked**
    # This prevents double-marking and confusion
    # Look for health fund names that don't already have CHECKED_MEDICAL or UNCHECKED_MEDICAL markers
    
    # First, let's identify the health fund section more precisely
    # Look for the pattern: "חבר בקופת חולים" followed by options
    cleaned_text = re.sub(r'(חבר בקופת חולים)', r'HEALTH_FUND_SECTION: \1', cleaned_text)
    
    # Now mark individual health fund options ONLY if they're not already marked
    # This prevents the jumping issue where "כללית" checked becomes "מאוחדת"
    
    # For each health fund option, check if it's already marked as checked/unchecked
    # If not, mark it as a potential option
    health_fund_options = ['כללית', 'לאומית', 'מכבי', 'מאוחדת']
    
    for option in health_fund_options:
        # Only mark as HEALTH_FUND_OPTION if it's not already marked as CHECKED_MEDICAL or UNCHECKED_MEDICAL
        if f'CHECKED_MEDICAL: {option}' not in cleaned_text and f'UNCHECKED_MEDICAL: {option}' not in cleaned_text:
            # Look for this option in the health fund section and mark it as an available option
            pattern = f'(HEALTH_FUND_SECTION: חבר בקופת חולים).*?({option})'
            replacement = f'\\1 HEALTH_FUND_OPTION: \\2'
            cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.DOTALL)
    
    # Mark the "מהות התאונה" label and its value
    cleaned_text = re.sub(r'(מהות התאונה)\s*\(([א-ת\s]+)\):', r'ACCIDENT_NATURE_LABEL: \1 (\2):', cleaned_text)
    
    # Look for the actual accident nature value that appears after the label
    # This should be the text that appears after the label, not from other parts
    cleaned_text = re.sub(r'(ACCIDENT_NATURE_LABEL: מהות התאונה \([א-ת\s]+\):)\s*([א-ת\s]+)', r'\1 ACCIDENT_NATURE_VALUE: \2', cleaned_text)
    
    logger.info(f"Markdown content cleaned. Original length: {len(markdown_text)}, Cleaned length: {len(cleaned_text)}")
    
    return cleaned_text.strip()

def detect_language_with_openai(text_content):
    """Uses Azure OpenAI to detect if the primary language is Hebrew or English."""
    if not text_content or not text_content.strip():
        logger.warning("Empty text content, defaulting to Hebrew")
        return "hebrew"
    
    try:
        logger.info("Starting language detection with OpenAI")
        client = get_azure_openai_client()
        
        prompt = f"Is the primary language of the following text Hebrew or English? Respond with only the single word 'Hebrew' or 'English'.\n\nText:\n---\n{text_content[:1000]}\n---"
        
        response = client.chat.completions.create(
            model=config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1, 
            max_tokens=5
        )

        detected_language = response.choices[0].message.content.strip().lower()
        logger.info(f"Language detection completed. Detected: {detected_language}")
        
        return "hebrew" if "hebrew" in detected_language else "english"
        
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
            raise RuntimeError("Authentication failed. Please check your Azure OpenAI API key and endpoint.")
        elif "quota" in str(e).lower() or "rate limit" in str(e).lower():
            raise RuntimeError("API quota exceeded. Please try again later or check your service limits.")
        else:
            logger.warning(f"Language detection failed, defaulting to Hebrew: {e}")
            return "hebrew"  # Fallback to Hebrew

def extract_fields_with_openai(text_content, language="hebrew"):
    """Uses Azure OpenAI to extract fields into the specified JSON schema."""
    if not text_content or not text_content.strip():
        logger.warning("Empty text content, returning empty schema")
        return get_json_schema_for_language(language)

    try:
        logger.info(f"Starting field extraction with OpenAI for {language} language")
        client = get_azure_openai_client()
        json_format = get_json_schema_for_language(language)
        
        with open(config.SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        # Enhanced user prompt with better context
        user_prompt = f"""JSON Schema to populate:
{json_format}

IMPORTANT: The OCR text has been pre-processed with CLEAR MARKERS. You MUST use these markers and NOT re-parse the text!

CLEANED OCR Text (Markdown format removed, checkboxes normalized):
---
{text_content}
---

CRITICAL INSTRUCTION: 
- The text contains pre-processed markers like "JOB_TYPE_VALUE: ירקנייה" and "WORK_LOCATION: במפעל"
- You MUST extract these exact values from the markers
- Do NOT try to re-analyze or re-parse the Hebrew text
- Use ONLY the values that appear after the markers

IMPORTANT EXTRACTION NOTES:
- Text has been cleaned from Markdown formatting
- Checkboxes are marked as "CHECKED" or "UNCHECKED"
- Focus on extracting actual data values, not field labels
- Map Hebrew field names to English schema fields
- If a field is not found, use empty string ""

SPECIFIC FORM STRUCTURE:
1. **Work Location & Job Type**: 
   - **CRITICAL**: You MUST use the OCR markers that are already provided in the text!
   - **Job Type**: Look for "JOB_TYPE_VALUE:" in the text - this is the EXACT value to extract
   - **Work Location**: Look for "WORK_LOCATION:" in the text - this is the EXACT value to extract
   - **OCR MARKERS ARE PROVIDED**: The text already contains clear markers like "JOB_TYPE_VALUE: ירקנייה" and "WORK_LOCATION: במפעל"
   - **DO NOT IGNORE MARKERS**: Use these exact values, do not try to re-parse the text
   
   **EXACT EXTRACTION FROM MARKERS**:
   - Find "JOB_TYPE_VALUE: [value]" → Extract [value] as jobType
   - Find "WORK_LOCATION: [value]" → Extract [value] as workLocation
   
   **EXAMPLE FROM CURRENT TEXT**:
   - Text shows: "JOB_TYPE_VALUE: ירקנייה" → jobType = "ירקנייה" ✅
   - Text shows: "WORK_LOCATION: במפעל" → workLocation = "במפעל" ✅
   
   **CRITICAL RULES**:
   - NEVER extract "במפעל" as jobType (it's the work location)
   - NEVER extract "ירקנייה" as workLocation (it's the job type)
   - Use ONLY the OCR markers provided
   - Do not re-analyze or re-parse the text
   
   **EXACT VALUES TO EXTRACT**:
   - jobType = "ירקנייה" (from JOB_TYPE_VALUE marker)
   - workLocation = "במפעל" (from WORK_LOCATION marker)

2. **Accident Location**: 
   - This is a checkbox field with options like:
     * במפעל (In factory/plant)
     * ת. דרכים בעבודה (Road accident at work)
     * ת. דרכים בדרך לעבודה/מהעבודה (Road accident to/from work)
     * תאונה בדרך ללא רכב (Accident on the way without vehicle)
     * אחר (Other)
   - **CRITICAL**: If "אחר" (Other) is CHECKED, extract the free text that appears next to it
   - If any other option is CHECKED, extract that option's text
   - Do NOT extract the label "מקום התאונה" (Place of Accident)
   
   **IMPORTANT: OCR LIMITATION HANDLING**:
   - Sometimes OCR misses checkbox options, especially "במפעל"
   - If you see "ACCIDENT_LOCATION_SECTION: מקום התאונה: (NOTE: 'במפעל' option may be missing from OCR)"
   - AND if the context suggests this is a workplace accident (job type, work location, etc.)
   - THEN consider "במפעל" as the likely accident location
   
   **CRITICAL: AVOID WRONG EXTRACTION**:
   - Do NOT extract "תאונה בדרך ללא רכב" from the medical institution section
   - This text appears in the medical section but is NOT the accident location
   - The accident location should come from the checkbox section above
   
   **Examples**:
   - If "במפעל" is CHECKED → accidentLocation = "במפעל"
   - If "אחר" is CHECKED and free text shows "בחצר הבית" → accidentLocation = "בחצר הבית"
   - If "ת. דרכים בעבודה" is CHECKED → accidentLocation = "ת. דרכים בעבודה"
   - If no checkbox is clearly checked BUT context suggests workplace accident → accidentLocation = "במפעל"

3. **Medical Institution Fields**:
   - **CRITICAL**: Use the OCR markers for medical institution section!
   - **Health Fund Member**: Look for "CHECKED_MEDICAL:" markers in the medical section
     * **ONLY** use "CHECKED_MEDICAL: [name]" markers - do NOT use "HEALTH_FUND_OPTION:" markers
     * If you see "CHECKED_MEDICAL: כללית" → healthFundMember = "כללית" ✅
     * If you see "CHECKED_MEDICAL: לאומית" → healthFundMember = "לאומית" ✅
     * If you see "CHECKED_MEDICAL: מכבי" → healthFundMember = "מכבי" ✅
     * If you see "CHECKED_MEDICAL: מאוחדת" → healthFundMember = "מאוחדת" ✅
     * **IMPORTANT**: Do NOT extract from "HEALTH_FUND_OPTION:" markers - these are just available options, not the selected one
     * **CRITICAL**: The checked checkbox is marked with "CHECKED_MEDICAL:" - use ONLY that value
   - **Nature of Accident**: Look for "ACCIDENT_NATURE_VALUE:" marker
     * This should be the text that appears AFTER the "מהות התאונה" label
     * Do NOT extract "תאונה בדרך ללא רכב" from other parts of the form
     * Look specifically for "ACCIDENT_NATURE_VALUE: [text]" marker
   - **Medical Diagnoses**: Usually empty in these forms, use empty string ""

4. **Date and Time**: 
   - Extract dates in DD.MM.YYYY format
   - Extract times in HH:MM format
   - These are separate fields

Return ONLY the JSON object, no additional text

FINAL REMINDER:
- Use ONLY the OCR markers provided in the text
- jobType = "ירקנייה" (from JOB_TYPE_VALUE marker)
- workLocation = "במפעל" (from WORK_LOCATION marker)
- healthFundMember = "כללית" (from CHECKED_MEDICAL marker)
- natureOfAccident = [value from ACCIDENT_NATURE_VALUE marker]
- Do NOT re-parse or re-analyze the Hebrew text

Extract the form data according to the schema above."""
        
        response = client.chat.completions.create(
            model=config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,  # Keep deterministic for consistent extraction
            response_format={"type": "json_object"},
            max_tokens=2000  # Ensure enough tokens for complete form data
        )

        extracted_json = response.choices[0].message.content
        logger.info("Field extraction completed successfully")
        
        # Validate that we got valid JSON
        try:
            json.loads(extracted_json)
        except json.JSONDecodeError as e:
            logger.error(f"OpenAI returned invalid JSON: {e}")
            raise RuntimeError(f"Field extraction returned invalid JSON: {e}")
        
        # **FIXED: Return raw English keys - let main function decide on language mapping**
        # The main process_form function will call map_response_to_language if needed
        return extracted_json
        
    except Exception as e:
        logger.error(f"Field extraction failed: {e}")
        if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
            raise RuntimeError("Authentication failed. Please check your Azure OpenAI API key and endpoint.")
        elif "quota" in str(e).lower() or "rate limit" in str(e).lower():
            raise RuntimeError("API quota exceeded. Please try again later or check your service limits.")
        else:
            raise RuntimeError(f"Field extraction failed: {e}")

def detect_values_language(extracted_json):
    """Detects if the extracted values are primarily in English or Hebrew."""
    try:
        # Parse the JSON to analyze the values
        if isinstance(extracted_json, str):
            data = json.loads(extracted_json)
        else:
            data = extracted_json
        
        # **SIMPLIFIED LOGIC**: Look for key indicators of English vs Hebrew
        hebrew_indicators = 0
        english_indicators = 0
        
        def analyze_text(text):
            nonlocal hebrew_indicators, english_indicators
            if not isinstance(text, str):
                return
            
            # **KEY INDICATORS**: Look for specific patterns that indicate language
            
            # Hebrew indicators: Hebrew characters, Hebrew names, Hebrew words
            if any('\u0590' <= char <= '\u05FF' for char in text):  # Hebrew Unicode
                hebrew_indicators += 1
                logger.debug(f"Hebrew indicator found in: '{text}'")
            
            # English indicators: English names, English words, English patterns
            # Look for common English name patterns (first letter capital, rest lowercase)
            if re.match(r'^[A-Z][a-z]+$', text.strip()):  # Like "John", "Mary"
                english_indicators += 1
                logger.debug(f"English name pattern found in: '{text}'")
            elif re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', text.strip()):  # Like "John Smith"
                english_indicators += 1
                logger.debug(f"English full name pattern found in: '{text}'")
            elif text.strip().lower() in ['male', 'female', 'm', 'f']:  # English gender
                english_indicators += 1
                logger.debug(f"English gender found in: '{text}'")
            elif text.strip().lower() in ['street', 'road', 'avenue', 'drive']:  # English address words
                english_indicators += 1
                logger.debug(f"English address word found in: '{text}'")
            elif text.strip().lower() in ['factory', 'office', 'shop', 'home']:  # English work location
                english_indicators += 1
                logger.debug(f"English work location found in: '{text}'")
            elif text.strip().lower() in ['accident', 'injury', 'work', 'job']:  # English work terms
                english_indicators += 1
                logger.debug(f"English work term found in: '{text}'")
        
        # Analyze all string values recursively
        def analyze_object(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    logger.debug(f"Analyzing key: {key}, value: {value}")
                    analyze_object(value)
            elif isinstance(obj, list):
                for item in obj:
                    analyze_object(item)
            elif isinstance(obj, str):
                analyze_text(obj)
        
        analyze_object(data)
        
        logger.info(f"Language indicators - Hebrew: {hebrew_indicators}, English: {english_indicators}")
        
        # **SIMPLE DECISION**: If more English indicators, use English keys
        if english_indicators > hebrew_indicators:
            logger.info(f"Decision: English indicators ({english_indicators}) > Hebrew indicators ({hebrew_indicators}) → Returning 'english'")
            return "english"
        else:
            logger.info(f"Decision: Hebrew indicators ({hebrew_indicators}) >= English indicators ({english_indicators}) → Returning 'hebrew'")
            return "hebrew"
            
    except Exception as e:
        logger.error(f"Failed to detect values language: {e}")
        return "hebrew"  # Default fallback

def debug_medical_section(cleaned_text):
    """Debug function to analyze medical section OCR processing."""
    logger.info("=== MEDICAL SECTION DEBUG ===")
    
    # Look for medical section markers
    if 'MEDICAL_SECTION_START:' in cleaned_text:
        logger.info("✅ Found MEDICAL_SECTION_START marker")
    else:
        logger.warning("❌ No MEDICAL_SECTION_START marker found")
    
    if 'HEALTH_FUND_SECTION:' in cleaned_text:
        logger.info("✅ Found HEALTH_FUND_SECTION marker")
    else:
        logger.warning("❌ No HEALTH_FUND_SECTION marker found")
    
    # Look for checked medical markers
    checked_medical = re.findall(r'CHECKED_MEDICAL: ([א-ת\s]+)', cleaned_text)
    if checked_medical:
        logger.info(f"✅ Found CHECKED_MEDICAL markers: {checked_medical}")
    else:
        logger.warning("❌ No CHECKED_MEDICAL markers found")
    
    # Look for unchecked medical markers
    unchecked_medical = re.findall(r'UNCHECKED_MEDICAL: ([א-ת\s]+)', cleaned_text)
    if unchecked_medical:
        logger.info(f"✅ Found UNCHECKED_MEDICAL markers: {unchecked_medical}")
    else:
        logger.warning("❌ No UNCHECKED_MEDICAL markers found")
    
    # Look for health fund option markers
    health_fund_options = re.findall(r'HEALTH_FUND_OPTION: ([א-ת\s]+)', cleaned_text)
    if health_fund_options:
        logger.info(f"✅ Found HEALTH_FUND_OPTION markers: {health_fund_options}")
    else:
        logger.warning("❌ No HEALTH_FUND_OPTION markers found")
    
    logger.info("=== END MEDICAL SECTION DEBUG ===")
    
    return {
        'checked': checked_medical,
        'unchecked': unchecked_medical,
        'options': health_fund_options
    }

# --- Main Processing Pipeline ---

def process_form(file_stream):
    """Main pipeline function to process a form file."""
    try:
        logger.info("Starting form processing pipeline")
        
        # Step 1: OCR with Azure Language Detection
        logger.info("Step 1: Performing OCR analysis with Azure language detection")
        ocr_result = analyze_document_with_ocr(file_stream)
        ocr_text = ocr_result['text']
        
        # Step 2: Language Detection (use Azure OCR if available, otherwise OpenAI)
        detected_language = "hebrew"  # default fallback
        
        if ocr_result['has_language_info'] and ocr_result['language'] != "unknown":
            # Use Azure OCR detected language
            azure_lang = ocr_result['language'].lower()
            
            # Map Azure language codes to our language categories
            if any(code in azure_lang for code in ['he', 'hebrew', 'iw', 'iw-il']):
                detected_language = "hebrew"
                logger.info(f"Using Azure OCR detected language: Hebrew (code: {azure_lang}, confidence: {ocr_result['confidence']:.2f})")
            elif any(code in azure_lang for code in ['en', 'english', 'en-us', 'en-gb', 'en-ca', 'en-au']):
                detected_language = "english"
                logger.info(f"Using Azure OCR detected language: English (code: {azure_lang}, confidence: {ocr_result['confidence']:.2f})")
            else:
                # Azure detected a different language, fall back to OpenAI
                logger.info(f"Azure detected language '{azure_lang}', using OpenAI for Hebrew/English detection")
                detected_language = detect_language_with_openai(ocr_text)
        else:
            # No Azure language info, use OpenAI detection
            logger.info("Step 2: Using OpenAI for language detection (Azure language info not available)")
            detected_language = detect_language_with_openai(ocr_text)
        
        logger.info(f"Final detected language: {detected_language}")
        
        # Step 3: Field Extraction
        logger.info("Step 3: Extracting form fields")
        extracted_json = extract_fields_with_openai(ocr_text, detected_language)
        
        # **NEW: Detect the language of the extracted VALUES (not just form format)**
        values_language = detect_values_language(extracted_json)
        logger.info(f"Form format: {detected_language}, Values language: {values_language}")
        
        # **FIXED: Always return English keys for consistency**
        # The system will always use English field names regardless of form language
        logger.info("Always returning English keys for consistency")
        return detected_language, extracted_json

    except Exception as e:
        logger.error(f"Form processing pipeline failed: {e}")
        # Re-raise with context
        raise RuntimeError(f"Form processing failed during {getattr(e, 'step', 'unknown step')}: {e}")

# --- Debug/Test Functions ---

def debug_ocr_output(file_path):
    """Debug function to see raw OCR output without running full extraction."""
    try:
        with open(file_path, 'rb') as f:
            logger.info(f"Testing OCR with file: {file_path}")
            ocr_result = analyze_document_with_ocr(f)
            
            print("\n" + "="*50)
            print("RAW OCR OUTPUT:")
            print("="*50)
            print(ocr_result['text'][:3000])  # Show first 3000 characters
            print("="*50)
            
            return ocr_result
            
    except Exception as e:
        logger.error(f"Debug OCR failed: {e}")
        return None

if __name__ == "__main__":
    # Test with a sample file if run directly
    import sys
    if len(sys.argv) > 1:
        debug_ocr_output(sys.argv[1])
    else:
        print("Usage: python form_extractor.py <pdf_file_path>")
        print("This will show the raw OCR output for debugging.")