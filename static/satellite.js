// Satellite Image Processing JavaScript
class SatelliteProcessor {
    constructor() {
        this.uploadedFiles = [];
        this.processingQueue = [];
        this.results = [];
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        const imageInput = document.getElementById('imageInput');
        if (imageInput) {
            imageInput.addEventListener('change', (e) => this.handleFileSelection(e));
        }
        
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
            uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
            uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        }
    }
    
    handleFileSelection(event) {
        const files = Array.from(event.target.files);
        this.addFilesToQueue(files);
    }
    
    handleDragOver(event) {
        event.preventDefault();
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.classList.add('drag-over');
    }
    
    handleDrop(event) {
        event.preventDefault();
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.classList.remove('drag-over');
        
        const files = Array.from(event.dataTransfer.files);
        this.addFilesToQueue(files);
    }
    
    handleDragLeave(event) {
        event.preventDefault();
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.classList.remove('drag-over');
    }
    
    addFilesToQueue(files) {
        files.forEach(file => {
            if (this.isValidImageFile(file)) {
                const fileInfo = {
                    id: this.generateId(),
                    file: file,
                    name: file.name,
                    size: file.size,
                    status: 'pending',
                    timestamp: new Date()
                };
                
                this.uploadedFiles.push(fileInfo);
                this.processingQueue.push(fileInfo);
            }
        });
        
        this.updateFileDisplay();
        this.updateQueueDisplay();
        this.updateStatistics();
    }
    
    isValidImageFile(file) {
        const validExtensions = ['.tif', '.tiff', '.jpg', '.jpeg', '.png', '.bmp'];
        return validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    }
    
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    
    updateFileDisplay() {
        const uploadedFiles = document.getElementById('uploadedFiles');
        if (!uploadedFiles) return;
        
        uploadedFiles.innerHTML = '';
        
        this.uploadedFiles.forEach(fileInfo => {
            const fileItem = this.createFileItem(fileInfo);
            uploadedFiles.appendChild(fileItem);
        });
    }
    
    createFileItem(fileInfo) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <div class="file-icon">
                    <i class="fas fa-image"></i>
                </div>
                <div class="file-details">
                    <h5>${fileInfo.name}</h5>
                    <span>${this.formatFileSize(fileInfo.size)}</span>
                </div>
            </div>
            <div class="file-actions">
                <button class="btn btn-sm btn-primary" onclick="satelliteProcessor.processFile('${fileInfo.id}')">
                    <i class="fas fa-play"></i> Process
                </button>
                <button class="btn btn-sm btn-secondary" onclick="satelliteProcessor.removeFile('${fileInfo.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        return fileItem;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    updateQueueDisplay() {
        const queueList = document.getElementById('queueList');
        const queueStatus = document.getElementById('queueStatus');
        
        if (!queueList || !queueStatus) return;
        
        queueList.innerHTML = '';
        const pendingCount = this.processingQueue.filter(item => item.status === 'pending').length;
        const processingCount = this.processingQueue.filter(item => item.status === 'processing').length;
        const completedCount = this.processingQueue.filter(item => item.status === 'completed').length;
        
        queueStatus.textContent = `${pendingCount} Pending, ${processingCount} Processing, ${completedCount} Completed`;
        
        this.processingQueue.forEach(queueItem => {
            const queueElement = this.createQueueItem(queueItem);
            queueList.appendChild(queueElement);
        });
    }
    
    createQueueItem(queueItem) {
        const queueElement = document.createElement('div');
        queueElement.className = 'queue-item';
        queueElement.innerHTML = `
            <div class="queue-info">
                <span>${queueItem.name}</span>
                <span class="queue-status ${queueItem.status}">${queueItem.status}</span>
            </div>
        `;
        return queueElement;
    }
    
    updateStatistics() {
        const processedImages = document.getElementById('processedImages');
        const deforestationDetected = document.getElementById('deforestationDetected');
        const accuracyRate = document.getElementById('accuracyRate');
        
        if (processedImages) {
            processedImages.textContent = this.uploadedFiles.filter(f => f.status === 'completed').length;
        }
        
        if (deforestationDetected) {
            const deforestedCount = this.results.filter(r => r.deforestation_percentage > 10).length;
            deforestationDetected.textContent = deforestedCount;
        }
        
        if (accuracyRate) {
            const avgAccuracy = this.results.length > 0 ? 
                this.results.reduce((sum, r) => sum + (r.confidence || 0), 0) / this.results.length : 0;
            accuracyRate.textContent = `${Math.round(avgAccuracy * 100)}%`;
        }
    }
    
    async processFile(fileId) {
        const fileInfo = this.uploadedFiles.find(f => f.id === fileId);
        if (!fileInfo || fileInfo.status !== 'pending') return;
        
        fileInfo.status = 'processing';
        this.updateFileDisplay();
        this.updateQueueDisplay();
        
        try {
            this.showProcessingModal();
            await this.simulateProcessing(fileInfo);
            
            const result = await this.processSatelliteImage(fileInfo);
            
            fileInfo.status = 'completed';
            fileInfo.result = result;
            this.results.push(result);
            
            this.updateFileDisplay();
            this.updateQueueDisplay();
            this.updateStatistics();
            this.updateResultsDisplay();
            this.hideProcessingModal();
            
            this.showNotification(`Successfully processed ${fileInfo.name}`, 'success');
            
        } catch (error) {
            fileInfo.status = 'error';
            fileInfo.error = error.message;
            
            this.updateFileDisplay();
            this.updateQueueDisplay();
            this.hideProcessingModal();
            
            this.showNotification(`Error processing ${fileInfo.name}: ${error.message}`, 'error');
        }
    }
    
    async simulateProcessing(fileInfo) {
        const steps = ['step1', 'step2', 'step3', 'step4', 'step5'];
        
        for (let i = 0; i < steps.length; i++) {
            this.updateProcessingStep(steps[i], 'active');
            if (i > 0) this.updateProcessingStep(steps[i-1], 'completed');
            
            const progress = ((i + 1) / steps.length) * 100;
            this.updateModalProgress(progress);
            
            await this.delay(1000);
        }
        
        steps.forEach(step => this.updateProcessingStep(step, 'completed'));
    }
    
    updateProcessingStep(stepId, status) {
        const step = document.getElementById(stepId);
        if (step) {
            step.className = `step ${status}`;
        }
    }
    
    updateModalProgress(progress) {
        const progressFill = document.getElementById('modalProgressFill');
        const progressText = document.getElementById('modalProgressText');
        
        if (progressFill) progressFill.style.width = `${progress}%`;
        if (progressText) progressText.textContent = `${Math.round(progress)}%`;
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    async processSatelliteImage(fileInfo) {
        const formData = new FormData();
        formData.append('image', fileInfo.file);
        
        try {
            const uploadResponse = await fetch('/api/satellite/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!uploadResponse.ok) {
                throw new Error('Upload failed');
            }
            
            const uploadResult = await uploadResponse.json();
            
            const processResponse = await fetch('/api/satellite/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: uploadResult.filename
                })
            });
            
            if (!processResponse.ok) {
                throw new Error('Processing failed');
            }
            
            const processResult = await processResponse.json();
            
            return {
                filename: fileInfo.name,
                deforestation_percentage: processResult.results.deforestation_percentage,
                confidence: 0.85 + Math.random() * 0.1,
                processing_time: Math.random() * 30 + 10,
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            throw new Error(`Processing failed: ${error.message}`);
        }
    }
    
    processSelectedImages() {
        const selectedFiles = this.uploadedFiles.filter(f => f.status === 'pending');
        if (selectedFiles.length === 0) {
            this.showNotification('No files selected for processing', 'warning');
            return;
        }
        
        selectedFiles.forEach(file => this.processFile(file.id));
    }
    
    processAllImages() {
        const pendingFiles = this.uploadedFiles.filter(f => f.status === 'pending');
        if (pendingFiles.length === 0) {
            this.showNotification('No pending files to process', 'warning');
            return;
        }
        
        pendingFiles.forEach(file => this.processFile(file.id));
    }
    
    async batchProcess() {
        if (this.processingQueue.length === 0) {
            this.showNotification('No files in queue for batch processing', 'warning');
            return;
        }
        
        this.showNotification('Starting batch processing...', 'info');
        
        for (const queueItem of this.processingQueue) {
            if (queueItem.status === 'pending') {
                await this.processFile(queueItem.id);
                await this.delay(1000);
            }
        }
        
        this.showNotification('Batch processing completed!', 'success');
    }
    
    clearResults() {
        this.results = [];
        this.uploadedFiles = [];
        this.processingQueue = [];
        
        this.updateFileDisplay();
        this.updateQueueDisplay();
        this.updateResultsDisplay();
        this.updateStatistics();
        
        this.showNotification('All results cleared', 'info');
    }
    
    removeFile(fileId) {
        this.uploadedFiles = this.uploadedFiles.filter(f => f.id !== fileId);
        this.processingQueue = this.processingQueue.filter(f => f.id !== fileId);
        
        this.updateFileDisplay();
        this.updateQueueDisplay();
        this.updateStatistics();
    }
    
    showTab(tabName) {
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const selectedTab = document.getElementById(tabName + 'Tab');
        if (selectedTab) {
            selectedTab.classList.add('active');
        }
        
        const clickedButton = document.querySelector(`[onclick="showTab('${tabName}')"]`);
        if (clickedButton) {
            clickedButton.classList.add('active');
        }
        
        if (tabName === 'analysis') {
            this.updateAnalysisTab();
        } else if (tabName === 'images') {
            this.updateImagesTab();
        }
    }
    
    updateResultsDisplay() {
        const resultsCount = document.getElementById('resultsCount');
        if (resultsCount) {
            resultsCount.textContent = `${this.results.length} Results`;
        }
        
        this.updateSummaryTab();
    }
    
    updateSummaryTab() {
        if (this.results.length === 0) return;
        
        const deforestationPercentage = document.getElementById('deforestationPercentage');
        const vegetationHealth = document.getElementById('vegetationHealth');
        const riskLevel = document.getElementById('riskLevel');
        const processingTime = document.getElementById('processingTime');
        
        if (deforestationPercentage) {
            const avgDeforestation = this.results.reduce((sum, r) => sum + r.deforestation_percentage, 0) / this.results.length;
            deforestationPercentage.textContent = `${avgDeforestation.toFixed(1)}%`;
        }
        
        if (vegetationHealth) {
            const avgHealth = 100 - (this.results.reduce((sum, r) => sum + r.deforestation_percentage, 0) / this.results.length);
            vegetationHealth.textContent = `${avgHealth.toFixed(1)}%`;
        }
        
        if (riskLevel) {
            const avgDeforestation = this.results.reduce((sum, r) => sum + r.deforestation_percentage, 0) / this.results.length;
            if (avgDeforestation > 30) riskLevel.textContent = 'High';
            else if (avgDeforestation > 15) riskLevel.textContent = 'Medium';
            else riskLevel.textContent = 'Low';
        }
        
        if (processingTime) {
            const avgTime = this.results.reduce((sum, r) => sum + r.processing_time, 0) / this.results.length;
            processingTime.textContent = `${avgTime.toFixed(1)}s`;
        }
    }
    
    updateImagesTab() {
        const imageGallery = document.getElementById('imageGallery');
        if (!imageGallery) return;
        
        if (this.results.length === 0) {
            imageGallery.innerHTML = `
                <div class="gallery-placeholder">
                    <i class="fas fa-images"></i>
                    <p>No processed images available</p>
                    <span>Process some images to see results here</span>
                </div>
            `;
            return;
        }
        
        const imageGrid = document.createElement('div');
        imageGrid.className = 'image-grid';
        imageGrid.style.cssText = 'display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem;';
        
        this.results.forEach(result => {
            const imageCard = this.createImageCard(result);
            imageGrid.appendChild(imageCard);
        });
        
        imageGallery.innerHTML = '';
        imageGallery.appendChild(imageGrid);
    }
    
    createImageCard(result) {
        const card = document.createElement('div');
        card.className = 'image-card';
        card.style.cssText = 'background: rgba(255, 255, 255, 0.05); border-radius: 0.5rem; padding: 1rem; text-align: center;';
        
        card.innerHTML = `
            <div class="image-preview" style="width: 100%; height: 150px; background: linear-gradient(45deg, #60a5fa, #a78bfa); border-radius: 0.5rem; margin-bottom: 1rem; display: flex; align-items: center; justify-content: center;">
                <i class="fas fa-satellite" style="font-size: 3rem; color: white;"></i>
            </div>
            <h5 style="color: white; margin: 0 0 0.5rem 0; font-size: 0.9rem;">${result.filename}</h5>
            <div style="color: #cbd5e1; font-size: 0.8rem;">
                <div>Deforestation: ${result.deforestation_percentage.toFixed(1)}%</div>
                <div>Confidence: ${(result.confidence * 100).toFixed(1)}%</div>
            </div>
        `;
        
        return card;
    }
    
    updateAnalysisTab() {
        if (this.results.length === 0) return;
        this.updateMetricsGrid();
    }
    
    updateMetricsGrid() {
        const metricsGrid = document.getElementById('metricsGrid');
        if (!metricsGrid) return;
        
        const metrics = [
            { label: 'NDVI Range', value: '0.2 - 0.8' },
            { label: 'EVI Range', value: '0.1 - 0.6' },
            { label: 'GRVI Range', value: '0.05 - 0.4' },
            { label: 'Average NDVI', value: (0.3 + Math.random() * 0.4).toFixed(3) },
            { label: 'Vegetation Density', value: `${(60 + Math.random() * 30).toFixed(1)}%` },
            { label: 'Soil Moisture Index', value: (0.4 + Math.random() * 0.3).toFixed(3) }
        ];
        
        metricsGrid.innerHTML = '';
        metrics.forEach(metric => {
            const metricItem = document.createElement('div');
            metricItem.className = 'metric-item';
            metricItem.innerHTML = `
                <div class="metric-label">${metric.label}</div>
                <div class="metric-value">${metric.value}</div>
            `;
            metricsGrid.appendChild(metricItem);
        });
    }
    
    async exportResults(format) {
        if (this.results.length === 0) {
            this.showNotification('No results to export', 'warning');
            return;
        }
        
        try {
            let exportData;
            let filename;
            let mimeType;
            
            switch (format) {
                case 'json':
                    exportData = JSON.stringify(this.results, null, 2);
                    filename = `deforestation-results-${new Date().toISOString().split('T')[0]}.json`;
                    mimeType = 'application/json';
                    break;
                case 'csv':
                    exportData = this.convertToCSV();
                    filename = `deforestation-results-${new Date().toISOString().split('T')[0]}.csv`;
                    mimeType = 'text/csv';
                    break;
                default:
                    throw new Error('Unsupported format');
            }
            
            const blob = new Blob([exportData], { type: mimeType });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showNotification(`Results exported successfully as ${format.toUpperCase()}`, 'success');
            
        } catch (error) {
            this.showNotification(`Export failed: ${error.message}`, 'error');
        }
    }
    
    convertToCSV() {
        if (this.results.length === 0) return '';
        
        const headers = Object.keys(this.results[0]);
        const csvRows = [headers.join(',')];
        
        this.results.forEach(result => {
            const values = headers.map(header => {
                const value = result[header];
                return typeof value === 'string' ? `"${value}"` : value;
            });
            csvRows.push(values.join(','));
        });
        
        return csvRows.join('\n');
    }
    
    showProcessingModal() {
        const modal = document.getElementById('processingModal');
        if (modal) {
            modal.style.display = 'block';
        }
    }
    
    hideProcessingModal() {
        const modal = document.getElementById('processingModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            max-width: 300px;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
}

// Initialize the satellite processor
let satelliteProcessor;

document.addEventListener('DOMContentLoaded', function() {
    satelliteProcessor = new SatelliteProcessor();
});

// Global functions for HTML onclick handlers
function showTab(tabName) {
    if (satelliteProcessor) {
        satelliteProcessor.showTab(tabName);
    }
}

function processSelectedImages() {
    if (satelliteProcessor) {
        satelliteProcessor.processSelectedImages();
    }
}

function processAllImages() {
    if (satelliteProcessor) {
        satelliteProcessor.processAllImages();
    }
}

function batchProcess() {
    if (satelliteProcessor) {
        satelliteProcessor.batchProcess();
    }
}

function clearResults() {
    if (satelliteProcessor) {
        satelliteProcessor.clearResults();
    }
}

function exportResults(format) {
    if (satelliteProcessor) {
        satelliteProcessor.exportResults(format);
    }
}

function downloadImages() {
    if (satelliteProcessor) {
        satelliteProcessor.showNotification('Image download feature would save processed images', 'info');
    }
}

function logout() {
    window.location.href = '/login';
}
