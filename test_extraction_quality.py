#!/usr/bin/env python3
"""
Phase 2 & 3: EXTRACT Quality Validation + CURRENT Methods Testing
Tests for:
- Priority-A #1: PDF Dark Matter (scanned vs text-encoded)
- Artifact #9: Column-Flow Hallucinations  
- Priority-A #6: British/Kenyan locale handling
- Priority-A #2: Safaricom outlier check
"""

import os
import re
from collections import Counter

class KenyaExtractionTester:
    def __init__(self, text_dir="nse_audit_data/processed_text"):
        self.text_dir = text_dir
        self.test_results = {}
        
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
    
    def test_ocr_detection(self, text):
        """
        Priority-A #1: Detect 'PDF Dark Matter' - scanned PDFs with poor OCR
        Heuristics:
        - High ratio of single characters to words
        - Unusual character patterns (random capitalization)
        - Missing common words
        """
        if len(text.strip()) == 0:
            return {"is_scanned": True, "confidence": 1.0, "reason": "Empty text"}
        
        words = text.split()
        if len(words) == 0:
            return {"is_scanned": True, "confidence": 0.95, "reason": "No words found"}
        
        # Check for single-character ratio (OCR often breaks words)
        single_char_count = sum(1 for w in words if len(w) == 1)
        single_char_ratio = single_char_count / len(words)
        
        # Check for unusual uppercase patterns (OCR artifact)
        uppercase_words = [w for w in words if w.isupper() and len(w) > 3]
        uppercase_ratio = len(uppercase_words) / len(words)
        
        # Check for common English words (should be present in good extraction)
        common_words = ['the', 'and', 'of', 'to', 'a', 'in', 'is', 'for', 'on', 'with']
        text_lower = text.lower()
        found_common = sum(1 for w in common_words if w in text_lower)
        common_word_ratio = found_common / len(common_words)
        
        # Scoring
        ocr_score = 0
        reasons = []
        
        if single_char_ratio > 0.15:  # More than 15% single chars
            ocr_score += 0.4
            reasons.append(f"High single-char ratio: {single_char_ratio:.2f}")
        
        if uppercase_ratio > 0.3:  # More than 30% all-caps words
            ocr_score += 0.3
            reasons.append(f"High uppercase ratio: {uppercase_ratio:.2f}")
        
        if common_word_ratio < 0.5:  # Less than 50% common words found
            ocr_score += 0.3
            reasons.append(f"Low common-word ratio: {common_word_ratio:.2f}")
        
        is_scanned = ocr_score > 0.5
        
        return {
            "is_scanned": is_scanned,
            "confidence": ocr_score,
            "reasons": reasons if reasons else ["Good text quality"],
            "metrics": {
                "single_char_ratio": single_char_ratio,
                "uppercase_ratio": uppercase_ratio,
                "common_word_ratio": common_word_ratio
            }
        }
    
    def test_column_layout_artifacts(self, text):
        """
        Artifact #9: Column-Flow Hallucinations
        Detect when multi-column PDF text gets jumbled (reading across columns instead of down)
        Heuristics:
        - Lines with very irregular lengths
        - Sentences that don't make grammatical sense
        - Repeated short phrases on same line
        """
        lines = text.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        if len(non_empty_lines) < 5:
            return {"has_column_issues": False, "confidence": 0, "reason": "Too few lines"}
        
        # Check line length variance (columns often create alternating short/long lines)
        line_lengths = [len(l) for l in non_empty_lines[:50]]  # Sample first 50
        avg_length = sum(line_lengths) / len(line_lengths)
        
        # Count lines that deviate significantly from average
        irregular_count = sum(1 for l in line_lengths if abs(l - avg_length) > avg_length * 0.7)
        irregular_ratio = irregular_count / len(line_lengths)
        
        # Check for mid-sentence breaks (column artifact)
        # Lines ending without punctuation but next line starts lowercase
        mid_sentence_breaks = 0
        for i in range(len(non_empty_lines) - 1):
            curr = non_empty_lines[i].strip()
            next_line = non_empty_lines[i+1].strip()
            
            if len(curr) > 10 and len(next_line) > 10:
                # Current line doesn't end with sentence-ending punctuation
                if not curr[-1] in '.!?;:':
                    # Next line starts with lowercase (continuation)
                    if next_line[0].islower():
                        mid_sentence_breaks += 1
        
        break_ratio = mid_sentence_breaks / len(non_empty_lines)
        
        has_issues = irregular_ratio > 0.4 or break_ratio > 0.3
        
        return {
            "has_column_issues": has_issues,
            "confidence": max(irregular_ratio, break_ratio),
            "metrics": {
                "irregular_line_ratio": irregular_ratio,
                "mid_sentence_break_ratio": break_ratio,
                "avg_line_length": avg_length
            }
        }
    
    def test_british_kenyan_locale(self, text):
        """
        Priority-A #6: British/Kenyan locale handling
        Check for proper recognition of:
        - British spelling (-ise vs -ize)
        - Kenyan terms/shorthand
        - Local currency formatting (KES, Ksh)
        """
        british_spellings = [
            'organised', 'recognised', 'authorised', 'analysed',
            'programme', 'centre', 'colour', 'favour', 'licence'  # noun
        ]
        
        kenyan_terms = [
            'Kenya', 'Nairobi', 'NSE', 'CMA', 'KES', 'Ksh', 'Shilling',
            'Safaricom', 'Equity', 'KCB', 'NCBA', 'Co-operative'
        ]
        
        text_lower = text.lower()
        
        british_found = [term for term in british_spellings if term in text_lower]
        kenyan_found = [term for term in kenyan_terms if term.lower() in text_lower or term in text]
        
        # Check for currency formatting
        kes_pattern = r'(KES|Ksh\.?|KSh|Sh\.)\s*[\d,]+'
        kes_matches = re.findall(kes_pattern, text, re.IGNORECASE)
        
        return {
            "british_spellings_found": british_found,
            "kenyan_terms_found": list(set(kenyan_found)),
            "currency_formatting_detected": len(kes_matches) > 0,
            "kes_matches_count": len(kes_matches),
            "locale_quality": "good" if len(british_found) > 0 or len(kenyan_found) > 2 else "needs_review"
        }
    
    def run_all_tests(self):
        """Run complete test suite on all available texts."""
        texts = self.load_all_texts()
        
        if not texts:
            print("[!] No texts to test. Run scraper first.")
            return
        
        print("\n" + "="*70)
        print("PHASE 2: EXTRACTION QUALITY VALIDATION")
        print("="*70)
        
        for fname, text in texts.items():
            print(f"\n--- Testing: {fname} ---")
            
            # Test 1: OCR Detection
            ocr_result = self.test_ocr_detection(text)
            print(f"\n[Priority-A #1] PDF Dark Matter Check:")
            print(f"  Is Scanned/Poor OCR: {ocr_result['is_scanned']}")
            print(f"  Confidence: {ocr_result['confidence']:.2f}")
            for reason in ocr_result.get('reasons', []):
                print(f"    • {reason}")
            
            # Test 2: Column Layout Artifacts
            column_result = self.test_column_layout_artifacts(text)
            print(f"\n[Artifact #9] Column-Flow Hallucinations Check:")
            print(f"  Has Column Issues: {column_result['has_column_issues']}")
            print(f"  Confidence: {column_result['confidence']:.2f}")
            if 'metrics' in column_result:
                print(f"    Avg line length: {column_result['metrics'].get('avg_line_length', 0):.1f}")
            
            # Test 3: British/Kenyan Locale
            locale_result = self.test_british_kenyan_locale(text)
            print(f"\n[Priority-A #6] British/Kenyan Locale Check:")
            print(f"  Locale Quality: {locale_result['locale_quality']}")
            if locale_result['british_spellings_found']:
                print(f"    British spellings: {', '.join(locale_result['british_spellings_found'][:5])}")
            if locale_result['kenyan_terms_found']:
                print(f"    Kenyan terms: {', '.join(locale_result['kenyan_terms_found'][:5])}")
            if locale_result['currency_formatting_detected']:
                print(f"    Currency formatting: Detected ({locale_result['kes_matches_count']} matches)")
            
            # Store results
            self.test_results[fname] = {
                'ocr': ocr_result,
                'column': column_result,
                'locale': locale_result
            }
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        
        total_files = len(texts)
        scanned_count = sum(1 for r in self.test_results.values() if r['ocr']['is_scanned'])
        column_issue_count = sum(1 for r in self.test_results.values() if r['column']['has_column_issues'])
        
        print(f"Total files tested: {total_files}")
        print(f"Files with OCR issues: {scanned_count} ({scanned_count/total_files*100:.1f}%)")
        print(f"Files with column layout issues: {column_issue_count} ({column_issue_count/total_files*100:.1f}%)")
        
        if scanned_count > 0:
            print("\n[WARNING] Some PDFs may be scanned images. Consider OCR preprocessing.")
        
        if column_issue_count > 0:
            print("[WARNING] Column layout artifacts detected. May need layout-aware extraction.")
        
        return self.test_results


if __name__ == "__main__":
    tester = KenyaExtractionTester()
    tester.run_all_tests()
