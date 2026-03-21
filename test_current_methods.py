#!/usr/bin/env python3
"""
Phase 3: TEST with CURRENT Methods
Tests basic linguistic extraction using existing PyMuPDF pipeline:
- Section identification logic (Priority-A #8: find MD&A equivalents via regex)
- Safaricom outlier check (Priority-A #2)
- Basic financial metric extraction
"""

import os
import re
from collections import defaultdict

class CurrentMethodTester:
    def __init__(self, text_dir="nse_audit_data/processed_text"):
        self.text_dir = text_dir
        self.results = {}
        
    def load_all_texts(self):
        """Load all extracted text files."""
        texts = {}
        if not os.path.exists(self.text_dir):
            print(f"[!] Directory {self.text_dir} not found")
            return texts
            
        for fname in os.listdir(self.text_dir):
            if fname.endswith('.txt'):
                fpath = os.path.join(self.text_dir, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    texts[fname] = f.read()
        print(f"[*] Loaded {len(texts)} text files")
        return texts
    
    def find_section_via_regex(self, text, section_patterns):
        """
        Priority-A #8: Find MD&A equivalents via regex patterns
        Tests basic section identification logic
        """
        found_sections = {}
        
        for section_name, patterns in section_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    found_sections[section_name] = {
                        'pattern_matched': pattern,
                        'match_count': len(matches),
                        'sample': matches[0][:100] if matches else None
                    }
                    break
        
        return found_sections
    
    def test_section_identification(self, text, filename):
        """Test current method for finding key sections."""
        
        # Define patterns for common annual report sections
        section_patterns = {
            'MD&A': [
                r'management[\'s]? discussion and analysis',
                r'directors[\'s]? report',
                r'chairman[\'s]? statement',
                r'review of operations'
            ],
            'Financial Statements': [
                r'financial statements',
                r'statement of financial position',
                r'income statement',
                r'cash flow statement'
            ],
            'Auditor Report': [
                r'independent auditor[\'s]? report',
                r'report of the auditors',
                r'auditor[\'s]? opinion'
            ],
            'Corporate Governance': [
                r'corporate governance',
                r'board of directors',
                r'directors[\'s]? responsibility'
            ],
            'Risk Management': [
                r'risk management',
                r'principal risks',
                r'risk factors'
            ]
        }
        
        found = self.find_section_via_regex(text, section_patterns)
        
        print(f"\n[Priority-A #8] Section Identification Test:")
        print(f"  File: {filename}")
        
        if found:
            print(f"  Sections Found: {len(found)}/{len(section_patterns)}")
            for section, info in found.items():
                print(f"    ✓ {section}: {info['match_count']} match(es)")
                if info['sample']:
                    print(f"      Sample: \"{info['sample']}...\"")
        else:
            print(f"  ✗ No standard sections identified")
        
        return found
    
    def test_safaricom_outlier(self, text, filename):
        """
        Priority-A #2: Safaricom outlier check
        Ensure large companies don't skew means
        """
        is_safaricom = 'safaricom' in filename.lower() or 'safaricom' in text.lower()[:5000]
        
        # Look for revenue/size indicators
        revenue_pattern = r'(revenue|turnover|gross income)[:\s]*([KES\s\d,\.]+)'
        revenue_matches = re.findall(revenue_pattern, text, re.IGNORECASE)
        
        # Check for employee count
        employee_pattern = r'(\d+[,\d]*)\s*(employees|staff)'
        employee_matches = re.findall(employee_pattern, text, re.IGNORECASE)
        
        size_indicators = {
            'is_safaricom': is_safaricom,
            'revenue_mentions': len(revenue_matches),
            'employee_mentions': len(employee_matches),
            'needs_normalization': is_safaricom or len(revenue_matches) > 5
        }
        
        print(f"\n[Priority-A #2] Safaricom Outlier Check:")
        print(f"  Is Safaricom/Large Entity: {size_indicators['is_safaricom']}")
        print(f"  Revenue mentions: {size_indicators['revenue_mentions']}")
        print(f"  Employee mentions: {size_indicators['employee_mentions']}")
        if size_indicators['needs_normalization']:
            print(f"  ⚠ FLAGGED: Needs normalization in aggregate analysis")
        else:
            print(f"  ✓ Standard entity")
        
        return size_indicators
    
    def test_financial_metric_extraction(self, text, filename):
        """Test basic financial metric extraction with current methods."""
        
        metrics = defaultdict(list)
        
        # Currency amounts (KES)
        kes_pattern = r'KES\s*([\d,]+(?:\.\d+)?)|Ksh\s*([\d,]+(?:\.\d+)?)'
        kes_matches = re.findall(kes_pattern, text, re.IGNORECASE)
        
        # Percentages
        pct_pattern = r'(\d+(?:\.\d+)?)\s*%'
        pct_matches = re.findall(pct_pattern, text)
        
        # Years (for temporal context)
        year_pattern = r'\b(20\d{2}|20\d{3})\b'
        year_matches = re.findall(year_pattern, text)
        
        metrics['currency_values'] = len([m for group in kes_matches for m in group if m])
        metrics['percentages'] = len(pct_matches)
        metrics['years_mentioned'] = len(set(year_matches))
        
        print(f"\n[Current Method] Financial Metric Extraction:")
        print(f"  Currency values found: {metrics['currency_values']}")
        print(f"  Percentages found: {metrics['percentages']}")
        print(f"  Unique years: {metrics['years_mentioned']} ({sorted(set(year_matches))[:5]}...)")
        
        return dict(metrics)
    
    def run_all_tests(self):
        """Run complete test suite with current methods."""
        texts = self.load_all_texts()
        
        if not texts:
            print("[!] No texts to test. Run scraper first.")
            return
        
        print("\n" + "="*70)
        print("PHASE 3: TESTING WITH CURRENT METHODS")
        print("="*70)
        
        for fname, text in texts.items():
            print(f"\n{'='*70}")
            print(f"Testing: {fname}")
            print(f"{'='*70}")
            
            # Test 1: Section Identification
            sections = self.test_section_identification(text, fname)
            
            # Test 2: Outlier Detection
            outlier_info = self.test_safaricom_outlier(text, fname)
            
            # Test 3: Financial Metrics
            metrics = self.test_financial_metric_extraction(text, fname)
            
            # Store results
            self.results[fname] = {
                'sections': sections,
                'outlier': outlier_info,
                'metrics': metrics
            }
        
        # Summary
        print("\n" + "="*70)
        print("CURRENT METHODS SUMMARY")
        print("="*70)
        
        total_files = len(texts)
        files_with_sections = sum(1 for r in self.results.values() if r['sections'])
        flagged_outliers = sum(1 for r in self.results.values() if r['outlier']['needs_normalization'])
        
        avg_sections = sum(len(r['sections']) for r in self.results.values()) / total_files if total_files > 0 else 0
        
        print(f"Total files tested: {total_files}")
        print(f"Files with identifiable sections: {files_with_sections} ({files_with_sections/total_files*100:.1f}%)")
        print(f"Average sections per file: {avg_sections:.1f}")
        print(f"Files flagged as outliers: {flagged_outliers}")
        
        if files_with_sections < total_files * 0.5:
            print("\n[WARNING] Less than 50% of files have identifiable sections.")
            print("Consider improving section detection patterns for Kenyan reports.")
        
        return self.results


if __name__ == "__main__":
    tester = CurrentMethodTester()
    tester.run_all_tests()
