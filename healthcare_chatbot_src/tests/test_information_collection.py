#!/usr/bin/env python3
"""
Test file for Information Collection Phase functionality
Tests user information extraction and completeness checking
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_information_collection_phase():
    """Test the information collection phase"""
    print("Testing Information Collection Phase")
    print("=" * 60)
    
    try:
        from utils import extract_user_info_from_conversation, is_user_info_complete
        from models import ChatRequest
        
        # Test 1: Empty conversation
        print("\n1. Testing Empty Conversation...")
        empty_conversation = []
        user_info = extract_user_info_from_conversation(empty_conversation)
        # Handle None return for empty conversation
        if user_info is None:
            print("✅ Empty conversation: PASS (correctly returns None)")
        else:
            is_complete = is_user_info_complete(user_info)
            if not is_complete:
                print("✅ Empty conversation: PASS (correctly incomplete)")
            else:
                print("❌ Empty conversation: FAIL (should be incomplete)")
                return False
        
        # Test 2: Partial information - just name
        print("\n2. Testing Partial Information - Name Only...")
        partial_conversation = [
            {"role": "user", "content": "My name is John"},
            {"role": "assistant", "content": "Hello John! I need your ID number to help you."}
        ]
        user_info = extract_user_info_from_conversation(partial_conversation)
        if user_info is None:
            print("✅ Partial information (name only): PASS (correctly returns None)")
        else:
            is_complete = is_user_info_complete(user_info)
            if not is_complete:
                print("✅ Partial information (name only): PASS (correctly incomplete)")
            else:
                print("❌ Partial information (name only): FAIL (should be incomplete)")
                return False
        
        # Test 3: Partial information - name and ID
        print("\n3. Testing Partial Information - Name and ID...")
        partial_conversation = [
            {"role": "user", "content": "My name is John Smith, ID 123456789"},
            {"role": "assistant", "content": "Great! I need your gender and age to continue."}
        ]
        user_info = extract_user_info_from_conversation(partial_conversation)
        if user_info is None:
            print("✅ Partial information (name + ID): PASS (correctly returns None)")
        else:
            is_complete = is_user_info_complete(user_info)
            if not is_complete:
                print("✅ Partial information (name + ID): PASS (correctly incomplete)")
            else:
                print("❌ Partial information (name + ID): FAIL (should be incomplete)")
                return False
        
        # Test 4: Complete information - English
        print("\n4. Testing Complete Information - English...")
        complete_conversation = [
            {"role": "user", "content": "My name is John Smith, ID 123456789, male, 30 years old, Maccabi HMO, card 987654321, Gold insurance"},
            {"role": "assistant", "content": "Thank you! I have all your information. How can I help you today?"}
        ]
        user_info = extract_user_info_from_conversation(complete_conversation)
        if user_info is None:
            print("❌ Complete information (English): FAIL (should extract info)")
            return False
        else:
            is_complete = is_user_info_complete(user_info)
            if is_complete:
                print("✅ Complete information (English): PASS (correctly complete)")
                print(f"   User: {user_info.get('name', 'N/A')}, HMO: {user_info.get('hmo_name', 'N/A')}")
            else:
                print("❌ Complete information (English): FAIL (should be complete)")
                return False
        
        # Test 5: Complete information - Hebrew
        print("\n5. Testing Complete Information - Hebrew...")
        hebrew_conversation = [
            {"role": "user", "content": "שמי דוד כהן, תעודת זהות 987654321, זכר, בן 35, מכבי, כרטיס 123456789, ביטוח זהב"},
            {"role": "assistant", "content": "תודה! יש לי את כל המידע שלך. איך אני יכול לעזור לך היום?"}
        ]
        user_info = extract_user_info_from_conversation(hebrew_conversation)
        if user_info is None:
            print("❌ Complete information (Hebrew): FAIL (should extract info)")
            return False
        else:
            is_complete = is_user_info_complete(user_info)
            if is_complete:
                print("✅ Complete information (Hebrew): PASS (correctly complete)")
                print(f"   User: {user_info.get('name', 'N/A')}, HMO: {user_info.get('hmo_name', 'N/A')}")
            else:
                print("❌ Complete information (Hebrew): FAIL (should be complete)")
                return False
        
        # Test 6: Mixed language conversation
        print("\n6. Testing Mixed Language Conversation...")
        mixed_conversation = [
            {"role": "user", "content": "My name is Sarah, תעודת זהות 111222333, female, 28 years old, Clalit, כרטיס 999888777, Silver insurance"},
            {"role": "assistant", "content": "Thank you Sarah! I have all your information."}
        ]
        user_info = extract_user_info_from_conversation(mixed_conversation)
        if user_info is None:
            print("❌ Mixed language conversation: FAIL (should extract info)")
            return False
        else:
            is_complete = is_user_info_complete(user_info)
            if is_complete:
                print("✅ Mixed language conversation: PASS (correctly complete)")
                print(f"   User: {user_info.get('name', 'N/A')}, HMO: {user_info.get('hmo_name', 'N/A')}")
            else:
                print("❌ Mixed language conversation: FAIL (should be complete)")
                return False
        
        # Test 7: Information extraction accuracy
        print("\n7. Testing Information Extraction Accuracy...")
        test_conversation = [
            {"role": "user", "content": "I'm David Wilson, ID 555666777, male, 42, Meuhedet HMO, card 333444555, Bronze plan"}
        ]
        user_info = extract_user_info_from_conversation(test_conversation)
        
        if user_info is None:
            print("❌ Information extraction accuracy: FAIL (should extract info)")
            return False
        
        expected_info = {
            'name': 'David Wilson',
            'id_number': '555666777',
            'gender': 'male',
            'age': '42',
            'hmo_name': 'Meuhedet',
            'hmo_card_number': '333444555',
            'insurance_tier': 'Bronze'
        }
        
        accuracy_score = 0
        for key, expected_value in expected_info.items():
            actual_value = user_info.get(key, '')
            if actual_value == expected_value:
                accuracy_score += 1
                print(f"   ✅ {key}: {actual_value}")
            else:
                print(f"   ❌ {key}: expected '{expected_value}', got '{actual_value}'")
        
        if accuracy_score >= 6:  # At least 6 out of 7 fields correct
            print(f"✅ Information extraction accuracy: PASS ({accuracy_score}/7 fields correct)")
        else:
            print(f"❌ Information extraction accuracy: FAIL ({accuracy_score}/7 fields correct)")
            return False
        
        print("\n✅ Information Collection Phase: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Information Collection Phase test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_information_collection_phase()
