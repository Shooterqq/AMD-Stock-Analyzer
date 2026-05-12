from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon


class LoadingWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Loading data...")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setFixedSize(400, 120)

        layout = QVBoxLayout(self)

        self.label = QLabel("Downloading data from SEC API...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)