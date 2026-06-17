# Server/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# 对于 SQLite，需要添加 check_same_thread 参数
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础模型类，后续所有的表都会继承它
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# 获取数据库连接的通用依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()