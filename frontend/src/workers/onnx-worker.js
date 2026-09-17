/**
 * Web Worker for handling ONNX Runtime inference.
 * Handles: Model loading, Preprocessing (Affine warp), Inference, and Postprocessing.
 */
import * as ort from 'onnxruntime-web';

let session = null;
const MODEL_INPUT_SIZE = [192, 256]; // [width, height]
const MEAN = new Float32Array([123.675, 116.28, 103.53]);
const STD = new Float32Array([58.395, 57.12, 57.375]);

// --- Helper Functions ---

/**
 * Converts bbox from [x1, y1, x2, y2] to center and scale.
 */
function bbox_xyxy2cs(bbox, padding = 1.0) {
  if (!bbox || bbox.length < 4) return { center: [0, 0], scale: [1, 1] };
  const [x1, y1, x2, y2] = bbox;
  const center = [(x1 + x2) / 2, (y1 + y2) / 2];
  const scale = [(x2 - x1) * padding, (y2 - y1) * padding];
  return { center, scale };
}

/**
 * Extend the scale to match the given aspect ratio.
 */
function _fix_aspect_ratio(bbox_scale, aspect_ratio) {
  const [w, h] = bbox_scale;
  return w > h * aspect_ratio
    ? [w, w / aspect_ratio]
    : [h * aspect_ratio, h];
}

/**
 * Rotate a point by an angle.
 */
function _rotate_point(pt, angle_rad) {
  const sn = Math.sin(angle_rad);
  const cs = Math.cos(angle_rad);
  const rot_mat = [[cs, -sn], [sn, cs]];
  return [
    rot_mat[0][0] * pt[0] + rot_mat[0][1] * pt[1],
    rot_mat[1][0] * pt[0] + rot_mat[1][1] * pt[1]
  ];
}

/**
 * To calculate the affine matrix, three pairs of points are required.
 * This function is used to get the 3rd point, given 2D points a & b.
 */
function _get_3rd_point(a, b) {
  const direction = [a[0] - b[0], a[1] - b[1]];
  return [b[0] + (-direction[1]), b[1] + direction[0]];
}

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

  const src_pts = [
    src[0],
    src[1],
    _get_3rd_point(src[0], src[1])
  ];
  const dst_pts = [
    dst[0],
    dst[1],
    _get_3rd_point(dst[0], dst[1])
  ];

  const solve = (pts1, pts2) => {
    const [p1, p2, p3] = pts1;
    const [q1, q2, q3] = pts2;
    const x1 = p1[0], y1 = p1[1], x2 = p2[0], y2 = p2[1], x3 = p3[0], y3 = p3[1];
    const u1 = q1[0], u2 = q2[0], u3 = q3[0];
    const v1 = q1[1], v2 = q2[1], v3 = q3[1];

    const det = (x1 * (y2 - y3) - x2 * (y1 - y3) + x3 * (y1 - y2));
    const a = (u1 * (y2 - y3) - u2 * (y1 - y3) + u3 * (y1 - y2)) / det;
    const b = (x1 * (u2 - u3) - x2 * (u1 - u3) + x3 * (u1 - u2)) / det;
    const c = (x1 * (y2 * u3 - y3 * u2) - x2 * (y1 * u3 - y3 * u1) + x3 * (y1 * u2 - y2 * u1)) / det;
    const d = (v1 * (y2 - y3) - v2 * (y1 - y3) + v3 * (y1 - y2)) / det;
    const e = (x1 * (v2 - v3) - x2 * (v1 - v3) + x3 * (v1 - v2)) / det;
    const f = (x1 * (y2 * v3 - y3 * v2) - x2 * (y1 * v3 - y3 * v1) + x3 * (y1 * v2 - y2 * v1)) / det;
    return [a, b, c, d, e, f];
  };

  return solve(src_pts, dst_pts);
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

      const r = imgData[pixelIdx];
      const g = imgData[pixelIdx + 1];
      const b = imgData[pixelIdx + 2];

      const valR = (r - MEAN[0]) / STD[0];
      const valG = (g - MEAN[1]) / STD[1];
      const valB = (b - MEAN[2]) / STD[2];

      output[0 * w * h + (y * w + x)] = valR;
      output[1 * w * h + (y * w + x)] = valG;
      output[2 * w * h + (y * w + x)] = valB;
    }
  }
  return output;
}

/**
 * Decodes SimCC outputs to keypoints.
 */
function decode(simcc_x, simcc_y, split_ratio) {
  // From your Shape log: [1, 133, 384] and [1, 133, 512]
  // This means K=133, Wx=384, Wy=512
  const K = Math.floor(simcc_x.length / 384);
  const keypoints = new Float32Array(K * 2);
  const scores = new Float32Array(K);

  for (let k = 0; k < K; k++) {
    let max_val_x = -Infinity;
    let max_idx_x = -1;
    let max_val_y = -Infinity;
    let max_idx_y = -1;

    for (let x = 0; x < 384; x++) {
      const val = simcc_x[k * 384 + x];
      if (val > max_val_x) {
        max_val_x = val;
        max_idx_x = x;
      }
    }

    for (let y = 0; y < 512; y++) {
      const val = simcc_y[k * 512 + y];
      if (val > max_val_y) {
        max_val_y = val;
        max_idx_y = y;
      }
    }

    keypoints[k * 2] = max_idx_x / split_ratio;
    keypoints[k * 2 + 1] = max_idx_y / split_ratio;
    scores[k] = Math.max(max_val_x, max_val_y);
  }

  return { keypoints, scores };
}

// --- Worker Listener ---

self.onmessage = async (e) => {
  const { type, payload } = e.data;

  if (type === 'LOAD_MODEL') {
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
      const tensor = new ort.Tensor('float32', inputTensor, [1, 3, MODEL_INPUT_SIZE[1], MODEL_INPUT_SIZE[0]]);
      const inputs = { [session.inputNames[0]]: tensor };

      const outputs = await session.run(inputs);

      // Correctly identify output tensors
      const outputList = Object.values(outputs).filter(o => o !== undefined && o !== null);
      if (outputList.length < 2) {
        throw new Error(`Expected at least 2 outputs from model, but got ${outputList.length}`);
      }

      const outX = outputList[0].data;
      const outY = outputList[1].data;

      // --- Postprocess (Ref: webcam.py) ---
      const { keypoints, scores } = decode(outX, outY, 2.0);

      // Rescale keypoints to original image space
      // keypoints = keypoints / model_input_size * scale + center - scale / 2
      const { center, scale } = bbox_xyxy2cs(bbox);
      const finalKeypoints = new Float32Array(keypoints.length);

      for (let i = 0; i < keypoints.length; i += 2) {
        // Note: model_input_size is [192, 256] (width, height)
        finalKeypoints[i] = (keypoints[i] / MODEL_INPUT_SIZE[0]) * scale[0] + center[0] - (scale[0] / 2);
        finalKeypoints[i+1] = (keypoints[i+1] / MODEL_INPUT_SIZE[1]) * scale[1] + center[1] - (scale[1] / 2);
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
