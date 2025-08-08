#!/usr/bin/env python3
"""
GreenLink Service Check
Simple verification that all services are running and accessible
"""

import requests
import json

# API base URLs
BACKEND_URL = "http://localhost:8000"
AI_SERVICE_URL = "http://localhost:8001"

def check_backend():
    """Check backend service"""
    print("🌐 Checking Backend Service...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend: {data['message']}")
            return True
        else:
            print(f"❌ Backend: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend: {str(e)}")
        return False

def check_ai_service():
    """Check AI service"""
    print("🤖 Checking AI Service...")
    
    try:
        response = requests.get(f"{AI_SERVICE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Service: {data['status']}")
            print(f"   GPU: {data['gpu_available']}")
            print(f"   Device: {data['device']}")
            return True
        else:
            print(f"❌ AI Service: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI Service: {str(e)}")
        return False

def check_ai_status():
    """Check AI service detailed status"""
    print("📊 Checking AI Service Status...")
    
    try:
        response = requests.get(f"{AI_SERVICE_URL}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Status: Version {data['version']}")
            print(f"   GPU Name: {data['gpu_info']['name']}")
            print(f"   GPU Memory: {data['gpu_info']['memory_total'] / 1024**3:.1f} GB")
            return True
        else:
            print(f"❌ AI Status: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI Status: {str(e)}")
        return False

def check_backend_ai_integration():
    """Check backend AI integration"""
    print("🔗 Checking Backend AI Integration...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/ai-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend AI: {data['service']} v{data['version']}")
            print(f"   GPU Available: {data['gpu_available']}")
            return True
        else:
            print(f"❌ Backend AI: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend AI: {str(e)}")
        return False

def main():
    """Run all checks"""
    print("🚀 GreenLink Phase 2 - Service Check")
    print("=" * 50)
    
    # Check all services
    backend_ok = check_backend()
    ai_ok = check_ai_service()
    ai_status_ok = check_ai_status()
    integration_ok = check_backend_ai_integration()
    
    print("\n" + "=" * 50)
    print("📊 Service Status:")
    print(f"   Backend: {'✅ RUNNING' if backend_ok else '❌ DOWN'}")
    print(f"   AI Service: {'✅ RUNNING' if ai_ok else '❌ DOWN'}")
    print(f"   AI Status: {'✅ OK' if ai_status_ok else '❌ FAIL'}")
    print(f"   Integration: {'✅ OK' if integration_ok else '❌ FAIL'}")
    
    if backend_ok and ai_ok and ai_status_ok and integration_ok:
        print("\n🎉 All services are running! Phase 2 is working!")
        print("\n🌐 Access Points:")
        print(f"   Backend API: {BACKEND_URL}")
        print(f"   AI Service: {AI_SERVICE_URL}")
        print(f"   Backend Docs: {BACKEND_URL}/docs")
        print(f"   AI Service Docs: {AI_SERVICE_URL}/docs")
        print("\n💡 Next Steps:")
        print("   1. Open http://localhost:8000/docs in your browser")
        print("   2. Try uploading an image using the /upload endpoint")
        print("   3. Use the /analyze/{submission_id} endpoint to get AI analysis")
        print("   4. Ready for Phase 3 blockchain integration!")
    else:
        print("\n❌ Some services are not running properly.")
        print("   Check Docker containers and logs.")

if __name__ == "__main__":
    main() 