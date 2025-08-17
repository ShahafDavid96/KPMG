"""
Healthcare Chatbot Test Suite Package
Contains comprehensive tests for RAG context retrieval, phases, and system functionality
"""

__version__ = "1.0.0"
__author__ = "KPMG Healthcare Chatbot Team"

# Import all test functions for easy access
from .test_rag_context import test_rag_context_retrieval, test_context_accuracy
from .test_information_collection import test_information_collection_phase
from .test_qa_phase import test_qa_phase
from .test_phase_transitions import test_phase_transitions
from .test_multi_user_connection import (
    test_single_user_connection,
    test_concurrent_user_connections,
    test_session_management,
    test_load_performance,
    test_connection_stability
)
from .test_all import run_all_tests, run_quick_test

__all__ = [
    'test_rag_context_retrieval',
    'test_context_accuracy',
    'test_information_collection_phase', 
    'test_qa_phase',
    'test_phase_transitions',
    'test_single_user_connection',
    'test_concurrent_user_connections',
    'test_session_management',
    'test_load_performance',
    'test_connection_stability',
    'run_all_tests',
    'run_quick_test'
]
