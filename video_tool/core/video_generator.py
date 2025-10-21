"""
视频生成器核心模块
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from moviepy.editor import (
    ImageClip,
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
)
from moviepy.video.fx import fadein, fadeout

from video_tool.utils.config import Config
from video_tool.core.image_processor import ImageProcessor
from video_tool.core.audio_handler import AudioHandler
from video_tool.core.effects import EffectsManager


logger = logging.getLogger(__name__)


class VideoGenerator:
    """
    视频生成器主类

    提供从图片、视频片段生成完整视频的功能
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化视频生成器

        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        self.config = Config(config_path)
        self.image_processor = ImageProcessor(self.config)
        self.audio_handler = AudioHandler(self.config)
        self.effects_manager = EffectsManager(self.config)

        # 确保输出目录存在
        os.makedirs(self.config.get("output.output_dir", "./output"), exist_ok=True)
        os.makedirs(self.config.get("output.temp_dir", "./temp"), exist_ok=True)

        logger.info("VideoGenerator initialized")

    def create_from_images(
        self,
        images: List[str],
        output: str,
        duration_per_image: Optional[float] = None,
        transition: str = "fade",
        transition_duration: Optional[float] = None,
        resolution: Optional[tuple] = None,
        fps: Optional[int] = None,
    ) -> str:
        """
        从图片列表创建视频

        Args:
            images: 图片文件路径列表
            output: 输出视频路径
            duration_per_image: 每张图片显示时长(秒)
            transition: 转场效果类型
            transition_duration: 转场效果持续时间
            resolution: 视频分辨率 (width, height)
            fps: 视频帧率

        Returns:
            输出视频路径
        """
        logger.info(f"Creating video from {len(images)} images")

        # 使用配置中的默认值
        if duration_per_image is None:
            duration_per_image = self.config.get("image.default_duration", 3.0)

        if transition_duration is None:
            transition_duration = self.config.get("video.transition_duration", 1.0)

        if resolution is None:
            res_config = self.config.get("video.default_resolution", {})
            resolution = (
                res_config.get("width", 1920),
                res_config.get("height", 1080)
            )

        if fps is None:
            fps = self.config.get("video.default_fps", 30)

        # 处理图片并创建视频片段
        clips = []
        for i, image_path in enumerate(images):
            logger.debug(f"Processing image {i+1}/{len(images)}: {image_path}")

            # 处理图片尺寸
            processed_image = self.image_processor.resize_to_fit(
                image_path,
                resolution[0],
                resolution[1]
            )

            # 创建图片片段
            clip = ImageClip(processed_image, duration=duration_per_image)

            # 添加转场效果
            if transition == "fade" and i > 0:
                clip = fadein(clip, transition_duration)

            if transition == "fade" and i < len(images) - 1:
                clip = fadeout(clip, transition_duration)

            clips.append(clip)

        # 合并所有片段
        logger.info("Concatenating video clips")
        final_clip = concatenate_videoclips(clips, method="compose")

        # 设置视频属性
        final_clip = final_clip.set_fps(fps)

        # 输出视频
        logger.info(f"Writing video to {output}")
        final_clip.write_videofile(
            output,
            fps=fps,
            codec=self.config.get("video.default_codec", "libx264"),
            audio_codec=self.config.get("audio.default_codec", "aac"),
            preset="medium",
            logger=None,  # 禁用moviepy的默认日志
        )

        # 清理
        final_clip.close()
        for clip in clips:
            clip.close()

        logger.info(f"Video created successfully: {output}")
        return output

    def add_audio(
        self,
        video_path: str,
        audio_path: str,
        output: str,
        volume: Optional[float] = None,
        fade_in: float = 0,
        fade_out: float = 0,
    ) -> str:
        """
        为视频添加音频

        Args:
            video_path: 输入视频路径
            audio_path: 音频文件路径
            output: 输出视频路径
            volume: 音频音量 (0.0-1.0)
            fade_in: 淡入时长(秒)
            fade_out: 淡出时长(秒)

        Returns:
            输出视频路径
        """
        logger.info(f"Adding audio to video: {video_path}")

        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)

        # 调整音频长度以匹配视频
        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)

        # 设置音量
        if volume is None:
            volume = self.config.get("audio.default_volume", 0.8)

        audio = audio.volumex(volume)

        # 应用淡入淡出
        audio = self.audio_handler.apply_fade(audio, fade_in, fade_out)

        # 合并音频到视频
        final_video = video.set_audio(audio)

        # 输出
        final_video.write_videofile(
            output,
            codec=self.config.get("video.default_codec", "libx264"),
            audio_codec=self.config.get("audio.default_codec", "aac"),
            logger=None,
        )

        # 清理
        final_video.close()
        video.close()
        audio.close()

        logger.info(f"Audio added successfully: {output}")
        return output

    def merge_videos(
        self,
        videos: List[str],
        output: str,
        transition: str = "fade",
        transition_duration: float = 1.0,
    ) -> str:
        """
        合并多个视频

        Args:
            videos: 视频文件路径列表
            output: 输出视频路径
            transition: 转场效果
            transition_duration: 转场时长(秒)

        Returns:
            输出视频路径
        """
        logger.info(f"Merging {len(videos)} videos")

        clips = []
        for video_path in videos:
            clip = VideoFileClip(video_path)

            # 应用转场效果
            if transition == "fade":
                clip = fadein(clip, transition_duration)
                clip = fadeout(clip, transition_duration)

            clips.append(clip)

        # 合并视频
        final_clip = concatenate_videoclips(clips, method="compose")

        # 输出
        final_clip.write_videofile(
            output,
            codec=self.config.get("video.default_codec", "libx264"),
            audio_codec=self.config.get("audio.default_codec", "aac"),
            logger=None,
        )

        # 清理
        final_clip.close()
        for clip in clips:
            clip.close()

        logger.info(f"Videos merged successfully: {output}")
        return output

    def add_subtitles(
        self,
        video_path: str,
        subtitles: List[Dict[str, Any]],
        output: str,
    ) -> str:
        """
        为视频添加字幕

        Args:
            video_path: 输入视频路径
            subtitles: 字幕列表，每项包含 {text, start, end, position}
            output: 输出视频路径

        Returns:
            输出视频路径
        """
        logger.info(f"Adding subtitles to video: {video_path}")

        from moviepy.editor import TextClip, CompositeVideoClip

        video = VideoFileClip(video_path)

        # 创建字幕片段
        text_clips = []
        for sub in subtitles:
            txt_clip = TextClip(
                sub["text"],
                fontsize=self.config.get("subtitle.font_size", 48),
                color=self.config.get("subtitle.font_color", "white"),
                font=self.config.get("subtitle.font_family", "Arial"),
                stroke_color=self.config.get("subtitle.stroke_color", "black"),
                stroke_width=self.config.get("subtitle.stroke_width", 2),
            )

            # 设置位置
            position = sub.get("position", self.config.get("subtitle.position", "bottom"))
            if position == "bottom":
                txt_clip = txt_clip.set_position(
                    ("center", video.h - self.config.get("subtitle.margin", 50))
                )
            elif position == "top":
                txt_clip = txt_clip.set_position(
                    ("center", self.config.get("subtitle.margin", 50))
                )
            else:  # center
                txt_clip = txt_clip.set_position("center")

            # 设置时间
            txt_clip = txt_clip.set_start(sub["start"]).set_end(sub["end"])
            text_clips.append(txt_clip)

        # 合成视频和字幕
        final_video = CompositeVideoClip([video] + text_clips)

        # 输出
        final_video.write_videofile(
            output,
            codec=self.config.get("video.default_codec", "libx264"),
            audio_codec=self.config.get("audio.default_codec", "aac"),
            logger=None,
        )

        # 清理
        final_video.close()
        video.close()
        for clip in text_clips:
            clip.close()

        logger.info(f"Subtitles added successfully: {output}")
        return output

    def apply_effect(
        self,
        video_path: str,
        effect: str,
        output: str,
        **effect_params
    ) -> str:
        """
        对视频应用特效

        Args:
            video_path: 输入视频路径
            effect: 特效名称
            output: 输出视频路径
            **effect_params: 特效参数

        Returns:
            输出视频路径
        """
        logger.info(f"Applying effect '{effect}' to video: {video_path}")

        video = VideoFileClip(video_path)

        # 应用特效
        video_with_effect = self.effects_manager.apply_effect(
            video,
            effect,
            **effect_params
        )

        # 输出
        video_with_effect.write_videofile(
            output,
            codec=self.config.get("video.default_codec", "libx264"),
            audio_codec=self.config.get("audio.default_codec", "aac"),
            logger=None,
        )

        # 清理
        video_with_effect.close()
        video.close()

        logger.info(f"Effect applied successfully: {output}")
        return output
