#!/usr/bin/env python
import sys
import os
import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel,Field
from typing import Dict, Any, Optional

# 导入硬件 SDK
sys.path.append("..")
try:
    from SCServo_Python.scservo_sdk import *
except ImportError:
    print("⚠️ 警告: 无法导入 SCServo_Python SDK，请确保 SDK 已在项目根目录或正确路径下。")

router = APIRouter(prefix="/api/servo", tags=["Servo Control"])

# --- 配置变量 ---
BAUDRATE                    = 115200
DEVICENAME                  = 'COM5'
SCS_MOVING_SPEED            = 2400

# --- 硬件初始化逻辑 ---
portHandler = PortHandler(DEVICENAME)
packetHandler = scscl(portHandler)
sts_packetHandler = sms_sts(portHandler)

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
    id: int = Field(
          ...,
          description="舵机 ID (例如: 1, 2, 3...)"
      )
    position: int = Field(
          ...,
          description="目标位置 (范围取决于数据库中记录的 min_position 和 max_position)"
      )
    moving_speed: int = Field(
        1,
        description="移动速度 (单位通常为 mm/s 或对应 SDK 的速度单位)"
    )
    SMS_STS_ACC: int = Field(
        15,
        description="SMS/STS 系列舵机的加速度值 (Acceleration)，默认 15。用于控制启动和停止时的平滑度。"
                             
                             )  # 默认加速度值，可根据需要调整

# --- 私有辅助函数 (重构核心) ---

def _get_servo_data(servo_id: int) -> Optional[Dict[str, Any]]:
    """
    核心逻辑提取：统一处理 Ping、模型识别、类型判断及数据读取。
    返回包含所有核心参数的字典，若通信失败则返回 None。
    """
    scs_model_number, scs_comm_result, scs_error = packetHandler.ping(servo_id)
    if scs_comm_result != COMM_SUCCESS:
        return None

    # 模型识别
    if scs_model_number == 1284:
        servo_type = 'scs'
    elif scs_model_number == 2307:
        servo_type = 'sts'
    else:
        servo_type = 'unknown'

    # 根据类型选择处理器并读取数据
    tmp, volt, load, moving, curr_pos = 0, 0, 0, 0, 0

    if servo_type == 'scs':
        tmp, _, _ = packetHandler.ReadTmp(servo_id)
        volt, _, _ = packetHandler.ReadVolt(servo_id)
        load, _, _, _ = packetHandler.ReadLoad(servo_id)
        moving, _, _ = packetHandler.ReadMoving(servo_id)
        curr_pos, _, _ = packetHandler.ReadCurrPosition(servo_id)
    elif servo_type == 'sts':
        tmp, _, _ = sts_packetHandler.ReadTmp(servo_id)
        volt, _, _ = sts_packetHandler.ReadVolt(servo_id)
        load, _, _, _ = sts_packetHandler.ReadLoad(servo_id)
        moving, _, _ = sts_packetHandler.ReadMoving(servo_id)
        curr_pos, _, _ = sts_packetHandler.ReadCurrPosition(servo_id)

    return {
        "id": servo_id,
        "model": scs_model_number,
        "type": servo_type,
        "tmp": tmp,
        "volt": volt,
        "load": load,
        "moving": moving,
        "curr_pos": curr_pos
    }

# --- 公共 API 接口 ---

@router.post("/search")
def search_servos():
    """扫描 ID 1-55 并持久化到数据库"""
    if not initialize_hardware():
        raise HTTPException(status_code=500, detail="Failed to initialize hardware port.")

    db_path = "robot_manager.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
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
        for s_id in range(1, 56):
            data = _get_servo_data(s_id)
            if data:
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
                # 保持与原逻辑一致的数据元组顺序
                # data 字典包含: id, model, type, tmp, volt, load, moving, curr_pos
                db_data = (data['id'], "", data['type'], data['curr_pos'], data['load'], data['volt'], data['tmp'])
                cursor.execute(sql, db_data)
                results.append(db_data)

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
    """遍历范围并返回详细数据"""
    if not initialize_hardware():
        raise HTTPException(status_code=500, detail="Failed to initialize hardware port.")

    results = []
    for s_id in range(request.start_id, request.end_id):
        data = _get_servo_data(s_id)
        if data:
            results.append(data)

    return {"status": "success", "pinged_count": len(results), "data": results}

@router.post("/write")
def write_servo(request: WritePosRequest):
    """基于数据库校验的增强版写入接口"""
    if not initialize_hardware():
        raise HTTPException(status_code=500, detail="Failed to initialize hardware port.")

    db_path = "robot_manager.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. 校验 ID 有效性
        cursor.execute(
            "SELECT SERVO_TYPE, min_position, max_position FROM servo_info WHERE SERVOID = ?",
            (request.id,)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Servo ID {request.id} not found in database.")

        servo_type, min_pos, max_pos = row

        # 2. 校验位置范围
        if not (min_pos <= request.position <= max_pos):
            raise HTTPException(
                status_code=400,
                detail=f"Position {request.position} out of range [{min_pos}, {max_pos}] for ID {request.id}."
            )

        # 3. 分发处理器执行
        scs_comm_result, scs_error = None, None
        if servo_type == 'scs':
            scs_comm_result, scs_error = packetHandler.WritePos(request.id, request.position, 0, request.moving_speed)
        elif servo_type == 'sts':
            # STS 需要额外的加速度参数
            scs_comm_result, scs_error = sts_packetHandler.WritePosEx(request.id, request.position,request.moving_speed,request.SMS_STS_ACC)
        else:
            raise HTTPException(status_code=500, detail=f"Unknown servo type '{servo_type}' for ID {request.id}.")

        # 4. 处理结果
        if scs_comm_result != COMM_SUCCESS:
            raise HTTPException(status_code=500, detail=f"Write failed: {packetHandler.getTxRxResult(scs_comm_result)}")
        if scs_error != 0:
            raise HTTPException(status_code=500, detail=f"SDK Error: {packetHandler.getRxPacketError(scs_error)}")

        return {
            "status": "success",
            "id": request.id,
            "position": request.position,
            "type": servo_type
        }

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()