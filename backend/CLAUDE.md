# Android Manager Backend - 架构与开发指南 (CLAUDE.md)

**版本:** 1.0.0
**最后更新:** 2026-09-02
**作者:** Claude Code
**目标:** 本文档旨在为所有开发者提供一个全局、权威的架构概述，描述 Android Manager 后端服务的核心功能、模块划分、数据流转路径以及最佳实践。

---

## 🌟 一、项目概述 (Project Overview)

Android Manager Backend 是一个基于 **FastAPI** 框架的、用于管理和控制机器人（Robot）单机的 API 服务。其核心功能包括但不限于：用户认证与授权、设备状态实时监控（通过 WebSocket）、接收和执行远程控制命令、以及持久化管理设备信息。

**主要技术栈:**
*   **框架:** Python, FastAPI
*   **数据库:** SQLAlchemy (ORM)
*   **认证:** JWT (JSON Web Tokens)
*   **实时通信:** WebSocket
*   **代码风格:** 优先使用函数式编程 (Functional Programming)。

## 📐 二、系统架构与数据流 (Architecture & Data Flow)

本项目采用经典的多层架构模型，并结合了 FastAPI 的 Dependency Injection (DI) 机制和 Middleware 进行请求拦截，形成一个严密的防御和执行链。

### 🌐 核心流程图 (The Request Lifecycle)

整个请求生命周期是一个三层过滤机制：

1.  **Middleware (L1 - 边界控制):**
    *   **拦截点:** 所有 HTTP 请求的入口。
    *   **功能:** **职责范围控制 (Scope Control)**。首先检查请求头是否包含 `Authorization: Bearer <token>`。如果缺失，则立即返回 401 Unauthorized，不传递给后续任何层级。
2.  **Dependency (L2 - 权限验证):**
    *   **拦截点:** 路由函数执行前。
    *   **机制:** 通过 FastAPI 的 Dependency Injection 注入 `get_current_user` 依赖。
    *   **功能:** **身份验证与用户上下文建立 (AuthN & AuthZ)**。该函数负责解析 JWT Token，验证其签名、是否过期，并在数据库中检索对应的用户对象。只有成功验证后，用户对象才会被注入到请求的上下文，供后续业务逻辑使用。
3.  **Handler / Endpoint (L3 - 业务执行):**
    *   **拦截点:** 路由函数体内部。
    *   **功能:** **核心业务逻辑 (Core Logic)**。在此层，所有模块（如 `database.py`）都能安全地访问到经过验证的 `current_user` 对象，执行业务操作。

---

## 🧩 三、核心模块职责划分 (Module Responsibilities)

系统被划分为以下几个相互协作的模块：

### 1. ⚙️ 启动与编排层 (The Orchestration Layer: `main.py`)
*   **职责:** 负责应用程序的生命周期管理。
*   **工作内容:**
    *   使用 `argparse` 接收并绑定服务端口 (`SERVICE_PORT`)。
    *   通过 `uvicorn.run()` 启动 FastAPI 实例。
    *   **关键生命周期钩子:** 利用 `@app.on_event("startup")` 钩子实现**数据库初始化/数据回填**（Schema Setup & Seeding）。这是确保服务启动时数据库具备基础数据的关键点。
    *   将所有主要的 API 路由（`api_router`）和 WebSocket 路由挂载到主应用实例上。

### 2. 🔗 API 接口与路由层 (The API Layer: `api/endpoints.py`)
*   **职责:** 接收外部 HTTP 请求，将其映射到具体的业务逻辑处理函数。
*   **工作内容:** 组织所有 API 路由（`@router.get`, `@router.post` 等），并强制应用全局安全依赖。它不应包含复杂的业务计算，只负责**请求参数的接收**和**业务流的调度**。

### 3. 💾 数据持久化层 (The Persistence Layer: `database.py`, `models.py`)
*   **职责:** 管理与数据库的连接、会话管理和数据模型的定义。
*   **`models.py`:** 定义所有核心数据实体（如 `User`, `Robot`, `Telemetry`）的 ORM 模型结构。
*   **`database.py`:** 封装了 SQLAlchemy 的 `engine` 和 `SessionLocal`，提供了数据库会话的获取和释放机制，是所有数据操作的**唯一入口点**，极大地保证了代码的健壮性和一致性。

### 4. 🛡️ 安全与认证层 (The Security Layer: `security.py` & Middleware)
*   **职责:** 保护所有敏感资源，是系统信任的基础。
*   **`security.py`:** 包含 JWT 的生成 (`create_access_token`)、验证（`JWT_SECRET_KEY`）和密码哈希等核心安全工具函数。
*   **Middleware:** 实现请求拦截和初步鉴权。
*   **Dependency:** `get_current_user` 依赖函数负责在 L2 层进行完整的二次验证，确保请求的合法性和用户身份的唯一性。

### 5. 📡 实时通信层 (The Real-Time Layer: `api/websocket.py`)
*   **职责:** 管理设备（机器人）与后端服务器之间**实时、双向、持久化的通信连接**。它不遵循传统的请求/响应（Request/Response）模式，而是模拟一个持续的会话（Session）。
*   **特点:** 与标准的 HTTP API 不同，WebSocket 允许服务器主动推送数据（如心跳、状态变化），并在低延迟环境下接收指令。

---

## 🛠️ 四、开发规范与最佳实践 (Best Practices)

1.  **依赖注入优先 (DI First):** 任何涉及数据库或用户上下文的操作，都必须通过 FastAPI 的 Dependency Injection 机制 (`Depends(...)`) 来获取资源（例如：数据库会话、当前用户）。**切勿**在业务逻辑函数中直接实例化或硬编码数据库连接。
2.  **分层隔离:** 严格遵循 **Handler $\leftarrow$ Service $\leftarrow$ Repository (DB)** 的三层结构。
    *   **Handler (Endpoint):** 接收请求，调用 Service 层。
    *   **Service (Business Logic):** 包含核心业务规则，调用 Repository 层。
    *   **Repository (DB):** 仅负责 ORM 层的 CRUD 操作。
3.  **代码风格:**
    *   **语言:** 必须使用英文注释和代码。
    *   **命名:** 采用 `camelCase` (TypeScript/JS) 或 `snake_case` (Python)。
    *   **编程范式:** 优先采用函数式编程，增强代码的可预测性和可测试性。

## 🚧 五、未来迭代建议 (Future Considerations)

1.  **完善日志系统:** 增加统一的、结构化的日志记录服务，记录 L1 到 L3 每一层的关键决策点和错误发生的位置。
2.  **速率限制 (Rate Limiting):** 在 Middleware 层增加基于用户或IP的速率限制功能，防止滥用 API 资源。
3.  **错误报告:** 标准化所有异常处理，使用统一的错误代码和结构化的 JSON 错误响应，而不是让用户看到原始的 Python 堆栈信息。
