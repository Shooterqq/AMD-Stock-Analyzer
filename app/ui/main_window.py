import ctypes
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QLabel
)

from app.services.stock_service import get_stock_analysis


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.dark_style = """
        QWidget {
            background-color: #121212;
            color: #e0e0e0;
        }

        QLineEdit, QTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #333;
            padding: 5px;
        }

        QPushButton {
            background-color: #2d2d2d;
            border: 1px solid #444;
            padding: 6px;
        }

        QPushButton:hover {
            background-color: #3a3a3a;
        }

        QLabel {
            color: #e0e0e0;
        }
        """

        self.setWindowTitle("Stock Analyzer")
        self.setStyleSheet(self.dark_style)
        self.setMinimumSize(350, 200)
        layout = QVBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter ticker (e.g. AMD)")

        self.button = QPushButton("Analyze")

        self.result_label = QLabel("Result will appear here")

        layout.addWidget(self.input)
        layout.addWidget(self.button)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

        # event
        self.button.clicked.connect(self.on_click)

    def on_click(self):
        ticker = self.input.text()

        if not ticker:
            self.result_label.setText("Enter ticker")
            return

        try:
            result = get_stock_analysis(ticker)

            decision = result["analysis"]["decision"]
            score = result["analysis"]["score"]

            self.result_label.setText(
                f"{ticker}: {decision} (score={score})"
            )

        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")


def set_dark_title_bar(win_id):
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Windows 10/11

    value = ctypes.c_int(1)

    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        ctypes.c_void_p(win_id),
        DWMWA_USE_IMMERSIVE_DARK_MODE,
        ctypes.byref(value),
        ctypes.sizeof(value)
    )
