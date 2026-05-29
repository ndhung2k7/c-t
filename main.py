#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Video Splitter Pro - Main Entry Point
Optimized for Dual Xeon E5-2680 v4 + GTX 1070
"""

import sys
import os
import multiprocessing
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Fix for high DPI displays
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)

from ui import MainWindow

def main():
    """Main entry point"""
    # Allow multiprocessing to work properly on Windows
    multiprocessing.freeze_support()
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Auto Video Splitter Pro")
    app.setOrganizationName("VideoSplitter")
    
    # Set dark style palette
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
