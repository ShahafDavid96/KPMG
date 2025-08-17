#!/usr/bin/env python3
"""
Test file for Phase Transitions functionality
Tests transitions between information collection and Q&A phases
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_phase_transitions():
    """Test transitions between information collection and Q&A phases"""
    print("Testing Phase Transitions")
    print("=" * 60)
    
    try:
        from utils import extract_user_info_from_conversation, is_user_info_complete
        from prompts import get_prompt
        
        # Test 1: Phase transition logic - empty conversation
        print("\n1. Testing Phase Transition Logic - Empty Conversation...")
        
        # Start with empty conversation
        conversation = []
        user_info = extract_user_info_from_conversation(conversation)
        
        if user_info is None:
            # Should use info collection prompt
            prompt = get_prompt("info_collection", "en")
            if prompt and "information" in prompt.lower():
                print("✅ Phase transition 1: PASS (info collection prompt)")
            else:
                print("❌ Phase transition 1: FAIL (wrong prompt type)")
                return False
        else:
            print("❌ Phase transition 1: FAIL (should be None)")
            return False
        
        # Test 2: Add partial information - name only
        print("\n2. Testing Partial Information Transition - Name Only...")
        conversation.append({"role": "user", "content": "My name is Sarah"})
        user_info = extract_user_info_from_conversation(conversation)
        
        # The system extracts partial info, which is correct behavior
        if user_info is not None:
            is_complete = is_user_info_complete(user_info)
            if not is_complete:
                print("✅ Phase transition 2: PASS (partial info extracted, correctly incomplete)")
            else:
                print("❌ Phase transition 2: FAIL (should be incomplete)")
                return False
        else:
            print("❌ Phase transition 2: FAIL (should extract partial info)")
            return False
        
        # Test 3: Add more partial information - name + ID
        print("\n3. Testing Partial Information Transition - Name + ID...")
        conversation.append({"role": "user", "content": "My ID is 123456789"})
        user_info = extract_user_info_from_conversation(conversation)
        
        if user_info is not None:
            is_complete = is_user_info_complete(user_info)
            if not is_complete:
                print("✅ Phase transition 3: PASS (more info extracted, still incomplete)")
            else:
                print("❌ Phase transition 3: FAIL (should still be incomplete)")
                return False
        else:
            print("❌ Phase transition 3: FAIL (should extract accumulated info)")
            return False
        
        # Test 4: Complete information transition
        print("\n4. Testing Complete Information Transition...")
        conversation.append({"role": "user", "content": "I'm female, 25 years old, Maccabi HMO, card 111111111, Gold insurance"})
        user_info = extract_user_info_from_conversation(conversation)
        
        if user_info is not None:
            is_complete = is_user_info_complete(user_info)
            if is_complete:
                print("✅ Phase transition 4: PASS (complete info detected)")
                print(f"   User: {user_info.get('name', 'N/A')}, HMO: {user_info.get('hmo_name', 'N/A')}")
            else:
                print("❌ Phase transition 4: FAIL (should be complete)")
                return False
        else:
            print("❌ Phase transition 4: FAIL (should extract info)")
            return False
        
        # Test 5: Phase transition to Q&A
        print("\n5. Testing Phase Transition to Q&A...")
        if user_info is not None:
            # Should now use Q&A prompt
            qa_prompt = get_prompt("qa", "en")
            if qa_prompt and "healthcare" in qa_prompt.lower():
                print("✅ Phase transition to Q&A: PASS (Q&A prompt generated)")
            else:
                print("❌ Phase transition to Q&A: FAIL (Q&A prompt not generated)")
                return False
        else:
            print("❌ Phase transition to Q&A: FAIL (user info not available)")
            return False
        
        # Test 6: Hebrew conversation phase transition
        print("\n6. Testing Hebrew Conversation Phase Transition...")
        hebrew_conversation = []
        
        # Empty Hebrew conversation
        hebrew_user_info = extract_user_info_from_conversation(hebrew_conversation)
        if hebrew_user_info is None:
            hebrew_prompt = get_prompt("info_collection", "he")
            if hebrew_prompt:
                print("✅ Hebrew phase transition 1: PASS (info collection prompt)")
            else:
                print("❌ Hebrew phase transition 1: FAIL (no prompt generated)")
                return False
        else:
            print("❌ Hebrew phase transition 1: FAIL (should be None)")
            return False
        
        # Add Hebrew information
        hebrew_conversation.append({"role": "user", "content": "שמי דוד כהן, תעודת זהות 987654321, זכר, בן 35, מכבי, כרטיס 123456789, ביטוח זהב"})
        hebrew_user_info = extract_user_info_from_conversation(hebrew_conversation)
        
        if hebrew_user_info is not None:
            hebrew_is_complete = is_user_info_complete(hebrew_user_info)
            if hebrew_is_complete:
                print("✅ Hebrew phase transition 2: PASS (complete info detected)")
                print(f"   User: {hebrew_user_info.get('name', 'N/A')}, HMO: {hebrew_user_info.get('hmo_name', 'N/A')}")
            else:
                print("❌ Hebrew phase transition 2: FAIL (should be complete)")
                return False
        else:
            print("❌ Hebrew phase transition 2: FAIL (should extract info)")
            return False
        
        # Test 7: Mixed language phase transition
        print("\n7. Testing Mixed Language Phase Transition...")
        mixed_conversation = []
        
        # Start with English
        mixed_conversation.append({"role": "user", "content": "My name is Rachel"})
        mixed_user_info = extract_user_info_from_conversation(mixed_conversation)
        
        # System extracts partial info, which is correct
        if mixed_user_info is not None:
            is_complete = is_user_info_complete(mixed_user_info)
            if not is_complete:
                print("✅ Mixed language phase transition 1: PASS (partial info extracted)")
            else:
                print("❌ Mixed language phase transition 1: FAIL (should be incomplete)")
                return False
        else:
            print("❌ Mixed language phase transition 1: FAIL (should extract partial info)")
            return False
        
        # Add Hebrew information
        mixed_conversation.append({"role": "user", "content": "תעודת זהות 111222333, נקבה, בת 29, כללית, כרטיס 999888777, ביטוח כסף"})
        mixed_user_info = extract_user_info_from_conversation(mixed_conversation)
        
        if mixed_user_info is not None:
            mixed_is_complete = is_user_info_complete(mixed_user_info)
            if mixed_is_complete:
                print("✅ Mixed language phase transition 2: PASS (complete info detected)")
                print(f"   User: {mixed_user_info.get('name', 'N/A')}, HMO: {mixed_user_info.get('hmo_name', 'N/A')}")
            else:
                print("❌ Mixed language phase transition 2: FAIL (should be complete)")
                return False
        else:
            print("❌ Mixed language phase transition 2: FAIL (should extract info)")
            return False
        
        # Test 8: Phase transition edge cases
        print("\n8. Testing Phase Transition Edge Cases...")
        
        # Test with minimal required info (using patterns the extraction function can recognize)
        minimal_conversation = [{"role": "user", "content": "John, ID 123456789, male, 30, Maccabi, card 111111111, Gold"}]
        minimal_user_info = extract_user_info_from_conversation(minimal_conversation)
        
        if minimal_user_info is not None:
            minimal_is_complete = is_user_info_complete(minimal_user_info)
            if minimal_is_complete:
                print("✅ Minimal info phase transition: PASS (complete with minimal format)")
            else:
                print("❌ Minimal info phase transition: FAIL (should be complete)")
                return False
        else:
            print("❌ Minimal info phase transition: FAIL (should extract info)")
            return False
        
        # Test with extra information
        extra_conversation = [{"role": "user", "content": "I'm Lisa, ID 555666777, female, 27, Meuhedet, card 333444555, Bronze plan, I also have diabetes and need special care"}]
        extra_user_info = extract_user_info_from_conversation(extra_conversation)
        
        if extra_user_info is not None:
            extra_is_complete = is_user_info_complete(extra_user_info)
            if extra_is_complete:
                print("✅ Extra info phase transition: PASS (complete with extra details)")
            else:
                print("❌ Extra info phase transition: FAIL (should be complete)")
                return False
        else:
            print("❌ Extra info phase transition: FAIL (should extract info)")
            return False
        
        print("\n✅ Phase Transitions: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Phase Transitions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_phase_transitions()
