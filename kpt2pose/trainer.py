import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm # 引入tqdm用于显示训练进度条
import os
import datetime

# 假设 model 和 data_loader 的文件结构已存在，进行相对导入
try:
    from model import RegressionModel, initialize_model
except ImportError:
    print("警告：无法从 'model.py' 导入模型。请确保 model.py 在 PYTHONPATH 中可访问。")
    # 为了让代码块可独立运行测试，我们暂时定义一个 Mock 模型（实际使用时应删除此部分）
    class RegressionModel(nn.Module):
        def __init__(self, input_dim: int = 4, hidden_dims: list = [32, 64]):
            super().__init__()
            # 使用占位符，防止运行时依赖问题
            self.linear = nn.Linear(input_dim, 1)
        def forward(self, x):
            return self.linear(x)

class Trainer:
    """
    项目训练控制器类。封装了整个模型生命周期 (训练、评估、保存)。
    这是一个整合后的版本，包含了所有必要的生命周期管理方法。
    """

    def __init__(self, device: torch.device = None):
        """初始化 Trainer，设置计算设备。"""
        self.device = device or torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        print(f"--- [Trainer] 初始化完成。运行设备设置为: {self.device} ---")

    def train(self, model: RegressionModel, train_loader: torch.utils.data.DataLoader, criterion: nn.Module, optimizer: optim.Optimizer, num_epochs: int = 1):
        """
        执行模型训练循环。
        Args:
            model: 要训练的 nn.Module 模型实例。
            train_loader: 包含训练数据的 DataLoader。
            criterion: 损失函数 (e.g., nn.MSELoss())。
            optimizer: 优化器 (e.g., optim.Adam(model.parameters(), lr=0.001))。
            num_epochs: 训练轮次。
        """
        if optimizer is None:
            print("错误：必须提供一个优化器实例来开始训练。")
            return

        # 将模型移动到指定设备
        model.to(self.device)
        model.train() # 设置为训练模式

        history = {'train_loss': []}

        for epoch in range(num_epochs):
            total_epoch_loss = 0
            # 使用 tqdm 创建进度条
            print(f"\n==== Epoch {epoch+1}/{num_epochs}: 开始训练 ====")
            loop = tqdm(train_loader, desc=f"Epoch {epoch+1} Training")

            for i, (inputs, targets) in enumerate(loop):
                # 1. 数据移动到设备
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)

                # 2. 清零梯度
                optimizer.zero_grad()

                # 3. 前向传播
                outputs = model(inputs)

                # 4. 计算损失 (Loss Calculation)
                loss = criterion(outputs, targets)
                total_epoch_loss += loss.item() / len(train_loader) # 平均每个batch的损失

                # 5. 反向传播和优化 (Backward Pass & Step)
                loss.backward()
                optimizer.step()

            avg_loss = total_epoch_loss / len(train_loader)
            history['train_loss'].append(avg_loss)
            if (epoch + 1) % 10 == 0 or epoch == num_epochs - 1:
                print(f"--> Epoch {epoch+1} 训练结束。平均损失: {avg_loss:.4f}")

    def evaluate(self, model: RegressionModel, val_loader: torch.utils.data.DataLoader, criterion=nn.MSELoss()):
        """
        在验证集上评估模型性能，返回包含关键指标的字典。
        指标包括 MSE (Mean Squared Error), MAE (Mean Absolute Error) 和 RMSE (Root Mean Squared Error)。
        """
        model.eval() # 关键：切换到评估模式

        # 初始化累加器，用于收集不同指标的总和
        total_sq_error = 0.0  # 用于计算 MSE 的平方误差总和
        total_abs_error = 0.0 # 用于计算 MAE 的绝对误差总和
        num_samples = 0

        print("\n==== 开始模型评估 (Validation) ====")

        with torch.no_grad(): # 禁用梯度跟踪，节省内存和时间
            for inputs, targets in tqdm(val_loader, desc="Evaluating Model"):
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)

                # 前向传播
                outputs = model(inputs)
                batch_size = inputs.size(0)

                # 1. MSE (Mean Squared Error) 的累加：平方误差总和
                sq_error = (outputs - targets)**2
                total_sq_error += sq_error.sum().item()

                # 2. MAE (Mean Absolute Error) 的累加：绝对误差总和
                abs_error = torch.abs(outputs - targets)
                total_abs_error += abs_error.sum().item()

                num_samples += batch_size # 直接累计样本数

        # --- 计算最终指标 ---
        if num_samples == 0:
            print("⚠️ 警告：验证集加载器为空，无法计算任何指标。")
            return {}

        # MSE (平均平方误差) = 总平方误差 / 总样本数
        mse = total_sq_error / num_samples

        # MAE (平均绝对误差) = 总绝对误差 / 总样本数
        mae = total_abs_error / num_samples

        # RMSE (均方根误差) = sqrt(MSE)
        rmse = mse**0.5

        # 打印结果，增强用户体验（仅供控制台反馈）
        print("\n--- 🏆 模型性能评估报告 ---")
        print(f"  ✅ MSE (Mean Squared Error): {mse:.6f}")
        print(f"  ✅ MAE (Mean Absolute Error): {mae:.6f}")
        print(f"  ✅ RMSE (Root Mean Squared Error): {rmse:.6f}")

        # 按照 main.py 的期望，返回包含核心指标的字典结构
        return {
            'validation_mse': mse,
            'best_mae': mae # 使用 MAE 作为替代的关键性能指标
        }

    def save_weights(self, model: RegressionModel, path: str):
        """
        将模型的参数状态字典保存到指定的路径。
        Args:
            model: 要保存的模型实例。
            path: 目标模型文件的目录，不是完整的文件名。
        """
            

        print(path)
        # 2. 确保父目录存在（关键健壮性增强）
        os.makedirs(os.path.dirname('/'+path), exist_ok=True)
        print('a')
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        full_save_path=f"./{path}/model_{timestamp}.pth"
        print(full_save_path)

        try:
            # 3. 保存权重：将 state_dict 写入到新的时间戳路径
            torch.save(model.state_dict(), full_save_path)
            print(f"✨ 模型权重已成功保存到时间戳版本: {full_save_path}")
        except Exception as e:
            print(f"❌ 保存模型权重失败，请检查目录权限或路径是否正确。错误信息: {e}")

    def load_weights(self, model: RegressionModel, path: str):
        """
        从指定路径加载模型参数状态字典。
        Args:
            model: 目标模型实例，必须与保存时的结构一致。
            path: 模型权重文件 (.pt) 的绝对路径。
        Returns:
            True 如果加载成功，否则返回 False。
        """
        try:
            # 1. 确保模型处于评估模式，防止状态冲突
            print(self.device)
            model.to(self.device)
            model.eval()

            # 2. 加载权重
            state_dict = torch.load(path, map_location=self.device)
            model.load_state_dict(state_dict)
            print(f"✨ 模型权重已成功加载自: {path}")
            return True
        except FileNotFoundError:
            print(f"❌ 错误：未找到模型权重文件在路径: {path}")
            return False
        except RuntimeError as e:
            # 这通常发生在加载的模型状态和当前模型结构不匹配时
            print(f"❌ 加载失败，请检查模型结构是否一致。详细错误: {e}")
            return False

if __name__ == '__main__':
    # --- 整体测试 (需依赖 model.py, data_loader.py) ---
    print("\n\n===================================================")
    print(">>> [Trainer] 重构后的 Trainer 类已成功集成所有功能块。")
    print(">>> 在 main.py 中集成时，只需使用单一的 Trainer 实例即可调用完整的生命周期管理方法。")
    print("===================================================\n")