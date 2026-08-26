# 🚀 后端服务启动指南 (server.md)

本指南描述了如何基于当前代码库启动和验证**核心 Python 后端服务**。请确保您当前的工作目录是 `backend/`。

**⚠️ 重要警告：关于虚拟环境 (Virtual Environment) ⚠️**
本次部署流程的特殊要求是：**不得创建 Python 虚拟环境**。所有 Python 依赖将直接安装到系统全局环境。请确保您的运行环境（`$PATH`）已经满足所有依赖。

---

## ⚙️ 第一步：环境准备与依赖安装 (Setup & Dependencies)

**假设当前工作目录：** `backend/`

### 1. 安装依赖

使用 `pip` 安装 `backend` 目录下的所有依赖。

```bash
pip install -r requirements.txt
```
**检查点：**
*   如果此步骤成功，则所有依赖已全局安装。
*   如果失败，请仔细阅读错误信息，并检查 `requirements.txt` 中的包名和版本是否正确，是否需要手动安装。

---

## 🐍 第二步：启动后端服务 (Backend Runtime)

后端服务是 Python 核心，负责业务逻辑和数据持久化。根据项目文件结构，我们猜测使用一个 ASGI/WSGI 框架（如 FastAPI 或 Flask）来运行 `main.py`。

**⚠️ 核心启动命令（请自行调整）：**

请根据您使用的实际框架（FastAPI/Flask等）修改以下命令。

```bash
# 示例 1: 如果使用 uvicorn 启动 FastAPI/Starlette 应用

uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 示例 2: 如果使用 Flask 启动应用
# python -m flask run --host=0.0.0.0 --port=8000
```

**操作步骤：**
1.  在 `backend/` 目录下执行上述任一启动命令。
2.  **重要：** **请保持此终端窗口运行**，因为它就是服务的持续运行环境。

**验证点：**
*   观察终端输出，确认服务已成功启动，并且明确报告了监听的地址和端口（例如 `Uvicorn running on http://0.0.0.0:8000`）。

---

## ✅ 第三步：端到端烟雾测试 (End-to-End Smoke Test)

在服务处于运行状态（第二步未退出终端）时，请在一个新的终端窗口执行以下测试。

### 1. API 接口调用测试 (HTTP Smoke Test)

使用 `curl` 或 Postman 等工具调用一个核心的 API 端点，验证业务逻辑和数据持久化是否正常。

```bash
# 示例：调用获取设备列表的 API
# 请将端口号和路径替换为实际值
端口list http://127.0.0.1:8000/docs

curl http://localhost:8000/api/v1/devices
```
**预期结果：**
*   HTTP 状态码为 `200 OK`。
*   接收到的 JSON 结构体是包含设备数据的列表，且数据内容符合业务预期。

### 2. 数据库状态验证

确认服务能够正常读取和写入数据库文件 (`robot_manager.db`)。

---

**总结流程：**
1.  确保你在 `backend/` 目录下。
2.  `pip install -r requirements.txt` (首次运行)
3.  `[执行服务启动命令]` (在一个终端保持运行)
4.  在新终端窗口，使用 `curl` 调用核心 API 进行验证。