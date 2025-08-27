# ML-Based Real-Time Deforestation Tracking System [Shahriar Akib ( 20222222) , Shafin Ahmed Shoscho ( 2221699) , Morium Akter Shorna ( 2222420) , MD Akash Hossen ( 2231188) , Maruf Al Hasan ( 2130208),Al Waresin ( 2211180)  

A comprehensive web application for monitoring and tracking deforestation activities in real-time using advanced machine learning algorithms and satellite imagery analysis.

## 🌟 **Features**

### **Core System**
- **Real-time Monitoring**: Live deforestation detection and tracking
- **Interactive Dashboard**: Comprehensive analytics and visualization
- **Alert System**: Real-time notifications for deforestation events
- **Geographic Mapping**: Interactive maps with deforestation hotspots
- **Data Export/Import**: Multiple format support (CSV, JSON, Excel, PDF)

### **Satellite Image Processing** 🛰️
- **Multi-format Support**: TIF, TIFF, JPG, PNG, BMP
- **Advanced Preprocessing**: Image normalization, resizing, and enhancement
- **Vegetation Indices Calculation**:
  - NDVI (Normalized Difference Vegetation Index)
  - EVI (Enhanced Vegetation Index)
  - GNDVI (Green Normalized Difference Vegetation Index)
  - SAVI (Soil Adjusted Vegetation Index)
  - GRVI (Green-Red Vegetation Index)
  - VARI (Visible Atmospherically Resistant Index)
  - TGI (Triangular Greenness Index)
- **Deforestation Detection**: AI-powered analysis with confidence scoring
- **Batch Processing**: Process multiple images simultaneously
- **Comprehensive Visualization**: Multi-panel analysis results

### **Machine Learning Model Training** 🧠
- **Multiple Architectures**: ResNet50, EfficientNetB0, Custom CNN
- **Transfer Learning**: Pre-trained models with fine-tuning
- **Data Augmentation**: Rotation, scaling, flipping for robust training
- **Advanced Training Features**:
  - Early stopping and learning rate scheduling
  - Model checkpointing and TensorBoard logging
  - GPU acceleration support
  - Comprehensive evaluation metrics
- **Model Management**: Save, load, and deploy trained models

### **Authentication & Security**
- **User Registration & Login**: Secure authentication system
- **Password Strength Validation**: Real-time password strength indicator
- **Social Login Integration**: Ready for OAuth implementation
- **Session Management**: Secure user sessions

## 🚀 **Technology Stack**

### **Backend**
- **Flask**: Python web framework
- **OpenCV**: Computer vision and image processing
- **TensorFlow/Keras**: Deep learning and model training
- **Rasterio**: Geospatial raster data handling
- **NumPy/Pandas**: Numerical computing and data manipulation
- **Scikit-learn**: Machine learning utilities

### **Frontend**
- **HTML5/CSS3**: Modern, responsive design
- **JavaScript (ES6+)**: Interactive functionality
- **Chart.js**: Data visualization
- **Font Awesome**: Icon library
- **CSS Grid/Flexbox**: Responsive layouts

### **Data Processing**
- **Satellite Imagery**: Multi-spectral and RGB image support
- **Geospatial Analysis**: Coordinate systems and projections
- **Real-time Processing**: Live data streaming and analysis
- **Batch Operations**: Efficient bulk processing

## 📁 **Project Structure**

```
Deforestation2/
├── app.py                          # Main Flask application
├── satellite_processor.py          # Satellite image processing module
├── model_trainer.py               # ML model training module
├── requirements.txt               # Python dependencies
├── README.md                     # Project documentation
├── static/                       # Static assets
│   ├── style.css                # Main dashboard styles
│   ├── satellite.css            # Satellite processing styles
│   ├── auth.css                 # Authentication page styles
│   ├── script.js                # Main dashboard JavaScript
│   └── satellite.js             # Satellite processing JavaScript
├── templates/                    # HTML templates
│   ├── index.html               # Main dashboard
│   ├── login.html               # Login page
│   ├── register.html            # Registration page
│   └── satellite_processing.html # Satellite processing interface
├── uploads/                     # File uploads
│   ├── satellite_images/        # Uploaded satellite images
│   ├── training_data/           # Training datasets
│   └── models/                  # Trained models
├── processed_images/            # Processed image outputs
│   ├── preprocessed/            # Preprocessed images
│   ├── features/                # Calculated vegetation indices
│   └── analysis/                # Analysis results and visualizations
└── trained_models/              # Model training outputs
    ├── checkpoints/             # Training checkpoints
    ├── saved_models/            # Saved model files
    └── training_logs/           # Training logs and TensorBoard data
```

## 🛠️ **Installation & Setup**

### **Prerequisites**
- Python 3.8+
- pip package manager
- Git (for cloning)
- Google account with Google Drive (for cloud integration)

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd Deforestation2
```

### **2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Run the Application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### **5. Google Drive Integration (Optional)**
```bash
# Follow the setup guide
# See GOOGLE_DRIVE_SETUP.md for detailed instructions

# Test Google Drive integration
python test_google_drive.py
```

## 📊 **API Endpoints**

### **Core System**
- `GET /` - Main dashboard
- `GET /login` - Login page
- `GET /register` - Registration page
- `GET /satellite` - Satellite processing interface

### **Data & Analytics**
- `GET /api/deforestation-data` - Get deforestation data
- `GET /api/real-time-update` - Real-time updates
- `GET /api/analytics` - Analytics data
- `GET /api/export-data/<format>` - Export data (CSV, JSON, Excel, PDF)

### **Satellite Image Processing**
- `POST /api/satellite/upload` - Upload satellite images
- `POST /api/satellite/process` - Process uploaded images
- `POST /api/satellite/batch-process` - Batch process images
- `GET /api/satellite/status` - Processor status

### **Model Training & Management**
- `POST /api/model/train` - Train new model
- `POST /api/model/upload` - Upload pre-trained model
- `POST /api/model/load` - Load trained model
- `POST /api/model/predict` - Make predictions
- `GET /api/model/status` - Model status

### **Google Drive Integration** 🗂️
- `GET /api/google-drive/status` - Check Google Drive connection
- `GET /api/google-drive/datasets` - List datasets in Google Drive
- `POST /api/google-drive/upload` - Upload file to Google Drive
- `GET /api/google-drive/download/<filename>` - Download file from Google Drive
- `POST /api/google-drive/sync` - Sync local folder with Google Drive
- `DELETE /api/google-drive/delete/<filename>` - Delete file from Google Drive

## 🔬 **Usage Examples**

### **Satellite Image Processing**

#### **1. Single Image Processing**
```python
from satellite_processor import SatelliteImageProcessor

# Initialize processor
processor = SatelliteImageProcessor()

# Process single image
results, mask, indices = processor.process_satellite_image("path/to/satellite_image.tif")

print(f"Deforestation detected: {results['deforestation_percentage']:.2f}%")
print(f"Vegetation indices calculated: {list(indices.keys())}")
```

#### **2. Batch Processing**
```python
# Process multiple images
batch_results = processor.batch_process("path/to/image/directory")
print(f"Processed {len(batch_results['results'])} images")
```

### **Model Training**

#### **1. Complete Training Pipeline**
```python
from model_trainer import DeforestationModelTrainer

# Initialize trainer
trainer = DeforestationModelTrainer()

# Train model with complete pipeline
results = trainer.create_training_pipeline(
    data_dir="path/to/dataset",
    model_type='resnet',
    epochs=50,
    batch_size=32
)

print(f"Model saved to: {results['model_path']}")
print(f"Accuracy: {results['evaluation_results']['accuracy']:.4f}")
```

#### **2. Custom Model Architecture**
```python
# Create custom CNN
model = trainer.create_model(model_type='custom', input_shape=(224, 224, 3))

# Train the model
history = trainer.train_model(train_generator, val_generator, epochs=100)
```

#### **3. Model Prediction**
```python
# Load trained model
trainer.load_model("path/to/model.h5")

# Make prediction
prediction = trainer.predict_single_image("path/to/test_image.jpg")
print(f"Predicted class: {prediction['predicted_class']}")
print(f"Confidence: {prediction['confidence']:.4f}")
```

#### **3. Model Prediction**
```python
# Load trained model
trainer.load_model("path/to/model.h5")

# Make prediction
prediction = trainer.predict_single_image("path/to/test_image.jpg")
print(f"Predicted class: {prediction['predicted_class']}")
print(f"Confidence: {prediction['confidence']:.4f}")
```

## 🌍 **Dataset Structure**

For model training, organize your data as follows:

```
dataset/
├── deforested/          # Images of deforested areas
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── forest/              # Images of healthy forest
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── mixed/               # Images with mixed conditions
    ├── image1.jpg
    ├── image2.jpg
    └── ...
```

## 📈 **Performance & Optimization**

### **GPU Acceleration**
- Automatic GPU detection and configuration
- Memory growth optimization for large models
- Multi-GPU support for distributed training

### **Image Processing Optimization**
- Efficient memory management for large images
- Parallel processing for batch operations
- Optimized vegetation index calculations

### **Model Training Optimization**
- Early stopping to prevent overfitting
- Learning rate scheduling for better convergence
- Data augmentation for improved generalization

## 🔒 **Security Features**

- **File Upload Validation**: Secure file type checking
- **Input Sanitization**: Protection against malicious inputs
- **Session Management**: Secure user authentication
- **API Rate Limiting**: Protection against abuse

## 📱 **Responsive Design**

- **Mobile-First Approach**: Optimized for all device sizes
- **Touch-Friendly Interface**: Mobile-optimized controls
- **Progressive Web App**: Offline capability and app-like experience

## 🚀 **Deployment**

### **Production Deployment**
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### **Docker Deployment**
```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🧪 **Testing**

### **Run Tests**
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests with coverage
pytest --cov=.
```

### **Test Coverage**
- Unit tests for core modules
- Integration tests for API endpoints
- Frontend component testing

## 🔄 **Continuous Integration**

- **Automated Testing**: GitHub Actions workflow
- **Code Quality**: Linting and formatting checks
- **Security Scanning**: Dependency vulnerability checks

## 📚 **Documentation**

- **API Documentation**: Comprehensive endpoint documentation
- **User Guide**: Step-by-step usage instructions
- **Developer Guide**: Code architecture and contribution guidelines

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **OpenCV Community**: Computer vision libraries
- **TensorFlow Team**: Deep learning framework
- **Flask Community**: Web framework
- **Research Community**: Deforestation detection algorithms

## 📞 **Support**

- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions
- **Documentation**: Comprehensive guides and tutorials

## 🔮 **Future Enhancements**

- **Real-time Satellite Feeds**: Live satellite data integration
- **Advanced ML Models**: Transformer-based architectures
- **Mobile App**: Native mobile applications
- **Cloud Deployment**: AWS/Azure integration
- **Blockchain Integration**: Immutable deforestation records
- **AI Chatbot**: Intelligent assistance system
- **Enhanced Cloud Integration**: Google Drive, Dropbox, OneDrive support
- **Automated Dataset Management**: AI-powered dataset organization and labeling

---

**Built with ❤️ for environmental conservation and sustainable development.**
