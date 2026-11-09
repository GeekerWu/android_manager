import numpy as np
from scipy.spatial.transform import Rotation as R

def parse_bvh(file_path):
    """解析 BVH 文件。解析阶段保持纯粹，最后统一验证一致性。"""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    joint_map = {}
    motion_data = []

    # 1. 解析关节基础数据
    for i, line in enumerate(lines):
        line_strip = line.strip()
        if "MOTION" in line_strip:
            break

        if line_strip.startswith("JOINT") or line_strip.startswith("ROOT"):
            # 提取名字：如 "ROOT Hips" -> "Hips"
            parts = line_strip.split()
            if len(parts) < 2:
                continue
            name = parts[1]

            offset = None
            channels = None

            # 严格在当前关节块内寻找属性
            for next_i in range(i + 1, min(i + 11, len(lines))):
                next_line = lines[next_i].strip()
                if next_line.startswith("JOINT") or next_line.startswith("ROOT") or "MOTION" in next_line:
                    break
                if "OFFSET" in next_line:
                    parts = next_line.split()
                    offset = np.array([float(x) for x in parts[1:4]])
                elif "CHANNELS" in next_line:
                    # 修复：跳过开头的数字计数，例如 "6 Xposition..." -> ["Xposition", ...]
                    channels = next_line.split()[2:]

            if offset is None:
                raise ValueError(f"解析错误：在关节 '{name}' 块中未找到 OFFSET。")
            if channels is None:
                raise ValueError(f"解析错误：在关节 '{name}' 块中未找到 CHANNELS。")

            joint_map[name] = {
                "name": name,
                "offset": offset,
                "channels": channels,
                "parent": None,
                "children": [],
                "data_index": None
            }
            print(f"DEBUG: Parsed Joint '{name}' with {len(channels)} channels.")

    # 2. 建立层级关系
    parent_map = {
        "RightLeg": "RightUpLeg",
        "RightFoot": "RightLeg",
        "LeftLeg": "LeftUpLeg",
        "LeftFoot": "LeftLeg",
        "RightForeArm": "RightArm",
        "RightHand": "RightForeArm",
        "LeftForeArm": "LeftArm",
        "LeftHand": "LeftForeArm",
        "Spine": "Hips",
        "Neck": "Spine",
        "Head": "Neck",
        "RightUpLeg": "Hips",
        "LeftUpLeg": "Hips",
        "Spine3": "Spine",
        "RightArm": "Spine",
        "LeftArm": "Spine",
    }

    for name, j in joint_map.items():
        parent_name = parent_map.get(name)
        if parent_name and parent_name in joint_map:
            j["parent"] = joint_map[parent_name]
            joint_map[parent_name]["children"].append(j)

    # 3. 提取运动数据
    motion_start_idx = -1
    for idx, line in enumerate(lines):
        if "MOTION" in line:
            motion_start_idx = idx
            break

    if motion_start_idx != -1:
        frame_start_idx = motion_start_idx + 3
        raw_frames = []
        for idx in range(frame_start_idx, len(lines)):
            line = lines[idx].strip()
            if not line: continue
            try:
                vals = [float(x) for x in line.split()]
                if len(vals) > 0: raw_frames.append(vals)
            except ValueError:
                raise ValueError(f"数据损坏：在 MOTION 块中发现无法解析的数值，行号: {idx}")
        motion_data = raw_frames

    if not motion_data:
        raise ValueError("数据错误：MOTION 块为空。")

    # 4. 统一验证阶段
    all_children_names = set()
    for j in joint_map.values():
        for child in j["children"]:
            all_children_names.add(child["name"])

    potential_roots = [j for name, j in joint_map.items() if name not in all_children_names]

    if len(potential_roots) != 1:
        raise ValueError(f"逻辑错误：数据结构不合理。识别到 {len(potential_roots)} 个根节点。必须且只能有一个根节点。")

    root_joint = potential_roots[0]
    print(f"[DEBUG] 识别到唯一根节点: {root_joint['name']}")

    # 检查孤立节点
    for name, j in joint_map.items():
        if name != root_joint["name"] and j["parent"] is None:
            raise ValueError(f"逻辑错误：数据结构不合理。发现孤立节点 {name}（既不是根节点也没有挂载到任何父节点下）。")

    # 分配索引并检查维度一致性
    current_pos = 0
    def walk_final(j):
        nonlocal current_pos
        j["data_index"] = current_pos
        current_pos += len(j["channels"])
        for child in j["children"]:
            walk_final(child)

    walk_final(root_joint)

    expected_channels = sum(len(j["channels"]) for j in joint_map.values())
    actual_channels = len(motion_data[0])
    print(f"DEBUG: Expected total channels: {expected_channels}")
    print(f"DEBUG: Actual motion data dimensions: {actual_channels}")

    if expected_channels != actual_channels:
        raise ValueError(f"数据不一致：关节定义的总通道数 {expected_channels} 与 MOTION 数据每帧维度 {actual_channels} 不匹配。")

    # 打印树形结构
    def print_tree(joint, indent=""):
        print(f"{indent}└── {joint['name']} ({len(joint['channels'])} channels)")
        for child in joint["children"]:
            print_tree(child, indent + "    ")

    print("\n--- 骨骼层级树结构 ---")
    print_tree(root_joint)
    print("-" * 30)

    return root_joint, joint_map, motion_data

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="BVH Parser Test")
    parser.add_argument("file", nargs="?", default="bvhsource/alpha_pose_kunkun_cut.bvh", help="Path to the BVH file")
    args = parser.parse_args()

    print(f"--- 开始解析文件: {args.file} ---")
    try:
        root, joint_map, motion_data = parse_bvh(args.file)
        print(f"✅ 解析成功！")
        print(f"根节点: {root['name']}")
        print(f"总帧数: {len(motion_data)}")
        print(f"总关节数: {len(joint_map)}")
    except Exception as e:
        print(f"❌ 解析失败！\n错误信息: {e}")
