from pathlib import Path
from io import BytesIO
import fitz

pdf_path = Path("data/input/aig_10q_2024q3.pdf")

print(f"Testing: {pdf_path}")
print(f"File exists: {pdf_path.exists()}")
print(f"File size: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB")

# Method 1: Read into memory first
try:
    print("\n=== Method 1: BytesIO ===")
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    print(f"✅ Read {len(pdf_data)} bytes into memory")
    
    pdf_stream = BytesIO(pdf_data)
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    print(f"✅ Opened PDF: {doc.page_count} pages")
    
    # Test extraction
    first_page = doc[0]
    text = first_page.get_text()
    print(f"✅ Extracted {len(text)} characters from page 1")
    print(f"First 200 chars: {text[:200]}")
    
    doc.close()
    print("✅ Method 1 SUCCESS!")
    
except Exception as e:
    print(f"❌ Method 1 FAILED: {e}")

# Method 2: Path.read_bytes()
try:
    print("\n=== Method 2: Path.read_bytes() ===")
    pdf_data = pdf_path.read_bytes()
    print(f"✅ Read {len(pdf_data)} bytes")
    
    pdf_stream = BytesIO(pdf_data)
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    print(f"✅ Opened PDF: {doc.page_count} pages")
    doc.close()
    print("✅ Method 2 SUCCESS!")
    
except Exception as e:
    print(f"❌ Method 2 FAILED: {e}")

# Method 3: Direct file path
try:
    print("\n=== Method 3: Direct path ===")
    doc = fitz.open(str(pdf_path))
    print(f"✅ Opened PDF: {doc.page_count} pages")
    doc.close()
    print("✅ Method 3 SUCCESS!")
    
except Exception as e:
    print(f"❌ Method 3 FAILED: {e}")
