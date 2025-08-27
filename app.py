from flask import Flask, render_template, jsonify, request, make_response
from flask_cors import CORS
from datetime import datetime
import json
import os
import uuid
from werkzeug.utils import secure_filename

# Import our custom modules
from satellite_processor import SatelliteImageProcessor
from model_trainer import DeforestationModelTrainer
from google_drive_integration import GoogleDriveIntegration

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp'}

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'satellite_images'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'training_data'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'models'), exist_ok=True)
# Stats file for processed images
PROCESSING_STATS_FILE = os.path.join(app.config['UPLOAD_FOLDER'], 'processing_stats.json')

def _read_processing_stats():
    if os.path.exists(PROCESSING_STATS_FILE):
        try:
            with open(PROCESSING_STATS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        'total_processed': 0,
        'total_deforested_images': 0,
        'average_deforestation_percentage': 0.0,
        'average_confidence': 0.0,
        'history': []
    }

def _write_processing_stats(stats):
    try:
        with open(PROCESSING_STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception:
        pass

def _update_processing_stats(filename: str, results: dict):
    stats = _read_processing_stats()
    prev_total = stats.get('total_processed', 0)
    new_total = prev_total + 1

    # Recompute running averages
    avg_def = stats.get('average_deforestation_percentage', 0.0)
    avg_conf = stats.get('average_confidence', 0.0)
    def_pct = float(results.get('deforestation_percentage', 0.0))
    conf = float(results.get('confidence', 0.0))
    stats['average_deforestation_percentage'] = round((avg_def * prev_total + def_pct) / new_total, 2)
    stats['average_confidence'] = round((avg_conf * prev_total + conf) / new_total, 3)
    stats['total_processed'] = new_total

    # Count as deforested image if above threshold
    if def_pct >= 20.0:
        stats['total_deforested_images'] = stats.get('total_deforested_images', 0) + 1

    # Add to history (cap last 100)
    stats['history'].append({
        'filename': filename,
        'deforestation_percentage': def_pct,
        'confidence': conf,
        'timestamp': datetime.now().isoformat()
    })
    stats['history'] = stats['history'][-100:]

    _write_processing_stats(stats)
    return stats

# Initialize processors
satellite_processor = SatelliteImageProcessor()
model_trainer = DeforestationModelTrainer()

# Initialize Google Drive integration (optional)
try:
    google_drive = GoogleDriveIntegration()
    google_drive_available = True
except Exception as e:
    logger.warning(f"Google Drive integration not available: {e}")
    google_drive = None
    google_drive_available = False

# Sample deforestation data (existing)
deforestation_data = {
    "coordinates": [
        {"lat": -23.5505, "lng": -46.6333, "severity": "high", "confidence": 0.95, "timestamp": "2024-01-15T10:30:00Z"},
        {"lat": -23.5600, "lng": -46.6400, "severity": "medium", "confidence": 0.87, "timestamp": "2024-01-15T10:35:00Z"},
        {"lat": -23.5450, "lng": -46.6250, "severity": "low", "confidence": 0.72, "timestamp": "2024-01-15T10:40:00Z"},
        {"lat": -23.5700, "lng": -46.6500, "severity": "high", "confidence": 0.91, "timestamp": "2024-01-15T10:45:00Z"},
        {"lat": -23.5350, "lng": -46.6200, "severity": "medium", "confidence": 0.83, "timestamp": "2024-01-15T10:50:00Z"}
    ],
    "statistics": {
        "total_area": 1250.5,
        "high_risk": 450.2,
        "medium_risk": 380.8,
        "low_risk": 419.5
    }
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/satellite')
def satellite():
    return render_template('satellite_processing.html')

# Model status page
@app.route('/model-status')
def model_status_page():
    return render_template('model_status.html')

@app.route('/api/deforestation-data')
def get_deforestation_data():
    return jsonify(deforestation_data)

@app.route('/api/real-time-update')
def real_time_update():
    """Simulate real-time deforestation data updates"""
    import random
    import time
    
    # Generate new random coordinates
    new_coord = {
        "lat": -23.5 + random.uniform(-0.1, 0.1),
        "lng": -46.6 + random.uniform(-0.1, 0.1),
        "severity": random.choice(["high", "medium", "low"]),
        "confidence": round(random.uniform(0.6, 0.98), 2),
        "timestamp": datetime.now().isoformat()
    }
    
    # Add to existing data
    deforestation_data["coordinates"].append(new_coord)
    
    # Keep only last 50 coordinates
    if len(deforestation_data["coordinates"]) > 50:
        deforestation_data["coordinates"] = deforestation_data["coordinates"][-50:]
    
    return jsonify({"new_coordinate": new_coord, "total_coordinates": len(deforestation_data["coordinates"])})

@app.route('/api/analytics')
def get_analytics():
    """Get deforestation analytics data"""
    analytics_data = {
        "trends": [
            {"month": "Jan", "deforestation": 120, "reforestation": 15},
            {"month": "Feb", "deforestation": 135, "reforestation": 18},
            {"month": "Mar", "deforestation": 110, "reforestation": 22},
            {"month": "Apr", "deforestation": 145, "reforestation": 12},
            {"month": "May", "deforestation": 130, "reforestation": 20},
            {"month": "Jun", "deforestation": 155, "reforestation": 16}
        ],
        "severity_distribution": [
            {"severity": "High", "count": 45, "percentage": 30},
            {"severity": "Medium", "count": 78, "percentage": 52},
            {"severity": "Low", "count": 27, "percentage": 18}
        ],
        "geographic_regions": [
            {"region": "Amazon Basin", "deforestation": 65, "risk_level": "Critical"},
            {"region": "Cerrado", "deforestation": 45, "risk_level": "High"},
            {"region": "Atlantic Forest", "deforestation": 25, "risk_level": "Medium"},
            {"region": "Pantanal", "deforestation": 15, "risk_level": "Low"}
        ]
    }
    return jsonify(analytics_data)

@app.route('/api/export-data/<format>')
def export_data(format):
    """Export deforestation data in various formats"""
    if format not in ['csv', 'json', 'excel', 'pdf']:
        return jsonify({'error': 'Unsupported format'}), 400
    
    export_data = {
        'export_info': {
            'format': format,
            'timestamp': datetime.now().isoformat(),
            'total_records': len(deforestation_data['coordinates']),
            'exported_by': 'system'
        },
        'data': deforestation_data
    }
    
    if format == 'json':
        return jsonify(export_data)
    elif format == 'csv':
        csv_data = "timestamp,lat,lng,severity,confidence\n"
        for coord in deforestation_data['coordinates']:
            csv_data += f"{coord['timestamp']},{coord['lat']},{coord['lng']},{coord['severity']},{coord['confidence']}\n"
        
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=deforestation-data-{datetime.now().strftime("%Y%m%d")}.csv'
        return response
    else:
        return jsonify(export_data)

# New Satellite Image Processing Endpoints
@app.route('/api/satellite/upload', methods=['POST'])
def upload_satellite_image():
    """Upload satellite image for processing"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'satellite_images', unique_filename)
            
            # Save file
            file.save(filepath)

            # Auto-process on upload to give immediate results
            try:
                results, _, _ = satellite_processor.process_satellite_image(filepath)
                stats = _update_processing_stats(unique_filename, results)
            except Exception as e:
                results = {'error': str(e)}
                stats = _read_processing_stats()
            
            return jsonify({
                'message': 'Image uploaded and processed successfully',
                'filename': unique_filename,
                'filepath': filepath,
                'results': results,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/satellite/process', methods=['POST'])
def process_satellite_image():
    """Process uploaded satellite image"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'Filename not provided'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'satellite_images', filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Process the image
        results, mask, indices = satellite_processor.process_satellite_image(filepath)

        # Update running stats
        stats = _update_processing_stats(filename, results)
        
        return jsonify({
            'message': 'Image processed successfully',
            'results': results,
            'stats': stats,
            'output_directory': satellite_processor.output_dir,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/satellite/batch-process', methods=['POST'])
def batch_process_images():
    """Process multiple satellite images in batch"""
    try:
        data = request.get_json()
        image_directory = data.get('image_directory')
        
        if not image_directory:
            return jsonify({'error': 'Image directory not provided'}), 400
        
        if not os.path.exists(image_directory):
            return jsonify({'error': 'Directory not found'}), 404
        
        # Batch process images
        batch_results = satellite_processor.batch_process(image_directory)

        # Update stats per file
        for entry in batch_results.get('results', []):
            if entry.get('status') == 'success' and entry.get('result'):
                _update_processing_stats(entry['file'], entry['result'])
        
        return jsonify({
            'message': 'Batch processing completed',
            'results': batch_results,
            'stats': _read_processing_stats(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Batch processing failed: {str(e)}'}), 500

# Model Training Endpoints
@app.route('/api/model/train', methods=['POST'])
def train_model():
    """Train deforestation detection model"""
    try:
        data = request.get_json()
        data_dir = data.get('data_directory')
        model_type = data.get('model_type', 'resnet')
        epochs = data.get('epochs', 50)
        batch_size = data.get('batch_size', 32)
        
        if not data_dir:
            return jsonify({'error': 'Data directory not provided'}), 400
        
        if not os.path.exists(data_dir):
            return jsonify({'error': 'Data directory not found'}), 404
        
        # Start training (this will run asynchronously in production)
        training_results = model_trainer.create_training_pipeline(
            data_dir=data_dir,
            model_type=model_type,
            epochs=epochs,
            batch_size=batch_size
        )
        
        return jsonify({
            'message': 'Model training completed successfully',
            'results': training_results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Training failed: {str(e)}'}), 500

@app.route('/api/model/upload', methods=['POST'])
def upload_trained_model():
    """Upload a pre-trained model file"""
    try:
        if 'model' not in request.files:
            return jsonify({'error': 'No model file provided'}), 400
        
        file = request.files['model']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if it's a model file
        if file.filename.endswith(('.h5', '.hdf5', '.pb')):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'models', unique_filename)
            
            # Save file
            file.save(filepath)
            
            return jsonify({
                'message': 'Model uploaded successfully',
                'filename': unique_filename,
                'filepath': filepath,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Invalid model file type'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/model/load', methods=['POST'])
def load_model():
    """Load a trained model for prediction"""
    try:
        data = request.get_json()
        model_path = data.get('model_path')
        
        if not model_path:
            return jsonify({'error': 'Model path not provided'}), 400
        
        if not os.path.exists(model_path):
            return jsonify({'error': 'Model file not found'}), 404
        
        # Load the model
        model = model_trainer.load_model(model_path)
        
        return jsonify({
            'message': 'Model loaded successfully',
            'model_info': {
                'input_shape': str(model.input_shape),
                'output_shape': str(model.output_shape),
                'num_params': model.count_params(),
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Model loading failed: {str(e)}'}), 500

@app.route('/api/model/predict', methods=['POST'])
def predict_deforestation():
    """Predict deforestation using loaded model"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        
        if not image_path:
            return jsonify({'error': 'Image path not provided'}), 400
        
        if not os.path.exists(image_path):
            return jsonify({'error': 'Image file not found'}), 404
        
        # Make prediction
        prediction = model_trainer.predict_single_image(image_path)
        
        return jsonify({
            'message': 'Prediction completed successfully',
            'prediction': prediction,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/api/model/status')
def get_model_status():
    """Get current model status and information"""
    try:
        model_info = {
            'model_loaded': model_trainer.model is not None,
            'model_type': 'Deforestation Detection CNN',
            'classes': model_trainer.class_names,
            'output_directory': model_trainer.model_dir,
            'timestamp': datetime.now().isoformat()
        }
        
        if model_trainer.model is not None:
            model_info.update({
                'input_shape': str(model_trainer.model.input_shape),
                'output_shape': str(model_trainer.model.output_shape),
                'total_params': model_trainer.model.count_params()
            })
        
        return jsonify(model_info)
        
    except Exception as e:
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500

@app.route('/api/satellite/status')
def get_satellite_processor_status():
    """Get satellite processor status"""
    try:
        status = {
            'processor_active': True,
            'output_directory': satellite_processor.output_dir,
            'supported_formats': satellite_processor.supported_formats,
            'vegetation_indices_available': list(satellite_processor.vegetation_indices.keys()),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500

# Google Drive Integration Endpoints
@app.route('/api/google-drive/status')
def get_google_drive_status():
    """Get Google Drive integration status"""
    try:
        if not google_drive_available:
            return jsonify({
                'status': 'unavailable',
                'message': 'Google Drive integration not configured',
                'timestamp': datetime.now().isoformat()
            })
        
        folder_info = google_drive.get_folder_info()
        return jsonify({
            'status': 'available',
            'folder_info': folder_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500

@app.route('/api/google-drive/datasets', methods=['GET'])
def list_google_drive_datasets():
    """List all datasets in Google Drive"""
    try:
        if not google_drive_available:
            return jsonify({'error': 'Google Drive integration not available'}), 503
        
        datasets = google_drive.list_datasets()
        return jsonify({
            'datasets': datasets,
            'total_count': len(datasets),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to list datasets: {str(e)}'}), 500

@app.route('/api/google-drive/upload', methods=['POST'])
def upload_to_google_drive():
    """Upload a file to Google Drive"""
    try:
        if not google_drive_available:
            return jsonify({'error': 'Google Drive integration not available'}), 503
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save file temporarily
            filename = secure_filename(file.filename)
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp', filename)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            file.save(temp_path)
            
            try:
                # Upload to Google Drive
                result = google_drive.upload_dataset(temp_path)
                
                # Clean up temp file
                os.remove(temp_path)
                
                return jsonify({
                    'message': 'File uploaded successfully to Google Drive',
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                # Clean up temp file on error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise e
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/google-drive/download/<filename>', methods=['GET'])
def download_from_google_drive(filename):
    """Download a file from Google Drive"""
    try:
        if not google_drive_available:
            return jsonify({'error': 'Google Drive integration not available'}), 503
        
        # Download to local uploads folder
        local_path = os.path.join(app.config['UPLOAD_FOLDER'], 'satellite_images', filename)
        
        success = google_drive.download_dataset(filename, local_path)
        
        if success:
            return jsonify({
                'message': 'File downloaded successfully',
                'local_path': local_path,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Download failed'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/google-drive/sync', methods=['POST'])
def sync_with_google_drive():
    """Sync a local folder with Google Drive"""
    try:
        if not google_drive_available:
            return jsonify({'error': 'Google Drive integration not available'}), 503
        
        data = request.get_json()
        local_folder = data.get('local_folder')
        
        if not local_folder:
            return jsonify({'error': 'Local folder path not provided'}), 400
        
        if not os.path.exists(local_folder):
            return jsonify({'error': 'Local folder not found'}), 404
        
        # Sync with Google Drive
        sync_results = google_drive.sync_local_folder(local_folder)
        
        return jsonify({
            'message': 'Sync completed successfully',
            'sync_results': sync_results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Sync failed: {str(e)}'}), 500

@app.route('/api/google-drive/delete/<filename>', methods=['DELETE'])
def delete_from_google_drive(filename):
    """Delete a file from Google Drive"""
    try:
        if not google_drive_available:
            return jsonify({'error': 'Google Drive integration not available'}), 503
        
        success = google_drive.delete_dataset(filename)
        
        if success:
            return jsonify({
                'message': 'File deleted successfully from Google Drive',
                'filename': filename,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'File not found or deletion failed'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Deletion failed: {str(e)}'}), 500

# Add new routes for upload manager
@app.route('/upload-manager')
def upload_manager():
    """Upload manager page for deforestation datasets"""
    return render_template('upload_manager.html')

@app.route('/api/upload/dataset', methods=['POST'])
def upload_dataset():
    """Upload deforestation dataset images"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        category = request.form.get('category', 'deforestation_dataset')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Create directory structure
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{secure_filename(file.filename)}"
            
            # Determine upload path based on category
            if category == 'deforestation_dataset':
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'training_data')
            else:
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'satellite_images')
            
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, filename)
            
            # Save file
            file.save(file_path)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            
            # Log upload
            upload_log = {
                'filename': filename,
                'original_name': file.filename,
                'category': category,
                'size': file_size,
                'timestamp': datetime.now().isoformat(),
                'path': file_path
            }
            
            # Save to upload history
            history_file = os.path.join(app.config['UPLOAD_FOLDER'], 'upload_history.json')
            history = []
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
            
            history.append(upload_log)
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'size': file_size,
                'path': file_path,
                'message': 'File uploaded successfully'
            })
        
        else:
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
            
    except Exception as e:
        app.logger.error(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dataset/structure')
def get_dataset_structure():
    """Get current dataset folder structure"""
    try:
        structure = {
            'folders': [],
            'total_files': 0,
            'total_size': 0
        }
        
        # Check training data folders
        training_path = os.path.join(app.config['UPLOAD_FOLDER'], 'training_data')
        if os.path.exists(training_path):
            for item in os.listdir(training_path):
                item_path = os.path.join(training_path, item)
                if os.path.isdir(item_path):
                    folder_info = {
                        'name': item,
                        'path': item_path,
                        'file_count': 0,
                        'files': [],
                        'size': 0
                    }
                    
                    # Count files in folder
                    for file in os.listdir(item_path):
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')):
                            file_path = os.path.join(item_path, file)
                            file_size = os.path.getsize(file_path)
                            folder_info['files'].append({
                                'name': file,
                                'size': file_size,
                                'path': file_path
                            })
                            folder_info['file_count'] += 1
                            folder_info['size'] += file_size
                            structure['total_files'] += 1
                            structure['total_size'] += file_size
                    
                    structure['folders'].append(folder_info)
        
        # Check satellite images
        satellite_path = os.path.join(app.config['UPLOAD_FOLDER'], 'satellite_images')
        if os.path.exists(satellite_path):
            satellite_files = []
            satellite_size = 0
            file_count = 0
            
            for file in os.listdir(satellite_path):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')):
                    file_path = os.path.join(satellite_path, file)
                    file_size = os.path.getsize(file_path)
                    satellite_files.append({
                        'name': file,
                        'size': file_size,
                        'path': file_path
                    })
                    satellite_size += file_size
                    file_count += 1
                    structure['total_files'] += 1
                    structure['total_size'] += file_size
            
            if satellite_files:
                structure['folders'].append({
                    'name': 'satellite_images',
                    'path': satellite_path,
                    'file_count': file_count,
                    'files': satellite_files,
                    'size': satellite_size
                })
        
        return jsonify(structure)
        
    except Exception as e:
        app.logger.error(f"Error getting dataset structure: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dataset/create-folders', methods=['POST'])
def create_dataset_folders():
    """Create standard dataset folder structure"""
    try:
        base_path = os.path.join(app.config['UPLOAD_FOLDER'], 'training_data')
        os.makedirs(base_path, exist_ok=True)
        
        # Create standard folders
        folders = ['deforested', 'forest', 'mixed', 'test', 'validation']
        created_folders = []
        
        for folder in folders:
            folder_path = os.path.join(base_path, folder)
            os.makedirs(folder_path, exist_ok=True)
            created_folders.append(folder)
        
        return jsonify({
            'success': True,
            'folders_created': created_folders,
            'message': f'Created {len(created_folders)} dataset folders'
        })
        
    except Exception as e:
        app.logger.error(f"Error creating dataset folders: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dataset/organize', methods=['POST'])
def organize_dataset():
    """Organize uploaded images into appropriate folders"""
    try:
        organized_count = 0
        errors = []
        
        # Get all images in training_data
        training_path = os.path.join(app.config['UPLOAD_FOLDER'], 'training_data')
        if not os.path.exists(training_path):
            return jsonify({'success': False, 'error': 'Training data folder not found'}), 404
        
        # Find images in root training_data folder
        for file in os.listdir(training_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')):
                file_path = os.path.join(training_path, file)
                
                try:
                    # Simple organization based on filename
                    # In a real system, you'd use AI to classify images
                    if 'deforest' in file.lower() or 'cut' in file.lower():
                        target_folder = 'deforested'
                    elif 'forest' in file.lower() or 'green' in file.lower():
                        target_folder = 'forest'
                    else:
                        target_folder = 'mixed'
                    
                    target_path = os.path.join(training_path, target_folder)
                    os.makedirs(target_path, exist_ok=True)
                    
                    # Move file to appropriate folder
                    new_path = os.path.join(target_path, file)
                    os.rename(file_path, new_path)
                    organized_count += 1
                    
                except Exception as e:
                    errors.append(f"Error organizing {file}: {str(e)}")
        
        return jsonify({
            'success': True,
            'organized_count': organized_count,
            'errors': errors,
            'message': f'Organized {organized_count} images'
        })
        
    except Exception as e:
        app.logger.error(f"Error organizing dataset: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload/history')
def get_upload_history():
    """Get upload history"""
    try:
        history_file = os.path.join(app.config['UPLOAD_FOLDER'], 'upload_history.json')
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Return last 50 uploads
            return jsonify({
                'uploads': history[-50:],
                'total_uploads': len(history)
            })
        else:
            return jsonify({'uploads': [], 'total_uploads': 0})
            
    except Exception as e:
        app.logger.error(f"Error getting upload history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/model/train-with-new-data', methods=['POST'])
def train_with_new_data():
    """Start model training with newly uploaded data"""
    try:
        # Check if we have new training data
        training_path = os.path.join(app.config['UPLOAD_FOLDER'], 'training_data')
        
        if not os.path.exists(training_path):
            return jsonify({'success': False, 'error': 'No training data folder found'}), 404
        
        # Count total images
        total_images = 0
        for root, dirs, files in os.walk(training_path):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')):
                    total_images += 1
        
        if total_images < 10:
            return jsonify({'success': False, 'error': 'Insufficient training data. Need at least 10 images.'}), 400
        
        # Start training process (this would typically be done in background)
        # For now, we'll simulate starting training
        training_info = {
            'status': 'started',
            'total_images': total_images,
            'timestamp': datetime.now().isoformat(),
            'message': 'Training started with new data'
        }
        
        # Save training info
        training_file = os.path.join(app.config['UPLOAD_FOLDER'], 'current_training.json')
        with open(training_file, 'w') as f:
            json.dump(training_info, f, indent=2)
        
        return jsonify({
            'success': True,
            'training_started': True,
            'total_images': total_images,
            'message': f'Training started with {total_images} images'
        })
        
    except Exception as e:
        app.logger.error(f"Error starting training: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Add new API endpoints for dashboard functionality
@app.route('/api/deforestation-statistics')
def get_deforestation_statistics():
    """Get deforestation statistics for dashboard"""
    try:
        # Get dataset structure
        training_path = os.path.join(app.config['UPLOAD_FOLDER'], 'training_data')
        satellite_path = os.path.join(app.config['UPLOAD_FOLDER'], 'satellite_images')
        
        stats = {
            'total_images': 0,
            'deforested_count': 0,
            'forest_count': 0,
            'mixed_count': 0,
            'satellite_images': 0,
            'total_size_mb': 0,
            'last_upload': None,
            'upload_trend': []
        }
        
        # Count training data
        if os.path.exists(training_path):
            for root, dirs, files in os.walk(training_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')):
                        stats['total_images'] += 1
                        file_path = os.path.join(root, file)
                        stats['total_size_mb'] += os.path.getsize(file_path) / (1024 * 1024)
                        
                        # Categorize by folder
                        folder_name = os.path.basename(root)
                        if folder_name == 'deforested':
                            stats['deforested_count'] += 1
                        elif folder_name == 'forest':
                            stats['forest_count'] += 1
                        elif folder_name == 'mixed':
                            stats['mixed_count'] += 1
        
        # Count satellite images
        if os.path.exists(satellite_path):
            for file in os.listdir(satellite_path):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')):
                    stats['satellite_images'] += 1
                    file_path = os.path.join(satellite_path, file)
                    stats['total_size_mb'] += os.path.getsize(file_path) / (1024 * 1024)
        
        # Get last upload time
        history_file = os.path.join(app.config['UPLOAD_FOLDER'], 'upload_history.json')
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
                if history:
                    stats['last_upload'] = history[-1]['timestamp']
                    
                    # Create upload trend (last 7 days)
                    from datetime import datetime, timedelta
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=7)
                    
                    daily_uploads = {}
                    for upload in history:
                        upload_date = datetime.fromisoformat(upload['timestamp']).date()
                        if start_date.date() <= upload_date <= end_date.date():
                            date_str = upload_date.strftime('%Y-%m-%d')
                            daily_uploads[date_str] = daily_uploads.get(date_str, 0) + 1
                    
                    # Fill missing days with 0
                    for i in range(7):
                        date = (end_date - timedelta(days=i)).strftime('%Y-%m-%d')
                        if date not in daily_uploads:
                            daily_uploads[date] = 0
                    
                    stats['upload_trend'] = [{'date': date, 'count': count} for date, count in daily_uploads.items()]
        
        # Merge processing stats for averages
        proc = _read_processing_stats()
        stats.update({
            'processed_images': proc.get('total_processed', 0),
            'average_detection': proc.get('average_deforestation_percentage', 0.0),
            'average_confidence': proc.get('average_confidence', 0.0)
        })
        return jsonify(stats)
        
    except Exception as e:
        app.logger.error(f"Error getting deforestation statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent-activity')
def get_recent_activity():
    """Get recent activity for dashboard"""
    try:
        activities = []
        
        # Get recent uploads
        history_file = os.path.join(app.config['UPLOAD_FOLDER'], 'upload_history.json')
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
                
                # Get last 10 uploads
                for upload in history[-10:]:
                    activities.append({
                        'type': 'upload',
                        'title': f'Image uploaded: {upload["original_name"]}',
                        'description': f'Category: {upload["category"]} • Size: {upload["size"]} bytes',
                        'timestamp': upload['timestamp'],
                        'icon': 'fas fa-upload',
                        'color': 'success'
                    })
        
        # Get model training status
        training_file = os.path.join(app.config['UPLOAD_FOLDER'], 'current_training.json')
        if os.path.exists(training_file):
            with open(training_file, 'r') as f:
                training = json.load(f)
                activities.append({
                    'type': 'training',
                    'title': 'Model training started',
                    'description': f'Training with {training["total_images"]} images',
                    'timestamp': training['timestamp'],
                    'icon': 'fas fa-brain',
                    'color': 'info'
                })
        
        # Get folder creation activities
        training_path = os.path.join(app.config['UPLOAD_FOLDER'], 'training_data')
        if os.path.exists(training_path):
            for folder in os.listdir(training_path):
                if os.path.isdir(os.path.join(training_path, folder)):
                    # Check if folder was created recently (simplified)
                    activities.append({
                        'type': 'folder',
                        'title': f'Dataset folder: {folder}',
                        'description': 'Ready for image organization',
                        'timestamp': datetime.now().isoformat(),
                        'icon': 'fas fa-folder',
                        'color': 'warning'
                    })
        
        # Processing stats events
        proc = _read_processing_stats()
        for h in proc.get('history', [])[-10:]:
            activities.append({
                'type': 'processing',
                'title': f"Processed: {h['filename']}",
                'description': f"Deforestation: {h['deforestation_percentage']}% • Confidence: {h['confidence']}",
                'timestamp': h['timestamp'],
                'icon': 'fas fa-cogs',
                'color': 'info'
            })

        # Sort by timestamp (newest first)
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'activities': activities[:10],  # Return top 10
            'total_activities': len(activities)
        })
        
    except Exception as e:
        app.logger.error(f"Error getting recent activity: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system-status')
def get_system_status():
    """Get system status for dashboard"""
    try:
        status = {
            'system_status': 'active',
            'last_update': datetime.now().isoformat(),
            'model_status': 'ready',
            'upload_folder_status': 'active',
            'google_drive_status': 'not_configured'
        }
        
        # Check upload folder
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            status['upload_folder_status'] = 'error'
        
        # Check model status
        model_file = os.path.join(app.config['UPLOAD_FOLDER'], 'current_training.json')
        if os.path.exists(model_file):
            with open(model_file, 'r') as f:
                training = json.load(f)
                if training.get('status') == 'started':
                    status['model_status'] = 'training'
        
        # Check Google Drive
        try:
            if google_drive:
                status['google_drive_status'] = 'available'
        except:
            status['google_drive_status'] = 'not_configured'
        
        # Attach processing stats summary
        stats = _read_processing_stats()
        status.update({
            'processed_images': stats.get('total_processed', 0),
            'average_detection': stats.get('average_deforestation_percentage', 0.0),
            'average_confidence': stats.get('average_confidence', 0.0)
        })
        return jsonify(status)
        
    except Exception as e:
        app.logger.error(f"Error getting system status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
