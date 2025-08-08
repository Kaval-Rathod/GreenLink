#!/usr/bin/env python3
"""
Test Full Upload & Analysis Workflow
Demonstrates the complete API workflow: register, login, upload, analyze
"""

import requests
import json
import time
import os

# API base URLs
BACKEND_URL = "http://localhost:8000"

def create_test_image():
    """Create a simple test image"""
    try:
        from PIL import Image
        import numpy as np
        
        # Create a 300x200 image with green areas
        img = np.zeros((200, 300, 3), dtype=np.uint8)
        img[50:150, 50:250] = [0, 255, 0]  # Green rectangle
        test_image = Image.fromarray(img)
        test_image.save("test_upload.jpg")
        print("✅ Test image created: test_upload.jpg")
        return "test_upload.jpg"
    except ImportError:
        print("ℹ️ PIL not available, using existing test image...")
        # Use existing test image if available
        if os.path.exists("test_photo.png"):
            return "test_photo.png"
        else:
            print("❌ No test image available. Please install PIL or add a test image.")
            return None

def test_full_workflow():
    """Test the complete workflow"""
    print("🚀 Testing Full Upload & Analysis Workflow")
    print("=" * 60)
    
    # Step 1: Create a new user
    print("\n1️⃣ Creating new user...")
    user_data = {
        "name": "Test Farmer",
        "email": "testfarmer@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BACKEND_URL}/users", json=user_data)
    if response.status_code == 201:
        user = response.json()
        print(f"✅ User created: {user['name']} (ID: {user['id']})")
    elif response.status_code == 400 and "already registered" in response.text:
        print("ℹ️ User already exists, continuing...")
    else:
        print(f"❌ User creation failed: {response.text}")
        return False
    
    # Step 2: Login
    print("\n2️⃣ Logging in...")
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
    
    # Step 3: Create test image
    print("\n3️⃣ Creating test image...")
    image_path = create_test_image()
    if not image_path:
        return False
    
    # Step 4: Upload image
    print("\n4️⃣ Uploading image...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": (image_path, f, "image/jpeg")}
            data = {"latitude": 40.7128, "longitude": -74.0060}
            response = requests.post(f"{BACKEND_URL}/upload", headers=headers, files=files, data=data)
        
        if response.status_code == 201:
            submission = response.json()
            submission_id = submission['id']
            print(f"✅ Upload successful: Submission ID {submission_id}")
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return False
    
    # Step 5: Analyze with AI
    print("\n5️⃣ Analyzing with AI...")
    response = requests.post(f"{BACKEND_URL}/analyze/{submission_id}", headers=headers)
    
    if response.status_code == 200:
        analysis_result = response.json()
        print("✅ AI Analysis complete!")
        print(f"   Greenery: {analysis_result['greenery_pct']}%")
        print(f"   Carbon Value: {analysis_result['carbon_value']} tonnes CO2")
        if 'gps_coords' in analysis_result:
            print(f"   GPS: {analysis_result['gps_coords']}")
        else:
            print(f"   GPS: [40.7128, -74.0060] (from upload)")
    else:
        print(f"❌ Analysis failed: {response.text}")
        return False
    
    # Step 6: List submissions
    print("\n6️⃣ Listing submissions...")
    response = requests.get(f"{BACKEND_URL}/submissions", headers=headers)
    
    if response.status_code == 200:
        submissions = response.json()
        print(f"✅ Found {len(submissions)} submissions")
        for sub in submissions:
            print(f"   - ID: {sub['id']}, Greenery: {sub.get('greenery_pct', 'N/A')}%")
    else:
        print(f"❌ List submissions failed: {response.text}")
    
    # Cleanup
    if os.path.exists("test_upload.jpg"):
        os.remove("test_upload.jpg")
        print("\n🧹 Cleaned up test image")
    
    print("\n" + "=" * 60)
    print("🎉 Full workflow test completed successfully!")
    print("\n🌐 Your API is working correctly!")
    print("   You can now:")
    print("   1. Upload images via POST /upload")
    print("   2. Analyze with AI via POST /analyze/{id}")
    print("   3. List submissions via GET /submissions")
    print("   4. Use the web interface at http://localhost:8000/docs")
    
    return True

def main():
    """Run the test"""
    try:
        success = test_full_workflow()
        if success:
            print("\n✅ API is working correctly!")
        else:
            print("\n❌ API test failed. Check the logs above.")
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")

if __name__ == "__main__":
    main() 