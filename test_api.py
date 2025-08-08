#!/usr/bin/env python3
"""
GreenLink API Test Script
Tests the Phase 1 endpoints: user registration, login, upload, and analysis
"""

import requests
import json
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_user_registration():
    """Test user registration"""
    print("👤 Testing user registration...")
    
    user_data = {
        "name": "Test Farmer",
        "email": "farmer@test.com",
        "password": "testpass123",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "wallet_address": "0x1234567890abcdef"
    }
    
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        user = response.json()
        print(f"✅ User created: {user['name']} (ID: {user['id']})")
        return user
    else:
        print(f"❌ Registration failed: {response.text}")
        return None

def test_user_login(email, password):
    """Test user login and get access token"""
    print("🔑 Testing user login...")
    
    login_data = {
        "username": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/token", data=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print(f"✅ Login successful, token received")
        return token_data["access_token"]
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_photo_upload(token, photo_path):
    """Test photo upload with GPS coordinates"""
    print("📸 Testing photo upload...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a simple test image if it doesn't exist
    if not os.path.exists(photo_path):
        # Create a simple 1x1 pixel PNG
        with open(photo_path, "wb") as f:
            # Minimal PNG file
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xe5\x08\x08\x10\x1d\x0c\xc8\xc8\xc8\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\x17\xdc\x8f\x00\x00\x00\x00IEND\xaeB`\x82')
    
    with open(photo_path, "rb") as f:
        files = {"file": (photo_path, f, "image/png")}
        data = {
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        
        response = requests.post(f"{BASE_URL}/upload", headers=headers, files=files, data=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            submission = response.json()
            print(f"✅ Upload successful: Submission ID {submission['id']}")
            return submission
        else:
            print(f"❌ Upload failed: {response.text}")
            return None

def test_analysis(token, submission_id):
    """Test photo analysis"""
    print(f"🔬 Testing analysis for submission {submission_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BASE_URL}/analyze/{submission_id}", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Analysis complete:")
        print(f"   - Greenery: {result['greenery_pct']}%")
        print(f"   - Carbon value: {result['carbon_value']} tonnes CO2")
        return result
    else:
        print(f"❌ Analysis failed: {response.text}")
        return None

def test_list_submissions(token):
    """Test listing user's submissions"""
    print("📋 Testing submission listing...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/submissions", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        submissions = response.json()
        print(f"✅ Found {len(submissions)} submissions")
        for sub in submissions:
            print(f"   - ID: {sub['id']}, Greenery: {sub['greenery_pct']}%, Carbon: {sub['carbon_value']}")
        return submissions
    else:
        print(f"❌ Listing failed: {response.text}")
        return None

def main():
    """Run all tests"""
    print("🚀 GreenLink API Phase 1 Test Suite")
    print("=" * 50)
    
    # Test health check
    test_health_check()
    
    # Test user registration
    user = test_user_registration()
    if not user:
        print("❌ Cannot continue without user registration")
        return
    
    # Test login
    token = test_user_login("farmer@test.com", "testpass123")
    if not token:
        print("❌ Cannot continue without login")
        return
    
    # Test photo upload
    photo_path = "test_photo.png"
    submission = test_photo_upload(token, photo_path)
    if not submission:
        print("❌ Cannot continue without photo upload")
        return
    
    # Test analysis
    analysis_result = test_analysis(token, submission["id"])
    
    # Test listing submissions
    test_list_submissions(token)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print(f"🌐 API Documentation: {BASE_URL}/docs")
    print(f"🔗 OpenAPI Schema: {BASE_URL}/openapi.json")

if __name__ == "__main__":
    main() 