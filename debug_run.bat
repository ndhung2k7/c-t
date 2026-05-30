@echo off
chcp 65001 > nul
title Auto Video Splitter Pro - DEBUG MODE

echo ========================================
echo AUTO VIDEO SPLITTER PRO - DEBUG MODE
echo ========================================
echo.
echo Nếu gặp lỗi, vui lòng chụp ảnh màn hình này
echo và gửi cho bộ phận hỗ trợ.
echo.
echo ========================================
echo.

REM Hiển thị thông tin hệ thống
echo [SYSTEM INFO]
echo Python path: 
where python
echo.
python --version
echo.
echo Current directory: %CD%
echo.
echo PATH: %PATH%
echo.
echo ========================================

REM Chạy với chế độ debug
echo [RUNNING IN DEBUG MODE]
echo.

set PYTHONVERBOSE=1
python main.py 2>&1

echo.
echo ========================================
echo DEBUG COMPLETE
echo ========================================
echo.
echo Nếu thấy lỗi, vui lòng kiểm tra:
echo 1. Đã cài đặt Python 3.8+
echo 2. Đã chạy install_deps.bat
echo 3. Kết nối Internet (cho lần đầu)
echo.

pause
