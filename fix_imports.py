#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script sửa lỗi import - Chạy nếu gặp lỗi module
"""

import sys
import subprocess
import os

def fix_imports():
    """Sửa lỗi import bằng cách cài đặt lại dependencies"""
    
    print("=" * 60)
    print("SỬA LỖI IMPORT - AUTO VIDEO SPLITTER PRO")
    print("=" * 60)
    print()
    
    packages = [
        "PyQt6",
        "PyQt6-Qt6", 
        "psutil",
        "GPUtil",
        "numpy",
        "colorama"
    ]
    
    for package in packages:
        print(f"Đang cài đặt: {package}")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package, "--upgrade"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✓ {package} cài đặt thành công")
        else:
            print(f"  ✗ {package} cài đặt thất bại")
            print(f"    Lỗi: {result.stderr[:200]}")
        print()
    
    print("=" * 60)
    print("HOÀN TẤT! Hãy chạy lại run.bat")
    print("=" * 60)
    
    input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    fix_imports()
