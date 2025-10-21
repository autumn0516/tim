"""
视频特效模块
"""

import logging
from typing import Any

import numpy as np


logger = logging.getLogger(__name__)


class EffectsManager:
    """
    视频特效管理器

    提供各种视频特效的应用
    """

    def __init__(self, config=None):
        """
        初始化特效管理器

        Args:
            config: 配置对象
        """
        self.config = config
        logger.info("EffectsManager initialized")

    def apply_effect(
        self,
        clip,
        effect_name: str,
        **effect_params
    ):
        """
        对视频片段应用特效

        Args:
            clip: MoviePy视频片段
            effect_name: 特效名称
            **effect_params: 特效参数

        Returns:
            应用特效后的视频片段
        """
        logger.debug(f"Applying effect: {effect_name}")

        effect_method = getattr(self, f"_effect_{effect_name}", None)

        if effect_method is None:
            logger.warning(f"Unknown effect: {effect_name}")
            return clip

        return effect_method(clip, **effect_params)

    def _effect_blur(self, clip, radius: int = 5):
        """
        模糊效果

        Args:
            clip: 视频片段
            radius: 模糊半径

        Returns:
            应用模糊后的视频片段
        """
        from moviepy.video.fx import blur

        return blur(clip, kernel_size=radius)

    def _effect_grayscale(self, clip):
        """
        黑白效果

        Args:
            clip: 视频片段

        Returns:
            黑白视频片段
        """
        from moviepy.video.fx import blackwhite

        return blackwhite(clip)

    def _effect_mirror_x(self, clip):
        """
        水平镜像

        Args:
            clip: 视频片段

        Returns:
            水平镜像的视频片段
        """
        from moviepy.video.fx import mirror_x

        return mirror_x(clip)

    def _effect_mirror_y(self, clip):
        """
        垂直镜像

        Args:
            clip: 视频片段

        Returns:
            垂直镜像的视频片段
        """
        from moviepy.video.fx import mirror_y

        return mirror_y(clip)

    def _effect_rotate(self, clip, angle: float = 90):
        """
        旋转效果

        Args:
            clip: 视频片段
            angle: 旋转角度

        Returns:
            旋转后的视频片段
        """
        from moviepy.video.fx import rotate

        return rotate(clip, angle)

    def _effect_speed(self, clip, factor: float = 2.0):
        """
        速度调整

        Args:
            clip: 视频片段
            factor: 速度倍数 (>1加速, <1减速)

        Returns:
            调整速度后的视频片段
        """
        from moviepy.video.fx import speedx

        return speedx(clip, factor)

    def _effect_reverse(self, clip):
        """
        倒放效果

        Args:
            clip: 视频片段

        Returns:
            倒放的视频片段
        """
        from moviepy.video.fx import time_mirror

        return time_mirror(clip)

    def _effect_sepia(self, clip):
        """
        复古棕褐色调效果

        Args:
            clip: 视频片段

        Returns:
            应用sepia效果的视频片段
        """
        def sepia_filter(get_frame, t):
            frame = get_frame(t)

            # Sepia滤镜矩阵
            sepia_matrix = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])

            # 应用滤镜
            sepia_frame = frame @ sepia_matrix.T
            sepia_frame = np.clip(sepia_frame, 0, 255).astype(np.uint8)

            return sepia_frame

        return clip.fl(sepia_filter)

    def _effect_vintage(self, clip, intensity: float = 0.5):
        """
        复古效果（降低饱和度和对比度）

        Args:
            clip: 视频片段
            intensity: 效果强度 (0-1)

        Returns:
            应用复古效果的视频片段
        """
        def vintage_filter(get_frame, t):
            frame = get_frame(t)

            # 转换为HSV
            from skimage import color

            # 归一化到0-1
            frame_normalized = frame / 255.0

            # RGB转HSV
            hsv = color.rgb2hsv(frame_normalized)

            # 降低饱和度
            hsv[:, :, 1] = hsv[:, :, 1] * (1 - intensity * 0.3)

            # HSV转回RGB
            rgb = color.hsv2rgb(hsv)

            # 降低对比度
            mean = rgb.mean()
            rgb = mean + (rgb - mean) * (1 - intensity * 0.2)

            # 转回0-255
            result = np.clip(rgb * 255, 0, 255).astype(np.uint8)

            return result

        return clip.fl(vintage_filter)

    def _effect_vignette(self, clip, intensity: float = 0.5):
        """
        晕影效果（边缘变暗）

        Args:
            clip: 视频片段
            intensity: 效果强度 (0-1)

        Returns:
            应用晕影效果的视频片段
        """
        def vignette_filter(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]

            # 创建径向渐变遮罩
            Y, X = np.ogrid[:h, :w]
            center_y, center_x = h / 2, w / 2

            # 计算到中心的距离
            distance = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
            max_distance = np.sqrt(center_x ** 2 + center_y ** 2)

            # 归一化距离
            distance_normalized = distance / max_distance

            # 创建遮罩
            mask = 1 - (distance_normalized ** 2) * intensity
            mask = np.clip(mask, 0, 1)

            # 应用遮罩
            result = frame * mask[:, :, np.newaxis]
            result = np.clip(result, 0, 255).astype(np.uint8)

            return result

        return clip.fl(vignette_filter)

    def _effect_brightness(self, clip, factor: float = 1.5):
        """
        亮度调整

        Args:
            clip: 视频片段
            factor: 亮度倍数 (>1变亮, <1变暗)

        Returns:
            调整亮度后的视频片段
        """
        def brightness_filter(get_frame, t):
            frame = get_frame(t)
            result = frame * factor
            return np.clip(result, 0, 255).astype(np.uint8)

        return clip.fl(brightness_filter)

    def _effect_contrast(self, clip, factor: float = 1.5):
        """
        对比度调整

        Args:
            clip: 视频片段
            factor: 对比度倍数

        Returns:
            调整对比度后的视频片段
        """
        def contrast_filter(get_frame, t):
            frame = get_frame(t)
            mean = frame.mean()
            result = mean + (frame - mean) * factor
            return np.clip(result, 0, 255).astype(np.uint8)

        return clip.fl(contrast_filter)

    def _effect_sharpen(self, clip):
        """
        锐化效果

        Args:
            clip: 视频片段

        Returns:
            锐化后的视频片段
        """
        def sharpen_filter(get_frame, t):
            from scipy.ndimage import convolve

            frame = get_frame(t)

            # 锐化卷积核
            kernel = np.array([
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0]
            ])

            # 对每个颜色通道应用锐化
            result = np.zeros_like(frame)
            for i in range(3):
                result[:, :, i] = convolve(frame[:, :, i], kernel, mode='reflect')

            return np.clip(result, 0, 255).astype(np.uint8)

        return clip.fl(sharpen_filter)

    def get_available_effects(self):
        """
        获取所有可用的特效列表

        Returns:
            特效名称列表
        """
        effects = []
        for attr in dir(self):
            if attr.startswith("_effect_"):
                effects.append(attr.replace("_effect_", ""))

        return sorted(effects)
