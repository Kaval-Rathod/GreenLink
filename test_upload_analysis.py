#!/usr/bin/env python3
"""
Test Upload and AI Analysis
Uploads an image and tests the AI analysis functionality
"""

import requests
import json
import os
from PIL import Image
import numpy as np

# API base URLs
BACKEND_URL = "http://localhost:8000"
AI_SERVICE_URL = "http://localhost:8001"

def create_test_image():
    """Create a simple test image with greenery"""
    print("🖼️ Creating test image...")
    
    # Create a 400x300 image with some green areas
    img = np.zeros((300, 400, 3), dtype=np.uint8)
    
    # Add green areas (simulating vegetation)
    img[50:150, 50:200] = [0, 255, 0]  # Bright green rectangle
    img[180:250, 250:350] = [0, 200, 0]  # Darker green rectangle
    
    # Save the image
    test_image = Image.fromarray(img)
    test_image.save("test_greenery.jpg")
    print("✅ Test image created: test_greenery.jpg")
    return "test_greenery.jpg"

def test_ai_service_direct():
    """Test AI service directly with image upload"""
    print("\n🔬 Testing AI Service Direct Analysis...")
    
    image_path = create_test_image()
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": ("test_greenery.jpg", f, "image/jpeg")}
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
    finally:
        # Clean up
        if os.path.exists(image_path):
            os.remove(image_path)

def test_backend_upload_analysis():
    """Test full backend upload and analysis workflow"""
    print("\n🔄 Testing Backend Upload & Analysis...")
    
    # First, try to login with existing user
    login_data = {
        "username": "farmer@test.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BACKEND_URL}/token", data=login_data)
    if response.status_code != 200:
        print("❌ Login failed. Creating new user...")
        
        # Create new user
        user_data = {
            "name": "Test Farmer",
            "email": "farmer2@test.com",
            "password": "testpass123"
        }
        response = requests.post(f"{BACKEND_URL}/users", json=user_data)
        if response.status_code != 201:
            print(f"❌ User creation failed: {response.text}")
            return False
        
        # Login with new user
        login_data = {
            "username": "farmer2@test.com",
            "password": "testpass123"
        }
        response = requests.post(f"{BACKEND_URL}/token", data=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return False
    
    token_data = response.json()
    token = token_data["access_token"]
    print("✅ Login successful")
    
    # Create test image
    image_path = create_test_image()
    
    # Upload image
    headers = {"Authorization": f"Bearer {token}"}
    with open(image_path, "rb") as f:
        files = {"file": ("test_greenery.jpg", f, "image/jpeg")}
        data = {"latitude": 40.7128, "longitude": -74.0060}
        response = requests.post(f"{BACKEND_URL}/upload", headers=headers, files=files, data=data)
    
    if response.status_code != 201:
        print(f"❌ Upload failed: {response.text}")
        return False
    
    submission = response.json()
    print(f"✅ Upload successful: Submission ID {submission['id']}")
    
    # Analyze with AI
    response = requests.post(f"{BACKEND_URL}/analyze/{submission['id']}", headers=headers)
    if response.status_code != 200:
        print(f"❌ Analysis failed: {response.text}")
        return False
    
    analysis_result = response.json()
    print("✅ Backend AI Analysis complete:")
    print(f"   Greenery: {analysis_result['greenery_pct']}%")
    print(f"   Carbon Value: {analysis_result['carbon_value']} tonnes CO2")
    
    # Clean up
    if os.path.exists(image_path):
        os.remove(image_path)
    
    return True

def main():
    """Run all tests"""
    print("🚀 GreenLink Phase 2 - Upload & Analysis Test")
    print("=" * 60)
    
    # Test AI service directly
    ai_ok = test_ai_service_direct()
    
    # Test backend integration
    backend_ok = test_backend_upload_analysis()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   AI Service Direct: {'✅ PASS' if ai_ok else '❌ FAIL'}")
    print(f"   Backend Integration: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    
    if ai_ok and backend_ok:
        print("\n🎉 All tests passed! Your AI integration is working perfectly!")
        print("\n🌐 You can now:")
        print("   1. Visit http://localhost:8000/docs to see the API")
        print("   2. Visit http://localhost:8001/docs to see the AI service")
        print("   3. Upload images and get real AI analysis!")
    else:
        print("\n❌ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main() 