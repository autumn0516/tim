"""
AI Content Processor

Uses AI models to understand and analyze user content
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class AIContentProcessor:
    """
    AI内容处理器

    使用大模型理解用户上传的图片、文本和音频内容，
    生成视频制作建议
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化AI处理器

        Args:
            api_key: AI服务的API密钥（如OpenAI、Claude等）
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.use_ai = bool(self.api_key)

        if not self.use_ai:
            logger.warning("No AI API key provided, using rule-based processing")

    def process_content(
        self,
        images: List[str],
        text: str,
        audio_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理用户内容

        Args:
            images: 图片文件名列表
            text: 用户文本描述
            audio_filename: 音频文件名

        Returns:
            处理结果，包含视频制作建议
        """
        logger.info(f"Processing content: {len(images)} images, text length: {len(text)}")

        # 如果配置了AI API，使用AI处理
        if self.use_ai:
            return self._process_with_ai(images, text, audio_filename)
        else:
            return self._process_with_rules(images, text, audio_filename)

    def _process_with_ai(
        self,
        images: List[str],
        text: str,
        audio_filename: Optional[str]
    ) -> Dict[str, Any]:
        """
        使用AI模型处理内容

        Args:
            images: 图片列表
            text: 文本内容
            audio_filename: 音频文件

        Returns:
            AI处理结果
        """
        try:
            # 这里可以集成OpenAI、Claude或其他AI服务
            # 示例：使用OpenAI API分析内容
            import openai

            openai.api_key = self.api_key

            # 构建提示词
            prompt = self._build_ai_prompt(images, text, audio_filename)

            # 调用AI
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的短视频制作助手。根据用户提供的内容，分析并给出视频制作建议。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )

            ai_response = response.choices[0].message.content

            # 解析AI响应
            return self._parse_ai_response(ai_response, images, text, audio_filename)

        except Exception as e:
            logger.error(f"AI processing failed: {e}, falling back to rules")
            return self._process_with_rules(images, text, audio_filename)

    def _process_with_rules(
        self,
        images: List[str],
        text: str,
        audio_filename: Optional[str]
    ) -> Dict[str, Any]:
        """
        使用基于规则的方法处理内容（无AI时的备用方案）

        Args:
            images: 图片列表
            text: 文本内容
            audio_filename: 音频文件

        Returns:
            处理结果
        """
        num_images = len(images)

        # 分析文本，提取关键词
        keywords = self._extract_keywords(text)

        # 根据内容确定视频风格
        style = self._determine_style(text, keywords)

        # 确定每张图片的显示时长
        if audio_filename:
            # 如果有音频，总时长由音频决定
            duration_per_image = 4.0  # 默认4秒
        else:
            # 根据文本长度调整
            text_length = len(text)
            if text_length > 200:
                duration_per_image = 5.0
            elif text_length > 100:
                duration_per_image = 4.0
            else:
                duration_per_image = 3.0

        # 确定转场效果
        transition = self._select_transition(style)

        # 确定特效
        effects = self._select_effects(style, keywords)

        # 生成字幕建议
        subtitles = self._generate_subtitles(text, num_images, duration_per_image)

        return {
            'analysis': {
                'style': style,
                'keywords': keywords,
                'num_images': num_images,
                'has_audio': bool(audio_filename),
                'estimated_duration': num_images * duration_per_image
            },
            'suggestions': {
                'duration_per_image': duration_per_image,
                'transition': transition,
                'effects': effects,
                'subtitles': subtitles
            },
            'processing_method': 'rules'
        }

    def _build_ai_prompt(
        self,
        images: List[str],
        text: str,
        audio_filename: Optional[str]
    ) -> str:
        """构建AI提示词"""
        prompt = f"""
用户想要制作一个短视频，提供了以下内容：

图片数量: {len(images)}
文本描述: {text if text else '无'}
背景音乐: {'有' if audio_filename else '无'}

请分析这些内容并给出视频制作建议，包括：
1. 视频风格（如：温馨、活力、专业、艺术等）
2. 每张图片建议的显示时长（秒）
3. 推荐的转场效果（fade/slide/wipe等）
4. 推荐的视频特效
5. 字幕内容和显示时机

请以JSON格式返回结果。
"""
        return prompt

    def _parse_ai_response(
        self,
        ai_response: str,
        images: List[str],
        text: str,
        audio_filename: Optional[str]
    ) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            # 尝试解析JSON响应
            result = json.loads(ai_response)
            return {
                'analysis': result.get('analysis', {}),
                'suggestions': result.get('suggestions', {}),
                'processing_method': 'ai'
            }
        except json.JSONDecodeError:
            # 如果不是JSON，尝试提取关键信息
            logger.warning("AI response is not JSON, using fallback")
            return self._process_with_rules(images, text, audio_filename)

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        if not text:
            return []

        # 简单的关键词提取（可以使用更复杂的NLP方法）
        words = text.lower().split()

        # 过滤常见停用词
        stopwords = {'的', '了', '是', '在', '和', '与', '或', '等', '也', '很', '就'}
        keywords = [w for w in words if w not in stopwords and len(w) > 1]

        return keywords[:10]  # 返回前10个关键词

    def _determine_style(self, text: str, keywords: List[str]) -> str:
        """确定视频风格"""
        text_lower = text.lower()

        # 基于关键词和文本判断风格
        if any(word in text_lower for word in ['温馨', '家庭', '回忆', '怀念']):
            return 'warm'
        elif any(word in text_lower for word in ['活力', '运动', '激情', '动感']):
            return 'energetic'
        elif any(word in text_lower for word in ['专业', '商务', '正式', '企业']):
            return 'professional'
        elif any(word in text_lower for word in ['艺术', '创意', '美学', '设计']):
            return 'artistic'
        elif any(word in text_lower for word in ['复古', '怀旧', '经典', '老照片']):
            return 'vintage'
        else:
            return 'default'

    def _select_transition(self, style: str) -> str:
        """根据风格选择转场效果"""
        transition_map = {
            'warm': 'fade',
            'energetic': 'slide',
            'professional': 'fade',
            'artistic': 'dissolve',
            'vintage': 'fade',
            'default': 'fade'
        }
        return transition_map.get(style, 'fade')

    def _select_effects(self, style: str, keywords: List[str]) -> List[str]:
        """根据风格选择特效"""
        effect_map = {
            'warm': ['vignette'],
            'energetic': ['brightness'],
            'professional': [],
            'artistic': ['vintage', 'vignette'],
            'vintage': ['sepia', 'vignette'],
            'default': []
        }
        return effect_map.get(style, [])

    def _generate_subtitles(
        self,
        text: str,
        num_images: int,
        duration_per_image: float
    ) -> List[Dict[str, Any]]:
        """生成字幕建议"""
        if not text or num_images == 0:
            return []

        # 将文本分割成句子
        sentences = self._split_into_sentences(text)

        if not sentences:
            return []

        # 计算每个句子的显示时间
        total_duration = num_images * duration_per_image
        duration_per_subtitle = total_duration / len(sentences)

        subtitles = []
        current_time = 0

        for sentence in sentences:
            subtitles.append({
                'text': sentence,
                'start': current_time,
                'end': current_time + duration_per_subtitle,
                'position': 'bottom'
            })
            current_time += duration_per_subtitle

        return subtitles

    def _split_into_sentences(self, text: str) -> List[str]:
        """将文本分割成句子"""
        if not text:
            return []

        # 按标点符号分割
        import re
        sentences = re.split('[。！？\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences
