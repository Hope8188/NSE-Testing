#!/usr/bin/env python3
"""
CORPUS FILTER: Identify which PDFs are valid NSE-listed company annual reports
vs. NSE institutional documents, vendor lists, training calendars, etc.

This script implements the ANNUAL_REPORT_SIGNALS gate before any governance analysis.
"""

import os
import re
from pathlib import Path

# Signals that indicate a valid annual report from a LISTED COMPANY
ANNUAL_REPORT_SIGNALS = [
    r"integrated\s+report",
    r"annual\s+report",
    r"financial\s+statements",  # Removed year requirement - may be on different line
    r"directors[\'\s]+report",
    r"report\s+of\s+the\s+directors",
    r"statement\s+of\s+financial\s+position",
    r"independent\s+auditor.*?report",
    r"\d{4}\s*integrated\s+report",  # "2018 Integrated Report" pattern
    r"\d{4}\s*annual\s+report",  # "2018 Annual Report" pattern
]

# Patterns that indicate NON-annual-report documents (institutional, vendor, training, etc.)
EXCLUSION_PATTERNS = [
    r"broker\s+back\s+office",
    r"prequalified\s+vendors",
    r"data\s+pricelist",
    r"training\s+calendar",
    r"training\s+calender",  # Alternate spelling
    r"strategy\s*\d{4}\s*[-–]\s*\d{4}",  # Strategy 2025-2029 pattern
    r"confidential\s*–\s*nse\s+strategic",
    r"aide\s+memoire",
    r"chairman[\'s]*\s*aide",
    r"minimum\s+standards",
    r"vendor\s+list",
    r"price\s*list",
    r"agm\s+.*\s+meeting\s+held",  # AGM meeting docs (not the annual report itself)
]

def is_annual_report(text: str) -> bool:
    """
    Require at least 2 positive signals AND zero exclusion patterns.
    This prevents false positives from boilerplate compliance language.
    """
    # First check exclusions - if any match, reject immediately
    for pattern in EXCLUSION_PATTERNS:
        if re.search(pattern, text[:3000], re.IGNORECASE):
            return False
    
    # Count positive signals
    hits = sum(1 for p in ANNUAL_REPORT_SIGNALS 
               if re.search(p, text[:3000], re.IGNORECASE))
    
    return hits >= 2  # Require at least 2 signals

def classify_pdf(pdf_path: str) -> dict:
    """Classify a single PDF file."""
    import fitz  # PyMuPDF
    
    filename = os.path.basename(pdf_path)
    
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc[:3]:  # Only check first 3 pages for classification
            text += page.get_text() + "\n"
        doc.close()
        
        if not text or len(text.strip()) < 100:
            return {
                'filename': filename,
                'classification': 'UNREADABLE',
                'reason': 'Could not extract text or text too short'
            }
        
        if is_annual_report(text):
            # Try to identify the company name and year
            company_match = re.search(r'^([A-Z][a-zA-Z\s&\.]+)(?:\s+limited|\s+plc|\s+ltd)?', 
                                      text[:500], re.IGNORECASE | re.MULTILINE)
            year_match = re.search(r'\b(20\d{2}|20\d{3})\b', text[:1000])
            
            return {
                'filename': filename,
                'classification': 'VALID_ANNUAL_REPORT',
                'company': company_match.group(1).strip() if company_match else 'Unknown',
                'year': year_match.group(1) if year_match else 'Unknown',
                'signals_found': sum(1 for p in ANNUAL_REPORT_SIGNALS 
                                    if re.search(p, text[:3000], re.IGNORECASE))
            }
        else:
            # Find which exclusion pattern matched
            exclusion_reason = 'No specific reason'
            for pattern in EXCLUSION_PATTERNS:
                if re.search(pattern, text[:3000], re.IGNORECASE):
                    exclusion_reason = f"Matched exclusion pattern: {pattern}"
                    break
            
            return {
                'filename': filename,
                'classification': 'EXCLUDED_NON_ANNUAL_REPORT',
                'reason': exclusion_reason
            }
            
    except Exception as e:
        return {
            'filename': filename,
            'classification': 'ERROR',
            'reason': str(e)
        }

def main():
    pdf_dir = Path('nse_audit_data/raw_pdfs')
    pdf_files = list(pdf_dir.glob('*.pdf'))
    
    print(f"{'='*80}")
    print(f"CORPUS VALIDATION: Classifying {len(pdf_files)} PDF files")
    print(f"{'='*80}\n")
    
    valid_reports = []
    excluded_files = []
    errors = []
    
    for pdf_path in sorted(pdf_files):
        result = classify_pdf(str(pdf_path))
        print(f"File: {result['filename']}")
        print(f"  Classification: {result['classification']}")
        
        if result['classification'] == 'VALID_ANNUAL_REPORT':
            print(f"  → Company: {result['company']}")
            print(f"  → Year: {result['year']}")
            print(f"  → Signals: {result['signals_found']}")
            valid_reports.append(result)
        elif result['classification'] == 'EXCLUDED_NON_ANNUAL_REPORT':
            print(f"  → Reason: {result['reason']}")
            excluded_files.append(result)
        else:
            print(f"  → Reason: {result['reason']}")
            errors.append(result)
        
        print()
    
    print(f"{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Valid Annual Reports: {len(valid_reports)}")
    print(f"Excluded (non-annual-report): {len(excluded_files)}")
    print(f"Errors/Unreadable: {len(errors)}")
    print(f"\nTotal files processed: {len(pdf_files)}")
    
    if valid_reports:
        print(f"\n✓ VALID CORPUS ({len(valid_reports)} files):")
        for r in valid_reports:
            print(f"   - {r['company']} ({r['year']}): {r['filename']}")
    
    if excluded_files:
        print(f"\n✗ EXCLUDED FILES ({len(excluded_files)} files):")
        for r in excluded_files:
            print(f"   - {r['filename']}: {r['reason']}")
    
    # Save the valid corpus list
    with open('nse_audit_data/valid_annual_reports.txt', 'w') as f:
        f.write("# Valid NSE-Listed Company Annual Reports\n")
        f.write(f"# Generated: {__import__('datetime').datetime.now().isoformat()}\n")
        f.write(f"# Total: {len(valid_reports)} files\n\n")
        for r in valid_reports:
            f.write(f"{r['filename']}\t{r['company']}\t{r['year']}\n")
    
    print(f"\n✓ Saved valid corpus list to: nse_audit_data/valid_annual_reports.txt")
    
    return valid_reports, excluded_files, errors

if __name__ == '__main__':
    main()
