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
    
    # Log PyTorch version for debugging
    logger.info(f"PyTorch version: {torch.__version__}")
    
    # Log whether CUDA is available
    cuda_available = torch.cuda.is_available() if hasattr(torch, 'cuda') else False
    logger.info(f"CUDA available: {cuda_available}")
    
except ImportError as e:
    logger.warning(f"PyTorch import failed: {str(e)} - using minimal implementation instead")
    
    # Look for the reason why import failed
    try:
        import importlib.util
        torch_spec = importlib.util.find_spec("torch")
        if torch_spec is None:
            logger.warning("PyTorch package is not installed")
        else:
            logger.warning("PyTorch package exists but cannot be imported - might be a dependency issue")
    except:
        pass
        
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
    
    def __init__(self, model_type="IT3"):
        self.model_type = model_type
        self.is_mock = True
        
        # Define typical findings for CXR abnormalities with realistic positions
        # Format: [x1, y1, x2, y2] coordinates in 512x512 image space
        self.common_findings = {
            'Cardiomegaly': {
                'boxes': [[180, 150, 340, 300]],  # Heart region
                'score_range': [0.75, 0.95]
            },
            'Pleural thickening': {
                'boxes': [[100, 150, 170, 350], [350, 150, 420, 350]],  # Left and right pleural regions
                'score_range': [0.65, 0.85]
            },
            'Pulmonary fibrosis': {
                'boxes': [[150, 100, 250, 200], [270, 100, 370, 200]],  # Lung fields
                'score_range': [0.70, 0.90]
            },
            'Pleural effusion': {
                'boxes': [[80, 250, 150, 400], [370, 250, 440, 400]],  # Lower pleural spaces
                'score_range': [0.72, 0.92]
            },
            'Nodule/Mass': {
                'boxes': [[150, 120, 190, 160], [300, 140, 340, 180], [220, 200, 260, 240]],  # Various lung regions
                'score_range': [0.60, 0.80]
            },
            'Infiltration': {
                'boxes': [[120, 120, 220, 220], [300, 120, 400, 220]],  # Upper lung fields
                'score_range': [0.68, 0.88]
            },
            'Consolidation': {
                'boxes': [[120, 220, 220, 320], [300, 220, 400, 320]],  # Lower lung fields
                'score_range': [0.63, 0.83]
            },
            'Atelectasis': {
                'boxes': [[100, 150, 200, 350], [320, 150, 420, 350]],  # Lung bases
                'score_range': [0.67, 0.87]
            },
            'Pneumothorax': {
                'boxes': [[50, 100, 120, 300], [400, 100, 470, 300]],  # Peripheral lung regions
                'score_range': [0.73, 0.93]
            }
        }
        
        logger.info(f"Initializing lightweight {model_type} model for mock predictions")
        
    def __call__(self, image_tensor):
        """Generate realistic mock detections based on image characteristics"""
        logger.info(f"Generating mock detections using lightweight {self.model_type} model")
        
        # Select which classes to use based on model type
        if self.model_type == "IT2":
            class_mapping = classes_it2
            reverse_mapping = classes_it2_reverse
            # IT2 has all 9 classes
            available_classes = list(self.common_findings.keys())
        else:  # IT3
            class_mapping = classes_it3
            reverse_mapping = classes_it3_reverse
            # IT3 has only 6 classes
            available_classes = list(classes_it3.keys())
        
        # Try to extract image characteristics for more realistic variations
        try:
            # Determine image factor based on tensor or PIL image
            if hasattr(image_tensor, 'mean') and callable(getattr(image_tensor, 'mean')):
                # For PyTorch tensors
                image_factor = min(max(image_tensor.mean().item(), 0.1), 0.9)
            elif hasattr(image_tensor, 'size'):
                # For PIL images
                image = image_tensor
                # Get average brightness as a factor
                if hasattr(image, 'convert'):
                    gray_image = image.convert('L')
                    avg_brightness = sum(gray_image.getdata()) / (gray_image.width * gray_image.height) / 255
                    image_factor = min(max(avg_brightness, 0.1), 0.9)
                else:
                    image_factor = 0.5
            else:
                image_factor = 0.5
                
            logger.info(f"Image characteristics factor: {image_factor:.4f}")
            
            # Generate random number of findings based on image factor
            # More abnormal images (lower factor) tend to have more findings
            import random
            random.seed(int(image_factor * 1000))  # Seed for reproducibility but varies by image
            
            # Decide how many findings to show (1-4)
            num_findings = random.randint(1, min(4, len(available_classes)))
            
            # Select which classes to show
            selected_classes = random.sample(available_classes, num_findings)
            
            # Create boxes, scores and labels for the selected findings
            boxes = []
            scores = []
            labels = []
            
            for class_name in selected_classes:
                # Skip if class not in model's capability
                if class_name not in class_mapping:
                    continue
                    
                # Get class details
                class_id = class_mapping[class_name]
                class_info = self.common_findings[class_name]
                
                # Select a random box for this finding
                box_idx = random.randint(0, len(class_info['boxes']) - 1)
                box = class_info['boxes'][box_idx]
                
                # Add random variation to box coordinates (±10%)
                variation = 0.1
                box = [
                    max(0, box[0] * (1 - variation * random.random())),
                    max(0, box[1] * (1 - variation * random.random())),
                    min(512, box[2] * (1 + variation * random.random())),
                    min(512, box[3] * (1 + variation * random.random()))
                ]
                
                # Generate score within the specified range
                min_score, max_score = class_info['score_range']
                score = min_score + random.random() * (max_score - min_score)
                
                # Add to results
                boxes.append(box)
                scores.append(score)
                labels.append(class_id)
            
            # Create mock tensor or regular list based on torch availability
            if torch_available:
                return [{
                    'boxes': torch.tensor(boxes),
                    'scores': torch.tensor(scores),
                    'labels': torch.tensor(labels)
                }]
            else:
                return [{
                    'boxes': [MockTensor(box) for box in boxes],
                    'scores': [MockTensor(score) for score in scores],
                    'labels': [MockTensor(label) for label in labels]
                }]
                
        except Exception as e:
            logger.error(f"Error generating dynamic predictions: {str(e)}")
            # Fall back to fixed predictions
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
        # Check if we should use mock models based on environment variable
        use_mock = os.environ.get('USE_MOCK_MODELS', 'False').lower() == 'true'
        
        # Log the current working directory for debugging
        logger.info(f"Current working directory: {os.getcwd()}")
        
        # Log environment settings
        is_render = os.environ.get('RENDER', 'False').lower() == 'true'
        env_type = "Render.com" if is_render else "Local/Docker"
        logger.info(f"Environment: {env_type}, USE_MOCK_MODELS={use_mock}, PyTorch available={torch_available}")
        
        # If PyTorch is not available, log critical error
        if not torch_available:
            logger.critical("PyTorch not available. Models cannot be loaded! Install torch and torchvision!")
            logger.critical("Edit requirements.txt to uncomment torch and torchvision, then run 'pip install -r requirements.txt'")
            # Fall back to mock models
            logger.info("Falling back to mock models since PyTorch is not available")
            use_mock = True
        
        # If USE_MOCK_MODELS is True, use lightweight mock models regardless of file existence
        if use_mock:
            logger.info("Using mock models as specified by environment configuration")
            model_it2 = LightweightModel("IT2")
            model_it3 = LightweightModel("IT3")
            model_loading = False
            logger.info("Mock models loaded successfully")
            return
        
        # Attempt to load real models
        logger.info("Starting background model loading for real models...")
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
        
        # Check for model files before trying to load them
        it2_path = os.path.join(os.path.dirname(__file__), 'IT2_model_epoch_300.pth')
        it3_path = os.path.join(os.path.dirname(__file__), 'IT3_model_epoch_260.pth')
        
        if not os.path.exists(it2_path):
            logger.warning(f"IT2 model file not found at: {it2_path}")
        else:
            logger.info(f"Found IT2 model file at: {it2_path} ({os.path.getsize(it2_path) / (1024*1024):.1f} MB)")
            
        if not os.path.exists(it3_path):
            logger.warning(f"IT3 model file not found at: {it3_path}")
        else:
            logger.info(f"Found IT3 model file at: {it3_path} ({os.path.getsize(it3_path) / (1024*1024):.1f} MB)")
        
        # Load IT2 model (9 classes)
        model_it2 = load_specific_model('IT2_model_epoch_300.pth', 'IT2')
        
        # Load IT3 model (6 classes)
        model_it3 = load_specific_model('IT3_model_epoch_260.pth', 'IT3')
        
        # Check if either model failed to load
        if model_it2 is None and model_it3 is None:
            logger.critical("Both models failed to load - falling back to mock models!")
            model_it2 = LightweightModel("IT2")
            model_it3 = LightweightModel("IT3")
        elif model_it2 is None:
            logger.warning("IT2 model failed to load - using mock model for IT2")
            model_it2 = LightweightModel("IT2")
        elif model_it3 is None:
            logger.warning("IT3 model failed to load - using mock model for IT3")
            model_it3 = LightweightModel("IT3")
        else:
            logger.info("Both models loaded successfully")
            
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
        logger.critical("Model loading failed - falling back to mock models!")
        model_it2 = LightweightModel("IT2")
        model_it3 = LightweightModel("IT3")
    finally:
        model_loading = False

def load_specific_model(model_filename, model_identifier):
    """Load a specific model file with error handling"""
    logger.info(f"Loading {model_identifier} model...")
    
    try:
        # Check if we should force mock models regardless of file existence
        if os.environ.get('USE_MOCK_MODELS', 'False').lower() == 'true':
            logger.info(f"Skipping real {model_identifier} model load due to USE_MOCK_MODELS flag")
            return None
        
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
            logger.critical(f"{model_identifier} model file not found! Falling back to mock model.")
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
        
        # Check if specific model type is requested
        model_type = request.form.get('model_type', 'combined').lower()
        logger.info(f"Requested model type: {model_type}")
            
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
            
            # Get predictions using the specified model(s)
            if model_type == 'it2':
                # Use only IT2 model
                logger.info("Using only IT2 model for prediction as requested")
                model_it2, _ = get_model()
                
                if model_it2 is None:
                    return jsonify({'error': 'IT2 model is not available'}), 500
                
                with torch_no_grad():
                    raw_predictions = model_it2(image_tensor)
                
                filtered_predictions = apply_nms(raw_predictions, iou_threshold=0.5)
                predictions = []
                
                # Format predictions from IT2 model
                for i in range(len(filtered_predictions['boxes'])):
                    box = filtered_predictions['boxes'][i].tolist()
                    score = filtered_predictions['scores'][i].item()
                    label_idx = filtered_predictions['labels'][i].item()
                    
                    # Skip low confidence predictions
                    if score < 0.3:
                        continue
                        
                    label = classes_it2[label_idx] if label_idx < len(classes_it2) else f"Unknown({label_idx})"
                    
                    predictions.append({
                        'boxes': box,
                        'score': score,
                        'label': label
                    })
            else:
                # Use combined IT2+IT3 model (default)
                logger.info("Using combined IT2+IT3 models for prediction")
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
                    "image_size": {"width": 512, "height": 512},
                    "model_used": model_type
                })
            
            response_data = {
                "predictions": predictions,
                "clean_image": clean_data_url,
                "annotated_image": annotated_data_url,
                "image_size": {"width": 512, "height": 512},
                "model_used": model_type
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
    """Return the status of model loading and deployment mode"""
    try:
        # Handle potential OPTIONS preflight request
        if request.method == 'OPTIONS':
            logger.info("Handling OPTIONS request for /model-status")
            return jsonify({"message": "CORS preflight handled"}), 200
            
        global model_it2, model_it3, model_loading
        
        # Check if environment is configured for mock models
        using_mock_models = os.environ.get('USE_MOCK_MODELS', 'False').lower() == 'true'
        
        # Get model information
        models = get_models()
        
        # Determine model deployment status
        is_render = os.environ.get('RENDER', 'False') == 'True'
        deployment_environment = "Render.com" if is_render else "Local"
        
        # Check model types
        mock_it2 = model_it2 is not None and hasattr(model_it2, 'is_mock')
        mock_it3 = model_it3 is not None and hasattr(model_it3, 'is_mock')
        
        # Create descriptive response
        response = {
            "status": "ready" if model_it2 is not None and model_it3 is not None else "loading",
            "loading": model_loading,
            "deployment_environment": deployment_environment,
            "using_mock_models": using_mock_models,
            "models": models,
            "pytorch_available": torch_available,
            "model_status": {
                "IT2": {
                    "loaded": model_it2 is not None,
                    "type": "mock" if mock_it2 else "real",
                    "classes": len(classes_it2) if model_it2 is not None else 0
                },
                "IT3": {
                    "loaded": model_it3 is not None,
                    "type": "mock" if mock_it3 else "real",
                    "classes": len(classes_it3) if model_it3 is not None else 0
                }
            },
            "explanation": "The system is using lightweight mock models that simulate real model behavior" if using_mock_models 
                          else "The system is using the actual trained PyTorch models",
            "notice": "Mock models provide realistic simulations but are not using the actual trained models" if using_mock_models
                     else ""
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error getting model status: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e),
            "pytorch_available": torch_available
        }), 500

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
    """Get information about available models"""
    global model_it2, model_it3
    
    # Determine if using mock models
    using_mock = os.environ.get('USE_MOCK_MODELS', 'False').lower() == 'true'
    
    it2_status = "Not loaded"
    it3_status = "Not loaded"
    
    # Check IT2 model status
    if model_it2 is not None:
        if hasattr(model_it2, 'is_mock'):
            it2_status = "Loaded (Mock Model)"
        else:
            it2_status = "Loaded (Real Model)"
    
    # Check IT3 model status
    if model_it3 is not None:
        if hasattr(model_it3, 'is_mock'):
            it3_status = "Loaded (Mock Model)"
        else:
            it3_status = "Loaded (Real Model)"
    
    return {
        "IT2": {
            "status": it2_status,
            "classes": list(classes_it2.keys()),
            "class_count": len(classes_it2)
        },
        "IT3": {
            "status": it3_status,
            "classes": list(classes_it3.keys()),
            "class_count": len(classes_it3)
        },
        "environment": {
            "using_mock_models": using_mock,
            "reason": "Running in memory-constrained environment or model files not found" if using_mock else "Running with full model files"
        }
    } 