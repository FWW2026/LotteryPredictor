# Server/crud.py
from sqlalchemy.orm import Session
from models import UserModel

def get_user_by_username(db: Session, username: str):
    """通过用户名查找用户"""
    return db.query(UserModel).filter(UserModel.username == username).first()

def update_user_device(db: Session, user_id: int, device_id: str):
    """更新/绑定用户的设备ID"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user:
        user.device_id = device_id
        db.commit()
        db.refresh(user)
    return user