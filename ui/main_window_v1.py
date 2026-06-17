from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QMessageBox,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QSpinBox,
    QComboBox,
    QSplitter
)

from PySide6.QtCore import Qt

from workers.predict_worker import PredictWorker
from workers.fetch_worker import FetchWorker

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
            "澳门六合彩数据分析工具 V2.0"
        )

        self.resize(1400, 900)

        root = QVBoxLayout(self)

        # ====================
        # 数据获取区域
        # ====================

        top = QHBoxLayout()

        root.addLayout(top)

        top.addWidget(QLabel("URL"))

        self.url_edit = QLineEdit()
        self.url_edit.setText(DEFAULT_URL)

        top.addWidget(self.url_edit)

        self.check_btn = QPushButton("检查URL")
        top.addWidget(self.check_btn)

        top.addWidget(QLabel("获取期数"))

        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(1)
        self.count_spin.setMaximum(10000)
        self.count_spin.setValue(500)

        top.addWidget(self.count_spin)

        self.fetch_btn = QPushButton("获取数据")
        top.addWidget(self.fetch_btn)

        self.export_btn = QPushButton("导出原始数据")
        top.addWidget(self.export_btn)

        self.info_label = QLabel("未检测")

        top.addWidget(self.info_label)

        # ====================
        # 预测区域
        # ====================

        predict_layout = QHBoxLayout()

        root.addLayout(predict_layout)

        predict_layout.addWidget(
            QLabel("历史依据")
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

        self.history_combo.setCurrentText("100")

        predict_layout.addWidget(
            self.history_combo
        )

        self.predict_btn = QPushButton(
            "开始预测"
        )

        predict_layout.addWidget(
            self.predict_btn
        )

        self.predict_status = QLabel(
            "未预测"
        )

        predict_layout.addWidget(
            self.predict_status
        )

        predict_layout.addStretch()

        # ====================
        # 主显示区
        # ====================

        splitter = QSplitter(
            Qt.Horizontal
        )

        root.addWidget(splitter)

        self.table = QTableWidget()

        splitter.addWidget(
            self.table
        )

        self.result_table = QTableWidget()

        splitter.addWidget(
            self.result_table
        )

        splitter.setSizes([
            800,
            600
        ])

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

    def show_prediction(
            self,
            result
    ):

        self.predict_result = result

        self.predict_status.setText(
            "预测完成"
        )

        rows = []

        for method, data in (
                result.items()
        ):

            for number, prob in (
                    data["number"].items()
            ):
                rows.append([
                    method,
                    "号码",
                    str(number),
                    round(
                        prob * 100,
                        4
                    )
                ])

            for zodiac, prob in (
                    data["zodiac"].items()
            ):
                rows.append([
                    method,
                    "生肖",
                    zodiac,
                    round(
                        prob * 100,
                        4
                    )
                ])

        self.result_table.setRowCount(
            len(rows)
        )

        self.result_table.setColumnCount(
            4
        )

        self.result_table.setHorizontalHeaderLabels(
            [
                "方法",
                "类型",
                "值",
                "概率(%)"
            ]
        )

        for row, values in (
                enumerate(rows)
        ):

            for col, value in (
                    enumerate(values)
            ):
                self.result_table.setItem(
                    row,
                    col,
                    QTableWidgetItem(
                        str(value)
                    )
                )

        history_size = int(
            self.history_combo.currentText()
        )

        filename = export_prediction(
            result,
            history_size
        )

        QMessageBox.information(
            self,
            "完成",
            f"预测结果已保存\n{filename}"
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
                f"自动调整为 {history_size}"
            )

        self.predict_status.setText(
            "预测中..."
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

    def check_url(self):

        import requests

        try:

            r = requests.get(
                self.url_edit.text(),
                verify=False,
                timeout=10
            )

            data = r.json()

            if data["code"] != 1:

                raise Exception()

            self.max_records = len(
                data["data"]
            )

            self.info_label.setText(
                f"有效，共{self.max_records}期"
            )

        except Exception as e:

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
                f"自动调整为{count}"
            )

        self.worker = FetchWorker(
            self.url_edit.text(),
            count
        )

        self.worker.finished.connect(
            self.show_records
        )

        self.worker.error.connect(
            self.show_error
        )

        self.worker.start()

    def show_records(self, records):

        self.records = records

        self.table.setColumnCount(7)

        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "年份",
                "期数",
                "日期",
                "号码",
                "生肖",
                "五行"
            ]
        )

        self.table.setRowCount(
            len(records)
        )

        for row, item in enumerate(records):

            self.table.setItem(
                row, 0,
                QTableWidgetItem(
                    str(item["id"])
                )
            )

            self.table.setItem(
                row, 1,
                QTableWidgetItem(
                    str(item["year"])
                )
            )

            self.table.setItem(
                row, 2,
                QTableWidgetItem(
                    item["qishu"]
                )
            )

            self.table.setItem(
                row, 3,
                QTableWidgetItem(
                    item["date"]
                )
            )

            self.table.setItem(
                row, 4,
                QTableWidgetItem(
                    item["num"]
                )
            )

            self.table.setItem(
                row, 5,
                QTableWidgetItem(
                    item["shengxiao"]
                )
            )

            self.table.setItem(
                row, 6,
                QTableWidgetItem(
                    item["wuxing"]
                )
            )

        self.info_label.setText(
            f"已加载 {len(records)} 条"
        )

    def show_error(self, msg):

        QMessageBox.critical(
            self,
            "错误",
            msg
        )

    def export_excel(self):

        if not self.records:

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

        export_records(
            self.records,
            filename
        )

        QMessageBox.information(
            self,
            "完成",
            "导出成功"
        )