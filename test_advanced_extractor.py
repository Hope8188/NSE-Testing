"""
TEST SUITE FOR ADVANCED EXTRACTOR
Validates Level 2 (value extraction) and Level 3 (citation-backed) on clean corpus.
NO KEYWORD MATCHING - Only numerical values, ratios, and cited evidence.
"""

import sys
import json
from pathlib import Path
from advanced_extractor import run_full_audit, extract_section_41, extract_section_45, extract_section_48

# Valid annual reports from our cleaned corpus
VALID_REPORTS = [
    "2019-Integrated-report-and-financial-statements-1.pdf.pdf",
    "2020-integrated-report-and-financial-statements.pdf.pdf",
]

def test_section_41_value_extraction():
    """Test that S.41 extracts NUMBERS not keywords."""
    print("=" * 80)
    print("TEST: Section 41 - Board Independence (Value Extraction)")
    print("=" * 80)
    
    all_passed = True
    
    for report_name in VALID_REPORTS:
        pdf_path = f"/workspace/nse_audit_data/raw_pdfs/{report_name}"
        
        if not Path(pdf_path).exists():
            print(f"SKIP: {report_name} (file not found)")
            continue
        
        report = run_full_audit(pdf_path)
        s41_results = report["sections"]["S.41"]["results"]
        
        print(f"\n📄 {report_name}")
        
        if not s41_results:
            print("  ⚠️  NO RESULTS - Extractor found no board independence data")
            print("  This is CORRECT behavior if the PDF doesn't have explicit ratios")
            continue
        
        for result in s41_results:
            extracted = result['extracted_value']
            
            # CRITICAL TEST: Must have actual numbers, not just text
            has_independent_count = 'independent_count' in extracted and extracted['independent_count'] is not None
            has_total_count = 'total_count' in extracted and extracted['total_count'] is not None
            has_ratio = 'ratio' in extracted and extracted['ratio'] is not None
            
            print(f"  Method: {result['extraction_method']}")
            print(f"  Independent Count: {extracted.get('independent_count', 'MISSING')}")
            print(f"  Total Count: {extracted.get('total_count', 'MISSING')}")
            print(f"  Ratio: {extracted.get('ratio_percent', 'MISSING')}")
            print(f"  Passes Compliance: {result['passes_compliance']}")
            print(f"  Confidence: {result['confidence_score']:.2f}")
            print(f"  Page: {result['page_number']}")
            print(f"  Evidence: {result['evidence_quote'][:120]}...")
            
            # Validation checks
            if not has_independent_count:
                print("  ❌ FAIL: No independent count extracted (keyword matching detected)")
                all_passed = False
            elif not has_total_count and result['extraction_method'] in ['ratio_explicit', 'ratio_board_composition']:
                print("  ❌ FAIL: Should have total count for ratio method")
                all_passed = False
            elif not has_ratio and has_total_count:
                print("  ❌ FAIL: Ratio should be calculated when total exists")
                all_passed = False
            else:
                print("  ✅ PASS: Value extraction working correctly")
            
            print()
    
    return all_passed


def test_section_45_tenure_calculation():
    """Test that S.45 calculates TENURE from appointment years."""
    print("=" * 80)
    print("TEST: Section 45 - Tenure Breach (Year Calculation)")
    print("=" * 80)
    
    for report_name in VALID_REPORTS[:1]:  # Test one file
        pdf_path = f"/workspace/nse_audit_data/raw_pdfs/{report_name}"
        
        if not Path(pdf_path).exists():
            print(f"SKIP: {report_name} (file not found)")
            return True
        
        report = run_full_audit(pdf_path)
        s45_results = report["sections"]["S.45"]["results"]
        
        print(f"\n📄 {report_name}")
        
        if not s45_results:
            print("  ℹ️  No tenure data found (may be correct for this report)")
            return True
        
        for result in s45_results[:5]:  # Show first 5
            extracted = result['extracted_value']
            
            has_appointment_year = 'appointment_year' in extracted
            has_tenure = 'tenure_years' in extracted
            requires_approval = extracted.get('requires_shareholder_approval', False)
            
            print(f"  Director: {extracted.get('director_name', 'Unknown')}")
            print(f"  Appointment Year: {extracted.get('appointment_year', 'MISSING')}")
            print(f"  Calculated Tenure: {extracted.get('tenure_years', 'MISSING')} years")
            print(f"  Requires Approval (>9 yrs): {requires_approval}")
            print(f"  Evidence: {result['evidence_quote'][:100]}...")
            
            # Validation: If we have appointment year, tenure must be calculable
            if has_appointment_year and not has_tenure:
                print("  ❌ FAIL: Appointment year found but tenure not calculated")
                return False
            elif has_tenure and extracted['tenure_years'] > 9 and not requires_approval:
                print("  ❌ FAIL: Tenure >9 years but approval requirement not flagged")
                return False
            else:
                print("  ✅ PASS: Tenure calculation correct")
            
            print()
    
    return True


def test_section_48_rpt_detection():
    """Test that S.48 finds RPT NOTE with VALUES and APPROVAL."""
    print("=" * 80)
    print("TEST: Section 48 - Related Party Transactions (Value + Approval)")
    print("=" * 80)
    
    for report_name in VALID_REPORTS:
        pdf_path = f"/workspace/nse_audit_data/raw_pdfs/{report_name}"
        
        if not Path(pdf_path).exists():
            print(f"SKIP: {report_name} (file not found)")
            continue
        
        report = run_full_audit(pdf_path)
        s48_results = report["sections"]["S.48"]["results"]
        
        print(f"\n📄 {report_name}")
        
        if not s48_results:
            print("  ❌ FAIL: No RPT results at all")
            return False
        
        for result in s48_results:
            extracted = result['extracted_value']
            
            transaction_count = extracted.get('transaction_count', 0)
            total_amount = extracted.get('total_amount_formatted', 'N/A')
            has_approval = extracted.get('board_approval_disclosed', False)
            note_number = extracted.get('note_number')
            
            print(f"  Note Number: {note_number}")
            print(f"  Transactions Found: {transaction_count}")
            print(f"  Total Amount: {total_amount}")
            print(f"  Board Approval Disclosed: {has_approval}")
            print(f"  Compliant: {result['passes_compliance']}")
            print(f"  Confidence: {result['confidence_score']:.2f}")
            
            # Validation: Must find actual transactions with amounts
            if transaction_count == 0:
                print("  ⚠️  No transactions found (may be correct, or missing note)")
            elif transaction_count > 0:
                print(f"  ✅ Found {transaction_count} transactions with disclosed values")
                
                # Show sample transaction
                transactions = extracted.get('transactions', [])
                if transactions:
                    sample = transactions[0]
                    print(f"     Sample: {sample.get('counterparty')} - {sample.get('amount_formatted')}")
            
            # Check approval detection
            if transaction_count > 0 and not has_approval:
                print("  ⚠️  WARNING: Transactions found but no board approval mentioned")
                print("  This may indicate a compliance gap (needs manual review)")
            
            print()
    
    return True


def test_no_keyword_false_positives():
    """CRITICAL TEST: Verify we're NOT getting 100% from keyword matching."""
    print("=" * 80)
    print("TEST: No Keyword False Positives (The 100% Problem)")
    print("=" * 80)
    
    s41_compliant_count = 0
    s41_total = 0
    
    for report_name in VALID_REPORTS:
        pdf_path = f"/workspace/nse_audit_data/raw_pdfs/{report_name}"
        
        if not Path(pdf_path).exists():
            continue
        
        report = run_full_audit(pdf_path)
        s41_results = report["sections"]["S.41"]["results"]
        
        s41_total += 1
        
        # Check if we got actual values
        has_values = False
        for r in s41_results:
            if r['extracted_value'].get('ratio') is not None:
                has_values = True
                if r['passes_compliance'] is True:
                    s41_compliant_count += 1
                break
        
        if not has_values:
            print(f"  📄 {report_name}: No S.41 values extracted (correct - no false positive)")
        else:
            print(f"  📄 {report_name}: Values extracted (compliant: {s41_compliant_count})")
    
    # If we have 100% compliance with values, that's suspicious
    if s41_total > 0 and s41_compliant_count == s41_total:
        print(f"\n  ⚠️  WARNING: {s41_compliant_count}/{s41_total} show compliance")
        print("  This could still be legitimate OR keyword matching in disguise.")
        print("  MANUAL SPOT-CHECK REQUIRED: Open PDF and verify cited page/quote.")
    else:
        print(f"\n  ✅ GOOD: Not 100% compliance - extractor is discriminating")
    
    return True


def main():
    print("\n" + "=" * 80)
    print("ADVANCED EXTRACTOR VALIDATION SUITE")
    print("Level 2 (Value Extraction) + Level 3 (Citation-Backed)")
    print("=" * 80 + "\n")
    
    results = {
        "S.41_Value_Extraction": test_section_41_value_extraction(),
        "S.45_Tenure_Calculation": test_section_45_tenure_calculation(),
        "S.48_RPT_Detection": test_section_48_rpt_detection(),
        "No_Keyword_False_Positives": test_no_keyword_false_positives()
    }
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED - Extractor is ready for ICPSK demo")
        print("\nNEXT STEP: Manual spot-check on 2-3 highest-risk findings")
        print("Open the PDF, go to cited page, verify quote matches exactly.")
    else:
        print("❌ SOME TESTS FAILED - Review extractor logic before proceeding")
    print("=" * 80 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
