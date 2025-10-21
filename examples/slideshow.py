"""
照片幻灯片示例

创建一个带背景音乐的照片幻灯片视频
"""

import os
from pathlib import Path
from video_tool import VideoGenerator


def create_slideshow(image_folder, audio_file, output_file):
    """
    创建照片幻灯片

    Args:
        image_folder: 图片文件夹路径
        audio_file: 背景音乐文件路径
        output_file: 输出视频路径
    """
    # 获取文件夹中的所有图片
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    images = []

    for file in sorted(Path(image_folder).iterdir()):
        if file.suffix.lower() in image_extensions:
            images.append(str(file))

    print(f"找到 {len(images)} 张图片")

    if not images:
        print("错误: 未找到图片文件")
        return

    # 创建视频生成器
    generator = VideoGenerator()

    # 创建视频（不含音频）
    print("创建幻灯片视频...")
    temp_video = 'temp/slideshow_temp.mp4'

    generator.create_from_images(
        images=images,
        output=temp_video,
        duration_per_image=5,  # 每张图片5秒
        transition='fade',
        resolution=(1920, 1080),
        fps=30
    )

    # 添加背景音乐
    if os.path.exists(audio_file):
        print("添加背景音乐...")
        generator.add_audio(
            video_path=temp_video,
            audio_path=audio_file,
            output=output_file,
            volume=0.6,
            fade_in=2.0,
            fade_out=2.0
        )

        # 删除临时文件
        os.remove(temp_video)
    else:
        print(f"警告: 音频文件不存在: {audio_file}")
        os.rename(temp_video, output_file)

    print(f"✓ 幻灯片已创建: {output_file}")


def main():
    create_slideshow(
        image_folder='photos/',
        audio_file='music/relaxing.mp3',
        output_file='output/photo_slideshow.mp4'
    )


if __name__ == '__main__':
    main()
