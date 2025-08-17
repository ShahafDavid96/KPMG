#!/usr/bin/env python3
"""
System test script for Medical Services ChatBot
Tests all major components and functionality
"""

import sys
import os
import traceback
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing module imports...")
    
    # Test RAGKB import
    try:
        from rag_kb import RAGKB
        print("RAGKB import: PASS")
    except Exception as e:
        print(f"Failed to import RAGKB: {e}")
        return False
    
    # Test API module import
    try:
        from api import create_app, get_knowledge_base
        print("API module import: PASS")
    except Exception as e:
        print(f"Failed to import API module: {e}")
        return False
    
    # Test Utils module import
    try:
        from utils import extract_user_info_from_conversation, is_user_info_complete
        print("Utils module import: PASS")
    except Exception as e:
        print(f"Failed to import Utils module: {e}")
        return False
    
    # Test Prompts module import
    try:
        from prompts import get_info_collection_prompt, get_qa_prompt
        print("Prompts module import: PASS")
    except Exception as e:
        print(f"Failed to import Prompts module: {e}")
        return False
    
    # Test Models module import
    try:
        from models import ChatRequest, ChatResponse
        print("Models module import: PASS")
    except Exception as e:
        print(f"Failed to import Models module: {e}")
        return False
    
    # Test Config module import
    try:
        from config import get_azure_openai_client, validate_configuration
        print("Config module import: PASS")
    except Exception as e:
        print(f"Failed to import Config module: {e}")
        return False
    
    print("All imports successful!")
    return True

def test_rag_knowledge_base():
    """Test RAG knowledge base functionality"""
    print("\nTesting RAG knowledge base...")
    
    try:
        from rag_kb import RAGKB
        
        # Initialize KB
        kb = RAGKB()
        
        # Test chunk creation
        if hasattr(kb, '_create_chunks'):
            chunks = kb._create_chunks()
            print(f"Chunk creation: PASS ({len(chunks)} chunks created)")
        else:
            print("Chunk creation: FAIL (method not found)")
            return False
        
        # Test search functionality
        search_result = kb.search_services("dental services", top_k=3, language="en")
        if search_result and len(search_result) > 0:
            print("Search functionality: PASS")
        else:
            print("Search functionality: FAIL (no results)")
            return False
        
        print("RAG knowledge base test: PASS")
        return True
        
    except Exception as e:
        print(f"RAG knowledge base test failed: {e}")
        return False

def test_utils_functions():
    """Test utility functions"""
    print("\nTesting utility functions...")
    
    try:
        from utils import extract_user_info_from_conversation, is_user_info_complete
        
        # Test user info extraction
        test_conversation = [
            "My name is John Doe, I'm 30 years old, male, ID 123456789, HMO Maccabi, card 987654321, insurance Gold"
        ]
        
        extracted_info = extract_user_info_from_conversation(test_conversation)
        if extracted_info and 'name' in extracted_info:
            print("User info extraction: PASS")
        else:
            print("User info extraction: FAIL")
            return False
        
        # Test user info completion check
        is_complete = is_user_info_complete(extracted_info)
        if isinstance(is_complete, bool):
            print("User info completion check: PASS")
        else:
            print("User info completion check: FAIL")
            return False
        
        print("Utils test: PASS")
        return True
        
    except Exception as e:
        print(f"Utils test failed: {e}")
        return False

def test_prompts():
    """Test prompt generation"""
    print("\nTesting prompts...")
    
    try:
        from prompts import get_info_collection_prompt, get_qa_prompt
        
        # Test info collection prompt
        info_prompt_he = get_info_collection_prompt("he")
        info_prompt_en = get_info_collection_prompt("en")
        
        if info_prompt_he and info_prompt_en:
            print("Info collection prompts: PASS")
        else:
            print("Info collection prompts: FAIL")
            return False
        
        # Test QA prompt
        qa_prompt_he = get_qa_prompt("he")
        qa_prompt_en = get_qa_prompt("en")
        
        if qa_prompt_he and qa_prompt_en:
            print("QA prompts: PASS")
        else:
            print("QA prompts: FAIL")
            return False
        
        print("Prompts test: PASS")
        return True
        
    except Exception as e:
        print(f"Prompts test failed: {e}")
        return False

def test_models():
    """Test Pydantic models"""
    print("\nTesting models...")
    
    try:
        from models import ChatRequest, ChatResponse
        
        # Test ChatRequest model
        test_request = ChatRequest(
            message="Hello",
            user_info=None,
            conversation_history=[],
            phase="info_collection",
            language="en"
        )
        
        if test_request.message == "Hello":
            print("ChatRequest model: PASS")
        else:
            print("ChatRequest model: FAIL")
            return False
        
        # Test ChatResponse model
        test_response = ChatResponse(
            response="Hello there!",
            phase="info_collection",
            user_info_complete=False
        )
        
        if test_response.response == "Hello there!":
            print("ChatResponse model: PASS")
        else:
            print("ChatResponse model: FAIL")
            return False
        
        print("Models test: PASS")
        return True
        
    except Exception as e:
        print(f"Models test failed: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        from config import validate_configuration
        
        # Test configuration validation
        is_valid = validate_configuration()
        if isinstance(is_valid, bool):
            print("Configuration validation: PASS")
        else:
            print("Configuration validation: FAIL")
            return False
        
        print("Config test: PASS")
        return True
        
    except Exception as e:
        print(f"Config test failed: {e}")
        return False

def run_all_tests():
    """Run all system tests"""
    print("Starting Medical Services ChatBot System Tests\n")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("RAG Knowledge Base", test_rag_knowledge_base),
        ("Utility Functions", test_utils_functions),
        ("Prompts", test_prompts),
        ("Models", test_models),
        ("Configuration", test_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                print(f"{test_name} PASSED\n")
                passed += 1
            else:
                print(f"{test_name} FAILED\n")
        except Exception as e:
            print(f"{test_name} FAILED with exception: {e}\n")
            traceback.print_exc()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! System is ready.")
        return True
    else:
        print(f"{total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
