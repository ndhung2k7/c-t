#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Video Splitter Module - Calculates split points
"""

from typing import List, Dict


class VideoSplitter:
    """Calculate video split points based on user settings"""
    
    def __init__(self, settings: Dict):
        self.settings = settings
        
    def calculate_segments(self, total_duration: float) -> List[Dict]:
        """
        Calculate video segments based on split mode
        
        Args:
            total_duration: Total video duration in seconds
            
        Returns:
            List of segment dicts with 'index', 'start', 'end'
        """
        segments = []
        
        split_mode = self.settings.get('split_mode', 0)
        
        if split_mode == 0:  # By number of videos
            num_videos = self.settings.get('num_videos', 10)
            segment_duration = total_duration / num_videos
            
            for i in range(num_videos):
                start = i * segment_duration
                end = (i + 1) * segment_duration
                
                # Handle last segment
                if i == num_videos - 1:
                    end = total_duration
                    
                segments.append({
                    'index': i + 1,
                    'start': start,
                    'end': end,
                    'duration': end - start
                })
                
        else:  # By duration
            duration_minutes = self.settings.get('duration_minutes', 10)
            segment_duration = duration_minutes * 60  # Convert to seconds
            
            num_segments = int(total_duration / segment_duration)
            if total_duration % segment_duration > 0:
                num_segments += 1
                
            for i in range(num_segments):
                start = i * segment_duration
                end = min((i + 1) * segment_duration, total_duration)
                
                segments.append({
                    'index': i + 1,
                    'start': start,
                    'end': end,
                    'duration': end - start
                })
                
        return segments
        
    def get_optimal_chunk_size(self, total_duration: float) -> int:
        """Get optimal chunk size based on video length"""
        if total_duration < 300:  # < 5 minutes
            return 30  # 30 second chunks
        elif total_duration < 1800:  # < 30 minutes
            return 60  # 1 minute chunks
        elif total_duration < 3600:  # < 1 hour
            return 180  # 3 minute chunks
        else:
            return 300  # 5 minute chunks
