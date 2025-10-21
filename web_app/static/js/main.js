// 全局变量
let uploadedImages = [];
let uploadedAudio = null;
let currentVideoUrl = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    console.log('Initializing app...');

    // 设置拖拽上传
    setupDropzone('imageDropzone', 'imageInput', handleImageUpload);
    setupDropzone('audioDropzone', 'audioInput', handleAudioUpload);

    // 设置文件输入
    document.getElementById('imageInput').addEventListener('change', handleImageInput);
    document.getElementById('audioInput').addEventListener('change', handleAudioInput);

    // 音量滑块
    const volumeInput = document.getElementById('volumeInput');
    const volumeValue = document.getElementById('volumeValue');
    volumeInput.addEventListener('input', function() {
        volumeValue.textContent = this.value + '%';
    });

    // 加载历史视频
    loadVideoHistory();

    console.log('App initialized');
}

// 设置拖拽区域（增强移动端支持）
function setupDropzone(dropzoneId, inputId, handler) {
    const dropzone = document.getElementById(dropzoneId);
    const input = document.getElementById(inputId);

    // 点击上传
    dropzone.addEventListener('click', () => input.click());

    // 桌面端拖拽支持
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handler(files);
        }
    });

    // 移动端触摸反馈
    dropzone.addEventListener('touchstart', (e) => {
        dropzone.style.opacity = '0.8';
    }, { passive: true });

    dropzone.addEventListener('touchend', (e) => {
        dropzone.style.opacity = '1';
    }, { passive: true });
}

// 处理图片输入
function handleImageInput(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleImageUpload(files);
    }
}

// 处理图片上传
async function handleImageUpload(files) {
    for (let file of files) {
        if (!file.type.startsWith('image/')) {
            showNotification('请上传图片文件', 'error');
            continue;
        }

        try {
            // 移动端图片压缩
            const processedFile = await compressImageForMobile(file);

            const formData = new FormData();
            formData.append('file', processedFile);

            const response = await fetch('/api/upload/image', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                uploadedImages.push({
                    filename: result.filename,
                    url: result.url
                });
                updateImagePreview();
                showNotification('图片上传成功', 'success');
            } else {
                showNotification(result.error || '上传失败', 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showNotification('上传失败: ' + error.message, 'error');
        }
    }
}

// 更新图片预览
function updateImagePreview() {
    const container = document.getElementById('imagePreview');
    container.innerHTML = '';

    uploadedImages.forEach((img, index) => {
        const item = document.createElement('div');
        item.className = 'preview-item';
        item.innerHTML = `
            <img src="${img.url}" alt="预览">
            <button class="remove-btn" onclick="removeImage(${index})">
                <i class="fas fa-times"></i>
            </button>
        `;
        container.appendChild(item);
    });
}

// 删除图片
function removeImage(index) {
    const image = uploadedImages[index];

    // 从服务器删除
    fetch(`/api/delete/${image.filename}`, {
        method: 'DELETE'
    }).catch(console.error);

    // 从列表中移除
    uploadedImages.splice(index, 1);
    updateImagePreview();
    showNotification('图片已删除', 'success');
}

// 处理音频输入
function handleAudioInput(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleAudioUpload(files);
    }
}

// 处理音频上传
async function handleAudioUpload(files) {
    const file = files[0];

    if (!file.type.startsWith('audio/')) {
        showNotification('请上传音频文件', 'error');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload/audio', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            uploadedAudio = {
                filename: result.filename,
                url: result.url,
                name: file.name
            };
            updateAudioPreview();
            showNotification('音频上传成功', 'success');
        } else {
            showNotification(result.error || '上传失败', 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showNotification('上传失败: ' + error.message, 'error');
    }
}

// 更新音频预览
function updateAudioPreview() {
    const container = document.getElementById('audioPreview');

    if (uploadedAudio) {
        container.innerHTML = `
            <div class="audio-item">
                <i class="fas fa-music"></i>
                <div class="audio-info">
                    <p class="audio-name">${uploadedAudio.name}</p>
                </div>
                <button class="btn-secondary" onclick="removeAudio()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    } else {
        container.innerHTML = '';
    }
}

// 删除音频
function removeAudio() {
    if (uploadedAudio) {
        fetch(`/api/delete/${uploadedAudio.filename}`, {
            method: 'DELETE'
        }).catch(console.error);

        uploadedAudio = null;
        updateAudioPreview();
        showNotification('音频已删除', 'success');
    }
}

// 切换设置显示
function toggleSettings() {
    const content = document.getElementById('settingsContent');
    const icon = document.querySelector('.btn-toggle i');

    if (content.style.display === 'none') {
        content.style.display = 'grid';
        icon.className = 'fas fa-chevron-up';
    } else {
        content.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
    }
}

// 生成视频
async function generateVideo() {
    const text = document.getElementById('textInput').value.trim();

    // 验证输入
    if (uploadedImages.length === 0 && !text) {
        showNotification('请至少上传一张图片或输入文本描述', 'warning');
        return;
    }

    if (uploadedImages.length === 0) {
        showNotification('请至少上传一张图片', 'warning');
        return;
    }

    // 收集设置
    const settings = {
        duration_per_image: parseFloat(document.getElementById('durationInput').value),
        transition: document.getElementById('transitionSelect').value,
        resolution: document.getElementById('resolutionSelect').value.split('x').map(Number),
        audio_volume: parseInt(document.getElementById('volumeInput').value) / 100
    };

    // 准备数据
    const data = {
        images: uploadedImages.map(img => img.filename),
        text: text,
        audio: uploadedAudio ? uploadedAudio.filename : null,
        settings: settings
    };

    console.log('Generating video with data:', data);

    // 显示进度
    showProgress('AI正在分析内容...');

    // 禁用生成按钮
    const generateBtn = document.getElementById('generateBtn');
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<div class="spinner"></div><span>生成中...</span>';

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            console.log('Video generated:', result);

            // 显示AI分析
            if (result.ai_analysis) {
                showAIAnalysis(result.ai_analysis);
            }

            // 更新进度
            updateProgress(100, '视频生成完成！');

            // 延迟显示结果
            setTimeout(() => {
                showVideoResult(result.video);
                hideProgress();
            }, 1000);

            showNotification('视频生成成功！', 'success');

            // 刷新历史
            loadVideoHistory();
        } else {
            hideProgress();
            showNotification(result.error || '生成失败', 'error');
        }
    } catch (error) {
        console.error('Generation error:', error);
        hideProgress();
        showNotification('生成失败: ' + error.message, 'error');
    } finally {
        // 恢复生成按钮
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-magic"></i><span>AI生成视频</span>';
    }
}

// 显示进度
function showProgress(message) {
    const section = document.getElementById('progressSection');
    const text = document.getElementById('progressText');
    const fill = document.getElementById('progressFill');

    section.style.display = 'block';
    text.textContent = message;
    fill.style.width = '0%';

    // 模拟进度
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 90) {
            progress = 90;
            clearInterval(interval);
        }
        fill.style.width = progress + '%';
    }, 500);
}

// 更新进度
function updateProgress(percent, message) {
    const text = document.getElementById('progressText');
    const fill = document.getElementById('progressFill');

    fill.style.width = percent + '%';
    text.textContent = message;
}

// 隐藏进度
function hideProgress() {
    const section = document.getElementById('progressSection');
    section.style.display = 'none';
}

// 显示AI分析结果
function showAIAnalysis(analysis) {
    const section = document.getElementById('analysisSection');
    const content = document.getElementById('analysisContent');

    let html = '';

    if (analysis.style) {
        html += `<div class="analysis-item"><strong>视频风格:</strong><span>${analysis.style}</span></div>`;
    }

    if (analysis.keywords) {
        html += `<div class="analysis-item"><strong>关键词:</strong><span>${analysis.keywords.join(', ')}</span></div>`;
    }

    if (analysis.num_images) {
        html += `<div class="analysis-item"><strong>图片数量:</strong><span>${analysis.num_images}</span></div>`;
    }

    if (analysis.estimated_duration) {
        html += `<div class="analysis-item"><strong>预计时长:</strong><span>${analysis.estimated_duration.toFixed(1)}秒</span></div>`;
    }

    content.innerHTML = html;
    section.style.display = 'block';
}

// 显示视频结果
function showVideoResult(video) {
    const section = document.getElementById('resultSection');
    const videoElement = document.getElementById('resultVideo');

    currentVideoUrl = video.url;
    videoElement.src = video.url;

    // 移动端自动播放控制
    if (isMobileDevice()) {
        videoElement.setAttribute('playsinline', '');
        videoElement.setAttribute('controls', '');
    }

    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 下载视频
function downloadVideo() {
    if (currentVideoUrl) {
        const a = document.createElement('a');
        a.href = currentVideoUrl;
        a.download = 'generated_video.mp4';
        a.click();
        showNotification('开始下载视频', 'success');
    }
}

// 分享视频
function shareVideo() {
    if (currentVideoUrl) {
        const url = window.location.origin + currentVideoUrl;

        if (navigator.share) {
            navigator.share({
                title: 'AI生成的短视频',
                text: '查看我用AI生成的短视频！',
                url: url
            }).catch(console.error);
        } else {
            // 复制链接
            navigator.clipboard.writeText(url).then(() => {
                showNotification('链接已复制到剪贴板', 'success');
            }).catch(() => {
                showNotification('无法复制链接', 'error');
            });
        }
    }
}

// 重置表单
function resetForm() {
    // 清空上传的文件
    uploadedImages = [];
    uploadedAudio = null;
    currentVideoUrl = null;

    // 清空输入
    document.getElementById('textInput').value = '';
    document.getElementById('imageInput').value = '';
    document.getElementById('audioInput').value = '';

    // 更新预览
    updateImagePreview();
    updateAudioPreview();

    // 隐藏结果和分析
    document.getElementById('resultSection').style.display = 'none';
    document.getElementById('analysisSection').style.display = 'none';

    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });

    showNotification('已重置，可以创建新视频', 'success');
}

// 加载视频历史
async function loadVideoHistory() {
    try {
        const response = await fetch('/api/videos');
        const result = await response.json();

        if (result.success) {
            displayVideoHistory(result.videos);
        }
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// 显示视频历史
function displayVideoHistory(videos) {
    const grid = document.getElementById('historyGrid');

    if (videos.length === 0) {
        grid.innerHTML = '<p class="empty-message">暂无历史记录</p>';
        return;
    }

    grid.innerHTML = videos.slice(0, 6).map(video => `
        <div class="history-item" onclick="playHistoryVideo('${video.url}')">
            <video src="${video.url}" preload="metadata"></video>
            <div class="history-info">
                <p><i class="fas fa-calendar"></i> ${formatDate(video.created)}</p>
                <p><i class="fas fa-file"></i> ${video.size_mb || (video.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
        </div>
    `).join('');
}

// 播放历史视频
function playHistoryVideo(url) {
    const section = document.getElementById('resultSection');
    const videoElement = document.getElementById('resultVideo');

    currentVideoUrl = url;
    videoElement.src = url;
    videoElement.play();

    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth' });
}

// 格式化日期
function formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    const now = new Date();
    const diff = now - date;

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) {
        return `${minutes}分钟前`;
    } else if (hours < 24) {
        return `${hours}小时前`;
    } else if (days < 7) {
        return `${days}天前`;
    } else {
        return date.toLocaleDateString('zh-CN');
    }
}

// 显示通知
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(notification);

    // 移动端震动反馈
    if (navigator.vibrate && type === 'error') {
        navigator.vibrate(200);
    } else if (navigator.vibrate && type === 'success') {
        navigator.vibrate(100);
    }

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 检测是否为移动设备
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           (window.innerWidth <= 768);
}

// 优化移动端滚动
function scrollToElement(element, offset = 0) {
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;

    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

// 防止移动端双击缩放
let lastTouchEnd = 0;
document.addEventListener('touchend', function(event) {
    const now = Date.now();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);

// 移动端适配：监听屏幕旋转
window.addEventListener('orientationchange', function() {
    // 屏幕旋转后重新调整布局
    setTimeout(() => {
        window.scrollTo(0, window.pageYOffset);
    }, 100);
});

// 移动端图片压缩（避免上传过大文件）
async function compressImageForMobile(file) {
    // 只在移动端且文件较大时压缩
    if (!isMobileDevice() || file.size < 2 * 1024 * 1024) {
        return file;
    }

    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;

                // 限制最大尺寸
                const maxSize = 1920;
                if (width > maxSize || height > maxSize) {
                    if (width > height) {
                        height = (height / width) * maxSize;
                        width = maxSize;
                    } else {
                        width = (width / height) * maxSize;
                        height = maxSize;
                    }
                }

                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);

                canvas.toBlob((blob) => {
                    resolve(new File([blob], file.name, {
                        type: 'image/jpeg',
                        lastModified: Date.now()
                    }));
                }, 'image/jpeg', 0.85);
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    });
}
