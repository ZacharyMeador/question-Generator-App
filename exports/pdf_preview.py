from pdf2image import convert_from_path
import os

def convert_pdf_to_image(pdf_path, poppler_path):
    try:
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
        if images:
            image_path = os.path.splitext(pdf_path)[0] + "_preview.png"
            images[0].save(image_path, "PNG")
            return image_path
    except Exception as e:
        print(f"[Error converting PDF to image] {e}")
    return None
