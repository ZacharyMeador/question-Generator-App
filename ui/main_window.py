# ui/main_window.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTextEdit,
    QMessageBox, QLineEdit, QLabel, QListWidget, QHBoxLayout,
    QFileDialog, QDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from exports.latex_export import LaTeXExporter
from exports.pdf_preview import convert_pdf_to_image
from exports.preview_renderer import PreviewRenderer
from ui.problem_dialog import ProblemDialog
import os
from pdf_renderer import render_latex_to_pdf


# main_window.py
class MainWindow(QWidget):
    def __init__(self, generator=None):
        super().__init__()
        self.generator = generator
        self.exporter = LaTeXExporter()
        self.preview_renderer = PreviewRenderer(poppler_path=r"C:\poppler-24.08.0\Library\bin")
        self.question = ""
        self.answer = ""
        self.preview_path = ""
        self.num_questions = 1
        self.initializing = True
        self.init_ui()
        # After UI is completely set up:
        self.initializing = False

    def init_ui(self):
        self.setWindowTitle("Stats Worksheet Generator")

        outer_layout = QHBoxLayout()

        # --- Left panel: Problem list ---
        self.problem_list = QListWidget()

        # Disconnect signal temporarily (extra-safe approach)
        try:
            self.problem_list.currentItemChanged.disconnect(self.change_generator)
        except:
            pass  # Safe if wasn't connected yet

        self.problem_list.addItem("Mean")
        self.problem_list.addItem("Median")

        # Explicitly set no selection
        self.problem_list.setCurrentRow(-1)

        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Select Question Type:"))
        left_panel.addWidget(self.problem_list)

        left_container = QWidget()
        left_container.setLayout(left_panel)
        outer_layout.addWidget(left_container, 1)

        # --- Right panel: Controls & preview ---
        right_panel = QVBoxLayout()

        self.header_input = QLineEdit()
        self.header_input.setPlaceholderText("Enter worksheet title (e.g., Mean Problems)")
        right_panel.addWidget(self.header_input)

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
        self.preview_label.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(400)
        self.preview_label.setMinimumWidth(500)
        self.preview_label.setMaximumWidth(600)
        right_panel.addWidget(self.preview_label)

        self.render_button = QPushButton("Render Sample PDF")
        self.render_button.clicked.connect(self.handle_render_pdf)
        right_panel.addWidget(self.render_button)

        right_container = QWidget()
        right_container.setLayout(right_panel)
        outer_layout.addWidget(right_container, 3)

        self.setLayout(outer_layout)

        # Now reconnect the signal explicitly at the end of UI initialization
        self.problem_list.itemClicked.connect(self.change_generator)

    def change_generator(self, item):
        if item is None:
            return

        selected = item.text()
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
            return

        self.show_problem_input_dialog()

    def show_problem_input_dialog(self):
        dialog = ProblemDialog(generator=self.generator, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.num_questions = int(dialog.input_box.text())
                self.question = dialog.questions
                self.answer = dialog.answers
                self.question_display.setText(self.question)
                self.answer_display.setText(self.answer)
                self.generate_preview_pdf()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Problem generation failed: {e}")

    def generate_problem(self):
        questions, answers = [], []
        for _ in range(self.num_questions):
            q, a = self.generator.generate_problem()
            questions.append(q)
            answers.append(a)

        self.question = "\n\n".join(questions)
        self.answer = "\n\n".join(answers)
        self.question_display.setText(self.question)
        self.answer_display.setText(self.answer)

        self.generate_preview_pdf()

    def generate_preview_pdf(self):
        try:
            latex_code = self.exporter.build_latex(
                self.question, self.answer,
                header="Preview (Not Saved)",
                num_questions=self.num_questions
            )
            preview_path = self.preview_renderer.render(latex_code)
        except Exception as e:
            print(f"[ERROR] Exception during rendering: {e}")
            self.preview_label.setText("Render error.")
            return

        if preview_path and os.path.exists(preview_path):
            self.preview_path = preview_path

            def delayed_preview():
                try:
                    pixmap = QPixmap(preview_path)
                    scaled = pixmap.scaled(
                        self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.preview_label.setPixmap(scaled)
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

        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not save_path:
            return

        pdf_path = self.exporter.export(
            self.question, self.answer, header=header, num_questions=self.num_questions, filename=save_path
        )

        self.preview_path = convert_pdf_to_image(pdf_path, self.preview_renderer.poppler_path)
        if self.preview_path and os.path.exists(self.preview_path):
            pixmap = QPixmap(self.preview_path)
            scaled_pixmap = pixmap.scaled(
                self.preview_label.width(),
                self.preview_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
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
        super().resizeEvent(event)
        if hasattr(self, 'preview_path') and os.path.exists(self.preview_path):
            pixmap = QPixmap(self.preview_path)
            scaled_pixmap = pixmap.scaled(
                self.preview_label.width(),
                self.preview_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
