"""
图片处理模块
"""

import os
from typing import Tuple, Optional, List
import logging

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    图片处理工具类

    提供图片缩放、滤镜、文字添加等功能
    """

    def __init__(self, config=None):
        """
        初始化图片处理器

        Args:
            config: 配置对象
        """
        self.config = config
        logger.info("ImageProcessor initialized")

    def resize_to_fit(
        self,
        image_path: str,
        width: int,
        height: int,
        mode: str = "fill"
    ) -> str:
        """
        调整图片尺寸以适应目标分辨率

        Args:
            image_path: 图片路径
            width: 目标宽度
            height: 目标高度
            mode: 缩放模式 - fill(填充), fit(适应), stretch(拉伸)

        Returns:
            处理后的图片路径或numpy数组
        """
        logger.debug(f"Resizing image: {image_path} to {width}x{height}, mode={mode}")

        img = Image.open(image_path)

        if mode == "stretch":
            # 直接拉伸到目标尺寸
            resized = img.resize((width, height), Image.Resampling.LANCZOS)

        elif mode == "fit":
            # 保持比例，适应目标尺寸（可能有黑边）
            img.thumbnail((width, height), Image.Resampling.LANCZOS)

            # 创建黑色背景
            bg_color = tuple(self.config.get("image.background_color", [0, 0, 0]))
            background = Image.new("RGB", (width, height), bg_color)

            # 居中粘贴
            offset = ((width - img.width) // 2, (height - img.height) // 2)
            background.paste(img, offset)
            resized = background

        else:  # fill - 默认模式
            # 保持比例，裁剪以填充目标尺寸
            img_ratio = img.width / img.height
            target_ratio = width / height

            if img_ratio > target_ratio:
                # 图片更宽，按高度缩放
                new_height = height
                new_width = int(height * img_ratio)
            else:
                # 图片更高，按宽度缩放
                new_width = width
                new_height = int(width / img_ratio)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 居中裁剪
            left = (new_width - width) // 2
            top = (new_height - height) // 2
            resized = img.crop((left, top, left + width, top + height))

        # 转换为numpy数组供moviepy使用
        return np.array(resized)

    def add_text(
        self,
        image_path: str,
        text: str,
        position: Tuple[int, int] = (50, 50),
        font_size: int = 48,
        color: str = "white",
        font_path: Optional[str] = None,
        output: Optional[str] = None,
    ) -> str:
        """
        在图片上添加文字

        Args:
            image_path: 图片路径
            text: 要添加的文字
            position: 文字位置 (x, y)
            font_size: 字体大小
            color: 文字颜色
            font_path: 字体文件路径
            output: 输出路径，如果为None则覆盖原图

        Returns:
            输出图片路径
        """
        logger.debug(f"Adding text to image: {image_path}")

        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        # 加载字体
        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                # 尝试使用默认字体
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            logger.warning("Could not load font, using default")
            font = ImageFont.load_default()

        # 添加文字
        draw.text(position, text, fill=color, font=font)

        # 保存
        if output is None:
            output = image_path

        img.save(output)
        logger.debug(f"Text added, saved to: {output}")

        return output

    def apply_filter(
        self,
        image_path: str,
        filter_name: str,
        output: Optional[str] = None,
        **filter_params
    ) -> str:
        """
        对图片应用滤镜

        Args:
            image_path: 图片路径
            filter_name: 滤镜名称
            output: 输出路径
            **filter_params: 滤镜参数

        Returns:
            输出图片路径
        """
        logger.debug(f"Applying filter '{filter_name}' to image: {image_path}")

        img = Image.open(image_path)

        if filter_name == "blur":
            radius = filter_params.get("radius", 5)
            filtered = img.filter(ImageFilter.GaussianBlur(radius))

        elif filter_name == "sharpen":
            filtered = img.filter(ImageFilter.SHARPEN)

        elif filter_name == "grayscale":
            filtered = img.convert("L").convert("RGB")

        elif filter_name == "sepia":
            # 转换为sepia色调
            img_array = np.array(img)
            sepia_filter = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])
            sepia_img = img_array @ sepia_filter.T
            sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
            filtered = Image.fromarray(sepia_img)

        elif filter_name == "vintage":
            # 复古效果：降低对比度和饱和度
            enhancer = ImageEnhance.Contrast(img)
            filtered = enhancer.enhance(0.8)
            enhancer = ImageEnhance.Color(filtered)
            filtered = enhancer.enhance(0.7)

        elif filter_name == "brighten":
            factor = filter_params.get("factor", 1.5)
            enhancer = ImageEnhance.Brightness(img)
            filtered = enhancer.enhance(factor)

        else:
            logger.warning(f"Unknown filter: {filter_name}")
            filtered = img

        # 保存
        if output is None:
            base, ext = os.path.splitext(image_path)
            output = f"{base}_{filter_name}{ext}"

        filtered.save(output)
        logger.debug(f"Filter applied, saved to: {output}")

        return output

    def create_gradient(
        self,
        width: int,
        height: int,
        color1: Tuple[int, int, int] = (0, 0, 0),
        color2: Tuple[int, int, int] = (255, 255, 255),
        direction: str = "vertical",
    ) -> np.ndarray:
        """
        创建渐变图片

        Args:
            width: 图片宽度
            height: 图片高度
            color1: 起始颜色 (R, G, B)
            color2: 结束颜色 (R, G, B)
            direction: 渐变方向 - vertical, horizontal, diagonal

        Returns:
            渐变图片的numpy数组
        """
        logger.debug(f"Creating gradient: {width}x{height}, {direction}")

        img = np.zeros((height, width, 3), dtype=np.uint8)

        if direction == "horizontal":
            for x in range(width):
                ratio = x / width
                color = tuple(
                    int(color1[i] + (color2[i] - color1[i]) * ratio)
                    for i in range(3)
                )
                img[:, x] = color

        elif direction == "diagonal":
            for y in range(height):
                for x in range(width):
                    ratio = (x + y) / (width + height)
                    color = tuple(
                        int(color1[i] + (color2[i] - color1[i]) * ratio)
                        for i in range(3)
                    )
                    img[y, x] = color

        else:  # vertical
            for y in range(height):
                ratio = y / height
                color = tuple(
                    int(color1[i] + (color2[i] - color1[i]) * ratio)
                    for i in range(3)
                )
                img[y, :] = color

        return img

    def batch_process(
        self,
        image_paths: List[str],
        operation: str,
        output_dir: str,
        **operation_params
    ) -> List[str]:
        """
        批量处理图片

        Args:
            image_paths: 图片路径列表
            operation: 操作类型 (resize, filter, etc.)
            output_dir: 输出目录
            **operation_params: 操作参数

        Returns:
            处理后的图片路径列表
        """
        logger.info(f"Batch processing {len(image_paths)} images with operation: {operation}")

        os.makedirs(output_dir, exist_ok=True)

        output_paths = []
        for i, image_path in enumerate(image_paths):
            filename = os.path.basename(image_path)
            output_path = os.path.join(output_dir, filename)

            if operation == "filter":
                self.apply_filter(image_path, output=output_path, **operation_params)
            elif operation == "text":
                self.add_text(image_path, output=output_path, **operation_params)
            # 可以添加更多操作类型

            output_paths.append(output_path)
            logger.debug(f"Processed {i+1}/{len(image_paths)}: {filename}")

        logger.info(f"Batch processing complete: {len(output_paths)} images")
        return output_paths
