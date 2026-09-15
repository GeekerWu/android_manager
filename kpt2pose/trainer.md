# 🧠 Trainer 控制器类 (`d:\kpt2pose\trainer.py`) 技术文档

**模块作用:**
`Trainer` 类是项目训练流程的核心控制器 (Controller)。它封装了整个模型生命周期管理（包括数据准备、训练循环、性能评估和权重持久化）。所有复杂的 PyTorch 训练状态维护和指标计算逻辑都集中于此。

## Class: Trainer

### `__init__(self, device: torch.device = None)`
**描述:**
初始化训练器，设置运行的计算设备 (`cpu` 或 `cuda`)。这是进入任何训练/评估流程的第一步。

**参数:**
*   `device` (torch.device): 可选，用于指定计算设备。如果未提供，将自动检测并优先使用 CUDA 设备。

**内部逻辑:**
*   设置了全局的 `self.device` 属性，保证后续所有张量操作都发生在正确的计算资源上。
*   打印初始化成功的确认信息。

### `train(self, model: RegressionModel, train_loader: torch.utils.data.DataLoader, criterion: nn.Module, optimizer: optim.Optimizer, num_epochs: int = 1)`
**描述:**
执行模型的完整训练循环。该方法负责梯度清零、前向传播、损失计算、反向传播和优化器步进等核心 PyTorch 操作。

**参数:**
*   `model`: 待训练的 `nn.Module` 模型实例（必须在 `trainer.py` 中定义的模型结构）。
*   `train_loader`: 包含训练数据的 `DataLoader`。
*   `criterion`: 损失函数，如 `nn.MSELoss()`。
*   `optimizer`: 优化器实例，用于控制模型权重更新（例如 `optim.Adam(...)`）。
*   `num_epochs`: 要运行的总训练轮次 (Epochs)。

**核心步骤流程:**
1.  `model.train()`: 将模型设置为训练模式。
2.  循环遍历所有指定 Epoch 及其批次数据 (`tqdm` 提供进度条)。
3.  在每个 Batch 中：
    *   将输入和目标张量移动到 `self.device`。
    *   调用 `optimizer.zero_grad()` 清零梯度。
    *   执行模型前向传播获取 `outputs`。
    *   计算损失 (`loss = criterion(outputs, targets)`)，并将损失加权（乘以 Batch Size）累积到总和中。
    *   执行 `loss.backward()` 进行反向传播，并通过 `optimizer.step()` 更新模型参数。

**返回值:**
无明确返回，通过控制台打印阶段性损失信息 (`print(...)`) 反馈训练进度。

### `evaluate(self, model: RegressionModel, val_loader: torch.utils.data.DataLoader, criterion=nn.MSELoss()):`
**描述:**
在验证集上评估模型性能，不执行梯度计算，旨在获取一系列稳定的、用于报告的指标。这是本次迭代的核心增强点。

**参数:**
*   `model`: 待评估的 `nn.Module` 模型实例。
*   `val_loader`: 包含验证数据的 `DataLoader`。
*   `criterion`: 用于损失计算的损失函数 (默认为 MSELoss)。

**核心逻辑 (🔥 重要增强点):**
1.  `model.eval()`: 将模型切换到评估模式（关闭 Dropout 等训练专用层）。
2.  使用 `with torch.no_grad():` 上下文管理器禁用梯度跟踪，提高效率。
3.  循环遍历验证集，计算并累积三种关键误差指标的总和：
    *   **平方误差 (Squared Error):** 用于 MSE 的总和。
    *   **绝对误差 (Absolute Error):** 用于 MAE 的总和。
    *   **样本计数:** 精确统计总的样本数 (`num_samples`)。

**返回值: `dict` (字典)**
返回一个结构化的指标字典，包含：
*   `validation_mse`: 验证集的平均平方误差（MSE）。
*   `best_mae`: 验证集的平均绝对误差（MAE）。 *（注：当前设计将 MAE 作为替代的关键性能指标。）*

### `save_weights(self, model: RegressionModel, path: str)`
**描述:**
负责将模型的参数状态字典 (`state_dict`) 保存到本地文件系统，并自动实现时间戳版本控制。

**参数:**
*   `model`: 要保存的模型实例。
*   `path`: 模型权重应该存放的目录路径（仅提供目录名）。

**内部逻辑:**
1.  构造完整的文件路径：使用当前日期和时间生成唯一的后缀，例如 `./{path}/model_YYYYMMDD_HHMMSS.pth`。
2.  调用 `torch.save()` 将模型权重保存到此唯一路径，防止覆盖历史最佳版本。

### `load_weights(self, model: RegressionModel, path: str)`
**描述:**
从指定路径加载已保存的模型参数状态字典，用于推理前的模型恢复。

**参数:**
*   `model`: 目标模型实例（必须在调用前已经实例化）。
*   `path`: 模型权重文件的完整绝对路径。

**核心逻辑与鲁棒性:**
1.  首先将模型切换到评估模式 (`model.eval()`)。
2.  使用 `try...except` 块进行严格的错误捕获，可以优雅地处理以下三种关键失败情况：
    *   `FileNotFoundError`: 文件不存在。
    *   `RuntimeError`: 模型结构不匹配（例如，当前模型增加了层，而加载权重是旧版本的）。

**总之，该类通过高度封装这些复杂的 PyTorch 流程和文件I/O细节，为项目提供了可靠、可复用的训练控制层。