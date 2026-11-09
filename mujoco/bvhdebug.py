import os

def debug_bvh_parser(file_path):
    print(f"--- 开始调试文件: {file_path} ---")
    with open(file_path, 'r') as f:
        lines = f.readlines()

    joint_count = 0
    found_offsets = 0

    # 我们直接扫描整个文件，看看抓到了多少个 OFFSET
    for i, line in enumerate(lines):
        if "JOINT" in line:
            name = line.split()[-1]
            # 检查接下来的几行
            for j in range(i+1, min(i+6, len(lines))):
                if "OFFSET" in lines[j]:
                    found_offsets += 1
                    parts = lines[j].strip().split()
                    print(f"找到关节: {name}")
                    print(f"  -> 对应的 OFFSET 行: {lines[j].strip()}")
                    print(f"  -> 解析出的数值: {parts[1:4]}")
                    break
            joint_count += 1
            if joint_count > 5: # 只打印前5个，防止刷屏
                print("... (仅显示前5个关节) ...")
                break

    print("-" * 30)
    print(f"总计识别到 JOINT 关键字数量: {joint_count}")
    print(f"总计成功抓取到 OFFSET 数值数量: {found_offsets}")

    if found_offsets == 0:
        print("!!! 警告: 没有抓取到任何 OFFSET ！！")
        print("这说明文件格式可能非常特殊，或者 OFFSET 关键字不在 JOINT 附近。")
    elif found_offsets < joint_count:
        print(f"!!! 警告: 抓取的 OFFSET 数量 ({found_offsets}) 少于关节数量 ({joint_count}) ！！")

if __name__ == "__main__":
    path = "bvhsource/alpha_pose_kunkun_cut.bvh"
    if os.path.exists(path):
        debug_bvh_parser(path)
    else:
        print("文件不存在，请检查路径。")