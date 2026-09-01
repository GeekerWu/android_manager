markdown: |
# Backend Module Documentation
(本文件是项目后端服务的核心技术文档，包含结构、部署流程及强制的开发规范。)

本项目后端服务模块 (`backend/`) 的文件结构和功能概述。本模块负责实现用户管理、内容发布、实时消息等核心业务逻辑。

## 📂 目录结构概览
当前模块结构包含了核心业务逻辑和数据访问层：

*   **`main.py`**:
    *   **作用**: 应用程序的入口点。用于初始化服务器、设置路由，并启动主服务流程。**【架构要点】** 负责全局中间件（Middleware）和应用生命周期管理（如 `@app.on_event("startup")`），是系统的核心粘合剂。
*   **`models.py`**:
    *   **作用**: 定义所有主要的业务数据模型（Data Models）。所有数据结构化和验证逻辑应在此处定义。
*   **`database.py`**:
    *   **作用**: 数据库操作层 (Data Access Object, DAO)。负责管理数据库连接、会话和通用的数据库查询函数。**【规范要点】** 提供了事务安全的会话管理 (`get_db`)，强制所有业务写入必须显式管理事务边界。
*   **`api/`**:
    *   **`endpoints.py`**: 核心 API 路由文件。负责处理标准的 HTTP 请求（GET/POST）和协调业务逻辑。**【规范要点】** 业务逻辑必须在 FastAPI 的 `Depends()` 依赖函数中获取依赖，以保证流程控制的清晰性。
    *   **`websocket.py`**: 实时通信模块。专门用于管理和处理 WebSocket 连接、消息广播和实时事件。
*   **`requirements.txt`**:
    *   **作用**: 记录了本后端服务运行所需的全部 Python 依赖库版本清单。
*   **`server.md`**:
    *   **作用**: （文档/配置）部署或服务器配置的补充文档，了解具体运行环境的配置参数。

## ✨ 模块职责与分层架构
本项目严格遵循分层架构（Layered Architecture）：

1.  **Presentation/API 层 (`api/`):** 接收外部 HTTP/WebSocket 请求，作为业务流程的门面，调用 Service 层。
2.  **Service/Business Logic 层 (`main.py`, `api/endpoints.py`):** 实现核心业务逻辑，是业务决策的执行者，协调数据访问和状态管理。
3.  **Data Access Object (DAO) 层 (`database.py`):** 负责与数据库的实际交互。它将业务逻辑与数据库的具体实现细节解耦。
4.  **Model 层 (`models.py`):** 定义并维护数据结构和领域模型。

## 🚀 快速启动与部署指南
(此部分的内容保持不变，但请注意，本服务是基于 FastAPI 构建的。)

### 📝 步骤 1: 环境准备与依赖安装 (Prerequisites)
首先，必须激活虚拟环境，并安装所有必要的 Python 依赖库。

```bash
pip install -r requirements.txt
```

### 💾 步骤 2: 数据库初始化与迁移 (Database Initialization & Migration)
**🚨 重要警告**: 本服务使用 Alembic 进行数据库版本控制。此过程不是简单的“刷新”，而是一个高度结构化的**蓝图演进**过程。

**✨ 迁移核心概念**: 数据库迁移是通过一套“施工蓝图”来更新数据库结构的。它主要负责：
*   **添加/修改/删除结构**: 确保表结构与代码模型一致。
*   **数据安全**: 迁移过程本身是数据安全的。除非迁移脚本内明确执行了 `DELETE` 或 `TRUNCATE`，否则历史数据是**不会丢失**的。

**执行流程**:
请始终执行以下命令来同步代码和数据库结构：
```bash
alembic upgrade head
```
*   **首次使用**: 如果是全新数据库，`alembic` 会自动执行所有基础结构创建。
*   **后续更新**: 当代码模型发生变化时，运行此命令，它会自动比对版本差异，并只执行增量变更。

### 🖥️ 步骤 3: 启动服务 (Running the Service)

本项目服务是基于 FastAPI/ASGI 标准构建的，启动方式应根据运行环境选择最适合的方案：

**🔴 🔵 开发环境 (Development)**: **推荐使用 Uvicorn**。使用 `--reload` 标志，支持热重载，极大地提高了开发效率。
```bash
uvicorn main:app --reload
```

**🟡 🚀 生产环境 (Production)**: **必须使用 Gunicorn 进程管理器**。这是保证高性能和高可用性的行业标准做法。
```bash
# 示例: 部署到生产环境，使用 4 个工作进程
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```
**⚠️ 兼容性警告**: 由于 `gunicorn` 依赖 POSIX 系统模块（如 `fcntl`），在纯 Windows 环境（如本本次执行的环境）下，`gunicorn` 可能会执行失败。在 Windows 上进行本地测试时，仍推荐使用 `uvicorn main:app --reload`。

## 🚀 核心开发规范与最佳实践 (MUST READ)

此部分规定了代码编写的最低标准，所有核心业务逻辑必须遵循以下原则。

### 1. 🛡️ 安全性（Security）：
*   **凭证管理 (Secret Keys):** 所有的敏感密钥（如 `SECRET_KEY`）**绝不能**在代码中硬编码。必须通过**环境变量**或配置服务引入。
*   **密码哈希 (Password Hashing):** 必须使用高强度、现代化的哈希算法（如 Bcrypt）并通过 `passlib` 等专业库处理，禁止使用 MD5/SHA1 等弱加密算法。
*   **Token管理:** 强制要求使用 **Refresh Token** 机制，而不能仅仅依赖 Access Token 的有效期。所有业务路由必须通过中间件拦截未授权请求（返回 401）。

### 2. 💾 事务完整性（Data Integrity）：
*   **原子性原则 (ACID):** 所有涉及数据库写入（POST/PUT）的复合操作（如一次心跳心跳）必须在显式的**事务块**内完成。
*   **流程控制:** 务必遵循 **Try-Commit-Finally-Rollback** 的模式。只有当所有子操作（如日志记录、状态更新、组件同步）全部成功时，才执行 `db.commit()`；否则必须执行回滚，确保数据一致性。

### 3. 💡 状态管理（State Management）：
*   **复合原子操作:** 机器人心跳（Heartbeat）代表一个完整的“状态快照”。这意味着单次心跳的写入必须是一个**复合原子操作**：它必须同时写入 **TelemetryLog**、更新 **Component** 和 **Robot** 状态，以保证获取的任何时间点的状态视图都是完整的。

## 🚧 待改进点和待办任务 (To Be Addressed)
*   **[待办]** 将用户凭证验证逻辑 (`/login` handler) 抽象到一个独立的 `AuthService` 类中，而非散落在 `endpoints.py` 的依赖函数中，以提升可复用性。
*   **[待办]** 在 `database.py` 中增加一个 `ensure_initial_data()` 静态方法，并调用该方法作为 `main.py` 启动事件的一部分，从而统一初始化逻辑。
*   **[待办]** 考虑将 WebSocket 和 REST API 的认证逻辑分离，使它们能复用更底层的安全检查器，避免代码冗余。
