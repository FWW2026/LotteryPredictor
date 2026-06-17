from pathlib import Path

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QMessageBox,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QSpinBox,
    QComboBox,
    QSplitter,
    QGroupBox,
    QHeaderView
)

from workers.fetch_worker import FetchWorker
from workers.predict_worker import PredictWorker

from exporters.excel_exporter import export_records
from exporters.prediction_exporter import export_prediction


DEFAULT_URL = (
    "https://gfgaewux.gjpheoighej11.com:3074/"
    "kjapi/index/index/kjdata?g=am"
)


class MainWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.records = []

        self.max_records = 0

        self.predict_result = {}

        self.init_ui()

    def init_ui(self):

        self.setWindowTitle(
            "澳门六合彩数据分析工具 V2.1"
        )

        self.resize(1600, 950)

        self.setStyleSheet("""
            QWidget{
                font-size:13px;
                font-family:Microsoft YaHei;
            }

            QGroupBox{
                font-size:14px;
                font-weight:bold;
                border:1px solid #cfcfcf;
                border-radius:8px;
                margin-top:12px;
                padding-top:12px;
            }

            QGroupBox::title{
                left:10px;
                padding-left:5px;
                padding-right:5px;
            }

            QPushButton{
                min-height:38px;
                min-width:120px;
                border:none;
                border-radius:6px;
                background:#2d89ef;
                color:white;
                font-weight:bold;
            }

            QPushButton:hover{
                background:#4699ff;
            }

            QLineEdit,
            QSpinBox,
            QComboBox{
                min-height:34px;
            }

            QTableWidget{
                gridline-color:#d0d0d0;
            }
        """)

        root = QVBoxLayout(self)

        # ==================================
        # 数据源区域
        # ==================================

        source_group = QGroupBox(
            "数据源设置"
        )

        root.addWidget(source_group)

        source_layout = QVBoxLayout(
            source_group
        )

        source_layout.addWidget(
            QLabel("开奖接口 URL")
        )

        self.url_edit = QLineEdit()

        self.url_edit.setText(
            DEFAULT_URL
        )

        self.url_edit.setMinimumHeight(
            38
        )

        source_layout.addWidget(
            self.url_edit
        )

        status_layout = QHBoxLayout()

        source_layout.addLayout(
            status_layout
        )

        self.info_label = QLabel(
            "● 未连接"
        )

        self.info_label.setStyleSheet("""
            QLabel{
                color:#e74c3c;
                font-weight:bold;
            }
        """)

        status_layout.addWidget(
            self.info_label
        )

        status_layout.addStretch()

        button_layout = QHBoxLayout()

        source_layout.addLayout(
            button_layout
        )

        self.check_btn = QPushButton(
            "检查URL"
        )

        self.fetch_btn = QPushButton(
            "获取数据"
        )

        self.export_btn = QPushButton(
            "导出原始数据"
        )

        button_layout.addWidget(
            self.check_btn
        )

        button_layout.addWidget(
            self.fetch_btn
        )

        button_layout.addWidget(
            self.export_btn
        )

        button_layout.addStretch()

        # ==================================
        # 分析参数区域
        # ==================================

        analysis_group = QGroupBox(
            "分析参数"
        )

        root.addWidget(
            analysis_group
        )

        analysis_layout = QGridLayout(
            analysis_group
        )

        analysis_layout.addWidget(
            QLabel("获取期数"),
            0,
            0
        )

        self.count_spin = QSpinBox()

        self.count_spin.setMinimum(1)

        self.count_spin.setMaximum(
            10000
        )

        self.count_spin.setValue(
            500
        )

        analysis_layout.addWidget(
            self.count_spin,
            0,
            1
        )

        analysis_layout.addWidget(
            QLabel("历史依据"),
            0,
            2
        )

        self.history_combo = QComboBox()

        self.history_combo.addItems([
            "10",
            "20",
            "30",
            "50",
            "100",
            "200",
            "500"
        ])

        self.history_combo.setCurrentText(
            "100"
        )

        analysis_layout.addWidget(
            self.history_combo,
            0,
            3
        )

        self.predict_btn = QPushButton(
            "开始预测"
        )

        analysis_layout.addWidget(
            self.predict_btn,
            0,
            4
        )

        self.predict_status = QLabel(
            "未预测"
        )

        self.predict_status.setStyleSheet("""
            QLabel{
                font-weight:bold;
                color:#666666;
            }
        """)

        analysis_layout.addWidget(
            self.predict_status,
            0,
            5
        )

        analysis_layout.setColumnStretch(
            6,
            1
        )

        # ==================================
        # 主显示区域
        # ==================================

        splitter = QSplitter(
            Qt.Horizontal
        )

        root.addWidget(
            splitter
        )

        # 左侧开奖记录

        left_group = QGroupBox(
            "历史开奖记录"
        )

        left_layout = QVBoxLayout(
            left_group
        )

        self.table = QTableWidget()

        self.table.setAlternatingRowColors(
            True
        )

        left_layout.addWidget(
            self.table
        )

        splitter.addWidget(
            left_group
        )

        # 右侧预测结果

        right_group = QGroupBox(
            "预测结果"
        )

        right_layout = QVBoxLayout(
            right_group
        )

        self.result_table = QTableWidget()

        self.result_table.setAlternatingRowColors(
            True
        )

        right_layout.addWidget(
            self.result_table
        )

        splitter.addWidget(
            right_group
        )

        splitter.setSizes([
            900,
            700
        ])

        # ==================================
        # 信号绑定
        # ==================================

        self.check_btn.clicked.connect(
            self.check_url
        )

        self.fetch_btn.clicked.connect(
            self.fetch_data
        )

        self.export_btn.clicked.connect(
            self.export_excel
        )

        self.predict_btn.clicked.connect(
            self.start_predict
        )
    def check_url(self):

        import requests

        try:

            self.info_label.setText(
                "● 检测中..."
            )

            r = requests.get(
                self.url_edit.text().strip(),
                verify=False,
                timeout=10
            )

            data = r.json()

            if data.get("code") != 1:
                raise Exception(
                    data.get(
                        "msg",
                        "接口返回异常"
                    )
                )

            self.max_records = len(
                data["data"]
            )

            self.info_label.setText(
                f"● 已连接（{self.max_records}期）"
            )

            self.info_label.setStyleSheet("""
                QLabel{
                    color:#27ae60;
                    font-weight:bold;
                }
            """)

        except Exception as e:

            self.info_label.setText(
                "● 连接失败"
            )

            self.info_label.setStyleSheet("""
                QLabel{
                    color:#e74c3c;
                    font-weight:bold;
                }
            """)

            QMessageBox.critical(
                self,
                "错误",
                str(e)
            )

    def fetch_data(self):

        if self.max_records == 0:

            QMessageBox.warning(
                self,
                "提示",
                "请先检查URL"
            )

            return

        count = self.count_spin.value()

        if count > self.max_records:

            count = self.max_records

            QMessageBox.information(
                self,
                "提示",
                f"自动调整为 {count}"
            )

        self.fetch_btn.setEnabled(
            False
        )

        self.worker = FetchWorker(
            self.url_edit.text().strip(),
            count
        )

        self.worker.finished.connect(
            self.show_records
        )

        self.worker.error.connect(
            self.show_error
        )

        self.worker.start()

    def show_records(
        self,
        records
    ):

        self.fetch_btn.setEnabled(
            True
        )

        self.records = records

        headers = [
            "ID",
            "年份",
            "期数",
            "日期",
            "号码",
            "生肖",
            "五行"
        ]

        self.table.setColumnCount(
            len(headers)
        )

        self.table.setHorizontalHeaderLabels(
            headers
        )

        self.table.setRowCount(
            len(records)
        )

        for row, item in enumerate(records):

            values = [

                str(item["id"]),

                str(item["year"]),

                item["qishu"],

                item["date"],

                item["num"],

                item["shengxiao"],

                item["wuxing"]
            ]

            for col, value in enumerate(values):

                self.table.setItem(
                    row,
                    col,
                    QTableWidgetItem(
                        str(value)
                    )
                )

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.info_label.setText(
            f"● 已加载 {len(records)} 条记录"
        )

    def start_predict(self):

        if not self.records:

            QMessageBox.warning(
                self,
                "提示",
                "请先获取数据"
            )

            return

        history_size = int(
            self.history_combo.currentText()
        )

        if history_size > len(
            self.records
        ):

            history_size = len(
                self.records
            )

            QMessageBox.information(
                self,
                "提示",
                f"历史依据自动调整为 {history_size}"
            )

        self.predict_status.setText(
            "预测中..."
        )

        self.predict_btn.setEnabled(
            False
        )

        self.predict_worker = (
            PredictWorker(
                self.records,
                history_size
            )
        )

        self.predict_worker.finished.connect(
            self.show_prediction
        )

        self.predict_worker.start()

    def show_prediction(
        self,
        result
    ):

        self.predict_btn.setEnabled(
            True
        )

        self.predict_result = result

        self.predict_status.setText(
            "预测完成"
        )

        rows = []

        for method, data in result.items():

            number_sorted = sorted(
                data["number"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            zodiac_sorted = sorted(
                data["zodiac"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            for number, prob in number_sorted:

                rows.append([
                    method,
                    "特码号码",
                    number,
                    f"{prob * 100:.4f}%"
                ])

            for zodiac, prob in zodiac_sorted:

                rows.append([
                    method,
                    "特码生肖",
                    zodiac,
                    f"{prob * 100:.4f}%"
                ])

        headers = [
            "预测方法",
            "预测类型",
            "预测值",
            "概率"
        ]

        self.result_table.setColumnCount(
            len(headers)
        )

        self.result_table.setHorizontalHeaderLabels(
            headers
        )

        self.result_table.setRowCount(
            len(rows)
        )

        for row, values in enumerate(rows):

            for col, value in enumerate(values):

                self.result_table.setItem(
                    row,
                    col,
                    QTableWidgetItem(
                        str(value)
                    )
                )

        self.result_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.result_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        history_size = min(
            int(
                self.history_combo.currentText()
            ),
            len(self.records)
        )

        try:

            filename = export_prediction(
                result,
                history_size
            )

            QMessageBox.information(
                self,
                "完成",
                f"预测完成\n\n结果已导出：\n{filename}"
            )

        except Exception as e:

            QMessageBox.warning(
                self,
                "导出失败",
                str(e)
            )

    def export_excel(self):

        if not self.records:

            QMessageBox.warning(
                self,
                "提示",
                "暂无数据"
            )

            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "保存Excel",
            str(
                Path.home()
                / "开奖记录.xlsx"
            ),
            "Excel (*.xlsx)"
        )

        if not filename:
            return

        try:

            export_records(
                self.records,
                filename
            )

            QMessageBox.information(
                self,
                "完成",
                "导出成功"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "错误",
                str(e)
            )

    def show_error(
        self,
        msg
    ):

        self.fetch_btn.setEnabled(
            True
        )

        QMessageBox.critical(
            self,
            "错误",
            msg
        )