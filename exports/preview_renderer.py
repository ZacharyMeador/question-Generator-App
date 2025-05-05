# preview_renderer.py

import os
import tempfile
import subprocess
from pdf2image import convert_from_path

class PreviewRenderer:
    def __init__(self, poppler_path):
        self.poppler_path = poppler_path

    def render(self, latex_code: str) -> str:
        #print("[DEBUG] Starting render()")

        with tempfile.TemporaryDirectory() as temp_dir:
            tex_path = os.path.join(temp_dir, "temp.tex")
            pdf_path = os.path.join(temp_dir, "temp.pdf")
            preview_path = os.path.join(temp_dir, "temp_preview.png")

            #print("[DEBUG] LaTeX content being written:")
            #print("-" * 40)
            #print(latex_code)
            #print("-" * 40)

            # Write LaTeX code to .tex file
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(latex_code)

            #print("[DEBUG] Writing LaTeX to temp file...")

            # Run pdflatex
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "temp.tex"],
                cwd=temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                print("[ERROR] pdflatex failed:")
                print(result.stdout)
                print(result.stderr)
                return ""

            if not os.path.exists(pdf_path):
                print("[ERROR] PDF not generated")
                return ""

            #print("[DEBUG] Converting PDF to PNG preview...")
            images = convert_from_path(pdf_path, poppler_path=self.poppler_path)

            if not images:
                print("[ERROR] No images returned by convert_from_path()")
                return ""

            # Save the first page of the PDF as an image
            images[0].save(preview_path, "PNG")
            #print("[DEBUG] Saved preview to:", preview_path)

            # Copy it to your static output directory if needed
            final_path = os.path.join("exports", "output", "temp_preview.png")
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            images[0].save(final_path)

            return final_path
