#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Video Processing Module - Handles video splitting and encoding
Optimized for Dual Xeon E5-2680 v4 + GTX 1070
"""

import os
import sys
import subprocess
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any
import json
import time
import psutil

from splitter import VideoSplitter
from gpu_encoder import GPUEncoder
from ffmpeg_utils import FFmpegUtils


class VideoProcessor:
    """Main video processing engine optimized for Dual Xeon"""
    
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.splitter = VideoSplitter(settings)
        self.gpu_encoder = GPUEncoder(settings)
        self.ffmpeg = FFmpegUtils()
        
        # System optimization settings
        self.total_cores = multiprocessing.cpu_count()
        self.total_threads = self.total_cores * 2  # Hyperthreading
        self.optimal_workers = min(self.total_threads - 4, 48)  # Leave room for system
        self.max_ram_gb = 24  # Limit as requested
        self.cpu_limit = 90  # Percentage
        
        # State
        self.is_paused = False
        self.is_cancelled = False
        self.progress = 0
        self.current_video = ""
        
        # Signals (will be connected from UI)
        self.progress_callback = None
        self.log_callback = None
        
        # Statistics
        self.stats = {
            'total_segments': 0,
            'processed_segments': 0,
            'start_time': None,
            'fps': 0
        }
        
    def process_videos(self, video_files: List[str]):
        """Process multiple videos with parallel optimization"""
        
        self.stats['start_time'] = time.time()
        self.stats['total_videos'] = len(video_files)
        
        # Analyze all videos first for better scheduling
        video_info_list = []
        for video_file in video_files:
            info = self.ffmpeg.get_video_info(video_file)
            if info:
                video_info_list.append(info)
                
        # Calculate total segments
        for info in video_info_list:
            segments = self.splitter.calculate_segments(info['duration'])
            self.stats['total_segments'] += len(segments)
            
        self.log(f"📊 Total segments to process: {self.stats['total_segments']}")
        self.log(f"🚀 Using {self.optimal_workers} parallel workers on {self.total_threads} threads")
        
        # Process videos with parallel execution
        with ProcessPoolExecutor(max_workers=self.optimal_workers) as executor:
            futures = []
            
            for video_file in video_files:
                if self.is_cancelled:
                    break
                    
                future = executor.submit(self._process_single_video, video_file)
                futures.append(future)
                
            # Monitor progress
            for future in as_completed(futures):
                if self.is_cancelled:
                    break
                try:
                    result = future.result()
                    if result:
                        self.stats['processed_segments'] += result
                        self._update_progress()
                except Exception as e:
                    self.log(f"❌ Error processing video: {e}")
                    
        total_time = time.time() - self.stats['start_time']
        self.log(f"✅ Processing completed in {total_time:.1f} seconds")
        
    def _process_single_video(self, video_file: str) -> int:
        """Process a single video file"""
        self.current_video = os.path.basename(video_file)
        self.log(f"🎬 Processing: {self.current_video}")
        
        # Get video info
        video_info = self.ffmpeg.get_video_info(video_file)
        if not video_info:
            self.log(f"❌ Cannot read video info: {video_file}")
            return 0
            
        # Calculate segments
        segments = self.splitter.calculate_segments(video_info['duration'])
        
        # Determine speeds to process
        speeds = [self.settings['speed']]
        if self.settings.get('multi_speed', False):
            speeds = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
            self.log(f"🎚️ Multi-speed mode: Processing {len(speeds)} speeds")
            
        # Process each segment
        segments_processed = 0
        for segment in segments:
            if self.is_cancelled:
                break
                
            while self.is_paused:
                time.sleep(0.5)
                
            # Process all speeds for this segment
            for speed in speeds:
                if self._process_segment(video_file, video_info, segment, speed):
                    segments_processed += 1
                    
            # Update progress
            self._update_progress()
            
        self.log(f"✅ Completed: {self.current_video}")
        return segments_processed
        
    def _process_segment(self, video_file: str, video_info: Dict, segment: Dict, speed: float) -> bool:
        """Process a single video segment with optional GPU acceleration"""
        
        # Generate output filename
        output_format = self.settings['output_format']
        prefix = self.settings.get('prefix', 'video')
        
        # Handle multi-speed naming
        speed_suffix = ""
        if speed != 1.0:
            speed_suffix = f"_{int(speed*100)}x"
            
        output_filename = f"{prefix}_{segment['index']:04d}{speed_suffix}.{output_format}"
        output_path = os.path.join(self.settings['output_folder'], output_filename)
        
        # Skip if already exists
        if os.path.exists(output_path):
            self.log(f"⏭️ Skipping existing: {output_filename}")
            return True
            
        # Get quality settings
        crf = self.settings['crf_values'][self.settings['quality']]
        
        # Build FFmpeg command
        if self.settings['use_gpu'] and self.gpu_encoder.is_available():
            # GPU encoding
            cmd = self.gpu_encoder.build_nvenc_command(
                video_file, output_path, segment['start'], segment['end'],
                crf, speed, self.settings['nvenc_preset']
            )
        else:
            # CPU encoding
            cmd = self.ffmpeg.build_cpu_command(
                video_file, output_path, segment['start'], segment['end'],
                crf, speed
            )
            
        # Execute command
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                timeout=3600  # 1 hour timeout per segment
            )
            
            if result.returncode == 0:
                self.log(f"✓ Created: {output_filename} (Speed: {speed}x)")
                return True
            else:
                self.log(f"❌ Failed: {output_filename} - {result.stderr[:200]}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"⏰ Timeout: {output_filename}")
            return False
        except Exception as e:
            self.log(f"❌ Error processing segment: {e}")
            return False
            
    def _update_progress(self):
        """Update progress statistics"""
        if self.stats['total_segments'] > 0:
            progress_pct = (self.stats['processed_segments'] / self.stats['total_segments']) * 100
            
            # Calculate ETA
            elapsed = time.time() - self.stats['start_time']
            if self.stats['processed_segments'] > 0:
                eta = (elapsed / self.stats['processed_segments']) * (self.stats['total_segments'] - self.stats['processed_segments'])
            else:
                eta = 0
                
            # Calculate FPS
            if elapsed > 0:
                fps = self.stats['processed_segments'] / elapsed
            else:
                fps = 0
                
            # Get system stats
            cpu_usage = psutil.cpu_percent()
            gpu_usage = 0
            
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_usage = gpus[0].load * 100
            except:
                pass
                
            # Emit progress
            if self.progress_callback:
                self.progress_callback(progress_pct, self.current_video, fps, eta, cpu_usage, gpu_usage)
                
    def pause(self):
        """Pause processing"""
        self.is_paused = True
        self.log("⏸ Processing paused")
        
    def resume(self):
        """Resume processing"""
        self.is_paused = False
        self.log("▶ Processing resumed")
        
    def cancel(self):
        """Cancel processing"""
        self.is_cancelled = True
        self.log("✖ Processing cancelled")
        
    def log(self, message: str):
        """Log message with callback"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        
        if self.log_callback:
            self.log_callback(log_line)
        else:
            print(log_line)
