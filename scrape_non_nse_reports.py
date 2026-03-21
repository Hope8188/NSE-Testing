"""
Targeted scraper for non-NSE listed company annual reports.
Focuses on major companies with reliable web presence: Safaricom, EABL, KCB, Equity, etc.
"""
import requests
from bs4 import BeautifulSoup
import fitz  # pymupdf
import os
import json
import time
from urllib.parse import urljoin, urlparse

class NonNSEScraper:
    def __init__(self, base_dir="nse_audit_data"):
        self.base_dir = base_dir
        self.raw_dir = os.path.join(base_dir, "raw_pdfs")
        self.text_dir = os.path.join(base_dir, "processed_text")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        for d in [self.raw_dir, self.text_dir]:
            os.makedirs(d, exist_ok=True)
    
    def search_safaricom_reports(self):
        """Safaricom has excellent investor relations page."""
        print("[*] Searching Safaricom PLC annual reports...")
        reports = []
        
        # Safaricom's official investor relations page
        urls_to_try = [
            "https://www.safaricom.co.ke/investor-relations/financial-reports/",
            "https://www.safaricom.co.ke/investor-relations/annual-reports/",
        ]
        
        for url in urls_to_try:
            try:
                resp = requests.get(url, headers=self.headers, timeout=20)
                if resp.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(resp.content, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if '.pdf' in href.lower() and ('annual' in href.lower() or 'report' in href.lower() or 'integrated' in href.lower()):
                        full_url = urljoin(url, href)
                        label = a.get_text(strip=True) or href.split('/')[-1]
                        if 'safaricom' not in label.lower():
                            label = f"Safaricom - {label}"
                        reports.append({"url": full_url, "label": label, "company": "Safaricom"})
                        print(f"    Found: {label}")
                if reports:
                    break
            except Exception as e:
                print(f"    Error with {url}: {e}")
                continue
        
        return reports
    
    def search_eabl_reports(self):
        """EABL investor relations."""
        print("[*] Searching EABL annual reports...")
        reports = []
        
        urls_to_try = [
            "https://www.eabl.com/investor-relations/financial-results/",
            "https://www.eabl.com/investor-relations/reports/",
        ]
        
        for url in urls_to_try:
            try:
                resp = requests.get(url, headers=self.headers, timeout=20)
                if resp.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(resp.content, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if '.pdf' in href.lower() and ('annual' in href.lower() or 'report' in href.lower()):
                        full_url = urljoin(url, href)
                        label = a.get_text(strip=True) or href.split('/')[-1]
                        if 'eabl' not in label.lower():
                            label = f"EABL - {label}"
                        reports.append({"url": full_url, "label": label, "company": "EABL"})
                        print(f"    Found: {label}")
                if reports:
                    break
            except Exception as e:
                print(f"    Error with {url}: {e}")
                continue
        
        return reports
    
    def search_kcb_reports(self):
        """KCB Group investor relations."""
        print("[*] Searching KCB Group annual reports...")
        reports = []
        
        urls_to_try = [
            "https://www.kcbbankgroup.com/investor-relations/financial-reports/",
            "https://www.kcbbankgroup.com/investor-relations/",
        ]
        
        for url in urls_to_try:
            try:
                resp = requests.get(url, headers=self.headers, timeout=20)
                if resp.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(resp.content, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if '.pdf' in href.lower() and ('annual' in href.lower() or 'report' in href.lower()):
                        full_url = urljoin(url, href)
                        label = a.get_text(strip=True) or href.split('/')[-1]
                        if 'kcb' not in label.lower():
                            label = f"KCB - {label}"
                        reports.append({"url": full_url, "label": label, "company": "KCB"})
                        print(f"    Found: {label}")
                if reports:
                    break
            except Exception as e:
                print(f"    Error with {url}: {e}")
                continue
        
        return reports
    
    def download_report(self, report_info):
        """Downloads a single PDF."""
        company = report_info.get('company', 'Unknown')
        filename = report_info['label'].replace(" ", "_").replace("/", "_").replace(":", "_")
        # Clean filename
        filename = "".join(c for c in filename if c.isalnum() or c in "._-") + ".pdf"
        filepath = os.path.join(self.raw_dir, f"{company}_{filename}")
        
        if os.path.exists(filepath):
            print(f"[-] Skip (Already exists): {filepath}")
            return filepath
        
        try:
            resp = requests.get(report_info['url'], headers=self.headers, timeout=60)
            if resp.status_code != 200:
                print(f"[!] Failed to download {report_info['url']}: HTTP {resp.status_code}")
                return None
            
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            print(f"[+] Downloaded: {filepath}")
            return filepath
        except Exception as e:
            print(f"[!] Error downloading: {e}")
            return None
    
    def extract_text(self, pdf_path):
        """Extracts text from PDF using PyMuPDF."""
        if not pdf_path or not os.path.exists(pdf_path):
            return None
        
        txt_filename = os.path.basename(pdf_path).replace('.pdf', '.txt')
        txt_path = os.path.join(self.text_dir, txt_filename)
        
        if os.path.exists(txt_path):
            print(f"[-] Text already extracted: {txt_path}")
            return txt_path
        
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text("text") + "\n\n---PAGE BREAK---\n\n"
            doc.close()
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            print(f"[*] Extracted text: {txt_path} ({len(full_text)} chars)")
            return txt_path
        except Exception as e:
            print(f"[!] Error extracting text: {e}")
            return None
    
    def run(self, target_company="Safaricom"):
        """Main execution: find and download reports for target company."""
        all_reports = []
        
        if target_company.lower() == "safaricom" or target_company.lower() == "all":
            all_reports.extend(self.search_safaricom_reports())
        
        if target_company.lower() == "eabl" or target_company.lower() == "all":
            all_reports.extend(self.search_eabl_reports())
        
        if target_company.lower() == "kcb" or target_company.lower() == "all":
            all_reports.extend(self.search_kcb_reports())
        
        if not all_reports:
            print("[!] No reports found. Trying direct links...")
            # Fallback: known direct URLs for recent reports
            fallback_reports = [
                {"url": "https://www.safaricom.co.ke/images/Investor_Relations/Annual_Reports/Safaricom_Integrated_Report_2023.pdf", 
                 "label": "Safaricom Integrated Report 2023", "company": "Safaricom"},
                {"url": "https://www.eabl.com/wp-content/uploads/2023/11/EABL-Integrated-Report-2023.pdf",
                 "label": "EABL Integrated Report 2023", "company": "EABL"},
            ]
            all_reports.extend(fallback_reports)
        
        print(f"\n[*] Total reports found: {len(all_reports)}")
        
        downloaded = []
        for i, report in enumerate(all_reports[:5], 1):  # Limit to first 5
            print(f"\n[{i}/{len(all_reports)}] Processing: {report['label']}...")
            pdf_path = self.download_report(report)
            if pdf_path:
                txt_path = self.extract_text(pdf_path)
                if txt_path:
                    downloaded.append({
                        "company": report['company'],
                        "pdf": pdf_path,
                        "text": txt_path,
                        "label": report['label']
                    })
            time.sleep(1)  # Be polite
        
        # Save manifest
        manifest_path = os.path.join(self.base_dir, "non_nse_reports_manifest.json")
        with open(manifest_path, 'w') as f:
            json.dump(downloaded, f, indent=2)
        
        print(f"\n[+] Download complete! Saved {len(downloaded)} reports.")
        print(f"[*] Manifest: {manifest_path}")
        return downloaded

if __name__ == "__main__":
    scraper = NonNSEScraper()
    # Start with Safaricom as the primary test case
    scraper.run(target_company="Safaricom")
