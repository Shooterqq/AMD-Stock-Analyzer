from PyQt5.QtWidgets import QApplication
import sys

from app.ui.main_window import MainWindow
from app.ui.main_window import set_dark_title_bar


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    set_dark_title_bar(int(window.winId()))

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()