# 🚀 API 入口点与应用启动文档: main.md

## 📝 模块概述

`main.py` 是整个 Android Manager 后端 API 的入口点（Entry Point）。它负责应用程序的生命周期管理、全局中间件的配置，以及将业务功能路由和安全依赖项组合起来，形成可访问的 RESTful API 接口。

## ⚙️ 核心流程与机制

### 1. 应用初始化 (FastAPI App Setup)
*   **实例:** `app = FastAPI(...)`
*   **功能:** 创建 FastAPI 应用实例。
*   **核心依赖:** 整个应用高度依赖于数据库（通过 `database.py`）和安全模块（通过 `security.py`）来初始化和运行。

### 2. 全局中间件 (Global Middleware)
*   **机制:** 使用 `@app.middleware("http")` 装饰器挂载的 `auth_middleware`。
*   **作用:** 它是拦截所有进站 HTTP 请求的第一道防线。
*   **逻辑（白名单机制）：**
    1.  **白名单维护:** 它维护了一个白名单列表（如 `/login`, `/docs`, `/openapi.json`）。
    2.  **拦截逻辑:** 凡是请求路径不在白名单内的请求，都会触发 Token 校验。
    3.  **功能修复点 (Critical Fix):** 修复了 FastAPI 启动时访问 `/openapi.json` 时被错误地拦截和拒绝的 Bug，通过将该路径加入白名单解决了这个问题。
*   **重要性:** **这是 API 保护的“粗粒度”防御层。**它确保任何未登录的、试图访问受保护路由的请求都会被拦截。

### 3. 应用生命周期事件 (Startup Event)
*   **函数:** `@app.on_event("startup")`
*   **作用:** 定义了应用启动时需要执行的初始化任务。
*   **核心操作:**
    1.  打印启动消息 (`🤖 FastAPI 启动中...`)。
    2.  初始化数据库连接。
    3.  **模拟数据初始化:** 检查并创建示例机器人（`SN001`）和其关联的组件记录。
*   **容错性:** 整个启动事件被 `try...except` 块包裹，确保即使数据库初始化失败（例如，因为配置错误），应用依然能优雅地启动，并打印出明确的错误警告。

### 4. 路由挂载与依赖注入 (Routing and Dependency)
*   **流程:** 所有的业务 API 路由（通过 `api_router` 导入）都会被挂载到 `/api/v1` 前缀下。
*   **保护机制:** 最重要的是，`app.include_router(...)` 必须包含 `dependencies=[Depends(get_current_user)]`。这确保了：
    1.  每次调用该路由时，都会先执行 `get_current_user`。
    2.  只有当 `get_current_user` 成功返回用户对象时，业务路由才会执行。

## 🛠️ 最佳实践与注意事项

1.  **Middleware 顺序:** 了解中间件的执行顺序。`auth_middleware` 必须放在所有需要保护的路由之前。
2.  **依赖注入优先:** 对于任何需要在路由层执行的流程控制（如认证、限速），应优先使用 FastAPI 的 `Depends()` 机制，它比依赖 Middleware 更贴合 Python 异步框架的思维模型。
3.  **错误代码:** 确保所有 `HTTPException` 都携带了 `status_code`，以便前端或调用者能够准确处理不同级别的错误（如 401 vs 403）。