# 🧠 Model 模型结构 (`d:\kpt2pose\model.py`) 技术文档

**模块作用:**
该文件定义了本项目所有主要的深度学习模型架构，特别是 `RegressionModel` 类。它负责将输入的特征张量映射到最终的预测输出（一个标量值）。该模型的模块化设计使其易于调整和实验不同的网络拓扑结构。

## Class: RegressionModel (nn.Module)

### 1. 初始化 (`__init__(self, input_dim: int = 4, hidden_dims: list = [32, 64])`)
**描述:**
根据用户指定的输入维度和隐藏层结构构建网络骨架。这是定义模型架构的入口点。

**关键逻辑与增强点:**
*   **模块化构建**: 使用循环和 `nn.Sequential` 模块来动态构建整个网络。这使得代码极具扩展性，只需修改 `hidden_dims` 即可改变网络深度和宽度。
*   **激活函数**: 默认使用 `nn.ReLU()` 作为隐藏层之间的非线性激活函数。
*   **维度映射**: 精确地跟踪当前层的输出维度 (`current_dim`)，确保每一层都能正确接收上一层的输出尺寸作为输入。

### 2. 前向传播 (`forward(self, x: torch.Tensor) -> torch.Tensor`)
**描述:**
定义数据流动的路径。它接受一个特征张量 `x` 并返回预测值。这是模型执行推理和训练的核心所在。

**核心步骤:**
1.  `x = self.model(x)`: 首先将输入数据通过所有构建好的隐藏层和 ReLU 激活函数进行处理，得到一个经过非线性变换的特征表示。
2.  `prediction = self.output_layer(x)`: 最后，使用最终线性层将这些高维度的特征表示压缩到目标维度（1），得出回归预测值。

**数据流向:** `Input -> Linear Layer (L1) -> ReLU -> ... -> Linear Layer (LN) -> Output (Prediction)`

### 3. 模型初始化 (`initialize_model(input_dim: int, hidden_dims: list = [32, 64])`)
**描述:**
提供一个简单的工厂函数，用户只需传入输入维度和隐藏层列表，即可获得一个实例化且可用的 `RegressionModel` 对象。

## 后续扩展建议 (Future Enhancements)
*   如果需要引入其他类型的激活函数（如 GeLU 或 Swish），应修改此处的 `nn.ReLU()` 部分并考虑在初始化参数中暴露选择开关。
*   将模型架构的配置信息提取到一个单独的 YAML/JSON 配置文件中，使模型结构和训练脚本解耦。

**总之，该类提供了一个高度可配置、遵循标准 PyTorch 设计模式的回归预测网络骨架。**