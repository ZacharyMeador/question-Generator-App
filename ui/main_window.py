# ui/main_window.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTextEdit,
    QMessageBox, QLineEdit, QLabel, QListWidget, QHBoxLayout,
    QFileDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from exports.latex_export import LaTeXExporter
from exports.pdf_preview import convert_pdf_to_image
from exports.preview_renderer import PreviewRenderer
import os
from pdf_renderer import render_latex_to_pdf


class MainWindow(QWidget):
    def __init__(self, generator=None):
        super().__init__()
        self.generator = generator
        self.exporter = LaTeXExporter()
        self.preview_renderer = PreviewRenderer(poppler_path=r"C:\poppler-24.08.0\Library\bin")
        self.question = ""
        self.answer = ""
        self.preview_path = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Stats Worksheet Generator")

        outer_layout = QHBoxLayout()

        # LEFT PANEL
        self.problem_list = QListWidget()
        self.problem_list.addItems(["Mean", "Median"])
        self.problem_list.currentItemChanged.connect(self.change_generator)

        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Select Question Type:"))
        left_panel.addWidget(self.problem_list)

        self.pdf_button = QPushButton("Render Sample PDF")
        self.pdf_button.clicked.connect(self.handle_render_pdf)
        left_panel.addWidget(self.pdf_button)

        left_container = QWidget()
        left_container.setLayout(left_panel)
        outer_layout.addWidget(left_container, 1)

        # RIGHT PANEL
        right_panel = QVBoxLayout()

        self.header_input = QLineEdit()
        self.header_input.setPlaceholderText("Enter worksheet title (e.g., Mean Problems)")
        right_panel.addWidget(self.header_input)

        self.num_questions_input = QLineEdit()
        self.num_questions_input.setPlaceholderText("How many questions?")
        right_panel.addWidget(self.num_questions_input)

        self.generate_button = QPushButton("Generate Problem")
        self.generate_button.clicked.connect(self.generate_problem)
        right_panel.addWidget(self.generate_button)

        self.export_button = QPushButton("Export to PDF")
        self.export_button.clicked.connect(self.export_to_pdf)
        right_panel.addWidget(self.export_button)

        self.question_display = QTextEdit()
        self.question_display.setReadOnly(True)
        right_panel.addWidget(self.question_display)

        self.answer_display = QTextEdit()
        self.answer_display.setReadOnly(True)
        right_panel.addWidget(self.answer_display)

        self.preview_label = QLabel("PDF Preview will show here.")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(500, 400)
        self.preview_label.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        right_panel.addWidget(self.preview_label)

        right_container = QWidget()
        right_container.setLayout(right_panel)
        outer_layout.addWidget(right_container, 3)

        self.setLayout(outer_layout)

    def change_generator(self):
        selected = self.problem_list.currentItem().text()
        try:
            if selected == "Mean":
                from generators.mean import MeanProblemGenerator
                self.generator = MeanProblemGenerator()
            elif selected == "Median":
                from generators.median import MedianProblemGenerator
                self.generator = MedianProblemGenerator()
        except ImportError:
            QMessageBox.warning(self, "Not Implemented", f"{selected} not implemented yet.")

    def generate_problem(self):
        try:
            num = int(self.num_questions_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Enter a valid number.")
            return

        questions, answers = [], []
        for _ in range(num):
            q, a = self.generator.generate_problem()
            questions.append(q)
            answers.append(a)

        self.question = "\n\n".join(questions)
        self.answer = "\n\n".join(answers)
        self.question_display.setText(self.question)
        self.answer_display.setText(self.answer)

        self.generate_preview_pdf()

    def generate_preview_pdf(self):
        print("[DEBUG] Starting generate_preview_pdf()")
        try:
            latex_code = self.exporter.build_latex(
                self.question, self.answer,
                header="Preview (Not Saved)",
                num_questions=self.question.count('\n\n') + 1
            )
            print("[DEBUG] LaTeX code built successfully")
            preview_path = self.preview_renderer.render(latex_code)
            print(f"[DEBUG] Render result: {preview_path}")
        except Exception as e:
            print(f"[ERROR] Exception during rendering: {e}")
            self.preview_label.setText("Render error.")
            return

        if preview_path and os.path.exists(preview_path):
            self.preview_path = preview_path
            debug_path = os.path.join("exports", "debug_preview.png")

            def delayed_preview():
                try:
                    pixmap = QPixmap(preview_path)
                    pixmap.save(debug_path)
                    scaled = pixmap.scaled(
                        self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.preview_label.setPixmap(scaled)
                    print(f"[DEBUG] Saved preview image to: {debug_path}")
                except Exception as e:
                    print(f"[ERROR] Failed to update preview: {e}")
                    self.preview_label.setText("Failed to display preview.")

            QTimer.singleShot(100, delayed_preview)
        else:
            self.preview_label.setText("Failed to generate preview.")
            print("[Preview Error] File missing.")

    def export_to_pdf(self):
        if not self.question or not self.answer:
            QMessageBox.warning(self, "Missing", "Generate a problem first.")
            return

        header = self.header_input.text().strip() or "Generated Worksheet"
        try:
            num = int(self.num_questions_input.text())
        except ValueError:
            num = 1

        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not save_path:
            return

        pdf_path = self.exporter.export(
            self.question, self.answer, header=header, num_questions=num, filename=save_path
        )

        self.preview_path = convert_pdf_to_image(pdf_path, self.preview_renderer.poppler_path)
        if self.preview_path and os.path.exists(self.preview_path):
            pixmap = QPixmap(self.preview_path)
            self.preview_label.setPixmap(pixmap.scaled(
                self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        else:
            self.preview_label.setText("Failed to load export preview.")

    def handle_render_pdf(self):
        sample_latex = r"""
        \documentclass{article}
        \usepackage{amsmath}
        \begin{document}
        Hello, this is a test.

        \[
        \int_0^1 x^2 \, dx = \frac{1}{3}
        \]
        \end{document}
        """
        path = render_latex_to_pdf(sample_latex, "exports/sample_render.pdf")
        print(f"PDF generated at: {path}" if path else "PDF generation failed.")

    def resizeEvent(self, event):
        if self.preview_path and os.path.exists(self.preview_path):
            pixmap = QPixmap(self.preview_path)
            scaled = pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio)
            self.preview_label.setPixmap(scaled)
        super().resizeEvent(event)
