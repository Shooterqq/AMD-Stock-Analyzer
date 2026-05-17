from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

class DocWindow(QWidget):
    def __init__(self, url):
        super().__init__()

        self.setWindowTitle("EDGAR Document")
        self.resize(1200, 900)

        layout = QVBoxLayout(self)

        self.viewer = QWebEngineView()
        layout.addWidget(self.viewer)

        settings = self.viewer.settings()
        settings.setAttribute(
            settings.WebAttribute.PluginsEnabled,
            True
        )

        self.viewer.load(QUrl(url))

        self.show()