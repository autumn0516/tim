# 示例代码

这个目录包含了各种使用示例，展示如何使用短视频生成工具的不同功能。

## 示例列表

### 1. basic_video.py
基础视频生成示例，展示如何从图片列表创建简单的视频。

```bash
python examples/basic_video.py
```

**功能演示:**
- 从多张图片创建视频
- 设置每张图片的显示时长
- 添加淡入淡出转场效果

### 2. with_effects.py
带特效的视频生成示例，展示如何创建视频并添加各种视频特效。

```bash
python examples/with_effects.py
```

**功能演示:**
- 创建基础视频
- 应用复古特效
- 添加背景音乐

### 3. slideshow.py
照片幻灯片示例，创建一个专业的照片幻灯片视频。

```bash
python examples/slideshow.py
```

**功能演示:**
- 批量读取文件夹中的图片
- 创建幻灯片视频
- 添加背景音乐和淡入淡出

### 4. with_subtitles.py
字幕添加示例，展示如何为视频添加字幕。

```bash
python examples/with_subtitles.py
```

**功能演示:**
- 创建视频
- 添加多个字幕片段
- 自定义字幕位置和时间

### 5. image_filters.py
图片滤镜示例，展示如何对图片应用各种滤镜效果。

```bash
python examples/image_filters.py
```

**功能演示:**
- 黑白滤镜
- 复古色调
- 模糊和锐化
- 批量处理

## 使用说明

1. 在运行示例之前，请确保已安装所有依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 准备好示例中需要的图片和音频文件

3. 运行相应的示例脚本

4. 生成的视频将保存在 `output/` 目录中

## 自定义修改

所有示例都可以根据您的需求进行修改：

- 修改图片路径
- 调整视频参数（分辨率、帧率等）
- 更换特效类型
- 自定义转场效果
- 调整音频音量

## 更多资源

查看主项目的 README.md 获取完整的 API 文档和更多使用说明。
