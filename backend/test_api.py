#!/usr/bin/env python3
"""
Test script for CityPulse API endpoints
Run this to verify all endpoints are working
"""

import requests
import json
import sys

# API base URL
BASE_URL = "http://localhost:5000"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"{method} {endpoint}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success")
            
            # Show sample data
            if isinstance(result, dict):
                if 'count' in result:
                    print(f"  Count: {result['count']}")
                if 'alerts' in result and isinstance(result['alerts'], list):
                    print(f"  Alerts: {len(result['alerts'])} items")
                if 'data' in result:
                    print(f"  Data: Available")
                if 'answer' in result:
                    print(f"  Answer: {result['answer'][:100]}...")
            
            return True
        else:
            print(f"✗ Failed: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection Error: Is the server running?")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all endpoint tests"""
    print("\n" + "="*60)
    print("CityPulse API Endpoint Tests")
    print("="*60)
    
    results = []
    
    # Test endpoints
    results.append(test_endpoint("GET", "/", description="API Home"))
    results.append(test_endpoint("GET", "/health", description="Health Check"))
    results.append(test_endpoint("GET", "/api/alerts", description="Get All Alerts"))
    results.append(test_endpoint("GET", "/api/alerts/safety", description="Get Safety Alerts"))
    results.append(test_endpoint("GET", "/api/community", description="Get Community Data"))
    results.append(test_endpoint("GET", "/api/safety", description="Get Safety Data"))
    results.append(test_endpoint("GET", "/api/investment", description="Get Investment Data"))
    results.append(test_endpoint("GET", "/api/permits", description="Get Permits Data"))
    results.append(test_endpoint("GET", "/api/news", description="Get News Data"))
    results.append(test_endpoint("GET", "/api/social", description="Get Social Data"))
    results.append(test_endpoint("GET", "/api/briefing", description="Get Morning Briefing"))
    results.append(test_endpoint(
        "POST", 
        "/api/voice/ask", 
        data={"question": "What are the trending topics?"},
        description="Voice Q&A"
    ))
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
