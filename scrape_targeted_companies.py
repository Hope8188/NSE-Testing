#!/usr/bin/env python3
"""
Focused scraper: Download annual reports from top 20 NSE-listed companies.
This is a pragmatic approach to build a meaningful corpus without waiting hours.

Targets the most liquid and significant companies by market cap and sector representation.
"""

import requests
from bs4 import BeautifulSoup
import fitz
import os
import json
import time
import re
from urllib.parse import urljoin
from datetime import datetime

class TargetedScraper:
    def __init__(self, base_dir="nse_audit_data"):
        self.base_dir = base_dir
        self.raw_dir = os.path.join(base_dir, "raw_pdfs")
        self.text_dir = os.path.join(base_dir, "processed_text")
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.text_dir, exist_ok=True)
        
        # Top 20 NSE companies by market cap/liquidity (representing all sectors)
        self.target_companies = [
            # Banking & Finance (largest sector)
            ("Safaricom", "Telecommunications"),
            ("Equity Bank", "Banking"),
            ("KCB Group", "Banking"),
            ("Co-operative Bank", "Banking"),
            ("NCBA Group", "Banking"),
            ("Diamond Trust Bank", "Banking"),
            ("Stanbic Holdings", "Banking"),
            ("Absa Bank Kenya", "Banking"),
            ("I&M Holdings", "Banking"),
            ("Family Bank", "Banking"),
            
            # Insurance
            ("Britam Holdings", "Insurance"),
            ("Jubilee Holdings", "Insurance"),
            ("CIC Insurance", "Insurance"),
            ("Sanlam Kenya", "Insurance"),
            
            # Agriculture & Tea
            ("Sasini", "Agriculture"),
            ("Williamson Tea", "Agriculture"),
            ("Kapchorua Tea", "Agriculture"),
            ("Kakuzi", "Agriculture"),
            
            # Manufacturing & Consumer Goods
            ("East African Breweries", "Manufacturing"),
            ("British American Tobacco Kenya", "Manufacturing"),
            ("Longhorn Publishers", "Manufacturing"),
            ("Bamburi Cement", "Manufacturing"),
            
            # Energy & Utilities
            ("KenGen", "Energy"),
            ("Kenya Power", "Utilities"),
            
            # Real Estate & Investment
            ("Centum Investment", "Investment"),
            ("Home Afrika", "Real Estate"),
            
            # Media
            ("Nation Media Group", "Media"),
            
            # Transport
            ("Kenya Airways", "Transport"),
        ]
    
    def search_nse_for_company_reports(self, company_name):
        """
        Search NSE website for a specific company's annual reports.
        Uses multiple search strategies.
        """
        reports = []
        
        # Strategy 1: Direct URL patterns
        base_urls = [
            f"https://www.nse.co.ke/annual-reports/",
            f"https://www.nse.co.ke/company/{company_name.lower().replace(' ', '-')}/",
            f"https://www.nse.co.ke/?s={company_name.replace(' ', '+')}+annual+report",
        ]
        
        for url in base_urls[:1]:  # Start with main annual reports page
            try:
                print(f"      Searching {url}...")
                resp = requests.get(url, headers=self.headers, timeout=15)
                if resp.status_code != 200:
                    continue
                
                soup = BeautifulSoup(resp.content, 'html.parser')
                
                # Find all PDF links
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if not href.lower().endswith('.pdf'):
                        continue
                    
                    text = a.get_text(strip=True).lower()
                    full_url = urljoin(url, href)
                    
                    # Check if this report belongs to our target company
                    company_keywords = company_name.lower().split()
                    name_match = any(kw in text for kw in company_keywords) or \
                                company_name.lower().replace(' ', '') in text.replace(' ', '')
                    
                    # Check if it's an annual/integrated report
                    report_type_match = any(x in text for x in [
                        'annual report', 'integrated report', 'financial statements'
                    ])
                    
                    # Extract year
                    year_match = re.search(r'(201\d|202\d)', text)
                    year = year_match.group(1) if year_match else None
                    
                    if name_match and report_type_match:
                        # Avoid duplicates
                        if not any(r['url'] == full_url for r in reports):
                            reports.append({
                                'url': full_url,
                                'year': year,
                                'title': a.get_text(strip=True),
                                'company': company_name
                            })
                            print(f"        Found: {a.get_text(strip=True)[:60]}")
                
            except Exception as e:
                print(f"        Error: {e}")
        
        return reports
    
    def download_pdf(self, url, filename):
        """Download a PDF with validation."""
        filepath = os.path.join(self.raw_dir, filename)
        
        if os.path.exists(filepath):
            print(f"        [SKIP] Already exists")
            return filepath
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=60)
            if resp.status_code != 200:
                print(f"        [FAIL] HTTP {resp.status_code}")
                return None
            
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            
            # Validate PDF
            try:
                doc = fitz.open(filepath)
                pages = doc.page_count
                doc.close()
                
                if pages == 0:
                    os.remove(filepath)
                    return None
                
                print(f"        [OK] {pages} pages, {len(resp.content)//1024} KB")
                return filepath
                
            except Exception as e:
                print(f"        [WARN] Invalid PDF: {e}")
                os.remove(filepath)
                return None
                
        except Exception as e:
            print(f"        [ERROR] {e}")
            return None
    
    def run(self, max_years_per_company=2):
        """Execute targeted scraping."""
        print("=" * 70)
        print("TARGETED NSE SCRAPER - Top Companies")
        print("=" * 70)
        print(f"Target companies: {len(self.target_companies)}")
        print(f"Max years per company: {max_years_per_company}")
        print()
        
        results = {
            'companies_processed': 0,
            'companies_with_downloads': 0,
            'total_downloaded': 0,
            'by_sector': {},
            'files': []
        }
        
        for idx, (company, sector) in enumerate(self.target_companies, 1):
            print(f"\n[{idx}/{len(self.target_companies)}] {company} ({sector})")
            
            # Track by sector
            if sector not in results['by_sector']:
                results['by_sector'][sector] = {'companies': 0, 'files': 0}
            
            # Search for reports
            reports = self.search_nse_for_company_reports(company)
            
            if not reports:
                print(f"      [!] No reports found on NSE website")
                # Try fallback: check if we already have this company's reports
                existing = [f for f in os.listdir(self.raw_dir) 
                           if company.lower().split()[0] in f.lower() and f.endswith('.pdf')]
                if existing:
                    print(f"      [INFO] Found {len(existing)} existing file(s)")
                    results['companies_with_downloads'] += 1
                continue
            
            # Download up to max_years_per_company (prefer most recent)
            reports_sorted = sorted(
                [r for r in reports if r['year']], 
                key=lambda x: x['year'], 
                reverse=True
            )[:max_years_per_company]
            
            downloaded = 0
            for report in reports_sorted:
                year = report['year']
                safe_name = re.sub(r'[^\w\s-]', '', company)
                filename = f"{safe_name}_{year}_Annual_Report.pdf"
                
                filepath = self.download_pdf(report['url'], filename)
                
                if filepath:
                    downloaded += 1
                    results['total_downloaded'] += 1
                    results['files'].append({
                        'company': company,
                        'sector': sector,
                        'year': year,
                        'filename': filename,
                        'url': report['url'],
                        'size_kb': os.path.getsize(filepath) // 1024
                    })
                
                time.sleep(0.3)  # Rate limiting
            
            if downloaded > 0:
                results['companies_with_downloads'] += 1
                results['by_sector'][sector]['companies'] += 1
                results['by_sector'][sector]['files'] += downloaded
            
            results['companies_processed'] += 1
            
            # Save progress
            time.sleep(0.5)
        
        # Summary
        print("\n" + "=" * 70)
        print("SCRAPING COMPLETE")
        print("=" * 70)
        print(f"Companies processed: {results['companies_processed']}")
        print(f"Companies with downloads: {results['companies_with_downloads']}")
        print(f"Total PDFs downloaded: {results['total_downloaded']}")
        print("\nBy Sector:")
        for sector, stats in sorted(results['by_sector'].items()):
            if stats['files'] > 0:
                print(f"  {sector}: {stats['companies']} companies, {stats['files']} files")
        
        # Save manifest
        manifest_path = os.path.join(self.base_dir, 'targeted_scrape_manifest.json')
        with open(manifest_path, 'w') as f:
            json.dump({
                'scraped_at': datetime.now().isoformat(),
                'parameters': {
                    'target_companies': len(self.target_companies),
                    'max_years_per_company': max_years_per_company
                },
                'results': results
            }, f, indent=2)
        
        print(f"\nManifest saved to: {manifest_path}")
        
        return results


if __name__ == "__main__":
    scraper = TargetedScraper()
    results = scraper.run(max_years_per_company=2)
    
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Run corpus_filter.py to validate downloaded files are annual reports")
    print("2. Run test_phase4_valid_corpus.py on expanded dataset")
    print("3. Review nse_audit_data/targeted_scrape_manifest.json for details")
