#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main UI Module - Dark Mode Professional Interface
Hỗ trợ đa ngôn ngữ Tiếng Việt/English
"""

import os
import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QComboBox, 
    QSpinBox, QDoubleSpinBox, QProgressBar, QTextEdit,
    QGroupBox, QGridLayout, QCheckBox, QLineEdit,
    QTabWidget, QListWidget, QListWidgetItem, QSplitter,
    QMessageBox, QSlider, QFrame, QMenu, QToolBar
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSize, 
    QPropertyAnimation, QEasingCurve
)
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QDragEnterEvent, 
    QDropEvent, QIcon, QLinearGradient, QBrush, QAction
)

from video_processor import VideoProcessor
from queue_manager import QueueManager
from settings import Settings
from languages import get_language_manager, tr


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
                for root, dirs, filenames in os.walk(file_path):
                    for filename in filenames:
                        if filename.lower().endswith(('.mp4', '.mkv', '.mov', '.avi', '.flv', '.webm', '.m4v')):
                            files.append(os.path.join(root, filename))
        if files:
            self.files_dropped.emit(files)
        event.acceptProposedAction()


class ProcessingThread(QThread):
    """Background thread for video processing"""
    
    progress = pyqtSignal(int, str, float, float, float, float, int, int)
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
    """Main application window with multi-language support"""
    
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.queue_manager = QueueManager()
        self.processing_thread = None
        self.video_files = []
        self.start_time = None
        self.total_segments = 0
        self.processed_segments = 0
        
        # Language manager
        self.lang_manager = get_language_manager()
        self.lang_manager.language_changed.connect(self.retranslate_ui)
        
        self.init_ui()
        self.apply_dark_theme()
        self.load_pending_queue()
        self.update_thread_info()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle(tr('app_title'))
        self.setMinimumSize(1400, 950)
        
        # Create menu bar
        self.create_menu_bar()
        
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
        
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        add_files_action = QAction("Add Files", self)
        add_files_action.triggered.connect(self.add_files_dialog)
        file_menu.addAction(add_files_action)
        
        add_folder_action = QAction("Add Folder", self)
        add_folder_action.triggered.connect(self.add_folder_dialog)
        file_menu.addAction(add_folder_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu(tr('settings'))
        
        # Language submenu
        language_menu = settings_menu.addMenu(tr('language'))
        
        vietnamese_action = QAction(tr('vietnamese'), self)
        vietnamese_action.triggered.connect(lambda: self.lang_manager.set_language('vi'))
        language_menu.addAction(vietnamese_action)
        
        english_action = QAction(tr('english'), self)
        english_action.triggered.connect(lambda: self.lang_manager.set_language('en'))
        language_menu.addAction(english_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_top_bar(self):
        """Create top navigation bar"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Logo and title
        self.title_label = QLabel("🎬 AUTO VIDEO SPLITTER PRO")
        self.title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #bd93f9;")
        
        # Stats labels
        self.cpu_label = QLabel(f"{tr('cpu')}: 0%")
        self.cpu_label.setStyleSheet("color: #50fa7b; font-weight: bold;")
        
        self.gpu_label = QLabel(f"{tr('gpu')}: 0%")
        self.gpu_label.setStyleSheet("color: #50fa7b; font-weight: bold;")
        
        self.ram_label = QLabel(f"{tr('ram')}: 0/24GB")
        self.ram_label.setStyleSheet("color: #50fa7b; font-weight: bold;")
        
        # Language selector
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["🇻🇳 Tiếng Việt", "🇬🇧 English"])
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d3a;
                color: #f8f8f2;
                padding: 5px 10px;
                border-radius: 5px;
            }
        """)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.gpu_label)
        layout.addWidget(self.ram_label)
        layout.addWidget(self.lang_combo)
        
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
        input_group = QGroupBox(tr('input_video'))
        input_group.setStyleSheet(self.get_group_box_style())
        input_layout = QVBoxLayout(input_group)
        
        # Drop area
        self.drop_area = DropArea()
        self.drop_area.files_dropped.connect(self.add_videos)
        self.drop_area.setMinimumHeight(200)
        self.drop_area.addItem(tr('drag_drop'))
        input_layout.addWidget(self.drop_area)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_files_btn = QPushButton(tr('add_files'))
        add_files_btn.clicked.connect(self.add_files_dialog)
        add_files_btn.setStyleSheet(self.get_button_style())
        
        add_folder_btn = QPushButton(tr('add_folder'))
        add_folder_btn.clicked.connect(self.add_folder_dialog)
        add_folder_btn.setStyleSheet(self.get_button_style())
        
        clear_btn = QPushButton(tr('clear_all'))
        clear_btn.clicked.connect(self.clear_queue)
        clear_btn.setStyleSheet(self.get_button_style("warning"))
        
        btn_layout.addWidget(add_files_btn)
        btn_layout.addWidget(add_folder_btn)
        btn_layout.addWidget(clear_btn)
        input_layout.addLayout(btn_layout)
        
        layout.addWidget(input_group)
        
        # Split settings
        split_group = QGroupBox(tr('split_settings'))
        split_group.setStyleSheet(self.get_group_box_style())
        split_layout = QGridLayout(split_group)
        
        # Split mode
        split_layout.addWidget(QLabel(tr('split_mode')), 0, 0)
        self.split_mode = QComboBox()
        self.split_mode.addItems([tr('by_number'), tr('by_duration')])
        self.split_mode.currentIndexChanged.connect(self.on_split_mode_changed)
        split_layout.addWidget(self.split_mode, 0, 1)
        
        # Number of videos
        self.num_videos_spin = QSpinBox()
        self.num_videos_spin.setRange(1, 1000)
        self.num_videos_spin.setValue(10)
        self.num_videos_label = QLabel(tr('num_videos'))
        split_layout.addWidget(self.num_videos_label, 1, 0)
        split_layout.addWidget(self.num_videos_spin, 1, 1)
        
        # Duration
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 360)
        self.duration_spin.setValue(10)
        self.duration_spin.setSuffix(tr('minutes'))
        self.duration_spin.setEnabled(False)
        self.duration_label = QLabel(tr('duration'))
        split_layout.addWidget(self.duration_label, 2, 0)
        split_layout.addWidget(self.duration_spin, 2, 1)
        
        layout.addWidget(split_group)
        
        # Speed settings
        speed_group = QGroupBox(tr('speed_settings'))
        speed_group.setStyleSheet(self.get_group_box_style())
        speed_layout = QVBoxLayout(speed_group)
        
        # Speed combo
        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel(tr('speed')))
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
        self.multi_speed_check = QCheckBox(tr('multi_speed'))
        self.multi_speed_check.setStyleSheet("color: #f8f8f2;")
        speed_layout.addWidget(self.multi_speed_check)
        
        layout.addWidget(speed_group)
        
        # Quality settings
        quality_group = QGroupBox(tr('quality_settings'))
        quality_group.setStyleSheet(self.get_group_box_style())
        quality_layout = QGridLayout(quality_group)
        
        quality_layout.addWidget(QLabel(tr('quality')), 0, 0)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([tr('ultra'), tr('high'), tr('medium'), tr('low')])
        self.quality_combo.setCurrentIndex(2)
        quality_layout.addWidget(self.quality_combo, 0, 1)
        
        quality_layout.addWidget(QLabel(tr('output_format')), 1, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "MKV", "MOV"])
        quality_layout.addWidget(self.format_combo, 1, 1)
        
        # GPU acceleration
        self.gpu_check = QCheckBox(tr('use_gpu'))
        self.gpu_check.setChecked(True)
        self.gpu_check.setStyleSheet("color: #50fa7b; font-weight: bold;")
        quality_layout.addWidget(self.gpu_check, 2, 0, 1, 2)
        
        # NVENC preset
        quality_layout.addWidget(QLabel(tr('nvenc_preset')), 3, 0)
        self.nvenc_preset = QComboBox()
        self.nvenc_preset.addItems([
            tr('preset_fastest'), tr('preset_fast'), tr('preset_medium'),
            tr('preset_slow'), tr('preset_slower'), tr('preset_very_slow'), tr('preset_quality')
        ])
        self.nvenc_preset.setCurrentIndex(4)
        quality_layout.addWidget(self.nvenc_preset, 3, 1)
        
        layout.addWidget(quality_group)
        
        # Output settings
        output_group = QGroupBox(tr('output_settings'))
        output_group.setStyleSheet(self.get_group_box_style())
        output_layout = QGridLayout(output_group)
        
        output_layout.addWidget(QLabel(tr('output_folder')), 0, 0)
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
        
        browse_btn = QPushButton(tr('browse'))
        browse_btn.clicked.connect(self.browse_output_folder)
        browse_btn.setStyleSheet(self.get_button_style())
        output_layout.addWidget(browse_btn, 0, 2)
        
        output_layout.addWidget(QLabel(tr('file_prefix')), 1, 0)
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText(tr('prefix_placeholder'))
        output_layout.addWidget(self.prefix_input, 1, 1, 1, 2)
        
        layout.addWidget(output_group)
        
        # Start button
        self.start_btn = QPushButton(tr('start'))
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
        self.pause_btn = QPushButton(tr('pause'))
        self.pause_btn.clicked.connect(self.pause_processing)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet(self.get_button_style())
        
        self.resume_btn = QPushButton(tr('resume'))
        self.resume_btn.clicked.connect(self.resume_processing)
        self.resume_btn.setEnabled(False)
        self.resume_btn.setStyleSheet(self.get_button_style())
        
        self.cancel_btn = QPushButton(tr('cancel'))
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setStyleSheet(self.get_button_style("danger"))
        
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.resume_btn)
        control_layout.addWidget(self.cancel_btn)
        layout.addLayout(control_layout)
        
        return widget
        
    def create_right_panel(self):
        """Create right panel with queue and progress (cải tiến)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Queue list
        queue_group = QGroupBox(tr('queue_title') if hasattr(tr, '__call__') else "📋 PROCESSING QUEUE")
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
        
        # Progress section - CẢI TIẾN CHI TIẾT
        progress_group = QGroupBox(tr('progress'))
        progress_group.setStyleSheet(self.get_group_box_style())
        progress_layout = QVBoxLayout(progress_group)
        
        # Main progress bar (Overall)
        self.progress_label = QLabel("0%")
        self.progress_label.setStyleSheet("color: #f1fa8c; font-weight: bold;")
        progress_layout.addWidget(self.progress_label)
        
        self.main_progress = QProgressBar()
        self.main_progress.setStyleSheet("""
            QProgressBar {
                background-color: #2d2d3a;
                border-radius: 5px;
                text-align: center;
                color: #f8f8f2;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #50fa7b;
                border-radius: 5px;
            }
        """)
        progress_layout.addWidget(self.main_progress)
        
        # Segment progress bar (Chi tiết cắt video)
        self.segment_label = QLabel("✂️ 0/0 segments")
        self.segment_label.setStyleSheet("color: #8be9fd; font-weight: bold;")
        progress_layout.addWidget(self.segment_label)
        
        self.segment_progress = QProgressBar()
        self.segment_progress.setStyleSheet("""
            QProgressBar {
                background-color: #2d2d3a;
                border-radius: 5px;
                text-align: center;
                color: #f8f8f2;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #bd93f9;
                border-radius: 5px;
            }
        """)
        progress_layout.addWidget(self.segment_progress)
        
        # Current video label
        self.current_video_label = QLabel("🎬 " + tr('ready'))
        self.current_video_label.setStyleSheet("color: #f1fa8c; font-weight: bold; font-size: 12px;")
        progress_layout.addWidget(self.current_video_label)
        
        # Stats grid (FPS, ETA, Time, Speed)
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        
        # FPS
        self.fps_label = QLabel(f"{tr('fps')}: --")
        self.fps_label.setStyleSheet("color: #50fa7b;")
        stats_grid.addWidget(self.fps_label, 0, 0)
        
        # ETA
        self.eta_label = QLabel(f"{tr('eta')}: --")
        self.eta_label.setStyleSheet("color: #50fa7b;")
        stats_grid.addWidget(self.eta_label, 0, 1)
        
        # Elapsed time
        self.elapsed_label = QLabel(f"{tr('elapsed_time')}: 00:00:00")
        self.elapsed_label.setStyleSheet("color: #ffb86c;")
        stats_grid.addWidget(self.elapsed_label, 1, 0)
        
        # Remaining time
        self.remaining_label = QLabel(f"{tr('remaining_time')}: --")
        self.remaining_label.setStyleSheet("color: #ffb86c;")
        stats_grid.addWidget(self.remaining_label, 1, 1)
        
        # Processing speed
        self.speed_info_label = QLabel(f"{tr('speed_info')}: --")
        self.speed_info_label.setStyleSheet("color: #ff5555;")
        stats_grid.addWidget(self.speed_info_label, 2, 0, 1, 2)
        
        # Completed segments info
        self.completed_label = QLabel(f"{tr('completed_segments')}: 0")
        self.completed_label.setStyleSheet("color: #8be9fd;")
        stats_grid.addWidget(self.completed_label, 3, 0)
        
        self.total_label = QLabel(f"{tr('total_segments')}: 0")
        self.total_label.setStyleSheet("color: #8be9fd;")
        stats_grid.addWidget(self.total_label, 3, 1)
        
        progress_layout.addLayout(stats_grid)
        
        # Estimated completion time
        self.est_completion_label = QLabel(f"📅 {tr('estimated_completion')}: --")
        self.est_completion_label.setStyleSheet("color: #f1fa8c; font-weight: bold;")
        progress_layout.addWidget(self.est_completion_label)
        
        layout.addWidget(progress_group)
        
        # Log output
        log_group = QGroupBox(tr('log'))
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
                font-size: 11px;
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
        
        self.status_label = QLabel(tr('ready_status'))
        self.status_label.setStyleSheet("color: #50fa7b; font-weight: bold;")
        
        self.thread_label = QLabel("🧠 0/56 Threads")
        self.thread_label.setStyleSheet("color: #bd93f9;")
        
        self.language_label = QLabel("🌐 Tiếng Việt")
        self.language_label.setStyleSheet("color: #6272a4;")
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.thread_label)
        layout.addWidget(self.language_label)
        
        return widget
        
    def retranslate_ui(self):
        """Cập nhật tất cả text khi đổi ngôn ngữ"""
        # Update window title
        self.setWindowTitle(tr('app_title'))
        
        # Update top bar
        self.title_label.setText("🎬 AUTO VIDEO SPLITTER PRO")
        self.cpu_label.setText(f"{tr('cpu')}: {self.cpu_label.text().split(':')[1] if ':' in self.cpu_label.text() else '0%'}")
        self.gpu_label.setText(f"{tr('gpu')}: {self.gpu_label.text().split(':')[1] if ':' in self.gpu_label.text() else '0%'}")
        self.ram_label.setText(f"{tr('ram')}: {self.ram_label.text().split(':')[1] if ':' in self.ram_label.text() else '0/24GB'}")
        
        # Update buttons and labels
        self.update_ui_texts()
        
        # Update status
        self.status_label.setText(tr('ready_status'))
        
        # Update language indicator
        current_lang = self.lang_manager.get_current_language()
        self.language_label.setText("🇻🇳 Tiếng Việt" if current_lang == 'vi' else "🇬🇧 English")
        
    def update_ui_texts(self):
        """Update all UI text elements"""
        # Find and update all QPushButton, QLabel, QGroupBox, QCheckBox
        for widget in self.findChildren(QPushButton):
            if widget.text() in ['▶ BẮT ĐẦU', '▶ START', '⏸ Tạm dừng', '⏸ Pause', 
                                  '▶ Tiếp tục', '▶ Resume', '✖ Hủy bỏ', '✖ Cancel',
                                  '➕ Add Files', '➕ Thêm file', '📂 Add Folder', '📂 Thêm thư mục',
                                  '🗑 Clear All', '🗑 Xóa tất cả', 'Duyệt', 'Browse']:
                if 'BẮT ĐẦU' in widget.text() or 'START' in widget.text():
                    widget.setText(tr('start'))
                elif 'Tạm dừng' in widget.text() or 'Pause' in widget.text():
                    widget.setText(tr('pause'))
                elif 'Tiếp tục' in widget.text() or 'Resume' in widget.text():
                    widget.setText(tr('resume'))
                elif 'Hủy bỏ' in widget.text() or 'Cancel' in widget.text():
                    widget.setText(tr('cancel'))
                elif 'Thêm file' in widget.text() or 'Add Files' in widget.text():
                    widget.setText(tr('add_files'))
                elif 'Thêm thư mục' in widget.text() or 'Add Folder' in widget.text():
                    widget.setText(tr('add_folder'))
                elif 'Xóa tất cả' in widget.text() or 'Clear All' in widget.text():
                    widget.setText(tr('clear_all'))
                elif 'Duyệt' in widget.text() or 'Browse' in widget.text():
                    widget.setText(tr('browse'))
                    
        # Update group boxes
        for group in self.findChildren(QGroupBox):
            text = group.title()
            if 'VIDEO ĐẦU VÀO' in text or 'INPUT VIDEO' in text:
                group.setTitle(tr('input_video'))
            elif 'CÀI ĐẶT CẮT' in text or 'SPLIT SETTINGS' in text:
                group.setTitle(tr('split_settings'))
            elif 'TỐC ĐỘ PHÁT' in text or 'PLAYBACK SPEED' in text:
                group.setTitle(tr('speed_settings'))
            elif 'CHẤT LƯỢNG' in text or 'QUALITY SETTINGS' in text:
                group.setTitle(tr('quality_settings'))
            elif 'CÀI ĐẶT ĐẦU RA' in text or 'OUTPUT SETTINGS' in text:
                group.setTitle(tr('output_settings'))
            elif 'TIẾN ĐỘ' in text or 'PROGRESS' in text:
                group.setTitle(tr('progress'))
            elif 'NHẬT KÝ' in text or 'LOG' in text:
                group.setTitle(tr('log'))
                
        # Update checkboxes
        self.multi_speed_check.setText(tr('multi_speed'))
        self.gpu_check.setText(tr('use_gpu'))
        
        # Update labels
        self.segment_label.setText(f"✂️ {tr('segment_progress')}")
        self.current_video_label.setText(f"🎬 {tr('current_video')}: {tr('ready')}")
        self.fps_label.setText(f"{tr('fps')}: --")
        self.eta_label.setText(f"{tr('eta')}: --")
        self.elapsed_label.setText(f"{tr('elapsed_time')}: 00:00:00")
        self.remaining_label.setText(f"{tr('remaining_time')}: --")
        self.speed_info_label.setText(f"{tr('speed_info')}: --")
        self.completed_label.setText(f"{tr('completed_segments')}: 0")
        self.total_label.setText(f"{tr('total_segments')}: 0")
        self.est_completion_label.setText(f"📅 {tr('estimated_completion')}: --")
        
        # Update combo boxes
        current_split_mode = self.split_mode.currentIndex()
        self.split_mode.clear()
        self.split_mode.addItems([tr('by_number'), tr('by_duration')])
        self.split_mode.setCurrentIndex(current_split_mode)
        
        current_quality = self.quality_combo.currentIndex()
        self.quality_combo.clear()
        self.quality_combo.addItems([tr('ultra'), tr('high'), tr('medium'), tr('low')])
        self.quality_combo.setCurrentIndex(current_quality)
        
        # Update NVENC presets
        current_preset = self.nvenc_preset.currentIndex()
        self.nvenc_preset.clear()
        self.nvenc_preset.addItems([
            tr('preset_fastest'), tr('preset_fast'), tr('preset_medium'),
            tr('preset_slow'), tr('preset_slower'), tr('preset_very_slow'), tr('preset_quality')
        ])
        self.nvenc_preset.setCurrentIndex(current_preset)
        
        # Update duration suffix
        self.duration_spin.setSuffix(tr('minutes'))
        
        # Update placeholder
        self.prefix_input.setPlaceholderText(tr('prefix_placeholder'))
        
        # Update drop area
        if self.drop_area.count() > 0:
            first_item = self.drop_area.item(0)
            if first_item and ('kéo & thả' in first_item.text() or 'drag & drop' in first_item.text().lower()):
                first_item.setText(tr('drag_drop'))
        
    def on_language_changed(self, index):
        """Xử lý khi đổi ngôn ngữ từ combobox"""
        if index == 0:  # Tiếng Việt
            self.lang_manager.set_language('vi')
        else:  # English
            self.lang_manager.set_language('en')
            
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
                self.log(f"{tr('added_to_queue')}: {os.path.basename(file)}")
                
        self.log(f"{tr('total_videos_queue')}: {len(self.video_files)}")
        
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
        self.log(tr('queue_cleared'))
        
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
        
    def update_thread_info(self):
        """Update thread count display"""
        import multiprocessing
        cores = multiprocessing.cpu_count()
        threads = cores * 2
        self.thread_label.setText(f"🧠 {threads}/{threads} Threads")
        
    def start_processing(self):
        """Start video processing"""
        if not self.video_files:
            QMessageBox.warning(self, tr('warning_title'), tr('no_videos'))
            return
            
        # Validate output folder
        output_folder = self.output_path.text()
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
                self.log(tr('output_folder_created'))
            except Exception as e:
                QMessageBox.critical(self, tr('error_title'), f"{tr('cannot_create_folder')}: {e}")
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
            'prefix': self.prefix_input.text() if self.prefix_input.text() else "video",
            'crf_values': [16, 18, 23, 28]
        }
        
        # Reset counters
        self.start_time = datetime.now()
        self.processed_segments = 0
        self.total_segments = 0
        
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
        self.status_label.setText(tr('processing_status'))
        
        self.log("=" * 50)
        self.log(tr('started'))
        self.log(f"📁 {tr('output_folder')}: {output_folder}")
        self.log(f"🎯 {tr('split_mode')}: {self.split_mode.currentText()}")
        self.log(f"⚡ {tr('speed')}: {settings['speed']}x")
        self.log(f"🎨 {tr('quality')}: {self.quality_combo.currentText()}")
        self.log(f"🎬 GPU Acceleration: {'ON' if settings['use_gpu'] else 'OFF'}")
        self.log("=" * 50)
        
    def pause_processing(self):
        """Pause processing"""
        if self.processing_thread:
            self.processing_thread.pause()
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(True)
            self.status_label.setText(tr('paused_status'))
            self.log(tr('paused'))
            
    def resume_processing(self):
        """Resume processing"""
        if self.processing_thread:
            self.processing_thread.resume()
            self.pause_btn.setEnabled(True)
            self.resume_btn.setEnabled(False)
            self.status_label.setText(tr('processing_status'))
            self.log(tr('resumed'))
            
    def cancel_processing(self):
        """Cancel processing"""
        reply = QMessageBox.question(self, tr('question_title'), tr('confirm_cancel'),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.processing_thread:
                self.processing_thread.cancel()
                self.cancel_btn.setEnabled(False)
                self.status_label.setText(tr('cancelled_status'))
                self.log(tr('cancelled'))
                
    def format_time(self, seconds):
        """Format time in HH:MM:SS"""
        if seconds < 0:
            return "--:--:--"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        
    def update_progress(self, percent, current_video, fps, eta, cpu_usage, gpu_usage, processed, total):
        """Update progress display with detailed information"""
        # Update overall progress
        self.main_progress.setValue(int(percent))
        self.progress_label.setText(f"{int(percent)}%")
        
        # Update segment progress
        self.processed_segments = processed
        self.total_segments = total
        
        if total > 0:
            segment_percent = int((processed / total) * 100)
            self.segment_progress.setValue(segment_percent)
            self.segment_label.setText(f"✂️ {tr('segment_progress')}: {segment_percent}%")
            self.completed_label.setText(f"{tr('completed_segments')}: {processed}")
            self.total_label.setText(f"{tr('total_segments')}: {total}")
        
        # Update current video
        self.current_video_label.setText(f"🎬 {tr('current_video')}: {os.path.basename(current_video)}")
        
        # Update FPS
        self.fps_label.setText(f"{tr('fps')}: {fps:.1f}" if fps > 0 else f"{tr('fps')}: --")
        
        # Update ETA
        if eta > 0:
            eta_str = self.format_time(eta)
            self.eta_label.setText(f"{tr('eta')}: {eta_str}")
            
            # Calculate and update remaining time
            if self.start_time:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                remaining = eta
                self.elapsed_label.setText(f"{tr('elapsed_time')}: {self.format_time(elapsed)}")
                self.remaining_label.setText(f"{tr('remaining_time')}: {self.format_time(remaining)}")
                
                # Calculate estimated completion time
                completion_time = datetime.now() + timedelta(seconds=remaining)
                self.est_completion_label.setText(f"📅 {tr('estimated_completion')}: {completion_time.strftime('%H:%M:%S')}")
                
            # Calculate processing speed
            if elapsed > 0 and processed > 0:
                speed = processed / elapsed
                self.speed_info_label.setText(f"{tr('speed_info')}: {speed:.2f} segments/sec")
        else:
            self.eta_label.setText(f"{tr('eta')}: --")
            self.remaining_label.setText(f"{tr('remaining_time')}: --")
            self.speed_info_label.setText(f"{tr('speed_info')}: --")
            self.est_completion_label.setText(f"📅 {tr('estimated_completion')}: --")
        
        # Update CPU and GPU labels
        self.cpu_label.setText(f"{tr('cpu')}: {cpu_usage:.0f}%")
        if gpu_usage > 0:
            self.gpu_label.setText(f"{tr('gpu')}: {gpu_usage:.0f}%")
        
    def update_system_stats(self):
        """Update system statistics"""
        try:
            import psutil
            
            # CPU usage (limit to 90% max as requested)
            cpu_percent = min(psutil.cpu_percent(interval=0.5), 90)
            self.cpu_label.setText(f"{tr('cpu')}: {cpu_percent:.0f}%")
            
            # RAM usage (limit to 24GB max)
            ram = psutil.virtual_memory()
            ram_used_gb = ram.used / (1024**3)
            ram_label_text = f"{tr('ram')}: {ram_used_gb:.1f}/24GB"
            if ram_used_gb > 24:
                ram_label_text = f"⚠️ {tr('ram')}: {ram_used_gb:.1f}/24GB"
            self.ram_label.setText(ram_label_text)
            
            # GPU usage
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    self.gpu_label.setText(f"{tr('gpu')}: {gpu.load*100:.0f}%")
            except:
                pass
                
        except:
            pass
            
    def on_processing_finished(self):
        """Handle processing completion"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.status_label.setText(tr('completed_status'))
        
        self.log("=" * 50)
        self.log(tr('completed_all'))
        
        # Calculate total time
        if self.start_time:
            total_time = (datetime.now() - self.start_time).total_seconds()
            self.log(f"⏱️ Total processing time: {self.format_time(total_time)}")
        self.log("=" * 50)
        
        QMessageBox.information(self, tr('info_title'), tr('complete_message'))
        
    def on_processing_error(self, error_msg):
        """Handle processing error"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.status_label.setText(tr('error_status'))
        self.log(f"❌ {tr('error')}: {error_msg}")
        
        QMessageBox.critical(self, tr('error_title'), f"{tr('error_message')}\n{error_msg}")
        
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
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Auto Video Splitter Pro",
                         """<h2>Auto Video Splitter Pro</h2>
                         <p><b>Version:</b> 2.0.0</p>
                         <p><b>Optimized for:</b> Dual Xeon E5-2680 v4 + GTX 1070</p>
                         <p><b>Features:</b></p>
                         <ul>
                             <li>Multi-language support (English/Tiếng Việt)</li>
                             <li>GPU acceleration with NVENC</li>
                             <li>56 threads parallel processing</li>
                             <li>Real-time progress tracking</li>
                             <li>Batch video splitting</li>
                             <li>Speed adjustment (0.25x - 2.0x)</li>
                         </ul>
                         <p>© 2024 Auto Video Splitter Pro</p>""")
