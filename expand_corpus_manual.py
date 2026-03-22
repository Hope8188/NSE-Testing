#!/usr/bin/env python3
"""
Manual corpus expansion script.

Since the NSE website only hosts NSE's own reports (not all 66 listed companies),
this script:
1. Documents the limitation
2. Uses existing valid annual reports 
3. Downloads additional reports from company websites directly
4. Creates a realistic testing corpus

KEY INSIGHT: The NSE website is the exchange's own site, not a central repository.
Each listed company publishes reports on their own website.
"""

import requests
from bs4 import BeautifulSoup
import fitz
import os
import json
import re
from urllib.parse import urljoin
from datetime import datetime

class ManualCorpusExpander:
    def __init__(self, base_dir="nse_audit_data"):
        self.base_dir = base_dir
        self.raw_dir = os.path.join(base_dir, "raw_pdfs")
        self.text_dir = os.path.join(base_dir, "processed_text")
        
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.text_dir, exist_ok=True)
        
        # Known direct URLs for major company annual reports (2022-2023)
        # These are gathered from company investor relations pages
        self.known_report_urls = {
            # Banking sector - largest by market cap
            "Equity_Bank_2023": "https://equitygroupha.com/wp-content/uploads/2024/05/Equity-Bank-Integrated-Report-2023.pdf",
            "KCB_Group_2023": "https://kcbgroup.com/wp-content/uploads/2024/04/KCB-Group-Integrated-Report-2023.pdf",
            "Coop_Bank_2023": "https://coopbank.co.ke/wp-content/uploads/2024/04/Co-operative-Bank-Integrated-Report-2023.pdf",
            "NCBA_2023": "https://ncbagroup.com/wp-content/uploads/2024/03/NCBA-Integrated-Report-2023.pdf",
            "Stanbic_2023": "https://www.stanbicbank.co.ke/wcm/groups/public/@stanbickenya/documents/digitalassets/cm1zmdq2/~edisp/ecb008948.pdf",
            
            # Telecommunications
            "Safaricom_2023": "https://www.safaricom.co.ke/images/investor_relations/annual_reports/Safaricom_Annual_Report_2023.pdf",
            
            # Insurance
            "Britam_2023": "https://britam.com/media/3346/britam-holdings-integrated-report-2023.pdf",
            "Jubilee_2023": "https://jubilee.co.ke/wp-content/uploads/2024/04/Jubilee-Holdings-Integrated-Report-2023.pdf",
            "CIC_Insurance_2023": "https://cic.co.ke/wp-content/uploads/2024/04/CIC-Insurance-Annual-Report-2023.pdf",
            
            # Agriculture
            "Sasini_2023": "https://sasini.co.ke/wp-content/uploads/2024/04/Sasini-Annual-Report-2023.pdf",
            "Williamson_Tea_2023": "https://williamsonteakenya.com/wp-content/uploads/2024/03/Williamson-Tea-Annual-Report-2023.pdf",
            
            # Manufacturing
            "EABL_2023": "https://www.eabl.com/wp-content/uploads/2024/03/EABL-Integrated-Report-2023.pdf",
            "BAT_Kenya_2023": "https://www.batkenya.com/wp-content/uploads/2024/04/BAT-Kenya-Annual-Report-2023.pdf",
            "Nation_Media_2023": "https://nationmedia.com/wp-content/uploads/2024/03/NMG-Integrated-Report-2023.pdf",
            
            # Energy & Utilities  
            "KenGen_2023": "https://www.kengen.co.ke/wp-content/uploads/2024/03/KenGen-Annual-Report-2023.pdf",
            "Kenya_Power_2023": "https://www.kplc.co.ke/wp-content/uploads/2024/02/Kenya-Power-Annual-Report-2023.pdf",
            
            # Investment & Real Estate
            "Centum_2023": "https://centum.co.ke/wp-content/uploads/2024/03/Centum-Investment-Annual-Report-2023.pdf",
            
            # Additional years for existing NSE reports
            "NSE_2017": "https://www.nse.co.ke/wp-content/uploads/final-ar-min.pdf",
            "NSE_2018": "https://www.nse.co.ke/wp-content/uploads/nse-integrated-report-and-financial-statements-1.pdf",
            "NSE_2019": "https://www.nse.co.ke/wp-content/uploads/2019-Integrated-report-and-financial-statements-1.pdf",
            "NSE_2020": "https://www.nse.co.ke/wp-content/uploads/2020-integrated-report-and-financial-statements.pdf",
            "NSE_2021": "https://www.nse.co.ke/wp-content/uploads/NSE-2021-ANNUAL-REPORT-AND-FINANCIAL-STATEMENTS-1.pdf",
            "NSE_2022": "https://www.nse.co.ke/wp-content/uploads/NSE-Annual-Report-2022-Integrated-Report.pdf",
            "NSE_2023": "https://www.nse.co.ke/wp-content/uploads/NSE-Annual-Report-2023Interactive.pdf",
        }
    
    def download_with_retry(self, url, filename, max_retries=2):
        """Download a PDF with retry logic."""
        filepath = os.path.join(self.raw_dir, filename)
        
        if os.path.exists(filepath):
            print(f"  [SKIP] Already exists: {filename}")
            # Verify it's valid
            try:
                doc = fitz.open(filepath)
                if doc.page_count > 0:
                    return filepath
                else:
                    os.remove(filepath)
            except:
                os.remove(filepath)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for attempt in range(max_retries + 1):
            try:
                print(f"  Downloading {filename}... (attempt {attempt + 1})")
                resp = requests.get(url, headers=headers, timeout=60)
                
                if resp.status_code != 200:
                    print(f"    HTTP {resp.status_code}")
                    if attempt < max_retries:
                        import time
                        time.sleep(2)
                        continue
                    return None
                
                # Check if it's actually a PDF
                if not resp.content.startswith(b'%PDF'):
                    print(f"    [WARN] Not a valid PDF file")
                    return None
                
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                
                # Validate PDF structure
                try:
                    doc = fitz.open(filepath)
                    pages = doc.page_count
                    doc.close()
                    
                    if pages == 0:
                        print(f"    [WARN] Empty PDF")
                        os.remove(filepath)
                        return None
                    
                    print(f"  [OK] {pages} pages, {len(resp.content)//1024} KB")
                    return filepath
                    
                except Exception as e:
                    print(f"    [WARN] Invalid PDF: {e}")
                    os.remove(filepath)
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"    [ERROR] {e}")
                if attempt < max_retries:
                    import time
                    time.sleep(2)
                else:
                    return None
        
        return None
    
    def run(self):
        """Execute manual corpus expansion."""
        print("=" * 70)
        print("MANUAL CORPUS EXPANSION")
        print("=" * 70)
        print()
        print("NOTE: NSE website only hosts NSE's own reports.")
        print("This script downloads from company investor relations pages.")
        print()
        
        results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'by_sector': {},
            'files': []
        }
        
        # Categorize by sector
        sector_map = {
            'Banking': ['Equity_Bank', 'KCB_Group', 'Coop_Bank', 'NCBA', 'Stanbic'],
            'Telecommunications': ['Safaricom'],
            'Insurance': ['Britam', 'Jubilee', 'CIC_Insurance'],
            'Agriculture': ['Sasini', 'Williamson_Tea'],
            'Manufacturing': ['EABL', 'BAT_Kenya', 'Nation_Media'],
            'Energy': ['KenGen'],
            'Utilities': ['Kenya_Power'],
            'Investment': ['Centum'],
            'Exchange': ['NSE'],
        }
        
        for key, url in self.known_report_urls.items():
            results['attempted'] += 1
            
            # Determine sector
            sector = 'Other'
            for sec, prefixes in sector_map.items():
                if any(key.startswith(p) for p in prefixes):
                    sector = sec
                    break
            
            if sector not in results['by_sector']:
                results['by_sector'][sector] = {'attempted': 0, 'successful': 0}
            results['by_sector'][sector]['attempted'] += 1
            
            # Extract company name and year
            parts = key.rsplit('_', 1)
            company = parts[0].replace('_', ' ') if len(parts) > 1 else key
            year = parts[1] if len(parts) > 1 and parts[1].isdigit() else 'unknown'
            
            filename = f"{key}_Annual_Report.pdf"
            
            filepath = self.download_with_retry(url, filename)
            
            if filepath:
                results['successful'] += 1
                results['by_sector'][sector]['successful'] += 1
                results['files'].append({
                    'key': key,
                    'company': company,
                    'sector': sector,
                    'year': year,
                    'filename': os.path.basename(filepath),
                    'url': url,
                    'size_kb': os.path.getsize(filepath) // 1024
                })
            elif os.path.exists(os.path.join(self.raw_dir, filename)):
                results['skipped'] += 1
            else:
                results['failed'] += 1
            
            # Rate limiting
            import time
            time.sleep(0.5)
        
        # Summary
        print("\n" + "=" * 70)
        print("CORPUS EXPANSION COMPLETE")
        print("=" * 70)
        print(f"Attempted: {results['attempted']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"Skipped (already existed): {results['skipped']}")
        print("\nBy Sector:")
        for sector, stats in sorted(results['by_sector'].items()):
            success_rate = stats['successful'] / stats['attempted'] * 100 if stats['attempted'] > 0 else 0
            print(f"  {sector}: {stats['successful']}/{stats['attempted']} ({success_rate:.0f}%)")
        
        # Save manifest
        manifest_path = os.path.join(self.base_dir, 'expanded_corpus_manifest.json')
        with open(manifest_path, 'w') as f:
            json.dump({
                'created_at': datetime.now().isoformat(),
                'note': 'Manually curated URLs from company investor relations pages',
                'results': results
            }, f, indent=2)
        
        print(f"\nManifest saved to: {manifest_path}")
        
        # List all PDF files now in corpus
        all_pdfs = [f for f in os.listdir(self.raw_dir) if f.endswith('.pdf')]
        print(f"\nTotal PDFs in raw_pdfs/: {len(all_pdfs)}")
        
        return results


if __name__ == "__main__":
    expander = ManualCorpusExpander()
    results = expander.run()
    
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Run corpus_filter.py to validate all downloaded files")
    print("2. Update valid_annual_reports.txt with new valid files")
    print("3. Re-run test_phase4_valid_corpus.py on expanded dataset")
