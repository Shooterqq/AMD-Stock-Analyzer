import os
import sys
import re
import requests
import webbrowser
import yfinance as yf

os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

from PyQt6.QtWidgets import (
    QApplication,
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
)

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
import pyqtgraph as pg
from PyQt6.QtGui import QIcon

FORM_DESCRIPTIONS = {
    "4": "Form 4 - Insider Trading",
    "10-K": "Annual Report",
    "10-Q": "Quarterly Report",
    "8-K": "Current Report",
    "ARS": "Annual Report to Shareholders",
    "DEF 14A": "Proxy Statement",
    "13F-HR": "Institutional Holdings Report",
    "144": "Notice of Proposed Stock Sale",
}

headers = {"User-Agent": "MyApp piotr.wiski1@gmail.com"}

TICKER_TO_CIK = {
    "AMD": "0000002488",
    "NVDA": "0001045810",
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "GOOGL": "0001652044",
    "AMZN": "0001018724",
    "TSLA": "0001318605",
    "META": "0001326801",
    "AVGO": "0001730168",
    "TXN": "0000097476",
    "ADI": "0000006281",
    "ARM": "0001973239",
    "TSM": "0001046179",
    "ASML": "0000937966",
    "MCD": "0000063908",
    "ORCL": "0001341439",
    "XOM": "0000034088",
    "CVX": "0000093410",
    "NVO": "0000353278",
}


def analyze_spm(html_text: str):
    matches = re.findall(r'<span class="SmallFormData">\s*([SPM])\s*</span>', html_text)
    return (
        matches.count("S"),
        matches.count("P"),
        matches.count("M"),
    )

class Edgar:
    def __init__(self, cik):
        self.cik = cik
        self.recent = None

    def load(self):
        url = f"https://data.sec.gov/submissions/CIK{self.cik}.json"
        self.recent = requests.get(url, headers=headers).json()["filings"]["recent"]

    def filings(self, limit=20):
        if self.recent is None:
            self.load()

        return list(zip(
            self.recent["form"][:limit],
            self.recent["filingDate"][:limit],
            self.recent["accessionNumber"][:limit],
            self.recent["primaryDocument"][:limit],
        ))

class DocWindow(QWidget):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("EDGAR Document")
        self.resize(1100, 800)

        layout = QVBoxLayout(self)

        self.viewer = QWebEngineView(self)
        layout.addWidget(self.viewer)

        self.viewer.setUrl(QUrl(url))
        self.show()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Market Reports Analyzer")
        self.setWindowIcon(QIcon("icon.ico"))
        self.resize(1600, 900)

        main_layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()

        self.ticker_box = QComboBox()
        self.ticker_box.addItems(list(TICKER_TO_CIK.keys()))

        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self.load_ticker)

        self.limit_box = QSpinBox()
        self.limit_box.setRange(0, 100)
        self.limit_box.setValue(20)

        self.limit_btn = QPushButton("Apply limit")
        self.limit_btn.clicked.connect(self.apply_limit)

        top_layout.addWidget(self.ticker_box)
        top_layout.addWidget(self.load_btn)
        top_layout.addWidget(self.limit_box)
        top_layout.addWidget(self.limit_btn)

        main_layout.addLayout(top_layout)

        content = QHBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Form", "Date", "S", "P", "M"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.table.cellDoubleClicked.connect(self.on_click)

        content.addWidget(self.table, 3)

        right = QVBoxLayout()

        self.title = QLabel("")
        self.title.setFont(QFont("Arial", 14))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right.addWidget(self.title)

        self.graph = pg.PlotWidget()
        self.graph.setBackground("black")
        self.graph.showGrid(x=True, y=True, alpha=0.3)
        self.graph.setMouseEnabled(x=False, y=False)
        self.graph.setMenuEnabled(False)
        self.graph.hideButtons()

        self.graph.setLabel("left", "Price", units="USD")
        self.graph.setLabel("bottom", "Time", units="days")

        right.addWidget(self.graph, 8)

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

        right.addLayout(btn_row)

        container = QWidget()
        container.setLayout(right)

        content.addWidget(container, 4)

        main_layout.addLayout(content)

        self.windows = []
        self.current_ticker = "AMD"
        self.edgar = None
        self.data = []
        self.limit = 20

        self.load_all("AMD")

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
        self.data = self.edgar.filings(limit=self.limit)
        self.table.setRowCount(len(self.data))

        for row, (form, date, acc, doc) in enumerate(self.data):

            desc = FORM_DESCRIPTIONS.get(form, form)

            s = p = m = ""

            if form == "4":
                try:
                    acc_no = acc.replace("-", "")
                    url = (
                        f"https://www.sec.gov/Archives/edgar/data/"
                        f"{int(self.edgar.cik)}/{acc_no}/{doc}"
                    )

                    html = requests.get(url, headers=headers).text
                    s, p, m = analyze_spm(html)

                except:
                    s, p, m = "?", "?", "?"

            self.table.setItem(row, 0, QTableWidgetItem(desc))
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem(str(s)))
            self.table.setItem(row, 3, QTableWidgetItem(str(p)))
            self.table.setItem(row, 4, QTableWidgetItem(str(m)))

        self.table.resizeColumnsToContents()

    def load_chart(self, period):
        self.graph.clear()

        data = yf.Ticker(self.current_ticker).history(period=period)
        self.graph.plot(data["Close"].values, pen="y")

        self.title.setText(f"{self.current_ticker} - {period}")

    def on_click(self, row, col):
        form, date, acc, doc = self.data[row]

        acc_no = acc.replace("-", "")

        url = (
            f"https://www.sec.gov/Archives/edgar/data/"
            f"{int(self.edgar.cik)}/{acc_no}/{doc}"
        )

        if doc.lower().endswith(".pdf"):
            webbrowser.open(url)
            return

        win = DocWindow(url)
        self.windows.append(win)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
