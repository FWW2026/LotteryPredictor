# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtGui import QIcon # or PyQt6.QtGui
from ui.login_window import LoginWindow


class MainWindow(QMainWindow):
    """这是登录成功后才会展现的软件主界面"""

    def __init__(self, token):
        super().__init__()
        self.token = token  # 保存当前会话的 JWT Token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("DouyinLeadFinder - 核心控制台")
        self.resize(1000, 650)
        # 设置窗口图标
        self.setWindowIcon(QIcon("icons/logo.ico"))

        # 简单展示，证明进入了主界面
        center_label = QLabel("欢迎使用 DouyinLeadFinder 系统！\n主程序核心逻辑已准备就绪。")
        center_label.setStyleSheet("font-size: 24px; text-align: center; color: #333;")
        self.setCentralWidget(center_label)


def run_app():
    app = QApplication(sys.argv)

    # 1. 实例化登录窗口
    login_win = LoginWindow()

    # 2. 定义登录成功后的跳转槽函数
    def on_login_success(token):
        global main_win  # 保持引用，防止被垃圾回收
        main_win = MainWindow(token)
        main_win.show()

    # 3. 绑定信号
    login_win.login_success_signal.connect(on_login_success)

    # 4. 显示登录界面
    login_win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()