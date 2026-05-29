#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPU Encoder Module - NVIDIA NVENC acceleration
Optimized for GTX 1070
"""

import subprocess
import os
from typing import List


class GPUEncoder:
    """Handle GPU-accelerated encoding with NVENC"""
    
    def __init__(self, settings: dict):
        self.settings = settings
        self.nvenc_available = self._check_nvenc()
        
    def _check_nvenc(self) -> bool:
        """Check if NVENC is available on the system"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-encoders'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Check for h264_nvenc or hevc_nvenc
            if 'h264_nvenc' in result.stdout or 'hevc_nvenc' in result.stdout:
                return True
            else:
                return False
                
        except Exception:
            return False
            
    def is_available(self) -> bool:
        """Return NVENC availability"""
        return self.nvenc_available
        
    def build_nvenc_command(self, input_file: str, output_file: str, 
                           start_time: float, end_time: float,
                           crf: int, speed: float, preset: int) -> List[str]:
        """
        Build FFmpeg command with NVENC acceleration
        
        Args:
            input_file: Source video file
            output_file: Output file path
            start_time: Start time in seconds
            end_time: End time in seconds
            crf: Quality CRF value (16-28)
            speed: Playback speed multiplier
            preset: NVENC preset (1-7, p1 fastest to p7 quality)
        """
        
        # NVENC presets mapping
        presets = {
            1: 'p1',  # Fastest
            2: 'p2',
            3: 'p3',
            4: 'p4',
            5: 'p5',
            6: 'p6',
            7: 'p7'   # Best quality
        }
        
        nvenc_preset = presets.get(preset, 'p4')
        
        # Calculate duration
        duration = end_time - start_time
        
        # Build command
        cmd = [
            'ffmpeg',
            '-ss', str(start_time),  # Seek to start
            '-i', input_file,
            '-t', str(duration),  # Duration
            '-c:v', 'h264_nvenc',  # NVENC video codec
            '-preset', nvenc_preset,
            '-rc', 'vbr',  # Variable bitrate
            '-cq', str(crf),  # Quality
            '-b:v', '0',  # Let CQ control bitrate
            '-maxrate', '30M',  # Max bitrate
            '-bufsize', '60M',
        ]
        
        # Handle speed change
        if speed != 1.0:
            # Adjust PTS for speed change
            cmd.extend([
                '-filter_complex', f'[0:v]setpts={1/speed}*PTS[v];[0:a]atempo={speed}[a]',
                '-map', '[v]',
                '-map', '[a]'
            ])
        else:
            cmd.extend([
                '-c:a', 'aac',  # Audio codec
                '-b:a', '192k'
            ])
            
        # Output format specific settings
        output_format = output_file.split('.')[-1].lower()
        
        if output_format == 'mp4':
            cmd.extend(['-movflags', '+faststart'])
        elif output_format == 'mkv':
            pass  # MKV doesn't need special flags
        
        # Add output file (overwrite if exists)
        cmd.extend(['-y', output_file])
        
        return cmd
        
    def get_gpu_info(self) -> dict:
        """Get GPU information using nvidia-smi"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total,memory.used,utilization.gpu', '--format=csv'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                data = lines[1].split(', ')
                return {
                    'name': data[0],
                    'memory_total': data[1],
                    'memory_used': data[2],
                    'gpu_util': data[3]
                }
        except:
            pass
            
        return {'name': 'Unknown', 'available': False}
