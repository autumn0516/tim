"""
添加字幕示例

演示如何为视频添加字幕
"""

from video_tool import VideoGenerator


def main():
    generator = VideoGenerator()

    # 创建基础视频
    print("创建基础视频...")
    images = ['scene1.jpg', 'scene2.jpg', 'scene3.jpg']

    video = generator.create_from_images(
        images=images,
        output='temp/video_base.mp4',
        duration_per_image=4,
    )

    # 定义字幕
    subtitles = [
        {
            "text": "欢迎来到短视频生成工具",
            "start": 0,
            "end": 3.5,
            "position": "bottom"
        },
        {
            "text": "轻松创建专业视频",
            "start": 4,
            "end": 7.5,
            "position": "bottom"
        },
        {
            "text": "支持多种特效和转场",
            "start": 8,
            "end": 12,
            "position": "bottom"
        },
    ]

    # 添加字幕
    print("添加字幕...")
    final_video = generator.add_subtitles(
        video_path=video,
        subtitles=subtitles,
        output='output/video_with_subtitles.mp4'
    )

    print(f"✓ 完成! 视频已保存到: {final_video}")


if __name__ == '__main__':
    main()
