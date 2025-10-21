"""
Tests for VideoGenerator
"""

import pytest
import os
from video_tool.core.video_generator import VideoGenerator


class TestVideoGenerator:
    """Test cases for VideoGenerator"""

    def test_initialization(self):
        """Test VideoGenerator initialization"""
        generator = VideoGenerator()
        assert generator is not None
        assert generator.config is not None

    def test_config_loading(self):
        """Test configuration loading"""
        generator = VideoGenerator()
        fps = generator.config.get('video.default_fps')
        assert fps == 30

    # 添加更多测试用例...
