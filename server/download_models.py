#!/usr/bin/env python3
"""
Model Downloader for CXRaide

Downloads both IT2 and IT3 model files from Google Drive.
This script can be used both locally and during deployment to Render.com.
"""

import os
import sys
import time
import requests
from tqdm import tqdm

# Default Google Drive file IDs (can be overridden by environment variables)
IT2_FILE_ID = "1cbvOqEkmhXw-4t1_Reoc29JbVPRF4MNr"
IT3_FILE_ID = "1rd0j7hmw19H02z4vDfWw3Il-s4Xx-zTz"  # Updated IT3 model ID

# Check for environment variables
IT2_FILE_ID = os.environ.get("IT2_MODEL_GOOGLE_DRIVE_ID", IT2_FILE_ID)
IT3_FILE_ID = os.environ.get("IT3_MODEL_GOOGLE_DRIVE_ID", IT3_FILE_ID)

# Model file configurations
MODEL_FILES = [
    {
        "name": "IT2_model_epoch_300.pth",
        "file_id": IT2_FILE_ID
    },
    {
        "name": "IT3_model_epoch_260.pth",
        "file_id": IT3_FILE_ID
    }
]

def download_file_from_google_drive(file_id, destination):
    """
    Download a file from Google Drive directly
    
    Args:
        file_id (str): Google Drive file ID
        destination (str): Destination path to save the file
    
    Returns:
        bool: Whether download was successful
    """
    # Base URL for Google Drive download
    URL = "https://drive.google.com/uc?export=download"
    
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None
    
    def save_response_content(response, destination):
        CHUNK_SIZE = 32768  # 32 KB chunks
        
        # Try to get content length
        total_size = int(response.headers.get('content-length', 0))
        if total_size == 0:
            print(f"Warning: Content length unknown")
        else:
            print(f"File size: {total_size / (1024*1024):.2f} MB")
        
        # Create directory if needed
        os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
        
        # Setup progress bar
        progress = tqdm(total=total_size, unit='B', unit_scale=True, desc=destination)
        
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:  # filter out keep-alive chunks
                    f.write(chunk)
                    progress.update(len(chunk))
        progress.close()

    # Start session
    session = requests.Session()
    
    # First request to get confirmation token
    print(f"Requesting file {file_id} from Google Drive...")
    response = session.get(URL, params={'id': file_id}, stream=True)
    
    # Check for confirmation token (appears for large files)
    token = get_confirm_token(response)
    if token:
        print(f"Confirmation token received: {token}")
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)
    
    # Download the file
    print(f"Downloading to {destination}...")
    save_response_content(response, destination)
    
    # Verify file exists
    if os.path.exists(destination):
        size_mb = os.path.getsize(destination) / (1024 * 1024)
        print(f"Download complete: {destination} ({size_mb:.2f} MB)")
        return True
    else:
        print(f"Error: File not found after download")
        return False

def download_model(model_info, force=False):
    """
    Download a single model file if it doesn't exist
    
    Args:
        model_info (dict): Dictionary with model name and file_id
        force (bool): Whether to force download even if file exists
        
    Returns:
        bool: Whether download was performed and successful
    """
    file_name = model_info["name"]
    file_id = model_info["file_id"]
    
    # Check if file already exists
    if os.path.exists(file_name) and not force:
        size_mb = os.path.getsize(file_name) / (1024 * 1024)
        print(f"File already exists: {file_name} ({size_mb:.2f} MB)")
        return True
    
    # Download the file
    print(f"Downloading {file_name}...")
    start_time = time.time()
    success = download_file_from_google_drive(file_id, file_name)
    elapsed = time.time() - start_time
    
    if success:
        size_mb = os.path.getsize(file_name) / (1024 * 1024)
        print(f"Download successful in {elapsed:.2f} seconds ({size_mb/elapsed:.2f} MB/s)")
    else:
        print(f"Download failed after {elapsed:.2f} seconds")
    
    return success

def download_all_models(force=False):
    """
    Download all model files, skipping existing ones unless forced
    
    Args:
        force (bool): Whether to force download even if files exist
        
    Returns:
        bool: Whether all downloads were successful
    """
    print("CXRaide PyTorch Models Downloader")
    print("================================")
    print(f"IT2 Model ID: {IT2_FILE_ID}")
    print(f"IT3 Model ID: {IT3_FILE_ID}")
    
    all_successful = True
    for model in MODEL_FILES:
        success = download_model(model, force)
        if not success:
            all_successful = False
    
    return all_successful

# Check if this is being run directly
if __name__ == "__main__":
    # Parse command line arguments
    force_download = "--force" in sys.argv
    
    # Download all models
    success = download_all_models(force=force_download)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1) 