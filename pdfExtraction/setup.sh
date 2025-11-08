#!/bin/bash
# Setup script for PDF extraction module

set -e

echo "Setting up PDF extraction module..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Found Python version: $PYTHON_VERSION"

# Install Python dependencies
echo "Installing Python dependencies..."
cd "$(dirname "$0")"

if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt --user
    echo "✓ Dependencies installed successfully"
else
    echo "Warning: requirements.txt not found"
fi

echo ""
echo "Setup complete! You can now use the PDF extraction module."
echo ""
echo "To test the extraction, run:"
echo "  python3 extract_pdf.py <path-to-pdf>"
echo ""
echo "For Gemini AI enhancement, set your API key:"
echo "  export GEMINI_API_KEY='your-api-key'"
echo "  python3 extract_pdf.py <path-to-pdf> --enhance"
