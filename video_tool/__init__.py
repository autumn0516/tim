"""
Short Video Generator Tool
一个功能强大的短视频生成工具
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from video_tool.core.video_generator import VideoGenerator
from video_tool.core.image_processor import ImageProcessor
from video_tool.core.audio_handler import AudioHandler
from video_tool.core.effects import EffectsManager

__all__ = [
    "VideoGenerator",
    "ImageProcessor",
    "AudioHandler",
    "EffectsManager",
]
