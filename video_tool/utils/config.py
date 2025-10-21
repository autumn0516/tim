"""
配置管理模块
"""

import os
import yaml
from typing import Any, Optional
import logging


logger = logging.getLogger(__name__)


class Config:
    """
    配置管理类

    加载和访问配置文件
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        if config_path is None:
            # 使用项目根目录的config.yaml
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config.yaml"
            )

        self.config_path = config_path
        self.config = self._load_config()

        logger.info(f"Configuration loaded from: {config_path}")

    def _load_config(self) -> dict:
        """
        加载配置文件

        Returns:
            配置字典
        """
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            return self._get_default_config()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config or {}
        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> dict:
        """
        获取默认配置

        Returns:
            默认配置字典
        """
        return {
            "video": {
                "default_resolution": {
                    "width": 1920,
                    "height": 1080
                },
                "default_fps": 30,
                "default_codec": "libx264",
                "quality": {
                    "high": 18,
                    "medium": 23,
                    "low": 28
                },
                "transition_duration": 1.0
            },
            "audio": {
                "default_sample_rate": 44100,
                "default_bitrate": "192k",
                "default_codec": "aac",
                "default_volume": 0.8
            },
            "image": {
                "default_duration": 3.0,
                "resize_mode": "fill",
                "background_color": [0, 0, 0]
            },
            "subtitle": {
                "font_family": "Arial",
                "font_size": 48,
                "font_color": "white",
                "position": "bottom",
                "margin": 50,
                "stroke_color": "black",
                "stroke_width": 2
            },
            "output": {
                "default_format": "mp4",
                "output_dir": "./output",
                "temp_dir": "./temp",
                "keep_temp_files": False
            },
            "logging": {
                "level": "INFO",
                "log_file": "video_tool.log",
                "console_output": True
            },
            "performance": {
                "threads": 0,
                "memory_limit": 2048,
                "use_gpu": False
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        支持点号分隔的嵌套键，如 "video.default_fps"

        Args:
            key: 配置键
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值

        Args:
            key: 配置键（支持点号分隔）
            value: 配置值
        """
        keys = key.split('.')
        config = self.config

        # 导航到最后一级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # 设置值
        config[keys[-1]] = value

    def save(self, path: Optional[str] = None) -> None:
        """
        保存配置到文件

        Args:
            path: 保存路径，如果为None则使用当前配置文件路径
        """
        if path is None:
            path = self.config_path

        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)

        logger.info(f"Configuration saved to: {path}")

    def reload(self) -> None:
        """
        重新加载配置文件
        """
        self.config = self._load_config()
        logger.info("Configuration reloaded")
