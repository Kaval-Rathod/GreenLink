# 🌱 GreenLink - Carbon Credit Tokenization Platform

A blockchain-based platform that uses AI to detect greenery from images and tokenizes carbon credits on Polygon Mumbai testnet.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

GreenLink is a complete carbon credit tokenization platform with:

- **AI-Powered Greenery Detection**: Uses OpenCV and PyTorch with GPU acceleration
- **FastAPI Backend**: RESTful API with JWT authentication
- **PostGIS Database**: Spatial data storage for GPS coordinates
- **Docker Containerization**: Easy deployment and scaling
- **Blockchain Integration**: ERC-1155 tokens on Polygon Mumbai (Phase 3)

## 🏗️ Architecture

```
GreenLink/
├── backend/          # FastAPI backend with authentication
├── ai_service/       # AI greenery detection service
├── db/              # PostgreSQL/PostGIS database
├── frontend/        # Next.js frontend (Phase 4)
├── blockchain/      # Smart contracts (Phase 3)
└── docker-compose.yml
```

## ⚙️ Prerequisites

### Required Software
- **Docker Desktop** (with WSL2 integration on Windows)
- **Python 3.11+** (for local testing)
- **Git**

### Hardware Requirements
- **GPU**: NVIDIA RTX 3050 or better (for AI acceleration)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space

### System Setup
1. **Install Docker Desktop**
   - Download from [docker.com](https://www.docker.com/products/docker-desktop/)
   - Enable WSL2 integration (Windows)
   - Start Docker Desktop

2. **Install Python Dependencies** (for local testing)
   ```bash
   pip install requests pillow
   ```

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd GreenLink_web
```

### 2. Verify Docker is Running
```bash
docker --version
docker info
```

### 3. Build and Start Services
```bash
# Build all services
docker compose up --build -d

# Check if all containers are running
docker compose ps
```

## 🏃‍♂️ Running the Project

### Start All Services
```bash
# Start all services in background
docker compose up -d

# View logs
docker compose logs -f
```

### Stop Services
```bash
# Stop all services
docker compose down

# Stop and remove volumes (resets database)
docker compose down -v
```

### Restart Services
```bash
# Restart specific service
docker compose restart backend
docker compose restart ai_service

# Restart all services
docker compose restart
```

## 🧪 Testing

### 1. Quick Health Check
```bash
python simple_api_test.py
```

**Expected Output:**
```
🚀 Testing GreenLink API...
✅ Backend is running
✅ AI Service: GreenLink AI Service v2.0.0
   GPU: True
🌐 Your API is working!
```

### 2. Service Status Check
```bash
python check_services.py
```

**Expected Output:**
```
🚀 GreenLink Phase 2 - Service Check
==================================================
🌐 Checking Backend Service...
✅ Backend: GreenLink backend running.
🤖 Checking AI Service...
✅ AI Service: healthy
   GPU: True
   Device: cuda
📊 Checking AI Service Status...
✅ AI Status: Version 2.0.0
   GPU Name: NVIDIA GeForce RTX 3050 Laptop GPU
   GPU Memory: 4.0 GB
🔗 Checking Backend AI Integration...
✅ Backend AI: GreenLink AI Service v2.0.0
   GPU Available: True
```

### 3. Full Workflow Test
```bash
python test_full_workflow.py
```

**Expected Output:**
```
🚀 Testing Full Upload & Analysis Workflow
============================================================
2️⃣ Logging in...
✅ Login successful
3️⃣ Creating test image...
ℹ️ PIL not available, using existing test image...
4️⃣ Uploading image...
✅ Upload successful: Submission ID 3
5️⃣ Analyzing with AI...
✅ AI Analysis complete!
   Greenery: 42.0%
   Carbon Value: 0.21 tonnes CO2
   GPS: [40.7128, -74.0060] (from upload)
6️⃣ Listing submissions...
🎉 Full workflow test completed successfully!
✅ API is working correctly!
```

### 4. AI Integration Test
```bash
python test_ai_simple.py
```

### 5. Manual API Testing

#### Test Backend Health
```bash
curl http://localhost:8000/
```

#### Test AI Service Health
```bash
curl http://localhost:8001/
```

#### Test AI Status
```bash
curl http://localhost:8000/ai-status
```

## 📚 API Documentation

### Web Interfaces
- **Backend API Docs**: http://localhost:8000/docs
- **AI Service Docs**: http://localhost:8001/docs

### Key Endpoints

#### Authentication
```bash
# Register user
POST /users
{
  "name": "Farmer John",
  "email": "farmer@example.com", 
  "password": "mypass123"
}

# Login
POST /token
{
  "username": "farmer@example.com",
  "password": "mypass123"
}
```

#### Image Upload & Analysis
```bash
# Upload image
POST /upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
- file: image.jpg
- latitude: 40.7128
- longitude: -74.0060

# Analyze with AI
POST /analyze/{submission_id}
Authorization: Bearer <token>

# List submissions
GET /submissions
Authorization: Bearer <token>
```

#### Status Endpoints
```bash
# Health check
GET /

# AI service status
GET /ai-status

# User info
GET /users/me
Authorization: Bearer <token>
```

## 📁 Project Structure

```
GreenLink_web/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── crud.py          # Database operations
│   │   ├── auth.py          # JWT authentication
│   │   └── database.py      # Database connection
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Backend container
├── ai_service/
│   ├── main.py             # AI service FastAPI
│   ├── greenery_detector.py # Core AI logic
│   ├── requirements.txt    # ML dependencies
│   └── Dockerfile         # AI service container
├── db/
│   └── init.sql           # Database schema
├── docker-compose.yml     # Service orchestration
├── test_*.py             # Test scripts
└── README.md             # This file
```

## 🔧 Development

### Adding New Features

#### Backend Development
```bash
# Edit backend code
code backend/app/main.py

# Restart backend to apply changes
docker compose restart backend

# View backend logs
docker compose logs backend -f
```

#### AI Service Development
```bash
# Edit AI service code
code ai_service/greenery_detector.py

# Restart AI service to apply changes
docker compose restart ai_service

# View AI service logs
docker compose logs ai_service -f
```

### Database Development
```bash
# Connect to database
docker compose exec db psql -U admin -d greenlink

# View tables
\dt

# View data
SELECT * FROM users;
SELECT * FROM submissions;
```

### Environment Variables
```bash
# Backend environment
DATABASE_URL=postgresql://admin:admin@db:5432/greenlink
AI_SERVICE_URL=http://ai_service:8001

# AI Service environment
NVIDIA_VISIBLE_DEVICES=all
NVIDIA_DRIVER_CAPABILITIES=compute,utility
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Docker Not Running
```bash
# Start Docker Desktop
docker desktop start

# Check Docker status
docker info
```

#### 2. Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :8001

# Kill process or change ports in docker-compose.yml
```

#### 3. GPU Not Detected
```bash
# Check GPU in container
docker compose exec ai_service nvidia-smi

# Check AI service logs
docker compose logs ai_service
```

#### 4. Database Connection Issues
```bash
# Restart database
docker compose restart db

# Check database logs
docker compose logs db

# Reset database (WARNING: loses data)
docker compose down -v
docker compose up -d
```

#### 5. AI Service Not Responding
```bash
# Check AI service health
curl http://localhost:8001/

# View AI service logs
docker compose logs ai_service -f

# Restart AI service
docker compose restart ai_service
```

### Logs and Debugging

#### View All Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs backend -f
docker compose logs ai_service -f
docker compose logs db -f
```

#### Debug Container
```bash
# Enter backend container
docker compose exec backend bash

# Enter AI service container
docker compose exec ai_service bash

# Enter database container
docker compose exec db psql -U admin -d greenlink
```

## 📊 Performance Monitoring

### Check Resource Usage
```bash
# Container resource usage
docker stats

# GPU usage
docker compose exec ai_service nvidia-smi
```

### Database Performance
```bash
# Connect to database
docker compose exec db psql -U admin -d greenlink

# Check table sizes
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats 
WHERE tablename IN ('users', 'submissions', 'credits');
```

## 🚀 Deployment

### Production Setup
1. **Environment Variables**: Set production database URLs
2. **SSL/TLS**: Configure HTTPS certificates
3. **Load Balancer**: Set up reverse proxy (nginx)
4. **Monitoring**: Add logging and metrics
5. **Backup**: Configure database backups

### Scaling
```bash
# Scale AI service (requires load balancer)
docker compose up -d --scale ai_service=3

# Scale backend (requires load balancer)
docker compose up -d --scale backend=2
```

## 📈 Phase Status

- ✅ **Phase 1**: Backend + Database + Authentication
- ✅ **Phase 2**: AI Greenery Detection + GPU Acceleration
- 🔄 **Phase 3**: Blockchain Integration (Polygon Mumbai)
- 📋 **Phase 4**: Frontend + Marketplace

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. View the logs: `docker compose logs`
3. Create an issue in the repository

---

**🌱 GreenLink - Making Carbon Credits Accessible Through AI and Blockchain** 