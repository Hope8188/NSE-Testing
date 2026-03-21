#!/usr/bin/env python3
"""
Scrape annual reports from ALL 66 NSE-listed companies.
This script:
1. Fetches the complete list of listed companies from NSE
2. For each company, searches for annual reports (2019-2024)
3. Downloads PDFs to nse_audit_data/raw_pdfs/
4. Creates a manifest file with download status
"""

import requests
from bs4 import BeautifulSoup
import fitz  # pymupdf
import os
import json
import time
import re
from urllib.parse import urljoin, quote
from datetime import datetime

class NSEFullScraper:
    def __init__(self, base_dir="nse_audit_data"):
        self.base_dir = base_dir
        self.raw_dir = os.path.join(base_dir, "raw_pdfs")
        self.text_dir = os.path.join(base_dir, "processed_text")
        self.manifest_file = os.path.join(base_dir, "scrape_manifest.json")
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        for d in [self.raw_dir, self.text_dir]:
            os.makedirs(d, exist_ok=True)
        
        self.manifest = self._load_manifest()
    
    def _load_manifest(self):
        """Load existing manifest or create new one."""
        if os.path.exists(self.manifest_file):
            with open(self.manifest_file, 'r') as f:
                return json.load(f)
        return {"companies": {}, "scraped_at": None, "total_downloaded": 0}
    
    def _save_manifest(self):
        """Save manifest to disk."""
        self.manifest["scraped_at"] = datetime.now().isoformat()
        with open(self.manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def get_listed_companies(self):
        """
        Scrape the NSE website for the complete list of listed companies.
        Returns list of {name, symbol, sector, page_url}
        """
        print("[*] Fetching list of all NSE-listed companies...")
        
        # Try multiple possible URLs for company listings
        urls_to_try = [
            "https://www.nse.co.ke/listed-companies/",
            "https://www.nse.co.ke/equities/",
            "https://www.nse.co.ke/market-data/equities/",
        ]
        
        companies = []
        
        for url in urls_to_try:
            try:
                print(f"  Trying {url}...")
                resp = requests.get(url, headers=self.headers, timeout=30)
                if resp.status_code != 200:
                    continue
                
                soup = BeautifulSoup(resp.content, 'html.parser')
                
                # Look for company links - various patterns
                company_links = []
                
                # Pattern 1: Links in tables
                for table in soup.find_all('table'):
                    for row in table.find_all('tr'):
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            link_cell = cells[0].find('a', href=True)
                            if link_cell:
                                name = link_cell.get_text(strip=True)
                                href = link_cell['href']
                                if name and len(name) > 2:
                                    company_links.append({
                                        "name": name,
                                        "url": urljoin(url, href)
                                    })
                
                # Pattern 2: Links in lists with company-like names
                for a in soup.find_all('a', href=True):
                    text = a.get_text(strip=True)
                    href = a['href']
                    # Heuristic: company names are typically 2-50 chars, not generic terms
                    if (text and 
                        2 < len(text) < 50 and 
                        not any(x in text.lower() for x in ['home', 'contact', 'about', 'login', 'register']) and
                        not text.lower().endswith('.pdf')):
                        company_links.append({
                            "name": text,
                            "url": urljoin(url, href)
                        })
                
                if company_links:
                    print(f"  Found {len(company_links)} potential companies at {url}")
                    companies = company_links
                    break
                    
            except Exception as e:
                print(f"  Error at {url}: {e}")
                continue
        
        if not companies:
            print("[!] Could not scrape company list. Falling back to known company names...")
            companies = self._get_fallback_companies()
        
        return companies
    
    def _get_fallback_companies(self):
        """Fallback list of major NSE-listed companies if scraping fails."""
        # Major NSE-listed companies (subset of 66)
        known_companies = [
            "Safaricom", "Equity Bank", "KCB Group", "Co-operative Bank", 
            "NCBA Group", "Diamond Trust Bank", "Stanbic Holdings", "Absa Bank Kenya",
            "Kenya Commercial Bank", "Family Bank", "I&M Holdings", "Bank of Africa Kenya",
            "East African Breweries", "Kenya Airways", "Carbacid Investments",
            "British American Tobacco Kenya", "KenolCobil", "TotalEnergies Kenya",
            "Vida Creamery", "Longhorn Publishers", "Nation Media Group",
            "Standard Chartered Kenya", "Citibank Kenya", "Barclays Bank Kenya",
            " Housing Finance Group", "Home Afrika", "Olympia Capital Holdings",
            "Dormans Coffee", "Kapchorua Tea", "Williamson Tea", "James Finlay Kenya",
            "Car & General", "Sameer Africa", "Scangroup", "Bamburi Cement",
            "Armour Group", "East African Portland Cement", "Mumias Sugar",
            "TransCentury", "Uchumi Supermarkets", "Naivas Limited", "Quickmart",
            "Centum Investment", "Britam Holdings", "Jubilee Holdings", "Liberty Kenya",
            "Sanlam Kenya", "Kenya Reinsurance", "CIC Insurance", "Direct Line Assurance",
            "Kenya Power", "KenGen", "Telkom Kenya", "Jamii Telecommunications",
            "Access Kenya", "Swan Telecom", "Sasini", "Rai International",
            "Carcuri", " Williamson Tea", "Kakuzi", "Del Monte Kenya",
            "Limuru Tea", "Hapi Energy", "Gulf Energy", "Orion Industries"
        ]
        
        return [{"name": name, "url": None} for name in known_companies]
    
    def search_company_reports(self, company_name, company_url=None):
        """
        Search for annual reports for a specific company.
        Returns list of {url, year, title}
        """
        reports = []
        search_terms = [
            f"{company_name} annual report",
            f"{company_name} integrated report",
            f"{company_name} financial statements",
        ]
        
        # If we have a company page URL, start there
        urls_to_search = []
        if company_url:
            urls_to_search.append(company_url)
        
        # Also search main NSE site
        urls_to_search.extend([
            "https://www.nse.co.ke/annual-reports/",
            "https://www.nse.co.ke/",
        ])
        
        for base_url in urls_to_search:
            try:
                print(f"    Searching {base_url[:50]}...")
                resp = requests.get(base_url, headers=self.headers, timeout=20)
                if resp.status_code != 200:
                    continue
                
                soup = BeautifulSoup(resp.content, 'html.parser')
                
                # Find PDF links
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if not href.lower().endswith('.pdf'):
                        continue
                    
                    text = a.get_text(strip=True).lower()
                    full_url = urljoin(base_url, href)
                    
                    # Check if this is an annual report for our company
                    company_match = company_name.lower().split()[0] in text or \
                                   company_name.lower() in text.replace(" ", "")
                    
                    year_match = re.search(r'(201\d|202\d)', text)
                    annual_match = any(x in text for x in ['annual', 'integrated', 'financial'])
                    
                    if (company_match or base_url == company_url) and annual_match:
                        year = year_match.group(1) if year_match else "unknown"
                        title = a.get_text(strip=True) or f"{company_name}_{year}"
                        
                        reports.append({
                            "url": full_url,
                            "year": year,
                            "title": title,
                            "company": company_name
                        })
                        
            except Exception as e:
                print(f"    Error searching {base_url}: {e}")
                continue
        
        # Deduplicate by URL
        seen = set()
        unique_reports = []
        for r in reports:
            if r["url"] not in seen:
                seen.add(r["url"])
                unique_reports.append(r)
        
        return unique_reports
    
    def download_pdf(self, url, filename):
        """Download a PDF file."""
        filepath = os.path.join(self.raw_dir, filename)
        
        if os.path.exists(filepath):
            print(f"    [SKIP] Already exists: {filename}")
            return filepath
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=60)
            if resp.status_code != 200:
                print(f"    [FAIL] HTTP {resp.status_code}: {url}")
                return None
            
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            
            # Verify it's a valid PDF
            try:
                doc = fitz.open(filepath)
                if doc.page_count == 0:
                    print(f"    [WARN] Empty PDF: {filename}")
                    os.remove(filepath)
                    return None
                doc.close()
            except:
                print(f"    [WARN] Invalid PDF: {filename}")
                os.remove(filepath)
                return None
            
            print(f"    [OK] Downloaded: {filename} ({len(resp.content)//1024} KB)")
            return filepath
            
        except Exception as e:
            print(f"    [ERROR] {e}")
            return None
    
    def run(self, max_per_company=3, target_companies=None):
        """
        Main scraping routine.
        
        Args:
            max_per_company: Max reports to download per company
            target_companies: Optional list of specific company names to focus on
        """
        print("=" * 60)
        print("NSE FULL SCRAPER - All 66 Listed Companies")
        print("=" * 60)
        
        # Get company list
        companies = self.get_listed_companies()
        print(f"\n[*] Found {len(companies)} companies")
        
        if target_companies:
            companies = [c for c in companies if c["name"] in target_companies]
            print(f"[*] Filtering to {len(companies)} target companies")
        
        total_downloaded = 0
        successful_companies = 0
        
        for i, company in enumerate(companies, 1):
            company_name = company["name"]
            print(f"\n[{i}/{len(companies)}] {company_name}")
            
            # Initialize company in manifest
            if company_name not in self.manifest["companies"]:
                self.manifest["companies"][company_name] = {
                    "reports_found": 0,
                    "reports_downloaded": 0,
                    "files": []
                }
            
            # Search for reports
            reports = self.search_company_reports(
                company_name, 
                company.get("url")
            )
            
            if not reports:
                print(f"  [!] No reports found for {company_name}")
                continue
            
            print(f"  Found {len(reports)} report(s)")
            self.manifest["companies"][company_name]["reports_found"] = len(reports)
            
            # Download up to max_per_company
            downloaded = 0
            for report in reports[:max_per_company]:
                year = report["year"]
                safe_name = re.sub(r'[^\w\s-]', '', company_name)
                filename = f"{safe_name}_{year}_annual_report.pdf"
                
                filepath = self.download_pdf(report["url"], filename)
                
                if filepath:
                    downloaded += 1
                    total_downloaded += 1
                    self.manifest["companies"][company_name]["files"].append({
                        "filename": filename,
                        "year": year,
                        "url": report["url"],
                        "size_kb": os.path.getsize(filepath) // 1024
                    })
                
                time.sleep(0.5)  # Be polite to the server
            
            self.manifest["companies"][company_name]["reports_downloaded"] = downloaded
            if downloaded > 0:
                successful_companies += 1
            
            # Save progress after each company
            self._save_manifest()
            
            # Rate limiting
            time.sleep(1)
        
        # Final summary
        print("\n" + "=" * 60)
        print("SCRAPING COMPLETE")
        print("=" * 60)
        print(f"Companies processed: {len(companies)}")
        print(f"Companies with downloads: {successful_companies}")
        print(f"Total PDFs downloaded: {total_downloaded}")
        print(f"Manifest saved to: {self.manifest_file}")
        
        return {
            "companies_processed": len(companies),
            "successful_companies": successful_companies,
            "total_downloaded": total_downloaded
        }


if __name__ == "__main__":
    scraper = NSEFullScraper()
    
    # Optional: focus on specific companies first
    # target = ["Safaricom", "Equity Bank", "KCB Group", "Co-operative Bank"]
    target = None  # Process all
    
    results = scraper.run(max_per_company=3, target_companies=target)
    
    print("\nNext steps:")
    print("1. Review nse_audit_data/scrape_manifest.json for download status")
    print("2. Run corpus_filter.py to identify valid annual reports")
    print("3. Run test_phase4_valid_corpus.py on the expanded dataset")
