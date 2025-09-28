# Tesseract OCR Installation Guide

## Windows Installation

### Method 1: Using Chocolatey (Recommended)
```bash
# Install Chocolatey if you don't have it
# Then run:
choco install tesseract
```

### Method 2: Manual Installation
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install the executable (usually to `C:\Program Files\Tesseract-OCR\`)
3. Add Tesseract to your PATH environment variable

### Method 3: Using Conda
```bash
conda install -c conda-forge tesseract
```

## Linux Installation

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### CentOS/RHEL
```bash
sudo yum install tesseract
```

## macOS Installation

### Using Homebrew
```bash
brew install tesseract
```

## Verification
After installation, verify Tesseract is working:
```bash
tesseract --version
```

## Troubleshooting
- If you get "tesseract not found" errors, ensure Tesseract is in your PATH
- For Windows, the app will automatically search common installation paths
- If Tesseract is installed in a non-standard location, update the `tesseract_paths` list in `app.py`
