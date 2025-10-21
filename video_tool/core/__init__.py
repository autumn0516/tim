"""
Core modules for video generation
"""

from .video_generator import VideoGenerator
from .image_processor import ImageProcessor
from .audio_handler import AudioHandler
from .effects import EffectsManager

__all__ = [
    "VideoGenerator",
    "ImageProcessor",
    "AudioHandler",
    "EffectsManager",
]
