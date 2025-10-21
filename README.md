# 短视频生成工具 (Short Video Generator)

一个功能强大的短视频生成工具，支持从文本、图片生成视频，添加特效、字幕、音乐等功能。

**🌟 新增Web应用**: 现在支持通过浏览器在线生成视频，无需编程！

## 功能特性

- 📝 **文本转视频**: 从文本描述生成视频内容
- 🖼️ **图片转视频**: 将静态图片转换为动态视频
- 🎬 **视频编辑**: 剪辑、合并、添加转场效果
- 🎵 **音频集成**: 添加背景音乐和音效
- 📊 **字幕生成**: 自动生成和添加字幕
- ✨ **特效滤镜**: 多种视频特效和滤镜
- 🎨 **模板支持**: 预设模板快速生成视频
- 🌐 **Web界面**: 浏览器在线使用，拖拽上传，所见即所得
- 🤖 **AI智能**: AI自动分析内容，推荐最佳视频风格和效果

## 安装

### 前置要求

- Python 3.8+
- FFmpeg (用于视频处理)

### 安装FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
下载并安装 [FFmpeg](https://ffmpeg.org/download.html)

### 安装项目依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 方式1: Web应用（推荐）

最简单的使用方式，无需编程：

```bash
# 启动Web应用
python -m web_app.app
```

然后在浏览器中打开 `http://localhost:5000`，即可通过可视化界面：
- 拖拽上传图片
- 输入文本描述
- 上传背景音乐
- AI自动分析并生成视频

详细使用说明请查看 [Web应用文档](web_app/README.md)

### 方式2: Python API

通过编程方式使用：

#### 1. 从图片生成视频

```python
from video_tool import VideoGenerator

# 创建生成器实例
generator = VideoGenerator()

# 从图片列表生成视频
generator.create_from_images(
    images=['image1.jpg', 'image2.jpg', 'image3.jpg'],
    output='output.mp4',
    duration_per_image=3,
    transition='fade'
)
```

### 2. 添加音乐和字幕

```python
from video_tool import VideoGenerator

generator = VideoGenerator()

# 创建视频并添加音乐
generator.create_from_images(
    images=['image1.jpg', 'image2.jpg'],
    output='temp.mp4'
)

# 添加背景音乐
generator.add_audio('temp.mp4', 'background.mp3', 'output.mp4')

# 添加字幕
generator.add_subtitles('output.mp4', 'subtitles.srt', 'final.mp4')
```

### 方式3: 命令行工具

```bash
# 从图片生成视频
python -m video_tool.cli create --images img1.jpg img2.jpg --output video.mp4

# 添加音乐
python -m video_tool.cli add-audio --video video.mp4 --audio music.mp3 --output final.mp4

# 应用特效
python -m video_tool.cli apply-effect --video video.mp4 --effect blur --output effect.mp4
```

## 配置

编辑 `config.yaml` 来自定义默认设置：

```yaml
video:
  default_resolution: "1920x1080"
  default_fps: 30
  default_codec: "libx264"

audio:
  default_sample_rate: 44100
  default_bitrate: "192k"

output:
  default_format: "mp4"
  quality: "high"
```

## 项目结构

```
video_tool/
├── video_tool/           # 核心库
│   ├── core/            # 核心功能模块
│   │   ├── video_generator.py  # 视频生成器
│   │   ├── image_processor.py  # 图片处理
│   │   ├── audio_handler.py    # 音频处理
│   │   └── effects.py          # 视频特效
│   ├── utils/           # 工具函数
│   │   ├── config.py           # 配置管理
│   │   └── logger.py           # 日志系统
│   ├── cli.py           # 命令行接口
│   └── main.py          # 主入口
├── web_app/             # Web应用 ⭐ 新增
│   ├── app.py           # Flask应用
│   ├── ai_processor.py  # AI内容分析
│   ├── video_builder.py # 视频构建器
│   ├── templates/       # HTML模板
│   │   └── index.html
│   └── static/          # 静态资源
│       ├── css/         # 样式文件
│       ├── js/          # JavaScript
│       └── uploads/     # 上传文件
├── examples/            # 示例代码
├── templates/           # 视频模板
├── tests/              # 测试文件
├── config.yaml         # 配置文件
├── requirements.txt    # 依赖列表
└── README.md          # 项目文档
```

## API 文档

### VideoGenerator

主要的视频生成类。

#### 方法

- `create_from_images(images, output, **kwargs)`: 从图片列表创建视频
- `create_from_template(template, data, output)`: 使用模板创建视频
- `add_audio(video, audio, output)`: 为视频添加音频
- `add_subtitles(video, subtitles, output)`: 添加字幕
- `apply_effect(video, effect, output)`: 应用视频特效
- `merge_videos(videos, output)`: 合并多个视频

### ImageProcessor

图片处理工具类。

#### 方法

- `resize(image, width, height)`: 调整图片大小
- `add_text(image, text, position)`: 在图片上添加文字
- `apply_filter(image, filter_name)`: 应用滤镜

### AudioHandler

音频处理工具类。

#### 方法

- `extract_audio(video)`: 从视频中提取音频
- `mix_audio(audio1, audio2)`: 混合两个音频
- `adjust_volume(audio, volume)`: 调整音频音量

## 示例

查看 `examples/` 目录获取更多使用示例：

- `basic_video.py`: 基础视频生成
- `with_effects.py`: 添加特效的视频
- `slideshow.py`: 创建照片幻灯片
- `text_to_video.py`: 文本转视频

## 开发

### 运行测试

```bash
pytest tests/
```

### 贡献

欢迎提交 Pull Request 和 Issue！

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。
