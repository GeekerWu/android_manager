# 🔐 安全认证模块文档: security.md

## 📝 模块概述

`security.py` 模块是应用程序的权限控制中心。它负责实现所有与用户身份认证、密码管理和令牌（JWT）相关的安全逻辑。它遵循 FastAPI 的依赖注入模型，将安全检查从业务路由中分离，确保代码的整洁性和可复用性。

## ⚙️ 核心组件与流程

### 1. 密码哈希与校验 (Password Hashing)
*   **技术栈:** `passlib` 结合 `bcrypt` 算法。
*   **组件:** `pwd_context`
*   **功能:** 负责密码的单向哈希存储。它确保原始密码永远不会存储在数据库中。
*   **方法:** `verify_password(plain_password, hashed_password)`。这是进行登录验证时，将用户输入的明文密码与存储的哈希密码进行比对的关键函数。

### 2. 用户凭证校验 (Credential Validation)
*   **函数:** `get_user_credentials(username: str, password: str) -> Optional[dict]`
*   **目的:** 这是认证的第一步。它模拟了对用户表进行查询，根据提交的 `username` 和 `password` 进行校验。
*   **流程:** 接受明文凭证，返回包含用户标识符（如 `user_id`）的字典，如果校验失败则返回 `None`。

### 3. JWT (JSON Web Token) 管理
*   **核心概念:** JWT 是一种紧凑的、自包含的、数字签名的字符串，用于在不安全通道上传输用户信息，而无需每次都查询数据库。
*   **密钥管理:** `SECRET_KEY` (必须是高熵的、保密的密钥，**强烈建议使用环境变量**)。
*   **生成 Token:** `create_access_token(data: dict, expires_delta: timedelta = None) -> str`
    *   它将用户身份信息（Payload）和过期时间（`exp`）一同编码到 Token 中。
    *   **安全性:** Token 通过 `SECRET_KEY` 签名，保证了数据的不可篡改性。
*   **提取 Token:** `OAuth2PasswordBearer(tokenUrl="login")`
    *   这是 FastAPI 提供的标准机制，用于自动从 HTTP 请求头（`Authorization: Bearer <token>`）中提取 Token。

### 4. 认证依赖函数 (The Authorization Gate)
*   **函数:** `get_current_user(token: str = Depends(oauth2_scheme))`
*   **用途:** **所有需要认证的路由必须使用此函数作为依赖。**
*   **工作流程 (执行流程):**
    1.  从请求中获取 Token。
    2.  尝试使用 `jwt.decode()` 解码 Token。如果解码失败（过期、签名错误），立即抛出 `401 Unauthorized`。
    3.  如果解码成功，提取 Payload 中的 `username`。
    4.  （最佳实践补充点）：理论上，应当在此处再次查询数据库，确保该用户在当前系统状态下仍然是有效的，防止使用已禁用的旧 Token。
    5.  返回一个包含用户信息的字典，供后续的业务逻辑使用。

## 🔒 总结与最佳实践

| 步骤 | 关键点 | 安全/性能建议 |
| :--- | :--- | :--- |
| **密钥** | ❌ 绝不硬编码 `SECRET_KEY`。 | 必须使用环境变量。 |
| **密码** | 每次使用 `verify_password` 时，都要防止彩虹表攻击，且哈希算法应保持最新。 | 使用 `passlib` 和至少 `bcrypt`。 |
| **Token** | 始终设置过期时间 (`ACCESS_TOKEN_EXPIRE_MINUTES`)。 | 最佳做法是实现 Token 刷新机制 (Refresh Token)，而不是仅依赖过期时间。 |
| **依赖** | 将 `get_current_user` 放在最外层，如 `app.include_router(..., dependencies=[Depends(get_current_user)])`。 | 确保所有受保护的路由都必须依赖此函数。 |