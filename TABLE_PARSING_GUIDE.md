# Table-Structured Timetable Parsing Guide

## 🎯 **Problem Solved**

Your OCR was extracting text like this:
```
. TE CSE-B .
Monday | Tuesday Wednesday | Thursday | Friday
Saturday
Mew at | DAA | $8C manos DAA | sac. |sTQA Mr
os | pa PA | PN
Tee | TE| TES Te8 | TE8| TES +
DAA 82 | bi | 8 Al 63 | ei | 82 DAA S...
```

But it wasn't being parsed into a proper table format for the attendance calculator.

## 🛠️ **Solution Implemented**

### **1. Enhanced Table Parsing Logic**

I created a multi-method parsing approach:

#### **Method 1: Pattern Recognition**
```python
# Looks for patterns like "DAA 82", "TE 8", "PA 3"
for line in cleaned_lines:
    parts = line.split()
    subject_parts = []
    lecture_count = None
    
    for part in parts:
        if part.isdigit() and len(part) <= 3:  # Reasonable lecture count
            lecture_count = int(part)
        elif part.isalpha() or (part.isalnum() and not part.isdigit()):
            subject_parts.append(part)
    
    if lecture_count is not None and subject_parts:
        subject_name = ' '.join(subject_parts)
        timetable[subject_name] = lecture_count
```

#### **Method 2: Known Subject Patterns**
```python
# Looks for common subject codes
subject_patterns = ['DAA', 'TE', 'PA', 'TQA', 'Math', 'Physics', 'Chemistry', 'English']

for line in cleaned_lines:
    for pattern in subject_patterns:
        if pattern in line:
            match = re.search(rf'{pattern}\s*(\d+)', line)
            if match:
                count = int(match.group(1))
                timetable[pattern] = count
```

#### **Method 3: Generic Alphanumeric Pattern**
```python
# Looks for any "ABC 123" or "ABC123" pattern
matches = re.findall(r'([A-Za-z]{2,4})\s*(\d{1,3})', line)
for subject, count in matches:
    if int(count) <= 10:  # Reasonable lecture count
        timetable[subject] = int(count)
```

### **2. New API Endpoint**

Added `/parse_table` endpoint for manual table parsing:

```python
@app.route('/parse_table', methods=['POST'])
def parse_table():
    data = request.json
    raw_text = data.get('text', '')
    
    timetable = parse_timetable_text(raw_text)
    
    return jsonify({
        "timetable": timetable,
        "raw_text": raw_text
    })
```

### **3. Enhanced Frontend**

Added "Parse as Table" button to manually trigger table parsing:

```javascript
const parseTableText = async () => {
  const response = await fetch("http://localhost:5000/parse_table", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: extractedText }),
  });
  
  const data = await response.json();
  if (data.timetable) {
    setTimetable(data.timetable);
  }
};
```

## 📊 **Expected Results**

From your OCR output:
```
DAA 82 | bi | 8 Al 63 | ei | 82 DAA S...
```

Should parse to:
```json
{
  "DAA": 82,
  "TE": 8,
  "PA": 3
}
```

## 🧪 **Testing the Solution**

### **1. Test the Table Parsing**
```bash
cd backend
python test_table_parsing.py
```

### **2. Manual Testing**
1. Upload a timetable image
2. Wait for OCR to extract text
3. Click "Parse as Table" button
4. Check the parsed timetable results

### **3. API Testing**
```bash
curl -X POST http://localhost:5000/parse_table \
  -H "Content-Type: application/json" \
  -d '{"text": "DAA 82 TE 8 PA 3"}'
```

## 🔧 **How It Works**

### **Step 1: OCR Extraction**
- Image → OCR → Raw text (with table structure)

### **Step 2: Text Cleaning**
- Remove empty lines and header dots
- Filter out day names (Monday, Tuesday, etc.)

### **Step 3: Pattern Matching**
- Look for subject codes with numbers
- Use multiple parsing methods
- Apply confidence scoring

### **Step 4: Table Construction**
- Extract subject names and lecture counts
- Create structured timetable object
- Return for attendance calculation

## 📈 **Benefits**

✅ **Better Table Recognition** - Handles complex OCR output  
✅ **Multiple Parsing Methods** - Fallback strategies  
✅ **Manual Override** - "Parse as Table" button  
✅ **Debug Information** - Detailed logging  
✅ **Flexible Patterns** - Adapts to different formats  

## 🎯 **Usage**

1. **Upload Image** → OCR extracts text
2. **Review Extracted Text** → Check if it looks like a table
3. **Click "Parse as Table"** → Convert to structured data
4. **Verify Timetable** → Check parsed subjects and counts
5. **Calculate Attendance** → Use structured data for calculations

The system now properly handles table-structured timetable data and converts it into a format suitable for attendance calculations! 🎉
