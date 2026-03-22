"""
Direct download of a known Safaricom annual report using working URLs.
Tests multiple URL patterns to find one that works.
"""
import requests
import os

# Working directory setup
base_dir = "nse_audit_data"
raw_dir = os.path.join(base_dir, "raw_pdfs")
text_dir = os.path.join(base_dir, "processed_text")
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(text_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/pdf,*/*',
    'Referer': 'https://www.safaricom.co.ke/'
}

# Try multiple known URL patterns for Safaricom reports
urls_to_try = [
    # Pattern 1: Direct from safaricom.co.ke
    "https://www.safaricom.co.ke/images/Investor_Relations/Annual_Reports/Safaricom_Integrated_Report_2022.pdf",
    "https://www.safaricom.co.ke/images/Investor_Relations/Annual_Reports/Safaricom_Annual_Report_2021.pdf",
    
    # Pattern 2: Alternative paths
    "https://safaricom.co.ke/images/Investor_Relations/Annual_Reports/Safaricom_Integrated_Report_2023.pdf",
    
    # Pattern 3: From other known sources (NSE archives often have copies)
    "https://www.nse.co.ke/wp-content/uploads/2023/07/Safaricom-Integrated-Report-2023.pdf",
]

print("[*] Attempting to download Safaricom annual report...")

for url in urls_to_try:
    print(f"\nTrying: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200 and len(resp.content) > 10000:  # At least 10KB
            filename = "Safaricom_Integrated_Report_2022.pdf"
            filepath = os.path.join(raw_dir, f"Safaricom_{filename}")
            
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            
            print(f"[+] SUCCESS! Downloaded {len(resp.content):,} bytes to {filepath}")
            
            # Now extract text
            import fitz
            doc = fitz.open(filepath)
            full_text = ""
            for page in doc:
                full_text += page.get_text("text") + "\n\n---PAGE BREAK---\n\n"
            doc.close()
            
            txt_filename = os.path.basename(filepath).replace('.pdf', '.txt')
            txt_path = os.path.join(text_dir, txt_filename)
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            print(f"[*] Extracted {len(full_text):,} characters to {txt_path}")
            print(f"\n[+] COMPLETE! Ready for testing.")
            break
        else:
            print(f"[-] Failed: HTTP {resp.status_code}, Size: {len(resp.content)} bytes")
    except Exception as e:
        print(f"[-] Error: {e}")
else:
    print("\n[!] All URLs failed. Creating a minimal test file manually...")
    # Create a placeholder for testing purposes
    sample_text = """
    SAFARICOM PLC - INTEGRATED REPORT 2023
    
    CORPORATE GOVERNANCE
    
    Board of Directors
    
    The Board comprises Five (5) Independent and Non-Executive Directors, 
    One (1) Executive Director, and Five (5) Non-Independent Non-Executive Directors.
    
    Total Board Size: 11 directors
    Independent Directors: 5 (45.5%)
    
    This meets the requirement of Section 41 of the CG Code (minimum one-third independent).
    
    DIRECTOR PROFILES
    
    Mr. Michael Turner
    Independent Non-Executive Director
    Appointment March 21, 2014
    
    Mr. Turner was appointed a Board Director of Safaricom on March 26, 2015.
    He has served since 2014 and brings extensive telecommunications experience.
    
    RELATED PARTY TRANSACTIONS
    
    Note 28: Related Party Disclosures
    
    Transactions with related parties during the year:
    
    Vodafone Kenya Limited (Parent Company):
    - Management fees: KES 450 million
    - Technical services: KES 120 million
    
    Directors and Key Management:
    - Short-term employee benefits: KES 89 million
    - Post-employment benefits: KES 12 million
    
    All related party transactions were conducted at arm's length terms 
    and approved by the Board Audit Committee.
    """
    
    txt_path = os.path.join(text_dir, "Safaricom_Integrated_Report_2023_SAMPLE.txt")
    with open(txt_path, 'w') as f:
        f.write(sample_text)
    
    print(f"[*] Created sample text file: {txt_path}")
