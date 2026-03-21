#!/usr/bin/env python3
"""
PHASE 4: TEST WITH NEW METHODS
- Governance Extraction (Sections 41, 45, 48 of Companies Act)
- Related Party "Tunneling" Analysis (Priority-A #5)
- CMA Enforcement Matching Layer
- Advanced Director Compensation Tracking
- Audit Committee Independence Scoring
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

# Configuration
PROCESSED_DIR = Path("nse_audit_data/processed_text")
OUTPUT_DIR = Path("nse_audit_data/governance_analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class GovernanceAnalyzer:
    """New methods for governance extraction and analysis"""
    
    def __init__(self):
        self.results = []
        
        # Companies Act 2015 (Kenya) specific sections
        self.governance_sections = {
            'section_41': r'(directors\s*(report|responsibilities?)|board\s*of\s*directors)',
            'section_45': r'(audit\s*committee|independent\s*auditor)',
            'section_48': r'(related\s*party\s*transactions|rpt|rps)',
            'corporate_governance': r'(corporate\s*governance|governance\s*framework)',
            'risk_management': r'(risk\s*management|risk\s*committee)',
            'remuneration': r'(remuneration\s*policy|directors?\s*remuneration|executive\s*compensation)'
        }
        
        # Related Party Tunneling Indicators (Priority-A #5)
        self.tunneling_patterns = [
            r'related\s*party\s*transaction',
            r'inter[- ]?company\s*loan',
            r'advance\s*to\s*director',
            r'loan\s*to\s*key\s*management',
            r'transaction\s*with\s*associate',
            r'balance\s*with\s*holding\s*company',
            r'guarantee\s*provided\s*to',
            r'collateral\s*for\s*related\s*party',
            r'non[- ]?arm\'s?\s*length',
            r'conflict\s*of\s*interest'
        ]
        
        # CMA Enforcement Keywords
        self.cma_enforcement = [
            r'CMA\s*enforcement',
            r'regulatory\s*penalty',
            r'compliance\s*breach',
            r'sanction',
            r'directive\s*from\s*CMA',
            r'market\s*conduct\s*authority',
            r'listing\s*rule\s*violation'
        ]
        
    def analyze_file(self, filepath):
        """Run all new method tests on a single file"""
        filename = filepath.name
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
            
        results = {
            'filename': filename,
            'governance_sections': {},
            'tunneling_risk': {
                'indicators_found': [],
                'risk_score': 0,
                'severity': 'LOW'
            },
            'cma_enforcement': {
                'mentions': [],
                'has_enforcement_issues': False
            },
            'audit_committee': {
                'mentioned': False,
                'independence_keywords': 0,
                'score': 0
            },
            'director_compensation': {
                'mentioned': False,
                'total_mentions': 0
            }
        }
        
        # 1. Governance Section Extraction (Sections 41, 45, 48)
        for section_name, pattern in self.governance_sections.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                results['governance_sections'][section_name] = len(matches)
        
        # 2. Related Party Tunneling Analysis (Priority-A #5)
        tunneling_count = 0
        for pattern in self.tunneling_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                results['tunneling_risk']['indicators_found'].append({
                    'pattern': pattern,
                    'count': len(matches)
                })
                tunneling_count += len(matches)
        
        results['tunneling_risk']['risk_score'] = min(tunneling_count, 10)
        if tunneling_count > 5:
            results['tunneling_risk']['severity'] = 'HIGH'
        elif tunneling_count > 2:
            results['tunneling_risk']['severity'] = 'MEDIUM'
            
        # 3. CMA Enforcement Matching
        cma_matches = []
        for pattern in self.cma_enforcement:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                cma_matches.extend(matches)
        
        results['cma_enforcement']['mentions'] = cma_matches
        results['cma_enforcement']['has_enforcement_issues'] = len(cma_matches) > 0
        
        # 4. Audit Committee Independence Scoring
        audit_match = re.search(r'audit\s*committee', content, re.IGNORECASE)
        if audit_match:
            results['audit_committee']['mentioned'] = True
            independence_keywords = ['independent', 'non-executive', 'chairman', 'majority']
            for keyword in independence_keywords:
                if keyword in content:
                    results['audit_committee']['independence_keywords'] += 1
            results['audit_committee']['score'] = min(
                results['audit_committee']['independence_keywords'] / len(independence_keywords), 
                1.0
            )
        
        # 5. Director Compensation Tracking
        comp_patterns = [r'directors?\s*remuneration', r'executive\s*compensation', r'board\s*fees']
        for pattern in comp_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                results['director_compensation']['mentioned'] = True
                results['director_compensation']['total_mentions'] += len(matches)
        
        return results
    
    def run_batch_analysis(self):
        """Analyze all files in processed_text directory"""
        print("=" * 70)
        print("PHASE 4: TESTING WITH NEW METHODS")
        print("=" * 70)
        print()
        
        text_files = list(PROCESSED_DIR.glob("*.txt"))
        
        if not text_files:
            print(f"[ERROR] No text files found in {PROCESSED_DIR}")
            return
        
        print(f"[*] Analyzing {len(text_files)} files with NEW methods...")
        print()
        
        all_results = []
        high_risk_files = []
        governance_coverage = defaultdict(int)
        
        for filepath in text_files:
            print("=" * 70)
            print(f"Testing: {filepath.name}")
            print("=" * 70)
            
            results = self.analyze_file(filepath)
            all_results.append(results)
            
            # Print Governance Sections (41, 45, 48)
            print("\n[NEW] Governance Section Extraction:")
            if results['governance_sections']:
                for section, count in results['governance_sections'].items():
                    status = "✓" if count > 0 else "✗"
                    print(f"  {status} {section.replace('_', ' ').title()}: {count} match(es)")
                
                # Track coverage
                for section in results['governance_sections']:
                    governance_coverage[section] += 1
            else:
                print("  ✗ No governance sections identified")
            
            # Print Related Party Tunneling Risk
            print(f"\n[NEW] Related Party Tunneling Analysis (Priority-A #5):")
            risk = results['tunneling_risk']
            print(f"  Risk Score: {risk['risk_score']}/10")
            print(f"  Severity: {risk['severity']}")
            if risk['indicators_found']:
                print(f"  Indicators Found:")
                for indicator in risk['indicators_found'][:3]:  # Show top 3
                    print(f"    - {indicator['pattern']}: {indicator['count']}x")
                if len(risk['indicators_found']) > 3:
                    print(f"    ... and {len(risk['indicators_found']) - 3} more")
            
            if risk['severity'] == 'HIGH':
                high_risk_files.append(filepath.name)
            
            # Print CMA Enforcement
            print(f"\n[NEW] CMA Enforcement Matching:")
            if results['cma_enforcement']['has_enforcement_issues']:
                print(f"  ⚠ ENFORCEMENT ISSUES DETECTED")
                print(f"  Mentions: {results['cma_enforcement']['mentions'][:3]}")
            else:
                print(f"  ✓ No enforcement issues detected")
            
            # Print Audit Committee Score
            print(f"\n[NEW] Audit Committee Independence:")
            if results['audit_committee']['mentioned']:
                print(f"  Mentioned: Yes")
                print(f"  Independence Keywords: {results['audit_committee']['independence_keywords']}")
                print(f"  Independence Score: {results['audit_committee']['score']:.2f}/1.00")
            else:
                print(f"  Not mentioned")
            
            # Print Director Compensation
            print(f"\n[NEW] Director Compensation Tracking:")
            if results['director_compensation']['mentioned']:
                print(f"  Mentioned: Yes ({results['director_compensation']['total_mentions']} references)")
            else:
                print(f"  Not explicitly mentioned")
            
            print()
        
        # Summary Statistics
        print("=" * 70)
        print("NEW METHODS SUMMARY")
        print("=" * 70)
        print(f"Total files analyzed: {len(all_results)}")
        print(f"Files with governance sections: {sum(1 for r in all_results if r['governance_sections'])}")
        print(f"High tunneling risk files: {len(high_risk_files)}")
        if high_risk_files:
            for f in high_risk_files:
                print(f"  ⚠ {f}")
        print(f"Files with CMA enforcement issues: {sum(1 for r in all_results if r['cma_enforcement']['has_enforcement_issues'])}")
        print(f"Average audit committee score: {sum(r['audit_committee']['score'] for r in all_results) / len(all_results):.2f}")
        print()
        print("Governance Section Coverage:")
        for section, count in sorted(governance_coverage.items(), key=lambda x: x[1], reverse=True):
            print(f"  {section.replace('_', ' ').title()}: {count}/{len(text_files)} files ({count/len(text_files)*100:.1f}%)")
        
        # Save results to JSON
        output_file = OUTPUT_DIR / "governance_analysis_results.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\n[✓] Detailed results saved to: {output_file}")
        
        return all_results


if __name__ == "__main__":
    analyzer = GovernanceAnalyzer()
    analyzer.run_batch_analysis()
