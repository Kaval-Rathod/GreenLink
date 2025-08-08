#!/usr/bin/env python3
"""
GreenLink Phase 2 Test Script
Tests the AI greenery detection integration
"""

import requests
import json
import os
import cv2
import numpy as np
from pathlib import Path

# API base URLs
BACKEND_URL = "http://localhost:8000"
AI_SERVICE_URL = "http://localhost:8001"

def test_ai_service_health():
    """Test AI service health"""
    print("🔍 Testing AI service health...")
    try:
        response = requests.get(f"{AI_SERVICE_URL}/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Service: {data['service']}")
            print(f"   GPU Available: {data['gpu_available']}")
            print(f"   Device: {data['device']}")
            return True
        else:
            print(f"❌ AI service health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ AI service unavailable: {str(e)}")
        return False

def test_ai_service_status():
    """Test AI service status with GPU info"""
    print("\n📊 Testing AI service status...")
    try:
        response = requests.get(f"{AI_SERVICE_URL}/status")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Service Status:")
            print(f"   Version: {data['version']}")
            print(f"   GPU Available: {data['gpu_available']}")
            if data['gpu_available'] and 'gpu_info' in data:
                gpu_info = data['gpu_info']
                print(f"   GPU Name: {gpu_info.get('name', 'Unknown')}")
                print(f"   GPU Memory: {gpu_info.get('memory_total', 0) / 1024**3:.1f} GB")
            return True
        else:
            print(f"❌ AI service status failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ AI service status unavailable: {str(e)}")
        return False

def create_test_images():
    """Create test images with different greenery levels"""
    print("\n🖼️ Creating test images...")
    
    test_images = []
    
    # Image 1: High greenery (forest-like)
    img1 = np.zeros((400, 600, 3), dtype=np.uint8)
    # Add green areas
    img1[50:350, 50:550] = [0, 255, 0]  # Bright green
    img1[100:300, 100:500] = [0, 200, 0]  # Darker green
    img1[150:250, 150:450] = [0, 150, 0]  # Even darker green
    cv2.imwrite("test_high_greenery.jpg", img1)
    test_images.append(("test_high_greenery.jpg", "High greenery (forest-like)"))
    
    # Image 2: Medium greenery (park-like)
    img2 = np.zeros((400, 600, 3), dtype=np.uint8)
    # Add some green areas
    img2[100:200, 100:200] = [0, 255, 0]  # Green patch
    img2[250:350, 400:500] = [0, 200, 0]  # Another green patch
    cv2.imwrite("test_medium_greenery.jpg", img2)
    test_images.append(("test_medium_greenery.jpg", "Medium greenery (park-like)"))
    
    # Image 3: Low greenery (urban-like)
    img3 = np.zeros((400, 600, 3), dtype=np.uint8)
    # Add minimal green
    img3[50:80, 50:80] = [0, 255, 0]  # Small green patch
    cv2.imwrite("test_low_greenery.jpg", img3)
    test_images.append(("test_low_greenery.jpg", "Low greenery (urban-like)"))
    
    print(f"✅ Created {len(test_images)} test images")
    return test_images

def test_ai_analysis(image_path, description):
    """Test AI analysis on a specific image"""
    print(f"\n🔬 Testing AI analysis: {description}")
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": (image_path, f, "image/jpeg")}
            response = requests.post(f"{AI_SERVICE_URL}/analyze", files=files, timeout=30)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Analysis Results:")
            print(f"   Greenery: {results['greenery_percentage']}%")
            print(f"   Carbon Value: {results['carbon_value']} tonnes CO2")
            print(f"   Image Size: {results['image_size']}")
            print(f"   Green Pixels: {results['green_pixels']}")
            return results
        else:
            print(f"❌ Analysis failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        return None

def test_backend_ai_integration():
    """Test the full backend integration with AI"""
    print("\n🔄 Testing backend AI integration...")
    
    # First, register and login a user
    user_data = {
        "name": "AI Test User",
        "email": "ai_test@example.com",
        "password": "testpass123",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    # Register user
    response = requests.post(f"{BACKEND_URL}/users", json=user_data)
    if response.status_code != 201:
        print(f"❌ User registration failed: {response.text}")
        return False
    
    user = response.json()
    print(f"✅ User created: {user['name']} (ID: {user['id']})")
    
    # Login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = requests.post(f"{BACKEND_URL}/token", data=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return False
    
    token_data = response.json()
    token = token_data["access_token"]
    print("✅ Login successful")
    
    # Upload test image
    headers = {"Authorization": f"Bearer {token}"}
    with open("test_high_greenery.jpg", "rb") as f:
        files = {"file": ("test_high_greenery.jpg", f, "image/jpeg")}
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
    print(f"✅ AI Analysis complete:")
    print(f"   Greenery: {analysis_result['greenery_pct']}%")
    print(f"   Carbon Value: {analysis_result['carbon_value']} tonnes CO2")
    
    return True

def test_backend_ai_status():
    """Test backend AI status endpoint"""
    print("\n📊 Testing backend AI status...")
    try:
        response = requests.get(f"{BACKEND_URL}/ai-status")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend AI Status:")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   GPU Available: {data.get('gpu_available', False)}")
            return True
        else:
            print(f"❌ Backend AI status failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Backend AI status unavailable: {str(e)}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...")
    test_files = [
        "test_high_greenery.jpg",
        "test_medium_greenery.jpg", 
        "test_low_greenery.jpg"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Removed {file}")
    
    print("✅ Cleanup complete")

def main():
    """Run all Phase 2 tests"""
    print("🚀 GreenLink Phase 2 - AI Integration Test Suite")
    print("=" * 60)
    
    # Test AI service health
    ai_healthy = test_ai_service_health()
    
    # Test AI service status
    test_ai_service_status()
    
    if not ai_healthy:
        print("\n❌ AI service is not available. Cannot continue with AI tests.")
        return
    
    # Create test images
    test_images = create_test_images()
    
    # Test AI analysis on each image
    print("\n" + "=" * 60)
    print("🧪 Testing AI Analysis on Different Images")
    print("=" * 60)
    
    for image_path, description in test_images:
        test_ai_analysis(image_path, description)
    
    # Test backend integration
    print("\n" + "=" * 60)
    print("🔄 Testing Backend AI Integration")
    print("=" * 60)
    
    test_backend_ai_integration()
    test_backend_ai_status()
    
    # Cleanup
    cleanup_test_files()
    
    print("\n" + "=" * 60)
    print("✅ Phase 2 Tests Completed!")
    print(f"🌐 Backend API: {BACKEND_URL}")
    print(f"🤖 AI Service: {AI_SERVICE_URL}")
    print(f"📚 Backend Docs: {BACKEND_URL}/docs")
    print(f"📚 AI Service Docs: {AI_SERVICE_URL}/docs")

if __name__ == "__main__":
    main() 