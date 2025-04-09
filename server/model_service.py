import torch
import torchvision.models as models
from torchvision import transforms
from torchvision.ops import nms
from PIL import Image, ImageDraw, ImageFont
import io
import os
import time
import threading
from flask import Blueprint, request, jsonify
import logging
import base64

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

# Colors for different classes (RGB)
class_colors = {
    'Cardiomegaly': (255, 100, 100),        # Red
    'Pleural thickening': (100, 100, 255),  # Blue
    'Pulmonary fibrosis': (100, 255, 100),  # Green
    'Pleural effusion': (100, 200, 255),    # Light blue
    'Nodule/Mass': (255, 200, 100),         # Orange
    'Infiltration': (255, 100, 255),        # Purple
    'Consolidation': (200, 200, 100),       # Yellow
    'Atelectasis': (100, 255, 200),         # Teal
    'Pneumothorax': (255, 150, 150),        # Pink
    'default': (255, 255, 255)              # White (fallback)
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

def draw_predictions_on_image(image, predictions):
    """Draw bounding boxes and labels directly on the image"""
    draw = ImageDraw.Draw(image)
    
    # Try to use a nice font, fall back to default if not available
    try:
        # For Windows
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        try:
            # For Linux
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except IOError:
            # Fallback
            font = ImageFont.load_default()
    
    # Draw each prediction box and label
    for pred in predictions:
        box = pred['boxes']
        label = pred['label']
        score = pred['score']
        
        # Get color for this class, or use default
        color = class_colors.get(label, class_colors['default'])
        
        # Convert coordinates to integers
        x1, y1, x2, y2 = [int(coord) for coord in box]
        
        # Draw rectangle with a 3-pixel width
        for i in range(3):
            draw.rectangle([x1-i, y1-i, x2+i, y2+i], outline=color)
        
        # Create label text with confidence percentage
        label_text = f"{label}: {int(score * 100)}%"
        
        # Draw label background
        text_w, text_h = draw.textsize(label_text, font=font) if hasattr(draw, 'textsize') else (len(label_text) * 7, 20)  # Estimate size if textsize not available
        draw.rectangle([x1, y1 - text_h - 4, x1 + text_w + 4, y1], fill=color)
        
        # Draw label text in white
        draw.text((x1 + 2, y1 - text_h - 2), label_text, fill=(255, 255, 255), font=font)
    
    return image

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
            
            # Create a standardized version of the image at 512x512 for display
            # This prevents scaling issues with bounding boxes
            display_image = image.copy()
            display_image = display_image.resize((512, 512), Image.LANCZOS)
            
            # Save a copy of the clean resized image
            clean_display_image = display_image.copy()
            
            # Transform image for model
            image_tensor = transform(image).unsqueeze(0)
            logger.info(f"Image transformed to tensor with shape: {image_tensor.shape}")
            
            with torch.no_grad():
                raw_predictions = model(image_tensor)
                # Log raw prediction details
                logger.info(f"Raw model output: {raw_predictions}")
                logger.info(f"Raw boxes: {raw_predictions[0]['boxes']}")
                logger.info(f"Raw scores: {raw_predictions[0]['scores']}")
                logger.info(f"Raw labels: {raw_predictions[0]['labels']}")
            
            predictions = predict(image_tensor)
            logger.info(f"Processed predictions: {predictions}")
            
            # Create an annotated image with bounding boxes drawn directly on it
            annotated_image = draw_predictions_on_image(display_image, predictions)
            
            # Convert both images to base64 for sending to client
            clean_buffered = io.BytesIO()
            clean_display_image.save(clean_buffered, format="JPEG", quality=90)
            clean_img_str = base64.b64encode(clean_buffered.getvalue()).decode()
            clean_display_image_data = f"data:image/jpeg;base64,{clean_img_str}"
            
            annotated_buffered = io.BytesIO()
            annotated_image.save(annotated_buffered, format="JPEG", quality=90)
            annotated_img_str = base64.b64encode(annotated_buffered.getvalue()).decode()
            annotated_display_image_data = f"data:image/jpeg;base64,{annotated_img_str}"
            
            elapsed = time.time() - start_time
            logger.info(f"Total processing time: {elapsed:.2f} seconds")
            
            # If no predictions were found after processing, log this clearly
            if len(predictions) == 0:
                logger.warning("No predictions met the confidence threshold!")
                # Return empty predictions array but with a message in the response
                return jsonify({
                    "predictions": [],
                    "message": "No abnormalities detected with confidence above threshold",
                    "clean_image": clean_display_image_data,
                    "annotated_image": clean_display_image_data,  # Use clean image since there are no annotations
                    "image_size": {"width": 512, "height": 512}
                })
            
            response_data = {
                "predictions": predictions,
                "clean_image": clean_display_image_data,
                "annotated_image": annotated_display_image_data,
                "image_size": {"width": 512, "height": 512}
            }
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