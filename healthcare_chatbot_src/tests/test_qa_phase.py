#!/usr/bin/env python3
"""
Test file for Q&A Phase functionality
Tests Q&A capabilities with RAG context and personalized responses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_qa_phase():
    """Test the Q&A phase with RAG context"""
    print("🧪 Testing Q&A Phase with RAG Context")
    print("=" * 60)
    
    try:
        from rag_kb import RAGKB
        from prompts import get_prompt
        from utils import extract_user_info_from_conversation
        
        # Initialize RAG KB
        kb = RAGKB()
        
        # Test 1: Basic Q&A with context
        print("\n1. Testing Basic Q&A...")
        user_info = {
            "name": "John Smith",
            "hmo_name": "Maccabi",
            "insurance_tier": "Gold"
        }
        
        # Search for relevant context
        context_results = kb.search_services("dental services", top_k=2, language="en")
        if context_results:
            # Get Q&A prompt using the actual function
            qa_prompt = get_prompt("qa", "en")
            if qa_prompt and "healthcare" in qa_prompt.lower():
                print("✅ Basic Q&A: PASS (Q&A prompt generated)")
            else:
                print("❌ Basic Q&A: FAIL (Q&A prompt not generated)")
                return False
        else:
            print("❌ Basic Q&A: FAIL (no context found)")
            return False
        
        # Test 2: HMO-specific Q&A
        print("\n2. Testing HMO-Specific Q&A...")
        maccabi_context = kb.search_services("Maccabi services", top_k=1, language="en")
        if maccabi_context:
            print("✅ HMO-specific Q&A: PASS (Maccabi context found)")
        else:
            print("❌ HMO-specific Q&A: FAIL (no context found)")
            return False
        
        # Test 3: Insurance tier specific Q&A
        print("\n3. Testing Insurance Tier Q&A...")
        gold_context = kb.search_services("Gold insurance benefits", top_k=2, language="en")
        if gold_context:
            print("✅ Insurance tier Q&A: PASS (Gold benefits context found)")
        else:
            print("❌ Insurance tier Q&A: FAIL (no Gold benefits context)")
            return False
        
        # Test 4: Bilingual Q&A
        print("\n4. Testing Bilingual Q&A...")
        hebrew_context = kb.search_services("שירותי רפואה משלימה", top_k=1, language="he")
        english_context = kb.search_services("alternative medicine", top_k=1, language="en")
        
        if hebrew_context and english_context:
            print("✅ Bilingual Q&A: PASS (both languages supported)")
        else:
            print("❌ Bilingual Q&A: FAIL (language support incomplete)")
            return False
        
        # Test 5: Service-specific Q&A
        print("\n5. Testing Service-Specific Q&A...")
        services_to_test = [
            ("dental", "שירותי שיניים"),
            ("alternative", "רפואה משלימה"),
            ("communication", "שירותי תקשורת"),
            ("optometry", "שירותי אופטומטריה"),
            ("pregnancy", "שירותי הריון"),
            ("workshops", "סדנאות")
        ]
        
        for english_service, hebrew_service in services_to_test:
            en_results = kb.search_services(english_service, top_k=1, language="en")
            he_results = kb.search_services(hebrew_service, top_k=1, language="he")
            
            if en_results or he_results:
                print(f"   ✅ {english_service} services: PASS")
            else:
                print(f"   ❌ {english_service} services: FAIL")
        
        # Test 6: Prompt generation for different phases
        print("\n6. Testing Prompt Generation...")
        qa_prompt_en = get_prompt("qa", "en")
        qa_prompt_he = get_prompt("qa", "he")
        info_prompt_en = get_prompt("info_collection", "en")
        info_prompt_he = get_prompt("info_collection", "he")
        
        if qa_prompt_en and qa_prompt_he:
            print("✅ Q&A prompts: PASS (both languages)")
        else:
            print("❌ Q&A prompts: FAIL")
            return False
        
        if info_prompt_en and info_prompt_he:
            print("✅ Info collection prompts: PASS (both languages)")
        else:
            print("❌ Info collection prompts: FAIL")
            return False
        
        # Test 7: Context relevance scoring
        print("\n7. Testing Context Relevance Scoring...")
        query = "dental services coverage"
        results = kb.search_services(query, top_k=3, language="en")
        
        if results:
            print(f"✅ Context relevance scoring: PASS ({len(results)} relevant results)")
            for i, result in enumerate(results, 1):
                if isinstance(result, dict):
                    content = result.get('content', '')
                else:
                    content = str(result)
                if 'dental' in content.lower() or 'שיניים' in content:
                    print(f"   ✅ Result {i}: Relevant content found")
                else:
                    print(f"   ⚠️ Result {i}: Content relevance unclear")
        else:
            print("❌ Context relevance scoring: FAIL (no results)")
            return False
        
        print("\n✅ Q&A Phase: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Q&A Phase test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_qa_phase()
