#!/usr/bin/env python3
"""
Multi-User Load Testing for Medical Services ChatBot
Tests concurrent user requests to evaluate server performance
"""

import asyncio
import aiohttp
import time
import json
import random
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import threading
from datetime import datetime
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

class MultiUserLoadTester:
    """Load testing class for multiple concurrent users"""
    
    def __init__(self, base_url: str = "http://localhost:8000", max_workers: int = 10):
        self.base_url = base_url
        self.max_workers = max_workers
        self.results = []
        self.lock = threading.Lock()
        
        # Sample user data for testing
        self.sample_users = [
            {
                "name": "Alice Johnson",
                "id_number": "123456789",
                "gender": "female",
                "age": "32",
                "hmo_name": "Maccabi",
                "hmo_card_number": "987654321",
                "insurance_tier": "Gold"
            },
            {
                "name": "Bob Smith",
                "id_number": "234567890",
                "gender": "male",
                "age": "28",
                "hmo_name": "Clalit",
                "hmo_card_number": "876543210",
                "insurance_tier": "Silver"
            },
            {
                "name": "Carol Davis",
                "id_number": "345678901",
                "gender": "female",
                "age": "45",
                "hmo_name": "Meuhedet",
                "hmo_card_number": "765432109",
                "insurance_tier": "Bronze"
            },
            {
                "name": "David Wilson",
                "id_number": "456789012",
                "gender": "male",
                "age": "39",
                "hmo_name": "Maccabi",
                "hmo_card_number": "654321098",
                "insurance_tier": "Gold"
            },
            {
                "name": "Eva Brown",
                "id_number": "567890123",
                "gender": "female",
                "age": "26",
                "hmo_name": "Clalit",
                "hmo_card_number": "543210987",
                "insurance_tier": "Silver"
            }
        ]
        
        # Sample questions for testing
        self.sample_questions = [
            "What dental services are available?",
            "Tell me about alternative medicine options",
            "What are the benefits of Gold insurance?",
            "How can I schedule an appointment?",
            "What's covered in basic insurance?",
            "איזה שירותי שיניים זמינים?",
            "מה ההטבות של ביטוח זהב?",
            "איך אני יכול לקבוע תור?",
            "מה מכוסה בביטוח בסיסי?",
            "תן לי מידע על רפואה משלימה"
        ]
    
    async def test_health_endpoint(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test the health endpoint"""
        try:
            start_time = time.time()
            async with session.get(f"{self.base_url}/api/v1/health") as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    return {
                        "endpoint": "health",
                        "status": "success",
                        "response_time": response_time,
                        "status_code": response.status,
                        "data": data
                    }
                else:
                    return {
                        "endpoint": "health",
                        "status": "error",
                        "response_time": response_time,
                        "status_code": response.status,
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "endpoint": "health",
                "status": "error",
                "response_time": 0,
                "status_code": 0,
                "error": str(e)
            }
    
    async def test_chat_endpoint(self, session: aiohttp.ClientSession, user_id: int, 
                                phase: str = "info_collection", language: str = "en") -> Dict[str, Any]:
        """Test the chat endpoint with a specific user"""
        try:
            # Prepare user data
            user_data = self.sample_users[user_id % len(self.sample_users)]
            
            # Create conversation history based on phase
            if phase == "info_collection":
                # Simulate user providing information
                message = f"My name is {user_data['name']}, I'm {user_data['age']} years old, {user_data['gender']}, ID {user_data['id_number']}, HMO {user_data['hmo_name']}, card {user_data['hmo_card_number']}, insurance {user_data['insurance_tier']}"
                conversation_history = []
            else:
                # QA phase - use sample questions
                message = random.choice(self.sample_questions)
                conversation_history = [
                    {
                        "role": "user",
                        "content": f"My name is {user_data['name']}, I'm {user_data['age']} years old, {user_data['gender']}, ID {user_data['id_number']}, HMO {user_data['hmo_name']}, card {user_data['hmo_card_number']}, insurance {user_data['insurance_tier']}",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "role": "assistant",
                        "content": "Information collected successfully. How can I help you?",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            
            # Prepare request payload
            payload = {
                "message": message,
                "user_info": None,
                "conversation_history": conversation_history,
                "phase": phase,
                "language": language
            }
            
            # Make request
            start_time = time.time()
            async with session.post(f"{self.base_url}/api/v1/chat", json=payload) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "user_id": user_id,
                        "endpoint": "chat",
                        "phase": phase,
                        "language": language,
                        "status": "success",
                        "response_time": response_time,
                        "status_code": response.status,
                        "response_length": len(data.get("response", "")),
                        "phase_returned": data.get("phase", ""),
                        "user_info_complete": data.get("user_info_complete", False)
                    }
                else:
                    error_text = await response.text()
                    return {
                        "user_id": user_id,
                        "endpoint": "chat",
                        "phase": phase,
                        "language": language,
                        "status": "error",
                        "response_time": response_time,
                        "status_code": response.status,
                        "error": error_text
                    }
                    
        except Exception as e:
            return {
                "user_id": user_id,
                "endpoint": "chat",
                "phase": phase,
                "language": language,
                "status": "error",
                "response_time": 0,
                "status_code": 0,
                "error": str(e)
            }
    
    async def test_single_user_session(self, session: aiohttp.ClientSession, user_id: int) -> List[Dict[str, Any]]:
        """Test a complete user session (info collection + QA)"""
        results = []
        
        # Test info collection phase
        info_result = await self.test_chat_endpoint(session, user_id, "info_collection", "en")
        results.append(info_result)
        
        # Wait a bit between requests
        await asyncio.sleep(0.1)
        
        # Test QA phase
        qa_result = await self.test_chat_endpoint(session, user_id, "qa", "en")
        results.append(qa_result)
        
        # Wait a bit between requests
        await asyncio.sleep(0.1)
        
        # Test Hebrew language
        hebrew_result = await self.test_chat_endpoint(session, user_id, "qa", "he")
        results.append(hebrew_result)
        
        return results
    
    async def run_concurrent_test(self, num_users: int, test_type: str = "mixed") -> Dict[str, Any]:
        """Run concurrent load test with multiple users"""
        print(f"Starting concurrent load test with {num_users} users...")
        print(f"Test type: {test_type}")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test health endpoint first
        async with aiohttp.ClientSession() as session:
            health_result = await self.test_health_endpoint(session)
            print(f"Health Check: {health_result['status']} ({health_result['response_time']:.3f}s)")
            
            if health_result['status'] != 'success':
                print("Health check failed. Server may not be running.")
                return {"error": "Health check failed"}
        
        # Run concurrent tests
        async with aiohttp.ClientSession() as session:
            if test_type == "health_only":
                # Test only health endpoint with many concurrent requests
                tasks = [self.test_health_endpoint(session) for _ in range(num_users)]
                results = await asyncio.gather(*tasks)
                
            elif test_type == "info_collection_only":
                # Test only info collection phase
                tasks = [self.test_chat_endpoint(session, i, "info_collection", "en") 
                        for i in range(num_users)]
                results = await asyncio.gather(*tasks)
                
            elif test_type == "qa_only":
                # Test only QA phase
                tasks = [self.test_chat_endpoint(session, i, "qa", "en") 
                        for i in range(num_users)]
                results = await asyncio.gather(*tasks)
                
            elif test_type == "mixed":
                # Test mixed scenarios
                tasks = []
                for i in range(num_users):
                    if i % 3 == 0:
                        # Info collection
                        tasks.append(self.test_chat_endpoint(session, i, "info_collection", "en"))
                    elif i % 3 == 1:
                        # QA English
                        tasks.append(self.test_chat_endpoint(session, i, "qa", "en"))
                    else:
                        # QA Hebrew
                        tasks.append(self.test_chat_endpoint(session, i, "qa", "he"))
                
                results = await asyncio.gather(*tasks)
                
            elif test_type == "full_session":
                # Test complete user sessions
                tasks = [self.test_single_user_session(session, i) for i in range(num_users)]
                session_results = await asyncio.gather(*tasks)
                results = [item for sublist in session_results for item in sublist]
            
            else:
                print(f"Unknown test type: {test_type}")
                return {"error": f"Unknown test type: {test_type}"}
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        analysis = self.analyze_results(results, total_time, num_users)
        
        return analysis
    
    def analyze_results(self, results: List[Dict[str, Any]], total_time: float, num_users: int) -> Dict[str, Any]:
        """Analyze test results and generate statistics"""
        
        # Separate successful and failed requests
        successful = [r for r in results if r.get('status') == 'success']
        failed = [r for r in results if r.get('status') != 'success']
        
        # Response time statistics
        response_times = [r.get('response_time', 0) for r in successful if r.get('response_time', 0) > 0]
        
        analysis = {
            "test_summary": {
                "total_users": num_users,
                "total_requests": len(results),
                "successful_requests": len(successful),
                "failed_requests": len(failed),
                "success_rate": (len(successful) / len(results) * 100) if results else 0,
                "total_test_time": total_time,
                "requests_per_second": len(results) / total_time if total_time > 0 else 0
            },
            "performance_metrics": {
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "median_response_time": statistics.median(response_times) if response_times else 0,
                "response_time_95th_percentile": self.percentile(response_times, 95) if response_times else 0,
                "response_time_99th_percentile": self.percentile(response_times, 99) if response_times else 0
            },
            "endpoint_breakdown": self.breakdown_by_endpoint(results),
            "phase_breakdown": self.breakdown_by_phase(results),
            "language_breakdown": self.breakdown_by_language(results),
            "error_analysis": self.analyze_errors(failed),
            "detailed_results": results
        }
        
        return analysis
    
    def breakdown_by_endpoint(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Break down results by endpoint"""
        endpoints = {}
        for result in results:
            endpoint = result.get('endpoint', 'unknown')
            if endpoint not in endpoints:
                endpoints[endpoint] = {"total": 0, "success": 0, "failed": 0, "response_times": []}
            
            endpoints[endpoint]["total"] += 1
            if result.get('status') == 'success':
                endpoints[endpoint]["success"] += 1
                if result.get('response_time'):
                    endpoints[endpoint]["response_times"].append(result['response_time'])
            else:
                endpoints[endpoint]["failed"] += 1
        
        # Calculate averages
        for endpoint in endpoints:
            if endpoints[endpoint]["response_times"]:
                endpoints[endpoint]["avg_response_time"] = statistics.mean(endpoints[endpoint]["response_times"])
            else:
                endpoints[endpoint]["avg_response_time"] = 0
        
        return endpoints
    
    def breakdown_by_phase(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Break down results by phase"""
        phases = {}
        for result in results:
            if 'phase' in result:
                phase = result['phase']
                if phase not in phases:
                    phases[phase] = {"total": 0, "success": 0, "failed": 0, "response_times": []}
                
                phases[phase]["total"] += 1
                if result.get('status') == 'success':
                    phases[phase]["success"] += 1
                    if result.get('response_time'):
                        phases[phase]["response_times"].append(result['response_time'])
                else:
                    phases[phase]["failed"] += 1
        
        # Calculate averages
        for phase in phases:
            if phases[phase]["response_times"]:
                phases[phase]["avg_response_time"] = statistics.mean(phases[phase]["response_times"])
            else:
                phases[phase]["avg_response_time"] = 0
        
        return phases
    
    def breakdown_by_language(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Break down results by language"""
        languages = {}
        for result in results:
            if 'language' in result:
                lang = result['language']
                if lang not in languages:
                    languages[lang] = {"total": 0, "success": 0, "failed": 0, "response_times": []}
                
                languages[lang]["total"] += 1
                if result.get('status') == 'success':
                    languages[lang]["success"] += 1
                    if result.get('response_time'):
                        languages[lang]["response_times"].append(result['response_time'])
                else:
                    languages[lang]["failed"] += 1
        
        # Calculate averages
        for lang in languages:
            if languages[lang]["response_times"]:
                languages[lang]["avg_response_time"] = statistics.mean(languages[lang]["response_times"])
            else:
                languages[lang]["avg_response_time"] = 0
        
        return languages
    
    def analyze_errors(self, failed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze failed requests"""
        error_types = {}
        status_codes = {}
        
        for result in failed_results:
            error = result.get('error', 'unknown_error')
            status_code = result.get('status_code', 0)
            
            if error not in error_types:
                error_types[error] = 0
            error_types[error] += 1
            
            if status_code not in status_codes:
                status_codes[status_code] = 0
            status_codes[status_code] += 1
        
        return {
            "error_types": error_types,
            "status_codes": status_codes,
            "total_errors": len(failed_results)
        }
    
    def percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def print_results(self, analysis: Dict[str, Any]):
        """Print formatted test results"""
        print("\n" + "=" * 60)
        print("LOAD TEST RESULTS")
        print("=" * 60)
        
        # Test Summary
        summary = analysis["test_summary"]
        print(f"Test Summary:")
        print(f"   Total Users: {summary['total_users']}")
        print(f"   Total Requests: {summary['total_requests']}")
        print(f"   Successful: {summary['successful_requests']}")
        print(f"   Failed: {summary['failed_requests']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        print(f"   Total Time: {summary['total_test_time']:.2f}s")
        print(f"   Requests/Second: {summary['requests_per_second']:.2f}")
        
        # Performance Metrics
        perf = analysis["performance_metrics"]
        print(f"\nPerformance Metrics:")
        print(f"   Min Response Time: {perf['min_response_time']:.3f}s")
        print(f"   Max Response Time: {perf['max_response_time']:.3f}s")
        print(f"   Average Response Time: {perf['avg_response_time']:.3f}s")
        print(f"   Median Response Time: {perf['median_response_time']:.3f}s")
        print(f"   95th Percentile: {perf['response_time_95th_percentile']:.3f}s")
        print(f"   99th Percentile: {perf['response_time_99th_percentile']:.3f}s")
        
        # Endpoint Breakdown
        endpoints = analysis["endpoint_breakdown"]
        print(f"\nEndpoint Breakdown:")
        for endpoint, stats in endpoints.items():
            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"   {endpoint}: {stats['total']} requests, {success_rate:.1f}% success, {stats['avg_response_time']:.3f}s avg")
        
        # Phase Breakdown
        phases = analysis["phase_breakdown"]
        if phases:
            print(f"\nPhase Breakdown:")
            for phase, stats in phases.items():
                success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"   {phase}: {stats['total']} requests, {success_rate:.1f}% success, {stats['avg_response_time']:.3f}s avg")
        
        # Language Breakdown
        languages = analysis["language_breakdown"]
        if languages:
            print(f"\nLanguage Breakdown:")
            for lang, stats in languages.items():
                success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"   {lang}: {stats['total']} requests, {success_rate:.1f}% success, {stats['avg_response_time']:.3f}s avg")
        
        # Error Analysis
        errors = analysis["error_analysis"]
        if errors["total_errors"] > 0:
            print(f"\nError Analysis:")
            print(f"   Total Errors: {errors['total_errors']}")
            print(f"   Error Types: {errors['error_types']}")
            print(f"   Status Codes: {errors['status_codes']}")
        
        print("\n" + "=" * 60)

async def main():
    """Main function to run load tests"""
    print("Medical Services ChatBot - Multi-User Load Testing")
    print("=" * 60)
    
    # Initialize tester
    tester = MultiUserLoadTester()
    
    # Test scenarios
    test_scenarios = [
        {"name": "Health Check Only", "type": "health_only", "users": 50},
        {"name": "Info Collection Phase", "type": "info_collection_only", "users": 20},
        {"name": "QA Phase Only", "type": "qa_only", "users": 20},
        {"name": "Mixed Scenarios", "type": "mixed", "users": 30},
        {"name": "Full User Sessions", "type": "full_session", "users": 15}
    ]
    
    all_results = {}
    
    for scenario in test_scenarios:
        print(f"\nRunning: {scenario['name']}")
        print(f"Users: {scenario['users']}")
        print(f"Type: {scenario['type']}")
        
        try:
            result = await tester.run_concurrent_test(scenario['users'], scenario['type'])
            all_results[scenario['name']] = result
            
            if 'error' not in result:
                tester.print_results(result)
            else:
                print(f"Test failed: {result['error']}")
                
        except Exception as e:
            print(f"Error running test: {e}")
            all_results[scenario['name']] = {"error": str(e)}
        
        # Wait between tests
        await asyncio.sleep(2)
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"load_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\nResults saved to: {filename}")
    print("\nLoad testing completed!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nLoad testing interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
