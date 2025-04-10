@echo off
echo CXRaide Local Model Server Startup
echo ===============================

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python 3.9 or later.
    goto :exit
)

REM Check for virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create virtual environment.
        goto :exit
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate virtual environment.
    goto :exit
)

REM Install requirements if needed
if not exist venv\Lib\site-packages\torch (
    echo Installing dependencies (this may take a few minutes)...
    pip install flask flask-cors pillow numpy
    pip install torch==2.0.1+cpu torchvision==0.15.2+cpu --extra-index-url https://download.pytorch.org/whl/cpu
    pip install opencv-python requests tqdm
)

REM Download models if needed
if not exist IT2_model_epoch_300.pth (
    echo IT2 model file not found. Attempting to download...
    if exist download_models_local.py (
        python download_models_local.py
        if %ERRORLEVEL% NEQ 0 (
            echo WARNING: Failed to download models automatically.
            echo Please download the model files manually and place them in this directory.
        )
    ) else (
        echo WARNING: download_models_local.py not found. 
        echo Please download the model files manually and place them in this directory.
    )
)

REM Set API key (you should change this in production)
set MODEL_API_KEY=default-secure-key-change-me

REM Check if models exist before starting
if not exist IT2_model_epoch_300.pth (
    echo ERROR: IT2 model file not found. Server will start but predictions may fail.
)

if not exist IT3_model_epoch_260.pth (
    echo ERROR: IT3 model file not found. Server will start but predictions may fail.
)

REM Start the server
echo Starting local model server on port 5500...
python local_model_server.py

:exit
echo.
echo Press any key to exit...
pause > nul 