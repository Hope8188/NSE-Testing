import requests
import fitz  # pymupdf
from bs4 import BeautifulSoup
import os

pdf_url = "https://www.safaricom.co.ke/annualreport_2024/Safaricom-PLC-Annual-Report-2024.pdf"
cma_url = "https://www.cma.or.ke/enforcement-of-securities-law/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

print("--- Testing CMA Access ---")
try:
    resp = requests.get(cma_url, headers=headers, timeout=20)
    print(f"CMA Page: {cma_url} -> HTTP {resp.status_code}")
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'html.parser')
        # Check for tables or key phrases
        text = soup.get_text()
        print(f"CMA content sample: {text[:500].strip()}...")
        if "fined" in text.lower() or "suspension" in text.lower():
            print("Found enforcement keywords in CMA text.")
except Exception as e:
    print(f"Error connecting to CMA: {e}")

print("\n--- Testing PDF Extraction (Safaricom 2024) ---")
pdf_path = "safaricom_2024.pdf"
try:
    print(f"Downloading {pdf_url}...")
    pdf_resp = requests.get(pdf_url, headers=headers, stream=True, timeout=30)
    if pdf_resp.status_code == 200:
        with open(pdf_path, 'wb') as f:
            f.write(pdf_resp.content)
        print(f"File saved to {pdf_path}")
        
        # Extraction
        doc = fitz.open(pdf_path)
        print(f"PDF Pages: {len(doc)}")
        
        text_sample = ""
        for i in range(min(5, len(doc))): # first 5 pages
            text_sample += f"\n--- PAGE {i+1} ---\n"
            text_sample += doc[i].get_text()
        
        print(f"Extracted {len(text_sample)} characters from first 5 pages.")
        print("Sample Text:")
        print(text_sample[:1000])
        
        # Clean up
        doc.close()
    else:
        print(f"Failed to download PDF: HTTP {pdf_resp.status_code}")
except Exception as e:
    print(f"Error in PDF pipeline: {e}")
finally:
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
