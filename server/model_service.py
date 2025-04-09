import torch
import torchvision.models as models
from torchvision import transforms
from torchvision.ops import nms
from PIL import Image
import io
import os
import time
import threading
from flask import Blueprint, request, jsonify
import logging

# Initialize logger
logger = logging.getLogger(__name__)

model_bp = Blueprint('model', __name__)

# Class dictionary
classes = {
    'Cardiomegaly': 1,
    'Pleural thickening': 2,
    'Pulmonary fibrosis': 3,
    'Pleural effusion': 4,
    'Nodule/Mass': 5,
    'Infiltration': 6,
    'Consolidation': 7,
    'Atelectasis': 8,
    'Pneumothorax': 9
}

# Reverse mapping
classes_reverse = {v: k for k, v in classes.items()}

# Transform pipeline - original code used 512x512
transform = transforms.Compose([
    transforms.Resize((512, 512)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load model
model = None
model_loading = False
model_load_lock = threading.Lock()

def load_model_in_background():
    """Load model in a background thread to avoid blocking the app startup"""
    global model, model_loading
    
    try:
        logger.info("Starting background model loading...")
        start_time = time.time()
        
        # Create model
        temp_model = models.detection.ssd300_vgg16(weights=None)
        
        # Check multiple possible locations for the model file
        possible_paths = [
            'IT2_model_epoch_300.pth',
            './IT2_model_epoch_300.pth',
            '../IT2_model_epoch_300.pth',
            '/app/IT2_model_epoch_300.pth',
            '/app/server/IT2_model_epoch_300.pth',
            os.path.join(os.path.dirname(__file__), 'IT2_model_epoch_300.pth'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'IT2_model_epoch_300.pth'),
            # Adding additional paths with model_epoch_300.pth filename
            'model_epoch_300.pth',
            './model_epoch_300.pth',
            '../model_epoch_300.pth',
            '/app/model_epoch_300.pth',
            '/app/server/model_epoch_300.pth',
            os.path.join(os.path.dirname(__file__), 'model_epoch_300.pth'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model_epoch_300.pth')
        ]
        
        model_path = None
        for path in possible_paths:
            if os.path.exists(path):
                model_path = path
                logger.info(f"Found model file at: {model_path}")
                break
        
        if not model_path:
            logger.error(f"Model file not found. Checked paths: {possible_paths}")
            return
        
        # Load weights
        logger.info(f"Loading model weights from {model_path}...")
        temp_model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        temp_model.eval()
        
        # Update the global model variable
        model = temp_model
        
        elapsed = time.time() - start_time
        logger.info(f"Model loaded successfully in {elapsed:.2f} seconds")
    except Exception as e:
        logger.error(f"Failed to load model in background: {str(e)}")
    finally:
        model_loading = False

def get_model():
    """Get the model, loading it if necessary"""
    global model, model_loading
    
    # Return immediately if model is loaded
    if model is not None:
        return model
    
    # Try to acquire the lock to load the model
    with model_load_lock:
        # Check again in case another thread loaded the model while we were waiting
        if model is not None:
            return model
        
        # Don't start multiple loading processes
        if model_loading:
            logger.info("Model is currently loading, waiting...")
            return None
        
        # Start loading the model in the background
        model_loading = True
        loading_thread = threading.Thread(target=load_model_in_background)
        loading_thread.daemon = True
        loading_thread.start()
        
        logger.info("Model loading started in background thread")
        return None

def apply_nms(predictions, iou_threshold=0.5):
    """
    Applies Non-Maximum Suppression (NMS) to the predictions.
    Returns filtered predictions.
    """
    boxes = predictions[0]['boxes']
    scores = predictions[0]['scores']
    labels = predictions[0]['labels']

    # Apply NMS
    keep = nms(boxes, scores, iou_threshold)

    # Filter results based on NMS
    filtered_boxes = boxes[keep]
    filtered_scores = scores[keep]
    filtered_labels = labels[keep]

    return {
        'boxes': filtered_boxes,
        'scores': filtered_scores,
        'labels': filtered_labels
    }

def extract_highest_confidence_boxes(predictions):
    """
    Extracts and filters the bounding boxes, keeping only the highest confidence box per class.
    """
    class_boxes = {}

    # Group boxes by class
    for i, box in enumerate(predictions['boxes']):
        class_id = predictions['labels'][i].item()
        score = predictions['scores'][i].item()

        # Use a confidence threshold - LOWERED TO ALLOW MORE PREDICTIONS
        if score < 0.01:
            continue

        # If the class is not in the dictionary or the current score is higher than the existing one, update
        if class_id not in class_boxes or class_boxes[class_id]['score'] < score:
            class_boxes[class_id] = {
                'box': box.tolist(),
                'score': score
            }

    # Convert class_boxes to a list for returning
    filtered_boxes = []
    for class_id, data in class_boxes.items():
        x1, y1, x2, y2 = data['box']
        class_name = classes_reverse.get(class_id, f"Unknown-{class_id}")  # Get class name
        filtered_boxes.append({
            'boxes': [x1, y1, x2, y2],
            'label': class_name,
            'score': data['score']
        })
        logger.info(f"Class: {class_name}, Confidence: {data['score']:.4f}, Bounding Box: ({x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f})")

    return filtered_boxes

def predict(image_tensor):
    """Make a prediction using the model"""
    global model
    
    if model is None:
        raise RuntimeError("Model is not loaded yet. Please try again later.")
    
    with torch.no_grad():
        start_time = time.time()
        raw_predictions = model(image_tensor)
        elapsed = time.time() - start_time
        logger.info(f"Raw prediction completed in {elapsed:.2f} seconds")
        
        # Apply Non-Maximum Suppression
        filtered_predictions = apply_nms(raw_predictions, iou_threshold=0.5)
        logger.info(f"NMS applied with iou_threshold=0.5")
        
        # Extract highest confidence box per class
        final_predictions = extract_highest_confidence_boxes(filtered_predictions)
        logger.info(f"Extracted {len(final_predictions)} highest confidence boxes")
        
        return final_predictions

@model_bp.route('/predict', methods=['POST'])
def predict_image():
    try:
        logger.info("Received prediction request")
        
        # Handle potential OPTIONS preflight request
        if request.method == 'OPTIONS':
            logger.info("Handling OPTIONS request for /predict")
            return jsonify({"message": "CORS preflight handled"}), 200
            
        # Ensure model is ready or loading
        current_model = get_model()
        if current_model is None and model_loading:
            logger.warning("Model is still loading, returning 503 Service Unavailable")
            return jsonify({'error': 'Model is still loading. Please try again later.'}), 503
        elif current_model is None:
            logger.error("Failed to load model")
            return jsonify({'error': 'Failed to load model. Please contact support.'}), 500

        # Log request details
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Files in request: {list(request.files.keys())}")
        
        # Get image from request
        if 'image' not in request.files:
            logger.error("No image file found in request")
            return jsonify({'error': 'No image provided', 'received_keys': list(request.files.keys())}), 400
        
        file = request.files['image']
        logger.info(f"Received file: {file.filename}, Content-Type: {file.content_type}")
        
        image_bytes = file.read()
        logger.info(f"Read {len(image_bytes)} bytes from image file")
        
        # Process image
        try:
            start_time = time.time()
            
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            original_width, original_height = image.size
            logger.info(f"Image opened successfully, original size: {original_width}x{original_height}")
            
            # Transform image
            image_tensor = transform(image).unsqueeze(0)
            logger.info(f"Image transformed to tensor with shape: {image_tensor.shape}")
            
            # Get predictions
            with torch.no_grad():
                raw_predictions = model(image_tensor)
                # Log raw prediction details
                logger.info(f"Raw model output: {raw_predictions}")
                logger.info(f"Raw boxes: {raw_predictions[0]['boxes']}")
                logger.info(f"Raw scores: {raw_predictions[0]['scores']}")
                logger.info(f"Raw labels: {raw_predictions[0]['labels']}")
            
            predictions = predict(image_tensor)
            logger.info(f"Processed predictions: {predictions}")
            
            # Scale bounding boxes back to the original image size
            for pred in predictions:
                x1, y1, x2, y2 = pred['boxes']
                # Scale from 512x512 back to original dimensions
                pred['boxes'] = [
                    x1 * (original_width / 512),
                    y1 * (original_height / 512),
                    x2 * (original_width / 512),
                    y2 * (original_height / 512)
                ]
            
            elapsed = time.time() - start_time
            logger.info(f"Total processing time: {elapsed:.2f} seconds")
            
            # If no predictions were found after processing, log this clearly
            if len(predictions) == 0:
                logger.warning("No predictions met the confidence threshold!")
                # Return empty predictions array but with a message in the response
                return jsonify({
                    "predictions": [],
                    "message": "No abnormalities detected with confidence above threshold"
                })
            
            response_data = {"predictions": predictions}
            return jsonify(response_data)
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}", exc_info=True)
            return jsonify({'error': f"Error processing image: {str(e)}"}), 500
        
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {str(e)}")
        return jsonify({'error': str(e)}), 503  # Service Unavailable
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        return jsonify({'error': f"Failed to process image: {str(e)}"}), 500

@model_bp.route('/model-status', methods=['GET'])
def model_status():
    """Check the status of the model loading"""
    global model, model_loading
    
    if model is not None:
        return jsonify({
            "status": "ready",
            "message": "Model is loaded and ready for predictions"
        })
    elif model_loading:
        return jsonify({
            "status": "loading",
            "message": "Model is currently loading, please try again later"
        })
    else:
        return jsonify({
            "status": "not_loaded",
            "message": "Model has not started loading yet"
        })

# Start loading the model in the background on module import
get_model() 