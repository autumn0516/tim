# Web应用 - AI短视频生成工具

一个基于Web的AI短视频生成工具，用户可以通过浏览器上传图片、输入文本、添加音乐，AI会自动分析内容并生成专业的短视频。

## 功能特性

### 🎨 用户界面
- 现代化的深色主题界面
- 拖拽上传图片和音频
- 实时预览上传的内容
- 响应式设计，支持移动端

### 🤖 AI智能分析
- 自动分析图片和文本内容
- 智能推荐视频风格和特效
- 自动生成字幕建议
- 根据内容选择合适的转场效果

### 🎬 视频生成
- 从图片自动生成视频
- 支持多种转场效果
- 添加背景音乐
- 应用视频特效
- 自动添加字幕

### ⚙️ 自定义设置
- 调整每张图片显示时长
- 选择转场效果类型
- 自定义视频分辨率
- 控制音频音量

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

如果要使用AI功能，需要设置API密钥：

```bash
# OpenAI API (用于内容分析)
export OPENAI_API_KEY="your-api-key-here"

# 或者使用Claude API
export ANTHROPIC_API_KEY="your-api-key-here"
```

**注意**: 即使不设置API密钥，应用也会使用基于规则的方法进行内容分析。

### 3. 启动Web应用

```bash
python -m web_app.app
```

或者：

```bash
cd web_app
python app.py
```

### 4. 访问应用

在浏览器中打开: `http://localhost:5000`

## 使用指南

### 步骤1: 上传内容

1. **上传图片**
   - 点击或拖拽图片到上传区域
   - 支持JPG、PNG、GIF等格式
   - 可以上传多张图片
   - 图片会按上传顺序在视频中显示

2. **输入文本描述**
   - 在文本框中输入视频的描述或想要添加的字幕内容
   - AI会根据文本内容分析视频风格
   - 例如：
     - "这是我们家庭旅行的美好回忆" → 温馨风格
     - "展示公司产品的专业介绍" → 专业风格
     - "充满活力的运动时刻" → 活力风格

3. **上传背景音乐（可选）**
   - 支持MP3、WAV、M4A等格式
   - 音乐会自动调整长度以匹配视频

### 步骤2: 调整设置（可选）

点击"视频设置"展开高级选项：

- **每张图片时长**: 1-10秒，默认3秒
- **转场效果**: 淡入淡出、滑动、擦除、溶解
- **视频分辨率**:
  - 1920x1080 (Full HD横屏)
  - 1280x720 (HD横屏)
  - 720x1280 (竖屏，适合抖音、快手)
  - 1080x1080 (方形，适合Instagram)
- **音频音量**: 0-100%

### 步骤3: 生成视频

1. 点击"AI生成视频"按钮
2. AI会分析你的内容：
   - 识别图片主题
   - 理解文本含义
   - 推荐视频风格
   - 生成字幕建议
3. 系统自动生成视频
4. 生成完成后可以：
   - 在线预览
   - 下载视频
   - 分享链接

### 步骤4: 查看历史

- 所有生成的视频会保存在"历史视频"区域
- 点击历史视频可以快速预览
- 视频会显示创建时间和文件大小

## API文档

### 上传图片

```
POST /api/upload/image
Content-Type: multipart/form-data

Body: file (image file)

Response:
{
  "success": true,
  "filename": "uuid_image.jpg",
  "url": "/static/uploads/images/uuid_image.jpg"
}
```

### 上传音频

```
POST /api/upload/audio
Content-Type: multipart/form-data

Body: file (audio file)

Response:
{
  "success": true,
  "filename": "uuid_audio.mp3",
  "url": "/static/uploads/audio/uuid_audio.mp3"
}
```

### 生成视频

```
POST /api/generate
Content-Type: application/json

Body:
{
  "images": ["image1.jpg", "image2.jpg"],
  "text": "视频描述文本",
  "audio": "audio.mp3",  // 可选
  "settings": {
    "duration_per_image": 3.0,
    "transition": "fade",
    "resolution": [1920, 1080],
    "audio_volume": 0.7
  }
}

Response:
{
  "success": true,
  "video": {
    "filename": "video_uuid.mp4",
    "url": "/static/uploads/videos/video_uuid.mp4",
    "size_mb": 5.2
  },
  "ai_analysis": {
    "style": "warm",
    "keywords": ["family", "travel", "memory"],
    "num_images": 5,
    "estimated_duration": 15
  }
}
```

### 查看视频列表

```
GET /api/videos

Response:
{
  "success": true,
  "videos": [
    {
      "filename": "video_uuid.mp4",
      "url": "/static/uploads/videos/video_uuid.mp4",
      "size": 5468123,
      "created": "2025-01-15T10:30:00"
    }
  ]
}
```

### 删除文件

```
DELETE /api/delete/<filename>

Response:
{
  "success": true,
  "message": "文件已删除"
}
```

## AI处理说明

### 使用AI模型（需要API密钥）

当配置了OpenAI或其他AI服务的API密钥时，系统会：

1. **分析图片内容**: 识别图片中的场景、物体、情感
2. **理解文本含义**: 提取关键词、分析语气和主题
3. **智能推荐**:
   - 推荐合适的视频风格
   - 选择最佳转场效果
   - 建议特效类型
4. **生成字幕**: 根据文本自动分段并设置时间轴

### 不使用AI模型

即使没有API密钥，系统也会使用基于规则的方法：

1. **关键词提取**: 从文本中提取重要词汇
2. **风格匹配**: 根据关键词匹配预设风格
3. **时长计算**: 根据图片数量和文本长度计算
4. **字幕分割**: 按标点符号智能分割文本

## 项目结构

```
web_app/
├── app.py                 # Flask应用主文件
├── ai_processor.py        # AI内容处理器
├── video_builder.py       # 视频构建器
├── templates/
│   └── index.html        # 主页面模板
├── static/
│   ├── css/
│   │   └── style.css     # 样式文件
│   ├── js/
│   │   └── main.js       # 前端JavaScript
│   └── uploads/          # 上传文件目录
│       ├── images/       # 图片存储
│       ├── audio/        # 音频存储
│       └── videos/       # 生成的视频
└── README.md             # 本文档
```

## 配置选项

可以通过环境变量配置应用：

```bash
# Flask配置
export FLASK_APP=web_app.app
export FLASK_ENV=development  # 或 production
export SECRET_KEY="your-secret-key"

# 文件上传限制
export MAX_CONTENT_LENGTH=104857600  # 100MB

# AI配置
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4"  # 或 gpt-3.5-turbo
```

## 生产部署

### 使用Gunicorn

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 web_app.app:app
```

### 使用Docker

```bash
docker build -t video-tool .
docker run -p 5000:5000 -e OPENAI_API_KEY=your-key video-tool
```

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/web_app/static;
    }
}
```

## 故障排除

### 视频生成失败

1. 检查FFmpeg是否正确安装: `ffmpeg -version`
2. 确保有足够的磁盘空间
3. 查看日志文件了解详细错误

### 文件上传失败

1. 检查文件大小是否超过限制（默认100MB）
2. 确认文件格式是否支持
3. 检查uploads目录的写入权限

### AI功能不工作

1. 确认API密钥已正确设置
2. 检查API配额和余额
3. 系统会自动降级到规则模式，不影响基本功能

## 技术栈

- **后端**: Flask 3.0
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **视频处理**: MoviePy, OpenCV, Pillow
- **音频处理**: PyDub
- **AI集成**: OpenAI API (可选)
- **UI图标**: Font Awesome 6

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v0.1.0 (2025-01-15)
- 初始版本发布
- 支持图片、文本、音频上传
- AI内容分析
- 自动视频生成
- Web界面

## 联系方式

如有问题或建议，请在GitHub上提交Issue。
