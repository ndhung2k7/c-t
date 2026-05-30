#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import multiprocessing

class Settings:
    """Quản lý cài đặt ứng dụng"""
    
    def __init__(self):
        self.settings_file = os.path.join(
            os.path.expanduser("~"), 
            ".auto_video_splitter_settings.json"
        )
        self.default_settings = {
            'output_folder': os.path.join(os.path.expanduser("~"), "Videos", "Split"),
            'output_format': 'mp4',
            'quality': 2,
            'use_gpu': True,
            'nvenc_preset': 4,
            'split_mode': 0,
            'num_videos': 10,
            'duration_minutes': 10,
            'default_speed': 1.0,
            'dark_theme': True,
            'auto_save_queue': True,
            'max_parallel': 0,
            'cpu_limit': 90,
            'ram_limit_gb': 24
        }
        self.settings = self.load_settings()
        
    def load_settings(self):
        """Tải cài đặt từ file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    merged = self.default_settings.copy()
                    merged.update(loaded)
                    return merged
        except Exception as e:
            print(f"Lỗi tải settings: {e}")
        return self.default_settings.copy()
        
    def save_settings(self):
        """Lưu cài đặt"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Lỗi lưu settings: {e}")
            
    def get(self, key, default=None):
        return self.settings.get(key, default)
        
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
        
    def get_optimal_workers(self):
        """Tính số lượng workers tối ưu"""
        cpu_count = multiprocessing.cpu_count()
        # Giới hạn theo RAM (mỗi worker ~1GB)
        try:
            import psutil
            ram_gb = psutil.virtual_memory().available / (1024**3)
            ram_limited = int(ram_gb / 1.5)
        except:
            ram_limited = 16
            
        workers = min(cpu_count, ram_limited, 48)
        return max(1, workers)
