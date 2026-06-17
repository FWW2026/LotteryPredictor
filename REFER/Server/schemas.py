# Server/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 客户端登录时发来的数据格式
class LoginRequest(BaseModel):
    username: str
    password: str
    device_id: str

# 服务器返回给客户端的数据格式
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expire_time: datetime