"""
音频处理模块
"""

import os
from typing import Optional, List
import logging

from pydub import AudioSegment
from pydub.effects import normalize


logger = logging.getLogger(__name__)


class AudioHandler:
    """
    音频处理工具类

    提供音频混合、调节、转换等功能
    """

    def __init__(self, config=None):
        """
        初始化音频处理器

        Args:
            config: 配置对象
        """
        self.config = config
        logger.info("AudioHandler initialized")

    def apply_fade(
        self,
        audio,
        fade_in: float = 0,
        fade_out: float = 0
    ):
        """
        对音频应用淡入淡出效果

        Args:
            audio: MoviePy音频对象
            fade_in: 淡入时长(秒)
            fade_out: 淡出时长(秒)

        Returns:
            处理后的音频对象
        """
        from moviepy.audio.fx import audio_fadein, audio_fadeout

        if fade_in > 0:
            audio = audio_fadein(audio, fade_in)

        if fade_out > 0:
            audio = audio_fadeout(audio, fade_out)

        return audio

    def extract_audio(
        self,
        video_path: str,
        output: Optional[str] = None,
        format: str = "mp3"
    ) -> str:
        """
        从视频中提取音频

        Args:
            video_path: 视频文件路径
            output: 输出音频路径
            format: 音频格式

        Returns:
            输出音频路径
        """
        logger.info(f"Extracting audio from video: {video_path}")

        from moviepy.editor import VideoFileClip

        video = VideoFileClip(video_path)

        if output is None:
            base = os.path.splitext(video_path)[0]
            output = f"{base}.{format}"

        video.audio.write_audiofile(output, logger=None)

        video.close()

        logger.info(f"Audio extracted: {output}")
        return output

    def mix_audio(
        self,
        audio_paths: List[str],
        output: str,
        volumes: Optional[List[float]] = None,
        overlay: bool = True
    ) -> str:
        """
        混合多个音频文件

        Args:
            audio_paths: 音频文件路径列表
            output: 输出音频路径
            volumes: 各音频的音量列表 (相对值，1.0为原音量)
            overlay: True为叠加，False为拼接

        Returns:
            输出音频路径
        """
        logger.info(f"Mixing {len(audio_paths)} audio files")

        if not audio_paths:
            raise ValueError("No audio files provided")

        if volumes is None:
            volumes = [1.0] * len(audio_paths)

        # 加载第一个音频
        mixed = AudioSegment.from_file(audio_paths[0])
        mixed = mixed + (20 * np.log10(volumes[0]))  # 调整音量

        # 混合其他音频
        for i, audio_path in enumerate(audio_paths[1:], 1):
            audio = AudioSegment.from_file(audio_path)

            # 调整音量
            if volumes[i] != 1.0:
                audio = audio + (20 * np.log10(volumes[i]))

            if overlay:
                # 叠加模式
                mixed = mixed.overlay(audio)
            else:
                # 拼接模式
                mixed = mixed + audio

        # 导出
        file_format = os.path.splitext(output)[1][1:]
        mixed.export(output, format=file_format)

        logger.info(f"Audio mixed: {output}")
        return output

    def adjust_volume(
        self,
        audio_path: str,
        output: str,
        volume: float = 1.0
    ) -> str:
        """
        调整音频音量

        Args:
            audio_path: 输入音频路径
            output: 输出音频路径
            volume: 音量倍数 (1.0为原音量)

        Returns:
            输出音频路径
        """
        logger.info(f"Adjusting audio volume: {audio_path}, volume={volume}")

        audio = AudioSegment.from_file(audio_path)

        # 调整音量 (dB)
        db_change = 20 * np.log10(volume)
        adjusted = audio + db_change

        # 导出
        file_format = os.path.splitext(output)[1][1:]
        adjusted.export(output, format=file_format)

        logger.info(f"Volume adjusted: {output}")
        return output

    def normalize_audio(
        self,
        audio_path: str,
        output: str
    ) -> str:
        """
        标准化音频音量

        Args:
            audio_path: 输入音频路径
            output: 输出音频路径

        Returns:
            输出音频路径
        """
        logger.info(f"Normalizing audio: {audio_path}")

        audio = AudioSegment.from_file(audio_path)
        normalized = normalize(audio)

        # 导出
        file_format = os.path.splitext(output)[1][1:]
        normalized.export(output, format=file_format)

        logger.info(f"Audio normalized: {output}")
        return output

    def trim_audio(
        self,
        audio_path: str,
        output: str,
        start: float = 0,
        end: Optional[float] = None
    ) -> str:
        """
        裁剪音频

        Args:
            audio_path: 输入音频路径
            output: 输出音频路径
            start: 起始时间(秒)
            end: 结束时间(秒)，None表示到结尾

        Returns:
            输出音频路径
        """
        logger.info(f"Trimming audio: {audio_path}, {start}s to {end}s")

        audio = AudioSegment.from_file(audio_path)

        # 转换为毫秒
        start_ms = int(start * 1000)
        end_ms = int(end * 1000) if end else len(audio)

        trimmed = audio[start_ms:end_ms]

        # 导出
        file_format = os.path.splitext(output)[1][1:]
        trimmed.export(output, format=file_format)

        logger.info(f"Audio trimmed: {output}")
        return output

    def convert_format(
        self,
        audio_path: str,
        output: str,
        bitrate: Optional[str] = None,
        sample_rate: Optional[int] = None
    ) -> str:
        """
        转换音频格式

        Args:
            audio_path: 输入音频路径
            output: 输出音频路径
            bitrate: 比特率 (如 "192k")
            sample_rate: 采样率 (如 44100)

        Returns:
            输出音频路径
        """
        logger.info(f"Converting audio format: {audio_path} -> {output}")

        audio = AudioSegment.from_file(audio_path)

        # 导出参数
        export_params = {
            "format": os.path.splitext(output)[1][1:]
        }

        if bitrate:
            export_params["bitrate"] = bitrate

        if sample_rate:
            audio = audio.set_frame_rate(sample_rate)

        audio.export(output, **export_params)

        logger.info(f"Audio format converted: {output}")
        return output


# 导入numpy用于音量计算
import numpy as np
