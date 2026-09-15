# 🚀 RTMPose 姿态估计模块文档 (Webcam/Live Stream)

**Module:** `webcam.py`
**Project Path:** `d:\kpt2pose\onnxruntime\`
**⭐ 模块功能:** 从实时视频流中捕获视频帧，并执行完整的端到端（End-to-End）人体姿态估计流程。它是系统实时追踪功能的核心实现。

---

## 💡 1. 核心工作流概述 (Workflow Overview)

本模块的整个执行流程是线性、连续的：
`VideoCapture` $\to$ `while True` $\to$ `read_frame` $\to$ **预处理** $\to$ **推理** $\to$ **后处理** $\to$ **可视化** $\to$ **等待退出信号** $\to$ `finally` $\to$ 资源释放。

**理解关键点:**
*   **实时性:** 系统在 `while True` 循环中运行，处理每一帧数据，因此需要持续观察和输入。
*   **资源管理:** 资源（如摄像头端口）的释放由 `finally` 块严格控制，这是程序健壮性的体现。

---

## ⚙️ 2. 使用指南 (User Guide)

### A. 环境依赖 (Prerequisites)
为了确保环境的兼容性和稳定性，请使用以下精确版本号进行安装。

**核心依赖 (Critical Dependencies):**
```bash
pip install loguru==0.6.0 numpy==1.21.6 opencv-python onnxruntime==1.14.1
```

**性能优化 (GPU 推荐):**
如果您的环境支持 GPU 并且希望获得最高帧率，请使用以下命令：
```bash
pip install onnxruntime-gpu==1.8.1
```

### B. 命令行调用 (CLI)
脚本的核心逻辑由 `main()` 函数驱动，必须通过命令行参数来定义输入源和计算环境。

**基本调用格式:**
```bash
python webcam.py --camera_index [相机编号] [--device <device>]
```

**参数说明:**
| 参数 | 类型 | 描述 | 必填性 | 默认值 |
| :--- | :--- | :--- | :--- | :--- |
| `camera_index` | 整数 | **视频流的源索引。** `0` 代表系统默认摄像头。 | **必需** | 0 |
| `--device` | 字符串 | 推理设备类型。可选值：`cpu` 或 `cuda`。 | 选填 | `cpu` |

**🎯 关键调用示例:**

1.  **【基础模式】(CPU/默认相机):**
    这是最稳定、最兼容的运行模式。
    ```bash
    python webcam.py --camera_index 0 --device cpu
    ```

2.  **【高性能模式】(GPU/特定相机):**
    推荐用于生产环境，利用 GPU 资源加速推理。
    ```bash
    python webcam.py --camera_index 1 --device cuda
    ```

3.  **【模型定制模式】(指定模型路径):**
    如果使用的模型文件不在当前目录，必须将模型文件路径作为第一个非可选参数传入。
    假设我们使用的是标准的 RTMPose 模型文件：
    ```bash
    python webcam.py rtmposefullbody.onnx --camera_index 0
    ```
    *注意: 在此示例中，`rtmposefullbody.onnx` 文件需要位于运行脚本的当前工作目录下。*

**🚨 退出流程 (极度重要!):**
程序在视频窗口运行后会进入一个无限循环。**必须**在实时视频窗口上按下 **`q`** 键。这是触发 `finally` 块执行资源清理的唯一方式，否则摄像头资源会持续被占用。
