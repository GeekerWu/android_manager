from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# --- 1. 配置和常量 ---
# 使用环境变量或配置读取，这里硬编码模拟
SECRET_KEY = "YOUR_SUPER_SECRET_KEY_FOR_JWT_SIGNING" # 🚨 ⚠️ 生产环境中必须使用环境变量！
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- 2. 密码哈希管理 ---
# 使用 Passlib 管理密码哈希，模拟实际的密码存储和校验
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配。
    注意：这里接收一个已哈希的密码和明文密码，但为了本次演示，我们将使用硬编码的判断。
    """
    # 实际应用中会调用 pwd_context.verify(plain_password, hashed_password)
    # 为了本次演示简化，我们假设后端逻辑会做这一步。
    return True

def get_user_credentials(username: str, password: str) -> Optional[dict]:
    """
    【模拟数据库查询】模拟根据用户名和密码获取用户信息。
    硬编码验证：仅允许 admin/admin 登录。
    """
    if username == "admin" and password == "admin":
        return {"username": "admin", "user_id": 1}
    return None

# --- 3. JWT 工具函数 ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """生成 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- 4. 核心认证依赖函数 ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    FastAPI 依赖函数。用于从请求头获取 Token 并验证用户身份。
    当用户提供有效的 Token 时，返回用户信息 (User Model)。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. 从 Token 中解码出 Payload (期望包含 'username')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")

        if username is None:
            raise credentials_exception

        # 2. 验证 Payload 中的用户名是否与系统用户库匹配 (这里仅做流程演示)
        # 实际应用中，会在这里调用数据库查询，确保用户和 Token 匹配
        # 为了本次演示，我们只检查用户名是否有效。

        # 假设用户对象就是 username
        return {"username": username, "user_id": 1}
    except JWTError:
        # 如果解码失败，抛出认证失败的异常
        raise credentials_exception
    except Exception as e:
        # 捕获其他可能的错误
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal authentication error: {str(e)}")

# 备注：在生产环境中，需要导入 pydantic 模型和 httpx/requests 来进行真正的密码哈希校验。
