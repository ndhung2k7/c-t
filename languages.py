#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Fix encoding cho Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

class LanguageManager:
    """Quản lý ngôn ngữ cho ứng dụng"""
    
    def __init__(self):
        self._current_language = 'vi'
        self._strings = {}
        self.load_languages()
        
    def load_languages(self):
        """Tải tất cả ngôn ngữ"""
        self._strings = {
            'vi': {
                'app_title': 'Auto Video Splitter Pro - Tối ưu cho Dual Xeon',
                'ready': 'Sẵn sàng',
                'processing': 'Đang xử lý...',
                'paused': 'Đã tạm dừng',
                'completed': 'Hoàn thành',
                'error': 'Lỗi',
                'input_video': 'Video đầu vào',
                'split_settings': 'Cài đặt cắt',
                'speed_settings': 'Tốc độ phát',
                'quality_settings': 'Chất lượng',
                'output_settings': 'Đầu ra',
                'start': 'Bắt đầu',
                'pause': 'Tạm dừng',
                'resume': 'Tiếp tục',
                'cancel': 'Hủy bỏ',
                'progress': 'Tiến độ',
                'log': 'Nhật ký',
                'fps': 'FPS',
                'eta': 'Thời gian còn lại',
            },
            'en': {
                'app_title': 'Auto Video Splitter Pro - Optimized for Dual Xeon',
                'ready': 'Ready',
                'processing': 'Processing...',
                'paused': 'Paused',
                'completed': 'Completed',
                'error': 'Error',
                'input_video': 'Input Video',
                'split_settings': 'Split Settings',
                'speed_settings': 'Playback Speed',
                'quality_settings': 'Quality',
                'output_settings': 'Output',
                'start': 'Start',
                'pause': 'Pause',
                'resume': 'Resume',
                'cancel': 'Cancel',
                'progress': 'Progress',
                'log': 'Log',
                'fps': 'FPS',
                'eta': 'ETA',
            }
        }
        
    def get_string(self, key):
        return self._strings.get(self._current_language, {}).get(key, key)
    
    def set_language(self, lang_code):
        if lang_code in self._strings:
            self._current_language = lang_code
            
    def tr(self, key):
        return self.get_string(key)


_lang_manager = None

def get_language_manager():
    global _lang_manager
    if _lang_manager is None:
        _lang_manager = LanguageManager()
    return _lang_manager

def tr(key):
    return get_language_manager().get_string(key)
