@echo off
echo ========================================
echo Auto Video Splitter Pro - Build Script
echo Optimized for Dual Xeon + GTX 1070
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Install requirements
echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [WARNING] Some dependencies may already be installed...
)

REM Install PyInstaller if not available
echo [2/4] Installing PyInstaller...
pip install pyinstaller

REM Build executable
echo [3/4] Building executable...
pyinstaller --onefile ^
    --windowed ^
    --name "AutoVideoSplitterPro" ^
    --icon=app.ico ^
    --add-data "requirements.txt;." ^
    --hidden-import PyQt6 ^
    --hidden-import psutil ^
    --hidden-import GPUtil ^
    --hidden-import numpy ^
    --collect-all PyQt6 ^
    main.py

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

REM Copy FFmpeg if available
echo [4/4] Preparing distribution...
if exist "ffmpeg.exe" (
    copy "ffmpeg.exe" "dist\"
    echo Copied FFmpeg to distribution folder.
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo.
echo Executable location: dist\AutoVideoSplitterPro.exe
echo.
echo Note: First run may take a moment to download FFmpeg
echo       if not already present.
echo.
pause
