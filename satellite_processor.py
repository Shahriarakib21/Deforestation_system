import cv2
import numpy as np
# import rasterio  # Commented out for Windows compatibility
# from rasterio.mask import mask
# from rasterio.plot import show
# import geopandas as gpd
# from shapely.geometry import box
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import os
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SatelliteImageProcessor:
    """
    Simplified satellite image processing for deforestation detection
    (Windows-compatible version without rasterio)
    """
    
    def __init__(self, output_dir="processed_images"):
        self.output_dir = output_dir
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp']  # Removed .tif, .tiff
        self.vegetation_indices = {}
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "preprocessed"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "features"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "analysis"), exist_ok=True)
        
    def load_image(self, image_path):
        """Load satellite image from various formats"""
        try:
            # Load regular image formats (no GeoTIFF support without rasterio)
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            logger.info(f"Loaded image: {image.shape}")
            return image, None
                
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            raise
    
    def preprocess_image(self, image, target_size=(512, 512)):
        """Preprocess satellite image for analysis"""
        try:
            if len(image.shape) == 3:
                image = cv2.resize(image, target_size)
            else:
                image = cv2.resize(image, target_size)
                image = np.expand_dims(image, axis=-1)
                
            # Normalize
            image = image.astype(np.float32) / 255.0
            
            logger.info(f"Preprocessed image shape: {image.shape}")
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise
    
    def calculate_vegetation_indices(self, image):
        """Calculate basic vegetation indices for deforestation detection"""
        try:
            indices = {}
            
            if len(image.shape) == 3 and image.shape[2] >= 3:
                # Extract RGB channels
                r = image[:, :, 0]
                g = image[:, :, 1]
                b = image[:, :, 2]
                
                # Calculate basic vegetation indices
                # NDVI approximation using RGB
                ndvi = (g - r) / (g + r + 1e-8)
                indices['NDVI'] = ndvi
                
                # GNDVI (Green Normalized Difference Vegetation Index)
                gndvi = (g - r) / (g + r + 1e-8)
                indices['GNDVI'] = gndvi
                
                # VARI (Visible Atmospherically Resistant Index)
                vari = (g - r) / (g + r - b + 1e-8)
                indices['VARI'] = vari
                
                # Simple greenness index
                greenness = g / (r + b + 1e-8)
                indices['Greenness'] = greenness
                
            else:
                logger.warning("Image doesn't have enough channels for vegetation indices")
                indices = {}
            
            self.vegetation_indices = indices
            logger.info(f"Calculated {len(indices)} vegetation indices")
            return indices
            
        except Exception as e:
            logger.error(f"Error calculating vegetation indices: {e}")
            return {}
    
    def detect_deforestation(self, image, vegetation_indices):
        """Detect deforestation using vegetation indices"""
        try:
            if not vegetation_indices:
                return {"deforestation_percentage": 0, "confidence": 0}
            
            # Use NDVI for deforestation detection
            if 'NDVI' in vegetation_indices:
                ndvi = vegetation_indices['NDVI']
                
                # Define thresholds (these would need calibration for real data)
                forest_threshold = 0.3
                deforested_threshold = 0.1
                
                # Calculate percentages
                forest_pixels = np.sum(ndvi > forest_threshold)
                deforested_pixels = np.sum(ndvi < deforested_threshold)
                total_pixels = ndvi.size
                
                deforestation_percentage = (deforested_pixels / total_pixels) * 100
                forest_percentage = (forest_pixels / total_pixels) * 100
                
                # Calculate confidence based on NDVI variance
                confidence = min(0.95, max(0.5, 1 - np.std(ndvi)))
                
                result = {
                    "deforestation_percentage": round(deforestation_percentage, 2),
                    "forest_percentage": round(forest_percentage, 2),
                    "confidence": round(confidence, 3),
                    "total_pixels": total_pixels,
                    "forest_pixels": forest_pixels,
                    "deforested_pixels": deforested_pixels
                }
                
                logger.info(f"Deforestation detection result: {result}")
                return result
            
            return {"deforestation_percentage": 0, "confidence": 0}
            
        except Exception as e:
            logger.error(f"Error in deforestation detection: {e}")
            return {"deforestation_percentage": 0, "confidence": 0}
    
    def process_satellite_image(self, image_path):
        """Main processing pipeline for satellite images"""
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Load image
            image, metadata = self.load_image(image_path)
            
            # Preprocess
            processed_image = self.preprocess_image(image)
            
            # Calculate vegetation indices
            indices = self.calculate_vegetation_indices(processed_image)
            
            # Detect deforestation
            results = self.detect_deforestation(processed_image, indices)
            
            # Create simple mask (placeholder)
            mask = np.ones(processed_image.shape[:2], dtype=np.uint8) * 255
            
            # Save results
            self.save_results(image_path, processed_image, indices, results, mask)
            
            return results, mask, indices
            
        except Exception as e:
            logger.error(f"Error processing satellite image: {e}")
            raise
    
    def save_results(self, image_path, processed_image, indices, results, mask):
        """Save processing results"""
        try:
            # Save processed image
            processed_path = os.path.join(self.output_dir, "preprocessed", 
                                        os.path.basename(image_path))
            processed_image_uint8 = (processed_image * 255).astype(np.uint8)
            cv2.imwrite(processed_path, cv2.cvtColor(processed_image_uint8, cv2.COLOR_RGB2BGR))
            
            # Save mask
            mask_path = os.path.join(self.output_dir, "analysis", 
                                   f"mask_{os.path.basename(image_path)}")
            cv2.imwrite(mask_path, mask)
            
            # Save results as JSON
            results_path = os.path.join(self.output_dir, "analysis", 
                                      f"results_{os.path.basename(image_path)}.json")
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Results saved to {self.output_dir}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def batch_process(self, directory_path):
        """Process multiple images in a directory"""
        try:
            results = []
            supported_files = []
            
            # Find supported files
            for filename in os.listdir(directory_path):
                if any(filename.lower().endswith(fmt) for fmt in self.supported_formats):
                    supported_files.append(os.path.join(directory_path, filename))
            
            logger.info(f"Found {len(supported_files)} supported files")
            
            # Process each file
            for file_path in supported_files:
                try:
                    result, mask, indices = self.process_satellite_image(file_path)
                    results.append({
                        "file": os.path.basename(file_path),
                        "result": result,
                        "status": "success"
                    })
                except Exception as e:
                    results.append({
                        "file": os.path.basename(file_path),
                        "result": None,
                        "status": "error",
                        "error": str(e)
                    })
            
            return {"results": results, "total_files": len(supported_files)}
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            raise
    
    def get_status(self):
        """Get processor status"""
        return {
            "status": "active",
            "supported_formats": self.supported_formats,
            "output_directory": self.output_dir,
            "vegetation_indices_available": list(self.vegetation_indices.keys())
        }

# Example usage
if __name__ == "__main__":
    processor = SatelliteImageProcessor()
    
    # Process single image
    # results, mask, indices = processor.process_satellite_image("path/to/satellite_image.tif")
    
    # Batch process
    # batch_results = processor.batch_process("path/to/image/directory")
