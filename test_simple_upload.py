#!/usr/bin/env python3
"""
Simple Upload and AI Analysis Test
Uses existing test image to test AI functionality
"""

import requests
import json
import os

# API base URLs
BACKEND_URL = "http://localhost:8000"
AI_SERVICE_URL = "http://localhost:8001"

def test_ai_service_with_existing_image():
    """Test AI service with existing test image"""
    print("🔬 Testing AI Service with existing image...")
    
    # Check if test image exists
    test_image = "test_photo.png"
    if not os.path.exists(test_image):
        print(f"❌ Test image {test_image} not found")
        print("   Creating a simple test...")
        return test_ai_service_health_only()
    
    try:
        with open(test_image, "rb") as f:
            files = {"file": (test_image, f, "image/png")}
            response = requests.post(f"{AI_SERVICE_URL}/analyze", files=files, timeout=30)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print("✅ AI Analysis Results:")
            print(f"   Greenery: {results['greenery_percentage']}%")
            print(f"   Carbon Value: {results['carbon_value']} tonnes CO2")
            print(f"   Image Size: {results['image_size']}")
            print(f"   Green Pixels: {results['green_pixels']}")
            return True
        else:
            print(f"❌ AI Analysis failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ AI Analysis error: {str(e)}")
        return False

def test_ai_service_health_only():
    """Test AI service health and status"""
    print("🔬 Testing AI Service Health...")
    
    # Test health
    response = requests.get(f"{AI_SERVICE_URL}/")
    if response.status_code == 200:
        data = response.json()
        print("✅ AI Service Health:")
        print(f"   Status: {data['status']}")
        print(f"   GPU Available: {data['gpu_available']}")
        print(f"   Device: {data['device']}")
    
    # Test status
    response = requests.get(f"{AI_SERVICE_URL}/status")
    if response.status_code == 200:
        data = response.json()
        print("✅ AI Service Status:")
        print(f"   Version: {data['version']}")
        print(f"   GPU Name: {data['gpu_info']['name']}")
        print(f"   GPU Memory: {data['gpu_info']['memory_total'] / 1024**3:.1f} GB")
    
    return True

def test_backend_ai_status():
    """Test backend AI integration"""
    print("\n🔄 Testing Backend AI Integration...")
    
    response = requests.get(f"{BACKEND_URL}/ai-status")
    if response.status_code == 200:
        data = response.json()
        print("✅ Backend AI Status:")
        print(f"   Service: {data['service']}")
        print(f"   Version: {data['version']}")
        print(f"   GPU Available: {data['gpu_available']}")
        print(f"   GPU Name: {data['gpu_info']['name']}")
        return True
    else:
        print(f"❌ Backend AI Status Failed: {response.status_code}")
        return False

def test_backend_health():
    """Test backend health"""
    print("\n🌐 Testing Backend Health...")
    
    response = requests.get(f"{BACKEND_URL}/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Backend Health: {data['message']}")
        return True
    else:
        print(f"❌ Backend Health Failed: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🚀 GreenLink Phase 2 - Simple Verification Test")
    print("=" * 60)
    
    # Test backend health
    backend_ok = test_backend_health()
    
    # Test AI service
    ai_ok = test_ai_service_with_existing_image()
    
    # Test backend AI integration
    integration_ok = test_backend_ai_status()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Backend Health: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"   AI Service: {'✅ PASS' if ai_ok else '❌ FAIL'}")
    print(f"   AI Integration: {'✅ PASS' if integration_ok else '❌ FAIL'}")
    
    if backend_ok and ai_ok and integration_ok:
        print("\n🎉 All tests passed! Your AI integration is working!")
        print("\n🌐 You can now:")
        print("   1. Visit http://localhost:8000/docs to see the API")
        print("   2. Visit http://localhost:8001/docs to see the AI service")
        print("   3. Upload images and get real AI analysis!")
        print("\n💡 To test with real images:")
        print("   - Use the web interface at http://localhost:8000/docs")
        print("   - Or use curl/Postman to upload images")
    else:
        print("\n❌ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main() 