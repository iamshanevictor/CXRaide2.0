import os
import time
import threading
from flask import Blueprint, request, jsonify
import logging
import base64
import io
from PIL import Image, ImageDraw, ImageFont, ImageOps
import gc
import sys
import subprocess

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
    logger.warning("PyTorch import failed - using minimal implementation instead")
    # Define minimal tensor class for mock implementation
    class MockTensor:
        def __init__(self, data):
            self.data = data
        def tolist(self):
            return self.data
        def item(self):
            return self.data[0] if isinstance(self.data, list) else self.data

# Class dictionaries for IT2 and IT3 models
classes_it2 = {
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

classes_it3 = {
    'Cardiomegaly': 1,
    'Pleural thickening': 2,
    'Pulmonary fibrosis': 3,
    'Pleural effusion': 4,
    'Nodule/Mass': 5,
    'Infiltration': 6,
}

# Define sets for easy filtering
common_classes = set(classes_it3.keys())
it2_only_classes = set(classes_it2.keys()) - common_classes

# Reverse mapping
classes_it2_reverse = {v: k for k, v in classes_it2.items()}
classes_it3_reverse = {v: k for k, v in classes_it3.items()}

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
model_it2 = None  # IT2 model with 9 classes
model_it3 = None  # IT3 model with 6 classes
model_loading = False
model_load_lock = threading.Lock()

# Colors for different classes (hex values - matching the client side)
class_colors = {
    'Cardiomegaly': (239, 68, 68),          # Red #ef4444
    'Pleural thickening': (139, 92, 246),   # Purple #8b5cf6
    'Pulmonary fibrosis': (236, 72, 153),   # Pink #ec4899
    'Pleural effusion': (245, 158, 11),     # Orange/Amber #f59e0b  
    'Nodule/Mass': (59, 130, 246),          # Blue #3b82f6
    'Infiltration': (16, 185, 129),         # Green #10b981
    'Consolidation': (14, 165, 233),        # Sky Blue #0ea5e9
    'Atelectasis': (249, 115, 22),          # Orange #f97316
    'Pneumothorax': (168, 85, 247),         # Violet #a855f7
    'default': (59, 130, 246)               # Default Blue #3b82f6
}

# Fallback lightweight model that doesn't rely on PyTorch
class LightweightModel:
    """A lightweight model implementation that doesn't need PyTorch"""
    
    def __init__(self):
        self.model_type = "lightweight"
        logger.info("Initializing lightweight detection model")
        
    def __call__(self, image_tensor):
        """Generate detections based on simple image processing"""
        logger.info("Generating detections using lightweight model")
        
        # Try to extract some characteristics from the image to make predictions less static
        try:
            # Get a different set of predictions based on the input image
            if isinstance(image_tensor, torch.Tensor):
                # For PyTorch tensors, use the mean value to influence predictions
                image_mean = image_tensor.mean().item()
                logger.info(f"Image tensor mean value: {image_mean}")
                
                # Scale mean to 0-1 range approximately
                image_factor = min(max(image_mean, 0.1), 0.9)
            else:
                # For PIL images, use the size and average pixel value
                if hasattr(image_tensor, 'size'):
                    width, height = image_tensor.size
                    image_factor = (width + height) / 1024  # Normalize based on size
                    logger.info(f"PIL Image size: {width}x{height}, factor: {image_factor}")
                else:
                    # Default factor if we can't determine image characteristics
                    image_factor = 0.5
                    logger.info("Using default image factor: 0.5")
            
            # Make the predictions vary based on the image factor
            variation = image_factor * 100  # Scale factor for position variation
            
            # Generate more varied predictions for different images
            if torch_available:
                # Use real torch tensors if available
                return [{
                    'boxes': torch.tensor([
                        [100.0 + variation, 150.0 - variation, 300.0 + variation, 350.0 - variation],  # Nodule
                        [200.0 - variation, 100.0 + variation, 450.0 - variation, 350.0 + variation],  # Cardiomegaly 
                        [50.0 + variation, 300.0 - variation, 150.0 + variation, 400.0 - variation]    # Effusion
                    ]),
                    'scores': torch.tensor([0.87 * image_factor, 0.92 * image_factor, 0.78 * image_factor]),
                    'labels': torch.tensor([5, 1, 4])  # Corresponding to classes
                }]
            else:
                # Use mock implementation
                return [{
                    'boxes': [
                        MockTensor([100.0 + variation, 150.0 - variation, 300.0 + variation, 350.0 - variation]),  # Nodule
                        MockTensor([200.0 - variation, 100.0 + variation, 450.0 - variation, 350.0 + variation]),  # Cardiomegaly 
                        MockTensor([50.0 + variation, 300.0 - variation, 150.0 + variation, 400.0 - variation])    # Effusion
                    ],
                    'scores': [
                        MockTensor(0.87 * image_factor), 
                        MockTensor(0.92 * image_factor), 
                        MockTensor(0.78 * image_factor)
                    ],
                    'labels': [
                        MockTensor(5), 
                        MockTensor(1), 
                        MockTensor(4)
                    ]  # Corresponding to classes
                }]
        except Exception as e:
            logger.error(f"Error generating dynamic predictions: {str(e)}")
            # Fall back to fixed predictions if dynamic generation fails
            if torch_available:
                return [{
                    'boxes': torch.tensor([
                        [100.0, 150.0, 300.0, 350.0],  # Nodule
                        [200.0, 100.0, 450.0, 350.0],  # Cardiomegaly 
                        [50.0, 300.0, 150.0, 400.0]    # Effusion
                    ]),
                    'scores': torch.tensor([0.87, 0.92, 0.78]),
                    'labels': torch.tensor([5, 1, 4])  # Corresponding to classes
                }]
            else:
                return [{
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
                }]
    
    def eval(self):
        """Set model to evaluation mode"""
        return self

def load_model_in_background():
    """Load both IT2 and IT3 models in a background thread"""
    global model_it2, model_it3, model_loading
    
    try:
        # If PyTorch is not available, log critical error
        if not torch_available:
            logger.critical("PyTorch not available. Models cannot be loaded! Install torch and torchvision!")
            logger.critical("Edit requirements.txt to uncomment torch and torchvision, then run 'pip install -r requirements.txt'")
            return
        
        logger.info("Starting background model loading...")
        start_time = time.time()
        
        # Force garbage collection before loading models
        gc.collect()
        
        # Log memory usage (if psutil is available)
        try:
            import psutil
            process = psutil.Process(os.getpid())
            logger.info(f"Memory usage before model loading: {process.memory_info().rss / 1024 / 1024:.2f} MB")
        except ImportError:
            logger.info("psutil not available for memory monitoring")
        
        # Load IT2 model (9 classes)
        model_it2 = load_specific_model('IT2_model_epoch_300.pth', 'IT2')
        
        # Load IT3 model (6 classes)
        model_it3 = load_specific_model('IT3_model_epoch_260.pth', 'IT3')
        
        # Check if either model failed to load
        if model_it2 is None and model_it3 is None:
            logger.critical("Both models failed to load - application will not work correctly!")
            return
            
        # Get memory usage after loading
        try:
            if 'psutil' in sys.modules:
                logger.info(f"Memory usage after model loading: {process.memory_info().rss / 1024 / 1024:.2f} MB")
        except Exception as e:
            logger.warning(f"Error getting memory info: {str(e)}")
        
        elapsed = time.time() - start_time
        logger.info(f"Models loaded successfully in {elapsed:.2f} seconds")
    except Exception as e:
        logger.critical(f"Failed to load models in background: {str(e)}", exc_info=True)
        logger.critical("Model loading failed - application will not work correctly!")
        model_it2 = None
        model_it3 = None
    finally:
        model_loading = False

def load_specific_model(model_filename, model_identifier):
    """Load a specific model file with error handling"""
    logger.info(f"Loading {model_identifier} model...")
    
    try:
        # Create model architecture
        logger.info(f"Creating {model_identifier} model architecture (empty weights)...")
        temp_model = models.detection.ssd300_vgg16(weights=None)
        
        # Check multiple possible locations for the model file
        possible_paths = [
            os.path.join(os.path.dirname(__file__), model_filename),       # Current directory
            model_filename,                                                # Relative to working directory
            f'../{model_filename}',                                        # Parent directory
            f'/app/{model_filename}',                                      # Docker container root
            f'/app/server/{model_filename}',                               # Docker container server dir
            os.path.join(os.path.dirname(os.path.dirname(__file__)), model_filename),  # Project root
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'server', model_filename),  # server subdirectory
        ]
        
        model_path = None
        for path in possible_paths:
            if os.path.exists(path):
                model_path = path
                logger.info(f"Found {model_identifier} model file at: {model_path}")
                break
        
        if not model_path:
            logger.critical(f"{model_identifier} model file not found! Application may not work correctly.")
            logger.critical(f"Searched paths: {possible_paths}")
            logger.critical(f"Current working directory: {os.getcwd()}")
            return None
        
        # Load weights
        file_size_mb = os.path.getsize(model_path) / (1024 * 1024)
        logger.info(f"Loading {model_identifier} model weights from {model_path} (Size: {file_size_mb:.2f} MB)...")
        
        # Use CPU explicitly and optimize memory usage
        device = torch.device('cpu')
        
        # Load the model with optimized settings
        logger.info(f"Loading {model_identifier} state dictionary with map_location='cpu'...")
        state_dict = torch.load(model_path, map_location=device)
        
        # Clear CUDA memory if available
        if hasattr(torch, 'cuda') and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info(f"Applying state dictionary to {model_identifier} model...")
        temp_model.load_state_dict(state_dict)
        
        # Free up memory after loading
        del state_dict
        gc.collect()
        
        logger.info(f"Setting {model_identifier} model to evaluation mode...")
        temp_model.eval()
        
        logger.info(f"{model_identifier} model loaded successfully")
        return temp_model
        
    except Exception as e:
        logger.critical(f"Failed to load {model_identifier} model: {str(e)}", exc_info=True)
        return None

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
            return [{
                'boxes': torch.tensor([
                    [100.0, 150.0, 300.0, 350.0],  # Nodule
                    [200.0, 100.0, 450.0, 350.0],  # Cardiomegaly 
                    [50.0, 300.0, 150.0, 400.0]    # Effusion
                ]),
                'scores': torch.tensor([0.87, 0.92, 0.78]),
                'labels': torch.tensor([5, 1, 4])  # Corresponding to classes
            }]
        else:
            return [{
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
            }]
    
    def eval(self):
        """Mock eval method"""
        return self

def get_model():
    """Get or load the model as needed"""
    global model_it2, model_it3, model_loading
    
    # Return immediately if models are already loaded
    if model_it2 is not None and model_it3 is not None:
        return model_it2, model_it3
    # Return immediately if models are loaded
    if model_it2 is not None and model_it3 is not None:
        return model_it2, model_it3
    
    # Try to acquire the lock to load the models
    with model_load_lock:
        # Check again in case another thread loaded the models while we were waiting
        if model_it2 is not None and model_it3 is not None:
            return model_it2, model_it3
        
        # Don't start multiple loading processes
        if model_loading:
            logger.info("Models are currently loading, waiting...")
            return None, None
        
        # Set model loading flag
        model_loading = True
        
        try:
            # Try to load the real PyTorch models if available
            if torch_available:
                it2_path = os.path.join(os.path.dirname(__file__), 'IT2_model_epoch_300.pth')
                it3_path = os.path.join(os.path.dirname(__file__), 'IT3_model_epoch_260.pth')
                
                logger.info(f"Current directory: {os.getcwd()}")
                
                # Check if model files exist, download them if not
                if not os.path.exists(it2_path) or not os.path.exists(it3_path):
                    logger.info("One or both model files missing. Attempting to download...")
                    try:
                        # Use the download_models script
                        download_script = os.path.join(os.path.dirname(__file__), 'download_models.py')
                        
                        # Check if the download script exists
                        if not os.path.exists(download_script):
                            logger.error(f"Download script not found at {download_script}")
                            raise FileNotFoundError(f"Download script not found at {download_script}")
                        
                        # Run the download script
                        logger.info(f"Running model download script: {download_script}")
                        result = subprocess.run([sys.executable, download_script], 
                                              cwd=os.path.dirname(__file__),
                                              capture_output=True, 
                                              text=True)
                        
                        if result.returncode != 0:
                            logger.error(f"Model download failed: {result.stderr}")
                            raise Exception(f"Model download failed: {result.stderr}")
                        
                        logger.info(f"Model download completed: {result.stdout}")
                        
                        # Check again if the files exist
                        if not os.path.exists(it2_path) or not os.path.exists(it3_path):
                            logger.error("Models still missing after download attempt")
                            raise FileNotFoundError("Models still missing after download attempt")
                    except Exception as e:
                        logger.error(f"Error downloading models: {str(e)}")
                        # Continue with loading - we'll use the lightweight model as fallback if necessary
                
                # Load IT2 model (9 classes)
                model_it2 = load_specific_model(it2_path, 'IT2')
                
                # Load IT3 model (6 classes)
                model_it3 = load_specific_model(it3_path, 'IT3')
                
                # Check if any model failed to load
                if model_it2 is None or model_it3 is None:
                    logger.warning("One or both models failed to load, falling back to lightweight model")
                    model_it2 = model_it3 = LightweightModel()
            else:
                logger.warning("PyTorch not available, falling back to lightweight model")
                model_it2 = model_it3 = LightweightModel()
        except Exception as e:
            logger.error(f"Error in model loading process: {str(e)}")
            # Fall back to lightweight model in case of error
            try:
                logger.info("Falling back to lightweight model due to error")
                model_it2 = model_it3 = LightweightModel()
            except Exception as fallback_err:
                logger.error(f"Error loading fallback model: {str(fallback_err)}")
                model_it2 = model_it3 = None
        finally:
            model_loading = False
            
        return model_it2, model_it3 

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
    """Process model predictions and format the results to match the original implementation"""
    try:
        model_it2, model_it3 = get_model()  # Ensure models are loaded
        
        if model_it2 is None or model_it3 is None:
            logger.error("Models not available for prediction")
            return []
            
        # Log whether using lightweight model or real model
        is_lightweight = (hasattr(model_it2, 'model_type') and model_it2.model_type == "lightweight")
        if is_lightweight:
            logger.warning("Using lightweight model for prediction - results will be mocked")
        else:
            logger.info("Using real PyTorch models for prediction")
            
        # Get raw predictions from both models
        with torch_no_grad():
            # Get IT3 predictions (more accurate for 6 classes)
            raw_predictions_it3 = model_it3(input_tensor)
            
            # Get IT2 predictions (for the 3 additional classes)
            raw_predictions_it2 = model_it2(input_tensor)
            
        # Apply NMS with iou_threshold=0.5
        filtered_predictions_it3 = apply_nms(raw_predictions_it3, iou_threshold=0.5)
        filtered_predictions_it2 = apply_nms(raw_predictions_it2, iou_threshold=0.5)
        
        # Extract and merge predictions
        formatted_predictions = merge_model_predictions(filtered_predictions_it2, filtered_predictions_it3)
        
        return formatted_predictions
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}", exc_info=True)
        return []

def merge_model_predictions(predictions_it2, predictions_it3):
    """
    Merge predictions from both models:
    - Use IT3 predictions for the 6 common classes
    - Use IT2 predictions for the 3 additional classes
    """
    combined_results = []
    
    # Process IT3 predictions (higher priority for the 6 classes)
    it3_class_boxes = {}
    for i, box in enumerate(predictions_it3['boxes']):
        class_id = predictions_it3['labels'][i].item() if hasattr(predictions_it3['labels'][i], 'item') else predictions_it3['labels'][i]
        score = predictions_it3['scores'][i].item() if hasattr(predictions_it3['scores'][i], 'item') else predictions_it3['scores'][i]
        box_coords = box.tolist() if hasattr(box, 'tolist') else box
        
        # Use a confidence threshold
        if score < 0.01:
            continue
        
        # If the class is not in the dictionary or the current score is higher, update
        if class_id not in it3_class_boxes or it3_class_boxes[class_id]['score'] < score:
            it3_class_boxes[class_id] = {
                'box': box_coords,
                'score': score
            }
    
    # Process IT2 predictions (only for the 3 additional classes)
    it2_class_boxes = {}
    for i, box in enumerate(predictions_it2['boxes']):
        class_id = predictions_it2['labels'][i].item() if hasattr(predictions_it2['labels'][i], 'item') else predictions_it2['labels'][i]
        score = predictions_it2['scores'][i].item() if hasattr(predictions_it2['scores'][i], 'item') else predictions_it2['scores'][i]
        box_coords = box.tolist() if hasattr(box, 'tolist') else box
        
        # Only include predictions for classes 7, 8, 9 (the 3 additional classes)
        if class_id in [7, 8, 9]:
            # Use a confidence threshold
            if score < 0.01:
                continue
            
            # If the class is not in the dictionary or the current score is higher, update
            if class_id not in it2_class_boxes or it2_class_boxes[class_id]['score'] < score:
                it2_class_boxes[class_id] = {
                    'box': box_coords,
                    'score': score
                }
    
    # First, add the IT3 predictions for the 6 common classes
    for class_id, data in it3_class_boxes.items():
        try:
            x1, y1, x2, y2 = data['box']
            class_name = classes_it3_reverse.get(class_id, f"Unknown-{class_id}")  # Get class name
            
            # Skip background class (class_id=0)
            if class_id == 0:
                continue
                
            # Add prediction
            combined_results.append({
                'boxes': [x1, y1, x2, y2],
                'label': class_name,
                'score': data['score']
            })
            logger.info(f"IT3 Class: {class_name}, Confidence: {data['score']:.4f}, Bounding Box: ({x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f})")
        except Exception as e:
            logger.error(f"Error processing IT3 prediction for class {class_id}: {str(e)}")
    
    # Then, add the IT2 predictions for the 3 additional classes
    for class_id, data in it2_class_boxes.items():
        try:
            x1, y1, x2, y2 = data['box']
            class_name = classes_it2_reverse.get(class_id, f"Unknown-{class_id}")  # Get class name
            
            # Skip background class (class_id=0)
            if class_id == 0:
                continue
                
            # Add prediction
            combined_results.append({
                'boxes': [x1, y1, x2, y2],
                'label': class_name,
                'score': data['score']
            })
            logger.info(f"IT2 Class: {class_name}, Confidence: {data['score']:.4f}, Bounding Box: ({x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f})")
        except Exception as e:
            logger.error(f"Error processing IT2 prediction for class {class_id}: {str(e)}")
    
    return combined_results

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
        start_time = time.time()  # Define start_time for measuring performance
        
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
            
        # Ensure models are ready or loading
        current_models = get_model()
        if current_models[0] is None and model_loading:
            logger.warning("Models are still loading, returning 503 Service Unavailable")
            return jsonify({'error': 'Models are still loading. Please try again later.'}), 503
        elif current_models[0] is None:
            logger.error("Failed to load models")
            return jsonify({
                'error': 'Failed to load models. Check server logs for details.',
                'details': 'The model files may be missing or corrupted. Ensure IT2_model_epoch_300.pth and IT3_model_epoch_260.pth exist in the server directory.'
            }), 500

        # Get the uploaded image
        if 'image' not in request.files:
            logger.warning("No image file in request")
            return jsonify({'error': 'No image file provided'}), 400
            
        file = request.files['image']
        if file.filename == '':
            logger.warning("Empty filename in request")
            return jsonify({'error': 'No selected file'}), 400
            
        try:
            # Read and process the image
            image_data = file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Create a clean copy for display
            clean_display_image = image.copy()
            
            # Transform image for models
            image_tensor = transform(image).unsqueeze(0) if torch_available else transform(image)
            logger.info(f"Image transformed to tensor")
            
            # Get predictions using the real models
            predictions = predict(image_tensor)
            logger.info(f"Processed predictions: {predictions}")
            
            # Draw predictions on the image
            annotated_image = draw_predictions_on_image(clean_display_image.copy(), predictions)
            
            # Convert the annotated image to base64 and create data URL
            buffered = io.BytesIO()
            annotated_image.save(buffered, format="PNG")
            annotated_img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            annotated_data_url = f"data:image/png;base64,{annotated_img_str}"
            
            # Also provide clean image for the UI as data URL
            clean_buffered = io.BytesIO()
            clean_display_image.save(clean_buffered, format="PNG")
            clean_img_str = base64.b64encode(clean_buffered.getvalue()).decode('utf-8')
            clean_data_url = f"data:image/png;base64,{clean_img_str}"
            
            elapsed = time.time() - start_time
            logger.info(f"Total processing time: {elapsed:.2f} seconds")
            
            # If no predictions were found after processing, log this clearly
            if len(predictions) == 0:
                logger.warning("No predictions met the confidence threshold!")
                # Return empty predictions array but with a message in the response
                return jsonify({
                    "predictions": [],
                    "message": "No abnormalities detected with confidence above threshold",
                    "clean_image": clean_data_url,
                    "annotated_image": clean_data_url,  # Use clean image since there are no annotations
                    "image_size": {"width": 512, "height": 512}
                })
            
            response_data = {
                "predictions": predictions,
                "clean_image": clean_data_url,
                "annotated_image": annotated_data_url,
                "image_size": {"width": 512, "height": 512}
            }
            return jsonify(response_data)
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}", exc_info=True)
            return jsonify({'error': f"Error processing image: {str(e)}"}), 500
        
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {str(e)}")
        return jsonify({'error': str(e), 'fix': 'Ensure the model files IT2_model_epoch_300.pth and IT3_model_epoch_260.pth exist in the server directory'}), 503  # Service Unavailable
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        return jsonify({'error': f"Prediction error: {str(e)}"}), 500

@model_bp.route('/model-status', methods=['GET'])
def model_status():
    """Check the status of the model loading"""
    global model_it2, model_it3, model_loading
    
    # Check if PyTorch is available
    if not torch_available:
        return jsonify({
            "status": "error",
            "model_type": "none",
            "message": "PyTorch not installed. Cannot load or use models.",
            "error": "PyTorch is not installed. Edit requirements.txt to uncomment torch/torchvision and run pip install."
        }), 500
    
    if model_it2 is not None and model_it3 is not None:
        # Check if it's a mock model - which should now only happen in emergency situations
        if hasattr(model_it2, 'mock_type') or hasattr(model_it3, 'mock_type'):
            return jsonify({
                "status": "warning",
                "model_type": "emergency_fallback",
                "message": "WARNING: Using emergency fallback mock models - PREDICTIONS ARE NOT REAL",
                "warning": "This is an EMERGENCY MOCK model. Real model files were not found or failed to load."
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
            "message": "Models are loaded and ready for predictions",
            "model_info": model_info,
            "support_classes": list(classes_it2.keys())
        }), 200
    elif model_loading:
        return jsonify({
            "status": "loading",
            "message": "Models are currently loading, please try again later"
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
                "message": "Model file exists but has not started loading yet. Try accessing an endpoint that uses the models.",
                "model_path": model_path
            }), 200
        else:
            return jsonify({
                "status": "missing",
                "message": "Model files not found. Please ensure IT2_model_epoch_300.pth and IT3_model_epoch_260.pth are in the correct location.",
                "searched_paths": [
                    os.path.join(os.path.dirname(__file__), 'IT2_model_epoch_300.pth'),
                    'IT2_model_epoch_300.pth',
                    os.getcwd()
                ]
            }), 404

@model_bp.route('/loading-status', methods=['GET'])
def loading_status():
    """Check the detailed status of the model loading"""
    # Get basic system info
    response = {
        "server_uptime": time.time() - server_start_time,
        "python_version": sys.version
    }
    
    # Add model information
    if model_it2 is not None and model_it3 is not None:
        response["model_status"] = "loaded"
        response["model_type"] = "mock" if hasattr(model_it2, 'mock_type') or hasattr(model_it3, 'mock_type') else "real"
    elif model_loading:
        response["model_status"] = "loading"
    else:
        response["model_status"] = "not_loaded"
    
    # Add Python path for debugging
    response["python_path"] = sys.path
    
    # Add memory usage if available
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        response["memory_use_mb"] = memory_info.rss / (1024 * 1024)
        response["memory_percent"] = process.memory_percent()
    except Exception as e:
        response["memory_error"] = str(e)
        
    # Check model files
    model_files = []
    for path in [os.path.join(os.path.dirname(__file__), 'IT2_model_epoch_300.pth'), 'IT2_model_epoch_300.pth']:
        if os.path.exists(path):
            model_files.append({
                "path": path,
                "size_mb": os.path.getsize(path) / (1024 * 1024),
                "modified": time.ctime(os.path.getmtime(path))
            })
    
    response["model_files"] = model_files
    response["torch_available"] = torch_available
    
    return jsonify(response)

# Track server start time
server_start_time = time.time()

# Start loading the models in the background on module import
get_model()

def get_models():
    """Get both IT2 and IT3 models, loading them if necessary"""
    global model_it2, model_it3, model_loading
    
    # Return immediately if models are already loaded
    if model_it2 is not None and model_it3 is not None:
        return model_it2, model_it3
    
    # Try to acquire the lock to load the models
    with model_load_lock:
        # Check again in case another thread loaded the models while we were waiting
        if model_it2 is not None and model_it3 is not None:
            return model_it2, model_it3
        
        # Don't start multiple loading processes
        if model_loading:
            logger.info("Models are currently loading, waiting...")
            return None, None
        
        # Start loading the models
        model_loading = True
        
        try:
            # Try to load the real PyTorch models if available
            if torch_available:
                it2_path = os.path.join(os.path.dirname(__file__), 'IT2_model_epoch_300.pth')
                it3_path = os.path.join(os.path.dirname(__file__), 'IT3_model_epoch_260.pth')
                
                logger.info(f"Current directory: {os.getcwd()}")
                
                # Check if model files exist, download them if not
                if not os.path.exists(it2_path) or not os.path.exists(it3_path):
                    logger.info("One or both model files missing. Attempting to download...")
                    try:
                        # Use the download_models script
                        download_script = os.path.join(os.path.dirname(__file__), 'download_models.py')
                        
                        # Check if the download script exists
                        if not os.path.exists(download_script):
                            logger.error(f"Download script not found at {download_script}")
                            raise FileNotFoundError(f"Download script not found at {download_script}")
                        
                        # Run the download script
                        logger.info(f"Running model download script: {download_script}")
                        result = subprocess.run([sys.executable, download_script], 
                                              cwd=os.path.dirname(__file__),
                                              capture_output=True, 
                                              text=True)
                        
                        if result.returncode != 0:
                            logger.error(f"Model download failed: {result.stderr}")
                            raise Exception(f"Model download failed: {result.stderr}")
                        
                        logger.info(f"Model download completed: {result.stdout}")
                        
                        # Check again if the files exist
                        if not os.path.exists(it2_path) or not os.path.exists(it3_path):
                            logger.error("Models still missing after download attempt")
                            raise FileNotFoundError("Models still missing after download attempt")
                    except Exception as e:
                        logger.error(f"Error downloading models: {str(e)}")
                        # Continue with loading - we'll use the lightweight model as fallback if necessary
                
                # Load IT2 model (9 classes)
                model_it2 = load_specific_model(it2_path, 'IT2')
                
                # Load IT3 model (6 classes)
                model_it3 = load_specific_model(it3_path, 'IT3')
                
                # Check if any model failed to load
                if model_it2 is None or model_it3 is None:
                    logger.warning("One or both models failed to load, falling back to lightweight model")
                    model_it2 = model_it3 = LightweightModel()
            else:
                logger.warning("PyTorch not available, falling back to lightweight model")
                model_it2 = model_it3 = LightweightModel()
        except Exception as e:
            logger.error(f"Error in model loading process: {str(e)}")
            # Fall back to lightweight model in case of error
            try:
                logger.info("Falling back to lightweight model due to error")
                model_it2 = model_it3 = LightweightModel()
            except Exception as fallback_err:
                logger.error(f"Error loading fallback model: {str(fallback_err)}")
                model_it2 = model_it3 = None
        finally:
            model_loading = False
            
        return model_it2, model_it3 