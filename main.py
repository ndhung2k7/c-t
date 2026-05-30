#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Video Splitter Pro - Main Entry Point
Optimized for Dual Xeon E5-2680 v4 + GTX 1070
"""

import sys
import os
import multiprocessing
import traceback

# Fix cho Windows - xử lý lỗi encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Thêm đường dẫn hiện tại vào sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_exception_handler():
    """Thiết lập xử lý exception toàn cục"""
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        print("=" * 60)
        print("LỖI NGHIÊM TRỌNG:")
        print(f"Loại: {exc_type.__name__}")
        print(f"Nội dung: {exc_value}")
        print("Chi tiết:")
        traceback.print_tb(exc_traceback)
        print("=" * 60)
        input("Nhấn Enter để thoát...")
        sys.exit(1)
    
    sys.excepthook = global_exception_handler

def main():
    """Main entry point"""
    # Thiết lập xử lý lỗi
    setup_exception_handler()
    
    # Cho phép multiprocessing trên Windows
    multiprocessing.freeze_support()
    
    # Kiểm tra Python version
    if sys.version_info < (3, 8):
        print("LỖI: Cần Python 3.8 hoặc cao hơn!")
        print(f"Phiên bản hiện tại: {sys.version}")
        input("Nhấn Enter để thoát...")
        sys.exit(1)
    
    try:
        # Import PyQt6 sau khi đã setup
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Import UI module
        from ui import MainWindow
        
        # Tạo application
        app = QApplication(sys.argv)
        app.setApplicationName("Auto Video Splitter Pro")
        app.setOrganizationName("VideoSplitter")
        
        # Set dark style palette
        app.setStyle("Fusion")
        
        # Tạo và hiển thị main window
        window = MainWindow()
        window.show()
        
        # Chạy event loop
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"LỖI IMPORT: {e}")
        print("\nVui lòng cài đặt dependencies bằng lệnh:")
        print("pip install -r requirements.txt")
        print("\nHoặc chạy file install_deps.bat")
        input("\nNhấn Enter để thoát...")
        sys.exit(1)
        
    except Exception as e:
        print(f"LỖI KHÔNG XÁC ĐỊNH: {e}")
        traceback.print_exc()
        input("\nNhấn Enter để thoát...")
        sys.exit(1)

if __name__ == "__main__":
    main()
