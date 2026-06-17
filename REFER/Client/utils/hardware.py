# utils/hardware.py
import subprocess
import hashlib
import sys


def get_device_id() -> str:
    """获取当前电脑的唯一硬件指纹 (目前支持 Windows)"""
    if sys.platform != "win32":
        # 兼容非 Windows 系统测试，实际生产环境可根据需求扩展
        return hashlib.sha256(b"NON_WINDOWS_TEST_DEV").hexdigest()

    try:
        # 读取 Windows 主板 UUID
        output = subprocess.check_output('wmic csproduct get uuid', shell=True).decode('utf-8')
        uuid_str = output.split('\n')[1].strip()

        # 使用 SHA-256 加密，避免明文暴露硬件信息，同时固定为 64 位字符串
        return hashlib.sha256(uuid_str.encode('utf-8')).hexdigest()
    except Exception:
        # 备用方案：如果由于权限问题获取失败，给一个相对稳定的标识
        import platform
        fallback = platform.node() + platform.processor()
        return hashlib.sha256(fallback.encode('utf-8')).hexdigest()