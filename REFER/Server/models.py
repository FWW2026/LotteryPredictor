# Server/models.py
from sqlalchemy import Column, Integer, String, DateTime
from database import Base
import datetime

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    expire_time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    plan_type = Column(String, default="monthly") # monthly, quarterly, annual
    device_id = Column(String, nullable=True)     # 绑定设备的硬件指纹