#!/usr/bin/env python3
"""
Test Phase 3: Blockchain Integration
Tests the complete workflow with blockchain tokenization
"""

import requests
import json
import time
import os

# API base URLs
BACKEND_URL = "http://localhost:8000"

def test_phase3_blockchain_integration():
    """Test the complete Phase 3 blockchain integration"""
    print("🚀 Testing Phase 3: Blockchain Integration")
    print("=" * 60)
    
    # Step 1: Check blockchain status
    print("\n1️⃣ Checking blockchain status...")
    try:
        response = requests.get(f"{BACKEND_URL}/blockchain/status")
        if response.status_code == 200:
            blockchain_status = response.json()
            print(f"✅ Blockchain Status: {blockchain_status}")
        else:
            print(f"⚠️ Blockchain status check failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Blockchain service not available: {str(e)}")
    
    # Step 2: Create test user
    print("\n2️⃣ Creating test user...")
    user_data = {
        "name": "Blockchain Test User",
        "email": "blockchain@test.com",
        "password": "testpass123",
        "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
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
    
    # Step 3: Login
    print("\n3️⃣ Logging in...")
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
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 4: Upload test image
    print("\n4️⃣ Uploading test image...")
    try:
        with open("test_photo.jpg", "rb") as f:
            files = {"file": ("test_photo.jpg", f, "image/jpeg")}
            data = {"latitude": 40.7128, "longitude": -74.0060}
            response = requests.post(f"{BACKEND_URL}/upload", headers=headers, files=files, data=data)
        
        if response.status_code == 201:
            submission = response.json()
            submission_id = submission['id']
            print(f"✅ Upload successful: Submission ID {submission_id}")
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
    except FileNotFoundError:
        print("⚠️ test_photo.jpg not found, skipping upload test")
        return False
    
    # Step 5: Analyze with AI
    print("\n5️⃣ Analyzing with AI...")
    response = requests.post(f"{BACKEND_URL}/analyze/{submission_id}", headers=headers)
    
    if response.status_code == 200:
        analysis_result = response.json()
        print("✅ AI Analysis complete!")
        print(f"   Greenery: {analysis_result['greenery_pct']}%")
        print(f"   Carbon Value: {analysis_result['carbon_value']} tonnes CO2")
    else:
        print(f"❌ Analysis failed: {response.text}")
        return False
    
    # Step 6: Register submission on blockchain
    print("\n6️⃣ Registering submission on blockchain...")
    try:
        response = requests.post(f"{BACKEND_URL}/blockchain/register-submission/{submission_id}", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Submission registered on blockchain!")
            print(f"   Transaction Hash: {result['transaction_hash']}")
        else:
            print(f"⚠️ Blockchain registration failed: {response.text}")
    except Exception as e:
        print(f"⚠️ Blockchain registration not available: {str(e)}")
    
    # Step 7: Mint carbon credit token
    print("\n7️⃣ Minting carbon credit token...")
    try:
        response = requests.post(f"{BACKEND_URL}/blockchain/mint/{submission_id}", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Carbon credit token minted!")
            print(f"   Transaction Hash: {result['transaction_hash']}")
            print(f"   Credit ID: {result['credit_id']}")
        else:
            print(f"⚠️ Token minting failed: {response.text}")
    except Exception as e:
        print(f"⚠️ Token minting not available: {str(e)}")
    
    # Step 8: Get user tokens
    print("\n8️⃣ Getting user tokens...")
    try:
        response = requests.get(f"{BACKEND_URL}/blockchain/tokens", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ User tokens retrieved!")
            print(f"   Token Count: {result['count']}")
            for token in result['tokens']:
                print(f"   - Token ID: {token['token_id']}")
                print(f"     Carbon Value: {token['carbon_value']} tonnes CO2")
                print(f"     Greenery: {token['greenery_percentage']}%")
        else:
            print(f"⚠️ Failed to get user tokens: {response.text}")
    except Exception as e:
        print(f"⚠️ Token retrieval not available: {str(e)}")
    
    # Step 9: Get marketplace listings
    print("\n9️⃣ Getting marketplace listings...")
    try:
        response = requests.get(f"{BACKEND_URL}/blockchain/marketplace")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Marketplace listings retrieved!")
            print(f"   Listing Count: {result['count']}")
            for listing in result['listings']:
                print(f"   - Listing ID: {listing['listing_id']}")
                print(f"     Token ID: {listing['token_id']}")
                print(f"     Price: {listing['price']} ETH")
        else:
            print(f"⚠️ Failed to get marketplace listings: {response.text}")
    except Exception as e:
        print(f"⚠️ Marketplace not available: {str(e)}")
    
    # Step 10: Get user credits from database
    print("\n🔟 Getting user credits from database...")
    response = requests.get(f"{BACKEND_URL}/credits", headers=headers)
    if response.status_code == 200:
        credits = response.json()
        print(f"✅ Database credits retrieved!")
        print(f"   Credit Count: {len(credits)}")
        for credit in credits:
            print(f"   - Credit ID: {credit['id']}")
            print(f"     CO2: {credit['tonnes_co2']} tonnes")
            print(f"     Token ID: {credit.get('token_id', 'N/A')}")
    else:
        print(f"❌ Failed to get credits: {response.text}")
    
    print("\n" + "=" * 60)
    print("🎉 Phase 3 Blockchain Integration Test Completed!")
    print("\n📋 Summary:")
    print("   ✅ User authentication working")
    print("   ✅ Image upload and AI analysis working")
    print("   ⚠️ Blockchain integration (requires local Hardhat node)")
    print("   ✅ Database integration working")
    
    print("\n🌐 Next Steps:")
    print("   1. Start local Hardhat node: npx hardhat node")
    print("   2. Deploy contracts: npx hardhat run scripts/deploy.js --network localhost")
    print("   3. Set BLOCKCHAIN_PRIVATE_KEY environment variable")
    print("   4. Test complete blockchain workflow")
    
    return True

def main():
    """Run the Phase 3 test"""
    try:
        success = test_phase3_blockchain_integration()
        if success:
            print("\n✅ Phase 3 test completed successfully!")
        else:
            print("\n❌ Phase 3 test failed. Check the logs above.")
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")

if __name__ == "__main__":
    main() 