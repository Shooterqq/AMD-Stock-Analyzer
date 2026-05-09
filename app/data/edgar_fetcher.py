import os
import sys
import requests
import webbrowser

os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
QAbstractItemView,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt

FORM_DESCRIPTIONS = {
    "4": "Form 4 - Insider Trading",
    "10-K": "Annual Report",
    "10-Q": "Quarterly Report",
    "8-K": "Current Report",
    "ARS": "Annual Report to Shareholders",
    "DEF 14A": "Proxy Statement",
    "DEFA14A": "Proxy Statement Amendment",
    "SCHEDULE 13G": "Large Ownership Report",
    "SCHEDULE 13G/A": "Large Ownership Amendment",
    "13F-HR": "Institutional Holdings Report",
    "144": "Notice of Proposed Stock Sale",
}

headers = {"User-Agent": "MyApp piotr.wiski1@gmail.com"}


class Edgar:
    def __init__(self, cik):
        self.cik = cik
        self.recent = None

    def load_cik(self):
        url = f"https://data.sec.gov/submissions/CIK{self.cik}.json"
        self.recent = requests.get(url, headers=headers).json()["filings"]["recent"]

    def filings(self, limit=100):
        if self.recent is None:
            self.load_cik()

        return list(zip(
            self.recent["form"][:limit],
            self.recent["filingDate"][:limit],
            self.recent["accessionNumber"][:limit],
            self.recent["primaryDocument"][:limit],
        ))


class DocWindow(QWidget):
    def __init__(self, url):
        super().__init__()

        self.setWindowTitle("EDGAR VIEWER")
        self.resize(1000, 700)

        layout = QVBoxLayout(self)

        self.viewer = QWebEngineView(self)
        layout.addWidget(self.viewer)

        self.viewer.setUrl(QUrl(url))
        self.show()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("EDGAR")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # TABLE
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Form", "Date"])
        layout.addWidget(self.table)

        self.edgar = Edgar("0000002488")
        self.data = self.edgar.filings()

        self.table.setRowCount(len(self.data))

        for row, (form, date, acc, doc) in enumerate(self.data):

            description = FORM_DESCRIPTIONS.get(form, form)

            self.table.setItem(row, 0, QTableWidgetItem(description))
            self.table.setItem(row, 1, QTableWidgetItem(date))

        self.table.resizeColumnsToContents()

        self.table.itemDoubleClicked.connect(self.on_click)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setTabKeyNavigation(False)

        self.windows = []

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

