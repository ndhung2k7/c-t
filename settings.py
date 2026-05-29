#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settings Module - User preferences and configuration
"""

import json
import os


class Settings:
    """Manage application settings"""
    
    def __init__(self):
        self.settings_file = os.path.join(os.path.expanduser("~"), ".video_splitter_settings.json")
        self.default_settings = {
            'output_folder': os.path.join(os.path.expanduser("~"), "Videos", "Split"),
            'output_format': 'mp4',
            'quality': 2,  # Medium
            'use_gpu': True,
            'nvenc_preset': 4,  # p4
            'split_mode': 0,  # By number
            'num_videos': 10,
            'duration_minutes': 10,
            'default_speed': 1.0,
            'dark_theme': True,
            'auto_save_queue': True,
            'max_parallel': 0,  # Auto-detect
            'cpu_limit': 90,
            'ram_limit_gb': 24
        }
        self.settings = self.load_settings()
        
    def load_settings(self) -> dict:
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    merged = self.default_settings.copy()
                    merged.update(loaded)
                    return merged
        except Exception as e:
            print(f"Error loading settings: {e}")
            
        return self.default_settings.copy()
        
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def get(self, key: str, default=None):
        """Get setting value"""
        return self.settings.get(key, default)
        
    def set(self, key: str, value):
        """Set setting value"""
        self.settings[key] = value
        self.save_settings()
        
    def get_optimal_workers(self) -> int:
        """Calculate optimal number of parallel workers"""
        import multiprocessing
        
        cpu_count = multiprocessing.cpu_count()
        ram_gb = self._get_available_ram_gb()
        
        # Limit based on CPU cores
        max_workers = cpu_count
        
        # Limit based on RAM (rough estimate: 2GB per worker)
        ram_limited = int(ram_gb / 2)
        
        # Use the lower limit
        workers = min(max_workers, ram_limited)
        
        # Apply user limit if set
        user_limit = self.get('max_parallel', 0)
        if user_limit > 0:
            workers = min(workers, user_limit)
            
        # Ensure at least 1 worker
        return max(1, workers)
        
    def _get_available_ram_gb(self) -> float:
        """Get available RAM in GB"""
        try:
            import psutil
            ram = psutil.virtual_memory()
            available_gb = ram.available / (1024**3)
            
            # Apply user limit
            user_limit = self.get('ram_limit_gb', 24)
            return min(available_gb, user_limit)
        except:
            return 16  # Default fallback
