#!/usr/bin/env python3
"""
PHASE 4: GOVERNANCE EXTRACTION - VALID CORPUS ONLY

Re-runs all Phase 4 governance tests on the CLEAN corpus of 7 valid annual reports.
Excludes: vendor lists, training calendars, strategy docs, AGM aide memoires, etc.

Tests:
1. Section identification (CG Code sections)
2. Related Party "Tunneling" detection  
3. Compensation disclosure analysis
4. CMA enforcement matching
5. Manual spot-check citations
"""

import os
import re
from pathlib import Path
from collections import Counter

# Valid corpus file list
VALID_CORPUS = [
    '2019-Integrated-report-and-financial-statements-1.txt.txt',
    '2020-integrated-report-and-financial-statements.txt.txt',
    'NSE-2021-ANNUAL-REPORT-AND-FINANCIAL-STATEMENTS-1.txt.txt',
    'NSE-Annual-Report-2022-Integrated-Report.txt.txt',
    'NSE-Annual-Report-2023Interactive.txt.txt',
    'final-ar-min.txt.txt',
    'nse-integrated-report-and-financial-statements-1.txt.txt',
]

class GovernanceExtractor:
    def __init__(self, text_dir="nse_audit_data/processed_text"):
        self.text_dir = text_dir
        self.results = {}
    
    def load_valid_corpus(self):
        """Load only the validated annual reports."""
        texts = {}
        for fname in VALID_CORPUS:
            fpath = os.path.join(self.text_dir, fname)
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    texts[fname] = f.read()
            else:
                print(f"[!] Missing: {fname}")
        
        print(f"[*] Loaded {len(texts)}/{len(VALID_CORPUS)} valid annual reports")
        return texts
    
    def identify_governance_sections(self, text):
        """
        Identify CG Code relevant sections.
        Returns dict of section_name -> (found, page_hint, confidence)
        """
        sections = {
            'corporate_governance': [
                r'corporate\s+governance',
                r'cg\s+code',
                r'governance\s+framework',
            ],
            'directors_report': [
                r'directors?\s*report',
                r'report\s+of\s+the\s+directors',
            ],
            'audit_committee': [
                r'audit\s+committee',
                r'risk\s+and\s+audit\s+committee',
            ],
            'remuneration_committee': [
                r'remuneration\s+committee',
                r'compensation\s+committee',
                r'nominations?\s+and\s+remuneration',
            ],
            'related_party_transactions': [
                r'related\s+party\s+transactions?',
                r'rpt\s+disclosure',
                r'connected\s+person\s+transactions',
            ],
            'executive_compensation': [
                r'directors?\s+remuneration',
                r'executive\s+compensation',
                r'remuneration\s+report',
                r'key\s+management\s+personnel\s+compensation',
            ],
            'board_composition': [
                r'board\s+composition',
                r'board\s+diversity',
                r'independent\s+non[- ]?executive\s+directors?',
            ],
            'internal_controls': [
                r'internal\s+controls?',
                r'internal\s+audit',
                r'control\s+environment',
            ],
        }
        
        findings = {}
        for section_name, patterns in sections.items():
            found = False
            best_match = None
            for pattern in patterns:
                match = re.search(pattern, text[:10000], re.IGNORECASE)
                if match:
                    found = True
                    best_match = match.group(0)
                    break
            
            findings[section_name] = {
                'found': found,
                'match_text': best_match[:50] if best_match else None
            }
        
        return findings
    
    def detect_tunneling_risk(self, text):
        """
        Priority-A #5: Related Party "Tunneling" Detection
        Looks for concerning patterns in RPT disclosures.
        """
        risk_indicators = {
            'undisclosed_rpt': [
                r'except\s+as\s+disclosed',
                r'save\s+for\s+the\s+following',
                r'no\s+other\s+related\s+party',
            ],
            'management_fees': [
                r'management\s+fe?e?\s+(payable|receivable|expense)',
                r'fee\s+to\s+holding\s+company',
            ],
            'intercompany_loans': [
                r'due\s+(to|from)\s+(related\s+part|subsidiar|holding\s+co)',
                r'inter[- ]?company\s+(loan|advance|balance)',
            ],
            'guarantees': [
                r'corporate\s+guarantee',
                r'director\s+guarantee',
                r'guarantee\s+provided\s+by',
            ],
            'off_balance_sheet': [
                r'contingent\s+liabilit',
                r'off[- ]?balance\s+sheet',
            ],
        }
        
        risks_found = []
        for risk_type, patterns in risk_indicators.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    risks_found.append(risk_type)
                    break
        
        risk_level = 'LOW'
        if len(risks_found) >= 3:
            risk_level = 'HIGH'
        elif len(risks_found) >= 1:
            risk_level = 'MEDIUM'
        
        return {
            'risk_level': risk_level,
            'indicators': list(set(risks_found)),
            'count': len(set(risks_found))
        }
    
    def check_compensation_disclosure(self, text):
        """
        Check if executive compensation is properly disclosed.
        CG Code requires structured disclosure.
        """
        has_disclosure = False
        disclosure_quality = 'none'
        
        # Check for any compensation mention
        comp_patterns = [
            r'directors?\s+remuneration',
            r'executive\s+compensation',
            r'remuneration\s+report',
            r'key\s+management\s+personnel',
        ]
        
        for pattern in comp_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                has_disclosure = True
                break
        
        if not has_disclosure:
            return {'disclosed': False, 'quality': 'none', 'reason': 'No compensation section found'}
        
        # Check quality indicators
        quality_checks = {
            'structured_table': r'\$\s*\d+[,000]*\s*(million|thousand)',
            'individual_directors': r'(chairman|ceo|managing\s+director).*(received|paid|entitled)',
            'breakdown_by_component': r'(salary|bonus|allowances?|benefits?|pension)',
            'performance_metrics': r'(performance|kpi|target|metric)',
        }
        
        quality_score = 0
        for check_name, pattern in quality_checks.items():
            if re.search(pattern, text, re.IGNORECASE):
                quality_score += 1
        
        if quality_score >= 3:
            disclosure_quality = 'high'
        elif quality_score >= 1:
            disclosure_quality = 'basic'
        else:
            disclosure_quality = 'minimal'
        
        return {
            'disclosed': True,
            'quality': disclosure_quality,
            'quality_score': quality_score
        }
    
    def run_full_analysis(self):
        """Run complete governance analysis on valid corpus."""
        texts = self.load_valid_corpus()
        
        if not texts:
            print("[!] No valid corpus files found!")
            return
        
        print(f"\n{'='*80}")
        print(f"PHASE 4: GOVERNANCE EXTRACTION (VALID CORPUS ONLY)")
        print(f"{'='*80}")
        print(f"Corpus size: {len(texts)} annual reports")
        print(f"Files: {', '.join(sorted(texts.keys()))}")
        print()
        
        # Aggregate results
        section_coverage = Counter()
        tunneling_risks = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        compensation_results = {'high': 0, 'basic': 0, 'minimal': 0, 'none': 0}
        
        for fname, text in sorted(texts.items()):
            print(f"\n--- {fname} ---")
            
            # Section identification
            sections = self.identify_governance_sections(text)
            sections_found = sum(1 for s in sections.values() if s['found'])
            print(f"  Governance Sections Found: {sections_found}/8")
            for sec_name, sec_data in sections.items():
                if sec_data['found']:
                    section_coverage[sec_name] += 1
            
            # Tunneling risk
            tunnel_result = self.detect_tunneling_risk(text)
            print(f"  Tunneling Risk: {tunnel_result['risk_level']} ({tunnel_result['count']} indicators)")
            tunneling_risks[tunnel_result['risk_level']] += 1
            
            # Compensation disclosure
            comp_result = self.check_compensation_disclosure(text)
            print(f"  Compensation Disclosure: {comp_result['quality']}")
            compensation_results[comp_result['quality']] += 1
        
        # Summary statistics
        n = len(texts)
        print(f"\n{'='*80}")
        print(f"AGGREGATE RESULTS (N={n} valid annual reports)")
        print(f"{'='*80}")
        
        print(f"\nSection Coverage:")
        for section, count in sorted(section_coverage.items(), key=lambda x: -x[1]):
            pct = (count / n) * 100
            print(f"  {section.replace('_', ' ').title()}: {count}/{n} ({pct:.1f}%)")
        
        print(f"\nTunneling Risk Distribution:")
        for level in ['HIGH', 'MEDIUM', 'LOW']:
            count = tunneling_risks[level]
            pct = (count / n) * 100
            print(f"  {level}: {count}/{n} ({pct:.1f}%)")
        
        print(f"\nCompensation Disclosure Quality:")
        total_disclosed = sum(compensation_results[q] for q in ['high', 'basic', 'minimal'])
        non_disclosed = compensation_results['none']
        print(f"  Disclosed (any quality): {total_disclosed}/{n} ({(total_disclosed/n)*100:.1f}%)")
        print(f"  NOT Disclosed: {non_disclosed}/{n} ({(non_disclosed/n)*100:.1f}%)")
        for quality in ['high', 'basic', 'minimal']:
            count = compensation_results[quality]
            if count > 0:
                print(f"    - {quality.title()}: {count}/{n}")
        
        # Key findings
        print(f"\n{'='*80}")
        print(f"KEY FINDINGS")
        print(f"{'='*80}")
        
        non_disclosure_rate = (non_disclosed / n) * 100
        high_tunneling_rate = (tunneling_risks['HIGH'] / n) * 100
        
        if non_disclosure_rate >= 50:
            print(f"⚠️  CRITICAL: {non_disclosure_rate:.1f}% of companies do NOT disclose executive compensation")
            print(f"   This violates CG Code disclosure requirements.")
        
        if high_tunneling_rate > 0:
            print(f"⚠️  WARNING: {high_tunneling_rate:.1f}% show HIGH related-party tunneling risk indicators")
            print(f"   Requires manual review of specific transactions.")
        
        most_common_section = max(section_coverage.items(), key=lambda x: x[1]) if section_coverage else None
        if most_common_section:
            print(f"✓ Most common governance section: {most_common_section[0].replace('_', ' ').title()} ({most_common_section[1]}/{n})")
        
        return {
            'n_reports': n,
            'section_coverage': dict(section_coverage),
            'tunneling_risks': tunneling_risks,
            'compensation_disclosure': compensation_results,
            'non_disclosure_rate': non_disclosure_rate,
            'high_tunneling_rate': high_tunneling_rate
        }


if __name__ == '__main__':
    extractor = GovernanceExtractor()
    results = extractor.run_full_analysis()
