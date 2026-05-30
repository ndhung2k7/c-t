@echo off
chcp 65001 > nul
title Auto Video Splitter Pro

echo ========================================
echo Auto Video Splitter Pro
echo Optimized for Dual Xeon + GTX 1070
echo ========================================
echo.

REM Kiểm tra Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [LOI] Khong tim thay Python!
    echo Vui long cai dat Python 3.8 hoac cao hon
    echo Tai: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Hiển thị phiên bản Python
echo Python version:
python --version
echo.

REM Kiểm tra và cài đặt dependencies
echo [1/3] Kiem tra dependencies...
pip list | findstr PyQt6 > nul
if errorlevel 1 (
    echo Dang cai dat dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [LOI] Khong the cai dat dependencies!
        pause
        exit /b 1
    )
)

REM Tạo thư mục cần thiết
echo [2/3] Tao thu muc can thiet...
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
if not exist "%USERPROFILE%\Videos\Split" mkdir "%USERPROFILE%\Videos\Split"

REM Chạy ứng dụng
echo [3/3] Khoi dong Auto Video Splitter Pro...
echo.
echo ========================================
echo UD DANG CHAY...
echo ========================================
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [LOI] Ung dung bi loi!
    echo Vui long xem thong bao ben tren de biet chi tiet.
    pause
)

pause
