import torch
import torch.nn as nn
import torch.optim as optim

class RegressionModel(nn.Module):
    """
    一个通用的全连接网络模型，用于回归任务 (Regression Task)。
    设计成模块化的结构，易于调整层数和维度。

    当前基于的输入特征数量为 4 个 (feature1-feature4)，输出标签数为 1.
    """
    def __init__(self, input_dim: int = 4, hidden_dims: list = [32, 64]):
        """
        Args:
            input_dim: 输入特征的维度。
            hidden_dims: 模型中隐藏层的维度列表，例如 [32, 64] 表示两层隐藏层，维度分别为 32 和 64。
        """
        super(RegressionModel, self).__init__()
        self.input_dim = input_dim

        # 存储所有全连接层 (Linear layers)
        layers = []
        current_dim = input_dim

        # 构建隐藏层
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(current_dim, hidden_dim))
            layers.append(nn.ReLU()) # 激活函数，这里统一使用 ReLU
            current_dim = hidden_dim

        # 输出层：将最后一个隐藏层的维度映射到目标标签的维度 (此处为1)
        self.output_layer = nn.Linear(current_dim, 1)

        # 将所有层组合成一个Sequential模块，方便管理和调用
        self.model = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播函数 (Forward Pass)。
        Args:
            x: 输入的特征张量。
        Returns:
            模型输出的预测值张量。
        """
        # 1. 通过所有的隐藏层和激活函数
        x = self.model(x)
        # 2. 经过最终的线性回归层，得到预测结果
        prediction = self.output_layer(x)
        return prediction

def initialize_model(input_dim: int, hidden_dims: list = [32, 64]) -> RegressionModel:
    """
    根据指定的维度初始化并返回一个模型实例。
    """
    return RegressionModel(input_dim=input_dim, hidden_dims=hidden_dims)

if __name__ == '__main__':
    # --- 模型测试 (Self-Test) ---
    INPUT_DIM = 4 # 与 data_loader.py 中的特征数匹配

    print("--- [Model Test] 测试模型初始化和前向传播 ---")
    try:
        model = initialize_model(input_dim=INPUT_DIM)

        # 模拟一个输入张量：[Batch Size, Input Dim]
        dummy_input = torch.randn(10, INPUT_DIM)
        output = model(dummy_input)
        print("✅ 模型初始化成功。")
        print(f"模型输出形状校验: {output.shape} (预期为 [Batch Size, 1])")

    except Exception as e:
        print(f"❌ 模型测试失败：{e}")