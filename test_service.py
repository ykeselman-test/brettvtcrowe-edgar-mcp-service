#!/usr/bin/env python3
"""
Simple test script for EdgarTools service
Run this to verify the service is working correctly
"""

import requests
import json
import sys

SERVICE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{SERVICE_URL}/health")
        print(f"✅ Health Check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_business_description():
    """Test business description extraction"""
    try:
        payload = {
            "cik": "0001318605",  # Tesla
            "form_type": "10-K"
        }
        response = requests.post(f"{SERVICE_URL}/extract/business-description", 
                               json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Business Description: {data['company_name']}")
            print(f"   Description length: {len(data['description'])} characters")
            print(f"   Source: {data['source']}")
            return True
        else:
            print(f"❌ Business Description Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Business Description Error: {e}")
        return False

def test_risk_factors():
    """Test risk factors extraction"""
    try:
        payload = {
            "cik": "0000320193",  # Apple
            "form_type": "10-K"
        }
        response = requests.post(f"{SERVICE_URL}/extract/risk-factors", 
                               json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Risk Factors: {data['company_name']}")
            print(f"   Risk factors found: {len(data['risk_factors'])}")
            if data['risk_factors']:
                print(f"   First risk category: {data['risk_factors'][0].get('category', 'N/A')}")
            return True
        else:
            print(f"❌ Risk Factors Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Risk Factors Error: {e}")
        return False

def main():
    print("🔧 Testing EdgarTools Service...")
    print(f"Service URL: {SERVICE_URL}")
    print("-" * 50)
    
    tests = [
        test_health,
        test_business_description, 
        test_risk_factors
    ]
    
    results = []
    for test in tests:
        print()
        result = test()
        results.append(result)
    
    print()
    print("-" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed! ({passed}/{total})")
        sys.exit(0)
    else:
        print(f"❌ {total - passed} tests failed. ({passed}/{total})")
        sys.exit(1)

if __name__ == "__main__":
    main()