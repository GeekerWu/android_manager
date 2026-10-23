#!/usr/bin/env python
import sys
import os
import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# 导入硬件 SDK
sys.path.append("..")
try:
    from SCServo_Python.scservo_sdk import *
except ImportError:
    print("⚠️ 警告: 无法导入 SCServo_Python SDK，请确保 SDK 已在项目根目录或正确路径下。")

router = APIRouter(prefix="/api/servo", tags=["Servo Control"])

# --- 配置变量 (可以根据需要后续改为读取配置文件) ---
BAUDRATE                    = 115200
DEVICENAME                  = 'COM5'
SCS_MOVING_SPEED            = 2400

# --- 硬件初始化逻辑 ---
portHandler = PortHandler(DEVICENAME)
packetHandler = scscl(portHandler)
sts_packetHandler = sms_sts(portHandler)

# 全局变量用于缓存连接状态
PORT_OPENED = False

def initialize_hardware():
    global PORT_OPENED
    if not PORT_OPENED:
        if portHandler.openPort():
            print("Succeeded to open the port")
            if portHandler.setBaudRate(BAUDRATE):
                print("Succeeded to change the baudrate")
                PORT_OPENED = True
            else:
                print("Failed to change the baudrate")
        else:
            print("Failed to open the port")
    return PORT_OPENED

# --- 请求模型 ---
class PingRequest(BaseModel):
    start_id: int
    end_id: int

class WritePosRequest(BaseModel):
    id: int
    position: int
    moving_speed: int = 1

# --- 核心逻辑 ---

@router.post("/search")
def search_servos():
    """
    将 getServoStatus.py 中的 search 功能作为 API 暴露
    直接写入到 robot_manager.db 中的 servo_info 表
    """
    if not initialize_hardware():
        raise HTTPException(status_code=500, detail="Failed to initialize hardware port.")

    # 使用 sqlite3 直接操作以符合“不改 model”和“快速跑通”的要求
    db_path = "robot_manager.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 确保表存在
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servo_info (
                SERVOID INTEGER PRIMARY KEY,
                SERVO_DESC TEXT DEFAULT '',
                SERVO_TYPE TEXT,
                CURR_POSITION INTEGER,
                SLOAD INTEGER,
                VOLTAGE INTEGER,
                TEMPERATURE INTEGER,
                min_position INTEGER DEFAULT NULL,
                max_position INTEGER DEFAULT NULL,
                max_load INTEGER DEFAULT NULL
            )
        ''')

        results = []
        for SERVO_ID in range(1, 56):
            scs_model_number, scs_comm_result, scs_error = packetHandler.ping(SERVO_ID)
            if scs_comm_result == COMM_SUCCESS:
                # 判断 Servo 类型
                if scs_model_number == 1284:
                    servo_type = 'scs'
                elif scs_model_number == 2307:
                    servo_type = 'sts'
                else:
                    servo_type = 'unknown'

                # 初始化变量
                tmp, volt, load, moving, curr_pos = 0, 0, 0, 0, 0
                servo_desc = ""

                # 根据类型获取数据
                if servo_type == 'scs':
                    tmp, _, _ = packetHandler.ReadTmp(SERVO_ID)
                    volt, _, _ = packetHandler.ReadVolt(SERVO_ID)
                    load, _, _, _ = packetHandler.ReadLoad(SERVO_ID)
                    moving, _, _ = packetHandler.ReadMoving(SERVO_ID)
                    curr_pos, _, _ = packetHandler.ReadCurrPosition(SERVO_ID)
                elif servo_type == 'sts':
                    tmp, _, _ = sts_packetHandler.ReadTmp(SERVO_ID)
                    volt, _, _ = sts_packetHandler.ReadVolt(SERVO_ID)
                    load, _, _, _ = sts_packetHandler.ReadLoad(SERVO_ID)
                    moving, _, _ = sts_packetHandler.ReadMoving(SERVO_ID)
                    curr_pos, _, _ = sts_packetHandler.ReadCurrPosition(SERVO_ID)

                # 执行 SQL 写入 (保持原逻辑)
                sql = """
                INSERT INTO servo_info (SERVOID, SERVO_DESC, SERVO_TYPE, CURR_POSITION, SLOAD, VOLTAGE, TEMPERATURE)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(SERVOID) DO UPDATE SET
                    SERVO_TYPE=excluded.SERVO_TYPE,
                    CURR_POSITION=excluded.CURR_POSITION,
                    SLOAD=excluded.SLOAD,
                    VOLTAGE=excluded.VOLTAGE,
                    TEMPERATURE=excluded.TEMPERATURE;
                """
                data = (SERVO_ID, servo_desc, servo_type, curr_pos, load, volt, tmp)
                cursor.execute(sql, data)
                results.append(data)

        conn.commit()
        return {"status": "success", "scanned_count": len(results), "data": results}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/ping")
def ping_servos(request: PingRequest):
    """
    将 getServoStatus.py 中的 p 参数逻辑作为 API 暴露
    遍历指定范围的 ID 进行 ping 扫描并返回详细数据
    """
    if not initialize_hardware():
        raise HTTPException(status_code=500, detail="Failed to initialize hardware port.")

    results = []
    for servo_ID in range(request.start_id, request.end_id):
        scs_model_number, scs_comm_result, scs_error = packetHandler.ping(servo_ID)
        if scs_comm_result == COMM_SUCCESS:
            # 判断 Servo 类型
            if scs_model_number == 1284:
                servo_type = 'scs'
            elif scs_model_number == 2307:
                servo_type = 'sts'
            else:
                servo_type = 'unknown'

            # 获取详细数据（复用与 search 相同的逻辑）
            tmp, volt, load, moving, curr_pos = 0, 0, 0, 0, 0
            if servo_type == 'scs':
                tmp, _, _ = packetHandler.ReadTmp(servo_ID)
                volt, _, _ = packetHandler.ReadVolt(servo_ID)
                load, _, _, _ = packetHandler.ReadLoad(servo_ID)
                moving, _, _ = packetHandler.ReadMoving(servo_ID)
                curr_pos, _, _ = packetHandler.ReadCurrPosition(servo_ID)
            elif servo_type == 'sts':
                tmp, _, _ = sts_packetHandler.ReadTmp(servo_ID)
                volt, _, _ = sts_packetHandler.ReadVolt(servo_ID)
                load, _, _, _ = sts_packetHandler.ReadLoad(servo_ID)
                moving, _, _ = sts_packetHandler.ReadMoving(servo_ID)
                curr_pos, _, _ = sts_packetHandler.ReadCurrPosition(servo_ID)

            results.append({
                "id": servo_ID,
                "type": servo_type,
                "model": scs_model_number,
                "tmp": tmp,
                "volt": volt,
                "load": load,
                "moving": moving,
                "curr_pos": curr_pos
            })

    return {"status": "success", "pinged_count": len(results), "data": results}

@router.post("/write")
def write_servo(request: WritePosRequest):
    """
    将 getServoStatus.py 中的 w 操作作为 API 暴露
    执行 WritePos 指令到指定的舵机
    """
    if not initialize_hardware():
        raise HTTPException(status_code=500, detail="Failed to initialize hardware port.")

    # 调用 SDK 执行写入
    # 参数顺序: id, position, speed_mode (0), moving_speed
    scs_comm_result, scs_error = packetHandler.WritePos(request.id, request.position, 0, request.moving_speed)

    if scs_comm_result != COMM_SUCCESS:
        raise HTTPException(status_code=500, detail=f"Write failed: {packetHandler.getTxRxResult(scs_comm_result)}")    
    if scs_error != 0:
        raise HTTPException(status_code=500, detail=f"SDK Error: {packetHandler.getRxPacketError(scs_error)}")

    return {"status": "success", "id": request.id, "position": request.position}
