#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Language Module - Đa ngôn ngữ cho Auto Video Splitter Pro
Hỗ trợ: Tiếng Việt, English
"""

from PyQt6.QtCore import QObject, pyqtSignal


class LanguageManager(QObject):
    """Quản lý ngôn ngữ cho ứng dụng"""
    
    language_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._current_language = 'vi'  # Mặc định Tiếng Việt
        self._strings = {}
        self.load_languages()
        
    def load_languages(self):
        """Tải tất cả ngôn ngữ"""
        self._strings = {
            'vi': {
                # Window & Menu
                'app_title': 'Auto Video Splitter Pro - Tối ưu cho Dual Xeon',
                'ready': '✅ Sẵn sàng',
                'processing': '🔄 Đang xử lý...',
                'paused': '⏸ Đã tạm dừng',
                'cancelling': '❌ Đang hủy...',
                'completed': '✅ Hoàn thành',
                'error': '❌ Lỗi',
                
                # Top bar
                'cpu': 'CPU',
                'gpu': 'GPU',
                'ram': 'RAM',
                'threads': 'Luồng',
                
                # Input section
                'input_video': '📁 VIDEO ĐẦU VÀO',
                'drag_drop': '🎯 Kéo & thả video hoặc thư mục vào đây',
                'add_files': '➕ Thêm file',
                'add_folder': '📂 Thêm thư mục',
                'clear_all': '🗑 Xóa tất cả',
                
                # Split settings
                'split_settings': '⚙️ CÀI ĐẶT CẮT',
                'split_mode': 'Chế độ cắt:',
                'by_number': 'Theo số lượng video',
                'by_duration': 'Theo thời lượng',
                'num_videos': 'Số lượng video:',
                'duration': 'Thời lượng mỗi phần:',
                'minutes': ' phút',
                
                # Speed settings
                'speed_settings': '🎬 TỐC ĐỘ PHÁT',
                'speed': 'Tốc độ:',
                'multi_speed': 'Xuất nhiều tốc độ cùng lúc',
                
                # Quality settings
                'quality_settings': '🎨 CHẤT LƯỢNG',
                'quality': 'Chất lượng:',
                'ultra': 'Siêu cao (CRF 16)',
                'high': 'Cao (CRF 18)',
                'medium': 'Trung bình (CRF 23)',
                'low': 'Thấp (CRF 28)',
                'output_format': 'Định dạng đầu ra:',
                'use_gpu': '✅ Sử dụng GPU NVIDIA (NVENC) - Đã phát hiện GTX 1070',
                'nvenc_preset': 'Cấu hình NVENC:',
                'preset_fastest': 'p1 (Nhanh nhất)',
                'preset_fast': 'p2 (Nhanh)',
                'preset_medium': 'p3 (Trung bình)',
                'preset_slow': 'p4 (Chậm)',
                'preset_slower': 'p5 (Chậm hơn)',
                'preset_very_slow': 'p6 (Rất chậm)',
                'preset_quality': 'p7 (Chất lượng)',
                
                # Output settings
                'output_settings': '💾 CÀI ĐẶT ĐẦU RA',
                'output_folder': 'Thư mục lưu:',
                'browse': 'Duyệt',
                'file_prefix': 'Tiền tố file:',
                'prefix_placeholder': 'VD: Anime, Video, Clip...',
                
                # Buttons
                'start': '▶ BẮT ĐẦU',
                'pause': '⏸ Tạm dừng',
                'resume': '▶ Tiếp tục',
                'cancel': '✖ Hủy bỏ',
                
                # Progress
                'progress': '📊 TIẾN ĐỘ',
                'current_video': '🎬 Đang xử lý',
                'segment_progress': '✂️ Tiến độ cắt',
                'fps': 'FPS',
                'eta': 'Thời gian còn lại',
                'completed_segments': 'Đã hoàn thành',
                'total_segments': 'Tổng số đoạn',
                'estimated_completion': 'Dự kiến hoàn thành',
                'elapsed_time': 'Thời gian đã chạy',
                'remaining_time': 'Thời gian còn lại',
                'speed_info': 'Tốc độ xử lý',
                
                # Log
                'log': '📝 NHẬT KÝ',
                'started': '🚀 BẮT ĐẦU XỬ LÝ VIDEO',
                'completed_all': '✅ TẤT CẢ VIDEO ĐÃ XỬ LÝ THÀNH CÔNG!',
                'added_to_queue': 'Đã thêm vào hàng đợi',
                'total_videos_queue': 'Tổng số video trong hàng đợi',
                'queue_cleared': 'Đã xóa hàng đợi',
                'output_folder_created': 'Đã tạo thư mục đầu ra',
                'loading_ffmpeg': 'Đang tải FFmpeg...',
                'ffmpeg_ready': 'FFmpeg đã sẵn sàng',
                'detected_gpu': 'Đã phát hiện GPU',
                'using_cpu': 'Sử dụng CPU encoding',
                'processing_video': 'Đang xử lý video',
                'segment_complete': 'Đã hoàn thành đoạn',
                'segment_failed': 'Lỗi xử lý đoạn',
                'cancelled': 'Đã hủy xử lý',
                
                # Dialog messages
                'warning_title': 'Cảnh báo',
                'error_title': 'Lỗi',
                'info_title': 'Thông báo',
                'question_title': 'Xác nhận',
                'no_videos': 'Chưa có video nào. Vui lòng thêm video để xử lý.',
                'cannot_create_folder': 'Không thể tạo thư mục đầu ra',
                'complete_message': 'Xử lý video hoàn tất thành công!',
                'error_message': 'Lỗi xử lý:',
                'confirm_cancel': 'Bạn có chắc muốn hủy xử lý?',
                'yes': 'Có',
                'no': 'Không',
                
                # Status messages
                'ready_status': 'Sẵn sàng',
                'processing_status': 'Đang xử lý',
                'paused_status': 'Đã tạm dừng',
                'cancelled_status': 'Đã hủy',
                'completed_status': 'Hoàn thành',
                
                # Time units
                'seconds': 'giây',
                'minutes': 'phút',
                'hours': 'giờ',
                'day': 'ngày',
                
                # Settings
                'language': '🌐 Ngôn ngữ',
                'vietnamese': 'Tiếng Việt',
                'english': 'English',
            },
            
            'en': {
                # Window & Menu
                'app_title': 'Auto Video Splitter Pro - Optimized for Dual Xeon',
                'ready': '✅ Ready',
                'processing': '🔄 Processing...',
                'paused': '⏸ Paused',
                'cancelling': '❌ Cancelling...',
                'completed': '✅ Completed',
                'error': '❌ Error',
                
                # Top bar
                'cpu': 'CPU',
                'gpu': 'GPU',
                'ram': 'RAM',
                'threads': 'Threads',
                
                # Input section
                'input_video': '📁 INPUT VIDEO',
                'drag_drop': '🎯 Drag & drop video files or folders here',
                'add_files': '➕ Add Files',
                'add_folder': '📂 Add Folder',
                'clear_all': '🗑 Clear All',
                
                # Split settings
                'split_settings': '⚙️ SPLIT SETTINGS',
                'split_mode': 'Split Mode:',
                'by_number': 'By Number of Videos',
                'by_duration': 'By Duration',
                'num_videos': 'Number of videos:',
                'duration': 'Duration per part:',
                'minutes': ' minutes',
                
                # Speed settings
                'speed_settings': '🎬 PLAYBACK SPEED',
                'speed': 'Speed:',
                'multi_speed': 'Export multiple speeds simultaneously',
                
                # Quality settings
                'quality_settings': '🎨 QUALITY SETTINGS',
                'quality': 'Quality:',
                'ultra': 'Ultra (CRF 16)',
                'high': 'High (CRF 18)',
                'medium': 'Medium (CRF 23)',
                'low': 'Low (CRF 28)',
                'output_format': 'Output Format:',
                'use_gpu': '✅ Use NVIDIA GPU (NVENC) - GTX 1070 Detected',
                'nvenc_preset': 'NVENC Preset:',
                'preset_fastest': 'p1 (Fastest)',
                'preset_fast': 'p2 (Fast)',
                'preset_medium': 'p3 (Medium)',
                'preset_slow': 'p4 (Slow)',
                'preset_slower': 'p5 (Slower)',
                'preset_very_slow': 'p6 (Very Slow)',
                'preset_quality': 'p7 (Quality)',
                
                # Output settings
                'output_settings': '💾 OUTPUT SETTINGS',
                'output_folder': 'Output Folder:',
                'browse': 'Browse',
                'file_prefix': 'File Prefix:',
                'prefix_placeholder': 'e.g., Anime, Video, Clip...',
                
                # Buttons
                'start': '▶ START',
                'pause': '⏸ Pause',
                'resume': '▶ Resume',
                'cancel': '✖ Cancel',
                
                # Progress
                'progress': '📊 PROGRESS',
                'current_video': '🎬 Processing',
                'segment_progress': '✂️ Split Progress',
                'fps': 'FPS',
                'eta': 'ETA',
                'completed_segments': 'Completed',
                'total_segments': 'Total Segments',
                'estimated_completion': 'Est. Completion',
                'elapsed_time': 'Elapsed Time',
                'remaining_time': 'Remaining Time',
                'speed_info': 'Processing Speed',
                
                # Log
                'log': '📝 LOG',
                'started': '🚀 STARTING VIDEO PROCESSING',
                'completed_all': '✅ ALL VIDEOS PROCESSED SUCCESSFULLY!',
                'added_to_queue': 'Added to queue',
                'total_videos_queue': 'Total videos in queue',
                'queue_cleared': 'Queue cleared',
                'output_folder_created': 'Output folder created',
                'loading_ffmpeg': 'Loading FFmpeg...',
                'ffmpeg_ready': 'FFmpeg ready',
                'detected_gpu': 'GPU detected',
                'using_cpu': 'Using CPU encoding',
                'processing_video': 'Processing video',
                'segment_complete': 'Segment completed',
                'segment_failed': 'Segment failed',
                'cancelled': 'Processing cancelled',
                
                # Dialog messages
                'warning_title': 'Warning',
                'error_title': 'Error',
                'info_title': 'Information',
                'question_title': 'Confirm',
                'no_videos': 'No videos added. Please add videos to process.',
                'cannot_create_folder': 'Cannot create output folder',
                'complete_message': 'Video processing completed successfully!',
                'error_message': 'Processing error:',
                'confirm_cancel': 'Are you sure you want to cancel processing?',
                'yes': 'Yes',
                'no': 'No',
                
                # Status messages
                'ready_status': 'Ready',
                'processing_status': 'Processing',
                'paused_status': 'Paused',
                'cancelled_status': 'Cancelled',
                'completed_status': 'Completed',
                
                # Time units
                'seconds': 'seconds',
                'minutes': 'minutes',
                'hours': 'hours',
                'day': 'day',
                
                # Settings
                'language': '🌐 Language',
                'vietnamese': 'Tiếng Việt',
                'english': 'English',
            }
        }
        
    def get_string(self, key: str) -> str:
        """Lấy chuỗi theo ngôn ngữ hiện tại"""
        return self._strings.get(self._current_language, {}).get(key, key)
        
    def set_language(self, lang_code: str):
        """Đổi ngôn ngữ"""
        if lang_code in self._strings:
            self._current_language = lang_code
            self.language_changed.emit()
            
    def get_current_language(self) -> str:
        """Lấy ngôn ngữ hiện tại"""
        return self._current_language
        
    def tr(self, key: str) -> str:
        """Alias for get_string - Qt style"""
        return self.get_string(key)


# Global instance
_lang_manager = None

def get_language_manager() -> LanguageManager:
    """Lấy instance LanguageManager (Singleton)"""
    global _lang_manager
    if _lang_manager is None:
        _lang_manager = LanguageManager()
    return _lang_manager


def tr(key: str) -> str:
    """Hàm dịch nhanh"""
    return get_language_manager().get_string(key)
