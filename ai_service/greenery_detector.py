"""
GreenLink AI Service - Greenery Detection Module
Uses OpenCV and PyTorch for vegetation segmentation
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path
import os

class GreeneryDetector:
    def __init__(self, use_gpu=True):
        """
        Initialize the greenery detector
        
        Args:
            use_gpu (bool): Whether to use GPU acceleration
        """
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.device = torch.device('cuda' if self.use_gpu else 'cpu')
        
        if self.use_gpu:
            print(f"🚀 Using GPU: {torch.cuda.get_device_name()}")
        else:
            print("💻 Using CPU")
    
    def load_image(self, image_path):
        """Load and preprocess image"""
        if isinstance(image_path, str):
            image = cv2.imread(image_path)
        else:
            # Convert PIL Image to OpenCV format
            image = cv2.cvtColor(np.array(image_path), cv2.COLOR_RGB2BGR)
        
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        return image
    
    def basic_greenery_detection(self, image):
        """
        Basic greenery detection using HSV color space
        This is a simple but effective method for vegetation detection
        """
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define green color ranges (vegetation typically falls in these ranges)
        # Lower green range
        lower_green1 = np.array([35, 40, 40])
        upper_green1 = np.array([85, 255, 255])
        
        # Upper green range (for different lighting conditions)
        lower_green2 = np.array([25, 40, 40])
        upper_green2 = np.array([95, 255, 255])
        
        # Create masks
        mask1 = cv2.inRange(hsv, lower_green1, upper_green1)
        mask2 = cv2.inRange(hsv, lower_green2, upper_green2)
        
        # Combine masks
        green_mask = cv2.bitwise_or(mask1, mask2)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((5,5), np.uint8)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
        
        return green_mask
    
    def advanced_greenery_detection(self, image):
        """
        Advanced greenery detection using multiple techniques
        Combines color-based detection with edge detection
        """
        # Basic greenery mask
        green_mask = self.basic_greenery_detection(image)
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Combine greenery mask with edge information
        # Remove edges from greenery areas (vegetation is usually smooth)
        edges_inv = cv2.bitwise_not(edges)
        edges_inv = cv2.dilate(edges_inv, np.ones((3,3), np.uint8))
        
        # Final mask combines greenery detection with edge filtering
        final_mask = cv2.bitwise_and(green_mask, edges_inv)
        
        return final_mask
    
    def calculate_greenery_percentage(self, mask):
        """Calculate percentage of greenery in the image"""
        total_pixels = mask.shape[0] * mask.shape[1]
        green_pixels = cv2.countNonZero(mask)
        greenery_percentage = (green_pixels / total_pixels) * 100
        return greenery_percentage
    
    def estimate_carbon_value(self, greenery_percentage, area_hectares=1.0):
        """
        Estimate carbon sequestration value based on greenery percentage
        This is a simplified model - in production you'd use more sophisticated calculations
        
        Args:
            greenery_percentage (float): Percentage of greenery detected
            area_hectares (float): Area in hectares (default 1 hectare)
        
        Returns:
            float: Estimated carbon value in tonnes CO2
        """
        # Simplified carbon sequestration model
        # Assumes average forest sequesters ~2.6 tonnes CO2 per hectare per year
        # Adjust based on greenery percentage and vegetation density
        
        # Base carbon sequestration per hectare per year
        base_carbon_per_hectare = 2.6  # tonnes CO2
        
        # Adjust based on greenery percentage (0-100%)
        greenery_factor = greenery_percentage / 100.0
        
        # Vegetation density factor (assume moderate density for detected greenery)
        density_factor = 0.7
        
        # Calculate carbon value
        carbon_value = base_carbon_per_hectare * area_hectares * greenery_factor * density_factor
        
        return round(carbon_value, 3)
    
    def create_visualization(self, image, mask, output_path=None):
        """
        Create visualization of greenery detection results
        
        Args:
            image: Original image
            mask: Greenery mask
            output_path: Path to save visualization
        
        Returns:
            numpy.ndarray: Visualization image
        """
        # Create colored mask
        colored_mask = np.zeros_like(image)
        colored_mask[mask > 0] = [0, 255, 0]  # Green color for vegetation
        
        # Blend original image with mask
        alpha = 0.6
        visualization = cv2.addWeighted(image, 1-alpha, colored_mask, alpha, 0)
        
        # Add text with greenery percentage
        greenery_pct = self.calculate_greenery_percentage(mask)
        text = f"Greenery: {greenery_pct:.1f}%"
        cv2.putText(visualization, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (255, 255, 255), 2)
        
        if output_path:
            cv2.imwrite(output_path, visualization)
        
        return visualization
    
    def analyze_image(self, image_path, output_dir=None):
        """
        Complete image analysis pipeline
        
        Args:
            image_path: Path to input image
            output_dir: Directory to save results
        
        Returns:
            dict: Analysis results
        """
        # Load image
        image = self.load_image(image_path)
        
        # Perform greenery detection
        mask = self.advanced_greenery_detection(image)
        
        # Calculate metrics
        greenery_percentage = self.calculate_greenery_percentage(mask)
        carbon_value = self.estimate_carbon_value(greenery_percentage)
        
        # Create visualization
        visualization = None
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save mask
            mask_path = output_dir / "greenery_mask.png"
            cv2.imwrite(str(mask_path), mask)
            
            # Save visualization
            viz_path = output_dir / "greenery_visualization.png"
            visualization = self.create_visualization(image, mask, str(viz_path))
        
        return {
            "greenery_percentage": round(greenery_percentage, 2),
            "carbon_value": carbon_value,
            "mask_path": str(mask_path) if output_dir else None,
            "visualization_path": str(viz_path) if output_dir else None,
            "image_size": image.shape[:2],
            "total_pixels": image.shape[0] * image.shape[1],
            "green_pixels": cv2.countNonZero(mask)
        }

# Simple test function
def test_greenery_detection():
    """Test the greenery detection on a sample image"""
    detector = GreeneryDetector()
    
    # Create a simple test image (you can replace this with a real image)
    test_image = np.zeros((300, 400, 3), dtype=np.uint8)
    
    # Add some green areas
    test_image[50:150, 50:150] = [0, 255, 0]  # Green rectangle
    test_image[200:250, 200:300] = [0, 200, 0]  # Darker green
    
    # Save test image
    cv2.imwrite("test_image.jpg", test_image)
    
    # Analyze
    results = detector.analyze_image("test_image.jpg", "test_output")
    
    print("🧪 Test Results:")
    print(f"Greenery: {results['greenery_percentage']}%")
    print(f"Carbon Value: {results['carbon_value']} tonnes CO2")
    print(f"Image Size: {results['image_size']}")
    print(f"Green Pixels: {results['green_pixels']}")

if __name__ == "__main__":
    test_greenery_detection() 