import requests

# Test basic API functionality
print("🚀 Testing GreenLink API...")

# Test health
response = requests.get("http://localhost:8000/")
if response.status_code == 200:
    print("✅ Backend is running")
else:
    print("❌ Backend not responding")

# Test AI status
response = requests.get("http://localhost:8000/ai-status")
if response.status_code == 200:
    data = response.json()
    print(f"✅ AI Service: {data['service']} v{data['version']}")
    print(f"   GPU: {data['gpu_available']}")
else:
    print("❌ AI service not responding")

print("\n🌐 Your API is working!")
print("📚 Visit http://localhost:8000/docs for interactive API docs") 