# Server/config.py
import os

# 安全密钥（商业部署时切记换成复杂的随机字符串）
SECRET_KEY = "DOUYIN_LEAD_FINDER_SUPER_SECRET_KEY_2026"
# 加密算法
ALGORITHM = "HS256"
# Token 有效期（分钟），比如设置为 1天
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# 数据库连接地址
# 现阶段使用本地 SQLite 文件（自动创建 sql_app.db）
# 以后上线切换 PostgreSQL 只需要改成: "postgresql://user:password@localhost/dbname"
DATABASE_URL = "sqlite:///./sql_app.db"