# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 📚 1. 核心架构概览 (High-Level Architecture)

本项目采用标准的**分层架构 (Layered Architecture)**，严格将核心业务逻辑、数据访问与外部请求处理解耦。理解每一层的作用是掌握本项目的关键。

### 🧩 核心组件职责 (The Components)

*   **`main.py` (Application Entry Point):**
    *   **角色:** 整个应用的“粘合剂”和生命周期管理器。
    *   **功能:** 初始化 FastAPI 实例、设置全局中间件 (Global Middleware)、处理应用级别的事件 (e.g., `@app.on_event("startup")`)。
    *   **重点:** 任何全局流程控制（如用户认证、日志初始化）都应在此层或通过此层暴露出的依赖函数实现。
*   **`api/endpoints.py` (Presentation/API Layer):**
    *   **角色:** 外部世界的接口。
    *   **功能:** 接收并解析 HTTP/WebSocket 请求。它不应包含复杂的业务判断，而应该将请求参数传递给 Service 层。
    *   **最佳实践:** 严格使用 FastAPI 的 `Depends()` 依赖注入机制来获取资源和执行安全检查。
*   **`service/` / `main.py` 业务逻辑层 (Business Logic Layer):**
    *   **角色:** 系统的“大脑”。
    *   **功能:** 包含核心业务规则、状态转换逻辑（例如用户心跳的复合原子操作）。它协调 DAO 和 Model，决策如何处理业务流程。
    *   **核心原则:** 必须遵循**原子性**，复杂操作需将其包装在数据库事务中。
*   **`database.py` (Data Access Object - DAO Layer):**
    *   **角色:** 数据库的唯一门面。
    *   **功能:** 负责与底层数据库的实际交互（Connection, Session, Query）。
    *   **关键:** 所有的数据库操作必须通过此层进行。它提供了事务安全的会话管理 (`get_db`)，确保了数据访问层与业务逻辑层的完全隔离。
*   **`models.py` (Model Layer):**
    *   **角色:** 领域模型 (Domain Model) 的定义。
    *   **功能:** 定义所有业务实体的数据结构和校验规则。它应是业务规则的最低层体现。

---

## ⚙️ 2. 开发环境与开发工作流 (Development Workflow)

本项目的开发流程严格围绕**版本控制**和**数据库迁移**展开。

### 🚀 运行和启动命令 (Run/Start Commands)

**⚠️ 依赖前提:** 确保已运行 `pip install -r requirements.txt` 安装所有依赖。

| 场景 | 命令 | 目的/备注 |
| :--- | :--- | :--- |
---
... (内容省略) ...

### 🚀 运行和启动命令 (Run/Start Commands)

**⚠️ 依赖前提:** 确保已运行 `pip install -r requirements.txt` 安装所有依赖。

| 场景 | 命令 | 目的/备注 |
| :--- | :--- | :--- |
| **开发模式 (Dev)** | `python main.py --port <端口号>` | **推荐用于开发。** 新的启动脚本通过解析命令行参数来设置服务端口。`<端口号>` 替换为你的服务端口（如 8000）。若不指定端口，则使用脚本中的默认值。 |
| **生产模式 (Prod)** | `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app` | **必须用于生产部署。** 使用 `gunicorn` 和 `uvicorn.workers.UvicornWorker` 保证高性能和多进程能力。此命令继续适用。 |
| **数据库初始化/迁移** | `alembic upgrade head` | **最关键的步骤。** 这是执行数据库结构（Schema）演进的唯一入口。**注意：** `alembic` 负责蓝图演进，而不是简单的数据刷新。每次代码模型（`models.py`）变更后，必须运行此命令。 |

... (剩余内容省略) ...

### 🧪 常用操作命令 (Utility Commands)

*   **Linting/代码规范检查:**
    *   *（建议）:* 建议使用 `flake8` 或 `pylint` 等标准工具。如果项目中配置了特定Linter，请使用 `pytest --lint` 或 `ruff check .` (根据实际项目依赖调整)。
*   **运行单元测试 (Unit Testing):**
    *   *（建议）:* 假设使用 Pytest，运行所有测试：`pytest`
    *   *单测:* 若要运行特定文件的测试，请使用 `pytest path/to/test_file.py`。

---

## ✨ 3. 强制开发规范与最佳实践 (MUST FOLLOW)

开发人员必须将以下规范作为强制要求，这些规范涉及数据完整性、安全性，并且已成为项目的工作方式（Working Way）。

### 🔒 安全性 (Security)
1.  **密钥管理:** 任何敏感密钥（如 `SECRET_KEY`）绝不能硬编码。必须通过**环境变量** (`os.environ`) 或专业的配置服务注入。
2.  **密码存储:** 必须使用现代、高强度、自带盐值的哈希算法（如 **Bcrypt**）。严禁使用 MD5、SHA1 等弱哈希。
3.  **认证机制:** 必须建立 **Refresh Token** 机制，不应过度依赖 Access Token 的单一有效期。所有业务路由必须通过中间件拦截未授权请求（HTTP 401）。

### 💾 数据完整性 (Data Integrity)
1.  **ACID 原则:** 所有涉及数据库写入（POST/PUT）的复合操作，无论多么简单（例如“心跳记录”），都必须封装在显式的**事务块**内。
2.  **事务流:** 必须遵循 **`Try...Commit...Finally...Rollback`** 的流程控制模式。只有所有子操作（包括日志记录、状态更新）都成功时，才执行 `db.commit()`；否则，强制执行回滚，确保数据原子性。

### 🚀 状态管理 (State Management)
*   **复合原子操作:** 任何代表业务状态的更新（如用户心跳/状态快照），必须是一个**复合原子操作**。这要求一次写入必须同时更新所有相关的实体（如 `TelemetryLog`、`Component`、`Robot`），从而保证在任何时间点读取的系统状态视图都是一致的。

---
**💡 总结:**
*   **写代码前:** 确认操作是否涉及数据修改 -> 确定是否需要数据库事务 -> 获取代码的最新逻辑 ->将改动点与最新逻辑进行整合 -> 弹出提示让用户确认是否修改 -> 如修改失败创建一个 当前文件名+new 后缀的新文件一遍用户追述。
*   **部署流程:** 依赖 `alembic upgrade head` -> `uvicorn/gunicorn` 启动。
*   **高风险点:** 永远不要绕过 DAO 层执行直接的 SQL 或 DB 操作。
***