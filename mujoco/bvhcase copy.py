import numpy as np
from scipy.spatial.transform import Rotation as R
import os

# --- Configuration ---
# 验证您要求的角度：RightUpLeg -> RightLeg -> RightFoot
MONITOR_ANGLE = ("RightUpLeg", "RightLeg", "RightFoot")

def parse_bvh(file_path):
    """强力解析 BVH 文件：动态识别根节点并建立层级结构。"""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    joint_map = {}
    root_joint = None
    motion_data = []

    # 1. 寻找 HIERARCHY 块
    hier_idx = -1
    for i, line in enumerate(lines):
        if "HIERARCHY" in line:
            hier_idx = i
            break

    if hier_idx == -1:
        return None, {}, []

    # 2. 线性遍历每一行，确保不漏掉任何关键字（解决 alpha_pose 格式错位问题）
    for i, line in enumerate(lines):
        line_strip = line.strip()
        if "MOTION" in line_strip:
            break

        if line_strip.startswith("JOINT"):
            name = line_strip.split()[-1]

            # 初始默认值
            offset = np.array([0.0, 0.0, 0.0])
            channels = []

            # 核心改动：在 JOINT 行之后的 10 行内寻找 OFFSET 和 CHANNELS
            # 这样即使中间有空行、注释或复杂的嵌套，也能准确抓取到数据
            for next_i in range(i + 1, min(i + 11, len(lines))):
                next_line = lines[next_i].strip()
                if "OFFSET" in next_line:
                    parts = next_line.split()
                    offset = np.array([float(x) for x in parts[1:4]])
                    # print(f"DEBUG: 关节 {name} 抓取到的 Offset 内容是: {offset}，来自文件第 {next_i} 行: {next_line.strip()}")
                    break
                if "CHANNELS" in next_line:
                    channels = next_line.split()[1:]
                    break

            new_j = {
                "name": name,
                "offset": offset,
                "channels": channels,
                "parent": None,
                "children": [],
                "global_offset": np.zeros(3),
                "global_rot": R.identity(),
                "data_index": None
            }
            joint_map[name] = new_j
    # 3. 自动重建树结构
    # 规则：在 BVH 中，父节点通常出现在子节点之前。
    # 我们建立一个简单的关联：如果一个关节被识别为父节点，它会包含子节点。
    # 对于 alpha_pose，如果层级复杂，我们确保所有节点至少挂在 root 上。
     # 3. 修正树结构 (手动定义核心骨骼的父子关系)
    if joint_map:
        # 定义父子关系映射：{子节点: 父节点}
        # 这里的映射是根据 alpha_pose/Mixamo 常见的层级逻辑确定的
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
            "RightUpLeg": "Pelvis", # 如果 Pelvis 存在，否则挂在 Hips 下
            "LeftUpLeg": "Pelvis",
        }

        # 确定根节点
        root_joint = joint_map.get("Hips") or joint_map.get("Pelvis") or next(iter(joint_map.values()))

        # 建立层级
        for name, j in joint_map.items():
            if name == root_joint["name"]:
                continue

            # 优先匹配手动定义的父子关系
            parent_name = parent_map.get(name)
            if parent_name and parent_name in joint_map:
                j["parent"] = joint_map[parent_name]
                joint_map[parent_name]["children"].append(j)
            else:
                # 如果没在映射里，且还没父节点，则挂载到根节点下（作为兜底）
                if j["parent"] is None:
                    j["parent"] = root_joint
                    root_joint["children"].append(j)
   
    # 4. 解析 MOTION 数据
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
            except ValueError: break
        motion_data = raw_frames

        # 分配数据索引
        current_pos = 0
        def walk_final(j):
            nonlocal current_pos
            j["data_index"] = current_pos
            current_pos += len(j["channels"])
            for child in j["children"]:
                walk_final(child)

        if root_joint:
            walk_final(root_joint)
    # print(f"joint_map:", joint_map["RightUpLeg"]["offset"])
    return root_joint, joint_map, motion_data

def calculate_angle(p1, p2, p3):
    v1 = p1 - p2
    v2 = p3 - p2
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 < 1e-6 or norm2 < 1e-6: return 0.0
    cosine_angle = np.dot(v1, v2) / (norm1 * norm2)
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    return np.degrees(np.arccos(cosine_angle))

def main():
    # 注意：请确保路径正确
    bvh_path = "bvhsource/alpha_pose_kunkun_cut.bvh"
    if not os.path.exists(bvh_path):
        print(f"文件未找到: {bvh_path}")
        return

    print(f"正在加载 {bvh_path}...")
    root, joint_map, motion_data = parse_bvh(bvh_path)
    # print(' joint_map["RightUpLeg"]["offset"]',  joint_map["RightUpLeg"]["offset"])
    # print('motion_data', motion_data)
    if not motion_data:
        print("在文件中未发现运动数据。")
        return

    num_frames = len(motion_data)
    print(f"识别到 {num_frames} 帧动画。总识别关节数: {len(joint_map)}")
    if root:
        print(f"识别到的根节点为: {root['name']}")
    else:
        print("未能识别到根节点。")
    print(f"识别到的所有关节: {list(joint_map.keys())}")

    global_positions = {name: np.zeros((num_frames, 3)) for name in joint_map}

    print("正在计算全局变换...")
    if root:
        for f in range(num_frames):
            # 使用 BFS 确保正确计算父节点到子节点的变换
            stack = [(root, np.zeros(3), R.identity())]
            while stack:
                curr, p_pos, p_rot = stack.pop(0)

                start_idx = curr["data_index"]
                channels = curr["channels"]
                rot_vals = []
                rot_indices = [idx for idx, c in enumerate(channels) if "rotation" in c.lower()]
                # 智能解析旋转数据：兼容带 "rotation" 标签的标准 BVH 和 alpha_pose 格式
                if rot_indices:
                    rot_vals = [motion_data[f][start_idx + i] for i in rot_indices]
                else:
                    # 如果没找到 "rotation" 标签，尝试抓取前 3 或 4 个数值
                    num_vals = min(len(channels), 4)
                    if num_vals >= 3:
                        rot_vals = [motion_data[f][start_idx + i] for i in range(num_vals)]
                    else:
                        rot_vals = []

                if len(rot_vals) == 3:
                    curr_rot = R.from_euler('xyz', rot_vals)
                elif len(rot_vals) == 4:
                    if abs(rot_vals[0]) > 1.0:
                        curr_rot = R.from_quat([rot_vals[1], rot_vals[2], rot_vals[3], rot_vals[0]])
                    else:
                        curr_rot = R.from_quat(rot_vals)
                else:
                    curr_rot = R.identity()
                local_offset_rotated = p_rot.apply(curr["offset"])
                current_pos = p_pos + local_offset_rotated
                global_positions[curr["name"]][f] = current_pos

                combined_rot = p_rot * curr_rot
                for child in curr["children"]:
                    stack.append((child, current_pos, combined_rot))
    else:
        print("警告: 由于没有根节点，无法计算全局坐标。")

    # 验证监控点
    missing_joints = [j for j in MONITOR_ANGLE if j not in joint_map]
    if missing_joints:
        print(f"警告: 监控点 {missing_joints} 在 BVH 文件中不存在！")

    print(f"监控夹角: {MONITOR_ANGLE[0]} -> {MONITOR_ANGLE[1]} -> {MONITOR_ANGLE[2]}")
    print("-" * 30)

    for f in range(num_frames):
        angle = 0.0
        if all(j in global_positions for j in MONITOR_ANGLE):
            p1 = global_positions[MONITOR_ANGLE[0]][f]
            p2 = global_positions[MONITOR_ANGLE[1]][f]
            p3 = global_positions[MONITOR_ANGLE[2]][f]
            angle = calculate_angle(p1, p2, p3)
            if f % 5 == 0: # 稍微减少一点打印频率
                print(f"Frame {f:03d}: {angle:6.2f}° | {MONITOR_ANGLE[0]}: {p1}")
                print(f"                | {MONITOR_ANGLE[1]}: {p2}")
                print(f"                | {MONITOR_ANGLE[2]}: {p3}")
        else:
            if f % 5 == 0:
                print(f"Frame {f:03d}: [跳过，关键点缺失]")

if __name__ == "__main__":
    main()