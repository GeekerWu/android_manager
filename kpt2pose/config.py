# config.py - 项目配置中心

"""
本项目所有的通用和硬编码配置常量应放在这里。
这样做的好处是实现单点配置修改 (Single Source of Truth)，提高代码的可维护性和可读性。
"""

# --- 文件路径配置 ---
# 必须确保这些路径在运行环境中是正确的，或者使用相对路径。
DATA_PATH = 'sample_data.csv'  # 用于加载训练和验证数据的主 CSV 文件
MODEL_SAVE_PATH = 'model' # 模型最佳权重保存路径

# --- 数据特征配置 ---
FEATURE_COLS = [
    'feature1',
    'feature2',
    'feature3',
    'feature4'
]  # 输入模型的特征列名（确保顺序和数量匹配）
TARGET_COL = 'target'      # 模型需要预测的目标列

# --- 模型训练超参数配置 ---
BATCH_SIZE = 30            # DataLoader 的批次大小
LEARNING_RATE = 0.001       # 优化器学习率
MAX_EPOCHS = 30             # 默认最大训练周期数（用于CLI覆盖）