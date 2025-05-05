import subprocess
import tempfile
import os

def render_latex_to_pdf(latex_code: str, output_path: str = "output.pdf") -> str:
    """
    Compiles LaTeX code into a PDF using pdflatex.
    Returns the path to the generated PDF or an empty string if it fails.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = os.path.join(tmpdir, "temp.tex")
        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(latex_code)

        try:
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file],
                cwd=tmpdir,
                check=True
            )
            pdf_path = os.path.join(tmpdir, "temp.pdf")
            os.replace(pdf_path, output_path)
            return os.path.abspath(output_path)
        except subprocess.CalledProcessError as e:
            print("LaTeX compilation failed:", e)
            return ""
