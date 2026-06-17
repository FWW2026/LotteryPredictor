# ui/login_window.py
import time
import base64
from datetime import datetime, timedelta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction
from PySide6.QtGui import QIcon # or PyQt6.QtGui

from Client.utils.hardware import get_device_id
from Client.utils.api_client import APIClient
from config import TOKEN_CACHE_PATH


class LoginWindow(QWidget):
    # 自定义信号：登录成功后通知 main.py 打开主界面
    login_success_signal = Signal(str)

    def __init__(self):
        super().__init__()
        # 登录失败计数和锁定时长
        self.fail_count = 0
        self.lock_until = None  # 锁定的截止时间
        self.max_fail_count = 5  # 最大失败次数
        self.lock_duration = 60  # 锁定60秒
        self.lock_timer = None  # 倒计时定时器
        self.remaining_lock_time = 0  # 剩余锁定时长

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("DouyinLeadFinder - 商业授权登录")
        self.setFixedSize(380, 480)  # 增加高度以容纳新功能
        self.setWindowIcon(QIcon("icons/logo.ico"))

        # 允许窗口无边框（可选，如果想要完全自定义的外观可以开启，这里先用标准窗口方便调试）
        # self.setWindowFlags(Qt.FramelessWindowHint)

        # 现代暗色调 QSS 样式表
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E24;
                color: #FFFFFF;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QLabel#TitleLabel {
                font-size: 22px;
                font-weight: bold;
                color: #00ADB5;
                margin-bottom: 20px;
            }
            QLineEdit {
                background-color: #2D2D35;
                border: 1px solid #3F3F46;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                color: #FFFFFF;
                margin-bottom: 15px;
            }
            QLineEdit:focus {
                border: 1px solid #00ADB5;
            }
            QPushButton#LoginBtn {
                background-color: #00ADB5;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
                color: #FFFFFF;
                margin-top: 10px;
            }
            QPushButton#LoginBtn:hover {
                background-color: #00F5FF;
            }
            QPushButton#LoginBtn:pressed {
                background-color: #008C95;
            }
            QPushButton#LoginBtn:disabled {
                background-color: #666666;
                cursor: not-allowed;
            }
            QLabel#Footnote {
                color: #666666;
                font-size: 11px;
            }
            QPushButton#TogglePwdBtn {
                background-color: transparent;
                border: none;
                font-size: 16px;
                color: #888888;
                padding: 0px;
                margin-left: -30px;
                margin-bottom: 15px;
                cursor: pointer;
            }
            QPushButton#TogglePwdBtn:hover {
                color: #00ADB5;
            }
        """)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setAlignment(Qt.AlignCenter)

        # 标题
        self.title_label = QLabel("系统商业授权登录")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        # 用户名输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入授权账号")
        main_layout.addWidget(self.username_input)

        # 密码输入框（带显示/隐藏按钮）
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入授权密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)

        # 显示/隐藏密码按钮
        self.toggle_pwd_btn = QPushButton("    👁️")
        self.toggle_pwd_btn.setObjectName("TogglePwdBtn")
        self.toggle_pwd_btn.setFixedSize(30, 60)
        self.toggle_pwd_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_pwd_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.toggle_pwd_btn)
        main_layout.addLayout(password_layout)

        # 登录按钮
        self.login_button = QPushButton("验证并登录系统")
        self.login_button.setObjectName("LoginBtn")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        main_layout.addWidget(self.login_button)

        # 底部机器码提示（让付费用户觉得很专业，同时方便售后）
        main_layout.addSpacing(20)
        device_id_short = get_device_id()[:16] + "..."
        self.footer_label = QLabel(f"本机指纹: {device_id_short}\n一号一机，严禁泄漏")
        self.footer_label.setObjectName("Footnote")
        self.footer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.footer_label)

        self.setLayout(main_layout)

        # 设置回车键登录
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def toggle_password_visibility(self):
        """切换密码显示/隐藏"""
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_pwd_btn.setText("    🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_pwd_btn.setText("    👁️")

    def check_lock_status(self):
        """检查是否被锁定，返回剩余锁定秒数"""
        if self.lock_until and datetime.now() < self.lock_until:
            remaining = int((self.lock_until - datetime.now()).total_seconds())
            return remaining
        return 0

    def start_lock_countdown(self):
        """开始倒计时解锁"""
        self.remaining_lock_time = self.lock_duration
        self.login_button.setEnabled(False)

        self.lock_timer = QTimer()
        self.lock_timer.timeout.connect(self.update_lock_countdown)
        self.lock_timer.start(1000)  # 每秒更新一次

    def update_lock_countdown(self):
        """更新倒计时显示"""
        self.remaining_lock_time -= 1

        if self.remaining_lock_time <= 0:
            # 解锁
            self.lock_timer.stop()
            self.login_button.setEnabled(True)
            self.login_button.setText("验证并登录系统")
            self.fail_count = 0
            self.lock_until = None
        else:
            self.login_button.setText(f"请等待 {self.remaining_lock_time} 秒后重试")

    def handle_login(self):
        """处理登录请求"""
        # 检查是否被锁定
        lock_remaining = self.check_lock_status()
        if lock_remaining > 0:
            QMessageBox.warning(
                self,
                "操作受限",
                f"登录失败次数过多，请在 {lock_remaining} 秒后重试"
            )
            return

        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "提示", "请填写完整的账号和密码！")
            return

        # 禁用按钮防止重复点击
        self.login_button.setEnabled(False)
        self.login_button.setText("正在验证授权...")

        # 获取设备指纹
        device_id = get_device_id()

        # 发起登录请求（带异常处理）
        try:
            status_code, response_data = APIClient.login(username, password, device_id)

            if status_code == 200:
                # 登录成功，重置失败计数
                self.fail_count = 0
                self.lock_until = None

                token = response_data.get("access_token")
                # 加密存储 Token 到本地（简单编码，避免明文）
                try:
                    encoded_token = base64.b64encode(token.encode()).decode()
                    with open(TOKEN_CACHE_PATH, "w", encoding="utf-8") as f:
                        f.write(encoded_token)
                except Exception as e:
                    # 如果加密失败，至少存储明文
                    with open(TOKEN_CACHE_PATH, "w", encoding="utf-8") as f:
                        f.write(token)

                # 触发成功信号，把 token 传出去
                self.login_success_signal.emit(token)
                self.close()

            else:
                # 登录失败，增加计数
                self.fail_count += 1

                # 获取错误信息
                error_msg = response_data.get("detail", "登录失败，未知错误")

                # 检查是否达到锁定阈值
                if self.fail_count >= self.max_fail_count:
                    # 触发锁定
                    self.lock_until = datetime.now() + timedelta(seconds=self.lock_duration)
                    lock_error = f"登录失败次数过多，已锁定 {self.lock_duration} 秒\n\n错误详情：{error_msg}"
                    QMessageBox.critical(self, "安全警告", lock_error)

                    # 开始倒计时
                    self.start_lock_countdown()
                else:
                    remaining_attempts = self.max_fail_count - self.fail_count
                    user_error_msg = f"{error_msg}\n\n剩余尝试次数：{remaining_attempts}"
                    QMessageBox.critical(self, "授权错误", user_error_msg)

                    # 恢复按钮状态（未被锁定的情况）
                    self.login_button.setEnabled(True)
                    self.login_button.setText("验证并登录系统")

        except Exception as e:
            # 网络异常或其他错误
            error_type = type(e).__name__
            if "Timeout" in error_type or "timeout" in str(e).lower():
                error_display = "网络超时，请检查网络连接后重试"
            elif "Connection" in error_type or "connect" in str(e).lower():
                error_display = "无法连接服务器，请检查网络连接"
            else:
                error_display = f"登录异常：{str(e)}"

            QMessageBox.critical(self, "网络错误", error_display)

            # 恢复按钮状态
            self.login_button.setEnabled(True)
            self.login_button.setText("验证并登录系统")

            # 注意：网络异常不计入失败次数（避免误锁定）

    def closeEvent(self, event):
        """窗口关闭时清理定时器"""
        if self.lock_timer and self.lock_timer.isActive():
            self.lock_timer.stop()
        event.accept()