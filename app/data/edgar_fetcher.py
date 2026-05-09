import os
import sys
import requests
import webbrowser

os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

headers = {"User-Agent": "MyApp piotr.wiski1@gmail.com"}


class Edgar:
    def __init__(self, cik):
        self.cik = cik
        self.recent = None

    def load_cik(self):
        url = f"https://data.sec.gov/submissions/CIK{self.cik}.json"
        self.recent = requests.get(url, headers=headers).json()["filings"]["recent"]

    def filings(self, limit=20):
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

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.edgar = Edgar("0000002488")
        self.data = self.edgar.filings()

        for form, date, acc, doc in self.data:
            self.list_widget.addItem(f"{form} | {date} | {doc}")

        self.list_widget.itemDoubleClicked.connect(self.on_click)

        self.windows = []

    def on_click(self, item):
        i = self.list_widget.row(item)

        form, date, acc, doc = self.data[i]

        acc_no = acc.replace("-", "")

        url = f"https://www.sec.gov/Archives/edgar/data/{int(self.edgar.cik)}/{acc_no}/{doc}"

        print("OPEN:", url)

        if doc.endswith(".pdf"):
            webbrowser.open(url)
            return

        # XML / HTML → Qt window
        win = DocWindow(url)
        self.windows.append(win)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())