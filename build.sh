#!/bin/bash
# This is Render-compatible build script for Python + OCR

# Update package list quietly
apt-get update -qq

# Install required system packages
apt-get install -y tesseract-ocr poppler-utils