#!/usr/bin/env python3
"""
Direct PDF scraper for NSE-listed companies.
Bypasses the NSE website and fetches annual reports directly from company websites.
"""

import os
import re
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime

# Try requests, fall back to urllib
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False

OUTPUT_DIR = Path("nse_audit_data/raw_pdfs")
MANIFEST_FILE = Path("nse_audit_data/direct_scrape_manifest.json")

# Top 20 NSE-listed companies with direct links to their investor relations pages
COMPANY_REPORTS = {
    "Safaricom": [
        ("2023", "https://www.safaricom.co.ke/images/investor_relations/annual_reports/Safaricom_Annual_Report_2023.pdf"),
        ("2022", "https://www.safaricom.co.ke/images/investor_relations/annual_reports/Safaricom_Annual_Report_2022.pdf"),
    ],
    "Equity_Bank": [
        ("2023", "https://equitygroupholdings.com/wp-content/uploads/2024/03/Equity-Bank-Annual-Report-2023.pdf"),
        ("2022", "https://equitygroupholdings.com/wp-content/uploads/2023/03/Equity-Bank-Integrated-Annual-Report-2022.pdf"),
    ],
    "KCB_Group": [
        ("2023", "https://kcbgroup.com/wp-content/uploads/2024/03/KCB-Group-Annual-Report-2023.pdf"),
        ("2022", "https://kcbgroup.com/wp-content/uploads/2023/03/KCB-Group-Integrated-Annual-Report-2022.pdf"),
    ],
    "Cooperative_Bank": [
        ("2023", "https://coopbank.co.ke/wp-content/uploads/2024/03/Co-operative-Bank-Annual-Report-2023.pdf"),
        ("2022", "https://coopbank.co.ke/wp-content/uploads/2023/03/Co-operative-Bank-Annual-Report-2022.pdf"),
    ],
    "NCBA_Group": [
        ("2023", "https://ncbagroup.com/wp-content/uploads/2024/03/NCBA-Annual-Report-2023.pdf"),
        ("2022", "https://ncbagroup.com/wp-content/uploads/2023/03/NCBA-Integrated-Annual-Report-2022.pdf"),
    ],
    "DTB_Kenya": [
        ("2023", "https://dtbafrica.com/images/reports/DTB-Kenya-Annual-Report-2023.pdf"),
        ("2022", "https://dtbafrica.com/images/reports/DTB-Kenya-Annual-Report-2022.pdf"),
    ],
    "Stanbic_Holdings": [
        ("2023", "https://stanbichafrica.com/sites/default/files/media/documents/2024-03/Stanbic-Holdings-Kenya-Annual-Report-2023.pdf"),
        ("2022", "https://stanbichafrica.com/sites/default/files/media/documents/2023-03/Stanbic-Holdings-Kenya-Annual-Report-2022.pdf"),
    ],
    "Absa_Bank_Kenya": [
        ("2023", "https://absabank.co.ke/content/dam/absa-web/ke/investor-relations/annual-reports/Absa%20Bank%20Kenya%20Annual%20Report%202023.pdf"),
        ("2022", "https://absabank.co.ke/content/dam/absa-web/ke/investor-relations/annual-reports/Absa%20Bank%20Kenya%20Annual%20Report%202022.pdf"),
    ],
    "Britam_Holdings": [
        ("2023", "https://britam.com/images/investor-relations/reports/Britam-Annual-Report-2023.pdf"),
        ("2022", "https://britam.com/images/investor-relations/reports/Britam-Annual-Report-2022.pdf"),
    ],
    "Jubilee_Holdings": [
        ("2023", "https://jubileekenya.com/wp-content/uploads/2024/03/Jubilee-Holdings-Annual-Report-2023.pdf"),
        ("2022", "https://jubileekenya.com/wp-content/uploads/2023/03/Jubilee-Holdings-Annual-Report-2022.pdf"),
    ],
    "CIC_Insurance": [
        ("2023", "https://cicinsurancegroup.com/wp-content/uploads/2024/03/CIC-Insurance-Annual-Report-2023.pdf"),
        ("2022", "https://cicinsurancegroup.com/wp-content/uploads/2023/03/CIC-Insurance-Annual-Report-2022.pdf"),
    ],
    "Sanlam_Kenya": [
        ("2023", "https://sanlam.co.ke/wp-content/uploads/2024/03/Sanlam-Kenya-Annual-Report-2023.pdf"),
        ("2022", "https://sanlam.co.ke/wp-content/uploads/2023/03/Sanlam-Kenya-Annual-Report-2022.pdf"),
    ],
    "EABL": [
        ("2023", "https://eabl.com/wp-content/uploads/2024/03/EABL-Annual-Report-2023.pdf"),
        ("2022", "https://eabl.com/wp-content/uploads/2023/03/EABL-Annual-Report-2022.pdf"),
    ],
    "BAT_Kenya": [
        ("2023", "https://batkenya.com/wp-content/uploads/2024/03/BAT-Kenya-Annual-Report-2023.pdf"),
        ("2022", "https://batkenya.com/wp-content/uploads/2023/03/BAT-Kenya-Annual-Report-2022.pdf"),
    ],
    "Longhorn_Publishers": [
        ("2023", "https://longhornpublishers.com/wp-content/uploads/2024/03/Longhorn-Annual-Report-2023.pdf"),
        ("2022", "https://longhornpublishers.com/wp-content/uploads/2023/03/Longhorn-Annual-Report-2022.pdf"),
    ],
    "Bamburi_Cement": [
        ("2023", "https://bamburicement.com/wp-content/uploads/2024/03/Bamburi-Cement-Annual-Report-2023.pdf"),
        ("2022", "https://bamburicement.com/wp-content/uploads/2023/03/Bamburi-Cement-Annual-Report-2022.pdf"),
    ],
    "KenGen": [
        ("2023", "https://kengen.co.ke/wp-content/uploads/2024/03/KenGen-Annual-Report-2023.pdf"),
        ("2022", "https://kengen.co.ke/wp-content/uploads/2023/03/KenGen-Annual-Report-2022.pdf"),
    ],
    "Centum_Investment": [
        ("2023", "https://centum.co.ke/wp-content/uploads/2024/03/Centum-Annual-Report-2023.pdf"),
        ("2022", "https://centum.co.ke/wp-content/uploads/2023/03/Centum-Annual-Report-2022.pdf"),
    ],
    "Nation_Media_Group": [
        ("2023", "https://nationmedia.com/wp-content/uploads/2024/03/NMG-Annual-Report-2023.pdf"),
        ("2022", "https://nationmedia.com/wp-content/uploads/2023/03/NMG-Annual-Report-2022.pdf"),
    ],
    "Sasini": [
        ("2023", "https://sasini.co.ke/wp-content/uploads/2024/03/Sasini-Annual-Report-2023.pdf"),
        ("2022", "https://sasini.co.ke/wp-content/uploads/2023/03/Sasini-Annual-Report-2022.pdf"),
    ],
}


def download_file(url: str, filepath: Path) -> bool:
    """Download a file from URL to filepath."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        if HAS_REQUESTS:
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(filepath, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
        
        return True
        
    except Exception as e:
        print(f"      Download failed: {str(e)[:100]}")
        return False


def get_file_hash(filepath: Path) -> str:
    """Calculate MD5 hash of file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    manifest = {
        "scrape_date": datetime.now().isoformat(),
        "total_companies": len(COMPANY_REPORTS),
        "total_reports_attempted": 0,
        "successful_downloads": 0,
        "failed_downloads": 0,
        "companies": {}
    }
    
    print("=" * 70)
    print("DIRECT NSE COMPANY ANNUAL REPORT SCRAPER")
    print("=" * 70)
    print(f"Companies: {len(COMPANY_REPORTS)}")
    print(f"Reports per company: up to 2 years (2022, 2023)")
    print()
    
    total_attempted = 0
    total_success = 0
    total_failed = 0
    
    for idx, (company, reports) in enumerate(COMPANY_REPORTS.items(), 1):
        print(f"[{idx}/{len(COMPANY_REPORTS)}] {company}")
        
        company_data = {
            "years_attempted": [],
            "years_downloaded": [],
            "files": []
        }
        
        for year, url in reports:
            total_attempted += 1
            company_data["years_attempted"].append(year)
            
            # Create filename
            safe_company = company.replace(" ", "_").replace("-", "_")
            filename = f"{safe_company}_{year}_Annual_Report.pdf"
            filepath = OUTPUT_DIR / filename
            
            # Check if already exists
            if filepath.exists():
                print(f"      [{year}] Already exists, skipping")
                company_data["years_downloaded"].append(year)
                company_data["files"].append({
                    "year": year,
                    "filename": filename,
                    "status": "already_exists"
                })
                total_success += 1
                continue
            
            print(f"      [{year}] Downloading...", end=" ", flush=True)
            
            success = download_file(url, filepath)
            
            if success and filepath.exists():
                file_size = filepath.stat().st_size
                file_hash = get_file_hash(filepath)
                
                # Validate it's a real PDF
                with open(filepath, 'rb') as f:
                    header = f.read(8)
                    if not header.startswith(b'%PDF'):
                        print(f"WARNING: File is not a valid PDF, removing")
                        filepath.unlink()
                        total_failed += 1
                        company_data["files"].append({
                            "year": year,
                            "filename": filename,
                            "status": "invalid_pdf",
                            "error": "Not a PDF file"
                        })
                        continue
                
                print(f"OK ({file_size:,} bytes)")
                total_success += 1
                company_data["years_downloaded"].append(year)
                company_data["files"].append({
                    "year": year,
                    "filename": filename,
                    "status": "success",
                    "size_bytes": file_size,
                    "md5": file_hash
                })
            else:
                total_failed += 1
                company_data["files"].append({
                    "year": year,
                    "filename": filename,
                    "status": "failed",
                    "error": "Download failed or invalid content"
                })
                if filepath.exists():
                    filepath.unlink()
            
            time.sleep(0.5)  # Rate limiting
        
        manifest["companies"][company] = company_data
        print()
    
    # Update totals
    manifest["total_reports_attempted"] = total_attempted
    manifest["successful_downloads"] = total_success
    manifest["failed_downloads"] = total_failed
    
    # Save manifest
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print("=" * 70)
    print("SCRAPING COMPLETE")
    print("=" * 70)
    print(f"Total attempted: {total_attempted}")
    print(f"Successful: {total_success} ({100*total_success/max(1,total_attempted):.1f}%)")
    print(f"Failed: {total_failed}")
    print()
    print(f"Manifest saved to: {MANIFEST_FILE}")
    print()
    print("=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Run corpus_filter.py to validate downloaded files are annual reports")
    print("2. Run test_phase4_valid_corpus.py on expanded dataset")
    print("3. Review manifest for any failed downloads")


if __name__ == "__main__":
    main()
