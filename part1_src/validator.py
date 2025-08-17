# validator.py
import json
import re
from pydantic import ValidationError
import config

# --- Individual Rule-Based Check Functions ---

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

def check_id_number(data: config.FormSchemaEN) -> bool:
    """Checks if ID number is exactly 9 digits."""
    if not data.idNumber:
        return False  # Empty ID number should fail validation
    
    # Take only the first 9 digits if there are more
    clean_id = re.sub(r'\D', '', data.idNumber)  # Remove non-digits
    if len(clean_id) > 9:
        clean_id = clean_id[:9]  # Take only first 9 digits
    
    # Check if it's exactly 9 digits
    return bool(re.fullmatch(r'\d{9}', clean_id))

def check_mobile_phone(data: config.FormSchemaEN) -> bool:
    """Checks mobile phone format (10 digits, starts with 05)."""
    if not data.mobilePhone:
        return False  # Empty mobile phone should fail validation
    
    # Fix the phone number first
    fixed_phone = fix_mobile_phone(data.mobilePhone)
    
    # Check if it's valid after fixing - must be 10 digits and start with 05
    return len(fixed_phone) == 10 and fixed_phone.startswith('05')

def check_landline_phone(data: config.FormSchemaEN) -> bool:
    """Checks landline phone format (9 digits, starts with 0)."""
    if not data.landlinePhone:
        return False  # Empty landline phone should fail validation
    
    # Fix the phone number first
    fixed_phone = fix_landline_phone(data.landlinePhone)
    
    # Check if it's valid after fixing - must be 9 digits and start with 0
    return len(fixed_phone) == 9 and fixed_phone.startswith('0')

def check_postal_code(data: config.FormSchemaEN) -> bool:
    """Checks if postal code is a 7-digit number."""
    if not data.address.postalCode:
        return False  # Empty postal code should fail validation
    return bool(re.fullmatch(r'\d{7}', data.address.postalCode))

def check_date_plausibility(date: config.DateModelEN) -> bool:
    """Checks if date fields are within a plausible range."""
    if not date.day or not date.month or not date.year:
        return False  # Incomplete date should fail validation
    try:
        day = int(date.day)
        month = int(date.month)
        year = int(date.year)
        # Basic plausibility checks
        return 1 <= day <= 31 and 1 <= month <= 12 and 1900 < year < 2100
    except (ValueError, TypeError):
        return False

def check_time_format(data: config.FormSchemaEN) -> bool:
    """Checks if time of injury is in HH:MM format."""
    if not data.timeOfInjury:
        return False  # Empty time should fail validation
    return bool(re.fullmatch(r'\d{1,2}:\d{2}', data.timeOfInjury))

def fix_id_number(id_number: str) -> str:
    """Fixes ID number to always be exactly 9 digits."""
    if not isinstance(id_number, str):
        return ""
    
    # Remove all non-digit characters
    clean_id = re.sub(r'\D', '', id_number)
    
    # If it's more than 9 digits, take only the first 9
    if len(clean_id) > 9:
        clean_id = clean_id[:9]
    
    # If it's less than 9 digits, pad with zeros (or return as is for validation)
    elif len(clean_id) < 9:
        # For validation purposes, we'll leave it as is to fail validation
        pass
    
    return clean_id

def fix_postal_code(postal_code: str) -> str:
    """Fixes postal code to always be exactly 7 digits."""
    if not isinstance(postal_code, str):
        return ""
    
    # Remove all non-digit characters
    clean_code = re.sub(r'\D', '', postal_code)
    
    # If it's more than 7 digits, take only the first 7
    if len(clean_code) > 7:
        clean_code = clean_code[:7]
    
    # If it's less than 7 digits, pad with zeros (or return as is for validation)
    elif len(clean_code) < 7:
        # For validation purposes, we'll leave it as is to fail validation
        pass
    
    return clean_code

def fix_time_format(time_str: str) -> str:
    """Fixes time format to HH:MM format."""
    if not isinstance(time_str, str):
        return ""
    
    # Remove all non-digit and non-colon characters
    clean_time = re.sub(r'[^\d:]', '', time_str)
    
    # Try to extract HH:MM pattern
    time_match = re.search(r'(\d{1,2}):(\d{2})', clean_time)
    if time_match:
        hours = int(time_match.group(1))
        minutes = int(time_match.group(2))
        
        # Validate hours and minutes
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            return f"{hours:02d}:{minutes:02d}"
    
    # If no valid pattern found, return original for validation to fail
    return time_str


# --- Main Validation Orchestrator ---

def validate_extracted_data(json_string):
    """
    Validates data for schema compliance, completeness, and rule-based accuracy.
    """
    results = {
        "is_valid_schema": False,
        "completeness_score": 0.0,
        "accuracy_score": 0.0,
        "validation_errors": [],
        "accuracy_details": {},
        "data_fixes_applied": [],  # Track any automatic fixes
        "corrected_data": None,    # Store the corrected data
    }

    try:
        data = json.loads(json_string)
        # **FIXED: Always expect English keys since form_extractor always returns English keys**
        # No need to check for Hebrew keys anymore
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

    # 4. Accuracy Score (Rule-Based Checks)
    # The validated_model now has consistent English field names regardless of source language
    accuracy_checks = {
        "ID Number Format": check_id_number,
        "Mobile Phone Format": check_mobile_phone,
        "Landline Phone Format": check_landline_phone,
        "Postal Code Format": check_postal_code,
        "Birth Date Plausibility": lambda d: check_date_plausibility(d.dateOfBirth),
        "Injury Date Plausibility": lambda d: check_date_plausibility(d.dateOfInjury),
        "Time of Injury Format": check_time_format,
    }
    
    passed_checks = 0
    total_checks = len(accuracy_checks)
    for name, func in accuracy_checks.items():
        is_passed = func(validated_model)
        results["accuracy_details"][name] = is_passed
        if is_passed:
            passed_checks += 1
    
    if total_checks > 0:
        results["accuracy_score"] = (passed_checks / total_checks) * 100

    return results