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
)

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView

import pyqtgraph as pg

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

def analyze_spm(html_text: str):
    matches = re.findall(
        r'<span class="SmallFormData">\s*([SPM])\s*</span>',
        html_text
    )

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

        self.setWindowTitle("EDGAR ANALYZER")
        self.resize(1600, 850)

        layout = QHBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Form", "Date", "S", "P", "M"])

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        layout.addWidget(self.table, 3)

        right = QVBoxLayout()

        self.title = QLabel("AMD - Advanced Micro Devices")
        self.title.setFont(QFont("Arial", 14))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right.addWidget(self.title)

        # CHART
        self.graph = pg.PlotWidget()
        self.graph.setBackground("black")
        self.graph.showGrid(x=True, y=True, alpha=0.3)

        self.graph.setLabel("left", "Price", units="$")
        self.graph.setLabel("bottom", "Time")

        self.graph.setMouseEnabled(x=False, y=False)
        self.graph.setMenuEnabled(False)
        self.graph.hideButtons()

        right.addWidget(self.graph, 8)

        btn_row = QHBoxLayout()

        for label, period in [
            ("1M", "1mo"),
            ("6M", "6mo"),
            ("12M", "1y"),
            ("24M", "2y"),
            ("5Y", "5y"),
            ("MAX", "max"),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, p=period: self.load_chart(p))
            btn_row.addWidget(btn)

        right.addLayout(btn_row)

        container = QWidget()
        container.setLayout(right)

        layout.addWidget(container, 4)

        self.edgar = Edgar("0000002488")
        self.data = self.edgar.filings()

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
        self.table.itemDoubleClicked.connect(self.on_click)

        self.windows = []

        self.load_chart("6mo")

    def load_chart(self, period="6mo"):
        self.graph.clear()

        data = yf.Ticker("AMD").history(period=period)

        self.graph.plot(data["Close"].values, pen="y")

        self.title.setText(f"AMD - Advanced Micro Devices ({period})")

    def on_click(self, item):
        row = item.row()

        form, date, acc, doc = self.data[row]

        acc_no = acc.replace("-", "")

        url = (
            f"https://www.sec.gov/Archives/edgar/data/"
            f"{int(self.edgar.cik)}/{acc_no}/{doc}"
        )

        print("OPEN:", url)

        if doc.lower().endswith(".pdf"):
            webbrowser.open(url)
            return

        win = DocWindow(url)
        self.windows.append(win)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())