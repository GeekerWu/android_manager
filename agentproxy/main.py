# agentproxy/main.py

import uvicorn
import argparse
import sys
import argparse
import sys
from fastapi import FastAPI
from endpoints import router # 使用绝对导入
# 注意：由于所有依赖已移除或重构，这里只需要引入 FastAPI 即可。
# 移除所有其他依赖导入。
# 错误处理已从 Uvicorn 的 lifespan 事件钩子转移到服务启动前一次性配置。

# 1. 初始化 FastAPI 应用程序
app = FastAPI(
    title="AgentProxy Service",
    description="系统所有状态报告和通用事件的唯一入口网关。所有业务逻辑必须经过此服务。(文件日志版)",
    version="1.0.0"
)

# 2. 挂载 API 路由

app.include_router(router, prefix="/api/v1")


# ----------------------------------------------------------------------
# 命令行启动逻辑 (CLI Launcher)
# 当通过 'python main.py' 运行时，此块代码会被执行。
# ----------------------------------------------------------------------
if __name__ == "__main__":


    # --- 1. 参数解析 ---
    parser = argparse.ArgumentParser(
        description="Android Manager Backend Service Launcher. 可用于启动 Web 服务或执行后台管理任务。",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 定义端口参数，并提供默认值
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API 服务的运行端口号。当作为 CLI 运行管理任务时，会记录此端口。"
    )

    # 新增一个用于模式切换的参数，明确告诉程序当前是 CLI 模式
    parser.add_argument(
        "--cli-mode",
        action="store_true",
        help="如果设置，则运行后台管理任务，而不是启动 Web 服务器。"
    )
    # 捕获所有剩余参数，传给核心业务逻辑
    parser.add_argument(
        "remaining_args",
        nargs=argparse.REMAINDER,
        help="传递给核心业务逻辑 main(args) 的所有额外参数。"
    )

    args = parser.parse_args()
    SERVICE_PORT = args.port

    # --- 2. 模式切换和执行 ---
    # 只有在命令行运行 (即 __name__ == "__main__") 时，才会进入此块。

    # 默认行为：启动 Web 服务器 (如果不是带 --cli-mode 参数运行)
    print("===================================================")
    print(f"🚀 服务已配置为通过脚本启动。")
    print(f"🚀 监听地址: 0.0.0.0:{SERVICE_PORT}")
    print("===================================================")
    try:
        # 修改启动方式以解决 Deprecation Warning
        uvicorn.run("main:app", host="0.0.0.0", port=SERVICE_PORT, reload=True)
    except Exception as e:
        print(f"\n🚨 启动 Uvicorn 服务器失败: {e}")
        print("请检查网络端口是否被占用，或确认所有依赖（fastapi, uvicorn, sqlalchemy）是否已安装。")
        sys.exit(1)