#!/usr/bin/env python3
"""
NSE Annual Report Scraper - Cloudflare Bypass Version
Downloads audited results from NSE website using cloudscraper
"""

import cloudscraper
from bs4 import BeautifulSoup
import os
import time
from pathlib import Path

def drain_nse_announcements():
    """Scrape NSE announcements for audited annual reports"""
    
    # Setup stealth scraper mimicking Windows Chrome
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    
    # Create directory structure
    base_dir = Path("nse_data/raw_pdfs")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Separate directories for NSE companies vs SACCOS
    nse_dir = Path("nse_data/nse_companies")
    sacco_dir = Path("nse_data/saccos")
    nse_dir.mkdir(parents=True, exist_ok=True)
    sacco_dir.mkdir(parents=True, exist_ok=True)
    
    target_urls = [
        "https://www.nse.co.ke/listed-company-announcements/",
        "https://www.nse.co.ke/company-announcements/"
    ]
    
    total_downloaded = 0
    
    for target_url in target_urls:
        print(f"\n🔗 Accessing: {target_url}")
        
        try:
            response = scraper.get(target_url, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Blocked with status: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract PDF links
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.text.lower()
                
                # Filter for audited results and annual reports
                if ".pdf" in href and any(keyword in text for keyword in ["audited", "annual report", "financial statements"]):
                    pdf_name = href.split("/")[-1]
                    
                    # Determine destination based on content
                    destination = nse_dir
                    
                    # Check if it's a SACCOS document
                    if any(sacco_keyword in text.lower() for sacco_keyword in ["sacco", "sasra", "stima", "kenya police"]):
                        destination = sacco_dir
                    
                    filepath = destination / pdf_name
                    
                    if filepath.exists():
                        print(f"⏭️  Skipping (exists): {pdf_name}")
                        continue
                    
                    print(f"📥 Downloading: {pdf_name}")
                    
                    try:
                        pdf_response = scraper.get(href, timeout=60)
                        if pdf_response.status_code == 200:
                            with open(filepath, "wb") as f:
                                f.write(pdf_response.content)
                            total_downloaded += 1
                            print(f"✅ Saved to: {filepath}")
                        else:
                            print(f"❌ Failed to download {pdf_name}: HTTP {pdf_response.status_code}")
                        
                        time.sleep(1)  # Ethical delay
                        
                    except Exception as e:
                        print(f"⚠️  Error downloading {pdf_name}: {e}")
                        
        except Exception as e:
            print(f"⚠️  Critical Failure accessing {target_url}: {e}")
            time.sleep(5)
    
    print(f"\n{'='*60}")
    print(f"✅ DOWNLOAD COMPLETE: {total_downloaded} new reports saved")
    print(f"📁 NSE Companies: {len(list(nse_dir.glob('*.pdf')))} files")
    print(f"📁 SACCOS: {len(list(sacco_dir.glob('*.pdf')))} files")
    print(f"{'='*60}")

if __name__ == "__main__":
    drain_nse_announcements()
