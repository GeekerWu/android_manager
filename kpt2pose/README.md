# 🎯 Kpt2Pose 模型工作流平台 (Project README)

**当前版本:** `1.0.1` | **状态:** `Production Ready`
---
本项目是一个为姿态估计（或任何回归任务）设计的、高度工程化的机器学习全生命周期管理系统。我们致力于提供一个稳定、可复现、低耦合的开发环境，确保模型训练和推理过程的透明性和可靠性。

## 🌟 核心架构亮点 (Refactored Features)
本次重构的核心是提升了**流程的可观察性（Observability）** 和 **依赖管理（Dependency Management）**：

1.  **🏆 指标可视化增强:** `trainer.py` 增加的指标计算和 `plot_history.py` 的调用，使得模型性能衰退或过拟合的问题可以直观地通过图形化曲线进行早期诊断。
2.  **🔒 版本控制增强 (Model Versioning):** 模型权重文件不再是简单的覆盖写入，而是基于时间戳命名 (`model/model_YYYYMMDD_HHmmss.pth`)。`main.py` 自动识别并加载最新的可用版本，极大地避免了实验痕迹的丢失或混乱。
3.  **🔗 单点配置锁定:** 所有关键常量均集中在 `config.py` 管理，确保全局修改的原子性和安全性。

## 📁 项目结构与模块职责 (Module Deep Dive)
该项目严格遵循微服务/插件式架构的思想，每个文件负责单一、明确的职能：

| 组件 | 文件名 | **核心功能** | **技术抽象度** |
| :--- | :--- | :--- | :--- |
| **Config Layer** | `config.py` | **【参数定义】** 系统的中央配置中心。维护所有常量、路径和超参数（如学习率）。 | 低 (Constants) |
| **Data Layer** | `data_loader.py` | **【数据管道】** 处理原始 CSV 数据 $\rightarrow$ 标准化特征 $\rightarrow$ PyTorch DataLoader，完成数据准备。 | 中 (Preprocessing Pipeline) |
| **Model Layer** | `model.py` | **【架构蓝图】** 定义了模型的网络结构 (`nn.Module`)。与业务逻辑分离，仅负责定义前向传播路径。 | 高 (Abstract Class) |
| **Control Flow** | `trainer.py` | **【业务控制器】** 封装了完整的 ML 生命周期方法（训练、评估、保存）。它协调 Model 和 DataLoader 的交互。 | 极高 (State Machine Logic) |
| **Execution Entry** | `main.py` | **【CLI调度器】** 用户唯一接触点。根据命令行模式 (`--mode`)，按顺序调用上述模块的流程方法。 | 中 (Orchestration) |
| **Utility** | `plot_history.py` | **【分析工具】** 后处理脚本。用于加载和可视化训练日志（Loss History），实现模型的性能趋势分析。 | 低 (Visualization Utility) |

## 💡 如何开始工作 (Getting Started)

### 1. 环境搭建
```bash
pip install pandas torch scikit-learn matplotlib tqdm
```

### 2. 工作流操作流程 (Workflow Execution)
所有流程都通过 `main.py` 启动。

#### 🥇 **[TRAIN] 训练模式**
用于迭代优化模型权重和超参数。

**命令:**
```bash
python main.py --mode train [--epochs N] [--export-metrics]
```
**📌 *最佳实践*:** 始终使用 `--export-metrics` 参数，以获取可复现的指标报告（JSON文件）。

#### 🥈 **[PREDICT] 推理模式**
用于测试模型在当前权重上的预测能力。自动加载最新版本。

**命令:**
```bash
python main.py --mode predict [--export-sample-data]
```
**📌 *注意*:** `predict` 是验证/集成阶段的关键步骤，它使用训练时保存的、带有时间戳的最佳权重。

---
### ♻️ 可扩展性指南 (Future Enhancements)

1.  **更换数据集源**: 修改 `config.py: DATA_PATH` 并更新 `data_loader.py` 的数据读取逻辑。
2.  **网络结构迭代**: 在 `model.py` 中修改隐藏层维度或激活函数，然后重新运行训练流程验证。
3.  **新任务类型**: 如果需要引入新的损失函数 (如 IoU Loss)，应在 `trainer.py` 中更新 `criterion` 的初始化和使用点。
