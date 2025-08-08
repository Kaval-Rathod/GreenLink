# 🚀 GreenLink Quick Start Guide

Get GreenLink running in 5 minutes!

## ⚡ Quick Setup

### 1. Prerequisites
- Docker Desktop running
- Python 3.11+ (for testing)

### 2. Start Services
```bash
# Clone and navigate to project
cd GreenLink_web

# Build and start all services
docker compose up --build -d

# Wait 30 seconds for services to start
```

### 3. Verify Everything is Working
```bash
# Quick health check
python simple_api_test.py

# Detailed service check
python check_services.py
```

### 4. Access Web Interfaces
- **API Documentation**: http://localhost:8000/docs
- **AI Service Docs**: http://localhost:8001/docs

## 🧪 Quick Testing

### Test 1: Basic Health
```bash
curl http://localhost:8000/
# Should return: {"ok": true, "message": "GreenLink backend running."}
```

### Test 2: AI Service
```bash
curl http://localhost:8001/
# Should return: {"status": "healthy", "service": "GreenLink AI Service", "gpu_available": true}
```

### Test 3: AI Status
```bash
curl http://localhost:8000/ai-status
# Should show GPU info and service status
```

## 📱 Using the API

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"test123"}'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"
```

### 3. Upload Image (using web interface)
1. Go to http://localhost:8000/docs
2. Click "Authorize" and enter your token
3. Use the `/upload` endpoint to upload an image
4. Use the `/analyze/{submission_id}` endpoint to analyze

## 🛠️ Common Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Restart specific service
docker compose restart backend
docker compose restart ai_service

# Check container status
docker compose ps

# Reset everything (WARNING: loses data)
docker compose down -v
docker compose up --build -d
```

## 🐛 Quick Troubleshooting

### Services Not Starting
```bash
# Check Docker is running
docker info

# Check ports are free
netstat -ano | findstr :8000
netstat -ano | findstr :8001
```

### GPU Not Working
```bash
# Check GPU in container
docker compose exec ai_service nvidia-smi

# Check AI service logs
docker compose logs ai_service
```

### Database Issues
```bash
# Restart database
docker compose restart db

# Check database logs
docker compose logs db
```

## ✅ Success Indicators

You'll know everything is working when:

1. ✅ `python simple_api_test.py` shows all green checkmarks
2. ✅ http://localhost:8000/docs loads the API documentation
3. ✅ http://localhost:8001/docs loads the AI service docs
4. ✅ GPU is detected in AI service status
5. ✅ All containers show "Up" status in `docker compose ps`

## 🎯 Next Steps

Once everything is working:
1. Try uploading an image via the web interface
2. Test the AI analysis functionality
3. Explore the API endpoints
4. Ready for Phase 3 blockchain integration!

---

**Need help?** Check the full README.md for detailed documentation. 