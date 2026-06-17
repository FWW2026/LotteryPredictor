# Server/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import datetime

from database import engine, Base, get_db
import models, schemas, crud, auth
from config import ACCESS_TOKEN_EXPIRE_MINUTES

# 初始化所有数据库表（如果不存在则自动创建）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DouyinLeadFinder 授权中心")

# 自动初始化测试数据
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    # 如果没有 admin 账号，自动创建一个
    if not crud.get_user_by_username(db, "admin"):
        test_user = models.UserModel(
            username="admin",
            password_hash=auth.hash_password("123456"), # 测试密码 123456
            expire_time=datetime.datetime.utcnow() + datetime.timedelta(days=30), # 30天后到期
            plan_type="monthly"
        )
        db.add(test_user)
        db.commit()
        print("====== 测试账号初始化成功! 账号: admin, 密码: 123456 ======")

@app.post("/api/login", response_model=schemas.TokenResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    # 1. 验证用户是否存在
    user = crud.get_user_by_username(db, request.username)
    if not user or not auth.verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="账号或密码错误")

    # 2. 验证套餐是否过期
    if user.expire_time < datetime.datetime.utcnow():
        raise HTTPException(status_code=403, detail="您的商业授权已到期，请续费")

    # 3. 验证设备绑定（一机一码防破解）
    if user.device_id is None:
        # 如果该账号从未登录过，绑定当前设备
        crud.update_user_device(db, user.id, request.device_id)
    elif user.device_id != request.device_id:
        # 如果登录的设备指纹与数据库记录的不一致，拒绝登录
        raise HTTPException(status_code=403, detail="该账号已绑定其他设备，请联系管理员解绑")

    # 4. 签发 JWT 令牌
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = auth.create_access_token(
        data={"sub": user.username, "plan": user.plan_type},
        expires_delta=access_token_expires
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expire_time": user.expire_time
    }