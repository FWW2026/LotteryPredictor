# config.py
import os

# 服务端 API 基础路径（本地测试用 localhost，上线后换成你的域名）
API_BASE_URL = "http://127.0.0.1:8000/api"

# 客户端版本号
APP_VERSION = "v1.0.0"

# 临时存放 Token 的本地路径 (实际商用建议用 keyring 库，初期可以用加密文件)
TOKEN_CACHE_PATH = os.path.join(os.path.expanduser("~"), ".douyin_lead_finder_token")