# android_manager/backend/api/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from database import get_db
from models import Robot, Component, ControlJob, TelemetryLog # 导入所有模型

router = APIRouter()

# =============================================================
# 🤖 0. 用户认证登录 (NEW: Hardcoded Login)
# =============================================================

@router.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    【临时/Demo】硬编码登录验证。
    仅支持用户名: admin, 密码: admin。
    成功后返回固定 Token: tmp_token。
    注意: 生产环境中必须替换为完整的认证服务。
    """
    print(f"🔑 [HARDCODE] 登录尝试：用户名={form_data.username} 密码={form_data.password}")

    if form_data.username == "admin" and form_data.password == "admin":
        # 成功硬编码登录
        return {"access_token": "tmp_token", "token_type": "bearer"}
    else:
        # 认证失败
        from fastapi import status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password (Using hardcoded: admin/admin)",
            headers={"WWW-Authenticate": "Bearer"},
        )

# =============================================================
# 🧩 1. 机器人设备管理 (Robot Management)
# =============================================================

@router.get("/robots/{robot_sn}")
def get_robot_details(robot_sn: str, db: Session = Depends(get_db)):
    """根据序列号获取机器人的完整状态，包含所有组件和历史日志。"""
    robot = db.query(Robot).filter(Robot.robot_sn == robot_sn).first()
    if not robot:
        raise HTTPException(status_code=404, detail=f"Robot with SN {robot_sn} not found.")

    # 1. 获取所有组件状态
    components = db.query(Component).filter(Component.robot_id == robot.id).all()

    # 2. 获取历史日志
    history_logs = db.query(TelemetryLog).filter(TelemetryLog.robot_id == robot.id).order_by(TelemetryLog.timestamp.desc()).limit(10).all()

    # 3. 获取当前任务
    recent_job = db.query(ControlJob).filter(ControlJob.robot_id == robot.id).order_by(ControlJob.start_time.desc()).first()

    return {
        "robot": {"sn": robot.robot_sn, "name": robot.name, "status": robot.status, "battery": robot.battery_level},
        "components": [{"type": c.component_type, "value": c.value, "status": c.status} for c in components],
        "history_logs": [{"timestamp": h.timestamp.isoformat(), "status": h.status, "battery": h.battery_level, "detail": h.log_detail} for h in history_logs],
        "current_job": {"id": recent_job.id, "name": recent_job.job_name, "status": recent_job.status} if recent_job else None
    }

# =============================================================
# 🚀 2. 实时心跳与状态同步 (Telemetry & Heartbeat)
# =============================================================

@router.post("/robots/heartbeat")
def record_heartbeat(robot_sn: str, status: str, battery: float, component_data: dict = None, db: Session = Depends(get_db)):
    """
    机器人定时上报：更新状态，电量，并记录本次心跳的日志。
    """
    robot = db.query(Robot).filter(Robot.robot_sn == robot_sn).first()
    if not robot:
        raise HTTPException(status_code=404, detail=f"Robot with SN {robot_sn} not found.")

    # --- 核心修改点：日志记录 ---
    # 1. 准备本次心跳的日志数据
    log_detail = f"Online/Status: {status} | Battery: {battery:.1f}%"

    # 2. 创建并保存历史记录 (TelemetryLog)
    new_log = TelemetryLog(
        robot_id=robot.id,
        status=status,
        battery_level=battery,
        log_detail=log_detail
    )
    db.add(new_log)

    # 3. 更新机器人基础状态
    robot.status = status
    robot.battery_level = battery
    robot.last_heartbeat = datetime.utcnow()

    # 4. 更新组件状态
    if component_data:
        for comp_type, value in component_data.items():
            component = db.query(Component).filter(Component.robot_id == robot.id, Component.component_type == comp_type).first()
            if component:
                component.value = str(value)
                component.status = "OK"
            else:
                # 如果组件不存在，则创建一个新的组件记录
                db.add(Component(robot_id=robot.id, component_type=comp_type, value=str(value), component_metadata="N/A"))
        db.commit()
        return {"message": f"Heartbeat and {len(component_data)} components updated successfully. Log created."}
    else:
        db.commit()
        return {"message": f"Heartbeat recorded successfully. Log created."}

# =============================================================
# 🛠️ 3. 健康检查 API (NEW)
# =============================================================

@router.get("/health")
def get_system_health(db: Session = Depends(get_db)):
    """系统健康检查，返回当前的系统全局状态，包括一个默认的电池电量占位符。"""
    # 这里我们查询任意一个机器人（SN001）的当前电量作为“系统基线”
    robot = db.query(Robot).filter(Robot.robot_sn == "SN001").first()
    print(f"Health Check: Found robot SN001: {robot is not None}, Battery Level: {robot.battery_level if robot else 'N/A'}")
    # 检查是否找到了机器人，以提供一个默认值
    default_battery = robot.battery_level if robot else 'N/A'
    print(f"Health Check: Returning default battery level: {default_battery}")
    return {
        "status": "online",
        "service": "Android Manager Backend",
        "time": datetime.utcnow().isoformat(),
        "system_baseline": {
            "battery_level": round(default_battery, 2), # 返回默认电量占位符
            "message": "系统已启动，请检查 /api/v1/robots/SN001 获取详细状态。"
        }
    }
print("✅ RESTful API 端点骨架 (endpoints.py) 已最终修正，增加了 /login 路由。")