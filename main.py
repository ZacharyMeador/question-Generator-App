# main.py
import sys
from PyQt5.QtWidgets import QApplication
from generators.mean import MeanProblemGenerator
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    generator = MeanProblemGenerator()
    window = MainWindow(generator)
    window.show()

    sys.exit(app.exec_())
