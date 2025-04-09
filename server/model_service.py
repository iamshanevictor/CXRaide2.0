import os
import time
import threading
from flask import Blueprint, request, jsonify
import logging
import base64
import io
from PIL import Image, ImageDraw, ImageFont

# Initialize logger
logger = logging.getLogger(__name__)

model_bp = Blueprint('model', __name__)

# Try importing torch, but provide fallbacks if it fails
torch_available = False
try:
    import torch
    import torchvision.models as models
    from torchvision import transforms
    from torchvision.ops import nms
    torch_available = True
    logger.info("PyTorch successfully imported")
except ImportError:
    logger.warning("PyTorch import failed - this is critical for model functionality!")
    logger.warning("Please install PyTorch by uncommenting it in requirements.txt and running 'pip install -r requirements.txt'")
    # Define minimal tensor class for mock implementation - ONLY used in emergency fallback
    class MockTensor:
        def __init__(self, data):
            self.data = data
        def tolist(self):
            return self.data
        def item(self):
            return self.data[0] if isinstance(self.data, list) else self.data

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
if torch_available:
    transform = transforms.Compose([
        transforms.Resize((512, 512)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
else:
    # Fallback transform function that doesn't require torchvision
    # This should never be used in production!
    def transform(image):
        """Simple transform function that resizes the image"""
        logger.critical("Using fallback transform function - THIS WILL NOT WORK PROPERLY!")
        # Resize image to 512x512
        resized_image = image.resize((512, 512))
        return resized_image

# Load model
model = None
model_loading = False
model_load_lock = threading.Lock()

def load_model_in_background():
    """Load model in a background thread to avoid blocking the app startup"""
    global model, model_loading
    
    try:
        # If PyTorch is not available, log critical error
        if not torch_available:
            logger.critical("PyTorch not available. Model cannot be loaded! Install torch and torchvision!")
            logger.critical("Edit requirements.txt to uncomment torch and torchvision, then run 'pip install -r requirements.txt'")
            return
        
        logger.info("Starting background model loading...")
        start_time = time.time()
        
        # Create model
        temp_model = models.detection.ssd300_vgg16(weights=None)
        
        # Check multiple possible locations for the model file, with most likely first
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'IT2_model_epoch_300.pth'),  # Current directory (most likely)
            'IT2_model_epoch_300.pth',                                           # Relative to working directory
            '../IT2_model_epoch_300.pth',                                        # Parent directory
            '/app/IT2_model_epoch_300.pth',                                      # Docker container root
            '/app/server/IT2_model_epoch_300.pth',                               # Docker container server dir
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'IT2_model_epoch_300.pth'),  # Project root
        ]
        
        model_path = None
        for path in possible_paths:
            if os.path.exists(path):
                model_path = path
                logger.info(f"Found model file at: {model_path}")
                break
        
        if not model_path:
            logger.critical("Model file not found! Application will not work correctly.")
            logger.critical(f"Searched paths: {possible_paths}")
            logger.critical(f"Current working directory: {os.getcwd()}")
            logger.critical(f"Directory contents: {os.listdir('.')}")
            if '__file__' in globals():
                logger.critical(f"Module directory: {os.path.dirname(__file__)}")
                logger.critical(f"Module directory contents: {os.listdir(os.path.dirname(__file__))}")
            # Do NOT create a mock model - fail properly
            return
        
        # Load weights
        file_size_mb = os.path.getsize(model_path) / (1024 * 1024)
        logger.info(f"Loading model weights from {model_path} (Size: {file_size_mb:.2f} MB)...")
        
        # Load the model with device mapping
        state_dict = torch.load(model_path, map_location=torch.device('cpu'))
        temp_model.load_state_dict(state_dict)
        temp_model.eval()
        
        # Update the global model variable
        model = temp_model
        
        elapsed = time.time() - start_time
        logger.info(f"Model loaded successfully in {elapsed:.2f} seconds")
    except Exception as e:
        logger.critical(f"Failed to load model in background: {str(e)}", exc_info=True)
        logger.critical("Model loading failed - application will not work correctly!")
        model = None
    finally:
        model_loading = False

class MockModel:
    """A mock model class that returns fixed predictions - THIS SHOULD NEVER BE USED IN PRODUCTION"""
    
    def __init__(self):
        self.mock_type = "emergency_fallback"
        logger.critical("EMERGENCY FALLBACK: Using mock model - PREDICTIONS WILL NOT BE REAL!")
        logger.critical("Install PyTorch and ensure model file exists at the correct location")
    
    def __call__(self, input_tensor):
        """Return mock predictions when the model is called"""
        logger.critical("WARNING: Using mock predictions instead of real model!")
        
        # Create demo predictions with fixed but realistic values
        if torch_available:
            # Use real torch tensors if available
            mock_predictions = [
                {
                    'boxes': torch.tensor([
                        [100.0, 150.0, 300.0, 350.0],  # Nodule
                        [200.0, 100.0, 450.0, 350.0],  # Cardiomegaly 
                        [50.0, 300.0, 150.0, 400.0]    # Effusion
                    ]),
                    'scores': torch.tensor([0.87, 0.92, 0.78]),
                    'labels': torch.tensor([5, 1, 4])  # Corresponding to classes
                }
            ]
        else:
            # Use mock tensor implementation
            mock_predictions = [
                {
                    'boxes': [
                        MockTensor([100.0, 150.0, 300.0, 350.0]),  # Nodule
                        MockTensor([200.0, 100.0, 450.0, 350.0]),  # Cardiomegaly 
                        MockTensor([50.0, 300.0, 150.0, 400.0])    # Effusion
                    ],
                    'scores': [
                        MockTensor(0.87), 
                        MockTensor(0.92), 
                        MockTensor(0.78)
                    ],
                    'labels': [
                        MockTensor(5), 
                        MockTensor(1), 
                        MockTensor(4)
                    ]  # Corresponding to classes
                }
            ]
        
        return mock_predictions
    
    def eval(self):
        """Mock eval method"""
        return self

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

def predict(input_tensor):
    """Process model predictions and format the results"""
    try:
        get_model()  # Ensure model is loaded
        
        if model is None:
            logger.error("Model not available for prediction")
            return []
            
        # Get raw predictions from model
        with torch_no_grad():
            raw_predictions = model(input_tensor)
            
        # Apply NMS if using a real torch model
        if not hasattr(model, 'mock_type'):
            filtered_predictions = apply_nms(raw_predictions)
        else:
            # Skip NMS for mock predictions
            filtered_predictions = raw_predictions[0]
        
        # Extract highest confidence boxes
        formatted_predictions = extract_highest_confidence_boxes(filtered_predictions)
        
        return formatted_predictions
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return []

def torch_no_grad():
    """Context manager to disable gradient calculation - with torch fallback"""
    if torch_available:
        return torch.no_grad()
    else:
        # Simple context manager that does nothing when torch isn't available
        class NoOpContextManager:
            def __enter__(self): 
                return None
            def __exit__(self, exc_type, exc_val, exc_tb): 
                pass
        return NoOpContextManager()

def extract_highest_confidence_boxes(predictions):
    """
    Extracts and filters the bounding boxes, keeping only the highest confidence box per class.
    """
    class_boxes = {}

    # Handle both torch tensor and mock implementation
    try:
        # Group boxes by class
        if torch_available and not hasattr(predictions['boxes'], '__iter__'):
            # Handle torch tensor case
            boxes = predictions['boxes']
            scores = predictions['scores'] 
            labels = predictions['labels']
            
            for i in range(len(boxes)):
                box = boxes[i]
                class_id = labels[i].item() if hasattr(labels[i], 'item') else labels[i]
                score = scores[i].item() if hasattr(scores[i], 'item') else scores[i]
                
                # Use a confidence threshold
                if score < 0.01:
                    continue
                    
                # If the class is not in the dictionary or the current score is higher than the existing one, update
                if class_id not in class_boxes or class_boxes[class_id]['score'] < score:
                    class_boxes[class_id] = {
                        'box': box.tolist() if hasattr(box, 'tolist') else box,
                        'score': score
                    }
        else:
            # Handle list case (for mock implementation)
            boxes = predictions['boxes']
            scores = predictions['scores']
            labels = predictions['labels']
            
            for i in range(len(boxes)):
                box = boxes[i]
                class_id = labels[i].item() if hasattr(labels[i], 'item') else labels[i]
                score = scores[i].item() if hasattr(scores[i], 'item') else scores[i]
                
                # Use a confidence threshold
                if score < 0.01:
                    continue
                    
                # If the class is not in the dictionary or the current score is higher than the existing one, update
                if class_id not in class_boxes or class_boxes[class_id]['score'] < score:
                    class_boxes[class_id] = {
                        'box': box.tolist() if hasattr(box, 'tolist') else box,
                        'score': score
                    }
    except Exception as e:
        logger.error(f"Error extracting predictions: {str(e)}")
        return []

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
            
        # Check if PyTorch is available
        if not torch_available:
            logger.critical("PyTorch is not available - cannot process predictions!")
            return jsonify({
                'error': 'PyTorch is not installed on the server. Please install PyTorch by uncommenting it in requirements.txt.',
                'fix': 'The server administrator needs to uncomment torch and torchvision in requirements.txt and run pip install -r requirements.txt'
            }), 500
            
        # Ensure model is ready or loading
        current_model = get_model()
        if current_model is None and model_loading:
            logger.warning("Model is still loading, returning 503 Service Unavailable")
            return jsonify({'error': 'Model is still loading. Please try again later.'}), 503
        elif current_model is None:
            logger.error("Failed to load model")
            return jsonify({
                'error': 'Failed to load model. Check server logs for details.',
                'details': 'The model file may be missing or corrupted. Ensure IT2_model_epoch_300.pth exists in the server directory.'
            }), 500

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
            
            # Get predictions using the real model
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
        return jsonify({'error': str(e), 'fix': 'Ensure the model file IT2_model_epoch_300.pth exists in the server directory'}), 503  # Service Unavailable
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        return jsonify({'error': f"Failed to process image: {str(e)}"}), 500

@model_bp.route('/model-status', methods=['GET'])
def model_status():
    """Check the status of the model loading"""
    global model, model_loading
    
    # Check if PyTorch is available
    if not torch_available:
        return jsonify({
            "status": "error",
            "model_type": "none",
            "message": "PyTorch not installed. Cannot load or use model.",
            "error": "PyTorch is not installed. Edit requirements.txt to uncomment torch/torchvision and run pip install."
        }), 500
    
    if model is not None:
        # Check if it's a mock model - which should now only happen in emergency situations
        if hasattr(model, 'mock_type'):
            return jsonify({
                "status": "warning",
                "model_type": "emergency_fallback",
                "message": "WARNING: Using emergency fallback mock model - PREDICTIONS ARE NOT REAL",
                "warning": "This is an EMERGENCY MOCK model. Real model file was not found or failed to load."
            }), 200
        
        # Get model file information if possible
        model_info = {}
        for model_path in [
            os.path.join(os.path.dirname(__file__), 'IT2_model_epoch_300.pth'),
            'IT2_model_epoch_300.pth',
        ]:
            if os.path.exists(model_path):
                model_info["file_path"] = model_path
                model_info["file_size_mb"] = round(os.path.getsize(model_path) / (1024 * 1024), 2)
                model_info["last_modified"] = time.ctime(os.path.getmtime(model_path))
                break
                
        # Return success with model info
        return jsonify({
            "status": "ready",
            "model_type": "real",
            "message": "Model is loaded and ready for predictions",
            "model_info": model_info,
            "support_classes": list(classes.keys())
        }), 200
    elif model_loading:
        return jsonify({
            "status": "loading",
            "message": "Model is currently loading, please try again later"
        }), 200
    else:
        # Get model existence info
        model_file_exists = False
        model_path = None
        for path in [
            os.path.join(os.path.dirname(__file__), 'IT2_model_epoch_300.pth'),
            'IT2_model_epoch_300.pth',
        ]:
            if os.path.exists(path):
                model_file_exists = True
                model_path = path
                break
        
        if model_file_exists:
            return jsonify({
                "status": "not_loaded",
                "message": "Model file exists but has not started loading yet. Try accessing an endpoint that uses the model.",
                "model_path": model_path
            }), 200
        else:
            return jsonify({
                "status": "missing",
                "message": "Model file not found. Please ensure IT2_model_epoch_300.pth is in the correct location.",
                "searched_paths": [
                    os.path.join(os.path.dirname(__file__), 'IT2_model_epoch_300.pth'),
                    'IT2_model_epoch_300.pth',
                    os.getcwd()
                ]
            }), 404

# Start loading the model in the background on module import
get_model() 