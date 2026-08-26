# 💾 数据库层模块文档: database.md

## 📝 模块概述

`database.py` 是本应用程序的数据库连接和会话（Session）管理核心模块。它封装了 SQLAlchemy 的引擎创建、会话工厂的配置，并提供了线程安全的依赖获取函数，确保整个应用程序在不同请求和生命周期中都能访问到正确的、可用的数据库连接。

## ⚙️ 核心组件与流程

### 1. 数据库引擎 (Engine)
*   **定义:** `engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})`
*   **功能:** 创建底层数据库连接的工厂。
*   **关键配置:**
    *   `SQLALCHEMY_DATABASE_URL`: 定义了数据库连接的 URI（当前为 SQLite）。
    *   `connect_args={"check_same_thread": False}`: 这是一个针对 SQLite 的特殊配置，允许在非主线程中访问数据库，对于Web应用是必需的。

### 2. 会话工厂 (Session Factory)
*   **定义:** `SessionLocal = sessionmaker(...)`
*   **功能:** 这是一个用于生成数据库会话对象（`Session`）的工厂。它实现了数据库连接的生命周期管理。
*   **📜 历史记录/重要更新:**
    *   **`autocommit` 参数:** 根据 SQLAlchemy 最佳实践，`autocommit=True` 已被弃用。当前的配置已更新为 `autocommit=False`，强制开发者在业务逻辑完成后显式调用 `session.commit()`，以保证事务的原子性（ACID）。
    *   **`autoflush` 参数:** 保持 `autoflush=True`，这允许 SQLAlchemy 在事务提交前自动将内存中的更改刷新到数据库。
*   **使用方法:** 每次使用时，应通过 `get_db()` 函数获取连接，并在 `finally` 块中确保调用 `db.close()` 来释放连接资源。

### 3. 依赖函数 (Dependency Function)
*   **函数:** `get_db()`
*   **作用:** 作为 FastAPI 的依赖注入（`Depends`）对象。
*   **流程:**
    1.  调用 `SessionLocal()` 创建一个新的数据库会话实例。
    2.  使用 `yield db` 机制，将会话对象提供给依赖它的路由。
    3.  无论路由执行成功还是失败，`finally` 块都会被触发，执行 `db.close()`，从而确保数据库连接始终被释放，防止连接泄漏。

## 🛠️ 最佳实践与注意事项

1.  **依赖管理:** 始终通过 `Depends(get_db)` 来获取数据库会话，这是保证资源正确释放的最佳实践。
2.  **事务控制:** **核心原则是：** 不要依赖 `autocommit`。所有修改数据库的操作（增、删、改）都必须在一个事务块内，并在操作成功后手动调用 `session.commit()`。
3.  **连接关闭:** 必须依赖 `finally` 块中的 `db.close()` 逻辑，确保在任何情况下连接都会被释放。