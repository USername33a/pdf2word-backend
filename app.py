from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pdf2docx import Converter
from pdfminer.high_level import extract_text
from docx import Document
from docx.shared import Pt
import os, uuid

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow all origins (Netlify frontend)

# Directories for uploads and outputs
UPLOAD = "uploads"
OUTPUT = "output"
os.makedirs(UPLOAD, exist_ok=True)
os.makedirs(OUTPUT, exist_ok=True)

# Function to check if PDF has selectable text
def is_text_pdf(path):
    text = extract_text(path)
    return bool(text and text.strip())

# Home route
@app.route("/")
def home():
    return jsonify({"status":"PDF to Word backend running"})

# Convert route
@app.route("/convert", methods=["POST"])
def convert():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    uid = str(uuid.uuid4())
    pdf_path = f"{UPLOAD}/{uid}.pdf"
    docx_path = f"{OUTPUT}/{uid}.docx"
    file.save(pdf_path)

    # Convert only text PDFs
    if is_text_pdf(pdf_path):
        # Convert PDF to DOCX
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()

        # Open DOCX and force standard font
        doc = Document(docx_path)
        for para in doc.paragraphs:
            for run in para.runs:
                run.font.name = 'Arial'   # Normal font
                run.font.size = Pt(11)    # Normal size
        doc.save(docx_path)

        return send_file(docx_path, as_attachment=True)
    else:
        return jsonify({"error": "Scanned PDF OCR not supported in free tier"}), 400

# Run locally (for testing)
if __name__ == "__main__":
    app.run()
