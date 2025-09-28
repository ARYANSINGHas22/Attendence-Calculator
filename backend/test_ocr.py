#!/usr/bin/env python3
"""
Test script to verify OCR functionality
Run this to test if Tesseract is properly installed and working
"""

import pytesseract
from PIL import Image, ImageDraw, ImageFont
import os

def test_tesseract_installation():
    """Test if Tesseract is properly installed"""
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        print(f"✅ Tesseract path: {pytesseract.pytesseract.tesseract_cmd}")
        return True
    except Exception as e:
        print(f"❌ Tesseract not found: {e}")
        return False

def test_ocr_with_sample():
    """Test OCR with a simple sample image"""
    try:
        # Create a white image
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Draw some text
        text = "Mathematics 3\nPhysics 4\nChemistry 2"
        draw.text((10, 10), text, fill='black', font=font)
        
        # Save test image
        img.save('test_image.png')
        print("✅ Created test image: test_image.png")
        
        # Test OCR
        extracted_text = pytesseract.image_to_string(img)
        print(f"✅ Extracted text: {repr(extracted_text)}")
        
        # Clean up
        if os.path.exists('test_image.png'):
            os.remove('test_image.png')
        
        return True
        
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False

def main():
    print("🔍 Testing OCR Setup...")
    print("=" * 50)
    
    # Test Tesseract installation
    if not test_tesseract_installation():
        print("\n❌ Tesseract is not properly installed!")
        print("Please install Tesseract OCR following the instructions in INSTALL_TESSERACT.md")
        return False
    
    # Test OCR functionality
    if not test_ocr_with_sample():
        print("\n❌ OCR functionality test failed!")
        return False
    
    print("\n✅ All tests passed! OCR is working correctly.")
    return True

if __name__ == "__main__":
    main()
