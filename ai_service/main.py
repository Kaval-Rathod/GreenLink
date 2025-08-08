"""
GreenLink AI Service - FastAPI Server
Provides greenery detection endpoints for the main backend
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import os
from pathlib import Path
import tempfile
import uuid
import torch

from greenery_detector import GreeneryDetector

app = FastAPI(title="GreenLink AI Service", version="2.0.0")

# Initialize the greenery detector
detector = GreeneryDetector(use_gpu=True)

# Create directories
INPUT_DIR = Path("/app/input")
OUTPUT_DIR = Path("/app/output")
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

class ImagePathRequest(BaseModel):
    image_path: str

@app.get("/")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GreenLink AI Service",
        "gpu_available": detector.use_gpu,
        "device": str(detector.device)
    }

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze uploaded image for greenery detection
    
    Args:
        file: Image file to analyze
    
    Returns:
        dict: Analysis results with greenery percentage and carbon value
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix if file.filename else '.jpg'
        input_path = INPUT_DIR / f"{file_id}{file_extension}"
        output_dir = OUTPUT_DIR / file_id
        
        # Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Analyze image
        results = detector.analyze_image(str(input_path), str(output_dir))
        
        # Clean up input file
        os.remove(input_path)
        
        return {
            "success": True,
            "greenery_percentage": results["greenery_percentage"],
            "carbon_value": results["carbon_value"],
            "image_size": results["image_size"],
            "total_pixels": results["total_pixels"],
            "green_pixels": results["green_pixels"],
            "mask_path": results["mask_path"],
            "visualization_path": results["visualization_path"]
        }
        
    except Exception as e:
        # Clean up on error
        if 'input_path' in locals() and os.path.exists(input_path):
            os.remove(input_path)
        
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-path")
async def analyze_image_path(request: ImagePathRequest):
    """
    Analyze image from file path (for internal use)
    
    Args:
        request: Request containing image_path
    
    Returns:
        dict: Analysis results
    """
    try:
        image_path = request.image_path
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image file not found")
        
        # Create output directory
        file_id = str(uuid.uuid4())
        output_dir = OUTPUT_DIR / file_id
        
        # Analyze image
        results = detector.analyze_image(image_path, str(output_dir))
        
        return {
            "success": True,
            "greenery_percentage": results["greenery_percentage"],
            "carbon_value": results["carbon_value"],
            "image_size": results["image_size"],
            "total_pixels": results["total_pixels"],
            "green_pixels": results["green_pixels"],
            "mask_path": results["mask_path"],
            "visualization_path": results["visualization_path"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/status")
def get_status():
    """Get service status and GPU information"""
    gpu_info = {}
    if detector.use_gpu:
        gpu_info = {
            "name": torch.cuda.get_device_name(),
            "memory_total": torch.cuda.get_device_properties(0).total_memory,
            "memory_allocated": torch.cuda.memory_allocated(0),
            "memory_cached": torch.cuda.memory_reserved(0)
        }
    
    return {
        "service": "GreenLink AI Service",
        "version": "2.0.0",
        "gpu_available": detector.use_gpu,
        "device": str(detector.device),
        "gpu_info": gpu_info,
        "input_dir": str(INPUT_DIR),
        "output_dir": str(OUTPUT_DIR)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 