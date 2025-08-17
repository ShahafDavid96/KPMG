# validator.py
import json
import re
from pydantic import ValidationError
import config
from typing import Dict, List, Any, Tuple

# --- Enhanced Validation Result Structure ---

class ValidationRule:
    """Represents a specific validation rule with detailed checking"""
    
    def __init__(self, name: str, description: str, check_function, field_path: str = None):
        self.name = name
        self.description = description
        self.check_function = check_function
        self.field_path = field_path

class ValidationResult:
    """Detailed validation result for a single rule"""
    
    def __init__(self, rule_name: str, passed: bool, details: str = "", violations: List[str] = None):
        self.rule_name = rule_name
        self.passed = passed
        self.details = details
        self.violations = violations or []

# --- Individual Rule-Based Check Functions with Detailed Results ---

def normalize_phone(phone_number: str) -> str:
    """Normalizes phone numbers to standard format."""
    if not isinstance(phone_number, str):
        return ""
    # Remove all non-digit characters
    return re.sub(r'\D', '', phone_number)

def fix_mobile_phone(phone_number: str) -> str:
    """Fixes mobile phone number to always be 10 digits starting with 05."""
    if not isinstance(phone_number, str):
        return ""
    
    # Remove all non-digit characters
    clean_phone = re.sub(r'\D', '', phone_number)
    
    # If it's 9 digits, add leading 0
    if len(clean_phone) == 9:
        clean_phone = '0' + clean_phone
    
    # If it's 10 digits or more, ensure it starts with 05
    elif len(clean_phone) >= 10:
        # Take the last 8 digits and add '05' at the beginning
        clean_phone = '05' + clean_phone[-8:]
    
    return clean_phone

def fix_landline_phone(phone_number: str) -> str:
    """Fixes landline phone number to always be 9 digits starting with 0."""
    if not isinstance(phone_number, str):
        return ""
    
    # Remove all non-digit characters
    clean_phone = re.sub(r'\D', '', phone_number)
    
    # If it's 8 digits, add leading 0
    if len(clean_phone) == 8:
        clean_phone = '0' + clean_phone
    
    # If it's 9 digits or more, ensure it starts with 0
    elif len(clean_phone) >= 9:
        if not clean_phone.startswith('0'):
            # For 10+ digits, just change the first digit to 0
            if len(clean_phone) == 10:
                # If it's exactly 10 digits, change first digit to 0
                clean_phone = '0' + clean_phone[1:]
            else:
                # For 9 digits, just add 0 at beginning
                clean_phone = '0' + clean_phone[:8]
    
    return clean_phone

def check_id_number_detailed(data: config.FormSchemaEN) -> ValidationResult:
    """Detailed ID number validation with specific rule violations."""
    rule_name = "ID Number Format"
    violations = []
    
    if not data.idNumber:
        return ValidationResult(rule_name, False, "ID number is empty", ["Field is empty"])
    
    # Clean the ID number
    clean_id = re.sub(r'\D', '', data.idNumber)
    
    # Rule 1: Must contain only digits
    if not clean_id.isdigit():
        violations.append("Contains non-digit characters")
    
    # Rule 2: Must be exactly 9 digits
    if len(clean_id) < 9:
        violations.append(f"Too short: {len(clean_id)} digits (required: 9)")
    elif len(clean_id) > 9:
        violations.append(f"Too long: {len(clean_id)} digits (required: 9)")
    
    # Rule 3: Must not be all zeros
    if clean_id == "000000000":
        violations.append("Cannot be all zeros")
    
    passed = len(violations) == 0
    details = f"ID: {data.idNumber} → Cleaned: {clean_id[:9] if len(clean_id) >= 9 else clean_id}"
    
    return ValidationResult(rule_name, passed, details, violations)

def check_mobile_phone_detailed(data: config.FormSchemaEN) -> ValidationResult:
    """Detailed mobile phone validation with specific rule violations."""
    rule_name = "Mobile Phone Format"
    violations = []
    
    if not data.mobilePhone:
        return ValidationResult(rule_name, False, "Mobile phone is empty", ["Field is empty"])
    
    # Clean the phone number
    clean_phone = re.sub(r'\D', '', data.mobilePhone)
    
    # Rule 1: Must contain only digits
    if not clean_phone.isdigit():
        violations.append("Contains non-digit characters")
    
    # Rule 2: Must be at least 9 digits
    if len(clean_phone) < 9:
        violations.append(f"Too short: {len(clean_phone)} digits (minimum: 9)")
    
    # Rule 3: Must start with 05 for 10+ digits
    if len(clean_phone) >= 10:
        if not clean_phone.startswith('05'):
            violations.append(f"Must start with '05' for 10+ digits, found: {clean_phone[:2]}")
    
    # Rule 4: Must be exactly 10 digits when formatted
    fixed_phone = fix_mobile_phone(data.mobilePhone)
    if len(fixed_phone) != 10:
        violations.append(f"Fixed length: {len(fixed_phone)} digits (required: 10)")
    
    passed = len(violations) == 0
    details = f"Phone: {data.mobilePhone} → Fixed: {fixed_phone}"
    
    return ValidationResult(rule_name, passed, details, violations)

def check_landline_phone_detailed(data: config.FormSchemaEN) -> ValidationResult:
    """Detailed landline phone validation with specific rule violations."""
    rule_name = "Landline Phone Format"
    violations = []
    
    if not data.landlinePhone:
        return ValidationResult(rule_name, False, "Landline phone is empty", ["Field is empty"])
    
    # Clean the phone number
    clean_phone = re.sub(r'\D', '', data.landlinePhone)
    
    # Rule 1: Must contain only digits
    if not clean_phone.isdigit():
        violations.append("Contains non-digit characters")
    
    # Rule 2: Must be at least 8 digits
    if len(clean_phone) < 8:
        violations.append(f"Too short: {len(clean_phone)} digits (minimum: 8)")
    
    # Rule 3: Must start with 0 for 9+ digits
    if len(clean_phone) >= 9:
        if not clean_phone.startswith('0'):
            violations.append(f"Must start with '0' for 9+ digits, found: {clean_phone[0]}")
    
    # Rule 4: Must be exactly 9 digits when formatted
    fixed_phone = fix_landline_phone(data.landlinePhone)
    if len(fixed_phone) != 9:
        violations.append(f"Fixed length: {len(fixed_phone)} digits (required: 9)")
    
    passed = len(violations) == 0
    details = f"Phone: {data.landlinePhone} → Fixed: {fixed_phone}"
    
    return ValidationResult(rule_name, passed, details, violations)

def check_postal_code_detailed(data: config.FormSchemaEN) -> ValidationResult:
    """Detailed postal code validation with specific rule violations."""
    rule_name = "Postal Code Format"
    violations = []
    
    if not data.address.postalCode:
        return ValidationResult(rule_name, False, "Postal code is empty", ["Field is empty"])
    
    # Clean the postal code
    clean_postal = re.sub(r'\D', '', data.address.postalCode)
    
    # Rule 1: Must contain only digits
    if not clean_postal.isdigit():
        violations.append("Contains non-digit characters")
    
    # Rule 2: Must be exactly 7 digits
    if len(clean_postal) < 7:
        violations.append(f"Too short: {len(clean_postal)} digits (required: 7)")
    elif len(clean_postal) > 7:
        violations.append(f"Too long: {len(clean_postal)} digits (required: 7)")
    
    # Rule 3: Must not be all zeros
    if clean_postal == "0000000":
        violations.append("Cannot be all zeros")
    
    passed = len(violations) == 0
    details = f"Postal: {data.address.postalCode} → Cleaned: {clean_postal[:7] if len(clean_postal) >= 7 else clean_postal}"
    
    return ValidationResult(rule_name, passed, details, violations)

def check_date_plausibility_detailed(date_obj) -> ValidationResult:
    """Detailed date validation with specific rule violations."""
    rule_name = "Date Plausibility"
    violations = []
    
    if not date_obj or not hasattr(date_obj, 'day') or not hasattr(date_obj, 'month') or not hasattr(date_obj, 'year'):
        return ValidationResult(rule_name, False, "Date object is invalid", ["Invalid date structure"])
    
    day = date_obj.day
    month = date_obj.month
    year = date_obj.year
    
    # Convert to integers for validation
    try:
        day_int = int(day) if day else 0
        month_int = int(month) if month else 0
        year_int = int(year) if year else 0
    except (ValueError, TypeError):
        violations.append("Date components must be valid numbers")
        return ValidationResult(rule_name, False, f"Date: {day}/{month}/{year}", violations)
    
    # Rule 1: Day must be between 1-31
    if not (1 <= day_int <= 31):
        violations.append(f"Invalid day: {day_int} (must be 1-31)")
    
    # Rule 2: Month must be between 1-12
    if not (1 <= month_int <= 12):
        violations.append(f"Invalid month: {month_int} (must be 1-12)")
    
    # Rule 3: Year must be reasonable (1900-2100)
    if not (1900 <= year_int <= 2100):
        violations.append(f"Invalid year: {year_int} (must be 1900-2100)")
    
    # Rule 4: Specific month-day combinations
    if month_int in [4, 6, 9, 11] and day_int > 30:
        violations.append(f"Month {month_int} cannot have day {day_int}")
    elif month_int == 2:
        if day_int > 29:
            violations.append(f"February cannot have day {day_int}")
        elif day_int == 29 and not (year_int % 4 == 0 and (year_int % 100 != 0 or year_int % 400 == 0)):
            violations.append(f"February 29 is invalid for non-leap year {year_int}")
    
    passed = len(violations) == 0
    details = f"Date: {day_int}/{month_int}/{year_int}"
    
    return ValidationResult(rule_name, passed, details, violations)

def check_time_format_detailed(data: config.FormSchemaEN) -> ValidationResult:
    """Detailed time format validation with specific rule violations."""
    rule_name = "Time Format"
    violations = []
    
    if not data.timeOfInjury:
        return ValidationResult(rule_name, False, "Time is empty", ["Field is empty"])
    
    time_str = str(data.timeOfInjury)
    
    # Rule 1: Must match HH:MM format
    if not re.fullmatch(r'\d{1,2}:\d{2}', time_str):
        violations.append("Must be in HH:MM format")
    
    # Rule 2: Hours must be 0-23
    try:
        hours, minutes = map(int, time_str.split(':'))
        if not (0 <= hours <= 23):
            violations.append(f"Invalid hours: {hours} (must be 0-23)")
        if not (0 <= minutes <= 59):
            violations.append(f"Invalid minutes: {minutes} (must be 0-59)")
    except ValueError:
        violations.append("Invalid time format")
    
    passed = len(violations) == 0
    details = f"Time: {time_str}"
    
    return ValidationResult(rule_name, passed, details, violations)

def check_name_format_detailed(data: config.FormSchemaEN) -> ValidationResult:
    """Detailed name validation with specific rule violations."""
    rule_name = "Name Format"
    violations = []
    
    # Check first name
    if not data.firstName:
        violations.append("First name is empty")
    else:
        # Rule 1: Must contain only letters, spaces, and hyphens
        if not re.fullmatch(r'^[A-Za-z\u0590-\u05FF\s\-]+$', data.firstName):
            violations.append("First name contains invalid characters (only letters, spaces, hyphens allowed)")
        
        # Rule 2: Must be at least 2 characters
        if len(data.firstName.strip()) < 2:
            violations.append("First name too short (minimum 2 characters)")
        
        # Rule 3: Must not be all spaces
        if data.firstName.strip() == "":
            violations.append("First name cannot be all spaces")
    
    # Check last name
    if not data.lastName:
        violations.append("Last name is empty")
    else:
        # Rule 1: Must contain only letters, spaces, and hyphens
        if not re.fullmatch(r'^[A-Za-z\u0590-\u05FF\s\-]+$', data.lastName):
            violations.append("Last name contains invalid characters (only letters, spaces, hyphens allowed)")
        
        # Rule 2: Must be at least 2 characters
        if len(data.lastName.strip()) < 2:
            violations.append("Last name too short (minimum 2 characters)")
        
        # Rule 3: Must not be all spaces
        if data.lastName.strip() == "":
            violations.append("Last name cannot be all spaces")
    
    passed = len(violations) == 0
    details = f"Names: {data.firstName} {data.lastName}"
    
    return ValidationResult(rule_name, passed, details, violations)

def check_gender_format_detailed(data: config.FormSchemaEN) -> ValidationResult:
    """Detailed gender validation with specific rule violations."""
    rule_name = "Gender Format"
    violations = []
    
    if not data.gender:
        violations.append("Gender is empty")
    else:
        gender_lower = str(data.gender).lower().strip()
        
        # Rule 1: Must be one of the accepted values
        accepted_values = ['male', 'female', 'm', 'f', 'זכר', 'נקבה', 'ז', 'נ']
        if gender_lower not in accepted_values:
            violations.append(f"Invalid gender value: '{data.gender}' (accepted: male/female/m/f/זכר/נקבה/ז/נ)")
        
        # Rule 2: Must not be empty after cleaning
        if gender_lower == "":
            violations.append("Gender cannot be empty or all spaces")
    
    passed = len(violations) == 0
    details = f"Gender: {data.gender}"
    
    return ValidationResult(rule_name, passed, details, violations)

def check_accident_details_detailed(data: config.FormSchemaEN) -> ValidationResult:
    """Detailed accident details validation with specific rule violations."""
    rule_name = "Accident Details"
    violations = []
    
    # Check accident location
    if hasattr(data, 'accidentLocation') and data.accidentLocation:
        location = str(data.accidentLocation).strip()
        if len(location) < 5:
            violations.append("Accident location too short (minimum 5 characters)")
        elif len(location) > 200:
            violations.append("Accident location too long (maximum 200 characters)")
    
    # Check accident description
    if hasattr(data, 'accidentDescription') and data.accidentDescription:
        description = str(data.accidentDescription).strip()
        if len(description) < 10:
            violations.append("Accident description too short (minimum 10 characters)")
        elif len(description) > 1000:
            violations.append("Accident description too long (maximum 1000 characters)")
    
    # Check injured body part
    if hasattr(data, 'injuredBodyPart') and data.injuredBodyPart:
        body_part = str(data.injuredBodyPart).strip()
        if len(body_part) < 3:
            violations.append("Injured body part too short (minimum 3 characters)")
    
    passed = len(violations) == 0
    details = "Accident details validated"
    
    return ValidationResult(rule_name, passed, details, violations)

# --- Helper Functions ---

def fix_id_number(id_number: str) -> str:
    """Fixes ID number to exactly 9 digits."""
    if not isinstance(id_number, str):
        return ""
    
    # Remove non-digits and take first 9
    clean_id = re.sub(r'\D', '', id_number)
    return clean_id[:9] if len(clean_id) >= 9 else clean_id

def fix_postal_code(postal_code: str) -> str:
    """Fixes postal code to exactly 7 digits."""
    if not isinstance(postal_code, str):
        return ""
    
    # Remove non-digits and take first 7
    clean_postal = re.sub(r'\D', '', postal_code)
    return clean_postal[:7] if len(clean_postal) >= 7 else clean_postal

def fix_time_format(time_str: str) -> str:
    """Fixes time format to HH:MM."""
    if not isinstance(time_str, str):
        return ""
    
    # Extract digits and format as HH:MM
    digits = re.findall(r'\d', time_str)
    if len(digits) >= 4:
        hours = int(digits[0] + digits[1]) if len(digits) > 1 else int(digits[0])
        minutes = int(digits[2] + digits[3]) if len(digits) > 3 else int(digits[2])
        return f"{hours:02d}:{minutes:02d}"
    elif len(digits) >= 2:
        hours = int(digits[0])
        minutes = int(digits[1])
        return f"{hours:02d}:{minutes:02d}"
    
    return time_str

# --- Main Validation Function ---

def validate_extracted_data(json_string: str) -> Dict[str, Any]:
    """
    Validates extracted data and returns detailed results with specific rule violations.
    """
    results = {
        "is_valid_schema": False,
        "completeness_score": 0.0,
        "accuracy_score": 0.0,
        "accuracy_details": {},
        "accuracy_details_detailed": {},  # New: Detailed validation results
        "data_fixes_applied": [],
        "corrected_data": None,
        "validation_errors": []
    }
    
    try:
        # Parse JSON
        data = json.loads(json_string)
        is_hebrew = False  # Always use English schema
        
        # 1. Schema Validation (using Pydantic)
        Model = config.FormSchemaEN  # Always use English schema
        validated_model = Model.model_validate(data)
        results["is_valid_schema"] = True

        # 2. Apply automatic fixes to phone numbers and ID number
        if hasattr(validated_model, 'idNumber') and validated_model.idNumber:
            original_id = validated_model.idNumber
            fixed_id = fix_id_number(original_id)
            if fixed_id != original_id:
                validated_model.idNumber = fixed_id
                # Determine the specific fix type
                if len(re.sub(r'\D', '', original_id)) > 9:
                    fix_type = "Truncated to 9 digits"
                else:
                    fix_type = "Cleaned non-digit characters"
                results["data_fixes_applied"].append({
                    "field": "idNumber",
                    "original": original_id,
                    "fixed": fixed_id,
                    "fix_type": fix_type
                })
        
        if hasattr(validated_model, 'mobilePhone') and validated_model.mobilePhone:
            original_phone = validated_model.mobilePhone
            fixed_phone = fix_mobile_phone(original_phone)
            if fixed_phone != original_phone:
                validated_model.mobilePhone = fixed_phone
                # Determine the specific fix type
                if len(re.sub(r'\D', '', original_phone)) == 9:
                    fix_type = "Added leading 0"
                elif len(re.sub(r'\D', '', original_phone)) >= 10:
                    fix_type = "Ensured starts with 05"
                else:
                    fix_type = "Standardized format"
                results["data_fixes_applied"].append({
                    "field": "mobilePhone",
                    "original": original_phone,
                    "fixed": fixed_phone,
                    "fix_type": fix_type
                })
        
        if hasattr(validated_model, 'landlinePhone') and validated_model.landlinePhone:
            original_phone = validated_model.landlinePhone
            fixed_phone = fix_landline_phone(original_phone)
            if fixed_phone != original_phone:
                validated_model.landlinePhone = fixed_phone
                # Determine the specific fix type
                if len(re.sub(r'\D', '', original_phone)) == 8:
                    fix_type = "Added leading 0"
                elif len(re.sub(r'\D', '', original_phone)) >= 9:
                    fix_type = "Ensured starts with 0"
                else:
                    fix_type = "Standardized format"
                results["data_fixes_applied"].append({
                    "field": "landlinePhone",
                    "original": original_phone,
                    "fixed": fixed_phone,
                    "fix_type": fix_type
                })

        # Fix postal code if needed
        if hasattr(validated_model, 'address') and hasattr(validated_model.address, 'postalCode') and validated_model.address.postalCode:
            original_postal = validated_model.address.postalCode
            fixed_postal = fix_postal_code(original_postal)
            if fixed_postal != original_postal:
                validated_model.address.postalCode = fixed_postal
                # Determine the specific fix type
                if len(re.sub(r'\D', '', original_postal)) > 7:
                    fix_type = "Truncated to 7 digits"
                else:
                    fix_type = "Cleaned non-digit characters"
                results["data_fixes_applied"].append({
                    "field": "postalCode",
                    "original": original_postal,
                    "fixed": fixed_postal,
                    "fix_type": fix_type
                })

        # Fix time of injury if needed
        if hasattr(validated_model, 'timeOfInjury') and validated_model.timeOfInjury:
            original_time = validated_model.timeOfInjury
            fixed_time = fix_time_format(original_time)
            if fixed_time != original_time:
                validated_model.timeOfInjury = fixed_time
                # Determine the specific fix type
                if not re.fullmatch(r'\d{1,2}:\d{2}', original_time):
                    fix_type = "Standardized format"
                else:
                    fix_type = "Cleaned non-digit characters"
                results["data_fixes_applied"].append({
                    "field": "timeOfInjury",
                    "original": original_time,
                    "fixed": fixed_time,
                    "fix_type": fix_type
                })

        # Store the corrected data
        results["corrected_data"] = validated_model.model_dump()

    except ValidationError as e:
        results["validation_errors"] = e.errors()
        return results
    except json.JSONDecodeError:
        results["validation_errors"] = [{"loc": ["JSON"], "msg": "Invalid JSON format."}]
        return results

    # 3. Completeness Score
    flat_data = validated_model.model_dump()
    field_count = 0
    filled_count = 0
    def count_fields(d):
        nonlocal field_count, filled_count
        for value in d.values():
            if isinstance(value, dict):
                count_fields(value)
            else:
                field_count += 1
                if value not in [None, ""]:
                    filled_count += 1
    count_fields(flat_data)
    if field_count > 0:
        results["completeness_score"] = (filled_count / field_count) * 100

    # 4. Enhanced Accuracy Score with Detailed Rule Checking
    accuracy_checks = [
        check_id_number_detailed,
        check_mobile_phone_detailed,
        check_landline_phone_detailed,
        check_postal_code_detailed,
        lambda d: check_date_plausibility_detailed(d.dateOfBirth),
        lambda d: check_date_plausibility_detailed(d.dateOfInjury),
        check_time_format_detailed,
        check_name_format_detailed,
        check_gender_format_detailed,
        check_accident_details_detailed,
    ]
    
    passed_checks = 0
    total_checks = len(accuracy_checks)
    
    for check_func in accuracy_checks:
        try:
            validation_result = check_func(validated_model)
            
            # Store both simple pass/fail and detailed results
            results["accuracy_details"][validation_result.rule_name] = validation_result.passed
            results["accuracy_details_detailed"][validation_result.rule_name] = {
                "passed": validation_result.passed,
                "details": validation_result.details,
                "violations": validation_result.violations
            }
            
            if validation_result.passed:
                passed_checks += 1
                
        except Exception as e:
            # Handle any errors in individual checks
            rule_name = getattr(check_func, '__name__', 'Unknown Rule')
            results["accuracy_details"][rule_name] = False
            results["accuracy_details_detailed"][rule_name] = {
                "passed": False,
                "details": f"Error during validation: {str(e)}",
                "violations": ["Validation error occurred"]
            }
    
    if total_checks > 0:
        results["accuracy_score"] = (passed_checks / total_checks) * 100

    return results