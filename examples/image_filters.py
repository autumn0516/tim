"""
图片滤镜示例

演示如何对图片应用各种滤镜
"""

from video_tool import ImageProcessor


def main():
    processor = ImageProcessor()

    input_image = 'photo.jpg'

    # 应用不同的滤镜
    filters = [
        'grayscale',
        'sepia',
        'vintage',
        'blur',
        'sharpen'
    ]

    print("应用滤镜...")
    for filter_name in filters:
        output = f'output/{filter_name}_photo.jpg'
        processor.apply_filter(
            image_path=input_image,
            filter_name=filter_name,
            output=output
        )
        print(f"✓ {filter_name}: {output}")

    print("完成!")


if __name__ == '__main__':
    main()
