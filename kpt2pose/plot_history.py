import json
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

def visualize_training_history(history_file: str, title: str = "模型训练误差变化趋势 (Training Loss Curve)",
                               xlabel: str = "训练 Epoch", ylabel: str = "平均 MSE 损失值"):
    """
    从指定的 JSON 文件加载训练历史数据，并生成可视化图表。

    Args:
        history_file (str): 包含 epoch 和 loss 数据的 JSON 文件路径。
        title (str): 图表的标题。
        xlabel (str): X轴的标签。
        ylabel (str): Y轴的标签。
    """
    print(f"--- 开始加载训练历史数据：{history_file} ---")

    try:
        # 1. 从文件中读取所有 epoch 的损失数据
        with open(history_file, 'r') as f:
            data = json.load(f)

        if not data:
            print("❌ 错误：训练历史文件为空，无法生成图表。")
            return # 如果没有数据，则退出函数

        # 2. 分离 Epoch 和 Loss 值
        epochs = [item['epoch'] for item in data]
        losses = [item['loss'] for item in data]

        # 3. 创建图形和子图
        plt.figure(figsize=(12, 6))

        # 绘制损失曲线 (核心部分)
        plt.plot(epochs, losses, marker='o', linestyle='-', color='#D9534F', linewidth=2, label="平均训练损失")

        # 4. 添加图表细节和关键标记
        plt.title(title, fontsize=16)
        plt.xlabel(xlabel, fontsize=14)
        plt.ylabel(ylabel, fontsize=14)

        # 每隔 5 个 epoch 添加一条垂直分割线作为视觉参考
        for i in range(0, len(epochs), 5):
            if i < len(epochs) - 1:
                plt.axvline(x=epochs[i], color='gray', linestyle='--', alpha=0.6)

        # 添加图例和网格线
        plt.legend(fontsize=12, frameon=True)
        plt.grid(True, linestyle=':', alpha=0.7)

        # 优化 x 轴显示，确保 epoch 数字清晰可见
        plt.xticks(epochs, rotation=45, ha="right")
        plt.ylim(bottom=0) # Y轴从0开始
        plt.tight_layout()

        print("\n✅ 图表数据加载并生成完毕。现在展示图表...")
        plt.show()

    except FileNotFoundError:
        print(f"\n⚠️ **【文件未找到】** 请注意：未能找到 '{history_file}' 文件。")
        print("请先确认您已成功运行训练流程，确保数据被写入此 JSON 文件后，再执行绘图脚本。")
    except Exception as e:
        print(f"\n🔥 绘图过程中发生未知错误: {e}")