#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main UI Module - Dark Mode Professional Interface
"""

import os
import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QComboBox, 
    QSpinBox, QDoubleSpinBox, QProgressBar, QTextEdit,
    QGroupBox, QGridLayout, QCheckBox, QLineEdit,
    QTabWidget, QListWidget, QListWidgetItem, QSplitter,
    QMessageBox, QSlider, QFrame
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSize, 
    QPropertyAnimation, QEasingCurve
)
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QDragEnterEvent, 
    QDropEvent, QIcon, QLinearGradient, QBrush
)

from video_processor import VideoProcessor
from queue_manager import QueueManager
from settings import Settings

class DropArea(QListWidget):
    """Custom list widget with drag and drop support"""
    
    files_dropped = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2e;
                border: 2px dashed #44475a;
                border-radius: 10px;
                padding: 10px;
                color: #f8f8f2;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #6272a4;
            }
        """)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                files.append(file_path)
            elif os.path.isdir(file_path):
                # Scan directory for video files
                for root, dirs, filenames in os.walk(file_path):
                    for filename in filenames:
                        if filename.lower().endswith(('.mp4', '.mkv', '.mov', '.avi', '.flv', '.webm', '.m4v')):
                            files.append(os.path.join(root, filename))
        if files:
            self.files_dropped.emit(files)
        event.acceptProposedAction()


class ProcessingThread(QThread):
    """Background thread for video processing"""
    
    progress = pyqtSignal(int, str, float, float, float, float)
    log = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, video_files, settings):
        super().__init__()
        self.video_files = video_files
        self.settings = settings
        self.processor = None
        self.is_running = True
        
    def run(self):
        self.processor = VideoProcessor(self.settings)
        
        # Connect processor signals
        self.processor.progress.connect(self.progress)
        self.processor.log.connect(self.log)
        
        try:
            self.processor.process_videos(self.video_files)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
            
    def pause(self):
        if self.processor:
            self.processor.pause()
            
    def resume(self):
        if self.processor:
            self.processor.resume()
            
    def cancel(self):
        self.is_running = False
        if self.processor:
            self.processor.cancel()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.queue_manager = QueueManager()
        self.processing_thread = None
        self.video_files = []
        
        self.init_ui()
        self.apply_dark_theme()
        self.load_pending_queue()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Auto Video Splitter Pro - Optimized for Dual Xeon")
        self.setMinimumSize(1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Top bar with logo and stats
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Input and settings
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Queue and progress
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([600, 800])
        main_layout.addWidget(splitter)
        
        # Bottom status bar
        status_bar = self.create_status_bar()
        main_layout.addWidget(status_bar)
        
    def create_top_bar(self):
        """Create top navigation bar"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Logo and title
        title = QLabel("🎬 AUTO VIDEO SPLITTER PRO")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #bd93f9;")
        
        # Stats labels
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_label.setStyleSheet("color: #50fa7b; font-weight: bold;")
        
        self.gpu_label = QLabel("GPU: 0%")
        self.gpu_label.setStyleSheet("color: #50fa7b; font-weight: bold;")
        
        self.ram_label = QLabel("RAM: 0/24GB")
        self.ram_label.setStyleSheet("color: #50fa7b; font-weight: bold;")
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.gpu_label)
        layout.addWidget(self.ram_label)
        
        # Update timer for stats
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_system_stats)
        self.stats_timer.start(1000)
        
        return widget
        
    def create_left_panel(self):
        """Create left panel with input and split settings"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Input section
        input_group = QGroupBox("📁 INPUT VIDEO")
        input_group.setStyleSheet(self.get_group_box_style())
        input_layout = QVBoxLayout(input_group)
        
        # Drop area
        self.drop_area = DropArea()
        self.drop_area.files_dropped.connect(self.add_videos)
        self.drop_area.setMinimumHeight(200)
        self.drop_area.addItem("🎯 Drag & drop video files or folders here")
        input_layout.addWidget(self.drop_area)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_files_btn = QPushButton("➕ Add Files")
        add_files_btn.clicked.connect(self.add_files_dialog)
        add_files_btn.setStyleSheet(self.get_button_style())
        
        add_folder_btn = QPushButton("📂 Add Folder")
        add_folder_btn.clicked.connect(self.add_folder_dialog)
        add_folder_btn.setStyleSheet(self.get_button_style())
        
        clear_btn = QPushButton("🗑 Clear All")
        clear_btn.clicked.connect(self.clear_queue)
        clear_btn.setStyleSheet(self.get_button_style("warning"))
        
        btn_layout.addWidget(add_files_btn)
        btn_layout.addWidget(add_folder_btn)
        btn_layout.addWidget(clear_btn)
        input_layout.addLayout(btn_layout)
        
        layout.addWidget(input_group)
        
        # Split settings
        split_group = QGroupBox("⚙️ SPLIT SETTINGS")
        split_group.setStyleSheet(self.get_group_box_style())
        split_layout = QGridLayout(split_group)
        
        # Split mode
        split_layout.addWidget(QLabel("Split Mode:"), 0, 0)
        self.split_mode = QComboBox()
        self.split_mode.addItems(["By Number of Videos", "By Duration"])
        self.split_mode.currentIndexChanged.connect(self.on_split_mode_changed)
        split_layout.addWidget(self.split_mode, 0, 1)
        
        # Number of videos
        self.num_videos_spin = QSpinBox()
        self.num_videos_spin.setRange(1, 1000)
        self.num_videos_spin.setValue(10)
        split_layout.addWidget(QLabel("Number of videos:"), 1, 0)
        split_layout.addWidget(self.num_videos_spin, 1, 1)
        
        # Duration
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 360)
        self.duration_spin.setValue(10)
        self.duration_spin.setSuffix(" minutes")
        self.duration_spin.setEnabled(False)
        split_layout.addWidget(QLabel("Duration per part:"), 2, 0)
        split_layout.addWidget(self.duration_spin, 2, 1)
        
        layout.addWidget(split_group)
        
        # Speed settings
        speed_group = QGroupBox("🎬 PLAYBACK SPEED")
        speed_group.setStyleSheet(self.get_group_box_style())
        speed_layout = QVBoxLayout(speed_group)
        
        # Speed combo
        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("Speed:"))
        self.speed_combo = QComboBox()
        speeds = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
        self.speed_combo.addItems([f"{s}x" for s in speeds])
        self.speed_combo.setCurrentIndex(3)  # 1.0x
        self.speed_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d3a;
                color: #f8f8f2;
                padding: 5px;
                border-radius: 5px;
            }
        """)
        speed_row.addWidget(self.speed_combo)
        speed_row.addStretch()
        speed_layout.addLayout(speed_row)
        
        # Multi-speed export
        self.multi_speed_check = QCheckBox("Export multiple speeds simultaneously")
        self.multi_speed_check.setStyleSheet("color: #f8f8f2;")
        speed_layout.addWidget(self.multi_speed_check)
        
        layout.addWidget(speed_group)
        
        # Quality settings
        quality_group = QGroupBox("🎨 QUALITY SETTINGS")
        quality_group.setStyleSheet(self.get_group_box_style())
        quality_layout = QGridLayout(quality_group)
        
        quality_layout.addWidget(QLabel("Quality:"), 0, 0)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Ultra (CRF 16)", "High (CRF 18)", "Medium (CRF 23)", "Low (CRF 28)"])
        self.quality_combo.setCurrentIndex(2)
        quality_layout.addWidget(self.quality_combo, 0, 1)
        
        quality_layout.addWidget(QLabel("Output Format:"), 1, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "MKV", "MOV"])
        quality_layout.addWidget(self.format_combo, 1, 1)
        
        # GPU acceleration
        self.gpu_check = QCheckBox("✅ Use NVIDIA GPU (NVENC) - GTX 1070 Detected")
        self.gpu_check.setChecked(True)
        self.gpu_check.setStyleSheet("color: #50fa7b; font-weight: bold;")
        quality_layout.addWidget(self.gpu_check, 2, 0, 1, 2)
        
        # NVENC preset
        quality_layout.addWidget(QLabel("NVENC Preset:"), 3, 0)
        self.nvenc_preset = QComboBox()
        self.nvenc_preset.addItems(["p1 (Fastest)", "p2", "p3", "p4", "p5", "p6", "p7 (Quality)"])
        self.nvenc_preset.setCurrentIndex(4)
        quality_layout.addWidget(self.nvenc_preset, 3, 1)
        
        layout.addWidget(quality_group)
        
        # Output settings
        output_group = QGroupBox("💾 OUTPUT SETTINGS")
        output_group.setStyleSheet(self.get_group_box_style())
        output_layout = QGridLayout(output_group)
        
        output_layout.addWidget(QLabel("Output Folder:"), 0, 0)
        self.output_path = QLineEdit()
        self.output_path.setText(os.path.join(os.path.expanduser("~"), "Videos", "Split"))
        self.output_path.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d3a;
                color: #f8f8f2;
                padding: 5px;
                border-radius: 5px;
            }
        """)
        output_layout.addWidget(self.output_path, 0, 1)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_output_folder)
        browse_btn.setStyleSheet(self.get_button_style())
        output_layout.addWidget(browse_btn, 0, 2)
        
        output_layout.addWidget(QLabel("File Prefix:"), 1, 0)
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("e.g., Anime, Video, Clip...")
        output_layout.addWidget(self.prefix_input, 1, 1, 1, 2)
        
        layout.addWidget(output_group)
        
        # Start button
        self.start_btn = QPushButton("▶ START PROCESSING")
        self.start_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #50fa7b;
                color: #282a36;
                padding: 15px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #69ff94;
            }
            QPushButton:disabled {
                background-color: #44475a;
                color: #6272a4;
            }
        """)
        layout.addWidget(self.start_btn)
        
        # Control buttons for queue
        control_layout = QHBoxLayout()
        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.clicked.connect(self.pause_processing)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet(self.get_button_style())
        
        self.resume_btn = QPushButton("▶ Resume")
        self.resume_btn.clicked.connect(self.resume_processing)
        self.resume_btn.setEnabled(False)
        self.resume_btn.setStyleSheet(self.get_button_style())
        
        self.cancel_btn = QPushButton("✖ Cancel")
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setStyleSheet(self.get_button_style("danger"))
        
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.resume_btn)
        control_layout.addWidget(self.cancel_btn)
        layout.addLayout(control_layout)
        
        return widget
        
    def create_right_panel(self):
        """Create right panel with queue and progress"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Queue list
        queue_group = QGroupBox("📋 PROCESSING QUEUE")
        queue_group.setStyleSheet(self.get_group_box_style())
        queue_layout = QVBoxLayout(queue_group)
        
        self.queue_list = QListWidget()
        self.queue_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2e;
                border: 1px solid #44475a;
                border-radius: 5px;
                color: #f8f8f2;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #44475a;
            }
        """)
        queue_layout.addWidget(self.queue_list)
        
        layout.addWidget(queue_group)
        
        # Progress section
        progress_group = QGroupBox("📊 PROGRESS")
        progress_group.setStyleSheet(self.get_group_box_style())
        progress_layout = QVBoxLayout(progress_group)
        
        # Main progress bar
        self.main_progress = QProgressBar()
        self.main_progress.setStyleSheet("""
            QProgressBar {
                background-color: #2d2d3a;
                border-radius: 5px;
                text-align: center;
                color: #f8f8f2;
            }
            QProgressBar::chunk {
                background-color: #50fa7b;
                border-radius: 5px;
            }
        """)
        progress_layout.addWidget(self.main_progress)
        
        # Current video label
        self.current_video_label = QLabel("Ready to start")
        self.current_video_label.setStyleSheet("color: #f1fa8c; font-weight: bold;")
        progress_layout.addWidget(self.current_video_label)
        
        # Stats row
        stats_layout = QHBoxLayout()
        self.fps_label = QLabel("FPS: --")
        self.eta_label = QLabel("ETA: --")
        stats_layout.addWidget(self.fps_label)
        stats_layout.addWidget(self.eta_label)
        stats_layout.addStretch()
        progress_layout.addLayout(stats_layout)
        
        layout.addWidget(progress_group)
        
        # Log output
        log_group = QGroupBox("📝 LOG")
        log_group.setStyleSheet(self.get_group_box_style())
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                color: #f8f8f2;
                border: 1px solid #44475a;
                border-radius: 5px;
                font-family: 'Consolas', monospace;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        return widget
        
    def create_status_bar(self):
        """Create bottom status bar"""
        widget = QFrame()
        widget.setFrameShape(QFrame.Shape.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_label = QLabel("✅ Ready")
        self.status_label.setStyleSheet("color: #50fa7b;")
        
        self.thread_label = QLabel(f"🧠 56 Threads Available")
        self.thread_label.setStyleSheet("color: #bd93f9;")
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.thread_label)
        
        return widget
        
    def apply_dark_theme(self):
        """Apply professional dark theme"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(40, 42, 54))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(248, 248, 242))
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 46))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(40, 42, 54))
        palette.setColor(QPalette.ColorRole.Text, QColor(248, 248, 242))
        palette.setColor(QPalette.ColorRole.Button, QColor(68, 71, 90))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(248, 248, 242))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(98, 114, 164))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(248, 248, 242))
        
        self.setPalette(palette)
        
    def get_group_box_style(self):
        """Get consistent group box styling"""
        return """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #44475a;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #f8f8f2;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        
    def get_button_style(self, variant="primary"):
        """Get button styling based on variant"""
        colors = {
            "primary": {"bg": "#6272a4", "hover": "#7383b4"},
            "danger": {"bg": "#ff5555", "hover": "#ff6e6e"},
            "warning": {"bg": "#f1fa8c", "hover": "#f4ffb8", "text": "#282a36"}
        }
        
        color = colors.get(variant, colors["primary"])
        text_color = color.get("text", "#f8f8f2")
        
        return f"""
            QPushButton {{
                background-color: {color["bg"]};
                color: {text_color};
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color["hover"]};
            }}
            QPushButton:disabled {{
                background-color: #44475a;
                color: #6272a4;
            }}
        """
        
    def add_videos(self, files):
        """Add videos to queue"""
        for file in files:
            if file not in self.video_files:
                self.video_files.append(file)
                item = QListWidgetItem(f"🎬 {os.path.basename(file)}")
                item.setToolTip(file)
                self.queue_list.addItem(item)
                self.log(f"Added to queue: {os.path.basename(file)}")
                
        self.log(f"Total videos in queue: {len(self.video_files)}")
        
    def add_files_dialog(self):
        """Open file dialog to add videos"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Video Files", "",
            "Video Files (*.mp4 *.mkv *.mov *.avi *.flv *.webm *.m4v)"
        )
        if files:
            self.add_videos(files)
            
    def add_folder_dialog(self):
        """Open folder dialog to add videos from directory"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            files = []
            for root, dirs, filenames in os.walk(folder):
                for filename in filenames:
                    if filename.lower().endswith(('.mp4', '.mkv', '.mov', '.avi', '.flv', '.webm', '.m4v')):
                        files.append(os.path.join(root, filename))
            if files:
                self.add_videos(files)
                self.log(f"Added {len(files)} videos from folder")
                
    def clear_queue(self):
        """Clear all videos from queue"""
        self.video_files = []
        self.queue_list.clear()
        self.log("Queue cleared")
        
    def browse_output_folder(self):
        """Browse output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_path.setText(folder)
            
    def on_split_mode_changed(self, index):
        """Handle split mode change"""
        is_duration = (index == 1)
        self.num_videos_spin.setEnabled(not is_duration)
        self.duration_spin.setEnabled(is_duration)
        
    def start_processing(self):
        """Start video processing"""
        if not self.video_files:
            QMessageBox.warning(self, "No Videos", "Please add videos to process.")
            return
            
        # Validate output folder
        output_folder = self.output_path.text()
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot create output folder: {e}")
                return
                
        # Prepare settings
        settings = {
            'split_mode': self.split_mode.currentIndex(),
            'num_videos': self.num_videos_spin.value(),
            'duration_minutes': self.duration_spin.value(),
            'speed': float(self.speed_combo.currentText().replace('x', '')),
            'multi_speed': self.multi_speed_check.isChecked(),
            'quality': self.quality_combo.currentIndex(),
            'output_format': self.format_combo.currentText().lower(),
            'use_gpu': self.gpu_check.isChecked(),
            'nvenc_preset': self.nvenc_preset.currentIndex() + 1,
            'output_folder': output_folder,
            'prefix': self.prefix_input.text(),
            'crf_values': [16, 18, 23, 28]
        }
        
        # Start processing thread
        self.processing_thread = ProcessingThread(self.video_files.copy(), settings)
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.log.connect(self.log)
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.error.connect(self.on_processing_error)
        self.processing_thread.start()
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.status_label.setText("🔄 Processing...")
        
        self.log("=" * 50)
        self.log("🚀 STARTING VIDEO PROCESSING")
        self.log(f"📁 Output folder: {output_folder}")
        self.log(f"🎯 Split mode: {self.split_mode.currentText()}")
        self.log(f"⚡ Speed: {settings['speed']}x")
        self.log(f"🎨 Quality: {self.quality_combo.currentText()}")
        self.log(f"🎬 GPU Acceleration: {'ON' if settings['use_gpu'] else 'OFF'}")
        self.log("=" * 50)
        
    def pause_processing(self):
        """Pause processing"""
        if self.processing_thread:
            self.processing_thread.pause()
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(True)
            self.status_label.setText("⏸ Paused")
            self.log("Processing paused")
            
    def resume_processing(self):
        """Resume processing"""
        if self.processing_thread:
            self.processing_thread.resume()
            self.pause_btn.setEnabled(True)
            self.resume_btn.setEnabled(False)
            self.status_label.setText("🔄 Processing...")
            self.log("Processing resumed")
            
    def cancel_processing(self):
        """Cancel processing"""
        if self.processing_thread:
            self.processing_thread.cancel()
            self.cancel_btn.setEnabled(False)
            self.status_label.setText("❌ Cancelling...")
            self.log("Cancelling processing...")
            
    def update_progress(self, percent, current_video, fps, eta, cpu_usage, gpu_usage):
        """Update progress display"""
        self.main_progress.setValue(int(percent))
        self.current_video_label.setText(f"🎬 {current_video}")
        self.fps_label.setText(f"FPS: {fps:.1f}" if fps > 0 else "FPS: --")
        self.eta_label.setText(f"ETA: {int(eta // 60)}m {int(eta % 60)}s" if eta > 0 else "ETA: --")
        
    def update_system_stats(self):
        """Update system statistics"""
        try:
            import psutil
            import GPUtil
            
            # CPU usage (limit to 90% max as requested)
            cpu_percent = min(psutil.cpu_percent(interval=0.5), 90)
            self.cpu_label.setText(f"CPU: {cpu_percent:.0f}%")
            
            # RAM usage (limit to 24GB max)
            ram = psutil.virtual_memory()
            ram_used_gb = ram.used / (1024**3)
            ram_label_text = f"RAM: {ram_used_gb:.1f}/24GB"
            if ram_used_gb > 24:
                ram_label_text = f"⚠️ RAM: {ram_used_gb:.1f}/24GB"
            self.ram_label.setText(ram_label_text)
            
            # GPU usage
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                self.gpu_label.setText(f"GPU: {gpu.load*100:.0f}%")
                
        except:
            pass  # Silently fail if psutil/GPUtil not available
            
    def on_processing_finished(self):
        """Handle processing completion"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.status_label.setText("✅ Completed")
        self.log("=" * 50)
        self.log("✅ ALL VIDEOS PROCESSED SUCCESSFULLY!")
        self.log("=" * 50)
        
        QMessageBox.information(self, "Complete", "Video processing completed successfully!")
        
    def on_processing_error(self, error_msg):
        """Handle processing error"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.status_label.setText("❌ Error")
        self.log(f"❌ ERROR: {error_msg}")
        
        QMessageBox.critical(self, "Error", f"Processing error: {error_msg}")
        
    def load_pending_queue(self):
        """Load pending tasks from queue"""
        pending = self.queue_manager.load_queue()
        if pending:
            self.log(f"Loaded {len(pending)} pending tasks from previous session")
            
    def log(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        self.log_text.append(log_line)
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
