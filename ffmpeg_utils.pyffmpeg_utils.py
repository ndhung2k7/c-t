#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFmpeg Utilities - Handle FFmpeg operations
"""

import subprocess
import os
import sys
import urllib.request
import zipfile
import platform
from typing import Dict, Optional, List


class FFmpegUtils:
    """Utility class for FFmpeg operations"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        if not self.ffmpeg_path:
            self.ffmpeg_path = self._download_ffmpeg()
            
    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg in system PATH or local directory"""
        
        # Check in same directory
        if platform.system() == "Windows":
            local_path = os.path.join(os.path.dirname(sys.argv[0]), "ffmpeg.exe")
            if os.path.exists(local_path):
                return local_path
                
        # Check PATH
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return 'ffmpeg'
        except:
            pass
            
        return None
        
    def _download_ffmpeg(self) -> Optional[str]:
        """Download FFmpeg if not available"""
        print("📥 Downloading FFmpeg...")
        
        system = platform.system()
        
        if system == "Windows":
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            zip_path = "ffmpeg.zip"
            extract_dir = "ffmpeg_temp"
            
            try:
                # Download
                urllib.request.urlretrieve(url, zip_path)
                
                # Extract
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                    
                # Find ffmpeg.exe
                for root, dirs, files in os.walk(extract_dir):
                    if 'ffmpeg.exe' in files:
                        exe_path = os.path.join(root, 'ffmpeg.exe')
                        dest_path = os.path.join(os.path.dirname(sys.argv[0]), 'ffmpeg.exe')
                        os.rename(exe_path, dest_path)
                        break
                        
                # Cleanup
                os.remove(zip_path)
                import shutil
                shutil.rmtree(extract_dir)
                
                print("✅ FFmpeg downloaded successfully")
                return dest_path
                
            except Exception as e:
                print(f"❌ Failed to download FFmpeg: {e}")
                return None
        else:
            print("⚠️ Please install FFmpeg manually:")
            print("  Ubuntu/Debian: sudo apt install ffmpeg")
            print("  macOS: brew install ffmpeg")
            return None
            
    def get_video_info(self, video_path: str) -> Optional[Dict]:
        """Get video information using ffprobe"""
        
        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-f', 'null',
            '-'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse duration from stderr
            output = result.stderr
            
            # Find duration
            import re
            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', output)
            
            if duration_match:
                hours = int(duration_match.group(1))
                minutes = int(duration_match.group(2))
                seconds = float(duration_match.group(3))
                duration = hours * 3600 + minutes * 60 + seconds
                
                # Find video stream info
                video_match = re.search(r'Video: (\w+).*? (\d{3,4})x(\d{3,4})', output)
                width, height = 1920, 1080
                codec = 'h264'
                
                if video_match:
                    codec = video_match.group(1)
                    width = int(video_match.group(2))
                    height = int(video_match.group(3))
                    
                return {
                    'duration': duration,
                    'width': width,
                    'height': height,
                    'codec': codec,
                    'path': video_path
                }
                
        except Exception as e:
            print(f"Error getting video info: {e}")
            
        return None
        
    def build_cpu_command(self, input_file: str, output_file: str,
                         start_time: float, end_time: float,
                         crf: int, speed: float) -> List[str]:
        """Build FFmpeg command for CPU encoding"""
        
        duration = end_time - start_time
        
        cmd = [
            self.ffmpeg_path,
            '-ss', str(start_time),
            '-i', input_file,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-crf', str(crf),
            '-preset', 'medium',
        ]
        
        # Handle speed change
        if speed != 1.0:
            cmd.extend([
                '-filter_complex', f'[0:v]setpts={1/speed}*PTS[v];[0:a]atempo={speed}[a]',
                '-map', '[v]',
                '-map', '[a]'
            ])
        else:
            cmd.extend([
                '-c:a', 'aac',
                '-b:a', '192k'
            ])
            
        cmd.extend(['-y', output_file])
        
        return cmd#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFmpeg Utilities - Handle FFmpeg operations
"""

import subprocess
import os
import sys
import urllib.request
import zipfile
import platform
from typing import Dict, Optional, List


class FFmpegUtils:
    """Utility class for FFmpeg operations"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        if not self.ffmpeg_path:
            self.ffmpeg_path = self._download_ffmpeg()
            
    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg in system PATH or local directory"""
        
        # Check in same directory
        if platform.system() == "Windows":
            local_path = os.path.join(os.path.dirname(sys.argv[0]), "ffmpeg.exe")
            if os.path.exists(local_path):
                return local_path
                
        # Check PATH
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return 'ffmpeg'
        except:
            pass
            
        return None
        
    def _download_ffmpeg(self) -> Optional[str]:
        """Download FFmpeg if not available"""
        print("📥 Downloading FFmpeg...")
        
        system = platform.system()
        
        if system == "Windows":
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            zip_path = "ffmpeg.zip"
            extract_dir = "ffmpeg_temp"
            
            try:
                # Download
                urllib.request.urlretrieve(url, zip_path)
                
                # Extract
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                    
                # Find ffmpeg.exe
                for root, dirs, files in os.walk(extract_dir):
                    if 'ffmpeg.exe' in files:
                        exe_path = os.path.join(root, 'ffmpeg.exe')
                        dest_path = os.path.join(os.path.dirname(sys.argv[0]), 'ffmpeg.exe')
                        os.rename(exe_path, dest_path)
                        break
                        
                # Cleanup
                os.remove(zip_path)
                import shutil
                shutil.rmtree(extract_dir)
                
                print("✅ FFmpeg downloaded successfully")
                return dest_path
                
            except Exception as e:
                print(f"❌ Failed to download FFmpeg: {e}")
                return None
        else:
            print("⚠️ Please install FFmpeg manually:")
            print("  Ubuntu/Debian: sudo apt install ffmpeg")
            print("  macOS: brew install ffmpeg")
            return None
            
    def get_video_info(self, video_path: str) -> Optional[Dict]:
        """Get video information using ffprobe"""
        
        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-f', 'null',
            '-'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse duration from stderr
            output = result.stderr
            
            # Find duration
            import re
            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', output)
            
            if duration_match:
                hours = int(duration_match.group(1))
                minutes = int(duration_match.group(2))
                seconds = float(duration_match.group(3))
                duration = hours * 3600 + minutes * 60 + seconds
                
                # Find video stream info
                video_match = re.search(r'Video: (\w+).*? (\d{3,4})x(\d{3,4})', output)
                width, height = 1920, 1080
                codec = 'h264'
                
                if video_match:
                    codec = video_match.group(1)
                    width = int(video_match.group(2))
                    height = int(video_match.group(3))
                    
                return {
                    'duration': duration,
                    'width': width,
                    'height': height,
                    'codec': codec,
                    'path': video_path
                }
                
        except Exception as e:
            print(f"Error getting video info: {e}")
            
        return None
        
    def build_cpu_command(self, input_file: str, output_file: str,
                         start_time: float, end_time: float,
                         crf: int, speed: float) -> List[str]:
        """Build FFmpeg command for CPU encoding"""
        
        duration = end_time - start_time
        
        cmd = [
            self.ffmpeg_path,
            '-ss', str(start_time),
            '-i', input_file,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-crf', str(crf),
            '-preset', 'medium',
        ]
        
        # Handle speed change
        if speed != 1.0:
            cmd.extend([
                '-filter_complex', f'[0:v]setpts={1/speed}*PTS[v];[0:a]atempo={speed}[a]',
                '-map', '[v]',
                '-map', '[a]'
            ])
        else:
            cmd.extend([
                '-c:a', 'aac',
                '-b:a', '192k'
            ])
            
        cmd.extend(['-y', output_file])
        
        return cmd
