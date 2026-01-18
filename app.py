from flask import Flask, request, send_file, jsonify
from pdf2docx import Converter
from pdfminer.high_level import extract_text
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
    return jsonify({"status":"PDF to Word backend running"})

@app.route("/convert", methods=["POST"])
def convert():
    file = request.files["file"]
    uid = str(uuid.uuid4())
    pdf_path = f"{UPLOAD}/{uid}.pdf"
    docx_path = f"{OUTPUT}/{uid}.docx"
    file.save(pdf_path)

    # Convert only text PDFs (skip OCR for now)
    if is_text_pdf(pdf_path):
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        return send_file(docx_path, as_attachment=True)
    else:
        return jsonify({"error": "Scanned PDF OCR not supported in free tier"}), 400

if __name__ == "__main__":
    app.run()
