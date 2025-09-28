#!/usr/bin/env python3
"""
Test script to verify table parsing functionality
"""

import requests
import json

def test_table_parsing():
    """Test the table parsing endpoint with sample data"""
    
    # Sample timetable text (similar to what OCR might extract)
    sample_text = """
    . TE CSE-B .
    Monday | Tuesday Wednesday | Thursday | Friday
    Saturday
    Mew at | DAA | $8C manos DAA | sac. |sTQA Mr
    os | pa PA | PN
    Tee | TE| TES Te8 | TE8| TES +
    DAA 82 | bi | 8 Al 63 | ei | 82 DAA S...
    """
    
    print("🧪 Testing Table Parsing...")
    print("=" * 50)
    
    try:
        # Test the parse_table endpoint
        response = requests.post(
            "http://localhost:5000/parse_table",
            json={"text": sample_text},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Table parsing successful!")
            print(f"📊 Parsed timetable: {data.get('timetable', {})}")
            
            if data.get('timetable'):
                print("\n📋 Subjects found:")
                for subject, count in data['timetable'].items():
                    print(f"  - {subject}: {count} lectures per week")
            else:
                print("⚠️  No subjects were parsed from the text")
                print(f"📝 Raw text: {data.get('raw_text', '')[:200]}...")
                
        else:
            print(f"❌ Table parsing failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Flask app is running on port 5000")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_with_real_ocr_output():
    """Test with actual OCR output from your terminal"""
    
    real_ocr_text = """
    . TE CSE-B .
    Monday | Tuesday Wednesday | Thursday | Friday
    Saturday
    Mew at | DAA | $8C manos DAA | sac. |sTQA Mr
    os | pa PA | PN
    Tee | TE| TES Te8 | TE8| TES +
    DAA 82 | bi | 8 Al 63 | ei | 82 DAA S...
    """
    
    print("\n🔍 Testing with Real OCR Output...")
    print("=" * 50)
    
    try:
        response = requests.post(
            "http://localhost:5000/parse_table",
            json={"text": real_ocr_text},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Real OCR parsing successful!")
            print(f"📊 Parsed timetable: {data.get('timetable', {})}")
        else:
            print(f"❌ Real OCR parsing failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Real OCR test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Table Parsing Tests...")
    test_table_parsing()
    test_with_real_ocr_output()
    print("\n✅ Tests completed!")
