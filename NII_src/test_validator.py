# test_validator.py
import json
from validator import validate_extracted_data

def test_enhanced_validator():
    """Test the enhanced validation system with detailed rule violations."""
    
    # Test 1: Data with multiple validation issues
    test_data_1 = {
        "lastName": "יוחננוף",
        "firstName": "רועי",
        "idNumber": "12345",  # Too short - should fail
        "gender": "invalid",  # Invalid gender - should fail
        "dateOfBirth": {
            "day": "32",  # Invalid day - should fail
            "month": "13",  # Invalid month - should fail
            "year": "1800"  # Invalid year - should fail
        },
        "address": {
            "street": "המאיר",
            "houseNumber": "15",
            "entrance": "1",
            "apartment": "16",
            "city": "אלוני הבשן",
            "postalCode": "123",  # Too short - should fail
            "poBox": ""
        },
        "landlinePhone": "abc",  # Contains letters - should fail
        "mobilePhone": "123",  # Too short - should fail
        "jobType": "ירקנייה",
        "dateOfInjury": {
            "day": "29",  # February 29 in non-leap year - should fail
            "month": "2",
            "year": "2023"
        },
        "timeOfInjury": "25:70",  # Invalid time - should fail
        "accidentLocation": "A",  # Too short - should fail
        "accidentAddress": "לוונברג 173 כפר סבא",
        "accidentDescription": "Short",  # Too short - should fail
        "injuredBodyPart": "X",  # Too short - should fail
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
    
    print("🧪 Testing Enhanced NII Validator with Detailed Rules")
    print("=" * 80)
    
    # Test the enhanced validation
    result = validate_extracted_data(json.dumps(test_data_1))
    
    print(f"✅ Schema Valid: {result['is_valid_schema']}")
    print(f"📊 Completeness Score: {result['completeness_score']:.1f}%")
    print(f"🎯 Accuracy Score: {result['accuracy_score']:.1f}%")
    
    print("\n📋 Enhanced Validation Results:")
    detailed_results = result.get("accuracy_details_detailed", {})
    
    for rule_name, details in detailed_results.items():
        if details['passed']:
            print(f"✅ {rule_name} - PASSED")
        else:
            print(f"❌ {rule_name} - FAILED")
            violations = details.get("violations", [])
            if violations:
                print("   Violations:")
                for violation in violations:
                    print(f"     • {violation}")
            if details.get("details"):
                print(f"   Details: {details['details']}")
    
    print("\n🔧 Data Fixes Applied:")
    fixes = result.get("data_fixes_applied", [])
    if fixes:
        for fix in fixes:
            print(f"   {fix['field']}: '{fix['original']}' → '{fix['fixed']}' ({fix['fix_type']})")
    else:
        print("   No automatic fixes applied")
    
    print("\n📊 Summary:")
    total_checks = len(detailed_results)
    passed_checks = sum(1 for details in detailed_results.values() if details['passed'])
    failed_checks = total_checks - passed_checks
    
    print(f"   Total Validation Rules: {total_checks}")
    print(f"   Passed: {passed_checks}")
    print(f"   Failed: {failed_checks}")
    print(f"   Success Rate: {(passed_checks/total_checks)*100:.1f}%")
    
    print("=" * 80)

def test_valid_data():
    """Test with valid data to show passing validations."""
    
    valid_data = {
        "lastName": "יוחננוף",
        "firstName": "רועי",
        "idNumber": "123456789",
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
            "postalCode": "4454123",
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
    
    print("\n🧪 Testing Enhanced Validator with Valid Data")
    print("=" * 80)
    
    result = validate_extracted_data(json.dumps(valid_data))
    
    print(f"✅ Schema Valid: {result['is_valid_schema']}")
    print(f"📊 Completeness Score: {result['completeness_score']:.1f}%")
    print(f"🎯 Accuracy Score: {result['accuracy_score']:.1f}%")
    
    print("\n📋 Validation Results (Should All Pass):")
    detailed_results = result.get("accuracy_details_detailed", {})
    
    for rule_name, details in detailed_results.items():
        if details['passed']:
            print(f"✅ {rule_name} - PASSED")
        else:
            print(f"❌ {rule_name} - FAILED")
            violations = details.get("violations", [])
            if violations:
                print("   Violations:")
                for violation in violations:
                    print(f"     • {violation}")
    
    print("=" * 80)

if __name__ == "__main__":
    test_enhanced_validator()
    test_valid_data()
