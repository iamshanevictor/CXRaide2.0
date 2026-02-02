#!/usr/bin/env python
"""
CXRaide Local Environment Setup Script
======================================

This script helps set up your local development environment for CXRaide.
It gives you options to:
1. Set up with real models (requires model files and PyTorch)
2. Set up with mock models (no large dependencies)

"""
import os
import sys
import subprocess
import platform
import argparse

def print_header(text):
    """Print a nice header for information"""
    width = 80
    print("\n" + "=" * width)
    print(f"{text.center(width)}")
    print("=" * width + "\n")

def print_step(text):
    """Print a step in the process"""
    print(f"▶ {text}")

def check_model_files():
    """Check if model files exist"""
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    it2_path = os.path.join(model_dir, 'IT2_model_epoch_300.pth')
    it3_path = os.path.join(model_dir, 'IT3_model_epoch_260.pth')
    
    it2_exists = os.path.exists(it2_path)
    it3_exists = os.path.exists(it3_path)
    
    return it2_exists, it3_exists

def setup_mock_environment():
    """Set up environment for mock models"""
    print_header("Setting up Mock Model Environment")
    
    print_step("Installing base requirements (no PyTorch)...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    print_step("Setting environment variable for mock models...")
    
    # Create or update .env file with USE_MOCK_MODELS=True
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    # Read existing .env content
    env_content = ""
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()
    
    # Check if USE_MOCK_MODELS is already set
    if "USE_MOCK_MODELS=" in env_content:
        # Replace existing value
        lines = env_content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("USE_MOCK_MODELS="):
                lines[i] = "USE_MOCK_MODELS=True"
        env_content = "\n".join(lines)
    else:
        # Add variable
        env_content += "\nUSE_MOCK_MODELS=True\n"
    
    # Write updated content
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print_step("Environment set up for mock models!")
    print("\nTo run the server with mock models:")
    if platform.system() == 'Windows':
        print("  python app.py")
    else:
        print("  python app.py")
    print("\nMock models provide realistic predictions without requiring large files or PyTorch.")

def setup_real_environment():
    """Set up environment for real models"""
    print_header("Setting up Real Model Environment")
    
    it2_exists, it3_exists = check_model_files()
    
    if it2_exists and it3_exists:
        model_dir = os.path.join(os.path.dirname(__file__), 'models')
        print_step("Model files found!")
        print(f"  ✅ IT2_model_epoch_300.pth: {os.path.getsize(os.path.join(model_dir, 'IT2_model_epoch_300.pth')) / (1024*1024):.1f} MB")
        print(f"  ✅ IT3_model_epoch_260.pth: {os.path.getsize(os.path.join(model_dir, 'IT3_model_epoch_260.pth')) / (1024*1024):.1f} MB")
    else:
        print_step("Model files not found in server/models. Please place IT2_model_epoch_300.pth and IT3_model_epoch_260.pth there. The application will fall back to mock models until then.")
    
    print_step("Installing requirements with PyTorch...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.local.txt'])
    
    print_step("Setting environment variable for real models...")
    # Create or update .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    # Read existing .env content
    env_content = ""
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()
    
    # Check if USE_MOCK_MODELS is already set
    if "USE_MOCK_MODELS=" in env_content:
        # Replace existing value
        lines = env_content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("USE_MOCK_MODELS="):
                lines[i] = "USE_MOCK_MODELS=False"
        env_content = "\n".join(lines)
    else:
        # Add variable
        env_content += "\nUSE_MOCK_MODELS=False\n"
    
    # Write updated content
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print_step("Environment set up for real models!")
    print("\nTo run the server with real models:")
    if platform.system() == 'Windows':
        print("  python app.py")
    else:
        print("  python app.py")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="CXRaide Local Environment Setup")
    parser.add_argument('--mode', type=str, choices=['real', 'mock'], 
                        help='Setup mode: "real" for real models or "mock" for mock models')
    
    args = parser.parse_args()
    
    print_header("CXRaide Local Environment Setup")
    
    if args.mode:
        # Use command line argument
        mode = args.mode
    else:
        # Ask user for mode
        print("Choose a setup mode:")
        print("1. Real Model Environment (requires model files and PyTorch)")
        print("2. Mock Model Environment (lightweight, no large dependencies)")
        
        choice = input("\nEnter your choice (1/2): ").strip()
        
        if choice == '1':
            mode = 'real'
        elif choice == '2':
            mode = 'mock'
        else:
            print("Invalid choice. Please run the script again.")
            sys.exit(1)
    
    if mode == 'real':
        setup_real_environment()
    else:
        setup_mock_environment()
    
    print_header("Setup Complete!")
    print("You can now run the CXRaide backend locally.")
    print("To start the server: python app.py")

if __name__ == "__main__":
    main() 