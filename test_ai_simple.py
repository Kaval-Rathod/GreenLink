#!/usr/bin/env python3
"""
Simple AI Integration Test
Tests the AI service integration without requiring local OpenCV
"""

import requests
import json

# API base URLs
BACKEND_URL = "http://localhost:8000"
AI_SERVICE_URL = "http://localhost:8001"

def test_ai_service():
    """Test AI service directly"""
    print("🔍 Testing AI Service...")
    
    # Test health
    response = requests.get(f"{AI_SERVICE_URL}/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ AI Service Health: {data['status']}")
        print(f"   GPU Available: {data['gpu_available']}")
        print(f"   Device: {data['device']}")
    else:
        print(f"❌ AI Service Health Failed: {response.status_code}")
        return False
    
    # Test status
    response = requests.get(f"{AI_SERVICE_URL}/status")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ AI Service Status:")
        print(f"   Version: {data['version']}")
        print(f"   GPU Name: {data['gpu_info']['name']}")
        print(f"   GPU Memory: {data['gpu_info']['memory_total'] / 1024**3:.1f} GB")
    else:
        print(f"❌ AI Service Status Failed: {response.status_code}")
        return False
    
    return True

def test_backend_ai_integration():
    """Test backend AI integration"""
    print("\n🔄 Testing Backend AI Integration...")
    
    # Test backend AI status
    response = requests.get(f"{BACKEND_URL}/ai-status")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Backend AI Status:")
        print(f"   Service: {data['service']}")
        print(f"   Version: {data['version']}")
        print(f"   GPU Available: {data['gpu_available']}")
        print(f"   GPU Name: {data['gpu_info']['name']}")
    else:
        print(f"❌ Backend AI Status Failed: {response.status_code}")
        return False
    
    return True

def test_backend_health():
    """Test backend health"""
    print("\n🌐 Testing Backend Health...")
    
    response = requests.get(f"{BACKEND_URL}/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Backend Health: {data['message']}")
    else:
        print(f"❌ Backend Health Failed: {response.status_code}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 GreenLink Phase 2 - AI Integration Test")
    print("=" * 50)
    
    # Test AI service
    ai_ok = test_ai_service()
    
    # Test backend health
    backend_ok = test_backend_health()
    
    # Test backend AI integration
    integration_ok = test_backend_ai_integration()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   AI Service: {'✅ PASS' if ai_ok else '❌ FAIL'}")
    print(f"   Backend Health: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"   AI Integration: {'✅ PASS' if integration_ok else '❌ FAIL'}")
    
    if ai_ok and backend_ok and integration_ok:
        print("\n🎉 All tests passed! Phase 2 is working!")
        print(f"🌐 Backend API: {BACKEND_URL}")
        print(f"🤖 AI Service: {AI_SERVICE_URL}")
        print(f"📚 Backend Docs: {BACKEND_URL}/docs")
        print(f"📚 AI Service Docs: {AI_SERVICE_URL}/docs")
    else:
        print("\n❌ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main() 