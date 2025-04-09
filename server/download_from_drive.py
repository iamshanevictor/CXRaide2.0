#!/usr/bin/env python3
"""
Direct Google Drive File Downloader for CXRaide

A simplified script to download the model file from Google Drive.
This can be used locally to test the download before deploying to Render.
"""

import os
import sys
import time
import requests
from tqdm import tqdm

# Google Drive file info - same as in download_model.py
FILE_ID = "1cbvOqEkmhXw-4t1_Reoc29JbVPRF4MNr"
DESTINATION = "IT2_model_epoch_300.pth"

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

if __name__ == "__main__":
    print("CXRaide PyTorch Model Downloader")
    print("================================")
    
    # Allow overriding destination from command line
    if len(sys.argv) > 1:
        DESTINATION = sys.argv[1]
        print(f"Custom destination: {DESTINATION}")
    
    # Check if file already exists
    if os.path.exists(DESTINATION):
        size_mb = os.path.getsize(DESTINATION) / (1024 * 1024)
        print(f"File already exists: {DESTINATION} ({size_mb:.2f} MB)")
        response = input("Download again? (y/n): ")
        if response.lower() != 'y':
            print("Exiting without download")
            sys.exit(0)
    
    # Time the download
    start_time = time.time()
    
    # Download the file
    success = download_file_from_google_drive(FILE_ID, DESTINATION)
    
    # Print summary
    elapsed = time.time() - start_time
    if success:
        size_mb = os.path.getsize(DESTINATION) / (1024 * 1024)
        print(f"Download successful in {elapsed:.2f} seconds ({size_mb/elapsed:.2f} MB/s)")
    else:
        print(f"Download failed after {elapsed:.2f} seconds")
        sys.exit(1) 