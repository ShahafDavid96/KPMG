# test_validator.py
import json
from validator import validate_extracted_data

def test_validator_fixes():
    """Test the new validation logic with various data scenarios."""
    
    # Test 1: ID number with more than 9 digits
    test_data_1 = {
        "lastName": "יוחננוף",
        "firstName": "רועי",
        "idNumber": "123456789012345",  # 15 digits - should be truncated to 9
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
            "postalCode": "445412123",  # 9 digits - should be truncated to 7
            "poBox": ""
        },
        "landlinePhone": "8975423541",  # 10 digits - should be fixed to start with 0
        "mobilePhone": "502451645",     # 9 digits - should be fixed to start with 05
        "jobType": "ירקנייה",
        "dateOfInjury": {
            "day": "14",
            "month": "04",
            "year": "1999"
        },
        "timeOfInjury": "15.30",        # Invalid format - should be fixed to 15:30
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
    
    print("Testing Validator with Data Fixes")
    print("=" * 60)
    
    # Test the validation
    result = validate_extracted_data(json.dumps(test_data_1))
    
    print(f"Schema Valid: {result['is_valid_schema']}")
    print(f"Completeness Score: {result['completeness_score']:.1f}%")
    print(f"Accuracy Score: {result['accuracy_score']:.1f}%")
    
    print("\nData Fixes Applied:")
    for fix in result.get("data_fixes_applied", []):
        print(f"  {fix['field']}: '{fix['original']}' → '{fix['fixed']}' ({fix['fix_type']})")
    
    print("\nAccuracy Details:")
    for check_name, is_passed in result.get("accuracy_details", {}).items():
        status = "✅ PASS" if is_passed else "❌ FAIL"
        print(f"  {check_name}: {status}")
    
    print("\nCorrected Data Preview:")
    corrected = result.get("corrected_data", {})
    if corrected:
        print(f"  ID Number: {corrected.get('idNumber', 'N/A')}")
        print(f"  Postal Code: {corrected.get('address', {}).get('postalCode', 'N/A')}")
        print(f"  Landline Phone: {corrected.get('landlinePhone', 'N/A')}")
        print(f"  Mobile Phone: {corrected.get('mobilePhone', 'N/A')}")
        print(f"  Time of Injury: {corrected.get('timeOfInjury', 'N/A')}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_validator_fixes()
