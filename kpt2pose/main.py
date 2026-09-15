import torch
from data_loader import create_data_loaders
from model import initialize_model
from trainer import Trainer

# 假设配置和CLI依赖现在从一个统一的config模块导入，这是最佳实践。
try:
    from config import (
        DATA_PATH, FEATURE_COLS, TARGET_COL, BATCH_SIZE,
        MODEL_SAVE_PATH, LEARNING_RATE, MAX_EPOCHS
    )
except ImportError:
    # 降级处理：如果用户没有创建 config.py，则使用硬编码作为后备（低质量模式）
    print("⚠️ Warning: 'config' module not found. Using hardcoded fallback constants.")
    DATA_PATH = 'sample_data.csv'
    FEATURE_COLS = ['feature1', 'feature2', 'feature3', 'feature4']
    TARGET_COL = 'target'
    BATCH_SIZE = 30
    MODEL_SAVE_PATH='model' # 注意：使用一个更简单的默认路径进行本地调试/模拟
    MAX_EPOCHS = 30

import argparse
import json
import glob # 新增文件系统操作依赖于glob

def export_results(data: dict | list[dict], filename: str, export_format: str = 'csv'):
    """
    将计算得到的结构化数据（如指标或样本对）导出到指定文件。
    Args:
        data: 要导出的数据，可以是字典（单个结果）或列表（多个样本）。
        filename: 导出的文件名 (不含扩展名)。
        export_format: 'csv' 或 'json'。
    """
    print(f"⚙️ 尝试导出 {len(data)} 条记录到文件: {filename}.{export_format}")

    if export_format == 'csv':
        import csv
        try:
            # 确保 data 是列表，并且至少包含一个元素来确定 fieldnames
            fieldnames = list(data[0].keys()) if isinstance(data, list) and data else []
            if not fieldnames: # 避免空数据导致字段错误
                print("❌ 无法导出 CSV：输入数据为空或结构不一致。")
                return False

            with open(f"{filename}.{export_format}", 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                if isinstance(data, list):
                    writer.writerows(data)
                else:
                    # 如果是单个指标字典，则将其写入一行数据
                    writer.writerow(data)
            print(f"✅ 数据成功导出为 CSV 格式: {filename}.csv")
            return True

        except Exception as e:
            print(f"❌ 警告：CSV 导出失败。可能原因包括缺少依赖 (如 csv)，或数据结构不一致。错误信息: {e}")
            return False

    elif export_format == 'json':
        try:
            with open(f"{filename}.{export_format}", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"✅ 数据成功导出为 JSON 格式: {filename}.json")
            return True
        except Exception as e:
            print(f"❌ 警告：JSON 导出失败。错误信息: {e}")
            return False
    else:
        print("⚠️ 未知导出格式，不支持的 format:")
        return False

def main():
    """
    主入口函数：根据命令行参数运行训练、推理或仅帮助。
    """
    parser = argparse.ArgumentParser(description="Kpt2Pose 模型的完整生命周期管理工具。", formatter_class=argparse.RawDescriptionHelpFormatter)

    # CLI 参数定义
    parser.add_argument('--mode', type=str, choices=['train', 'predict'], default='help',
                        help='运行模式：train (训练), predict (推理)。')
    parser.add_argument('--epochs', type=int, default=MAX_EPOCHS,
                        help=f'用于训练的最大 Epoch 数 (默认: {MAX_EPOCHS})。')
    parser.add_argument('--export-metrics', action='store_true', help='在训练结束后导出关键性能指标到 JSON 文件。')
    parser.add_argument('--export-sample-data', action='store_true', help='在推理结束后，将输入样本和预测结果导出为 CSV 文件。')

    args = parser.parse_args()

    print("=" * 60)
    print(f"           🚀 ModelTrain 项目主控入口 (main.py - Refactored)          ")
    print("=" * 60)
    print(f"⚙️ 启动模式: {args.mode}")
    if args.epochs != MAX_EPOCHS:
        print(f"📈 使用的 Epoch 数: {args.epochs}")

    # --- 1. 初始化组件 (资源检查和初始化) ---
    try:
        print("\n[STEP 1/3] 正在初始化核心组件...")

        train_loader, val_loader = create_data_loaders(
            csv_file=DATA_PATH,
            feature_cols=FEATURE_COLS,
            target_col=TARGET_COL,
            batch_size=BATCH_SIZE
        )
        print('  ✅ 状态: DataLoader 初始化成功。')

        model = initialize_model(input_dim=len(FEATURE_COLS))
        print('  ✅ 状态: Model 架构初始化成功。')

        trainer = Trainer()
        print('  ✅ 状态: Trainer 类实例化成功。')

    except Exception as e:
        print(f"\n❌ 致命错误：项目启动失败，无法初始化核心组件。请检查依赖文件和配置文件（config.py）。错误信息: {e}")
        return


    # --- 2. 根据模式执行流程 (Mode Dispatching) ---
    if args.mode == 'train':
        print("\n\n========== [ MODE: TRAIN ] ===========================")

        criterion = torch.nn.MSELoss() # 回归任务常用均方误差
        optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

        try:
            # 训练模型 (使用命令行指定的 Epoch 数)
            trainer.train(
                model=model,
                train_loader=train_loader,
                criterion=criterion,
                optimizer=optimizer,
                num_epochs=args.epochs # 使用CLI参数的Epoch数
            )

            # 模型评估 (Model Evaluation)
            val_metrics = trainer.evaluate(model, val_loader, criterion)
            print("\n--- 🏆 模型性能评估报告 ---")

            # 关键修复：首先检查指标字典本身是否存在，避免迭代时崩溃。
            if not val_metrics:
                print("⚠️ 模型评估失败或未返回有效指标 (val_metrics 为空/None)。请检查 trainer.evaluate 方法是否成功执行并返回数据。")
            else:
                # 安全地遍历和打印所有已获取的指标
                for k, v in val_metrics.items():
                    # 增强健壮性：尝试将值转换为浮点数进行格式化。
                    try:
                        float_v = float(v) # 使用更广范围的转换，捕获各种数字类型
                        print(f"  {k}: {float_v:.6f}")
                    except (TypeError, ValueError):
                        # 安全处理非数值类型或 None 值，避免抛出 "NoneType object has no attribute 'get'" 错误
                        print(f"  {k}: {repr(v)} [⚠️ 数据类型警告: 指标值 '{k}' 的原始数据无法安全格式化为浮点数]")
            # 保存模型权重
            trainer.save_weights(model,MODEL_SAVE_PATH)
            print("\n✅ 模型权重保存完成。")

            if args.export_metrics:
                # 修复的关键：使用 .get(key, default_value) 来安全地获取指标，防止父对象为 None 时报错
                metric_report = {
                    "mode": "train",
                    "epochs_run": args.epochs,
                    # 如果 val_metrics 为 None 或者 key 不存在，则默认取 None 而不是引发 KeyError/AttributeError
                    "validation_mse": val_metrics.get('validation_mse', None) if val_metrics else None,
                    "best_mae": float(val_metrics.get('best_mae') or -1), # 使用 'or' 确保None时使用-1，避免float()抛出TypeError
                    # 计算总样本数 (如果需要，根据实际逻辑调整)
                    "total_samples": len(train_loader) * BATCH_SIZE
                }
                export_results(metric_report, "training_metrics", export_format='json')

        except Exception as e:
            print(f"⚠️ [TRAIN] 训练流程发生错误：{e}")


    elif args.mode == 'predict':
        print("\n\n========== [ MODE: PREDICT ] ========================")

        predictor_model = initialize_model(input_dim=len(FEATURE_COLS))

        # --- FIX: 从目录中选择最新模型权重 ---
        from glob import glob # 必须导入glob
        import os # 必须导入os

        model_path_pattern = os.path.join(MODEL_SAVE_PATH, 'model_*.*')
        print(model_path_pattern)
        all_model_paths = glob(model_path_pattern)

        if not all_model_paths:
            print("❌ 致命错误：在模型保存目录下未找到任何权重文件。请先运行训练模式生成模型。")
            return

        # 按修改时间 (os.path.getmtime) 排序，并选取最后一个（即最新的）文件路径
        # os.path.getmtime 返回的是Unix时间戳，数字越大，越新。
        all_model_paths.sort(key=os.path.getmtime)
        latest_model_path = all_model_paths[-1] # 选取最后一个 (最新的那个)

        print(f"🔎 自动检测到最新的模型权重文件：{latest_model_path}")
        # --- END FIX: 替换了原有的单点路径依赖逻辑 ---


        if trainer.load_weights(predictor_model, latest_model_path):
            print("\n✅ 模型权重加载成功。准备进行推理测试...")

            # --- 构建用于预测的虚拟数据 (模拟读取外部输入) ---
            DUMMY_BATCH_SIZE = 5
            device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") 
            dummy_inputs = torch.randn(DUMMY_BATCH_SIZE, len(FEATURE_COLS)).to(device)

            print(f"\n--- [推理测试] 输入 {DUMMY_BATCH_SIZE} 个虚拟样本 ---")

            # 推理核心代码块: 必须使用 no_grad() 上下文管理器
            predictor_model.eval() # 确保模型在评估模式
            with torch.no_grad():
                predictions = predictor_model(dummy_inputs)

            print("\n✨ 模型推理完成。")
            print(f"  -> 预测结果张量形状: {predictions.shape}")
            # 打印前两个样本的预测值进行确认
            print("  -> 前两个样本的预测值示例:")
            cpu_tensor =predictions.cpu()
            print(cpu_tensor[0].numpy())
            print(cpu_tensor[1].numpy())

            if args.export_sample_data:
                # 触发样本数据导出功能：将输入特征和结果打包成列表，用于CSV写入。
                export_data = []
                for i in range(DUMMY_BATCH_SIZE):
                    sample_row = {
                        'input_feature1': dummy_inputs[i, 0].item(),
                        'input_feature2': dummy_inputs[i, 1].item(),
                        'input_feature3': dummy_inputs[i, 2].item(),
                        'input_feature4': dummy_inputs[i, 3].item(),
                        'predicted_value': predictions[i].item()
                    }
                    export_data.append(sample_row)

                # 执行导出
                export_results(export_data, "prediction_samples", export_format='csv')


    elif args.mode == 'help':
        print("\n\n[❓ 帮助信息] 请使用以下格式运行程序:")
        print(f"1. 训练模式 (带导出): python main.py --mode train --epochs 50 --export-metrics")
        print(f"2. 推理模式 (带导出): python main.py --mode predict --export-sample-data")
        print("\n--- 注意 ---")
        print("在运行前，请确保已安装所有依赖库（如 pandas, torch 等），并且存在 config.py 文件。")

# 执行主函数入口
if __name__ == "__main__":
    main()