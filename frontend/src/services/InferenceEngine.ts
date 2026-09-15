import { reactive } from 'vue';

/**
 * InferenceService provides a high-level API for RTMPose inference.
 * It manages a Web Worker to offload heavy computation from the main thread.
 */

// --- Types ---
export interface InferenceResult {
  keypoints: number[]; // Flat array [x0, y0, x1, y1, ...]
  scores: number[];
  inputSize: [number, number];
}

export interface AppStatus {
  isProcessing: boolean;
  isCapturing: boolean;
  isCameraActive: boolean;
  modelStatus: 'idle' | 'loading' | 'ready' | 'error';
  modelLoaded: boolean;
  snapshotCaptured: boolean;
}

export class InferenceService {
  private worker: Worker | null = null;
  public status = reactive<AppStatus>({
    isProcessing: false,
    isCapturing: false,
    isCameraActive: false,
    modelStatus: 'idle',
    modelLoaded: false,
    snapshotCaptured: false,
  });

  private modelInputSize: [number, number] = [192, 256];

  constructor() {
    // Initialize worker - Path is relative to the project root
    // Vite will resolve this correctly if the worker file is in src/workers
    this.worker = new Worker(
      new URL('../workers/onnx-worker.js', import.meta.url),
      { type: 'module' }
    );

    this.worker.onmessage = (e) => {
      if (!e || !e.data) return;
      const { type, payload, error } = e.data;

      if (type === 'LOADED') {
        this.status.modelStatus = 'ready';
        this.status.modelLoaded = true;
      } else if (type === 'ERROR') {
        this.status.modelStatus = 'error';
        console.error('InferenceService Worker Error:', error);
      } else if (type === 'RESULT') {
        this.status.isProcessing = false;
        // Success callback will be handled by the promise in runInference
      }
    };
  }

  async initModel() {
    this.status.modelStatus = 'loading';
    // Standardize on payload object to match INFERENCE structure
    this.worker?.postMessage({ type: 'LOAD_MODEL', payload: { path: '/onnxmodels/rtmposefullbody.onnx' } });
  }

  async runInference(imageData: Uint8ClampedArray, width: number, height: number): Promise<InferenceResult | null> {
    if (!this.worker) return null;
    this.status.isProcessing = true;

    return new Promise((resolve) => {
      const handleMessage = (e: any) => {
        if (!e || !e.data) return;
        const { type, payload, error } = e.data;

        if (type === 'RESULT') {
          this.worker?.removeEventListener('message', handleMessage);
          this.status.isProcessing = false;
          resolve(payload);
        } else if (type === 'ERROR') {
          this.worker?.removeEventListener('message', handleMessage);
          this.status.isProcessing = false;
          console.error('Inference Error:', error);
          resolve(null);
        }
      };

      this.worker.addEventListener('message', handleMessage);
      this.worker.postMessage({
        type: 'INFERENCE',
        payload: {
          imageData,
          width,
          height,
          bbox: [0, 0, width, height] // Default to full screen for now
        }
      });
    });
  }

  terminate() {
    this.worker?.terminate();
  }
}

// Export a singleton instance
export const inferenceService = new InferenceService();
