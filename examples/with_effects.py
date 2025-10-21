"""
带特效的视频生成示例

演示如何创建视频并添加各种特效
"""

from video_tool import VideoGenerator


def main():
    generator = VideoGenerator()

    # 第一步：从图片创建基础视频
    print("步骤 1/3: 创建基础视频...")
    images = ['img1.jpg', 'img2.jpg', 'img3.jpg']

    base_video = generator.create_from_images(
        images=images,
        output='temp/base_video.mp4',
        duration_per_image=4,
    )

    # 第二步：应用特效
    print("步骤 2/3: 应用复古特效...")
    video_with_effect = generator.apply_effect(
        video_path=base_video,
        effect='vintage',
        output='temp/video_with_vintage.mp4',
        intensity=0.6
    )

    # 第三步：添加音乐
    print("步骤 3/3: 添加背景音乐...")
    final_video = generator.add_audio(
        video_path=video_with_effect,
        audio_path='music/background.mp3',
        output='output/final_video_with_effects.mp4',
        volume=0.7
    )

    print(f"✓ 完成! 视频已保存到: {final_video}")


if __name__ == '__main__':
    main()
