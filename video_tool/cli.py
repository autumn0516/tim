"""
命令行接口模块
"""

import click
from pathlib import Path
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
import logging

from video_tool.core.video_generator import VideoGenerator
from video_tool.core.image_processor import ImageProcessor
from video_tool.core.audio_handler import AudioHandler
from video_tool.core.effects import EffectsManager
from video_tool.utils.config import Config
from video_tool.utils.logger import setup_logger


console = Console()


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='配置文件路径')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
@click.pass_context
def cli(ctx, config, verbose):
    """
    短视频生成工具 - 命令行接口

    一个功能强大的短视频生成工具，支持从文本、图片生成视频，添加特效、字幕、音乐等功能。
    """
    # 设置日志
    log_level = "DEBUG" if verbose else "INFO"
    setup_logger(level=log_level, console_output=True)

    # 初始化配置
    ctx.ensure_object(dict)
    ctx.obj['config'] = Config(config)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.option('--images', '-i', multiple=True, required=True, help='图片文件路径')
@click.option('--output', '-o', required=True, help='输出视频路径')
@click.option('--duration', '-d', type=float, help='每张图片显示时长(秒)')
@click.option('--transition', '-t', default='fade', help='转场效果')
@click.option('--fps', type=int, help='视频帧率')
@click.option('--resolution', help='分辨率 (如 1920x1080)')
@click.pass_context
def create(ctx, images, output, duration, transition, fps, resolution):
    """
    从图片创建视频
    """
    console.print("[bold green]创建视频中...[/bold green]")

    generator = VideoGenerator(ctx.obj['config'].config_path)

    # 解析分辨率
    res = None
    if resolution:
        w, h = resolution.split('x')
        res = (int(w), int(h))

    with console.status("[bold yellow]处理图片并生成视频...", spinner="dots"):
        output_path = generator.create_from_images(
            images=list(images),
            output=output,
            duration_per_image=duration,
            transition=transition,
            fps=fps,
            resolution=res
        )

    console.print(f"[bold green]✓[/bold green] 视频已创建: {output_path}")


@cli.command()
@click.option('--video', '-v', required=True, help='视频文件路径')
@click.option('--audio', '-a', required=True, help='音频文件路径')
@click.option('--output', '-o', required=True, help='输出视频路径')
@click.option('--volume', type=float, help='音频音量 (0.0-1.0)')
@click.pass_context
def add_audio(ctx, video, audio, output, volume):
    """
    为视频添加音频
    """
    console.print("[bold green]添加音频中...[/bold green]")

    generator = VideoGenerator(ctx.obj['config'].config_path)

    with console.status("[bold yellow]处理音频并合并到视频...", spinner="dots"):
        output_path = generator.add_audio(
            video_path=video,
            audio_path=audio,
            output=output,
            volume=volume
        )

    console.print(f"[bold green]✓[/bold green] 音频已添加: {output_path}")


@cli.command()
@click.option('--videos', '-v', multiple=True, required=True, help='视频文件路径')
@click.option('--output', '-o', required=True, help='输出视频路径')
@click.option('--transition', '-t', default='fade', help='转场效果')
@click.pass_context
def merge(ctx, videos, output, transition):
    """
    合并多个视频
    """
    console.print(f"[bold green]合并 {len(videos)} 个视频...[/bold green]")

    generator = VideoGenerator(ctx.obj['config'].config_path)

    with console.status("[bold yellow]合并视频中...", spinner="dots"):
        output_path = generator.merge_videos(
            videos=list(videos),
            output=output,
            transition=transition
        )

    console.print(f"[bold green]✓[/bold green] 视频已合并: {output_path}")


@cli.command()
@click.option('--video', '-v', required=True, help='视频文件路径')
@click.option('--effect', '-e', required=True, help='特效名称')
@click.option('--output', '-o', required=True, help='输出视频路径')
@click.pass_context
def apply_effect(ctx, video, effect, output):
    """
    对视频应用特效
    """
    console.print(f"[bold green]应用特效: {effect}[/bold green]")

    generator = VideoGenerator(ctx.obj['config'].config_path)

    with console.status("[bold yellow]应用特效中...", spinner="dots"):
        output_path = generator.apply_effect(
            video_path=video,
            effect=effect,
            output=output
        )

    console.print(f"[bold green]✓[/bold green] 特效已应用: {output_path}")


@cli.command()
@click.pass_context
def list_effects(ctx):
    """
    列出所有可用的特效
    """
    config = ctx.obj['config']
    effects_manager = EffectsManager(config)

    effects = effects_manager.get_available_effects()

    table = Table(title="可用特效列表")
    table.add_column("特效名称", style="cyan")
    table.add_column("描述", style="white")

    effect_descriptions = {
        "blur": "模糊效果",
        "grayscale": "黑白效果",
        "mirror_x": "水平镜像",
        "mirror_y": "垂直镜像",
        "rotate": "旋转效果",
        "speed": "速度调整",
        "reverse": "倒放效果",
        "sepia": "复古棕褐色调",
        "vintage": "复古效果",
        "vignette": "晕影效果",
        "brightness": "亮度调整",
        "contrast": "对比度调整",
        "sharpen": "锐化效果"
    }

    for effect in effects:
        desc = effect_descriptions.get(effect, "")
        table.add_row(effect, desc)

    console.print(table)


@cli.command()
@click.option('--image', '-i', required=True, help='图片文件路径')
@click.option('--filter', '-f', required=True, help='滤镜名称')
@click.option('--output', '-o', required=True, help='输出图片路径')
@click.pass_context
def apply_filter(ctx, image, filter, output):
    """
    对图片应用滤镜
    """
    console.print(f"[bold green]应用滤镜: {filter}[/bold green]")

    config = ctx.obj['config']
    processor = ImageProcessor(config)

    output_path = processor.apply_filter(
        image_path=image,
        filter_name=filter,
        output=output
    )

    console.print(f"[bold green]✓[/bold green] 滤镜已应用: {output_path}")


@cli.command()
@click.option('--video', '-v', required=True, help='视频文件路径')
@click.option('--output', '-o', required=True, help='输出音频路径')
@click.option('--format', '-f', default='mp3', help='音频格式')
@click.pass_context
def extract_audio(ctx, video, output, format):
    """
    从视频中提取音频
    """
    console.print("[bold green]提取音频中...[/bold green]")

    config = ctx.obj['config']
    audio_handler = AudioHandler(config)

    with console.status("[bold yellow]提取音频...", spinner="dots"):
        output_path = audio_handler.extract_audio(
            video_path=video,
            output=output,
            format=format
        )

    console.print(f"[bold green]✓[/bold green] 音频已提取: {output_path}")


@cli.command()
@click.pass_context
def info(ctx):
    """
    显示配置信息
    """
    config = ctx.obj['config']

    table = Table(title="当前配置")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="white")

    table.add_row("视频分辨率", f"{config.get('video.default_resolution.width')}x{config.get('video.default_resolution.height')}")
    table.add_row("视频帧率", str(config.get('video.default_fps')))
    table.add_row("视频编码器", config.get('video.default_codec'))
    table.add_row("音频比特率", config.get('audio.default_bitrate'))
    table.add_row("输出目录", config.get('output.output_dir'))

    console.print(table)


def main():
    """
    主入口函数
    """
    cli(obj={})


if __name__ == '__main__':
    main()
