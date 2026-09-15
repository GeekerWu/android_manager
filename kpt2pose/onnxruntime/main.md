# 🚀 RTMPose 人体姿态估计文档

本指南提供了关于 `main.py` 脚本所实现的 RTMPose 推理流程的全面概述和使用说明。该脚本利用 RTMPose 模型，这是一个高效的深度学习模型，用于从输入图像中准确地检测和绘制人体关键点。

## 📋 1. 背景：什么是 RTMPose？

**目的：** 本系统的主要目标是实现实时的人体姿态估计。给定一张输入图像，该脚本能够估算出图像中一个或多个人体关键身体关节（如肩膀、肘部、膝盖）在二维坐标系中的精确位置。

**工作原理：** RTMPose 模型经过训练，输出对应于关键解剖点的**高分辨率热图**（特别是中心点/SimCC 热图）。系统随后通过一个鲁棒的过程解码这些热图，从而推导出精确、像素级的关键点坐标及其相关的置信度得分。最终结果是在原始图像上叠加了骨骼结构的视觉化结果。

## 🛠️ 2. 先决条件和环境配置

要运行此管道，请确保您的开发环境满足以下要求：

### A. 硬件要求
*   **最低配置：** 现代 CPU，至少 8GB 内存。
*   **推荐配置 (性能)：** 支持 CUDA 的 GPU（例如 NVIDIA RTX 系列）。强烈建议使用兼容的 GPU，因为 ONNX Runtime 可以通过 GPU 大幅加速推理时间。

### B. 软件依赖
您必须安装所需的 Python 库。建议在一个虚拟环境中（例如 `conda` 或 `venv`）进行操作。

```bash
# 1. 克隆或进入项目目录
# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows用户请使用 venv\Scripts\activate

# 3. 安装依赖项
# 核心库，用于推理和图像处理
# 依赖列表来自 requirements.txt
pip install loguru==0.6.0 numpy==1.21.6 onnxruntime==1.14.1 opencv-python
# 如果使用 GPU，请额外安装：
# pip install onnxruntime-gpu==1.8.1
```

### C. 模型文件
请确保必要的模型资产位于项目目录中：
*   `rtmposefullbody.onnx`: 核心 ONNX 模型权重文件。
*   `config.json`: 模型配置文件，定义了输入/输出尺寸和关键点定义。

## 💻 3. 运行：执行流程与参数说明

该脚本通过命令行参数来指定输入模型和图像，并支持配置运行环境和输出路径。

**基本调用格式：**
```bash
python main.py <ONNX模型文件路径> <输入图像文件路径> [可选参数]
```

**参数说明：**

| 参数 | 类型 | 描述 | 必填性 | 默认值 |
| :--- | :--- | :--- | :--- | :--- |
| `onnx_file` | 路径 | 姿态估计模型（ONNX）文件路径。 | 必需 | N/A |
| `image_file` | 路径 | 需要进行姿态估计的输入图像文件路径。 | 必需 | N/A |
| `--device` | 字符串 | 推理使用的设备类型，可选值包括 `cpu` 或 `cuda`。 | 选填 | `cpu` |
| `--save-path` | 路径 | 保存可视化结果的输出图片路径。 | 选填 | `output.jpg` |

**示例：**
假设我们使用当前目录下的 `rtmposefullbody.onnx` 模型文件和 `human-pose.jpeg` 作为输入图像，并将结果保存到 `pose_output.jpg`：

```bash
python main.py rtmposefullbody.onnx test_img/human-pose.jpeg --save-path test_img/pose_output.jpg
```
*如果您的机器有支持 CUDA 的 GPU，可以使用以下命令加速：*
```bash
python main.py rtmposefullbody.onnx test_img/human-pose.jpeg --device cuda --save-path test_img/pose_output_gpu.jpg
```

***
*注意：脚本会自动处理模型加载和完整的处理流程。*
***

## 🧩 4. 组件分解：系统逻辑

`main.py` 脚本被结构化为四个独立、顺序执行的组件，每个组件负责推理管道中的特定步骤。

### `preprocess(image)` (预处理)
此函数负责将原始输入图像准备成 RTMPose 模型所需的格式。

*   **输入：** 原始彩色图像（例如使用 OpenCV 格式）。
*   **流程：**
    1.  **缩放 (Resizing):** 图像被缩放到 ONNX 模型预期的固定输入尺寸。
    2.  **仿射变换 (Affine Transformation):** 图像通过仿射变换，确保关键区域的几何结构（如长宽比和对齐）保持正确，这对检测精度至关重要。
    3.  **归一化 (Normalization):** 像素值被标准化（通常缩放到 [0, 1] 或 [-1, 1] 范围），以稳定模型的输入。
*   **输出：** 一个标准化、预缩放的 NumPy 数组，可用于 ONNX 推理。

### `inference(preprocessed_image)` (推理)
此组件执行模型的核心数学计算过程。

*   **输入：** 预处理后的、归一化的图像数组。
*   **流程：**
    1.  **ONNX 会话：** 使用 `rtmpose_model.onnx` 文件初始化 ONNX Runtime 会话。
    2.  **执行：** 将预处理后的图像通过 ONNX 模型运行推理。
    3.  **输出：** 模型输出多个原始张量热图（SimCC 热图），每个热图对应模型定义的关键点。
*   **输出：** 一个包含原始模型输出热图的字典或数组。

### `postprocess(heatmaps)` (后处理)
这是将模型输出从抽象热图数据转化为实际人体关节坐标的关键解码阶段。

*   **输入：** 来自 `inference` 阶段的原始热图。
*   **流程：**
    1.  **峰值检测 (Peak Detection):** 对每个热图，检测最高概率的点（即激活峰值），该点即为预测的关键点位置。
    2.  **坐标提取 (Coordinate Extraction):** 提取峰值的 (x, y) 坐标，代表预测的关键点位置。
    3.  **置信度评分 (Confidence Scoring):** 将热图值转换为标准的置信度得分，用于评估预测的可靠性。
    4.  **骨架构建 (Skeleton Construction):** 根据预设的解剖学骨骼连接关系，将关键点组建成人体骨架结构。
*   **输出：** 一组检测到的关键点（包含坐标和置信度得分）以及相应的骨骼连接结构。

### `visualize(original_image, keypoints, skeleton)` (可视化)
负责将最终结果呈现在用户面前的函数。

*   **输入：** 原始未修改的输入图像、检测到的关键点坐标和骨骼结构定义。
*   **流程：**
    1.  **绘制关键点：** 在原始图像的 $(x, y)$ 坐标位置绘制圆点，其大小和颜色可以根据置信度得分进行区分。
    2.  **绘制骨架：** 根据模型定义的骨骼连接，在连接的关节之间绘制线条，形成连贯的骨架叠加层。
*   **输出：** 带有可见注释（关键点和骨骼）的原始图像，并将其保存为最终输出图像。

***
**文档更新完成**