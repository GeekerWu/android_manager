# android_manager/backend/main.py
import argparse
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
import argparse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
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
    OAuth2PasswordBearer,
    get_user_credentials,
    get_current_user,
    HTTPException,
    status
)

# =================================================================
# 1. 初始化与中间件设置 (Middleware)
# =================================================================
app = FastAPI(title="Android Manager API", description="机器人状态监控与控制API")

# 3. 配置 CORS 中间件 (关键步骤)
# ⚠️ 注意：'http://localhost:8088' 必须是您的前端应用实际运行的地址。
# 端口现在通过 SERVICE_PORT 变量进行控制，但 CORS 仍然需要手动维护允许的来源列表。
origins = [
    # "http://localhost:8088",  # 允许您的前端应用访问
    # 如果您在开发或测试时，需要允许所有来源，可以使用 "*"
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
    这是保护 /docs 和所有其他路由的全局防御层。
    """
    # 1. 允许的公共路径：登录和文档本身（用于查看文档，我们不拦截它）
    if request.url.path in ["/login", "/docs", "/openapi.json"]:
        return await call_next(request)

    # 2. 检查 Token 的存在性
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # 未携带 Token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing or invalid Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 增强的 Token 校验（模拟）
    # ⚠️ 实际生产中，这里需要调用安全函数来解密JWT，并检查Token的过期时间、签名等。
    try:
        # 绕过复杂的中间件逻辑，我们依赖 get_current_user 依赖函数来处理这个 Token 校验，
        # 这样更符合 FastAPI 的依赖注入模型。
        # 对于Middleware，我们只做前置检查，依赖函数处理业务逻辑。
        # 此处仅做占位，实际的校验会由下游的依赖函数处理，防止过早抛出 401。
        pass
    except Exception:
        # 如果校验失败，Middleware 应该抛出异常，但在 FastAPI 的结构下，通常的做法是依赖函数处理。
        pass

    # 流程放行：让请求继续到下一个处理程序
    return await call_next(request)


# ----------------------------------------------------------------
# 2. 启动事件与数据库初始化 (Startup Event)
# ----------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    print(f"🤖 FastAPI 启动中：正在初始化机器人管理系统 (端口: {SERVICE_PORT})...")
    try:
        from sqlalchemy.orm import sessionmaker
        # 注意：此处需要使用从 database.py 导入的 SessionLocal
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db: Session = SessionLocal()

        # 检查并创建示例机器人 (逻辑保持不变)
        existing_robot = db.query(Robot).filter(Robot.robot_sn == "SN001").first()

        if existing_robot is None:
            # 如果机器人不存在，则创建
            db.add(Robot(robot_sn="SN001", name="主控制机", status="Online", battery_level=95.0))
            db.commit()

            # 假设ID=1是本次首次运行的ID。
            db.add(Component(robot_id=1, component_type="Battery", value="95%", component_metadata="N/A", status="OK"))
            db.commit()
            print("✅ 示例机器人 'SN001' 已成功创建。")
        else:
            print(f"✅ 示例机器人 'SN001' 已存在，跳过创建。")

        db.close()
    except Exception as e:
        print(f"⚠️ 启动时初始化数据库失败: {e}")

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
app.include_router(api_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])

def main(args):
    """
    主启动函数：解析命令行参数，设置配置，并启动 FastAPI 应用。
    """
    global SERVICE_PORT
    SERVICE_PORT = args.port

    # 重新设置 FastAPI 实例，确保所有依赖和中间件都基于新的端口上下文
    app = FastAPI(title="Android Manager API", description="机器人状态监控与控制API")

    # 3. 配置 CORS 中间件 (关键步骤)
    origins = [
        "*", # ⚠️ 注意：生产环境中应替换为实际的前端源
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,          # 允许的来源列表
        allow_credentials=True,         # 允许携带 Cookie 和认证凭证
        allow_methods=["*"],            # 允许所有 HTTP 方法 (GET, POST, PUT, DELETE...)
        allow_headers=["*"],            # 允许所有 HTTP Header
    )

    # 重新挂载中间件，确保其覆盖新的 app 实例
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        """
        【全局认证中间件】：拦截所有请求，检查是否需要认证。
        """
        # 1. 允许的公共路径
        if request.url.path in ["/login", "/docs", "/openapi.json"]:
            return await call_next(request)

        # 2. 检查 Token 的存在性
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Missing or invalid Authorization header.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. 流程放行
        return await call_next(request)

    # 重新设置 startup 事件
    @app.on_event("startup")
    async def startup_event():
        print(f"🤖 FastAPI 启动中：正在初始化机器人管理系统 (端口: {SERVICE_PORT})...")
        try:
            from sqlalchemy.orm import sessionmaker
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db: Session = SessionLocal()

            # 检查并创建示例机器人 (逻辑保持不变)
            # 注意：这里假设模型类 Robot, Component 已被正确导入
            try:
                from models import Robot, Component # 确保导入
                existing_robot = db.query(Robot).filter(Robot.robot_sn == "SN001").first()

                if existing_robot is None:
                    # 如果机器人不存在，则创建
                    # ⚠️ 需注意：如果此处依赖 ID=1 的创建，需要更复杂的逻辑来获取新创建的 ID。
                    # 为保持与原逻辑一致性，假设 Robot 创建后，其 ID 是本次会话的焦点。
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
    # 启动服务器
    print("===================================================")
    print(f"🚀 服务已配置为通过脚本启动。")
    print(f"🚀 监听地址: 0.0.0.0:{SERVICE_PORT}")
    print("===================================================")
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