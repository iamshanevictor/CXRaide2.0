#!/usr/bin/env python3
import os
import sys
import torch
import numpy as np
import cv2
from PIL import Image
import io
import base64
import logging
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('local_model_server')

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# API key for basic security
API_KEY = os.environ.get('MODEL_API_KEY', 'default-secure-key-change-me')

# Model constants
INPUT_SIZE = 512
IT2_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'IT2_model_epoch_300.pth')
IT3_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'IT3_model_epoch_260.pth')

# Class dictionaries
IT2_CLASSES = {
    0: "Background",
    1: "Cardiomegaly",
    2: "Pleural thickening",
    3: "Pulmonary fibrosis",
    4: "Pleural effusion",
    5: "Nodule/Mass",
    6: "Infiltration",
    7: "Consolidation",
    8: "Atelectasis",
    9: "Pneumothorax"
}

IT3_CLASSES = {
    0: "Background",
    1: "Cardiomegaly",
    2: "Pleural thickening",
    3: "Pulmonary fibrosis",
    4: "Pleural effusion",
    5: "Nodule/Mass",
    6: "Infiltration"
}

# Global variables to store models
models = {
    'IT2': None,
    'IT3': None
}

def load_models():
    """Load both IT2 and IT3 models in background"""
    try:
        if os.path.exists(IT2_MODEL_PATH):
            logger.info(f"Loading IT2 model from {IT2_MODEL_PATH}")
            models['IT2'] = torch.load(IT2_MODEL_PATH, map_location=torch.device('cpu'))
            models['IT2'].eval()
            logger.info("IT2 model loaded successfully")
        else:
            logger.warning(f"IT2 model not found at {IT2_MODEL_PATH}")
            
        if os.path.exists(IT3_MODEL_PATH):
            logger.info(f"Loading IT3 model from {IT3_MODEL_PATH}")
            models['IT3'] = torch.load(IT3_MODEL_PATH, map_location=torch.device('cpu'))
            models['IT3'].eval()
            logger.info("IT3 model loaded successfully")
        else:
            logger.warning(f"IT3 model not found at {IT3_MODEL_PATH}")
            
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        
# Function to resize and preprocess image
def preprocess_image(image_data, target_size=INPUT_SIZE):
    """
    Preprocess the input image data:
    - Decode base64 data
    - Resize to target size preserving aspect ratio
    - Convert to model input format
    """
    try:
        # Handle possible data:image/jpeg;base64, prefix
        if ',' in image_data:
            image_data = image_data.split(',')[1]
            
        # Decode base64 to image
        image_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Get original dimensions
        original_width, original_height = img.size
        aspect_ratio = original_width / original_height
        
        # Calculate new dimensions preserving aspect ratio
        if aspect_ratio > 1:  # Width > Height
            new_width = target_size
            new_height = int(target_size / aspect_ratio)
        else:  # Height >= Width
            new_height = target_size
            new_width = int(target_size * aspect_ratio)
            
        # Resize image
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Create black canvas of target size
        canvas = Image.new('RGB', (target_size, target_size), color='black')
        
        # Paste resized image onto canvas (centered)
        paste_x = (target_size - new_width) // 2
        paste_y = (target_size - new_height) // 2
        canvas.paste(img_resized, (paste_x, paste_y))
        
        # Convert to numpy array and normalize
        img_array = np.array(canvas).astype(np.float32) / 255.0
        
        # Transpose from (H,W,C) to (C,H,W) format
        img_tensor = torch.from_numpy(img_array.transpose(2, 0, 1)).unsqueeze(0)
        
        # Return preprocessed image and dimensions for bounding box adjustment
        return {
            'tensor': img_tensor,
            'original_size': (original_width, original_height),
            'new_size': (new_width, new_height),
            'offset': (paste_x, paste_y)
        }
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise ValueError(f"Failed to preprocess image: {str(e)}")

@torch.no_grad()
def predict_with_model(image_data, model_type='IT3'):
    """Run prediction with the specified model"""
    if model_type not in models or models[model_type] is None:
        raise ValueError(f"Model {model_type} not loaded or not available")
    
    # Preprocess image
    processed = preprocess_image(image_data)
    img_tensor = processed['tensor']
    
    # Start prediction timer
    start_time = time.time()
    
    # Get model and class dictionary
    model = models[model_type]
    class_dict = IT3_CLASSES if model_type == 'IT3' else IT2_CLASSES
    
    # Run inference
    outputs = model(img_tensor)
    
    # Process different output types
    if isinstance(outputs, tuple) and len(outputs) > 1:
        # Model returns class scores and bounding boxes
        class_scores, bboxes = outputs
        
        # Convert to numpy for processing
        class_scores = class_scores.cpu().numpy()
        probabilities = np.exp(class_scores) / np.sum(np.exp(class_scores), axis=1, keepdims=True)
        
        if bboxes is not None:
            bboxes = bboxes.cpu().numpy()
            
            # Scale bounding boxes to original image coordinates
            original_width, original_height = processed['original_size']
            offset_x, offset_y = processed['offset']
            new_width, new_height = processed['new_size']
            
            scaled_boxes = []
            for box in bboxes[0]:  # First batch item
                # Adjust from canvas to resized image
                x1 = max(0, box[0] - offset_x) 
                y1 = max(0, box[1] - offset_y)
                x2 = min(new_width, box[2] - offset_x)
                y2 = min(new_height, box[3] - offset_y)
                
                # Scale to original image dimensions
                x1 = int((x1 / new_width) * original_width)
                y1 = int((y1 / new_height) * original_height)
                x2 = int((x2 / new_width) * original_width)
                y2 = int((y2 / new_height) * original_height)
                
                scaled_boxes.append([x1, y1, x2, y2])
    else:
        # Model returns only class scores
        if isinstance(outputs, tuple):
            outputs = outputs[0]
            
        # Calculate probabilities from outputs
        if isinstance(outputs, torch.Tensor):
            outputs = outputs.cpu().numpy()
            
        probabilities = outputs
        if len(probabilities.shape) > 1 and probabilities.shape[1] > 1:
            # For multi-class probabilities
            probabilities = np.exp(probabilities) / np.sum(np.exp(probabilities), axis=1, keepdims=True)
        bboxes = None
        scaled_boxes = None
    
    # End timer
    end_time = time.time()
    
    # Format results
    results = {
        'model_type': model_type,
        'processing_time': end_time - start_time,
        'predictions': []
    }
    
    # Process predictions based on model type
    if model_type == 'IT2':
        # For IT2 model with classes 0-9
        probs = probabilities[0]
        top_indices = np.argsort(probs)[::-1][:5]  # Get indices of top 5 classes
        
        for idx in top_indices:
            if idx > 0 and probs[idx] > 0.1:  # Skip background (0) and only include predictions with >10% confidence
                results['predictions'].append({
                    'class_id': int(idx),
                    'class_name': IT2_CLASSES.get(int(idx), f"Unknown-{idx}"),
                    'confidence': float(probs[idx])
                })
    else:
        # For IT3 model with classes 0-6
        probs = probabilities[0]
        top_indices = np.argsort(probs)[::-1][:5]  # Get indices of top 5 classes
        
        for idx in top_indices:
            if idx > 0 and probs[idx] > 0.1:  # Skip background (0) and only include predictions with >10% confidence
                results['predictions'].append({
                    'class_id': int(idx),
                    'class_name': IT3_CLASSES.get(int(idx), f"Unknown-{idx}"),
                    'confidence': float(probs[idx])
                })
    
    # Add bounding boxes if available
    if scaled_boxes:
        results['bounding_boxes'] = scaled_boxes
    
    return results

def merge_model_predictions(it3_results, it2_results):
    """
    Merge predictions from both models:
    - Use IT3 predictions for the 6 common classes (1-6)
    - Use IT2 predictions for the 3 additional classes (7-9)
    """
    merged_results = {
        'model_type': 'merged',
        'processing_time': it3_results['processing_time'] + it2_results['processing_time'],
        'predictions': []
    }
    
    # First, add all IT3 predictions (classes 1-6)
    merged_results['predictions'].extend(it3_results['predictions'])
    
    # Then, add IT2 predictions only for classes 7, 8, 9
    for pred in it2_results['predictions']:
        # Only include classes 7-9 from IT2
        if pred['class_id'] >= 7:
            merged_results['predictions'].append(pred)
    
    # Add bounding boxes if available in either result
    if 'bounding_boxes' in it3_results:
        merged_results['bounding_boxes'] = it3_results['bounding_boxes']
    elif 'bounding_boxes' in it2_results:
        merged_results['bounding_boxes'] = it2_results['bounding_boxes']
    
    return merged_results

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint to check server health and model status"""
    # Check model availability
    it2_available = models['IT2'] is not None
    it3_available = models['IT3'] is not None
    merged_available = it2_available and it3_available
    
    return jsonify({
        'status': 'ok',
        'models': {
            'IT2': it2_available,
            'IT3': it3_available,
            'merged': merged_available
        },
        'capabilities': {
            'classes': {
                'IT2': list(IT2_CLASSES.items()),
                'IT3': list(IT3_CLASSES.items())
            },
            'prioritized_classes': 'Using IT3 for classes 1-6 and IT2 for classes 7-9 when using merged mode'
        }
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint to process prediction requests"""
    # Verify API key for security
    api_key = request.headers.get('X-API-Key')
    if api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {api_key[:10] if api_key else 'None'}")
        return jsonify({'error': 'Unauthorized - Invalid API key'}), 401
        
    try:
        # Get data from request
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'Missing image data'}), 400
            
        # Get model type from request (default to 'merged')
        model_type = data.get('model_type', 'merged')
        
        # If user specifically requests a single model
        if model_type in ['IT2', 'IT3']:
            # Check if model is loaded
            if models[model_type] is None:
                return jsonify({
                    'error': f'Model {model_type} not loaded',
                    'status': 'service_unavailable'
                }), 503
                
            # Run prediction with single model
            start_time = time.time()
            results = predict_with_model(data['image'], model_type)
            end_time = time.time()
            
            # Add timing information
            results['total_processing_time'] = end_time - start_time
            
            return jsonify(results)
        
        # For merged predictions (default behavior)
        elif model_type == 'merged':
            # Check if both models are loaded
            if models['IT3'] is None or models['IT2'] is None:
                missing_models = []
                if models['IT3'] is None:
                    missing_models.append('IT3')
                if models['IT2'] is None:
                    missing_models.append('IT2')
                    
                return jsonify({
                    'error': f'Required models not loaded: {", ".join(missing_models)}',
                    'status': 'service_unavailable'
                }), 503
            
            # Run predictions with both models
            start_time = time.time()
            it3_results = predict_with_model(data['image'], 'IT3')
            it2_results = predict_with_model(data['image'], 'IT2')
            
            # Merge results
            merged_results = merge_model_predictions(it3_results, it2_results)
            end_time = time.time()
            
            # Add timing information
            merged_results['total_processing_time'] = end_time - start_time
            
            return jsonify(merged_results)
        
        else:
            return jsonify({'error': f'Invalid model type: {model_type}'}), 400
            
    except ValueError as e:
        logger.error(f"Value error in prediction: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing prediction: {str(e)}")
        return jsonify({
            'error': f'Prediction failed: {str(e)}',
            'status': 'internal_server_error'
        }), 500

if __name__ == '__main__':
    # Load models at startup
    load_models()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5500))
    
    # Print server information
    logger.info(f"Starting Local Model Server on port {port}")
    logger.info(f"API Key: {API_KEY[:3]}...{API_KEY[-3:]} (Change this in production!)")
    logger.info(f"Models available: IT2={'✓' if models['IT2'] else '✗'}, IT3={'✓' if models['IT3'] else '✗'}")
    
    # Run server
    app.run(host='0.0.0.0', port=port, debug=False) 