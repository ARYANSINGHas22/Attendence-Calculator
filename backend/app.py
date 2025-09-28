from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Tesseract path for Windows (adjust if Tesseract is installed elsewhere)
tesseract_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
]

for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        logger.info(f"Tesseract found at: {path}")
        break
else:
    logger.warning("Tesseract not found in common locations. Please install Tesseract OCR.")


def preprocess_image(image):
    """Preprocess image for better OCR results using only PIL"""
    try:
        # Convert to grayscale if needed
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)  # Increase contrast
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)  # Increase sharpness
        
        # Apply a slight blur to reduce noise
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}")
        return image  # Return original image if preprocessing fails

@app.route('/upload_timetable', methods=['POST'])
def upload_timetable():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Open and preprocess the image
        image = Image.open(file.stream)
        logger.info(f"Original image size: {image.size}")
        
        # Preprocess image for better OCR
        processed_image = preprocess_image(image)
        
        # Try different OCR configurations
        ocr_configs = [
            '--psm 6',  # Uniform block of text
            '--psm 3',  # Fully automatic page segmentation
            '--psm 4',  # Assume a single column of text
        ]
        
        best_text = ""
        best_confidence = 0
        
        for config in ocr_configs:
            try:
                # Get text with confidence scores
                data = pytesseract.image_to_data(processed_image, config=config, output_type=pytesseract.Output.DICT)
                
                # Calculate average confidence
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                # Get text
                text = pytesseract.image_to_string(processed_image, config=config)
                
                logger.info(f"OCR config '{config}' - Confidence: {avg_confidence:.1f}%, Text length: {len(text)}")
                
                if avg_confidence > best_confidence:
                    best_confidence = avg_confidence
                    best_text = text
                    
            except Exception as e:
                logger.warning(f"OCR failed with config '{config}': {e}")
                continue
        
        if not best_text.strip():
            return jsonify({"error": "No text could be extracted from the image. Please ensure the image is clear and contains readable text."}), 400
        
        logger.info(f"Best OCR result - Confidence: {best_confidence:.1f}%")
        logger.info(f"Extracted text: {best_text[:200]}...")  # Log first 200 chars
        
        # Improved parsing logic for timetable
        timetable = parse_timetable_text(best_text)
        
        if not timetable:
            return jsonify({
                "error": "Could not parse timetable from extracted text. Please ensure the image contains a clear timetable with subject names and lecture counts.",
                "extracted_text": best_text[:500]  # Include first 500 chars for debugging
            }), 400
        
        return jsonify({
            "timetable": timetable,
            "confidence": round(best_confidence, 1),
            "extracted_text": best_text
        })

    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        return jsonify({"error": f"OCR processing failed: {str(e)}"}), 500

def parse_timetable_text(text):
    """Parse timetable text to extract subject names and lecture counts from table format"""
    timetable = {}
    lines = text.split('\n')
    
    # Clean and filter lines
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('.'):  # Skip empty lines and header dots
            cleaned_lines.append(line)
    
    logger.info(f"Cleaned lines: {cleaned_lines[:10]}")  # Log first 10 lines for debugging
    
    # Method 1: Look for subject patterns with numbers
    for line in cleaned_lines:
        # Skip lines that look like headers (days of week, etc.)
        if any(day in line.lower() for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
            continue
            
        # Look for subject codes and numbers
        # Pattern: "DAA 82" or "TE 8" or "PA 3" etc.
        parts = line.split()
        if len(parts) >= 2:
            subject_parts = []
            lecture_count = None
            
            for part in parts:
                # Check if it's a number (could be lecture count)
                if part.isdigit() and len(part) <= 3:  # Reasonable lecture count
                    lecture_count = int(part)
                elif part.isalpha() or (part.isalnum() and not part.isdigit()):
                    # It's a subject code/name
                    subject_parts.append(part)
            
            if lecture_count is not None and subject_parts:
                subject_name = ' '.join(subject_parts)
                # Clean up subject name
                subject_name = subject_name.rstrip('.,;:|')
                if subject_name and len(subject_name) <= 10:  # Reasonable subject name length
                    timetable[subject_name] = lecture_count
                    logger.info(f"Found subject: {subject_name} -> {lecture_count}")
    
    # Method 2: If no subjects found, try alternative parsing
    if not timetable:
        logger.info("No subjects found with method 1, trying alternative parsing...")
        
        # Look for common subject patterns
        subject_patterns = ['DAA', 'TE', 'PA', 'TQA', 'Math', 'Physics', 'Chemistry', 'English']
        
        for line in cleaned_lines:
            for pattern in subject_patterns:
                if pattern in line:
                    # Extract number after the pattern
                    import re
                    match = re.search(rf'{pattern}\s*(\d+)', line)
                    if match:
                        count = int(match.group(1))
                        timetable[pattern] = count
                        logger.info(f"Found subject (pattern): {pattern} -> {count}")
    
    # Method 3: If still no subjects, try to extract any alphanumeric codes with numbers
    if not timetable:
        logger.info("No subjects found with method 2, trying generic parsing...")
        
        for line in cleaned_lines:
            # Look for any pattern like "ABC 123" or "ABC123"
            import re
            matches = re.findall(r'([A-Za-z]{2,4})\s*(\d{1,3})', line)
            for subject, count in matches:
                if int(count) <= 10:  # Reasonable lecture count
                    timetable[subject] = int(count)
                    logger.info(f"Found subject (generic): {subject} -> {count}")
    
    logger.info(f"Final timetable: {timetable}")
    return timetable

@app.route('/parse_table', methods=['POST'])
def parse_table():
    """Parse table-structured timetable data"""
    data = request.json
    raw_text = data.get('text', '')
    
    if not raw_text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        # Parse the table text
        timetable = parse_timetable_text(raw_text)
        
        if not timetable:
            return jsonify({
                "error": "Could not parse timetable from the provided text",
                "raw_text": raw_text[:500]
            }), 400
        
        return jsonify({
            "timetable": timetable,
            "raw_text": raw_text
        })
        
    except Exception as e:
        logger.error(f"Table parsing failed: {e}")
        return jsonify({"error": f"Table parsing failed: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify OCR functionality"""
    try:
        # Test if Tesseract is accessible
        version = pytesseract.get_tesseract_version()
        return jsonify({
            "status": "healthy",
            "tesseract_version": version,
            "tesseract_path": pytesseract.pytesseract.tesseract_cmd
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "tesseract_path": pytesseract.pytesseract.tesseract_cmd
        }), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    try:
        overallPercent = float(data.get("overallPercent", 0))
        totalLectures = int(data.get("totalLectures", 0))
        targetPercent = float(data.get("targetPercent", 75))
        remainingWeeks = int(data.get("remainingWeeks", 0))
        timetable = data.get("timetable", {})

        results = {}
        for subject, lecturesPerWeek in timetable.items():
            lecturesSoFar = totalLectures
            attendedLectures = (overallPercent / 100) * lecturesSoFar
            try:
                requiredLectures = int(
                    (targetPercent/100 * lecturesSoFar - attendedLectures) /
                    (1 - targetPercent/100)
                )
            except ZeroDivisionError:
                requiredLectures = float("inf")

            possibleLectures = remainingWeeks * lecturesPerWeek
            if requiredLectures <= possibleLectures:
                results[subject] = f"Attend at least {requiredLectures} lectures."
            else:
                results[subject] = "Not possible to reach target attendance."

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
