import yfinance as yf
import requests

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QPushButton,
    QLabel,
    QComboBox,
    QSpinBox,
    QFrame,
)

from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QFont, QIcon

import pyqtgraph as pg

from core.constants import FORM_DESCRIPTIONS, TICKER_TO_CIK, headers
from core.edgar import Edgar
from utils.analyzer import analyze_spm

from ui.loading_window import LoadingWindow
from ui.doc_window import DocWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.windows = []
        self.current_ticker = "AMD"
        self.edgar = None
        self.data = []
        self.limit = 20

        self.loading_window = LoadingWindow()

        self.setup_window()
        self.setup_main_layout()
        self.setup_ticker_section()
        self.setup_limit_section()
        self.setup_content_section()

        self.load_all("AMD")

    # ---------------- LABELS ----------------

    def setup_window(self):
        self.setWindowTitle("Stock Market Reports Analyzer")
        self.setWindowIcon(QIcon("icon.ico"))
        self.resize(1600, 900)

    def setup_main_layout(self):
        self.main_layout = QVBoxLayout(self)

    def setup_ticker_section(self):
        ticker_label = QLabel("Select ticker")
        self.main_layout.addWidget(ticker_label)

        top_layout = QHBoxLayout()

        self.ticker_box = QComboBox()
        self.ticker_box.addItems(list(TICKER_TO_CIK.keys()))

        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self.load_ticker)

        top_layout.addWidget(self.ticker_box)
        top_layout.addWidget(self.load_btn)

        self.main_layout.addLayout(top_layout)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)

        self.main_layout.addWidget(line1)

    def setup_limit_section(self):
        self.main_layout.addWidget(QLabel("Reports amount"))

        limit_layout = QHBoxLayout()

        self.limit_box = QSpinBox()
        self.limit_box.setRange(0, 100)
        self.limit_box.setValue(20)

        self.limit_btn = QPushButton("Apply limit")
        self.limit_btn.clicked.connect(self.apply_limit)

        limit_layout.addWidget(self.limit_box)
        limit_layout.addWidget(self.limit_btn)

        self.main_layout.addLayout(limit_layout)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)

        self.main_layout.addWidget(line2)

    def setup_content_section(self):
        content_layout = QHBoxLayout()

        self.setup_left_panel(content_layout)
        self.setup_separator(content_layout)
        self.setup_right_panel(content_layout)

        self.main_layout.addLayout(content_layout)

    def setup_left_panel(self, parent_layout):
        left_layout = QVBoxLayout()

        left_layout.addWidget(QLabel("Reports"))

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Form", "Date", "Sale", "Purchase", "Mix"])

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.table.cellDoubleClicked.connect(self.on_click)

        left_layout.addWidget(self.table)
        parent_layout.addLayout(left_layout, 3)

    def setup_separator(self, parent_layout):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        parent_layout.addWidget(sep)

    def setup_right_panel(self, parent_layout):
        right_layout = QVBoxLayout()

        self.title = QLabel("")
        self.title.setFont(QFont("Arial", 14))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        right_layout.addWidget(self.title)

        self.graph = pg.PlotWidget()
        self.graph.setBackground("black")
        self.graph.showGrid(x=True, y=True, alpha=0.3)
        self.graph.setMouseEnabled(x=False, y=False)
        self.graph.setMenuEnabled(False)
        self.graph.hideButtons()
        self.graph.setLabel("left", "Price", units="USD")
        self.graph.setLabel("bottom", "Time", units="days")

        right_layout.addWidget(self.graph, 8)

        btn_row = QHBoxLayout()

        for label, period in [
            ("1M", "1mo"),
            ("6M", "6mo"),
            ("1Y", "1y"),
            ("2Y", "2y"),
            ("5Y", "5y"),
            ("MAX", "max"),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, p=period: self.load_chart(p))
            btn_row.addWidget(btn)

        right_layout.addLayout(btn_row)

        container = QWidget()
        container.setLayout(right_layout)

        parent_layout.addWidget(container, 4)

    # ---------------- LOGIC ----------------

    def ticker_to_cik(self, ticker):
        return TICKER_TO_CIK.get(ticker.upper())

    def apply_limit(self):
        self.limit = self.limit_box.value()
        if self.edgar:
            self.load_filings()

    def load_ticker(self):
        self.load_all(self.ticker_box.currentText())

    def load_all(self, ticker):
        cik = self.ticker_to_cik(ticker)

        if not cik:
            self.title.setText("Unknown ticker")
            return

        self.current_ticker = ticker
        self.edgar = Edgar(cik)

        self.load_chart("6mo")
        self.load_filings()

    def load_filings(self):
        self.loading_window.progress.setValue(0)
        self.loading_window.show()
        QCoreApplication.processEvents()

        self.data = self.edgar.filings(limit=self.limit)
        self.table.setRowCount(len(self.data))

        if not self.data:
            self.loading_window.close()
            return

        total = len(self.data)

        for row, filing in enumerate(self.data):
            self.process_filing(row, filing)
            self.update_progress(row, total)

        self.finish_loading()

    def process_filing(self, row, filing):
        form, date, acc, doc = filing

        desc = FORM_DESCRIPTIONS.get(form, form)
        s, p, m = self.get_form4_analysis(form, acc, doc)

        self.fill_row(row, desc, date, s, p, m)

    def get_form4_analysis(self, form, acc, doc):
        if form != "4":
            return "", "", ""

        try:
            acc_no = acc.replace("-", "")

            url = (f"https://www.sec.gov/Archives/edgar/data/"
                   f"{int(self.edgar.cik)}/{acc_no}/{doc}")

            html = requests.get(url, headers=headers).text

            return analyze_spm(html)

        except Exception:
            return "?", "?", "?"

    def fill_row(self, row, desc, date, s, p, m):
        self.table.setItem(row, 0, QTableWidgetItem(desc))
        self.table.setItem(row, 1, QTableWidgetItem(date))
        self.table.setItem(row, 2, QTableWidgetItem(str(s)))
        self.table.setItem(row, 3, QTableWidgetItem(str(p)))
        self.table.setItem(row, 4, QTableWidgetItem(str(m)))

    def update_progress(self, row, total):
        progress_value = int(((row + 1) / total) * 100)
        self.loading_window.progress.setValue(progress_value)
        QCoreApplication.processEvents()

    def finish_loading(self):
        self.table.resizeColumnsToContents()
        self.loading_window.close()

    def load_chart(self, period):
        self.graph.clear()

        data = yf.Ticker(self.current_ticker).history(period=period)
        self.graph.plot(data["Close"].values, pen="y")

        self.title.setText(f"{self.current_ticker} - {period}")

    def on_click(self, row):
        form, date, acc, doc = self.data[row]

        acc_no = acc.replace("-", "")

        url = (f"https://www.sec.gov/Archives/edgar/data/"
               f"{int(self.edgar.cik)}/{acc_no}/{doc}")

        win = DocWindow(url)
        self.windows.append(win)
        win.show()