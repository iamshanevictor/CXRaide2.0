#!/usr/bin/env python3
"""
Model Downloader for CXRaide

This script downloads the PyTorch model file from a specified URL
during the build process on render.com or other deployment platforms.
"""

import os
import sys
import time
import logging
import requests
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MODEL_FILENAME = "IT2_model_epoch_300.pth"
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
GITHUB_URL = "https://github.com/iamshanevictor/CXRaide2.0/raw/Docker/server/IT2_model_epoch_300.pth"

def download_file(url, destination):
    """
    Download a file from a URL to a destination path with progress bar
    """
    try:
        logger.info(f"Downloading model from {url} to {destination}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file size for progress bar
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        
        # Show progress during download
        t = tqdm(total=total_size, unit='iB', unit_scale=True)
        
        with open(destination, 'wb') as f:
            for data in response.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        t.close()
        
        # Check if download was complete
        if total_size != 0 and t.n != total_size:
            logger.error("Downloaded file size does not match expected size")
            return False
            
        logger.info(f"Successfully downloaded model to {destination}")
        return True
        
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        return False

def download_model():
    """
    Download the model file if it doesn't exist
    """
    if os.path.exists(MODEL_PATH):
        logger.info(f"Model already exists at {MODEL_PATH}")
        file_size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        logger.info(f"Model file size: {file_size_mb:.2f} MB")
        return MODEL_PATH
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    # Only try to download if the file doesn't exist locally
    logger.warning(f"Model file not found at {MODEL_PATH}, attempting to download")
    
    # Try direct GitHub download
    if download_file(GITHUB_URL, MODEL_PATH):
        logger.info("Successfully downloaded model from GitHub")
        return MODEL_PATH
    
    logger.error("Failed to download model from all sources")
    return None

def main():
    """Main function to run the downloader"""
    logger.info("Starting model download process")
    
    model_path = download_model()
    
    if model_path:
        logger.info("Model download process completed successfully")
        sys.exit(0)
    else:
        logger.error("Model download failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 