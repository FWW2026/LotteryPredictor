项目结构
DouyinLeadFinder/
│
├─ Client/              # 客户端代码
│  ├─ config.py            # 全局配置（如服务器API地址、版本号）
│  ├─ main.py              # 客户端启动总入口
│  │
│  ├─ utils/               # 工具类文件夹
│  │  ├─ __init__.py
│  │  ├─ hardware.py       # 获取机器硬件指纹 (Device ID)
│  │  └─ api_client.py     # 封装与 FastAPI 服务端通信的 HTTP 请求
│  │
│  └─ ui/                  # 界面视图文件夹
│     ├─ __init__.py
│     └─ login_window.py   # 登录界面 UI 及交互逻辑
└─ Server/              # 后端文件夹
   ├─ config.py         # 后端全局配置（密钥、数据库连接）
   ├─ database.py       # 数据库连接初始化
   ├─ models.py         # 数据库表结构 (SQLAlchemy 模型)
   ├─ schemas.py        # 数据传输格式校验 (Pydantic 模型)
   ├─ auth.py           # 密码加密与 JWT Token 签发工具
   ├─ crud.py           # 数据库增删改查具体逻辑
   └─ main.py           # 后端服务启动主入口

注意：
bcrypt要用低版本，不然报错
pip install bcrypt==4.0.1
以上版本经过测试可用

测试：
第一步启动模拟服务器
cd C:\Users\yyx20\PycharmProjects\DouyinLeadFinder\Server
uvicorn main:app --reload --port 8000   
