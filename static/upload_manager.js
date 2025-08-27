// Upload Manager JavaScript
class UploadManager {
    constructor() {
        this.files = [];
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.fileList = document.getElementById('fileList');
        this.fileItems = document.getElementById('fileItems');
        this.progressSection = document.getElementById('progressSection');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.uploadBtn = document.getElementById('uploadBtn');
        
        this.initializeEventListeners();
        this.loadInitialData();
    }

    initializeEventListeners() {
        // File input change
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => {
                this.handleFileSelection(e.target.files);
            });
        }

        // Drag and drop events
        if (this.uploadArea) {
            this.uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                this.uploadArea.classList.add('dragover');
            });

            this.uploadArea.addEventListener('dragleave', (e) => {
                e.preventDefault();
                this.uploadArea.classList.remove('dragover');
            });

            this.uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                this.uploadArea.classList.remove('dragover');
                this.handleFileSelection(e.dataTransfer.files);
            });

            // Click to upload
            this.uploadArea.addEventListener('click', () => {
                if (this.fileInput) {
                    this.fileInput.click();
                }
            });
        }
    }

    handleFileSelection(fileList) {
        if (!fileList || fileList.length === 0) return;
        
        const validFiles = Array.from(fileList).filter(file => this.validateFile(file));
        
        if (validFiles.length === 0) {
            this.showError('No valid image files selected. Please select JPG, PNG, TIFF, or BMP files.');
            return;
        }

        this.files = [...this.files, ...validFiles];
        this.updateFileList();
        this.showFileList();
    }

    validateFile(file) {
        // Check file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'image/tif', 'image/bmp'];
        if (!validTypes.includes(file.type)) {
            this.showError(`Invalid file type: ${file.name}. Only image files are allowed.`);
            return false;
        }

        // Check file size (50MB limit)
        const maxSize = 50 * 1024 * 1024; // 50MB
        if (file.size > maxSize) {
            this.showError(`File too large: ${file.name}. Maximum size is 50MB.`);
            return false;
        }

        return true;
    }

    updateFileList() {
        if (!this.fileItems) return;
        
        this.fileItems.innerHTML = '';
        
        this.files.forEach((file, index) => {
            const fileItem = this.createFileItem(file, index);
            this.fileItems.appendChild(fileItem);
        });
    }

    createFileItem(file, index) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.id = `file-${index}`;

        const fileExtension = file.name.split('.').pop().toLowerCase();
        const fileIcon = this.getFileIcon(fileExtension);

        fileItem.innerHTML = `
            <div class="file-info">
                <i class="file-icon ${fileExtension}">${fileIcon}</i>
                <div class="file-details">
                    <h4>${file.name}</h4>
                    <p>${this.formatFileSize(file.size)} • ${fileExtension.toUpperCase()}</p>
                </div>
            </div>
            <div class="file-status">
                <span class="status-text">Ready</span>
                <div class="file-progress" style="display: none;">
                    <div class="file-progress-fill"></div>
                </div>
            </div>
        `;

        return fileItem;
    }

    getFileIcon(extension) {
        const icons = {
            'jpg': '📷',
            'jpeg': '📷',
            'png': '🖼️',
            'tiff': '🖼️',
            'tif': '🖼️',
            'bmp': '🖼️'
        };
        return icons[extension] || '📄';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showFileList() {
        if (this.fileList) {
            this.fileList.style.display = 'block';
        }
        if (this.uploadBtn) {
            this.uploadBtn.disabled = false;
        }
    }

    async uploadFiles() {
        if (this.files.length === 0) {
            this.showError('No files to upload.');
            return;
        }

        if (this.uploadBtn) {
            this.uploadBtn.disabled = true;
        }
        this.showProgressSection();
        
        let uploadedCount = 0;
        const totalFiles = this.files.length;

        for (let i = 0; i < this.files.length; i++) {
            const file = this.files[i];
            const fileItem = document.getElementById(`file-${i}`);
            
            try {
                // Update file status
                if (fileItem) {
                    this.updateFileStatus(fileItem, 'uploading', 'Uploading...');
                }
                
                // Upload file
                const result = await this.uploadSingleFile(file);
                
                if (result.success) {
                    if (fileItem) {
                        this.updateFileStatus(fileItem, 'success', 'Uploaded');
                    }
                    uploadedCount++;
                } else {
                    if (fileItem) {
                        this.updateFileStatus(fileItem, 'error', 'Failed');
                    }
                    console.error(`Upload failed for ${file.name}:`, result.error);
                }
                
                // Update progress
                const progress = ((i + 1) / totalFiles) * 100;
                this.updateProgress(progress);
                
            } catch (error) {
                if (fileItem) {
                    this.updateFileStatus(fileItem, 'error', 'Error');
                }
                console.error(`Upload error for ${file.name}:`, error);
            }
        }

        // Upload complete
        this.uploadComplete(uploadedCount, totalFiles);
    }

    async uploadSingleFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', 'deforestation_dataset');

        try {
            const response = await fetch('/api/upload/dataset', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return { success: true, data: result };

        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    updateFileStatus(fileItem, status, text) {
        if (!fileItem) return;
        
        fileItem.className = `file-item ${status}`;
        const statusText = fileItem.querySelector('.status-text');
        if (statusText) {
            statusText.textContent = text;
        }
    }

    showProgressSection() {
        if (this.progressSection) {
            this.progressSection.style.display = 'block';
        }
        this.updateProgress(0);
    }

    updateProgress(percentage) {
        if (this.progressFill) {
            this.progressFill.style.width = `${percentage}%`;
        }
        if (this.progressText) {
            this.progressText.textContent = `${Math.round(percentage)}% Complete`;
        }
    }

    uploadComplete(uploadedCount, totalFiles) {
        this.updateProgress(100);
        
        setTimeout(() => {
            if (uploadedCount === totalFiles) {
                this.showSuccess(`All ${uploadedCount} files uploaded successfully!`);
            } else {
                this.showError(`${uploadedCount} out of ${totalFiles} files uploaded successfully.`);
            }
            
            // Reset after showing result
            setTimeout(() => {
                this.resetUpload();
            }, 3000);
        }, 1000);
    }

    resetUpload() {
        this.files = [];
        if (this.fileList) {
            this.fileList.style.display = 'none';
        }
        if (this.progressSection) {
            this.progressSection.style.display = 'none';
        }
        if (this.uploadBtn) {
            this.uploadBtn.disabled = false;
        }
        this.updateProgress(0);
        this.loadInitialData(); // Refresh data
    }

    clearFiles() {
        this.files = [];
        if (this.fileList) {
            this.fileList.style.display = 'none';
        }
        if (this.progressSection) {
            this.progressSection.style.display = 'none';
        }
        if (this.uploadBtn) {
            this.uploadBtn.disabled = false;
        }
        this.updateProgress(0);
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.loadFolderStructure(),
                this.loadGoogleDriveStatus(),
                this.loadUploadHistory()
            ]);
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async loadFolderStructure() {
        try {
            const response = await fetch('/api/dataset/structure');
            const data = await response.json();
            this.displayFolderStructure(data);
        } catch (error) {
            console.error('Error loading folder structure:', error);
            const folderTree = document.getElementById('folderTree');
            if (folderTree) {
                folderTree.innerHTML = '<div class="error">Failed to load folder structure</div>';
            }
        }
    }

    displayFolderStructure(data) {
        const folderTree = document.getElementById('folderTree');
        if (!folderTree) return;
        
        if (!data.folders || data.folders.length === 0) {
            folderTree.innerHTML = '<div class="info">No dataset folders found. Create folders to get started.</div>';
            return;
        }

        let html = '';
        data.folders.forEach(folder => {
            html += `
                <div class="folder-item folder">
                    <i class="fas fa-folder"></i>
                    <span>${folder.name}</span>
                    <span class="file-count">(${folder.file_count} files)</span>
                </div>
            `;
            
            if (folder.files && folder.files.length > 0) {
                folder.files.forEach(file => {
                    html += `
                        <div class="folder-item file">
                            <i class="fas fa-file-image"></i>
                            <span>${file.name}</span>
                            <span class="file-size">${this.formatFileSize(file.size)}</span>
                        </div>
                    `;
                });
            }
        });
        
        folderTree.innerHTML = html;
    }

    async loadGoogleDriveStatus() {
        try {
            const response = await fetch('/api/google-drive/status');
            const data = await response.json();
            this.displayGoogleDriveStatus(data);
        } catch (error) {
            console.error('Error loading Google Drive status:', error);
            const gdriveStatus = document.getElementById('gdriveStatus');
            if (gdriveStatus) {
                gdriveStatus.innerHTML = '<div class="error">Google Drive not available</div>';
            }
        }
    }

    displayGoogleDriveStatus(data) {
        const gdriveStatus = document.getElementById('gdriveStatus');
        if (!gdriveStatus) return;
        
        if (data.status === 'active') {
            gdriveStatus.innerHTML = `
                <div class="success">
                    <i class="fas fa-check-circle"></i>
                    <strong>Connected to Google Drive</strong><br>
                    Folder: ${data.folder_name}<br>
                    Files: ${data.file_count}
                </div>
            `;
        } else {
            gdriveStatus.innerHTML = `
                <div class="warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Google Drive not connected</strong><br>
                    <a href="/google-drive-setup" class="btn btn-sm btn-primary">Setup Google Drive</a>
                </div>
            `;
        }
    }

    async loadUploadHistory() {
        try {
            const response = await fetch('/api/upload/history');
            const data = await response.json();
            this.displayUploadHistory(data);
        } catch (error) {
            console.error('Error loading upload history:', error);
            const historyList = document.getElementById('historyList');
            if (historyList) {
                historyList.innerHTML = '<div class="error">Failed to load upload history</div>';
            }
        }
    }

    displayUploadHistory(data) {
        const historyList = document.getElementById('historyList');
        if (!historyList) return;
        
        if (!data.uploads || data.uploads.length === 0) {
            historyList.innerHTML = '<div class="info">No upload history found.</div>';
            return;
        }

        let html = '';
        data.uploads.forEach(upload => {
            const date = new Date(upload.timestamp).toLocaleDateString();
            const time = new Date(upload.timestamp).toLocaleTimeString();
            
            html += `
                <div class="history-item">
                    <div class="history-info">
                        <h4>${upload.filename}</h4>
                        <p>${upload.category} • ${this.formatFileSize(upload.size)}</p>
                    </div>
                    <div class="history-time">
                        ${date}<br>${time}
                    </div>
                </div>
            `;
        });
        
        historyList.innerHTML = html;
    }

    async createDatasetFolders() {
        try {
            const response = await fetch('/api/dataset/create-folders', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Dataset folders created successfully!');
                this.loadFolderStructure();
            } else {
                this.showError('Failed to create dataset folders: ' + data.error);
            }
        } catch (error) {
            this.showError('Error creating dataset folders: ' + error.message);
        }
    }

    async organizeImages() {
        try {
            const response = await fetch('/api/dataset/organize', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(`Organized ${data.organized_count} images into dataset folders!`);
                this.loadFolderStructure();
            } else {
                this.showError('Failed to organize images: ' + data.error);
            }
        } catch (error) {
            this.showError('Error organizing images: ' + error.message);
        }
    }

    async trainWithNewData() {
        try {
            const response = await fetch('/api/model/train-with-new-data', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Model training started with new data! Check model status for progress.');
            } else {
                this.showError('Failed to start training: ' + data.error);
            }
        } catch (error) {
            this.showError('Error starting training: ' + error.message);
        }
    }

    async syncWithGoogleDrive() {
        try {
            const response = await fetch('/api/google-drive/sync', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    local_folder: 'uploads/training_data'
                })
            });
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(`Synced ${data.synced_count} files with Google Drive!`);
                this.loadGoogleDriveStatus();
            } else {
                this.showError('Failed to sync with Google Drive: ' + data.error);
            }
        } catch (error) {
            this.showError('Error syncing with Google Drive: ' + error.message);
        }
    }

    async uploadToGoogleDrive() {
        if (this.files.length === 0) {
            this.showError('No files selected for Google Drive upload.');
            return;
        }

        try {
            let uploadedCount = 0;
            
            for (const file of this.files) {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/api/google-drive/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    uploadedCount++;
                }
            }
            
            if (uploadedCount > 0) {
                this.showSuccess(`${uploadedCount} files uploaded to Google Drive!`);
                this.loadGoogleDriveStatus();
            } else {
                this.showError('No files were uploaded to Google Drive.');
            }
        } catch (error) {
            this.showError('Error uploading to Google Drive: ' + error.message);
        }
    }

    showSuccess(message) {
        const successMessage = document.getElementById('successMessage');
        const successModal = document.getElementById('successModal');
        
        if (successMessage) {
            successMessage.textContent = message;
        }
        if (successModal) {
            successModal.style.display = 'block';
        }
    }

    showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        const errorModal = document.getElementById('errorModal');
        
        if (errorMessage) {
            errorMessage.textContent = message;
        }
        if (errorModal) {
            errorModal.style.display = 'block';
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    }
}

// Global functions for HTML onclick handlers
function uploadFiles() {
    if (window.uploadManager) {
        window.uploadManager.uploadFiles();
    }
}

function clearFiles() {
    if (window.uploadManager) {
        window.uploadManager.clearFiles();
    }
}

function createDatasetFolders() {
    if (window.uploadManager) {
        window.uploadManager.createDatasetFolders();
    }
}

function organizeImages() {
    if (window.uploadManager) {
        window.uploadManager.organizeImages();
    }
}

function trainWithNewData() {
    if (window.uploadManager) {
        window.uploadManager.trainWithNewData();
    }
}

function syncWithGoogleDrive() {
    if (window.uploadManager) {
        window.uploadManager.syncWithGoogleDrive();
    }
}

function uploadToGoogleDrive() {
    if (window.uploadManager) {
        window.uploadManager.uploadToGoogleDrive();
    }
}

function closeModal(modalId) {
    if (window.uploadManager) {
        window.uploadManager.closeModal(modalId);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.uploadManager = new UploadManager();
        console.log('Upload Manager initialized successfully');
    } catch (error) {
        console.error('Error initializing Upload Manager:', error);
    }
});

// Close modals when clicking outside
window.addEventListener('click', (event) => {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
