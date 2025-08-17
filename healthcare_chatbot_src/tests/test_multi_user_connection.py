#!/usr/bin/env python3
"""
Test file for Multi-User Connection functionality
Tests multiple concurrent users, session management, and connection stability
"""

import sys
import os
import time
import threading
import concurrent.futures
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_single_user_connection():
    """Test basic single user connection functionality"""
    print("🧪 Testing Single User Connection")
    print("=" * 60)
    
    try:
        from rag_kb import RAGKB
        from utils import extract_user_info_from_conversation
        
        # Initialize RAG KB
        kb = RAGKB()
        print("✅ RAG KB initialized")
        
        # Test basic user interaction
        conversation = [{"role": "user", "content": "My name is John Smith, ID 123456789, male, 30, Maccabi, 111111111, Gold"}]
        user_info = extract_user_info_from_conversation(conversation)
        
        if user_info:
            print("✅ User info extraction: PASS")
            
            # Test RAG search for this user
            search_result = kb.search_services("dental services", hmo_name="maccabi", top_k=1, language="en")
            if search_result:
                print("✅ RAG search for user: PASS")
            else:
                print("❌ RAG search for user: FAIL")
                return False
        else:
            print("❌ User info extraction: FAIL")
            return False
        
        print("✅ Single User Connection: PASS")
        return True
        
    except Exception as e:
        print(f"❌ Single User Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_concurrent_user_connections():
    """Test multiple concurrent user connections"""
    print("\n🧪 Testing Concurrent User Connections")
    print("=" * 60)
    
    try:
        from rag_kb import RAGKB
        from utils import extract_user_info_from_conversation
        
        # Test data for multiple users
        test_users = [
            {"name": "Alice Johnson", "id": "111111111", "hmo": "maccabi"},
            {"name": "Bob Davis", "id": "222222222", "hmo": "clalit"},
            {"name": "Carol Wilson", "id": "333333333", "hmo": "meuhedet"},
            {"name": "David Brown", "id": "444444444", "hmo": "maccabi"},
            {"name": "Eva Garcia", "id": "555555555", "hmo": "clalit"}
        ]
        
        def simulate_user_session(user_data):
            """Simulate a single user session"""
            try:
                # Create user conversation
                conversation = [{"role": "user", "content": f"My name is {user_data['name']}, ID {user_data['id']}, Maccabi HMO"}]
                
                # Extract user info
                user_info = extract_user_info_from_conversation(conversation)
                if not user_info:
                    return False, f"Failed to extract info for {user_data['name']}"
                
                # Simulate RAG search
                kb = RAGKB()
                search_result = kb.search_services("dental", hmo_name=user_data['hmo'], top_k=1, language="en")
                if not search_result:
                    return False, f"Failed RAG search for {user_data['name']}"
                
                # Simulate processing time
                time.sleep(0.1)
                
                return True, f"Success for {user_data['name']}"
                
            except Exception as e:
                return False, f"Error for {user_data['name']}: {e}"
        
        # Test concurrent execution
        print("Testing 5 concurrent user sessions...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all user sessions concurrently
            future_to_user = {executor.submit(simulate_user_session, user): user for user in test_users}
            
            # Collect results
            successful_sessions = 0
            total_sessions = len(test_users)
            
            for future in concurrent.futures.as_completed(future_to_user):
                user = future_to_user[future]
                try:
                    success, message = future.result()
                    if success:
                        successful_sessions += 1
                        print(f"   ✅ {message}")
                    else:
                        print(f"   ❌ {message}")
                except Exception as e:
                    print(f"   ❌ {user['name']}: Exception occurred: {e}")
        
        success_rate = (successful_sessions / total_sessions) * 100
        print(f"\nConcurrent Sessions: {successful_sessions}/{total_sessions} successful ({success_rate:.1f}%)")
        
        if success_rate >= 80:  # At least 80% success rate
            print("✅ Concurrent User Connections: PASS")
            return True
        else:
            print("❌ Concurrent User Connections: FAIL (insufficient success rate)")
            return False
        
    except Exception as e:
        print(f"❌ Concurrent User Connections test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_management():
    """Test session management and isolation"""
    print("\n🧪 Testing Session Management")
    print("=" * 60)
    
    try:
        from rag_kb import RAGKB
        from utils import extract_user_info_from_conversation
        
        # Test that different users get isolated responses
        user1_conversation = [{"role": "user", "content": "My name is Alice, Maccabi HMO"}]
        user2_conversation = [{"role": "user", "content": "My name is Bob, Clalit HMO"}]
        
        # Extract user info
        user1_info = extract_user_info_from_conversation(user1_conversation)
        user2_info = extract_user_info_from_conversation(user2_conversation)
        
        if not user1_info or not user2_info:
            print("❌ User info extraction failed")
            return False
        
        # Test that users get different HMO-specific responses
        kb = RAGKB()
        
        user1_response = kb.search_services("dental", hmo_name="maccabi", top_k=1, language="en")
        user2_response = kb.search_services("dental", hmo_name="clalit", top_k=1, language="en")
        
        if user1_response and user2_response:
            # Check that responses are different (different HMOs)
            if user1_response != user2_response:
                print("✅ Session isolation: PASS (different users get different responses)")
            else:
                print("⚠️ Session isolation: WARNING (identical responses for different users)")
            
            # Check that each response contains the correct HMO information
            if "maccabi" in user1_response.lower():
                print("✅ User 1 HMO-specific response: PASS")
            else:
                print("❌ User 1 HMO-specific response: FAIL")
                return False
            
            if "clalit" in user2_response.lower():
                print("✅ User 2 HMO-specific response: PASS")
            else:
                print("❌ User 2 HMO-specific response: FAIL")
                return False
        else:
            print("❌ RAG responses failed")
            return False
        
        print("✅ Session Management: PASS")
        return True
        
    except Exception as e:
        print(f"❌ Session Management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_load_performance():
    """Test system performance under load"""
    print("\n🧪 Testing Load Performance")
    print("=" * 60)
    
    try:
        from rag_kb import RAGKB
        from utils import extract_user_info_from_conversation
        
        # Test performance with multiple rapid requests
        kb = RAGKB()
        
        # Generate test queries
        test_queries = [
            "dental services",
            "alternative medicine", 
            "optometry",
            "pregnancy care",
            "communication services",
            "workshops"
        ]
        
        print("Testing rapid sequential queries...")
        start_time = time.time()
        
        successful_queries = 0
        total_queries = len(test_queries)
        
        for query in test_queries:
            try:
                result = kb.search_services(query, top_k=1, language="en")
                if result:
                    successful_queries += 1
                    print(f"   ✅ {query}: PASS")
                else:
                    print(f"   ❌ {query}: FAIL")
            except Exception as e:
                print(f"   ❌ {query}: ERROR - {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        success_rate = (successful_queries / total_queries) * 100
        avg_query_time = total_time / total_queries
        
        print(f"\nLoad Test Results:")
        print(f"   Successful Queries: {successful_queries}/{total_queries} ({success_rate:.1f}%)")
        print(f"   Total Time: {total_time:.2f}s")
        print(f"   Average Query Time: {avg_query_time:.2f}s")
        
        # Performance criteria
        if success_rate >= 80 and avg_query_time <= 2.0:  # 80% success, max 2s per query
            print("✅ Load Performance: PASS")
            return True
        else:
            print("❌ Load Performance: FAIL (insufficient success rate or too slow)")
            return False
        
    except Exception as e:
        print(f"❌ Load Performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_connection_stability():
    """Test connection stability over time"""
    print("\n🧪 Testing Connection Stability")
    print("=" * 60)
    
    try:
        from rag_kb import RAGKB
        
        # Test repeated connections over time
        print("Testing connection stability with repeated initializations...")
        
        successful_connections = 0
        total_attempts = 5
        
        for attempt in range(total_attempts):
            try:
                kb = RAGKB()
                
                # Test basic functionality
                result = kb.search_services("dental", top_k=1, language="en")
                if result:
                    successful_connections += 1
                    print(f"   ✅ Connection attempt {attempt + 1}: PASS")
                else:
                    print(f"   ❌ Connection attempt {attempt + 1}: FAIL (no results)")
                
                # Small delay between attempts
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Connection attempt {attempt + 1}: ERROR - {e}")
        
        stability_rate = (successful_connections / total_attempts) * 100
        print(f"\nConnection Stability: {successful_connections}/{total_attempts} successful ({stability_rate:.1f}%)")
        
        if stability_rate >= 80:  # At least 80% success rate
            print("✅ Connection Stability: PASS")
            return True
        else:
            print("❌ Connection Stability: FAIL (insufficient stability)")
            return False
        
    except Exception as e:
        print(f"❌ Connection Stability test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run all multi-user connection tests
    print("🚀 Running Multi-User Connection Test Suite")
    print("=" * 80)
    
    tests = [
        ("Single User Connection", test_single_user_connection),
        ("Concurrent User Connections", test_concurrent_user_connections),
        ("Session Management", test_session_management),
        ("Load Performance", test_load_performance),
        ("Connection Stability", test_connection_stability)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 {test_name}: CRASHED with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 MULTI-USER CONNECTION TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL MULTI-USER CONNECTION TESTS PASSED!")
        print("✅ Single user connections: Working")
        print("✅ Concurrent connections: Working")
        print("✅ Session management: Working")
        print("✅ Load performance: Working")
        print("✅ Connection stability: Working")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the issues above.")
