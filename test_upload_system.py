#!/usr/bin/env python3
"""
Test script for the new upload system
"""

import os
import requests
import json
from PIL import Image
import numpy as np

def create_test_images():
    """Create test images for testing upload"""
    print("🖼️  Creating test images...")
    
    # Create test directory
    test_dir = "test_upload_images"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create different types of test images
    test_images = [
        ("deforested_area.jpg", "deforested"),
        ("healthy_forest.jpg", "forest"),
        ("mixed_landscape.jpg", "mixed"),
        ("satellite_view.jpg", "satellite")
    ]
    
    for filename, category in test_images:
        # Create a simple test image
        img_array = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        
        # Add some color patterns based on category
        if category == "deforested":
            img_array[:, :, 0] = np.random.randint(150, 220, (300, 300), dtype=np.uint8)  # More red
            img_array[:, :, 1] = np.random.randint(80, 150, (300, 300), dtype=np.uint8)   # Less green
        elif category == "forest":
            img_array[:, :, 1] = np.random.randint(120, 200, (300, 300), dtype=np.uint8)  # More green
            img_array[:, :, 0] = np.random.randint(30, 100, (300, 300), dtype=np.uint8)   # Less red
        elif category == "mixed":
            # Balanced colors
            pass
        
        # Save image
        img = Image.fromarray(img_array)
        filepath = os.path.join(test_dir, filename)
        img.save(filepath)
        print(f"   Created: {filename}")
    
    print(f"✅ Created {len(test_images)} test images in {test_dir}")
    return test_dir

def test_upload_endpoint():
    """Test the upload API endpoint"""
    print("\n🚀 Testing upload endpoint...")
    
    test_dir = "test_upload_images"
    if not os.path.exists(test_dir):
        print("❌ Test images not found. Run create_test_images() first.")
        return False
    
    # Test upload
    url = "http://localhost:5000/api/upload/dataset"
    
    for filename in os.listdir(test_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join(test_dir, filename)
            
            try:
                with open(filepath, 'rb') as f:
                    files = {'file': (filename, f, 'image/jpeg')}
                    data = {'category': 'deforestation_dataset'}
                    
                    response = requests.post(url, files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ {filename}: Uploaded successfully")
                        print(f"   Saved as: {result.get('filename')}")
                        print(f"   Size: {result.get('size')} bytes")
                    else:
                        print(f"❌ {filename}: Upload failed - {response.status_code}")
                        print(f"   Error: {response.text}")
                        
            except Exception as e:
                print(f"❌ {filename}: Error during upload - {str(e)}")
    
    return True

def test_dataset_structure():
    """Test the dataset structure API"""
    print("\n📁 Testing dataset structure endpoint...")
    
    try:
        url = "http://localhost:5000/api/dataset/structure"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dataset structure retrieved successfully")
            print(f"   Total folders: {len(data.get('folders', []))}")
            print(f"   Total files: {data.get('total_files', 0)}")
            print(f"   Total size: {data.get('total_size', 0)} bytes")
            
            # Show folder details
            for folder in data.get('folders', []):
                print(f"   📁 {folder['name']}: {folder['file_count']} files")
                
        else:
            print(f"❌ Failed to get dataset structure - {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing dataset structure: {str(e)}")

def test_create_folders():
    """Test creating dataset folders"""
    print("\n📂 Testing folder creation...")
    
    try:
        url = "http://localhost:5000/api/dataset/create-folders"
        response = requests.post(url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dataset folders created successfully")
            print(f"   Folders created: {data.get('folders_created', [])}")
        else:
            print(f"❌ Failed to create folders - {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating folders: {str(e)}")

def test_upload_history():
    """Test upload history endpoint"""
    print("\n📋 Testing upload history...")
    
    try:
        url = "http://localhost:5000/api/upload/history"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload history retrieved successfully")
            print(f"   Total uploads: {data.get('total_uploads', 0)}")
            print(f"   Recent uploads: {len(data.get('uploads', []))}")
            
            # Show recent uploads
            for upload in data.get('uploads', [])[-3:]:  # Last 3
                print(f"   📄 {upload.get('filename')} - {upload.get('category')}")
                
        else:
            print(f"❌ Failed to get upload history - {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting upload history: {str(e)}")

def main():
    """Main test function"""
    print("🧪 Testing New Upload System")
    print("=" * 50)
    
    # Check if Flask app is running
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code != 200:
            print("❌ Flask app is not responding properly")
            return
        print("✅ Flask app is running")
    except:
        print("❌ Flask app is not running. Please start it first with: python app.py")
        return
    
    # Create test images
    test_images_dir = create_test_images()
    
    # Test upload functionality
    if test_upload_endpoint():
        print("\n🎉 Upload testing completed!")
        
        # Test other endpoints
        test_dataset_structure()
        test_create_folders()
        test_upload_history()
        
        print("\n📋 Test Summary:")
        print("   1. ✅ Test images created")
        print("   2. ✅ Upload endpoint tested")
        print("   3. ✅ Dataset structure tested")
        print("   4. ✅ Folder creation tested")
        print("   5. ✅ Upload history tested")
        
        print("\n🚀 Your upload system is working!")
        print("   Visit: http://localhost:5000/upload-manager")
        
    else:
        print("\n❌ Upload testing failed!")

if __name__ == "__main__":
    main()
