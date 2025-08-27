# Google Drive Integration Setup Guide

This guide will help you set up Google Drive integration for your deforestation detection system.

## Prerequisites

- Google account with Google Drive
- Python 3.8+ installed
- Required Python packages (already installed)

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

## Step 2: Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as application type
4. Give it a name (e.g., "Deforestation Detection App")
5. Click "Create"
6. Download the credentials file (JSON format)
7. Rename it to `credentials.json` and place it in your project root directory

## Step 3: First Run Authentication

1. Run your Flask application:
   ```bash
   python app.py
   ```

2. The first time you access Google Drive features, a browser window will open
3. Sign in with your Google account
4. Grant permissions to access Google Drive
5. A `token.json` file will be created automatically

## Step 4: Test the Integration

Once set up, you can use these API endpoints:

### Check Status
```bash
GET /api/google-drive/status
```

### List Datasets
```bash
GET /api/google-drive/datasets
```

### Upload File
```bash
POST /api/google-drive/upload
# Include file in form data
```

### Download File
```bash
GET /api/google-drive/download/<filename>
```

### Sync Local Folder
```bash
POST /api/google-drive/sync
# JSON body: {"local_folder": "/path/to/folder"}
```

### Delete File
```bash
DELETE /api/google-drive/delete/<filename>
```

## Usage Examples

### Python Script Example
```python
from google_drive_integration import GoogleDriveIntegration

# Initialize
drive = GoogleDriveIntegration()

# Create folder
folder_id = drive.create_deforestation_folder()

# Upload dataset
result = drive.upload_dataset("path/to/dataset.zip")

# List all datasets
datasets = drive.list_datasets()

# Download dataset
success = drive.download_dataset("dataset.zip", "local_dataset.zip")

# Sync entire folder
sync_results = drive.sync_local_folder("path/to/local/datasets")
```

### JavaScript Example (Frontend)
```javascript
// Check Google Drive status
fetch('/api/google-drive/status')
    .then(response => response.json())
    .then(data => console.log(data));

// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/api/google-drive/upload', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));

// List datasets
fetch('/api/google-drive/datasets')
    .then(response => response.json())
    .then(data => console.log(data.datasets));
```

## Folder Structure

The integration will create this structure in your Google Drive:

```
Deforestation_Dataset/
├── satellite_images/
│   ├── image1.jpg
│   ├── image2.tif
│   └── ...
├── training_data/
│   ├── dataset1.zip
│   └── ...
├── models/
│   ├── model1.h5
│   └── ...
└── analysis_results/
    ├── results1.json
    └── ...
```

## Troubleshooting

### Common Issues

1. **"Credentials file not found"**
   - Ensure `credentials.json` is in your project root
   - Check file permissions

2. **"Authentication failed"**
   - Delete `token.json` and re-authenticate
   - Check internet connection

3. **"Permission denied"**
   - Ensure you granted the necessary permissions
   - Check if the file/folder exists

4. **"API not enabled"**
   - Verify Google Drive API is enabled in Google Cloud Console

### Reset Authentication

To reset authentication:
1. Delete `token.json` file
2. Restart your application
3. Re-authenticate through the browser

## Security Notes

- Keep `credentials.json` secure and don't commit it to version control
- The `token.json` file contains sensitive authentication tokens
- Consider using environment variables for production deployments

## Advanced Configuration

### Custom Folder Names
```python
# Create custom folder
drive.create_deforestation_folder("My_Custom_Folder_Name")
```

### Multiple Accounts
```python
# Use different credential files
drive1 = GoogleDriveIntegration('account1_credentials.json', 'account1_token.json')
drive2 = GoogleDriveIntegration('account2_credentials.json', 'account2_token.json')
```

### Batch Operations
```python
# Upload multiple files
for file_path in file_list:
    result = drive.upload_dataset(file_path)
    print(f"Uploaded: {result['name']}")

# Sync entire directory
sync_results = drive.sync_local_folder("path/to/datasets")
print(f"Synced {sync_results['total_files']} files")
```

## Support

If you encounter issues:
1. Check the application logs for detailed error messages
2. Verify your Google Cloud Console setup
3. Ensure all required packages are installed
4. Check file permissions and paths
