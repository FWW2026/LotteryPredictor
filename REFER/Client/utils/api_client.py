# utils/api_client.py
import requests
from config import API_BASE_URL

class APIClient:
    @staticmethod
    def login(username, password, device_id):
        """向 FastAPI 服务端发送登录验证"""
        url = f"{API_BASE_URL}/login"
        payload = {
            "username": username,
            "password": password,
            "device_id": device_id
        }
        try:
            # 这里的 timeout 很重要，防止网络卡死导致 UI 崩溃
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code, response.json()
        except requests.exceptions.RequestException as e:
            return 0, {"detail": f"无法连接到认证服务器: {str(e)}"}