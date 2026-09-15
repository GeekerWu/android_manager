# Project ModelTrain Architecture Plan

**Context**: 本项目旨在构建一个完整的、工业级可用的 PyTorch 深度学习模型训练工作流，能够处理从 CSV 文件加载的数据到最终的模型推理预测的全过程。为了实现高模块化和良好的工程实践，架构必须严格分离数据处理、模型定义、业务逻辑（训练）和入口控制四个核心层。

**Goal**: 实现一个名为 modeltrain 的项目，具备以下功能：
1. **Data Loading**: 从 CSV 文件读取，进行标准化预处理，生成 PyTorch `DataLoader`。
2. **Model Definition**: 定义具体的网络结构。
3. **Training Cycle**: 管理完整的训练、评估和权重更新流程。
4. **Serialization/Deserialization**: 实现模型权重的持久化（保存为 `.pt`）和加载功能。
5. **Inference**: 使用已加载的模型进行新的数据预测。

**Modules & Files:**

1.  **`data_loader.py` (数据处理层)**:
    *   职责：封装所有与 CSV I/O 和 PyTorch 数据转换相关的逻辑。
    *   核心类：`CSVDataset(torch.utils.data.Dataset)`，实现 `__len__` 和 `__getitem__`。
    *   方法要求：必须包含数据预处理（如归一化、特征编码）的步骤，确保返回的数据是标准化的 PyTorch Tensor。

2.  **`model.py` (模型定义层)**:
    *   职责：定义网络结构。
    *   核心类：`MyModel(torch.nn.Module)`。
    *   方法要求：实现 `__init__` 和 `forward()` 方法，结构必须是通用的，以便将来替换具体的网络架构（如从 CNN 改为 Transformer）。

3.  **`trainer.py` (训练与管理层)**:
    *   职责：作为项目的“大脑”，隔离业务逻辑。不应包含数据读取和模型定义。
    *   核心类：`Trainer`。
    *   方法集合：
        *   `train(model, train_loader, criterion, optimizer)`：实现完整的 epoch 循环、loss 计算、反向传播和优化器步进。
        *   `evaluate(model, val_loader, criterion)`：负责验证集的性能评估，返回准确率或平均损失。
        *   **`save_state(model, path)`**: 使用 `torch.save(model.state_dict(), path)` 保存权重。
        *   **`load_state(model, path)`**: 使用 `model.load_state_dict(torch.load(path))` 加载权重，并确保模型处于评估模式 (`model.eval()`)。

4.  **`main.py` (项目入口/控制层)**:
    *   职责：作为 CLI 接口和主调度器。
    *   执行流程（通过命令行参数 `sys.argv` 控制）：
        *   `python main.py --mode train`: 初始化 -> 加载数据 -> 实例化模型 -> 调用 Trainer.train() -> 保存模型。
        *   `python main.py --mode predict`: 实例化模型 (并加载权重) -> 准备测试数据 DataLoader -> 调用推理函数，输出结果。

**执行流程依赖关系:**
`main.py` $\rightarrow$ `data_loader.py` / `model.py` / `trainer.py`

**关键最佳实践提醒**:
*   所有的设备管理（GPU/CPU）应在入口文件或 Trainer 的初始化时统一处理。
*   模型推理必须始终使用 `torch.no_grad()` 上下文管理器，并在调用前设置 `model.eval()`。
*   代码中要体现清晰的配置分割点 (Configuration Management)，例如用一个 `config.py` 来集中管理数据集路径、学习率、批次大小等超参数。

**Summary**: 本架构设计提供了一个高度模块化且符合 PyTorch 工程标准的蓝图，所有功能都被精确地分配到不同的文件中，极大地增强了项目的可维护性和扩展性。
***