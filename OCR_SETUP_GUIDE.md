# OCR Setup Guide for Attendance Calculator

## Issues Fixed

The OCR text extraction issues have been resolved with the following improvements:

### 1. **Fixed Tesseract Path Configuration**
- Added automatic Tesseract path detection for Windows
- Searches common installation locations
- Provides clear error messages if Tesseract is not found

### 2. **Added Missing Dependencies**
- Added `Pillow` for image processing
- Added `pytesseract` for OCR functionality
- Added `opencv-python` for image preprocessing
- Added `numpy` for array operations

### 3. **Improved Image Preprocessing**
- Added grayscale conversion
- Added Gaussian blur for noise reduction
- Added thresholding for better text contrast
- Added morphological operations for text cleanup

### 4. **Enhanced OCR Configuration**
- Tests multiple OCR page segmentation modes
- Selects the best result based on confidence scores
- Provides detailed logging for debugging

### 5. **Better Error Handling**
- Comprehensive error messages
- Debugging information in responses
- Confidence scores for OCR results
- Extracted text preview for troubleshooting

## Installation Steps

### 1. Install Tesseract OCR

**Windows:**
```bash
# Using Chocolatey (recommended)
choco install tesseract

# Or download from: https://github.com/UB-Mannheim/tesseract/wiki
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Test OCR Functionality

```bash
python test_ocr.py
```

### 4. Start the Application

```bash
# Backend
cd backend
python app.py

# Frontend (in another terminal)
cd frontend
npm start
```

## Troubleshooting

### Common Issues:

1. **"Tesseract not found" error**
   - Install Tesseract OCR following the installation guide
   - Ensure Tesseract is in your system PATH
   - Check the health endpoint: `http://localhost:5000/health`

2. **Poor OCR accuracy**
   - Use high-quality, well-lit images
   - Ensure text is clearly visible and not blurry
   - Try different image formats (PNG, JPG)
   - Check the extracted text preview in the UI

3. **No text extracted**
   - Verify the image contains readable text
   - Check if the image is too small or low resolution
   - Try preprocessing the image manually (increase contrast, brightness)

### Debug Information:

- The app now shows OCR confidence scores
- Extracted text is displayed for debugging
- Detailed error messages help identify issues
- Health check endpoint verifies Tesseract installation

## Expected Timetable Format

The OCR expects timetable images with format like:
```
Mathematics 3
Physics 4
Chemistry 2
English 1
```

Where:
- Subject names can contain spaces, hyphens, or underscores
- Numbers represent lectures per week
- Each subject on a new line

## API Endpoints

- `POST /upload_timetable` - Upload and process timetable image
- `GET /health` - Check OCR system health
- `POST /calculate` - Calculate attendance requirements

## Features Added

✅ Automatic Tesseract path detection  
✅ Image preprocessing for better OCR  
✅ Multiple OCR configurations with confidence scoring  
✅ Comprehensive error handling  
✅ Debug information in UI  
✅ Health check endpoint  
✅ Installation guide and test script  
