import os
import io
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Google Drive API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.discovery import build

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleDriveIntegration:
    """
    Google Drive integration for deforestation dataset management
    """
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
        self.service = None
        self.folder_id = None
        
        # Initialize authentication
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""
        try:
            # The file token.json stores the user's access and refresh tokens
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
            
            # If there are no (valid) credentials available, let the user log in
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"Credentials file not found: {self.credentials_file}")
                        logger.info("Please download credentials.json from Google Cloud Console")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.token_file, 'w') as token:
                    token.write(self.creds.to_json())
            
            # Build the service
            self.service = build('drive', 'v3', credentials=self.creds)
            logger.info("Google Drive authentication successful")
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    def create_deforestation_folder(self, folder_name: str = "Deforestation_Dataset") -> str:
        """Create a folder for deforestation datasets in Google Drive"""
        try:
            if not self.service:
                raise ValueError("Google Drive service not initialized")
            
            # Check if folder already exists
            existing_folder = self._find_folder_by_name(folder_name)
            if existing_folder:
                self.folder_id = existing_folder['id']
                logger.info(f"Using existing folder: {folder_name}")
                return self.folder_id
            
            # Create new folder
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'description': 'Deforestation detection dataset and analysis results'
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            self.folder_id = folder.get('id')
            logger.info(f"Created folder '{folder_name}' with ID: {self.folder_id}")
            return self.folder_id
            
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            raise
    
    def _find_folder_by_name(self, folder_name: str) -> Optional[Dict]:
        """Find a folder by name in Google Drive"""
        try:
            results = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            return folders[0] if folders else None
            
        except Exception as e:
            logger.error(f"Error finding folder: {e}")
            return None
    
    def upload_dataset(self, local_path: str, folder_name: str = "Deforestation_Dataset") -> Dict:
        """Upload a dataset to Google Drive"""
        try:
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local path not found: {local_path}")
            
            # Ensure folder exists
            if not self.folder_id:
                self.create_deforestation_folder(folder_name)
            
            # Get file info
            file_name = os.path.basename(local_path)
            file_size = os.path.getsize(local_path)
            
            # Check if file already exists
            existing_file = self._find_file_by_name(file_name)
            if existing_file:
                logger.info(f"File '{file_name}' already exists, updating...")
                return self._update_file(existing_file['id'], local_path)
            
            # Upload new file
            file_metadata = {
                'name': file_name,
                'parents': [self.folder_id],
                'description': f'Deforestation dataset uploaded on {datetime.now().isoformat()}'
            }
            
            # Upload file
            with open(local_path, 'rb') as f:
                media = MediaIoBaseUpload(f, mimetype='application/octet-stream', resumable=True)
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, name, size, createdTime'
                ).execute()
            
            logger.info(f"Successfully uploaded: {file_name} (ID: {file['id']})")
            return {
                'id': file['id'],
                'name': file['name'],
                'size': file.get('size', file_size),
                'upload_time': file.get('createdTime', datetime.now().isoformat()),
                'status': 'uploaded'
            }
            
        except Exception as e:
            logger.error(f"Error uploading dataset: {e}")
            raise
    
    def _find_file_by_name(self, file_name: str) -> Optional[Dict]:
        """Find a file by name in the deforestation folder"""
        try:
            if not self.folder_id:
                return None
            
            results = self.service.files().list(
                q=f"name='{file_name}' and '{self.folder_id}' in parents and trashed=false",
                spaces='drive',
                fields='files(id, name, size)'
            ).execute()
            
            files = results.get('files', [])
            return files[0] if files else None
            
        except Exception as e:
            logger.error(f"Error finding file: {file_name}")
            return None
    
    def _update_file(self, file_id: str, local_path: str) -> Dict:
        """Update an existing file in Google Drive"""
        try:
            with open(local_path, 'rb') as f:
                media = MediaIoBaseUpload(f, mimetype='application/octet-stream', resumable=True)
                file = self.service.files().update(
                    fileId=file_id,
                    media_body=media,
                    fields='id, name, size, modifiedTime'
                ).execute()
            
            logger.info(f"Successfully updated: {file['name']}")
            return {
                'id': file['id'],
                'name': file['name'],
                'size': file.get('size'),
                'upload_time': file.get('modifiedTime', datetime.now().isoformat()),
                'status': 'updated'
            }
            
        except Exception as e:
            logger.error(f"Error updating file: {e}")
            raise
    
    def download_dataset(self, file_name: str, local_path: str) -> bool:
        """Download a dataset from Google Drive"""
        try:
            # Find file in Google Drive
            file_info = self._find_file_by_name(file_name)
            if not file_info:
                raise FileNotFoundError(f"File '{file_name}' not found in Google Drive")
            
            # Download file
            request = self.service.files().get_media(fileId=file_info['id'])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    logger.info(f"Download {int(status.progress() * 100)}%")
            
            # Save to local path
            with open(local_path, 'wb') as f:
                f.write(fh.getvalue())
            
            logger.info(f"Successfully downloaded: {file_name} to {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading dataset: {e}")
            return False
    
    def list_datasets(self, folder_name: str = "Deforestation_Dataset") -> List[Dict]:
        """List all datasets in the deforestation folder"""
        try:
            # Ensure folder exists
            if not self.folder_id:
                self.create_deforestation_folder(folder_name)
            
            # List files in folder
            results = self.service.files().list(
                q=f"'{self.folder_id}' in parents and trashed=false",
                spaces='drive',
                fields='files(id, name, size, createdTime, modifiedTime, mimeType)',
                orderBy='createdTime desc'
            ).execute()
            
            files = results.get('files', [])
            datasets = []
            
            for file in files:
                # Skip folders
                if file['mimeType'] == 'application/vnd.google-apps.folder':
                    continue
                
                datasets.append({
                    'id': file['id'],
                    'name': file['name'],
                    'size': file.get('size', 0),
                    'created_time': file.get('createdTime'),
                    'modified_time': file.get('modifiedTime'),
                    'download_url': f"https://drive.google.com/uc?id={file['id']}"
                })
            
            logger.info(f"Found {len(datasets)} datasets in Google Drive")
            return datasets
            
        except Exception as e:
            logger.error(f"Error listing datasets: {e}")
            return []
    
    def delete_dataset(self, file_name: str) -> bool:
        """Delete a dataset from Google Drive"""
        try:
            file_info = self._find_file_by_name(file_name)
            if not file_info:
                logger.warning(f"File '{file_name}' not found")
                return False
            
            # Move to trash (soft delete)
            self.service.files().delete(fileId=file_info['id']).execute()
            logger.info(f"Successfully deleted: {file_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting dataset: {e}")
            return False
    
    def get_folder_info(self) -> Dict:
        """Get information about the deforestation folder"""
        try:
            if not self.folder_id:
                return {"status": "no_folder_created"}
            
            folder = self.service.files().get(
                fileId=self.folder_id,
                fields='id, name, createdTime, modifiedTime'
            ).execute()
            
            # Get file count
            files = self.service.files().list(
                q=f"'{self.folder_id}' in parents and trashed=false",
                spaces='drive',
                fields='files(id)'
            ).execute()
            
            file_count = len(files.get('files', []))
            
            return {
                'folder_id': folder['id'],
                'folder_name': folder['name'],
                'created_time': folder.get('createdTime'),
                'modified_time': folder.get('modifiedTime'),
                'file_count': file_count,
                'status': 'active'
            }
            
        except Exception as e:
            logger.error(f"Error getting folder info: {e}")
            return {"status": "error", "error": str(e)}
    
    def sync_local_folder(self, local_folder: str, folder_name: str = "Deforestation_Dataset") -> Dict:
        """Sync a local folder with Google Drive"""
        try:
            if not os.path.exists(local_folder):
                raise FileNotFoundError(f"Local folder not found: {local_folder}")
            
            # Ensure Google Drive folder exists
            if not self.folder_id:
                self.create_deforestation_folder(folder_name)
            
            sync_results = {
                'uploaded': [],
                'updated': [],
                'errors': [],
                'total_files': 0
            }
            
            # Get all files in local folder
            for root, dirs, files in os.walk(local_folder):
                for file in files:
                    local_path = os.path.join(root, file)
                    try:
                        result = self.upload_dataset(local_path, folder_name)
                        if result['status'] == 'uploaded':
                            sync_results['uploaded'].append(result['name'])
                        elif result['status'] == 'updated':
                            sync_results['updated'].append(result['name'])
                        sync_results['total_files'] += 1
                    except Exception as e:
                        sync_results['errors'].append({
                            'file': file,
                            'error': str(e)
                        })
            
            logger.info(f"Sync completed: {len(sync_results['uploaded'])} uploaded, "
                       f"{len(sync_results['updated'])} updated, {len(sync_results['errors'])} errors")
            return sync_results
            
        except Exception as e:
            logger.error(f"Error syncing folder: {e}")
            raise

# Example usage
if __name__ == "__main__":
    try:
        # Initialize Google Drive integration
        drive = GoogleDriveIntegration()
        
        # Create folder
        folder_id = drive.create_deforestation_folder()
        print(f"Folder created/accessed: {folder_id}")
        
        # List existing datasets
        datasets = drive.list_datasets()
        print(f"Found {len(datasets)} datasets")
        
        # Get folder info
        info = drive.get_folder_info()
        print(f"Folder info: {info}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Please ensure you have downloaded credentials.json from Google Cloud Console")
