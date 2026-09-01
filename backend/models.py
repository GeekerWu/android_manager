# android_manager/backend/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Robot(Base):
    __tablename__ = "robots"
    id = Column(Integer, primary_key=True, index=True)
    robot_sn = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True)
    status = Column(String, default="Offline")
    battery_level = Column(Float, default=95.0)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)

    # 关系：一个机器人可以有多个组件/设备记录
    components = relationship("Component", back_populates="robot")

    # ***【最关键的修复点】***: 必须在这里声明关系，让 SQLAlchemy 知道这个关联存在。
    telemetry_logs = relationship("TelemetryLog", back_populates="robot")


class Component(Base):
    __tablename__ = "components"
    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(Integer, ForeignKey("robots.id"))
    component_type = Column(String, nullable=False)
    value = Column(String)
    component_metadata = Column(String) # 修复了关键字冲突
    status = Column(String, default="OK")

    robot = relationship("Robot", back_populates="components")

class ControlJob(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(Integer, ForeignKey("robots.id"))
    job_name = Column(String, index=True)
    description = Column(String)
    status = Column(String, default="Pending")
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    log_data = Column(String, nullable=True)

# ***【新增】历史状态和遥测记录表***
class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"
    id = Column(Integer, primary_key=True)
    robot_id = Column(Integer, ForeignKey("robots.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String) # 记录发生状态 (Online, Offline, Error, Moving)
    battery_level = Column(Float) # 记录该时间点的电池电量
    log_detail = Column(String)  # 记录其他详细信息，如哪个组件告警了

    # 关键点：回指关系，让 SQLAlchemy 知道这个日志属于哪个机器人
    robot = relationship("Robot", back_populates="telemetry_logs")

print("✅ 数据库模型文件 (models.py) 已最终修复，添加了 Robot 模型中的 'telemetry_logs' 关系。")