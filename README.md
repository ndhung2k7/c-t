# Auto Video Splitter Pro

## Professional Video Splitting Software
### Optimized for Dual Xeon E5-2680 v4 + NVIDIA GTX 1070

## Features

- 🚀 **Ultra-Fast Processing** - Utilizes all 56 CPU threads
- 🎮 **GPU Acceleration** - NVENC encoding on GTX 1070
- 📊 **Real-time Monitoring** - CPU, GPU, RAM usage
- 💾 **Large File Support** - Handles 100GB+ 8K videos
- 🔄 **Batch Processing** - Process multiple videos simultaneously
- ⚡ **Speed Adjustment** - 0.25x to 2.0x with audio sync
- 📁 **Drag & Drop** - Intuitive file management
- 💾 **Queue Persistence** - Auto-save and resume tasks

## System Requirements

- Windows 10/11 64-bit
- Python 3.8 or higher (for development)
- 8GB RAM minimum (32GB recommended)
- NVIDIA GPU with NVENC (GTX 1070 or better)

## Installation

### Method 1: Pre-built Executable
1. Download `AutoVideoSplitterPro.exe`
2. Run the executable (first launch may download FFmpeg)

### Method 2: Build from Source
1. Install Python 3.8+
2. Run `build.bat`
3. Find executable in `dist\` folder

## Usage

1. **Add Videos**: Drag & drop or use file dialogs
2. **Configure Split**: 
   - By number of videos
   - By duration per clip
3. **Set Speed**: Choose playback speed (0.25x - 2.0x)
4. **Enable GPU**: Check "Use NVIDIA GPU" for faster encoding
5. **Start Processing**: Click "Start Processing"

## Performance Optimizations

### Dual Xeon Configuration
- Automatic detection of 28 cores / 56 threads
- Process pool with 48 parallel workers
- 90% CPU usage limit to prevent system hang
- 24GB RAM usage cap

### GTX 1070 NVENC
- h264_nvenc hardware encoding
- Preset options p1 (fastest) to p7 (quality)
- 2-3x faster than CPU encoding

## File Support

### Input Formats
MP4, MKV, MOV, AVI, FLV, WEBM, M4V

### Output Formats
MP4, MKV, MOV

## Troubleshooting

### FFmpeg Not Found
- App will auto-download FFmpeg on first run
- Or manually place ffmpeg.exe in same folder

### GPU Not Detected
- Update NVIDIA drivers
- Ensure GTX 1070 is active
- App will fallback to CPU encoding

### High RAM Usage
- Limit set to 24GB max
- Reduce parallel workers if needed

## Keyboard Shortcuts

- `Ctrl+O`: Open files
- `Ctrl+Shift+O`: Open folder
- `Ctrl+S`: Start processing
- `Ctrl+P`: Pause
- `Ctrl+R`: Resume
- `Ctrl+Q`: Quit

## License

Commercial software - All rights reserved

## Support

For issues or feature requests, please contact support.

---

**Version**: 1.0.0
**Optimized for**: Intel Xeon E5-2680 v4 Dual CPU + GTX 1070
