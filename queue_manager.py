#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Queue Manager - Handles task persistence and recovery
"""

import json
import os
from datetime import datetime
from typing import List, Dict


class QueueManager:
    """Manage processing queue with persistence"""
    
    def __init__(self):
        self.queue_file = os.path.join(os.path.expanduser("~"), ".video_splitter_queue.json")
        self.current_queue = []
        
    def save_queue(self, queue_data: List[Dict]):
        """Save queue to disk"""
        try:
            with open(self.queue_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'queue': queue_data
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving queue: {e}")
            
    def load_queue(self) -> List[Dict]:
        """Load queue from disk"""
        try:
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r') as f:
                    data = json.load(f)
                    return data.get('queue', [])
        except Exception as e:
            print(f"Error loading queue: {e}")
            
        return []
        
    def add_to_queue(self, task: Dict):
        """Add task to queue"""
        self.current_queue.append(task)
        self.save_queue(self.current_queue)
        
    def remove_from_queue(self, task_id: str):
        """Remove task from queue"""
        self.current_queue = [t for t in self.current_queue if t.get('id') != task_id]
        self.save_queue(self.current_queue)
        
    def clear_queue(self):
        """Clear entire queue"""
        self.current_queue = []
        self.save_queue([])
        
    def get_pending_tasks(self) -> List[Dict]:
        """Get pending tasks"""
        return self.current_queue
