"""
Download model files from Google Drive for local use
"""
import os
import sys
import time
import requests
import tqdm

# Google Drive file IDs for the models
IT2_MODEL_ID = "1cbvOqEkmhXw-4t1_Reoc29JbVPRF4MNr"
IT3_MODEL_ID = "1rd0j7hmw19H02z4vDfWw3Il-s4Xx-zTz"

def download_file_from_google_drive(file_id, destination):
    """
    Download a file from Google Drive without using the Google Drive API
    """
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768
        
        # Get total file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Initialize progress bar
        progress_bar = tqdm.tqdm(
            total=total_size, 
            unit='iB', 
            unit_scale=True,
            desc=f"Downloading {os.path.basename(destination)}"
        )
        
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    progress_bar.update(len(chunk))
        progress_bar.close()

    print(f"Downloading file to {destination}...")
    
    # Initial request
    url = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(url, params={'id': file_id}, stream=True)
    
    # Get confirmation token
    token = get_confirm_token(response)
    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(url, params=params, stream=True)

    save_response_content(response, destination)
    
    # Verify download
    if os.path.exists(destination):
        file_size = os.path.getsize(destination)
        print(f"Downloaded {os.path.basename(destination)} ({file_size / (1024*1024):.1f} MB)")
        return True
    else:
        print(f"Failed to download {os.path.basename(destination)}")
        return False

def main():
    # Determine output directory (current directory)
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("CXRaide Model Downloader")
    print("=======================")
    print(f"Output directory: {output_dir}")
    
    # Download IT2 model
    it2_path = os.path.join(output_dir, "IT2_model_epoch_300.pth")
    if os.path.exists(it2_path):
        print(f"IT2 model already exists at {it2_path}")
    else:
        print("Downloading IT2 model...")
        download_file_from_google_drive(IT2_MODEL_ID, it2_path)
    
    # Download IT3 model
    it3_path = os.path.join(output_dir, "IT3_model_epoch_260.pth")
    if os.path.exists(it3_path):
        print(f"IT3 model already exists at {it3_path}")
    else:
        print("Downloading IT3 model...")
        download_file_from_google_drive(IT3_MODEL_ID, it3_path)
    
    # Verify downloads
    if os.path.exists(it2_path) and os.path.exists(it3_path):
        print("\nBoth models downloaded successfully!")
        print(f"IT2 model: {it2_path} ({os.path.getsize(it2_path) / (1024*1024):.1f} MB)")
        print(f"IT3 model: {it3_path} ({os.path.getsize(it3_path) / (1024*1024):.1f} MB)")
        return 0
    else:
        missing = []
        if not os.path.exists(it2_path):
            missing.append("IT2 model")
        if not os.path.exists(it3_path):
            missing.append("IT3 model")
        print(f"\nError: Failed to download {', '.join(missing)}")
        return 1

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(result)
    except KeyboardInterrupt:
        print("\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1) 