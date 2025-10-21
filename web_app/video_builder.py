"""
Video Builder

Builds videos based on AI processing results
"""

import os
import uuid
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from video_tool import VideoGenerator

logger = logging.getLogger(__name__)


class VideoBuilder:
    """
    视频构建器

    根据AI分析结果和用户上传的内容构建视频
    """

    def __init__(self):
        """初始化视频构建器"""
        self.generator = VideoGenerator()
        self.upload_folder = 'web_app/static/uploads'
        self.output_folder = 'web_app/static/uploads/videos'

        # 确保输出目录存在
        os.makedirs(self.output_folder, exist_ok=True)

    def build_video(
        self,
        images: List[str],
        ai_result: Dict[str, Any],
        audio_filename: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        构建视频

        Args:
            images: 图片文件名列表
            ai_result: AI处理结果
            audio_filename: 音频文件名
            settings: 用户自定义设置

        Returns:
            视频信息
        """
        logger.info("Building video...")

        # 合并设置
        suggestions = ai_result.get('suggestions', {})
        final_settings = self._merge_settings(suggestions, settings or {})

        # 构建图片路径列表
        image_paths = [
            os.path.join(self.upload_folder, 'images', img)
            for img in images
        ]

        # 验证图片文件存在
        valid_images = [img for img in image_paths if os.path.exists(img)]
        if not valid_images:
            raise ValueError("没有有效的图片文件")

        logger.info(f"Using {len(valid_images)} images")

        # 生成唯一的输出文件名
        output_filename = f"video_{uuid.uuid4()}.mp4"
        output_path = os.path.join(self.output_folder, output_filename)

        # 创建基础视频
        logger.info("Creating base video from images...")
        base_video = self._create_base_video(
            valid_images,
            output_path,
            final_settings
        )

        # 应用特效
        if final_settings.get('effects'):
            logger.info("Applying effects...")
            base_video = self._apply_effects(
                base_video,
                final_settings['effects']
            )

        # 添加音频
        if audio_filename:
            logger.info("Adding audio...")
            audio_path = os.path.join(self.upload_folder, 'audio', audio_filename)
            if os.path.exists(audio_path):
                base_video = self._add_audio(
                    base_video,
                    audio_path,
                    final_settings
                )

        # 添加字幕
        if final_settings.get('subtitles'):
            logger.info("Adding subtitles...")
            base_video = self._add_subtitles(
                base_video,
                final_settings['subtitles']
            )

        # 获取视频信息
        video_info = self._get_video_info(output_filename)

        logger.info(f"Video built successfully: {output_filename}")

        return video_info

    def _merge_settings(
        self,
        suggestions: Dict[str, Any],
        user_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """合并AI建议和用户设置"""
        # 用户设置优先于AI建议
        merged = {
            'duration_per_image': user_settings.get('duration_per_image') or suggestions.get('duration_per_image', 3.0),
            'transition': user_settings.get('transition') or suggestions.get('transition', 'fade'),
            'effects': user_settings.get('effects') or suggestions.get('effects', []),
            'subtitles': user_settings.get('subtitles') or suggestions.get('subtitles', []),
            'resolution': user_settings.get('resolution', (1920, 1080)),
            'fps': user_settings.get('fps', 30),
            'audio_volume': user_settings.get('audio_volume', 0.7)
        }

        return merged

    def _create_base_video(
        self,
        image_paths: List[str],
        output_path: str,
        settings: Dict[str, Any]
    ) -> str:
        """创建基础视频"""
        try:
            self.generator.create_from_images(
                images=image_paths,
                output=output_path,
                duration_per_image=settings['duration_per_image'],
                transition=settings['transition'],
                resolution=settings['resolution'],
                fps=settings['fps']
            )

            return output_path

        except Exception as e:
            logger.error(f"Error creating base video: {e}")
            raise

    def _apply_effects(
        self,
        video_path: str,
        effects: List[str]
    ) -> str:
        """应用视频特效"""
        if not effects:
            return video_path

        current_video = video_path

        for i, effect in enumerate(effects):
            try:
                # 生成临时输出路径
                temp_output = video_path.replace('.mp4', f'_effect_{i}.mp4')

                self.generator.apply_effect(
                    video_path=current_video,
                    effect=effect,
                    output=temp_output
                )

                # 如果不是第一个特效，删除临时文件
                if current_video != video_path:
                    os.remove(current_video)

                current_video = temp_output

            except Exception as e:
                logger.error(f"Error applying effect {effect}: {e}")
                # 继续处理其他特效

        # 重命名最终文件
        if current_video != video_path:
            os.replace(current_video, video_path)

        return video_path

    def _add_audio(
        self,
        video_path: str,
        audio_path: str,
        settings: Dict[str, Any]
    ) -> str:
        """添加音频"""
        try:
            temp_output = video_path.replace('.mp4', '_with_audio.mp4')

            self.generator.add_audio(
                video_path=video_path,
                audio_path=audio_path,
                output=temp_output,
                volume=settings.get('audio_volume', 0.7)
            )

            # 替换原文件
            os.replace(temp_output, video_path)

            return video_path

        except Exception as e:
            logger.error(f"Error adding audio: {e}")
            raise

    def _add_subtitles(
        self,
        video_path: str,
        subtitles: List[Dict[str, Any]]
    ) -> str:
        """添加字幕"""
        if not subtitles:
            return video_path

        try:
            temp_output = video_path.replace('.mp4', '_with_subs.mp4')

            self.generator.add_subtitles(
                video_path=video_path,
                subtitles=subtitles,
                output=temp_output
            )

            # 替换原文件
            os.replace(temp_output, video_path)

            return video_path

        except Exception as e:
            logger.error(f"Error adding subtitles: {e}")
            # 字幕失败不应该导致整个流程失败
            return video_path

    def _get_video_info(self, filename: str) -> Dict[str, Any]:
        """获取视频信息"""
        filepath = os.path.join(self.output_folder, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Video file not found: {filepath}")

        stat = os.stat(filepath)

        return {
            'filename': filename,
            'url': f'/static/uploads/videos/{filename}',
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'created': stat.st_ctime
        }
