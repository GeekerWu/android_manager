<template>
    <div class="onnx-runtime-container">
        <el-card class="card-container">
            <template #header>
                <div class="header">
                    <div class="title-group">
                        <span class="title">ONNX Runtime Inference</span>
                        <span class="status-label" v-if="status.modelStatus !== 'loading'">
                            Step: <span :class="['status-text', currentStepClass]">{{ currentStepLabel }}</span>
                        </span>
                    </div>
                    <el-tag :type="status.modelStatus === 'loading' ? 'warning' : 'success'">
                        {{ status.modelStatus === 'loading' ? 'Loading Model...' : 'Ready' }}
                    </el-tag>
                </div>
            </template>

            <div class="main-content">
                <div class="layout-grid">
                    <!-- Left Side: Camera & Input -->
                    <div class="input-section">
                        <div class="video-wrapper">
                            <video ref="videoRef" autoplay playsinline muted class="video-element"></video>
                            <canvas ref="canvasRef" class="canvas-overlay"></canvas>
                        </div>

                        <div class="controls">
                            <div class="action-buttons">
                                <!-- Step 1: Load Model -->
                                <el-button v-if="!status.modelLoaded" type="primary"
                                    :loading="status.modelStatus === 'loading'" @click="handleLoadModel">
                                    Load Model
                                </el-button>

                                <!-- Step 2: Capture Image -->
                                <el-button v-else-if="!status.snapshotCaptured" type="success"
                                    :loading="status.isCapturing" @click="handleCaptureSnapshot">
                                    Capture Image
                                </el-button>

                                <!-- Step 3: Run Inference -->
                                <el-button v-else type="warning" :loading="status.isProcessing"
                                    @click="handleRunInference">
                                    Run Inference
                                </el-button>
                            </div>

                            <el-button :type="status.isCameraActive ? 'success' : 'info'" @click="handleToggleCamera">
                                {{ status.isCameraActive ? 'Turn Off Camera' : 'Turn On Camera' }}
                            </el-button>
                        </div>

                        <div class="info-text" v-if="status.snapshotCaptured && !status.isProcessing">
                            Next: Click "Run Inference" to process the captured frame.
                        </div>
                    </div>

                    <!-- Right Side: Result Preview -->
                    <div class="output-section">
                        <h3 class="section-title">Result Preview</h3>
                        <div class="result-wrapper">
                            <canvas ref="resultCanvasRef" class="result-canvas"></canvas>
                            <p v-if="!inferenceResults" class="placeholder-text">
                                {{ status.snapshotCaptured ? 'Snapshot captured. Ready to infer.' :
                                'Load model first.' }}
                            </p>
                            <div v-else-if="inferenceResults.keypoints.length === 0" class="placeholder-text">
                                No keypoints detected.
                            </div>
                            <div v-else class="stats">
                                <p>Detected Points: {{ inferenceResults.keypoints.length / 2 }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { inferenceService } from '@/services/InferenceEngine';

// --- Constants ---
const PALETTE = [[51, 153, 255], [0, 255, 0], [255, 128, 0], [255, 255, 255],
[255, 153, 255], [102, 178, 255], [255, 51, 51]];

const SKELETON = [
    [15, 13], [13, 11], [16, 14], [14, 12], [11, 12], [5, 11],
    [6, 12], [5, 6], [5, 7], [6, 8], [7, 9], [8, 10], [1, 2],
    [0, 1], [0, 2], [1, 3], [2, 4], [15, 17],
    [15, 18], [15, 19], [16, 20], [16, 21], [16, 22], [91, 92],
    [92, 93], [93, 94], [94, 95], [91, 96], [96, 97], [97, 98],
    [98, 99], [91, 100], [100, 101], [101, 102], [102, 103],
    [91, 104], [104, 105], [105, 106], [106, 107], [91, 108],
    [108, 109], [109, 110], [110, 111], [112, 113], [113, 114],
    [114, 115], [115, 116], [112, 117], [117, 118], [118, 119],
    [119, 120], [112, 121], [121, 122], [122, 123], [123, 124],
    [112, 125], [125, 126], [126, 127], [127, 128], [112, 129],
    [129, 130], [130, 131], [131, 132]
];

// --- Types ---
type ModelStatusType = 'idle' | 'loading' | 'ready' | 'error';

interface InferenceResult {
    keypoints: number[]; // Flat array [x0, y0, x1, y1, ...]
    scores: number[];
    inputSize: [number, number];
}

// --- Refs ---
const videoRef = ref<HTMLVideoElement | null>(null);
const canvasRef = ref<HTMLCanvasElement | null>(null);
const resultCanvasRef = ref<HTMLCanvasElement | null>(null);

// --- State ---
const status = inferenceService.status;
const inferenceResults = ref<InferenceResult | null>(null);

// --- Computed ---
const currentStepLabel = computed(() => {
    if (!status.modelLoaded) return 'Load Model';
    if (!status.snapshotCaptured) return 'Capture Image';
    return 'Run Inference';
});

const currentStepClass = computed(() => {
    if (!status.modelLoaded) return 'loading';
    if (!status.snapshotCaptured) return 'success';
    return 'warning';
});

// --- Methods ---
const handleLoadModel = async () => {
    await inferenceService.initModel();
};

const handleToggleCamera = async () => {
    if (status.isCameraActive) {
        // Stop Camera
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        if (videoRef.value) videoRef.value.srcObject = null;
        status.isCameraActive = false;
    } else {
        // Start Camera
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (videoRef.value) {
                videoRef.value.srcObject = stream;
                status.isCameraActive = true;
            }
        } catch (error) {
            console.error(error);
            ElMessage.error('Camera access denied.');
        }
    }
};

const handleCaptureSnapshot = async () => {
    const video = videoRef.value;
    if (!video || video.readyState !== 4) {
        ElMessage.warning('Video not ready. Please wait a moment.');
        return;
    }

    status.isCapturing = true;
    await new Promise(r => setTimeout(r, 500));

    let canvas = canvasRef.value;
    if (!canvas) {
        canvas = document.createElement('canvas');
        canvasRef.value = canvas;
        document.body.appendChild(canvas);
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        status.snapshotCaptured = true;
        ElMessage.success('Snapshot captured');
    }

    status.isCapturing = false;
};

const handleRunInference = async () => {
    if (!status.modelLoaded || !status.snapshotCaptured || !canvasRef.value) {
        ElMessage.warning('Please ensure model is loaded and snapshot is captured.');
        return;
    }

    status.isProcessing = true;
    try {
        const canvas = canvasRef.value;
        const ctx = canvas.getContext('2d');
        if (!ctx) throw new Error('Could not get canvas context');

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

        const res = await inferenceService.runInference(imageData.data, canvas.width, canvas.height);

        if (!res) {
            ElMessage.error('Invalid inference result received.');
            return;
        }

        inferenceResults.value = res;
        drawResults(res.inputSize);
        ElMessage.success('Inference complete');
    } catch (err) {
        console.error('[UI] Inference error:', err);
        ElMessage.error('Inference failed.');
    } finally {
        status.isProcessing = false;
    }
};

const drawResults = (inputSize: [number, number]) => {
    const canvas = resultCanvasRef.value;
    const ctx = canvas?.getContext('2d');
    if (!ctx || !canvas || !inferenceResults.value) {
        return;
    }

    const [modelW, modelH] = inputSize;
    if (canvas.width !== modelW || canvas.height !== modelH) {
        canvas.width = modelW;
        canvas.height = modelH;
    }

    // Draw preview image if available
    if (canvasRef.value) {
        ctx.drawImage(canvasRef.value, 0, 0, canvas.width, canvas.height);
    } else {
        ctx.fillStyle = '#f8fafc';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    const { keypoints } = inferenceResults.value;

    const scaleX = canvas.width / modelW;
    const scaleY = canvas.height / modelH;

    for (let i = 0; i < keypoints.length; i += 2) {
        const x = keypoints[i] * scaleX;
        const y = keypoints[i + 1] * scaleY;

        ctx.fillStyle = PALETTE[Math.floor((i / 2) % PALETTE.length)];
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();

        const skeletonIdx = Math.floor((i / 2) % SKELETON.length);
        const [u, v] = SKELETON[skeletonIdx];

        const uIdx = u * 2;
        const vIdx = v * 2;

        if (uIdx < keypoints.length && vIdx < keypoints.length) {
            const ux = keypoints[uIdx] * scaleX;
            const uy = keypoints[uIdx + 1] * scaleY;
            const vx = keypoints[vIdx] * scaleX;
            const vy = keypoints[vIdx + 1] * scaleY;

            ctx.strokeStyle = PALETTE[skeletonIdx % PALETTE.length];
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(ux, uy);
            ctx.lineTo(vx, vy);
            ctx.stroke();
        }
    }
};

let stream: MediaStream | null = null;

onMounted(async () => {
    await inferenceService.initModel();
});

onUnmounted(() => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
});
</script>

<style scoped>
/* Styles remain the same as before */
.onnx-runtime-container {
    padding: 20px;
    height: calc(100vh - 40px);
    overflow-y: auto;
}

.card-container {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 20px;
    border-bottom: 1px solid #e5e7eb;
}

.title-group {
    display: flex;
    align-items: center;
    gap: 20px;
}

.title {
    font-size: 1.5rem;
    font-weight: bold;
}

.status-label {
    font-size: 0.9rem;
    color: #64748b;
}

.status-text {
    font-weight: bold;
}

.status-text.ready {
    color: #10b981;
}

.status-text.loading {
    color: #f59e0b;
}

.status-text.error {
    color: #ef4444;
}

.main-content {
    flex: 1;
    padding: 20px 0;
}

.layout-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
}

.input-section,
.output-section {
    display: flex;
    flex-direction: column;
}

.video-wrapper {
    position: relative;
    background: #000;
    border-radius: 8px;
    overflow: hidden;
    aspect-ratio: 16 / 9;
    margin-bottom: 20px;
}

.video-element {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.canvas-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

.controls {
    display: flex;
    align-items: center;
    gap: 20px;
}

.action-buttons {
    display: flex;
    gap: 10px;
}

.section-title {
    margin-bottom: 15px;
    font-size: 1.2rem;
    font-weight: bold;
}

.result-wrapper {
    flex: 1;
    background: #f8fafc;
    border: 2px dashed #cbd5e1;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px;
    min-height: 300px;
}

.result-canvas {
    max-width: 100%;
    max-height: 100%;
    border: 1px solid #e2e8f0;
}

.placeholder-text {
    color: #94a382;
}

.info-text {
    margin-top: 10px;
    font-size: 0.85rem;
    color: #64748b;
}

@media (max-width: 1024px) {
    .layout-grid {
        grid-template-columns: 1fr;
    }
}
</style>