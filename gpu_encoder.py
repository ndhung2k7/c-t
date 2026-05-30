#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

class GPUEncoder:
    """Xử lý encoding bằng GPU NVIDIA"""
    
    def __init__(self, settings):
        self.settings = settings
        self.nvenc_available = self._check_nvenc()
        
    def _check_nvenc(self):
        """Kiểm tra NVENC có sẵn không"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-encoders'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return 'h264_nvenc' in result.stdout
        except:
            return False
            
    def is_available(self):
        return self.nvenc_available
        
    def build_nvenc_command(self, input_file, output_file, start_time, end_time, crf, speed, preset):
        """Xây dựng lệnh FFmpeg với NVENC"""
        duration = end_time - start_time
        
        cmd = [
            'ffmpeg',
            '-ss', str(start_time),
            '-i', input_file,
            '-t', str(duration),
            '-c:v', 'h264_nvenc',
            '-preset', f'p{preset}',
            '-cq', str(crf),
            '-b:v', '0',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            output_file
        ]
        
        # Xử lý speed
        if speed != 1.0:
            cmd.insert(-2, '-filter_complex')
            cmd.insert(-2, f'[0:v]setpts={1/speed}*PTS[v];[0:a]atempo={speed}[a]')
            cmd.insert(-2, '-map')
            cmd.insert(-2, '[v]')
            cmd.insert(-2, '-map')
            cmd.insert(-2, '[a]')
            
        return cmd
