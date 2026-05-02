from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QLabel
)

from app.services.stock_service import get_stock_analysis


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stock Analyzer")
        self.setMinimumSize(300, 150)
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