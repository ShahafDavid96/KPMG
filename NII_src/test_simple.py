# test_simple.py
import json
import re

def detect_values_language_simple(extracted_json):
    """Simple version of the language detection logic for testing."""
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
                print(f"Hebrew indicator found in: '{text}'")
            
            # English indicators: English names, English words, English patterns
            # Look for common English name patterns (first letter capital, rest lowercase)
            if re.match(r'^[A-Z][a-z]+$', text.strip()):  # Like "John", "Mary"
                english_indicators += 1
                print(f"English name pattern found in: '{text}'")
            elif re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', text.strip()):  # Like "John Smith"
                english_indicators += 1
                print(f"English full name pattern found in: '{text}'")
            elif text.strip().lower() in ['male', 'female', 'm', 'f']:  # English gender
                english_indicators += 1
                print(f"English gender found in: '{text}'")
            elif text.strip().lower() in ['street', 'road', 'avenue', 'drive']:  # English address words
                english_indicators += 1
                print(f"English address word found in: '{text}'")
            elif text.strip().lower() in ['factory', 'office', 'shop', 'home']:  # English work location
                english_indicators += 1
                print(f"English work location found in: '{text}'")
            elif text.strip().lower() in ['accident', 'injury', 'work', 'job']:  # English work terms
                english_indicators += 1
                print(f"English work term found in: '{text}'")
        
        # Analyze all string values recursively
        def analyze_object(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    print(f"Analyzing key: {key}, value: {value}")
                    analyze_object(value)
            elif isinstance(obj, list):
                for item in obj:
                    analyze_object(item)
            elif isinstance(obj, str):
                analyze_text(obj)
        
        analyze_object(data)
        
        print(f"Language indicators - Hebrew: {hebrew_indicators}, English: {english_indicators}")
        
        # **SIMPLE DECISION**: If more English indicators, use English keys
        if english_indicators > hebrew_indicators:
            print(f"Decision: English indicators ({english_indicators}) > Hebrew indicators ({hebrew_indicators}) → Returning 'english'")
            return "english"
        else:
            print(f"Decision: Hebrew indicators ({hebrew_indicators}) >= English indicators ({english_indicators}) → Returning 'hebrew'")
            return "hebrew"
            
    except Exception as e:
        print(f"Failed to detect values language: {e}")
        return "hebrew"  # Default fallback

def test_ex2_data():
    """Test with the exact data from ex2."""
    
    # This is the exact JSON from ex2 that should be detected as Hebrew
    ex2_data = {
        "lastName": "יוחננוף",
        "firstName": "רועי",
        "idNumber": "",
        "gender": "זכר",
        "dateOfBirth": {
            "day": "03",
            "month": "03",
            "year": "1974"
        },
        "address": {
            "street": "המאיר",
            "houseNumber": "15",
            "entrance": "1",
            "apartment": "16",
            "city": "אלוני הבשן",
            "postalCode": "445412",
            "poBox": ""
        },
        "landlinePhone": "0975423541",
        "mobilePhone": "0502451645",
        "jobType": "ירקנייה",
        "dateOfInjury": {
            "day": "14",
            "month": "04",
            "year": "1999"
        },
        "timeOfInjury": "15:30",
        "accidentLocation": "במפעל",
        "accidentAddress": "לוונברג 173 כפר סבא",
        "accidentDescription": "במהלך העבודה הרמתי משקל כבד וכתוצאה מכך הייתי צריך ניתוח קילה",
        "injuredBodyPart": "קילה",
        "signature": "רועי יוחננוף",
        "formFillingDate": {
            "day": "20",
            "month": "05",
            "year": "1999"
        },
        "formReceiptDateAtClinic": {
            "day": "30",
            "month": "06",
            "year": "1999"
        },
        "medicalInstitutionFields": {
            "healthFundMember": "כללית",
            "natureOfAccident": "",
            "medicalDiagnoses": ""
        }
    }
    
    print("Testing Language Detection with EX2 Data")
    print("=" * 60)
    
    result = detect_values_language_simple(ex2_data)
    
    print("=" * 60)
    print(f"Final Result: {result}")
    print(f"Expected: hebrew")
    print(f"Status: {'✅ PASS' if result == 'hebrew' else '❌ FAIL'}")
    
    if result != 'hebrew':
        print("\n❌ PROBLEM: This should be detected as Hebrew but isn't!")
        print("The system will show English keys instead of Hebrew keys.")
    else:
        print("\n✅ SUCCESS: This will correctly show Hebrew keys!")

if __name__ == "__main__":
    test_ex2_data()
