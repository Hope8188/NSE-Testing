import requests
from bs4 import BeautifulSoup
import fitz  # pymupdf
import os
import json
import time
from urllib.parse import urljoin

class NSESuperTool:
    def __init__(self, base_dir="nse_audit_data"):
        self.base_dir = base_dir
        self.raw_dir = os.path.join(base_dir, "raw_pdfs")
        self.text_dir = os.path.join(base_dir, "processed_text")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for d in [self.raw_dir, self.text_dir]:
            os.makedirs(d, exist_ok=True)

    def harvest_report_links(self):
        """Scrapes NSE website for annual report PDF links."""
        url = "https://www.nse.co.ke/annual-reports/"
        print(f"[*] Harvesting links from {url}...")
        try:
            resp = requests.get(url, headers=self.headers, timeout=20)
            if resp.status_code != 200:
                print(f"[!] Failed to reach NSE: HTTP {resp.status_code}")
                return []
            
            soup = BeautifulSoup(resp.content, 'html.parser')
            links = []
            # Find all <a> tags that end in .pdf
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.lower().endswith('.pdf'):
                    full_url = urljoin(url, href)
                    # Try to guess company/year from text or link
                    label = a.get_text(strip=True) or href.split('/')[-1]
                    links.append({"url": full_url, "label": label})
            
            print(f"[+] Found {len(links)} potential PDF reports.")
            return links
        except Exception as e:
            print(f"[!] Error harvesting: {e}")
            return []

    def download_report(self, report_info):
        """Downloads a single PDF."""
        filename = report_info['label'].replace(" ", "_").replace("/", "_") + ".pdf"
        filepath = os.path.join(self.raw_dir, filename)
        
        if os.path.exists(filepath):
            print(f"[-] Skip (Already exists): {filename}")
            return filepath
            
        print(f"[*] Downloading: {report_info['url']}...")
        try:
            r = requests.get(report_info['url'], headers=self.headers, timeout=30)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                return filepath
        except Exception as e:
            print(f"[!] Failed download: {e}")
        return None

    def extract_and_clean_text(self, pdf_path):
        """Converts PDF to text and strips common noise."""
        if not pdf_path: return
        
        base_name = os.path.basename(pdf_path).replace(".pdf", ".txt")
        text_path = os.path.join(self.text_dir, base_name)
        
        print(f"[*] Extracting: {os.path.basename(pdf_path)}...")
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            for page in doc:
                # Basic cleaning: remove very small boxes (likely page numbers/sidebars)
                # This is a 'supertool' heuristic
                text = page.get_text()
                full_text += text + "\n"
            
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            doc.close()
            return text_path
        except Exception as e:
            print(f"[!] Extraction error: {e}")
            return None

if __name__ == "__main__":
    tool = NSESuperTool()
    
    # 1. Harvest
    reports = tool.harvest_report_links()
    
    print(f"\n[*] Total reports found: {len(reports)}")
    print("[*] Downloading ALL reports for comprehensive testing...\n")
    
    # 2. Download & Extract ALL reports (not just 3)
    success_count = 0
    for i, r in enumerate(reports, 1):
        print(f"[{i}/{len(reports)}] Processing: {r['label'][:50]}...")
        path = tool.download_report(r)
        if path:
            txt = tool.extract_and_clean_text(path)
            if txt:
                print(f"    [SUCCESS] {os.path.basename(txt)}")
                success_count += 1
        time.sleep(0.5) # Be nice
    
    print(f"\n{'='*60}")
    print(f"SCRAPE PHASE COMPLETE")
    print(f"{'='*60}")
    print(f"Successfully processed: {success_count}/{len(reports)} reports")
    print(f"Output directory: {tool.text_dir}")
