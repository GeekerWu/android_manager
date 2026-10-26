#!/usr/bin/env python
import sys
import os
import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- 数据库配置 ---
DB_PATH = "robot_manager.db"

router = APIRouter(prefix="/api/randompose", tags=["Random Pose Control"])

# --- 请求模型 ---

class RandomPoseBase(BaseModel):
    servo_id: int
    servo_desc: str
    servo_type: str
    mini_position: int
    max_position: int
    random_rate: float
    target_position: int

class RandomPoseCreate(RandomPoseBase):
    pass

class RandomPoseUpdate(BaseModel):
    servo_id: int
    servo_desc: Optional[str] = None
    servo_type: Optional[str] = None
    mini_position: Optional[int] = None
    max_position: Optional[int] = None
    random_rate: Optional[float] = None
    target_position: Optional[int] = None

class BatchDeleteRequest(BaseModel):
    ids: List[int]

# --- 数据库辅助函数 ---

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- 核心 API 逻辑 ---

@router.get("/search_randompose")
def search_randompose(page: int = 1, pageSize: int = 20, servo_id: Optional[int] = None):
    """获取所有随机姿态参数"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 确保表存在 (如果尚未创建)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ui_random_pose_parameter (
                servo_id INTEGER PRIMARY KEY,
                servo_desc TEXT DEFAULT '',
                servo_type TEXT,
                mini_position INTEGER DEFAULT 0,
                max_position INTEGER DEFAULT 0,
                random_rate REAL DEFAULT 0.0,
                target_position INTEGER DEFAULT 0
            )
        ''')

        offset = (page - 1) * pageSize
        if servo_id:
            query = "SELECT * FROM ui_random_pose_parameter WHERE servo_id = ? LIMIT ? OFFSET ?"
            params = [servo_id, pageSize, offset]
        else:
            query = "SELECT * FROM ui_random_pose_parameter LIMIT ? OFFSET ?"
            params = [pageSize, offset]

        cursor.execute(query, params)
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]

        return {
            "code": 200,
            "message": "success",
            "data": data
        }
    except Exception as e:
        return {"code": 500, "message": str(e)}
    finally:
        conn.close()

@router.get("/getdropdown_randompose")
def get_dropdown_randompose():
    """获取所有电机列表（从 servo_info 表中获取描述）"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 假设 servo_info 表由 servo_service.py 维护
        cursor.execute("SELECT SERVOID as id, SERVO_DESC as name FROM servo_info")
        rows = cursor.fetchall()
        data = [{"id": row["id"], "name": row["name"]} for row in rows]

        return {
            "code": 200,
            "message": "success",
            "data": data
        }
    except Exception as e:
        return {"code": 500, "message": str(e)}
    finally:
        conn.close()

@router.post("/add_randompose")
def add_randompose(item: RandomPoseCreate):
    """创建新记录"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """
        INSERT INTO ui_random_pose_parameter
        (servo_id, servo_desc, servo_type, mini_position, max_position, random_rate, target_position)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(servo_id) DO UPDATE SET
            servo_desc=excluded.servo_desc,
            servo_type=excluded.servo_type,
            mini_position=excluded.mini_position,
            max_position=excluded.max_position,
            random_rate=excluded.random_rate,
            target_position=excluded.target_position;
        """
        cursor.execute(sql, (
            item.servo_id,
            item.servo_desc,
            item.servo_type,
            item.mini_position,
            item.max_position,
            item.random_rate,
            item.target_position
        ))
        conn.commit()

        return {
            "code": 200,
            "message": "success",
            "data": item.dict()
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.post("/edit_randompose/")
def edit_randompose(item: RandomPoseUpdate):
    """更新特定记录"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        fields = []
        params = []

        if item.servo_desc is not None:
            fields.append("servo_desc = ?")
            params.append(item.servo_desc)
        if item.servo_type is not None:
            fields.append("servo_type = ?")
            params.append(item.servo_type)
        if item.mini_position is not None:
            fields.append("mini_position = ?")
            params.append(item.mini_position)
        if item.max_position is not None:
            fields.append("max_position = ?")
            params.append(item.max_position)
        if item.random_rate is not None:
            fields.append("random_rate = ?")
            params.append(item.random_rate)
        if item.target_position is not None:
            fields.append("target_position = ?")
            params.append(item.target_position)

        params.append(item.servo_id) # WHERE 条件

        if not fields:
            return {"code": 200, "message": "No fields to update"}

        sql = f"UPDATE ui_random_pose_parameter SET {', '.join(fields)} WHERE servo_id = ?"
        cursor.execute(sql, params)
        conn.commit()

        return {
            "code": 200,
            "message": "success",
            "data": item.dict()
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.post("/delete_randompose")
def delete_randompose(request: BatchDeleteRequest):
    """批量移除记录"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if not request.ids:
            return {"code": 200, "message": "success", "data": True}

        placeholders = ", ".join(["?"] * len(request.ids))
        sql = f"DELETE FROM ui_random_pose_parameter WHERE servo_id IN ({placeholders})"

        cursor.execute(sql, request.ids)
        conn.commit()

        return {
            "code": 200,
            "message": "success",
            "data": True
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
