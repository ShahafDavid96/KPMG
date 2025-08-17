# Healthcare Chatbot Test Suite
This directory contains comprehensive tests for the Healthcare Chatbot system, covering all critical aspects from basic functionality to multi-user performance.

## Complete Testing Strategy (5 Categories)

### 1. Syntax Error Testing
- **Purpose**: Catch basic syntax issues and import problems
- **Tests**: Quick smoke test, basic imports, system initialization
- **File**: `test_all.py --quick`

### 2. Information Collection Testing
- **Purpose**: Validate user data extraction and completeness checking
- **Tests**: Empty conversations, partial info, complete info, multi-language support
- **File**: `test_information_collection.py`

### 3. Q&A Phase Testing
- **Purpose**: Test question-answering with RAG context integration
- **Tests**: Basic Q&A, HMO-specific responses, bilingual support, prompt generation
- **File**: `test_qa_phase.py`

### 4. RAG Retrieve Right Chunk Testing
- **Purpose**: Ensure accurate context retrieval and prevent hallucination
- **Tests**: HMO-specific accuracy, service-specific validation, chunk structure (18 chunks)
- **File**: `test_rag_context.py`

### 5. Multi-User Connection Testing
- **Purpose**: Validate system performance under load and concurrent usage
- **Tests**: Single user, concurrent connections, session management, load performance, stability
- **File**: `test_multi_user_connection.py`

## Test Structure

### Individual Test Files

1. **`test_rag_context.py`** - Tests RAG knowledge base search and retrieval
   - Basic search functionality
   - Language-specific search (Hebrew/English)
   - Context relevance validation
   - Top-K parameter testing
   - Service type coverage
   - Context Retrieval Accuracy Testing
     - HMO-specific retrieval validation
     - Service-specific retrieval validation
     - Cross-language retrieval accuracy
     - Chunk structure validation (18 chunks: 6 services × 3 HMOs)
     - Specific chunk retrieval validation
     - Relevance scoring validation

2. **`test_information_collection.py`** - Tests user information collection phase
   - Empty conversation handling
   - Partial information detection
   - Complete information validation
   - Hebrew language support
   - Mixed language conversations
   - Information extraction accuracy

3. **`test_qa_phase.py`** - Tests Q&A phase with RAG context
   - Basic Q&A with context
   - HMO-specific Q&A
   - Insurance tier specific Q&A
   - Bilingual support
   - Service-specific Q&A
   - Prompt generation for different phases
   - Context relevance scoring

4. **`test_phase_transitions.py`** - Tests phase transitions
   - Information collection → Q&A transitions
   - Partial information handling
   - Complete information detection
   - Hebrew conversation transitions
   - Mixed language transitions
   - Edge case handling

5. **`test_multi_user_connection.py`** - Tests multi-user scenarios
   - Single user connection validation
   - Concurrent user connections (5 simultaneous users)
   - Session management and isolation
   - Load performance testing
   - Connection stability over time

### Comprehensive Test Runner

6. **`test_all.py`** - Runs all tests and provides comprehensive reporting
   - Individual test execution
   - Performance timing
   - Success rate calculation
   - System health assessment
   - Detailed recommendations
   - Quick smoke test option

## Usage

### Run All Tests (Complete 5-Category Testing)
```bash
cd healthcare_chatbot_src/tests
python test_all.py
```

### Run Individual Test Categories
```bash
# 1. Syntax Error Testing (Quick)
python test_all.py --quick

# 2. Information Collection Testing
python test_information_collection.py

# 3. Q&A Phase Testing
python test_qa_phase.py

# 4. RAG Context Accuracy Testing
python test_rag_context.py

# 5. Multi-User Connection Testing
python test_multi_user_connection.py
```

### Run Tests from Parent Directory
```bash
cd healthcare_chatbot_src
python -m tests.test_all
python -m tests.test_multi_user_connection
```

## Test Output

Each test provides:
- PASS - Test completed successfully
- FAIL - Test failed (check output for details)
- CRASH - Test crashed with an error

The comprehensive test runner provides:
- Individual test results with timing
- Success rate percentage
- Performance analysis
- System health assessment
- Specific recommendations for failed tests

## Test Requirements

- Virtual environment activated
- All dependencies installed (`pip install -r requirements.txt`)
- Azure services configured (for RAG functionality)
- Healthcare data files present in `healthcare_chatbot_data/`

## Test Coverage

### RAG System
- Vector search functionality
- Language support (Hebrew/English)
- Context relevance
- Top-K parameter handling
- Service type coverage
- Context Retrieval Accuracy
  - HMO-Specific Retrieval: Ensures queries for "Maccabi dental" return Maccabi-specific content
  - Service-Specific Retrieval: Validates that dental queries return dental-related chunks
  - Cross-Language Accuracy: Tests Hebrew/English query matching
  - Chunk Structure Validation: Verifies exactly 18 chunks (6 services × 3 HMOs)
  - Specific Chunk Retrieval: Tests each service-HMO combination
  - Relevance Scoring: Validates that specific queries return more targeted results

### Information Collection
- User data extraction
- Completeness validation
- Multi-language support
- Edge case handling
- Accuracy validation

### Q&A System
- Context integration
- Personalized responses
- HMO-specific information
- Insurance tier handling
- Bilingual support

### Multi-User System
- Single user connections
- Concurrent user handling (5+ users)
- Session isolation
- Load performance
- Connection stability

## Performance Expectations

- RAG Tests: 2-5 seconds (depends on Azure service response time)
- Context Accuracy Tests: 3-8 seconds (comprehensive validation)
- Information Collection: 0.1-0.5 seconds
- Q&A Tests: 1-3 seconds
- Phase Transitions: 0.1-0.3 seconds
- Multi-User Tests: 5-15 seconds (concurrent processing)
- Total Suite: 15-35 seconds

## Why These 5 Categories Matter

### 1. Syntax Error Testing
- Prevents deployment failures by catching basic issues before they reach production
- Provides fast feedback on system startup capability
- Ensures all dependencies are properly configured

### 2. Information Collection Testing
- Ensures users can provide information correctly
- Validates that extracted information is accurate and complete
- Tests Hebrew/English functionality

### 3. Q&A Phase Testing
- Tests the main chatbot capability
- Ensures AI responses use retrieved context
- Validates HMO-specific and user-specific responses

### 4. RAG Context Accuracy Testing
- Prevents hallucination by ensuring AI responses are based on actual data
- Maintains data integrity with the 18-chunk structure (6 services × 3 HMOs)
- Tests that queries return appropriate information

### 5. Multi-User Connection Testing
- Ensures system can handle real-world usage
- Tests system performance under load and concurrent access
- Validates connection reliability over time

This comprehensive testing approach ensures the healthcare chatbot provides accurate, relevant, and trustworthy information to users while maintaining performance and stability under real-world conditions.
