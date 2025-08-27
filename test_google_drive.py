#!/usr/bin/env python3
"""
Test script for Google Drive integration
Run this to test the Google Drive functionality
"""

import os
import sys
from google_drive_integration import GoogleDriveIntegration

def test_google_drive_integration():
    """Test Google Drive integration functionality"""
    print("🌐 Testing Google Drive Integration")
    print("=" * 50)
    
    try:
        # Initialize Google Drive integration
        print("1. Initializing Google Drive integration...")
        drive = GoogleDriveIntegration()
        print("✅ Google Drive integration initialized successfully")
        
        # Test folder creation
        print("\n2. Testing folder creation...")
        folder_id = drive.create_deforestation_folder()
        print(f"✅ Folder created/accessed with ID: {folder_id}")
        
        # Test folder info
        print("\n3. Getting folder information...")
        folder_info = drive.get_folder_info()
        print(f"✅ Folder info: {folder_info}")
        
        # Test listing datasets
        print("\n4. Listing existing datasets...")
        datasets = drive.list_datasets()
        print(f"✅ Found {len(datasets)} datasets")
        
        if datasets:
            print("   Datasets:")
            for dataset in datasets:
                print(f"   - {dataset['name']} ({dataset['size']} bytes)")
        
        # Test with a sample file (if exists)
        test_file = "test_image.jpg"
        if os.path.exists(test_file):
            print(f"\n5. Testing file upload with {test_file}...")
            result = drive.upload_dataset(test_file)
            print(f"✅ File uploaded: {result}")
        else:
            print(f"\n5. Skipping file upload test (no {test_file} found)")
        
        print("\n🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Upload your deforestation datasets to Google Drive")
        print("2. Use the API endpoints in your Flask application")
        print("3. Check the GOOGLE_DRIVE_SETUP.md for detailed instructions")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Setup required:")
        print("1. Follow the GOOGLE_DRIVE_SETUP.md guide")
        print("2. Download credentials.json from Google Cloud Console")
        print("3. Place credentials.json in your project root directory")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check your setup and try again")

def create_sample_test_file():
    """Create a sample test image file"""
    try:
        from PIL import Image
        import numpy as np
        
        # Create a simple test image
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save("test_image.jpg")
        print("✅ Created test_image.jpg for testing")
        return True
    except ImportError:
        print("⚠️  PIL not available, skipping test file creation")
        return False
    except Exception as e:
        print(f"❌ Error creating test file: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Google Drive Integration Test Suite")
    print("=" * 50)
    
    # Check if credentials exist
    if not os.path.exists("credentials.json"):
        print("⚠️  credentials.json not found!")
        print("Please follow the setup guide in GOOGLE_DRIVE_SETUP.md")
        print("\nQuick setup:")
        print("1. Go to Google Cloud Console")
        print("2. Enable Google Drive API")
        print("3. Create OAuth 2.0 credentials")
        print("4. Download and rename to credentials.json")
        print("5. Place in project root directory")
        return
    
    # Create test file if needed
    if not os.path.exists("test_image.jpg"):
        create_sample_test_file()
    
    # Run tests
    test_google_drive_integration()

if __name__ == "__main__":
    main()
