#!/usr/bin/env python3
"""
Comprehensive Test Runner for Healthcare Chatbot System
Runs all individual test suites and provides a complete system overview
"""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def run_all_tests():
    """Run all test suites and provide comprehensive results"""
    print("🚀 Running Comprehensive Healthcare Chatbot Test Suite")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Import all test modules
    try:
        from test_rag_context import test_rag_context_retrieval, test_context_accuracy
        from test_information_collection import test_information_collection_phase
        from test_qa_phase import test_qa_phase
        from test_phase_transitions import test_phase_transitions
        from test_multi_user_connection import (
            test_single_user_connection,
            test_concurrent_user_connections,
            test_session_management,
            test_load_performance,
            test_connection_stability
        )
        print("✅ All test modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import test modules: {e}")
        return False
    
    # Define test suites
    tests = [
        ("RAG Context Retrieval", test_rag_context_retrieval),
        ("Context Retrieval Accuracy", test_context_accuracy),
        ("Information Collection Phase", test_information_collection_phase),
        ("Q&A Phase", test_qa_phase),
        ("Phase Transitions", test_phase_transitions),
        ("Single User Connection", test_single_user_connection),
        ("Concurrent User Connections", test_concurrent_user_connections),
        ("Session Management", test_session_management),
        ("Load Performance", test_load_performance),
        ("Connection Stability", test_connection_stability)
    ]
    
    # Run all tests
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            test_start = time.time()
            result = test_func()
            test_time = time.time() - test_start
            
            if result:
                print(f"✅ {test_name}: PASSED in {test_time:.2f}s")
                results.append((test_name, True, test_time))
            else:
                print(f"❌ {test_name}: FAILED in {test_time:.2f}s")
                results.append((test_name, False, test_time))
                
        except Exception as e:
            print(f"💥 {test_name}: CRASHED with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False, 0))
    
    # Calculate total time
    total_time = time.time() - start_time
    
    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("=" * 80)
    
    passed = 0
    failed = 0
    total = len(results)
    
    for test_name, result, test_time in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name:<30} ({test_time:.2f}s)")
        if result:
            passed += 1
        else:
            failed += 1
    
    # Summary statistics
    print("\n" + "-" * 80)
    print("📈 SUMMARY STATISTICS")
    print("-" * 80)
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Total Execution Time: {total_time:.2f}s")
    print(f"Average Test Time: {total_time/total:.2f}s per test")
    
    # Performance analysis
    print("\n" + "-" * 80)
    print("⚡ PERFORMANCE ANALYSIS")
    print("-" * 80)
    
    if results:
        test_times = [time for _, _, time in results if time > 0]
        if test_times:
            fastest_test = min(test_times)
            slowest_test = max(test_times)
            avg_test_time = sum(test_times) / len(test_times)
            
            print(f"Fastest Test: {fastest_test:.2f}s")
            print(f"Slowest Test: {slowest_test:.2f}s")
            print(f"Average Test Time: {avg_test_time:.2f}s")
    
    # System health assessment
    print("\n" + "-" * 80)
    print("🏥 SYSTEM HEALTH ASSESSMENT")
    print("-" * 80)
    
    if success_rate >= 90:
        print("🟢 EXCELLENT: System is working perfectly!")
        print("   All major components are functioning correctly.")
    elif success_rate >= 75:
        print("🟡 GOOD: System is mostly working well.")
        print("   Some minor issues detected but core functionality is solid.")
    elif success_rate >= 50:
        print("🟠 FAIR: System has some issues.")
        print("   Core functionality works but several components need attention.")
    else:
        print("🔴 POOR: System has significant issues.")
        print("   Multiple components are failing and need immediate attention.")
    
    # Recommendations
    print("\n" + "-" * 80)
    print("💡 RECOMMENDATIONS")
    print("-" * 80)
    
    if failed > 0:
        print("Issues detected that need attention:")
        for test_name, result, _ in results:
            if not result:
                print(f"   • {test_name}: Investigate and fix failures")
        print("\nConsider running individual test files for detailed debugging:")
        print("   python test_rag_context.py")
        print("   python test_information_collection.py")
        print("   python test_qa_phase.py")
        print("   python test_phase_transitions.py")
        print("   python test_multi_user_connection.py")
    else:
        print("🎉 No issues detected! System is ready for production use.")
    
    # Final status
    print("\n" + "=" * 80)
    if passed == total:
        print("🎉 ALL TESTS PASSED! Healthcare Chatbot System is fully operational.")
        print("✅ RAG Context Retrieval: Working")
        print("✅ Context Retrieval Accuracy: Working")
        print("✅ Information Collection: Working")
        print("✅ Q&A Phase: Working")
        print("✅ Phase Transitions: Working")
        print("✅ Multi-User Connections: Working")
    else:
        print(f"⚠️ {failed} test(s) failed. Please review the issues above.")
    
    print(f"\nTest suite completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return passed == total

def run_quick_test():
    """Run a quick smoke test to check basic functionality"""
    print("🚀 Running Quick Smoke Test")
    print("=" * 50)
    
    try:
        # Test basic imports
        from rag_kb import RAGKB
        from utils import extract_user_info_from_conversation
        print("✅ Basic imports: PASS")
        
        # Test RAG initialization
        kb = RAGKB()
        print("✅ RAG initialization: PASS")
        
        # Test basic search
        results = kb.search_services("dental", top_k=1, language="en")
        if results:
            print("✅ Basic search: PASS")
        else:
            print("❌ Basic search: FAIL")
            return False
        
        # Test user info extraction
        conversation = [{"role": "user", "content": "My name is Test User"}]
        user_info = extract_user_info_from_conversation(conversation)
        if user_info:
            print("✅ User info extraction: PASS")
        else:
            print("❌ User info extraction: FAIL")
            return False
        
        print("✅ Quick smoke test: PASS")
        return True
        
    except Exception as e:
        print(f"❌ Quick smoke test failed: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Healthcare Chatbot Test Suite")
    parser.add_argument("--quick", action="store_true", help="Run quick smoke test only")
    
    args = parser.parse_args()
    
    if args.quick:
        success = run_quick_test()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
