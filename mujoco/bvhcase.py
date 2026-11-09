from bvh_parser import parse_bvh
import numpy as np
from scipy.spatial.transform import Rotation as R
import os

# --- Configuration ---
# 验证您要求的角度：RightUpLeg -> RightLeg -> RightFoot
MONITOR_ANGLE = ("RightUpLeg", "RightLeg", "RightFoot")

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