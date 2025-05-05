# exports/latex_export.py

import os
from datetime import datetime

class LaTeXExporter:
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def export(self, question_text, answer_text, header="Generated Problems", num_questions=1, filename=None):
        """
        Creates a .tex file, compiles it to PDF, and returns the PDF path.
        """
        if filename:
            tex_filename = f"{os.path.splitext(os.path.basename(filename))[0]}.tex"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            tex_filename = f"{header.replace(' ', '_')}_{timestamp}.tex"

        filepath = os.path.join(self.output_dir, tex_filename)

        latex_content = self._build_latex(header, question_text, answer_text)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(latex_content)

        # Compile LaTeX to PDF using pdflatex
        os.system(f'pdflatex -interaction=nonstopmode -output-directory="{self.output_dir}" "{filepath}"')

        pdf_filename = tex_filename.replace(".tex", ".pdf")
        return os.path.join(self.output_dir, pdf_filename)

    def _build_latex(self, header, question_text, answer_text):
        """
        Internal method for export() that wraps question/answer in a LaTeX structure.
        """
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

\title{{{header}}}
\author{{}}  % Prevent maketitle failure
\date{{}}

\begin{{document}}
\maketitle

\section*{{Questions}}
\begin{{enumerate}}[label=\textbf{{\arabic*.}}]
{self._format_problems(question_text)}
\end{{enumerate}}

\newpage
\section*{{Answer Key}}
\begin{{enumerate}}[label=\textbf{{\arabic*.}}]
{self._format_problems(answer_text)}
\end{{enumerate}}

\end{{document}}
""".strip()

    def _format_problems(self, text_block):
        """
        Turns a double-newline-separated string into LaTeX \item blocks.
        """
        lines = text_block.strip().split("\n\n")
        return "\n".join([f"  \\item {line.strip()}" for line in lines])

    def build_latex(self, question_text, answer_text, header, num_questions):
        """
        Used by preview renderer. Returns raw LaTeX string (no file writing).
        """
        return rf"""
\documentclass[12pt]{{article}}
\usepackage{{amsmath, amssymb, geometry}}
\geometry{{margin=1in}}

\title{{{header}}}
\author{{}}  % Required for \maketitle
\date{{}}

\begin{{document}}
\maketitle

\section*{{Questions}}
{question_text}

\newpage
\section*{{Answer Key}}
{answer_text}

\end{{document}}
""".strip()
