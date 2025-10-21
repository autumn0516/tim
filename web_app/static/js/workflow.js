// Workflow Editor - Canvas-based visual workflow designer

class WorkflowEditor {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');

        this.nodes = [];
        this.connections = [];
        this.selectedNode = null;
        this.selectedConnection = null;
        this.connectingFrom = null;

        // Canvas state
        this.offset = { x: 0, y: 0 };
        this.scale = 1.0;
        this.isDragging = false;
        this.dragStart = null;
        this.draggingNode = null;

        // Node ID counter
        this.nodeIdCounter = 1;

        this.init();
    }

    init() {
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());

        // Mouse events
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.onMouseUp(e));
        this.canvas.addEventListener('wheel', (e) => this.onWheel(e));

        // Touch events for mobile
        this.canvas.addEventListener('touchstart', (e) => this.onTouchStart(e));
        this.canvas.addEventListener('touchmove', (e) => this.onTouchMove(e));
        this.canvas.addEventListener('touchend', (e) => this.onTouchEnd(e));

        // Setup drag and drop from palette
        this.setupDragAndDrop();

        // Start render loop
        this.render();
    }

    resizeCanvas() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        this.render();
    }

    setupDragAndDrop() {
        const palette = document.querySelector('.node-palette');
        const nodeItems = palette.querySelectorAll('.node-item');

        nodeItems.forEach(item => {
            item.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('nodeType', item.dataset.nodeType);
            });
        });

        this.canvas.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        this.canvas.addEventListener('drop', (e) => {
            e.preventDefault();
            const nodeType = e.dataTransfer.getData('nodeType');
            if (nodeType) {
                const rect = this.canvas.getBoundingClientRect();
                const x = (e.clientX - rect.left - this.offset.x) / this.scale;
                const y = (e.clientY - rect.top - this.offset.y) / this.scale;
                this.addNode(nodeType, x, y);
            }
        });
    }

    addNode(type, x, y) {
        const node = {
            id: `node_${this.nodeIdCounter++}`,
            type: type,
            x: x,
            y: y,
            width: 180,
            height: 100,
            data: {},
            inputs: [],
            outputs: []
        };

        // Configure node based on type
        switch(type) {
            case 'image':
                node.title = '图片输入';
                node.icon = '🖼️';
                node.color = '#6366f1';
                node.outputs = ['images'];
                node.data = { images: [] };
                break;
            case 'text':
                node.title = '文本输入';
                node.icon = '📝';
                node.color = '#8b5cf6';
                node.outputs = ['text'];
                node.data = { text: '' };
                break;
            case 'audio':
                node.title = '音频输入';
                node.icon = '🎵';
                node.color = '#ec4899';
                node.outputs = ['audio'];
                node.data = { audio: null };
                break;
            case 'effect':
                node.title = '视频特效';
                node.icon = '✨';
                node.color = '#10b981';
                node.inputs = ['video'];
                node.outputs = ['effects'];
                node.data = { effect: 'vintage', params: {} };
                break;
            case 'filter':
                node.title = '图片滤镜';
                node.icon = '🎨';
                node.color = '#f59e0b';
                node.inputs = ['images'];
                node.outputs = ['images'];
                node.data = { filter: 'sepia' };
                break;
            case 'transition':
                node.title = '转场效果';
                node.icon = '🔄';
                node.color = '#06b6d4';
                node.inputs = ['video'];
                node.outputs = ['transition'];
                node.data = { transition: 'fade', duration: 1.0 };
                break;
            case 'video_generator':
                node.title = '视频生成';
                node.icon = '🎬';
                node.color = '#ef4444';
                node.inputs = ['images', 'text', 'audio', 'effects'];
                node.outputs = [];
                node.data = {
                    settings: {
                        duration_per_image: 3.0,
                        transition: 'fade',
                        resolution: [1920, 1080],
                        fps: 30,
                        audio_volume: 0.7
                    }
                };
                break;
        }

        this.nodes.push(node);
        this.updateNodeCount();
        this.render();
    }

    onMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left - this.offset.x) / this.scale;
        const y = (e.clientY - rect.top - this.offset.y) / this.scale;

        // Check if clicking on a node
        const clickedNode = this.getNodeAt(x, y);
        if (clickedNode) {
            // Check if clicking on a port
            const port = this.getPortAt(clickedNode, x, y);
            if (port) {
                this.connectingFrom = { node: clickedNode, port: port };
            } else {
                this.draggingNode = clickedNode;
                this.dragStart = { x: x - clickedNode.x, y: y - clickedNode.y };
                this.selectNode(clickedNode);
            }
        } else {
            // Deselect and start panning
            this.selectedNode = null;
            this.isDragging = true;
            this.dragStart = { x: e.clientX - this.offset.x, y: e.clientY - this.offset.y };
            updatePropertiesPanel(null);
        }
        this.render();
    }

    onMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left - this.offset.x) / this.scale;
        const y = (e.clientY - rect.top - this.offset.y) / this.scale;

        if (this.draggingNode) {
            this.draggingNode.x = x - this.dragStart.x;
            this.draggingNode.y = y - this.dragStart.y;
            this.render();
        } else if (this.isDragging) {
            this.offset.x = e.clientX - this.dragStart.x;
            this.offset.y = e.clientY - this.dragStart.y;
            this.render();
        } else if (this.connectingFrom) {
            this.render();
            // Draw temporary connection line
            const fromPort = this.getPortPosition(this.connectingFrom.node, this.connectingFrom.port, true);
            this.drawConnection(fromPort.x, fromPort.y, x, y, '#6366f1', true);
        }
    }

    onMouseUp(e) {
        if (this.connectingFrom) {
            const rect = this.canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left - this.offset.x) / this.scale;
            const y = (e.clientY - rect.top - this.offset.y) / this.scale;

            const targetNode = this.getNodeAt(x, y);
            if (targetNode && targetNode !== this.connectingFrom.node) {
                const targetPort = this.getPortAt(targetNode, x, y);
                if (targetPort && targetPort.isInput) {
                    // Create connection
                    this.addConnection(
                        this.connectingFrom.node.id,
                        this.connectingFrom.port.name,
                        targetNode.id,
                        targetPort.name
                    );
                }
            }
            this.connectingFrom = null;
        }

        this.isDragging = false;
        this.draggingNode = null;
        this.dragStart = null;
        this.render();
    }

    onWheel(e) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        this.scale = Math.max(0.1, Math.min(3, this.scale * delta));
        this.updateZoomDisplay();
        this.render();
    }

    onTouchStart(e) {
        if (e.touches.length === 1) {
            const touch = e.touches[0];
            this.onMouseDown({
                clientX: touch.clientX,
                clientY: touch.clientY
            });
        }
    }

    onTouchMove(e) {
        if (e.touches.length === 1) {
            e.preventDefault();
            const touch = e.touches[0];
            this.onMouseMove({
                clientX: touch.clientX,
                clientY: touch.clientY
            });
        }
    }

    onTouchEnd(e) {
        this.onMouseUp(e);
    }

    addConnection(sourceNodeId, sourcePort, targetNodeId, targetPort) {
        // Check if connection already exists
        const exists = this.connections.some(conn =>
            conn.source === sourceNodeId &&
            conn.sourceOutput === sourcePort &&
            conn.target === targetNodeId &&
            conn.targetInput === targetPort
        );

        if (!exists) {
            this.connections.push({
                source: sourceNodeId,
                sourceOutput: sourcePort,
                target: targetNodeId,
                targetInput: targetPort
            });
            this.render();
        }
    }

    getNodeAt(x, y) {
        for (let i = this.nodes.length - 1; i >= 0; i--) {
            const node = this.nodes[i];
            if (x >= node.x && x <= node.x + node.width &&
                y >= node.y && y <= node.y + node.height) {
                return node;
            }
        }
        return null;
    }

    getPortAt(node, x, y) {
        const portRadius = 8;

        // Check input ports
        node.inputs.forEach((input, i) => {
            const pos = this.getPortPosition(node, { name: input, isInput: true }, false);
            const dist = Math.sqrt((x - pos.x) ** 2 + (y - pos.y) ** 2);
            if (dist < portRadius) {
                return { name: input, isInput: true, index: i };
            }
        });

        // Check output ports
        node.outputs.forEach((output, i) => {
            const pos = this.getPortPosition(node, { name: output, isInput: false }, true);
            const dist = Math.sqrt((x - pos.x) ** 2 + (y - pos.y) ** 2);
            if (dist < portRadius) {
                return { name: output, isInput: false, index: i };
            }
        });

        return null;
    }

    getPortPosition(node, port, isOutput) {
        const portY = node.y + node.height / 2;
        const portX = isOutput ? node.x + node.width : node.x;
        return { x: portX, y: portY };
    }

    selectNode(node) {
        this.selectedNode = node;
        updatePropertiesPanel(node);
    }

    render() {
        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        ctx.save();
        ctx.translate(this.offset.x, this.offset.y);
        ctx.scale(this.scale, this.scale);

        // Draw connections
        this.connections.forEach(conn => {
            const sourceNode = this.nodes.find(n => n.id === conn.source);
            const targetNode = this.nodes.find(n => n.id === conn.target);

            if (sourceNode && targetNode) {
                const from = this.getPortPosition(sourceNode, { name: conn.sourceOutput }, true);
                const to = this.getPortPosition(targetNode, { name: conn.targetInput }, false);
                this.drawConnection(from.x, from.y, to.x, to.y, '#6366f1');
            }
        });

        // Draw nodes
        this.nodes.forEach(node => {
            this.drawNode(node);
        });

        ctx.restore();
    }

    drawNode(node) {
        const ctx = this.ctx;
        const isSelected = node === this.selectedNode;

        // Shadow
        ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
        ctx.shadowBlur = 10;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 4;

        // Node background
        ctx.fillStyle = isSelected ? '#334155' : '#1e293b';
        ctx.strokeStyle = isSelected ? node.color : '#475569';
        ctx.lineWidth = isSelected ? 3 : 2;
        this.roundRect(ctx, node.x, node.y, node.width, node.height, 8);
        ctx.fill();
        ctx.stroke();

        ctx.shadowColor = 'transparent';

        // Node header
        ctx.fillStyle = node.color;
        this.roundRect(ctx, node.x, node.y, node.width, 35, 8, true, false);
        ctx.fill();

        // Node icon and title
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 14px Arial';
        ctx.fillText(`${node.icon} ${node.title}`, node.x + 10, node.y + 22);

        // Input ports
        node.inputs.forEach((input, i) => {
            const portY = node.y + 50 + i * 20;
            this.drawPort(node.x, portY, '#6366f1');
            ctx.fillStyle = '#cbd5e1';
            ctx.font = '11px Arial';
            ctx.fillText(input, node.x + 15, portY + 4);
        });

        // Output ports
        node.outputs.forEach((output, i) => {
            const portY = node.y + 50 + i * 20;
            this.drawPort(node.x + node.width, portY, '#6366f1');
            ctx.fillStyle = '#cbd5e1';
            ctx.font = '11px Arial';
            ctx.textAlign = 'right';
            ctx.fillText(output, node.x + node.width - 15, portY + 4);
            ctx.textAlign = 'left';
        });
    }

    drawPort(x, y, color) {
        const ctx = this.ctx;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();
    }

    drawConnection(x1, y1, x2, y2, color, dashed = false) {
        const ctx = this.ctx;
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;

        if (dashed) {
            ctx.setLineDash([5, 5]);
        }

        ctx.beginPath();
        const midX = (x1 + x2) / 2;
        ctx.moveTo(x1, y1);
        ctx.bezierCurveTo(midX, y1, midX, y2, x2, y2);
        ctx.stroke();

        ctx.setLineDash([]);
    }

    roundRect(ctx, x, y, w, h, r, fillTop = false, fillBottom = true) {
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.lineTo(x + w - r, y);
        if (fillTop || fillBottom) ctx.arcTo(x + w, y, x + w, y + r, r);
        ctx.lineTo(x + w, y + h - r);
        if (fillBottom) ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
        ctx.lineTo(x + r, y + h);
        if (fillBottom) ctx.arcTo(x, y + h, x, y + h - r, r);
        ctx.lineTo(x, y + r);
        if (fillTop || fillBottom) ctx.arcTo(x, y, x + r, y, r);
        ctx.closePath();
    }

    updateNodeCount() {
        document.getElementById('nodeCount').textContent = `${this.nodes.length} 个节点`;
    }

    updateZoomDisplay() {
        document.getElementById('canvasZoom').textContent = `${Math.round(this.scale * 100)}%`;
    }

    getWorkflowData() {
        return {
            name: document.getElementById('workflowName').value,
            nodes: this.nodes,
            connections: this.connections
        };
    }

    loadWorkflowData(data) {
        this.nodes = data.nodes || [];
        this.connections = data.connections || [];
        if (data.name) {
            document.getElementById('workflowName').value = data.name;
        }
        this.updateNodeCount();
        this.render();
    }

    clear() {
        this.nodes = [];
        this.connections = [];
        this.selectedNode = null;
        this.nodeIdCounter = 1;
        this.updateNodeCount();
        this.render();
    }

    fitToScreen() {
        if (this.nodes.length === 0) return;

        let minX = Infinity, minY = Infinity;
        let maxX = -Infinity, maxY = -Infinity;

        this.nodes.forEach(node => {
            minX = Math.min(minX, node.x);
            minY = Math.min(minY, node.y);
            maxX = Math.max(maxX, node.x + node.width);
            maxY = Math.max(maxY, node.y + node.height);
        });

        const width = maxX - minX;
        const height = maxY - minY;
        const scaleX = this.canvas.width / (width + 100);
        const scaleY = this.canvas.height / (height + 100);

        this.scale = Math.min(scaleX, scaleY, 1.5);
        this.offset.x = (this.canvas.width - width * this.scale) / 2 - minX * this.scale;
        this.offset.y = (this.canvas.height - height * this.scale) / 2 - minY * this.scale;

        this.updateZoomDisplay();
        this.render();
    }

    deleteNode(nodeId) {
        this.nodes = this.nodes.filter(n => n.id !== nodeId);
        this.connections = this.connections.filter(c =>
            c.source !== nodeId && c.target !== nodeId
        );
        this.selectedNode = null;
        this.updateNodeCount();
        this.render();
        updatePropertiesPanel(null);
    }
}

// Global editor instance
let editor;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    editor = new WorkflowEditor('workflowCanvas');
});

// Properties panel functions
function updatePropertiesPanel(node) {
    const panel = document.getElementById('propertiesContent');

    if (!node) {
        panel.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-hand-pointer"></i>
                <p>选择一个节点查看属性</p>
            </div>
        `;
        return;
    }

    let html = `<h4>${node.icon} ${node.title}</h4>`;

    // Node type specific properties
    switch(node.type) {
        case 'image':
            html += `
                <div class="property-group">
                    <label>图片文件</label>
                    <button class="btn-secondary" onclick="uploadImagesForNode('${node.id}')">
                        <i class="fas fa-upload"></i> 上传图片
                    </button>
                    <div id="node-images-${node.id}" style="margin-top: 10px;">
                        ${node.data.images.length} 张图片已上传
                    </div>
                </div>
            `;
            break;

        case 'text':
            html += `
                <div class="property-group">
                    <label>文本内容</label>
                    <textarea id="node-text-${node.id}" onchange="updateNodeData('${node.id}', 'text', this.value)">${node.data.text}</textarea>
                </div>
            `;
            break;

        case 'audio':
            html += `
                <div class="property-group">
                    <label>音频文件</label>
                    <button class="btn-secondary" onclick="uploadAudioForNode('${node.id}')">
                        <i class="fas fa-upload"></i> 上传音频
                    </button>
                </div>
            `;
            break;

        case 'effect':
            html += `
                <div class="property-group">
                    <label>特效类型</label>
                    <select id="node-effect-${node.id}" onchange="updateNodeData('${node.id}', 'effect', this.value)">
                        <option value="vintage" ${node.data.effect === 'vintage' ? 'selected' : ''}>复古</option>
                        <option value="sepia" ${node.data.effect === 'sepia' ? 'selected' : ''}>棕褐色</option>
                        <option value="grayscale" ${node.data.effect === 'grayscale' ? 'selected' : ''}>黑白</option>
                        <option value="blur" ${node.data.effect === 'blur' ? 'selected' : ''}>模糊</option>
                        <option value="vignette" ${node.data.effect === 'vignette' ? 'selected' : ''}>晕影</option>
                    </select>
                </div>
            `;
            break;

        case 'video_generator':
            const settings = node.data.settings;
            html += `
                <div class="property-group">
                    <label>每张图片时长（秒）</label>
                    <input type="number" value="${settings.duration_per_image}" min="1" max="10" step="0.5"
                           onchange="updateNodeSetting('${node.id}', 'duration_per_image', parseFloat(this.value))">
                </div>
                <div class="property-group">
                    <label>转场效果</label>
                    <select onchange="updateNodeSetting('${node.id}', 'transition', this.value)">
                        <option value="fade" ${settings.transition === 'fade' ? 'selected' : ''}>淡入淡出</option>
                        <option value="slide" ${settings.transition === 'slide' ? 'selected' : ''}>滑动</option>
                        <option value="wipe" ${settings.transition === 'wipe' ? 'selected' : ''}>擦除</option>
                    </select>
                </div>
                <div class="property-group">
                    <label>音频音量</label>
                    <input type="range" min="0" max="100" value="${settings.audio_volume * 100}"
                           onchange="updateNodeSetting('${node.id}', 'audio_volume', this.value / 100)">
                </div>
            `;
            break;
    }

    html += `
        <div class="property-actions">
            <button class="btn-secondary" onclick="deleteSelectedNode()">
                <i class="fas fa-trash"></i> 删除节点
            </button>
        </div>
    `;

    panel.innerHTML = html;
}

function updateNodeData(nodeId, key, value) {
    const node = editor.nodes.find(n => n.id === nodeId);
    if (node) {
        node.data[key] = value;
    }
}

function updateNodeSetting(nodeId, key, value) {
    const node = editor.nodes.find(n => n.id === nodeId);
    if (node && node.data.settings) {
        node.data.settings[key] = value;
    }
}

function deleteSelectedNode() {
    if (editor.selectedNode) {
        editor.deleteNode(editor.selectedNode.id);
    }
}

// Canvas control functions
function clearCanvas() {
    if (confirm('确定要清空画布吗？所有节点和连接都将被删除。')) {
        editor.clear();
    }
}

function fitToScreen() {
    editor.fitToScreen();
}

function zoomIn() {
    editor.scale = Math.min(3, editor.scale * 1.2);
    editor.updateZoomDisplay();
    editor.render();
}

function zoomOut() {
    editor.scale = Math.max(0.1, editor.scale / 1.2);
    editor.updateZoomDisplay();
    editor.render();
}

// Workflow operations
function saveWorkflow() {
    const data = editor.getWorkflowData();
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${data.name || 'workflow'}.json`;
    a.click();
    URL.revokeObjectURL(url);

    showNotification('工作流已保存', 'success');
}

function loadWorkflow() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const data = JSON.parse(event.target.result);
                editor.loadWorkflowData(data);
                showNotification('工作流已加载', 'success');
            } catch (error) {
                showNotification('加载失败：' + error.message, 'error');
            }
        };
        reader.readAsText(file);
    };
    input.click();
}

async function executeWorkflow() {
    const workflow = editor.getWorkflowData();

    if (workflow.nodes.length === 0) {
        showNotification('工作流为空，请先添加节点', 'warning');
        return;
    }

    // Show execution modal
    document.getElementById('executionModal').style.display = 'flex';
    document.getElementById('executionProgress').style.width = '0%';
    document.getElementById('executionStatus').textContent = '准备执行工作流...';
    document.getElementById('executionLog').innerHTML = '';

    try {
        // Send to backend
        const response = await fetch('/api/workflow/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(workflow)
        });

        const result = await response.json();

        if (result.success) {
            document.getElementById('executionProgress').style.width = '100%';
            document.getElementById('executionStatus').textContent = '执行完成！';
            addLogEntry('✓ 视频生成成功: ' + result.video_url, 'success');

            setTimeout(() => {
                closeExecutionModal();
                showNotification('工作流执行成功！', 'success');
                // Show video result
                window.location.href = '/?video=' + result.video_file;
            }, 1500);
        } else {
            throw new Error(result.error || '执行失败');
        }
    } catch (error) {
        document.getElementById('executionStatus').textContent = '执行失败';
        addLogEntry('✗ 错误: ' + error.message, 'error');
        showNotification('工作流执行失败: ' + error.message, 'error');
    }
}

function addLogEntry(message, type = 'info') {
    const log = document.getElementById('executionLog');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
}

function closeExecutionModal() {
    document.getElementById('executionModal').style.display = 'none';
}

function closePropertiesPanel() {
    editor.selectedNode = null;
    editor.render();
    updatePropertiesPanel(null);
}

// File upload helpers
async function uploadImagesForNode(nodeId) {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = 'image/*';

    input.onchange = async (e) => {
        const files = e.target.files;
        const node = editor.nodes.find(n => n.id === nodeId);

        for (let file of files) {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/upload/image', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (result.success) {
                const fullPath = 'web_app/static' + result.url;
                node.data.images.push(fullPath);
            }
        }

        updatePropertiesPanel(node);
        showNotification(`已上传 ${files.length} 张图片`, 'success');
    };

    input.click();
}

async function uploadAudioForNode(nodeId) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'audio/*';

    input.onchange = async (e) => {
        const file = e.target.files[0];
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload/audio', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (result.success) {
            const node = editor.nodes.find(n => n.id === nodeId);
            const fullPath = 'web_app/static' + result.url;
            node.data.audio = fullPath;
            updatePropertiesPanel(node);
            showNotification('音频已上传', 'success');
        }
    };

    input.click();
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
