<template>
  <div class="camera-container">
    <el-card class="camera-card">
      <template #header>
        <h2 class="title">摄像头页面</h2>
      </template>

      <div class="camera-controls">
        <div class="button-group">
          <el-button
            type="primary"
            :disabled="isStreaming"
            @click="startCamera"
            class="action-btn"
          >
            {{ isStreaming ? '停止摄像头' : '启动摄像头' }}
          </el-button>
          <el-button
            type="danger"
            :disabled="!isStreaming"
            @click="stopCamera"
            class="action-btn"
          >
            停止
          </el-button>
        </div>
        <p class="status-text">状态: {{ statusMessage }}</p>
      </div>

      <div class="video-wrapper">
        <video ref="videoRef" autoplay playsinline class="video-feed"></video>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const videoRef = ref(null);
const isStreaming = ref(false);
const statusMessage = ref('准备就绪');
let currentStream = null;

const startCamera = async () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    statusMessage.value = '错误：当前浏览器不支持摄像头功能（可能是因为非 HTTPS 环境）。';
    return;
  }

  try {
    const constraints = {
      video: {
        facingMode: "user"
      }
    };

    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    currentStream = stream;

    if (videoRef.value) {
      videoRef.value.srcObject = stream;
      isStreaming.value = true;
      statusMessage.value = '正在播放...';
    }
  } catch (err) {
    console.error('Camera Error:', err);
    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      statusMessage.value = '错误：权限被拒绝。请在浏览器设置中允许访问摄像头。';
    } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      statusMessage.value = '错误：未检测到摄像头设备。';
    } else if (err.name === 'NotFoundError' && err.message.includes('getUserMedia')) {
      statusMessage.value = '错误：无法访问摄像头。请检查硬件连接。';
    } else {
      statusMessage.value = '错误: ' + (err.message || '未知错误');
    }
  }
};

const stopCamera = () => {
  if (currentStream) {
    currentStream.getTracks().forEach(track => {
      if (track.readyState === 'live') {
        track.stop();
      }
    });
    currentStream = null;
  }
  if (videoRef.value) {
    videoRef.value.srcObject = null;
  }
  isStreaming.value = false;
  statusMessage.value = '已停止';
};
</script>

<style scoped>
.camera-container {
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--bg);
}

.camera-card {
  width: 100%;
  max-width: 800px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  box-shadow: var(--shadow);
}

.title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-h);
}

.camera-controls {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.button-group {
  display: flex;
  gap: 15px;
}

.action-btn {
  height: 40px;
  padding: 0 20px;
  font-size: 1rem;
  font-weight: bold;
}

.status-text {
  font-size: 0.9rem;
  color: var(--muted);
}

.video-wrapper {
  width: 100%;
  background-color: #000;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 16 / 9;
  display: flex;
  justify-content: center;
  align-items: center;
}

.video-feed {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
