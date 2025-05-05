# exports/latex_export.py

import os
from datetime import datetime

class LaTeXExporter:
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def export(self, question_text, answer_text, header="Generated Problems", num_questions=1, filename=None):
        # Determine filename
        if filename:
            tex_filename = f"{filename}.tex"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            tex_filename = f"{header.replace(' ', '_')}_{timestamp}.tex"

        # Full file path
        filepath = os.path.join(self.output_dir, tex_filename)

        # Write LaTeX content to .tex file
        latex_content = self._build_latex(header, question_text, answer_text, num_questions)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(latex_content)

        # Compile the PDF using pdflatex
        os.system(f'pdflatex -output-directory="{self.output_dir}" "{filepath}"')

        # Return the PDF path
        pdf_filename = tex_filename.replace(".tex", ".pdf")
        return os.path.join(self.output_dir, pdf_filename)

    def _build_latex(self, header, question_text, answer_text, num_questions):
        return rf"""
\documentclass[12pt]{{article}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{amsmath, amssymb}}
\usepackage{{fancyhdr}}
\usepackage{{enumitem}}

\pagestyle{{fancy}}
\fancyhf{{}}
\rhead{{\thepage}}
\lhead{{{header}}}

\begin{{document}}

\section*{{{header}}}

\begin{{enumerate}}[label=\textbf{{\arabic*.}}]
{self._format_problems(question_text)}
\end{{enumerate}}

\newpage
\section*{{Answer Key}}

\begin{{enumerate}}[label=\textbf{{\arabic*.}}]
{self._format_problems(answer_text)}
\end{{enumerate}}

\end{{document}}
"""

    def _format_problems(self, text_block):
        lines = text_block.strip().split("\n\n")
        return "\n".join([f"  \\item {line.strip()}" for line in lines])
