# ui/problem_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class ProblemDialog(QDialog):
    def __init__(self, generator, parent=None):
        super().__init__(parent)
        self.generator = generator
        self.setWindowTitle("Generate Problems")

        self.layout = QVBoxLayout()
        self.instructions = QLabel("How many problems would you like to generate?")
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Enter number")

        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate_problems)

        self.layout.addWidget(self.instructions)
        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.generate_button)
        self.setLayout(self.layout)

        self.questions = ""
        self.answers = ""

    def generate_problems(self):
        try:
            num = int(self.input_box.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number.")
            return

        questions = []
        answers = []
        for _ in range(num):
            q, a = self.generator.generate_problem()
            questions.append(q)
            answers.append(a)

        self.questions = "\n\n".join(questions)
        self.answers = "\n\n".join(answers)
        self.accept()  # Close dialog and return
