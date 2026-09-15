import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class CSVDataset(Dataset):
    """
    自定义 PyTorch Dataset 类，用于从 CSV 文件加载并处理数据。
    实现了特征的标准化和张量转换。
    """
    def __init__(self, csv_file: str, feature_cols: list, target_col: str = None):
        """
        Args:
            csv_file: 数据的路径 (e.g., 'sample_data.csv').
            feature_cols: 需要作为特征的列名列表。
            target_col: 目标标签列名。如果为 None，则抛出错误或使用预设的最后一列。
        """
        print(f"--- [Dataset] 开始加载数据：{csv_file} ---")
        self.df = pd.read_csv(csv_file)
        
        if target_col is None:
            # 假设目标列是最后一个非ID的列，这里需要根据实际情况调整
            self.target_col = self.df.columns[-1]
            print(f"警告：未指定目标列名。自动使用最后一列 '{self.target_col}' 作为目标标签。")
        else:
            self.target_col = target_col
        
        # 筛选出所需的特征和目标列，并忽略第一个ID列 (假设第一列是索引/ID)
        all_cols = self.df.columns.tolist()
        if all_cols[0] == 'ID' or (len(self.df.columns) > len(feature_cols) + 1 and all_cols[0].isdigit()):
             # 忽略第一列作为 ID，只使用指定的特征和目标
            selected_features = [col for col in all_cols if col not in ['ID'] and col not in feature_cols] # A potential issue here if 'ID' is used as a placeholder name
        else:
            # 修正：我们假设第一个列是 ID，剩下的就是数据
             selected_features = feature_cols + [self.target_col]

        self.feature_names = [c for c in all_cols[1:] if c in feature_cols or c == self.target_col] # Simplification: assuming no explicit header is read and the first column is a true ID
        # self.data_features = self.df.iloc[:, 1:].copy()
        self.data_features = self.df.iloc[:, 0:].copy()
        
        # --- 标准化处理 ---
        # 仅对特征列进行标准化
        X_train_raw = self.data_features[feature_cols].dropna()
        y_train_raw = self.data_features[self.target_col].dropna()
        
        if X_train_raw.empty or y_train_raw.empty:
             raise ValueError("数据加载失败或数据全部缺失，无法进行标准化。")

        # 初始化 StandardScaler
        self.scaler = StandardScaler()
        # 拟合和转换特征
        X_scaled_array = self.scaler.fit_transform(X_train_raw)
        self.features_data = pd.DataFrame(X_scaled_array, columns=feature_cols)

        # 重新对齐数据集，确保X和y的行数匹配（以dropna为准）
        valid_indices = X_train_raw.index.intersection(y_train_raw.index)
        self.features_data = self.features_data.loc[valid_indices]
        self.targets_data = y_train_raw.loc[valid_indices]

        print(f"--- [Dataset] 数据预处理完成。特征维度: {self.features_data.shape}, 目标标签维度: {self.targets_data.shape} ---")


    def __len__(self):
        return len(self.targets_data)

    def __getitem__(self, idx):
        """返回一个样本的特征张量和目标张量。"""
        # 获取标准化后的特征和原始目标值
        features = self.features_data.iloc[idx].values.astype(float)
        target = self.targets_data.iloc[idx]

        return torch.tensor(features, dtype=torch.float32), torch.tensor(target, dtype=torch.float32)


def create_data_loaders(csv_file: str, feature_cols: list, target_col: str, batch_size: int = 16):
    """
    创建训练集和验证集的 DataLoader。
    Args:
        csv_file (str): CSV 文件路径。
        feature_cols (list): 特征列名列表。
        target_col (str): 目标标签列名。
        batch_size (int): 批次大小。

    Returns:
        tuple: (train_loader, val_loader)
    """
    
    # 1. 创建数据集实例
    dataset = CSVDataset(csv_file=csv_file, feature_cols=feature_cols, target_col=target_col)
    
    # 为了示例，我们使用数据的 80% 作为训练集，20% 作为验证集
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size

    print(f"\n--- [Data Split] 分割数据集: 训练集 ({train_size} samples), 验证集 ({val_size} samples) ---")

    # 创建用于索引划分的列表
    indices = list(range(len(dataset)))
    train_index = indices[:train_size]
    val_index = indices[train_size:]

    # 使用 Dataset 的 __getitem__ 方式来构建独立的数据集实例，确保标准化参数一致
    from torch.utils.data import Subset

    train_dataset = Subset(dataset, train_index)
    val_dataset = Subset(dataset, val_index)

    # 2. 创建 DataLoader
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    return train_loader, val_loader

if __name__ == '__main__':
    # --- 模拟运行和测试 (假设运行环境已安装 pandas 和 scikit-learn) ---
    DATA_PATH = 'sample_data.csv' # 确保此文件存在于执行目录下
    FEATURE_COLS = ['feature1', 'feature2', 'feature3', 'feature4']
    TARGET_COL = 'target'

    try:
        # 尝试创建 DataLoaders
        train_loader, val_loader = create_data_loaders(
            csv_file=DATA_PATH,
            feature_cols=FEATURE_COLS,
            target_col=TARGET_COL,
            batch_size=3 # 使用小批次进行测试验证
        )

        print("\n✅ DataLoaders 创建成功！开始打印一个批次的样本数据进行校验...")

        # 打印第一个批次的特征和标签，用于视觉确认维度是否正确
        first_batch_features, first_batch_targets = next(iter(train_loader))

        print("-" * 40)
        print("💡 验证通过：")
        print(f"  训练集首个批次 (Features): {first_batch_features.shape} 张，数据类型: {first_batch_features.dtype}")
        print(f"  训练集首个批次 (Targets): {first_batch_targets.shape} 个，数据类型: {first_batch_targets.dtype}")

    except FileNotFoundError:
        print("\n❌ 运行时错误：请确保 'sample_data.csv' 文件位于当前运行目录下。")
    except ValueError as e:
         print(f"\n❌ 数据加载/预处理错误：{e}")
    except Exception as e:
        print(f"\n❌ 发生未知错误：{e}")
