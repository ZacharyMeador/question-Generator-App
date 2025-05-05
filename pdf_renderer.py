from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import sys

class PDFWindow(QMainWindow):
    def __init__(self, pdf_path):
        super().__init__()
        self.setWindowTitle("Rendered LaTeX Output")

        view = QWebEngineView()
        view.load(QUrl.fromLocalFile(pdf_path))

        layout = QVBoxLayout()
        layout.addWidget(view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFWindow("output.pdf")
    window.show()
    sys.exit(app.exec_())
