# android_manager/backend/main.py
import argparse
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import Base, engine

# =================================================================
# ⚙️ 配置变量
# =================================================================
# 端口号和配置参数将从命令行传入，这里只保留默认值作为备用。
DEFAULT_PORT = 8001
# ... (其他代码保持不变)
# =================================================================

# 导入所有模型（假设存在）
from models import Robot, Component, ControlJob, TelemetryLog

# 从 security 模块引入认证和JWT工具
from security import (
    get_current_user,
    create_access_token,
    get_user_credentials,
    HTTPException,
    status
)

# =================================================================
# 1. 初始化 (Initialization)
# =================================================================
# ⚠️ 核心修改：应用程序实例的创建和所有配置（CORS, Middleware, Router Inclusion）
# 全部在全局作用域完成，确保 FastAPI 框架在启动时能够一次性完整扫描所有路由和中间件。
app = FastAPI(title="Android Manager API", description="机器人状态监控与控制API")

# 3. 配置 CORS 中间件 (关键步骤)
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # 允许的来源列表
    allow_credentials=True,         # 允许携带 Cookie 和认证凭证
    allow_methods=["*"],            # 允许所有 HTTP 方法 (GET, POST, PUT, DELETE...)
    allow_headers=["*"],            # 允许所有 HTTP Header
)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """
    【全局认证中间件】：拦截所有请求，检查是否需要认证。
    注意: 此版本已根据开发需求修改为硬编码明文密钥校验，**极度不安全，仅用于开发/测试！**
    """
    # 1. 允许的公共路径
    if request.url.path in ["/login", "/docs", "/openapi.json"]:
        return await call_next(request)

    # 2. 硬编码密钥校验 (Developer Override)
    auth_header = request.headers.get("Authorization")
    HARDCODED_API_KEY = "dev_temp_secret_key_123"
    if not auth_header or auth_header != f"Bearer {HARDCODED_API_KEY}":
        # 如果没有提供 Header，或者 Header 的内容与硬编码密钥不匹配
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Using temporary hardcoded key for testing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 流程放行
    return await call_next(request)


# ----------------------------------------------------------------
# 2. 数据库初始化 (Startup Event)
# ----------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    print(f"🤖 FastAPI 启动中：正在初始化机器人管理系统 (端口: {SERVICE_PORT})...")
    try:
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db: Session = SessionLocal()

        # 检查并创建示例机器人 (逻辑保持不变)
        try:
            from models import Robot, Component # 确保导入
            existing_robot = db.query(Robot).filter(Robot.robot_sn == "SN001").first()

            if existing_robot is None:
                # 如果机器人不存在，则创建
                new_robot = Robot(robot_sn="SN001", name="主控制机", status="Online", battery_level=95.0)
                db.add(new_robot)
                db.commit()
                robot_id = new_robot.id # 假设数据库能提供 ID

                # 假设Component需要知道Robot的ID
                db.add(Component(robot_id=robot_id, component_type="Battery", value="95%", component_metadata="N/A", status="OK"))
                db.commit()
                print("✅ 示例机器人 'SN001' 已成功创建。")
            else:
                print(f"✅ 示例机器人 'SN001' 已存在，跳过创建。")
        except ImportError:
            print("⚠️ 警告：无法导入 models.py 或数据库模型，跳过数据库初始化部分。")
            
    except Exception as e:
        print(f"⚠️ 启动时初始化数据库失败: {e}")
    finally:
        db.close()

# ----------------------------------------------------------------
# 3. 登录路由 (Login Endpoint)
# ----------------------------------------------------------------
@app.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    模拟用户登录。接收用户名和密码，验证凭证，成功后生成 JWT。
    """
    print(f"🔑 登录尝试：用户名={form_data.username,} 密码={form_data.password}")
    # 1. 使用后端定义的函数进行用户凭证校验
    credentials = get_user_credentials(form_data.username, form_data.password)

    if not credentials:
        # 认证失败：用户名或密码错误
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. 登录成功：生成 JWT Token (Payload 只包含 username)
    access_token = create_access_token(data={"username": credentials["username"]})

    # 3. 返回 Token 给前端
    return {"access_token": access_token, "token_type": "bearer"}


# 4. 路由挂载 (Router Inclusion)
from api.endpoints import router as api_router
# ⭐️ 核心修改：这里所有路由都需要通过get_current_user 进行保护
# 注意：我们在路由装饰器上添加 Depends(get_current_user) 来保护业务路由
app.include_router(api_router, prefix="/api", dependencies=[Depends(get_current_user)])


def main(args):
    """
    主启动函数：解析命令行参数，设置配置，并启动 FastAPI 应用。
    """
    global SERVICE_PORT
    SERVICE_PORT = args.port

    # ⚠️ 注意：这里不再重新实例化 app，因为所有配置已在全局作用域完成。
    # 我们只需要启动它。
    print("===================================================")
    print(f"🚀 服务已配置为通过脚本启动。")
    print(f"🚀 监听地址: 0.0.0.0:{SERVICE_PORT}")
    print("===================================================")
    # 启动 Uvicorn，因为它能感知全局作用域已经设置好的 app 实例。
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Android Manager Backend Service Launcher.")
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"API 服务的运行端口号 (Default: {DEFAULT_PORT})."
    )
    args = parser.parse_args()
    main(args)