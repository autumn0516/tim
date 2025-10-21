"""
Flask Web Application for Short Video Generation

This application allows users to upload images, text, and audio,
then uses AI to understand the content and generate a short video.
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
import logging

from video_tool import VideoGenerator
from web_app.ai_processor import AIContentProcessor
from web_app.video_builder import VideoBuilder
from web_app.workflow_engine import WorkflowEngine

# 配置
UPLOAD_FOLDER = 'web_app/static/uploads'
OUTPUT_FOLDER = 'web_app/static/uploads/videos'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'aac'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

# 初始化Flask应用
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 确保必要的目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'images'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'audio'), exist_ok=True)

# 初始化AI处理器和视频构建器
ai_processor = AIContentProcessor()
video_builder = VideoBuilder()
workflow_engine = WorkflowEngine()


def allowed_file(filename, allowed_extensions):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/workflow')
def workflow():
    """工作流编辑器页面"""
    return render_template('workflow.html')


@app.route('/api/upload/image', methods=['POST'])
def upload_image():
    """上传图片"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400

        if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            # 生成唯一文件名
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, 'images', unique_filename)

            # 保存文件
            file.save(filepath)

            logger.info(f"Image uploaded: {unique_filename}")

            return jsonify({
                'success': True,
                'filename': unique_filename,
                'url': url_for('static', filename=f'uploads/images/{unique_filename}')
            })

        return jsonify({'error': '不支持的文件格式'}), 400

    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/audio', methods=['POST'])
def upload_audio():
    """上传音频"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400

        if file and allowed_file(file.filename, ALLOWED_AUDIO_EXTENSIONS):
            # 生成唯一文件名
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, 'audio', unique_filename)

            # 保存文件
            file.save(filepath)

            logger.info(f"Audio uploaded: {unique_filename}")

            return jsonify({
                'success': True,
                'filename': unique_filename,
                'url': url_for('static', filename=f'uploads/audio/{unique_filename}')
            })

        return jsonify({'error': '不支持的文件格式'}), 400

    except Exception as e:
        logger.error(f"Error uploading audio: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def generate_video():
    """
    生成视频的主要API端点

    接收：
    - images: 图片文件名列表
    - text: 用户输入的文本描述
    - audio: 音频文件名（可选）
    - settings: 视频设置（可选）
    """
    try:
        data = request.json
        logger.info(f"Received generation request: {data}")

        # 验证输入
        if not data.get('images') and not data.get('text'):
            return jsonify({'error': '请至少提供图片或文本内容'}), 400

        images = data.get('images', [])
        text = data.get('text', '')
        audio_filename = data.get('audio')
        settings = data.get('settings', {})

        # 使用AI处理内容
        logger.info("Processing content with AI...")
        ai_result = ai_processor.process_content(
            images=images,
            text=text,
            audio_filename=audio_filename
        )

        logger.info(f"AI processing result: {ai_result}")

        # 构建视频
        logger.info("Building video...")
        video_info = video_builder.build_video(
            images=images,
            ai_result=ai_result,
            audio_filename=audio_filename,
            settings=settings
        )

        logger.info(f"Video generated: {video_info}")

        return jsonify({
            'success': True,
            'video': video_info,
            'ai_analysis': ai_result.get('analysis', {}),
            'message': '视频生成成功！'
        })

    except Exception as e:
        logger.error(f"Error generating video: {e}", exc_info=True)
        return jsonify({'error': f'生成视频时出错: {str(e)}'}), 500


@app.route('/api/videos')
def list_videos():
    """列出所有生成的视频"""
    try:
        videos_dir = Path(OUTPUT_FOLDER)
        videos = []

        for video_file in videos_dir.glob('*.mp4'):
            stat = video_file.stat()
            videos.append({
                'filename': video_file.name,
                'url': url_for('static', filename=f'uploads/videos/{video_file.name}'),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
            })

        # 按创建时间排序
        videos.sort(key=lambda x: x['created'], reverse=True)

        return jsonify({
            'success': True,
            'videos': videos
        })

    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """删除文件"""
    try:
        # 检查文件类型并构建路径
        for subdir in ['images', 'audio', 'videos']:
            filepath = os.path.join(UPLOAD_FOLDER, subdir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Deleted file: {filepath}")
                return jsonify({'success': True, 'message': '文件已删除'})

        return jsonify({'error': '文件不存在'}), 404

    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/workflow/execute', methods=['POST'])
def execute_workflow():
    """
    执行工作流

    接收：
    - name: 工作流名称
    - nodes: 节点列表
    - connections: 连接列表
    """
    try:
        data = request.json
        logger.info(f"Executing workflow: {data.get('name', 'Unnamed')}")

        # Execute workflow
        output_file = workflow_engine.execute(data)

        return jsonify({
            'success': True,
            'video_file': output_file,
            'video_url': url_for('static', filename=f'uploads/videos/{output_file}'),
            'message': '工作流执行成功！'
        })

    except Exception as e:
        logger.error(f"Error executing workflow: {e}", exc_info=True)
        return jsonify({'error': f'执行工作流时出错: {str(e)}'}), 500


@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'version': '0.1.0',
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(413)
def request_entity_too_large(error):
    """处理文件过大错误"""
    return jsonify({'error': '文件太大，请上传小于100MB的文件'}), 413


@app.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return jsonify({'error': '资源不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': '服务器内部错误'}), 500


if __name__ == '__main__':
    # 开发模式
    app.run(debug=True, host='0.0.0.0', port=5000)
