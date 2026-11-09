import mujoco
import mujoco.viewer
import numpy as np
import time
print(f"Mujoco version: {mujoco.__version__}")
print(f"Viewer contents: {dir(mujoco.viewer)}")

# 直接使用相对路径，不需要写 D:\... 这一大串
MODEL_PATH = "D:/android_manager/mujoco/model/testgroup/mjcf/testgroup.xml"
# MODEL_PATH = "D:/android_manager/mujoco/model/robot_structure_real_size/mjcf/robot_structure_real_size.xml"


def main():
    # 2. 加载模型和数据
    model = mujoco.MjModel.from_xml_path(MODEL_PATH)
    # print(dir(model)) # 这会打印出模型对象所有可用的属性
    data = mujoco.MjData(model)

    # 修正后的代码：使用 model.nact 获取驱动器数量
    print(f"模型加载成功！总共有 {model.nactuator} 个可控驱动器 (Actuators)")

    # 3. 创建可视化窗口
    # 你的 XML 里有 14 个 motor，所以这里初始化一个长度为 14 的数组
    target_angles = np.zeros(model.nactuator)

    with mujoco.viewer.launch_passive(model, data) as viewer:
        print("仿真开始！按 'ESC' 键退出。")
        
        while viewer.is_running():
            # --- 【核心：你的神经网络推理插槽】 ---
            t = data.time
            # 示例：让所有的关节随时间摆动（这里只是模拟，以后换成模型推理）
            for i in range(model.nactuator):
                target_angles[i] = np.sin(t + i) * 0.5
            
            # --- 【核心：下发控制指令】 ---
            # data.ctrl 对应你的 XML 中的 <actuator> 数量
            data.ctrl[:] = target_angles

            # 4. 步进物理仿真
            mujoco.mj_step(model, data)

            # 5. 更新渲染
            viewer.sync()
            
            # 控制每秒的刷新频率
            time.sleep(0.001)

if __name__ == "__main__":
    main()
