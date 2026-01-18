from flask import Flask, request, send_file, jsonify
from flask_cors import CORS  # <- added for CORS support
from pdf2docx import Converter
from pdfminer.high_level import extract_text
from docx import Document
import os, uuid

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # <- enable CORS for all origins

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

    # Convert only text PDFs (skip OCR)
    if is_text_pdf(pdf_path):
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        return send_file(docx_path, as_attachment=True)
    else:
        return jsonify({"error": "Scanned PDF OCR not supported in free tier"}), 400

# Run the app (local testing)
if __name__ == "__main__":
    app.run()
