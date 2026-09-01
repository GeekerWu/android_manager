# android_manager/backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 使用SQLite作为数据库引擎
SQLALCHEMY_DATABASE_URL = "sqlite:///./robot_manager.db"

# 创建引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 定义基础声明基类
Base = declarative_base()

# -----------------------------------------------------------
# 创建会话工厂 (Session Factory)：
# 这个工厂负责生成数据库会话对象，并且集成了性能优化和健壮性增强参数。
# -----------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,  # ⚠️ 禁用自动提交：每次更改都需要显式调用 session.commit() 来提交，保证事务原子性。
    autoflush=True,   # ⚠️ 禁用自动刷新：精确控制数据何时从本地缓存推送到数据库。
    bind=engine      # 绑定到已定义的数据库引擎。
)

# 依赖函数：用于获取数据库Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print("✅ 数据库连接和基础结构文件 (database.py) 已创建。")