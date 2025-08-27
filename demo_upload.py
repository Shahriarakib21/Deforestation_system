#!/usr/bin/env python3
"""
Demo script to show the new upload system functionality
"""

import os
import requests
from PIL import Image
import numpy as np

def create_demo_image(filename, size=(300, 300)):
    """Create a demo image for testing"""
    # Create a simple test image
    img_array = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
    
    # Add some patterns
    if 'deforested' in filename:
        # Brown/reddish patterns
        img_array[:, :, 0] = np.random.randint(150, 220, size, dtype=np.uint8)
        img_array[:, :, 1] = np.random.randint(80, 150, size, dtype=np.uint8)
    elif 'forest' in filename:
        # Green patterns
        img_array[:, :, 1] = np.random.randint(120, 200, size, dtype=np.uint8)
        img_array[:, :, 0] = np.random.randint(30, 100, size, dtype=np.uint8)
    
    # Save image
    img = Image.fromarray(img_array)
    img.save(filename)
    print(f"✅ Created: {filename}")
    return filename

def demo_upload_system():
    """Demonstrate the upload system"""
    print("🚀 Deforestation Image Upload System Demo")
    print("=" * 50)
    
    # Check if Flask app is running
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code != 200:
            print("❌ Flask app is not responding")
            return
        print("✅ Flask app is running")
    except:
        print("❌ Flask app is not running. Please start it with: python app.py")
        return
    
    # Create demo images
    print("\n🖼️  Creating demo images...")
    demo_images = [
        "demo_deforested_area.jpg",
        "demo_healthy_forest.jpg", 
        "demo_mixed_landscape.jpg"
    ]
    
    for img in demo_images:
        create_demo_image(img)
    
    # Test upload
    print("\n📤 Testing image upload...")
    url = "http://localhost:5000/api/upload/dataset"
    
    for img_file in demo_images:
        try:
            with open(img_file, 'rb') as f:
                files = {'file': (img_file, f, 'image/jpeg')}
                data = {'category': 'deforestation_dataset'}
                
                response = requests.post(url, files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ {img_file}: Uploaded successfully!")
                    print(f"   Saved as: {result.get('filename')}")
                    print(f"   Size: {result.get('size')} bytes")
                else:
                    print(f"❌ {img_file}: Upload failed - {response.status_code}")
                    
        except Exception as e:
            print(f"❌ {img_file}: Error - {str(e)}")
    
    # Check dataset structure
    print("\n📁 Checking dataset structure...")
    try:
        response = requests.get("http://localhost:5000/api/dataset/structure")
        if response.status_code == 200:
            data = response.json()
            print("✅ Dataset structure retrieved!")
            print(f"   Total folders: {len(data.get('folders', []))}")
            print(f"   Total files: {data.get('total_files', 0)}")
            
            for folder in data.get('folders', []):
                print(f"   📁 {folder['name']}: {folder['file_count']} files")
        else:
            print(f"❌ Failed to get dataset structure")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Cleanup demo images
    print("\n🧹 Cleaning up demo images...")
    for img_file in demo_images:
        if os.path.exists(img_file):
            os.remove(img_file)
            print(f"   Removed: {img_file}")
    
    print("\n🎉 Demo completed!")
    print("\n📋 What you can do now:")
    print("   1. Visit: http://localhost:5000/upload-manager")
    print("   2. Upload your real deforestation images")
    print("   3. Use drag & drop or click to select files")
    print("   4. Organize images into dataset folders")
    print("   5. Train your model with new data")
    print("   6. Sync with Google Drive")

if __name__ == "__main__":
    demo_upload_system()
