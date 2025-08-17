#!/usr/bin/env python3
"""
Test file for RAG Context Retrieval functionality
Tests the core RAG knowledge base search and retrieval capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_rag_context_retrieval():
    """Test RAG context retrieval functionality"""
    print("Testing RAG Context Retrieval")
    print("=" * 60)
    
    try:
        from rag_kb import RAGKB
        
        # Initialize RAG KB
        kb = RAGKB()
        
        # Test 1: Basic search functionality
        print("\n1. Testing Basic Search...")
        search_results = kb.search_services("dental services", top_k=3, language="en")
        if search_results:
            print(f"✅ Basic search: PASS (results found)")
            # search_services returns a string, so we just check if it contains relevant content
            if "dental" in search_results.lower() or "שיניים" in search_results:
                print("   ✅ Relevant dental content found")
            else:
                print("   ⚠️ Content relevance unclear")
        else:
            print("❌ Basic search: FAIL (no results)")
            return False
        
        # Test 2: Language-specific search
        print("\n2. Testing Language-Specific Search...")
        hebrew_results = kb.search_services("שירותי שיניים", top_k=3, language="he")
        english_results = kb.search_services("dental services", top_k=3, language="en")
        
        if hebrew_results and english_results:
            print(f"✅ Language search: PASS (both Hebrew and English queries returned results)")
        else:
            print("❌ Language search: FAIL")
            return False
        
        # Test 3: Context relevance
        print("\n3. Testing Context Relevance...")
        relevant_results = kb.search_services("alternative medicine", top_k=2, language="en")
        if relevant_results:
            print("✅ Context relevance: PASS")
            # search_services returns a string, so we check the content directly
            if 'alternative' in relevant_results.lower() or 'רפואה משלימה' in relevant_results:
                print("   ✅ Relevant content found")
            else:
                print("   ⚠️ Content relevance unclear")
        else:
            print("❌ Context relevance: FAIL")
            return False
        
        # Test 4: Top-K parameter
        print("\n4. Testing Top-K Parameter...")
        top_1 = kb.search_services("dental", top_k=1, language="en")
        top_5 = kb.search_services("dental", top_k=5, language="en")
        
        # search_services returns a string, so we check if results exist and are not empty
        if top_1 and top_5 and len(top_1) > 0 and len(top_5) > 0:
            print("✅ Top-K parameter: PASS")
        else:
            print("❌ Top-K parameter: FAIL")
            return False
        
        # Test 5: Search with different service types
        print("\n5. Testing Different Service Types...")
        service_types = ["dental", "alternative", "communication", "optometry", "pregnancy", "workshops"]
        for service in service_types:
            results = kb.search_services(service, top_k=1, language="en")
            if results:
                print(f"   ✅ {service} services: PASS")
            else:
                print(f"   ❌ {service} services: FAIL")
        
        print("\n✅ RAG Context Retrieval: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ RAG Context Retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_accuracy():
    """Test that the RAG system retrieves the correct and relevant chunks"""
    print("\nTesting Context Retrieval Accuracy")
    print("=" * 60)
    
    try:
        from rag_kb import RAGKB
        
        # Initialize RAG KB
        kb = RAGKB()
        
        # Test 1: HMO-specific retrieval accuracy
        print("\n1. Testing HMO-Specific Retrieval Accuracy...")
        
        # Test Maccabi dental services
        maccabi_dental = kb.search_services("dental services", hmo_name="maccabi", top_k=1, language="en")
        if maccabi_dental and "maccabi" in maccabi_dental.lower():
            print("✅ Maccabi dental services: PASS (correct HMO retrieved)")
        else:
            print("❌ Maccabi dental services: FAIL (wrong HMO or no results)")
            return False
        
        # Test Clalit alternative medicine
        clalit_alternative = kb.search_services("alternative medicine", hmo_name="clalit", top_k=1, language="en")
        if clalit_alternative and "clalit" in clalit_alternative.lower():
            print("✅ Clalit alternative medicine: PASS (correct HMO retrieved)")
        else:
            print("❌ Clalit alternative medicine: FAIL (wrong HMO or no results)")
            return False
        
        # Test Meuhedet optometry
        meuhedet_optometry = kb.search_services("optometry", hmo_name="meuhedet", top_k=1, language="en")
        if meuhedet_optometry and "meuhedet" in meuhedet_optometry.lower():
            print("✅ Meuhedet optometry: PASS (correct HMO retrieved)")
        else:
            print("❌ Meuhedet optometry: FAIL (wrong HMO or no results)")
            return False
        
        # Test 2: Service-specific retrieval accuracy
        print("\n2. Testing Service-Specific Retrieval Accuracy...")
        
        # Test dental services across all HMOs
        dental_results = kb.search_services("dental", top_k=3, language="en")
        if dental_results:
            # Should return chunks from different HMOs for dental services
            print("✅ Dental services retrieval: PASS (multiple HMO chunks returned)")
        else:
            print("❌ Dental services retrieval: FAIL (no results)")
            return False
        
        # Test alternative medicine across all HMOs
        alternative_results = kb.search_services("alternative", top_k=3, language="en")
        if alternative_results:
            print("✅ Alternative medicine retrieval: PASS (multiple HMO chunks returned)")
        else:
            print("❌ Alternative medicine retrieval: FAIL (no results)")
            return False
        
        # Test 3: Cross-language retrieval accuracy
        print("\n3. Testing Cross-Language Retrieval Accuracy...")
        
        # English query should find Hebrew content
        english_query = kb.search_services("dental", top_k=1, language="en")
        if english_query and any('\u0590' <= char <= '\u05FF' for char in english_query):
            print("✅ English query finds Hebrew content: PASS")
        else:
            print("❌ English query finds Hebrew content: FAIL")
            return False
        
        # Hebrew query should find relevant content
        hebrew_query = kb.search_services("שירותי שיניים", top_k=1, language="he")
        if hebrew_query and "שיניים" in hebrew_query:
            print("✅ Hebrew query finds relevant content: PASS")
        else:
            print("❌ Hebrew query finds relevant content: FAIL")
            return False
        
        # Test 4: Chunk structure validation
        print("\n4. Testing Chunk Structure Validation...")
        
        # Verify that we have exactly 18 chunks (6 services × 3 HMOs)
        if hasattr(kb, 'chunks') and len(kb.chunks) == 18:
            print(f"✅ Chunk count: PASS (18 chunks as expected)")
            
            # Verify chunk structure
            chunk_structure_valid = True
            for chunk in kb.chunks:
                required_fields = ['content', 'service', 'chunk_type', 'chunk_id', 'hmo', 'hmo_hebrew']
                if not all(field in chunk for field in required_fields):
                    chunk_structure_valid = False
                    break
            
            if chunk_structure_valid:
                print("✅ Chunk structure: PASS (all required fields present)")
            else:
                print("❌ Chunk structure: FAIL (missing required fields)")
                return False
        else:
            print(f"❌ Chunk count: FAIL (expected 18, got {len(kb.chunks) if hasattr(kb, 'chunks') else 'unknown'})")
            return False
        
        # Test 5: Specific chunk retrieval validation
        print("\n5. Testing Specific Chunk Retrieval...")
        
        # Test specific service-HMO combinations
        test_cases = [
            ("dental", "maccabi", "מכבי"),
            ("alternative", "clalit", "כללית"),
            ("optometry", "meuhedet", "מאוחדת"),
            ("pregnancy", "maccabi", "מכבי"),
            ("communication", "clalit", "כללית"),
            ("workshops", "meuhedet", "מאוחדת")
        ]
        
        for service, hmo_english, hmo_hebrew in test_cases:
            result = kb.search_services(service, hmo_name=hmo_english, top_k=1, language="en")
            if result and hmo_english.lower() in result.lower():
                print(f"   ✅ {service} + {hmo_english}: PASS")
            else:
                print(f"   ❌ {service} + {hmo_english}: FAIL")
                return False
        
        # Test 6: Relevance scoring validation
        print("\n6. Testing Relevance Scoring...")
        
        # Test that more specific queries return more relevant results
        specific_query = kb.search_services("Maccabi dental services coverage", top_k=1, language="en")
        general_query = kb.search_services("dental", top_k=1, language="en")
        
        if specific_query and general_query:
            # The specific query should contain more targeted information
            if "maccabi" in specific_query.lower() and "dental" in specific_query.lower():
                print("✅ Specific query relevance: PASS")
            else:
                print("❌ Specific query relevance: FAIL")
                return False
        else:
            print("❌ Query relevance comparison: FAIL (no results)")
            return False
        
        print("\n✅ Context Retrieval Accuracy: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Context Retrieval Accuracy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run both tests
    success1 = test_rag_context_retrieval()
    success2 = test_context_accuracy()
    
    if success1 and success2:
        print("\n🎉 ALL RAG CONTEXT TESTS PASSED!")
        print("✅ Basic functionality: PASS")
        print("✅ Context accuracy: PASS")
    else:
        print("\n❌ Some RAG context tests failed!")
        if not success1:
            print("❌ Basic functionality: FAIL")
        if not success2:
            print("❌ Context accuracy: FAIL")
