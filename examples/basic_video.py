"""
基础视频生成示例

演示如何从图片列表创建简单的视频
"""

from video_tool import VideoGenerator


def main():
    # 创建视频生成器实例
    generator = VideoGenerator()

    # 准备图片列表
    images = [
        'image1.jpg',
        'image2.jpg',
        'image3.jpg',
        'image4.jpg',
    ]

    # 创建视频
    print("正在生成视频...")
    output = generator.create_from_images(
        images=images,
        output='output/basic_video.mp4',
        duration_per_image=3,  # 每张图片显示3秒
        transition='fade',      # 淡入淡出转场
    )

    print(f"视频已创建: {output}")


if __name__ == '__main__':
    main()
