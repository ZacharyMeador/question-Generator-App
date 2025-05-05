# ui/main_window.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTextEdit,
    QMessageBox, QLineEdit, QLabel, QListWidget, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from exports.latex_export import LaTeXExporter
from pdf2image import convert_from_path
from PIL import Image
from exports.pdf_preview import convert_pdf_to_image
import os
from pdf_renderer import render_latex_to_pdf


class MainWindow(QWidget):
    def __init__(self, generator=None):
        super().__init__()
        self.generator = generator
        self.exporter = LaTeXExporter()
        self.question = ""
        self.answer = ""
        self.preview_path = ""
        self.poppler_path = r"C:\poppler-24.08.0\Library\bin"  # Update if needed
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Stats Worksheet Generator")

        # --- Outer layout (horizontal) ---
        outer_layout = QHBoxLayout()

        # --- Left panel: Problem type list ---
        self.problem_list = QListWidget()
        self.problem_list.addItem("Mean")
        self.problem_list.addItem("Median")
        self.problem_list.currentItemChanged.connect(self.change_generator)

        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Select Question Type:"))
        left_panel.addWidget(self.problem_list)

        left_container = QWidget()
        left_container.setLayout(left_panel)
        outer_layout.addWidget(left_container, 1)  # Stretch factor 1

        # --- Right panel: Everything else ---
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

        # Add a PDF render test button
        self.pdf_button = QPushButton("Render Sample PDF")
        self.pdf_button.clicked.connect(self.handle_render_pdf)
        left_panel.addWidget(self.pdf_button)  # Or left_layout if it's a local variable

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
        right_panel.addWidget(self.preview_label)

        right_container = QWidget()
        right_container.setLayout(right_panel)
        outer_layout.addWidget(right_container, 3)  # Stretch factor 3

        # Apply layout
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
            else:
                raise ImportError
        except ImportError:
            QMessageBox.warning(self, "Not Implemented", f"{selected} is not implemented.")

    def generate_problem(self):
        try:
            num = int(self.num_questions_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number of questions.")
            return

        questions = []
        answers = []
        for _ in range(num):
            q, a = self.generator.generate_problem()
            questions.append(q)
            answers.append(a)

        self.question = "\n\n".join(questions)
        self.answer = "\n\n".join(answers)

        self.question_display.setText(self.question)
        self.answer_display.setText(self.answer)

        # --- Auto-generate PDF and preview image ---
        temp_pdf_path = self.exporter.export(
            self.question,
            self.answer,
            header="Preview (Not Saved)",
            num_questions=len(questions),
            filename="temp_preview"  # Optional custom name
        )

        preview_path = convert_pdf_to_image(temp_pdf_path, self.poppler_path)

        if preview_path and os.path.exists(preview_path):
            pixmap = QPixmap(preview_path)
            label_size = self.preview_label.size()
            self.preview_label.setPixmap(pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))   # Adjust size as needed
            print(f"[Preview] Auto-preview updated: {preview_path}")
        else:
            self.preview_label.setText("Failed to generate preview.")
            print("[Preview Error] from auto-preview")

    def export_to_pdf(self):
        if not self.question or not self.answer:
            QMessageBox.warning(self, "Missing Content", "Please generate a problem first.")
            return

        header = self.header_input.text().strip()
        if not header:
            header = "Generated Worksheet"

        try:
            num = int(self.num_questions_input.text())
        except ValueError:
            num = 1

        # Export PDF
        pdf_path = self.exporter.export(self.question, self.answer, header=header, num_questions=num)
        print(f"[Export] PDF saved at {pdf_path}")

        preview_path = convert_pdf_to_image(pdf_path, self.poppler_path)

        # Display preview
        if preview_path and os.path.exists(preview_path):
            pixmap = QPixmap(preview_path)
            self.preview_label.setPixmap(pixmap)
            print(f"[Preview] Preview image loaded: {preview_path}")
        else:
            self.preview_label.setText("Could not generate preview.")
            print("[Preview Error] Failed to load preview image.")

    def handle_render_pdf(self):
        sample_latex = r"""
        \documentclass{article}
        \usepackage{amsmath}
        \begin{document}
        Hello, this is a test of rendering LaTeX to PDF.

        Here's a math example:
        \[
            \int_0^1 x^2 \, dx = \frac{1}{3}
        \]
        \end{document}
        """
        pdf_path = render_latex_to_pdf(sample_latex, output_path="exports/sample_render.pdf")
        if pdf_path:
            print(f"PDF generated at: {pdf_path}")
        else:
            print("PDF generation failed.")

    def resizeEvent(self, event):
        if hasattr(self, 'preview_path') and os.path.exists(self.preview_path):
            pixmap = QPixmap(self.preview_path)
            self.preview_label.setPixmap(pixmap.scaledToWidth(self.preview_label.width()))
        super().resizeEvent(event)

