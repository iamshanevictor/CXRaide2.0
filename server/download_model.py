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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("model_downloader")

# Define model download URL - replace with your actual URL
# This should be a public, accessible URL where you've uploaded the model
MODEL_URL = "https://storage.googleapis.com/example-medical-models/IT2_model_epoch_300.pth"
MODEL_FILENAME = "IT2_model_epoch_300.pth"

def download_model(url, target_path):
    """Download a file with progress bar"""
    try:
        start_time = time.time()
        logger.info(f"Downloading model from {url} to {target_path}")
        
        # First check if the file already exists
        if os.path.exists(target_path):
            file_size_mb = os.path.getsize(target_path) / (1024 * 1024)
            logger.info(f"Model file already exists: {target_path} ({file_size_mb:.2f} MB)")
            logger.info(f"Skip download - using existing file")
            return True
            
        # Make a streaming request
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        # Get file size if available
        total_size = int(response.headers.get('content-length', 0))
        total_size_mb = total_size / (1024 * 1024)
        
        # Create progress bar
        logger.info(f"Starting download: {total_size_mb:.2f} MB")
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
        
        # Download the file in chunks
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))
        
        progress_bar.close()
        
        # Verify file was downloaded
        if os.path.exists(target_path):
            file_size_mb = os.path.getsize(target_path) / (1024 * 1024)
            elapsed = time.time() - start_time
            logger.info(f"Model download successful: {target_path} ({file_size_mb:.2f} MB)")
            logger.info(f"Download took {elapsed:.2f} seconds ({file_size_mb/elapsed:.2f} MB/s)")
            return True
        else:
            logger.error(f"Download completed but file not found at {target_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        return False

def main():
    """Main function to run the downloader"""
    logger.info("Starting model download process")
    
    # Get the model path - prefer the script directory but fall back to current working dir
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(script_dir, MODEL_FILENAME)
    
    success = download_model(MODEL_URL, target_path)
    
    if success:
        logger.info("Model download process completed successfully")
        sys.exit(0)
    else:
        logger.error("Model download failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 