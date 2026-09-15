 // --- Types ---
  // Removed for JS worker file

  /**
   * Web Worker for handling ONNX Runtime inference.
   * Handles: Model loading, Preprocessing (Affine warp), Inference, and Postprocessing.
   */
  import * as ort from 'onnxruntime-web';

  let session = null;
  const MODEL_INPUT_SIZE = [192, 256];
  const MEAN = new Float32Array([123.675, 116.28, 103.53]);
  const STD = new Float32Array([58.395, 57.12, 57.375]);

  // --- Helper Functions ---

  /**
   * Converts bbox from [x1, y1, x2, y2] to center and scale.
   */
  function bbox_xyxy2cs(bbox, padding = 1.25) {
    if (!bbox || bbox.length < 4) return { center: [0, 0], scale: [1, 1] };
    const [x1, y1, x2, y2] = bbox;
    const center = [(x1 + x2) / 2, (y1 + y2) / 2];
    const scale = Math.min(x2 - x1, y2 - y1) * padding;
    return { center, scale };
  }

  /**
   * Calculates the affine transformation matrix.
   */
  function get_warp_matrix(center, scale, rot, output_size) {
    const [w, h] = output_size;
    const src_w = scale[0];
    const src_h = scale[1];

    const rot_rad = (rot * Math.PI) / 180;
    const sn = Math.sin(rot_rad);
    const cs = Math.cos(rot_rad);

    const src_dir = [cs * src_w * -0.5 - sn * src_h * -0.5, sn * src_w * -0.5 + cs * src_h * -0.5];   
    const dst_dir = [0, -h * 0.5];

    const src = [
      [center[0] + src_w * -0.5, center[1] + src_h * -0.5],
      [center[0] + src_dir[0] + src_w * -0.5, center[1] + src_dir[1] + src_h * -0.5]
    ];

    const dst = [
      [w * 0.5, h * 0.5],
      [w * 0.5 + dst_dir[0], h * 0.5 + dst_dir[1]]
    ];

    // Simplified for no rotation case:
    const a = w / src_w;
    const b = 0;
    const c = (w - src_w) / 2;
    const d = h / src_h;
    const e = 0;
    const f = (h - src_h) / 2;

    return [a, b, c, d, e, f];
  }

  /**
   * Preprocesses image: affine warp -> normalization
   */
  function preprocess(imgData, width, height, bbox) {
    const { center, scale } = bbox_xyxy2cs(bbox);
    const [w, h] = MODEL_INPUT_SIZE;

    const output = new Float32Array(w * h * 3);

    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const srcX = (x - w / 2) * (scale[0] / w) + (scale[0] / 2);
        const srcY = (y - h / 2) * (scale[1] / h) + (scale[1] / 2);

        const ix = Math.min(Math.max(Math.floor(srcX), 0), width - 1);
        const iy = Math.min(Math.max(Math.floor(srcY), 0), height - 1);

        const pixelIdx = (iy * width + ix) * 3;

        output[(y * w + x) * 3 + 0] = (imgData[pixelIdx] - MEAN[0]) / STD[0];
        output[(y * w + x) * 3 + 1] = (imgData[pixelIdx + 1] - MEAN[1]) / STD[1];
        output[(y * w + x) * 3 + 2] = (imgData[pixelIdx + 2] - MEAN[2]) / STD[2];
      }
    }

    return output;
  }

  /**
   * Decodes SimCC outputs to keypoints.
   */
  function decode(simcc_x, simcc_y, split_ratio) {
    const K = simcc_x.length / MODEL_INPUT_SIZE[1];
    const locs = new Float32Array(K * 2);
    const vals = new Float32Array(K);

    for (let k = 0; k < K; k++) {
      let max_x = -Infinity;
      let max_y = -Infinity;
      for (let x = 0; x < MODEL_INPUT_SIZE[0]; x++) {
        if (simcc_x[k * MODEL_INPUT_SIZE[0] + x] > max_x) max_x = simcc_x[k * MODEL_INPUT_SIZE[0] +   
  x];
      }
      for (let y = 0; y < MODEL_INPUT_SIZE[1]; y++) {
        if (simcc_y[k * MODEL_INPUT_SIZE[1] + y] > max_y) max_y = simcc_y[k * MODEL_INPUT_SIZE[1] +   
  y];
      }
      locs[k * 2] = max_x;
      locs[k * 2 + 1] = max_y;
      vals[k] = Math.max(max_x, max_y);
    }

    const keypoints = new Float32Array(K * 2);
    for (let k = 0; k < K; k++) {
      keypoints[k * 2] = locs[k * 2] / split_ratio;
      keypoints[k * 2 + 1] = locs[k * 2 + 1] / split_ratio;
    }

    return { keypoints, scores: vals };
  }

  // --- Worker Listener ---

  self.onmessage = async (e) => {
    const { type, payload } = e.data;
    console.log(`Worker received message of type: ${type}`, payload);

    if (type === 'LOAD_MODEL') {
      // Robust path extraction: check payload.path first, then fallback to e.data.path
      const path = payload?.path || e.data.path;
      if (!path || typeof path !== 'string') {
        self.postMessage({ type: 'ERROR', error: 'Missing or invalid path in LOAD_MODEL payload' });  
        return;
      }
      try {
        session = await ort.InferenceSession.create(path);
        self.postMessage({ type: 'LOADED' });
      } catch (err) {
        self.postMessage({ type: 'ERROR', error: err.message });
      }
    }

    if (type === 'INFERENCE') {
      if (!session) {
        self.postMessage({ type: 'ERROR', error: 'Session not loaded' });
        return;
      }
      if (!payload || !payload.imageData) {
        self.postMessage({ type: 'ERROR', error: 'Missing imageData in INFERENCE payload' });
        return;
      }
      try {
        const { imageData, width, height, bbox } = payload;

        const inputTensor = preprocess(imageData, width, height, bbox);

        const tensor = new ort.Tensor('float32', inputTensor, [1, 3, MODEL_INPUT_SIZE[1],
  MODEL_INPUT_SIZE[0]]);
        const inputs = { [session.inputNames[0]]: tensor };

        const outputs = await session.run(inputs);
        const outX = Object.values(outputs)[0].data;
        const outY = Object.values(outputs)[1].data;

        const { keypoints, scores } = decode(outX, outY, 2.0);

        const { center, scale } = bbox_xyxy2cs(bbox);
        const finalKeypoints = new Float32Array(keypoints.length);

        for (let i = 0; i < keypoints.length; i += 2) {
          finalKeypoints[i] = keypoints[i] / MODEL_INPUT_SIZE[0] * scale[0] + center[0] - scale[0] /  
  2;
          finalKeypoints[i+1] = keypoints[i+1] / MODEL_INPUT_SIZE[1] * scale[1] + center[1] - scale[1]
  / 2;
        }

        self.postMessage({
          type: 'RESULT',
          payload: {
            keypoints: Array.from(finalKeypoints),
            scores: Array.from(scores),
            inputSize: MODEL_INPUT_SIZE
          }
        });
      } catch (err) {
        self.postMessage({ type: 'ERROR', error: err.message });
      }
    }
  };