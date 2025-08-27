#!/usr/bin/env python3
"""
Model Training Script for Deforestation Detection
This script will train a model using available data or create sample data for training
"""

import os
import sys
import numpy as np
from PIL import Image
import json
from datetime import datetime

# Import our modules
from model_trainer import DeforestationModelTrainer
from satellite_processor import SatelliteImageProcessor

def create_sample_training_data(output_dir="sample_training_data", num_samples=50):
    """Create sample training data for model training"""
    print("🖼️  Creating sample training data...")
    
    # Create directories
    classes = ['deforested', 'forest', 'mixed']
    for class_name in classes:
        class_dir = os.path.join(output_dir, class_name)
        os.makedirs(class_dir, exist_ok=True)
    
    # Generate sample images
    for class_idx, class_name in enumerate(classes):
        print(f"   Creating {num_samples} samples for class: {class_name}")
        
        for i in range(num_samples):
            # Create different patterns for each class
            if class_name == 'deforested':
                # Brown/reddish patterns (deforested)
                img_array = np.random.randint(100, 200, (224, 224, 3), dtype=np.uint8)
                img_array[:, :, 0] = np.random.randint(150, 220, (224, 224), dtype=np.uint8)  # More red
                img_array[:, :, 1] = np.random.randint(80, 150, (224, 224), dtype=np.uint8)   # Less green
                img_array[:, :, 2] = np.random.randint(50, 120, (224, 224), dtype=np.uint8)   # Less blue
                
            elif class_name == 'forest':
                # Green patterns (healthy forest)
                img_array = np.random.randint(50, 150, (224, 224, 3), dtype=np.uint8)
                img_array[:, :, 0] = np.random.randint(30, 100, (224, 224), dtype=np.uint8)   # Less red
                img_array[:, :, 1] = np.random.randint(120, 200, (224, 224), dtype=np.uint8)  # More green
                img_array[:, :, 2] = np.random.randint(30, 100, (224, 224), dtype=np.uint8)   # Less blue
                
            else:  # mixed
                # Mixed patterns
                img_array = np.random.randint(80, 180, (224, 224, 3), dtype=np.uint8)
                # Random color distribution
                for j in range(3):
                    img_array[:, :, j] = np.random.randint(80, 180, (224, 224), dtype=np.uint8)
            
            # Add some noise and patterns
            noise = np.random.randint(-20, 20, (224, 224, 3), dtype=np.int16)
            img_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            
            # Save image
            img = Image.fromarray(img_array)
            filename = f"{class_name}_{i+1:03d}.jpg"
            filepath = os.path.join(output_dir, class_name, filename)
            img.save(filepath)
    
    print(f"✅ Created {len(classes) * num_samples} sample images in {output_dir}")
    return output_dir

def check_training_data(data_dir):
    """Check if training data exists and is properly structured"""
    print(f"🔍 Checking training data in: {data_dir}")
    
    if not os.path.exists(data_dir):
        print(f"❌ Training data directory not found: {data_dir}")
        return False
    
    classes = ['deforested', 'forest', 'mixed']
    total_samples = 0
    
    for class_name in classes:
        class_dir = os.path.join(data_dir, class_name)
        if os.path.exists(class_dir):
            samples = [f for f in os.listdir(class_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            print(f"   {class_name}: {len(samples)} samples")
            total_samples += len(samples)
        else:
            print(f"   {class_name}: ❌ Directory not found")
    
    print(f"📊 Total training samples: {total_samples}")
    return total_samples > 0

def train_model_with_data(data_dir, model_type='simple', epochs=10, batch_size=16):
    """Train a model using the specified training data"""
    print(f"🚀 Starting model training...")
    print(f"   Data directory: {data_dir}")
    print(f"   Model type: {model_type}")
    print(f"   Epochs: {epochs}")
    print(f"   Batch size: {batch_size}")
    
    try:
        # Initialize model trainer
        trainer = DeforestationModelTrainer()
        
        # Create and train model
        print("\n📋 Creating training pipeline...")
        results = trainer.create_training_pipeline(
            data_dir=data_dir,
            model_type=model_type,
            epochs=epochs,
            batch_size=batch_size
        )
        
        print(f"✅ Training completed successfully!")
        print(f"   Model saved to: {results['model_path']}")
        print(f"   Training status: {results['training_status']}")
        print(f"   Epochs trained: {results['epochs_trained']}")
        print(f"   Accuracy: {results['evaluation_results']['accuracy']:.4f}")
        
        return results
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return None

def test_trained_model(model_path, test_image_path):
    """Test the trained model with a sample image"""
    print(f"🧪 Testing trained model...")
    
    try:
        from model_trainer import DeforestationModelTrainer
        
        # Initialize trainer and load model
        trainer = DeforestationModelTrainer()
        success = trainer.load_model(model_path)
        
        if not success:
            print("❌ Failed to load trained model")
            return None
        
        # Test prediction
        if os.path.exists(test_image_path):
            prediction = trainer.predict_single_image(test_image_path)
            print(f"✅ Prediction successful!")
            print(f"   Predicted class: {prediction['predicted_class']}")
            print(f"   Confidence: {prediction['confidence']:.4f}")
            return prediction
        else:
            print(f"⚠️  Test image not found: {test_image_path}")
            return None
            
    except Exception as e:
        print(f"❌ Model testing failed: {e}")
        return None

def main():
    """Main training function"""
    print("🌳 Deforestation Detection Model Training")
    print("=" * 50)
    
    # Check for existing training data
    training_data_dirs = [
        "uploads/training_data",
        "sample_training_data",
        "training_data"
    ]
    
    data_dir = None
    for dir_path in training_data_dirs:
        if check_training_data(dir_path):
            data_dir = dir_path
            break
    
    # If no training data found, create sample data
    if not data_dir:
        print("\n📝 No training data found. Creating sample data...")
        data_dir = create_sample_training_data()
    
    # Train the model
    print(f"\n🎯 Training model with data from: {data_dir}")
    
    # Training parameters
    training_config = {
        'data_dir': data_dir,
        'model_type': 'simple',
        'epochs': 15,  # Start with fewer epochs for testing
        'batch_size': 16
    }
    
    # Train model
    training_results = train_model_with_data(**training_config)
    
    if training_results:
        print(f"\n🎉 Model training completed successfully!")
        
        # Test the model
        test_image = os.path.join(data_dir, "deforested", "deforested_001.jpg")
        if os.path.exists(test_image):
            test_result = test_trained_model(training_results['model_path'], test_image)
        
        # Show next steps
        print(f"\n📋 Next Steps:")
        print(f"   1. Your model is saved at: {training_results['model_path']}")
        print(f"   2. Use the model in your Flask app")
        print(f"   3. Upload real deforestation images for better training")
        print(f"   4. Check model status: GET /api/model/status")
        
        # Save training summary
        summary = {
            'training_completed': True,
            'timestamp': datetime.now().isoformat(),
            'data_directory': data_dir,
            'training_results': training_results,
            'model_path': training_results['model_path']
        }
        
        with open('training_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Training summary saved to: training_summary.json")
        
    else:
        print(f"\n❌ Model training failed. Please check the error messages above.")
        print(f"   Common issues:")
        print(f"   - Insufficient training data")
        print(f"   - Memory issues")
        print(f"   - File permission problems")

if __name__ == "__main__":
    main()
