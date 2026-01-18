from flask import Flask, request, send_file, jsonify
from pdf2docx import Converter
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
import pytesseract
from docx import Document
import os, uuid

app = Flask(__name__)

UPLOAD = "uploads"
OUTPUT = "output"

os.makedirs(UPLOAD, exist_ok=True)
os.makedirs(OUTPUT, exist_ok=True)

def is_text_pdf(path):
    text = extract_text(path)
    return bool(text and text.strip())

@app.route("/")
def home():
    return jsonify({"status": "PDF to Word backend running"})

@app.route("/convert", methods=["POST"])
def convert():
    file = request.files["file"]

    uid = str(uuid.uuid4())
    pdf_path = f"{UPLOAD}/{uid}.pdf"
    docx_path = f"{OUTPUT}/{uid}.docx"

    file.save(pdf_path)

    # TEXT PDF
    if is_text_pdf(pdf_path):
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()

    # SCANNED PDF (OCR)
    else:
        pages = convert_from_path(pdf_path, dpi=300)
        doc = Document()
        for page in pages:
            text = pytesseract.image_to_string(page, lang="eng")
            doc.add_paragraph(text)
        doc.save(docx_path)

    return send_file(docx_path, as_attachment=True)

if __name__ == "__main__":
    app.run()
