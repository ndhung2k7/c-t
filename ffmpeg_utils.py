#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import urllib.request
import zipfile
import platform
import shutil

class FFmpegUtils:
    """Quản lý FFmpeg"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        if not self.ffmpeg_path:
            self.ffmpeg_path = self._download_ffmpeg()
            
    def _find_ffmpeg(self):
        """Tìm FFmpeg trong hệ thống"""
        # Kiểm tra trong thư mục hiện tại
        if platform.system() == "Windows":
            local_path = os.path.join(os.path.dirname(sys.argv[0]), "ffmpeg.exe")
            if os.path.exists(local_path):
                return local_path
                
        # Kiểm tra trong PATH
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return 'ffmpeg'
        except:
            pass
            
        return None
        
    def _download_ffmpeg(self):
        """Tải FFmpeg nếu chưa có"""
        print("Đang tải FFmpeg... Vui lòng chờ")
        
        if platform.system() == "Windows":
            # Sử dụng URL dự phòng
            urls = [
                "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
                "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            ]
            
            for url in urls:
                try:
                    zip_path = "ffmpeg_temp.zip"
                    extract_dir = "ffmpeg_extract"
                    
                    # Tải file
                    print(f"Đang tải từ: {url}")
                    urllib.request.urlretrieve(url, zip_path)
                    
                    # Giải nén
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    
                    # Tìm ffmpeg.exe
                    for root, dirs, files in os.walk(extract_dir):
                        if 'ffmpeg.exe' in files:
                            src = os.path.join(root, 'ffmpeg.exe')
                            dst = os.path.join(os.path.dirname(sys.argv[0]), 'ffmpeg.exe')
                            shutil.copy2(src, dst)
                            print("Đã tải FFmpeg thành công!")
                            
                            # Dọn dẹp
                            os.remove(zip_path)
                            shutil.rmtree(extract_dir)
                            return dst
                            
                except Exception as e:
                    print(f"Lỗi khi tải từ {url}: {e}")
                    continue
                    
            print("Không thể tải FFmpeg. Vui lòng tải thủ công từ: https://ffmpeg.org/")
            
        return None
        
    def get_video_info(self, video_path):
        """Lấy thông tin video"""
        if not self.ffmpeg_path:
            return None
            
        try:
            cmd = [self.ffmpeg_path, '-i', video_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse duration
            import re
            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', result.stderr)
            if duration_match:
                hours = int(duration_match.group(1))
                minutes = int(duration_match.group(2))
                seconds = float(duration_match.group(3))
                duration = hours * 3600 + minutes * 60 + seconds
                
                return {
                    'duration': duration,
                    'path': video_path
                }
        except Exception as e:
            print(f"Lỗi đọc video: {e}")
            
        return None
