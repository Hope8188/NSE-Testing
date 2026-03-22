"""
ADVANCED GOVERNANCE EXTRACTOR - LEVEL 2 & 3
Extracts VALUES, not keywords. Citation-backed assertions.
HFT-level accuracy: No hallucinations, page-tracked, ratio-calculated.
"""

import re
import sys
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict
from pathlib import Path
import fitz  # PyMuPDF
from dateutil import parser as date_parser
from datetime import datetime

@dataclass
class ExtractionResult:
    """Level 3: Citation-backed assertion"""
    section: str
    cg_code_requirement: str
    extracted_value: any
    passes_compliance: Optional[bool]
    evidence_quote: str
    page_number: int
    confidence_score: float  # 0.0-1.0
    extraction_method: str

# ============================================================================
# SECTION 41: BOARD INDEPENDENCE (One-third minimum)
# ============================================================================

def extract_section_41(text: str, pdf_path: str) -> List[ExtractionResult]:
    """
    CG Code S.41: At least one-third of board members must be independent.
    Level 2: Extract actual counts and ratios.
    Level 3: Cite exact page and quote.
    """
    results = []
    
    # Pattern 1: "X of Y directors are independent"
    pattern1 = r"(\d+)\s+of\s+(\d+)\s+(?:directors|board\s+members?|members\s+of\s+the\s+board)\s+(?:are|is)\s+independent"
    
    # Pattern 2: "The board comprises X independent non-executive directors out of Y total"
    pattern2 = r"(?:board\s+comprises|board\s+consists\s+of|there\s+are)\s+(\d+)\s+independent\s+(?:non[-\s]?executive\s+)?directors?\s+(?:out\s+of|from|among)\s+(\d+)"
    
    # Pattern 3: "X independent directors and Y executive directors" (calculate total)
    pattern3 = r"(\d+)\s+independent\s+(?:non[-\s]?executive\s+)?directors?(?:\s*,?\s+(?:and|&)\s+(\d+)\s+(?:executive|other))?"
    
    # Pattern 4: Table-like structure "Independent Non-Executive Directors: X"
    pattern4 = r"independent\s+(?:non[-\s]?executive\s+)?directors?(?:\s*:|\s+-)\s*(\d+)"
    
    # Pattern 5: "The Board has X members, of whom Y are independent"
    pattern5 = r"(?:board\s+has|composition\s+of\s+the\s+board)\s+(\d+)\s+members?,?\s+(?:of\s+whom|with)\s+(\d+)\s+(?:being\s+)?independent"
    
    # Pattern 6: "X independent and Y non-independent directors"
    pattern6 = r"(\d+)\s+independent\s+(?:and|&)\s+(\d+)\s+(?:non[-\s]?independent|executive|other)"
    
    # Pattern 7: Written numbers like "Five (5) Independent" or "five independent"
    pattern7 = r"(?:^|\n)\s*(?:[Ff]ive|[Ss]ix|[Ss]even|[Ee]ight|[Nn]ine|[Tt]en|[Ee]leven|[Tt]welve)\s+\((\d+)\)\s+independent"
    
    # Pattern 8: "constituted as follows: a) X (Y) Independent"
    pattern8 = r"(?:constituted|composed)\s+(?:as\s+follows|below)[:\s]+.*?(\d+)\s*\)?\s*independent\s+(?:and\s+)?(?:non[-\s]?executive\s+)?director"
    
    patterns = [
        (pattern1, "ratio_explicit", 0.95),
        (pattern2, "ratio_board_composition", 0.90),
        (pattern5, "ratio_board_has", 0.92),
        (pattern6, "ratio_independent_vs_other", 0.88),
        (pattern8, "constituted_as_follows", 0.93),
        (pattern7, "written_number_parenthetical", 0.87),
        (pattern3, "count_with_calculation", 0.85),
        (pattern4, "count_only", 0.70)
    ]
    
    for pattern, method, base_confidence in patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
        
        for match in matches:
            try:
                if method in ["ratio_explicit", "ratio_board_composition"]:
                    independent = int(match.group(1))
                    total = int(match.group(2))
                    ratio = independent / total if total > 0 else 0
                    passes = ratio >= 0.333
                    
                    result = ExtractionResult(
                        section="S.41",
                        cg_code_requirement="At least one-third (33.3%) of board must be independent",
                        extracted_value={
                            "independent_count": independent,
                            "total_count": total,
                            "ratio": round(ratio, 3),
                            "ratio_percent": f"{ratio*100:.1f}%"
                        },
                        passes_compliance=passes,
                        evidence_quote=match.group(0).strip(),
                        page_number=find_page_for_text(pdf_path, match.group(0)),
                        confidence_score=base_confidence,
                        extraction_method=method
                    )
                    results.append(result)
                    
                elif method == "count_with_calculation":
                    independent = int(match.group(1))
                    executives = int(match.group(2)) if match.group(2) else None
                    
                    # Only create result if we can calculate or have high confidence
                    if executives is not None:
                        total = independent + executives
                        ratio = independent / total if total > 0 else 0
                        passes = ratio >= 0.333
                        
                        result = ExtractionResult(
                            section="S.41",
                            cg_code_requirement="At least one-third (33.3%) of board must be independent",
                            extracted_value={
                                "independent_count": independent,
                                "executive_count": executives,
                                "total_count": total,
                                "ratio": round(ratio, 3),
                                "ratio_percent": f"{ratio*100:.1f}%"
                            },
                            passes_compliance=passes,
                            evidence_quote=match.group(0).strip(),
                            page_number=find_page_for_text(pdf_path, match.group(0)),
                            confidence_score=base_confidence,
                            extraction_method=method
                        )
                        results.append(result)
                        
                elif method in ["ratio_board_has", "ratio_independent_vs_other"]:
                    # Handle patterns 5 and 6
                    if method == "ratio_board_has":
                        total = int(match.group(1))
                        independent = int(match.group(2))
                    else:  # ratio_independent_vs_other
                        independent = int(match.group(1))
                        other = int(match.group(2))
                        total = independent + other
                    
                    ratio = independent / total if total > 0 else 0
                    passes = ratio >= 0.333
                    
                    result = ExtractionResult(
                        section="S.41",
                        cg_code_requirement="At least one-third (33.3%) of board must be independent",
                        extracted_value={
                            "independent_count": independent,
                            "total_count": total,
                            "ratio": round(ratio, 3),
                            "ratio_percent": f"{ratio*100:.1f}%"
                        },
                        passes_compliance=passes,
                        evidence_quote=match.group(0).strip(),
                        page_number=find_page_for_text(pdf_path, match.group(0)),
                        confidence_score=base_confidence,
                        extraction_method=method
                    )
                    results.append(result)
                
                elif method in ["constituted_as_follows", "written_number_parenthetical"]:
                    # Handle patterns 7 and 8 - these typically find independent count only
                    independent = int(match.group(1))
                    
                    # Try to find total board size from context
                    # Look for other director categories in nearby text
                    context_start = max(0, match.start() - 200)
                    context_end = min(len(text), match.end() + 500)
                    context = text[context_start:context_end]
                    
                    # Count all director mentions with numbers - include ALL categories
                    all_director_counts = re.findall(r'\((\d+)\)\s+(?:independent\s+and\s+)?(?:non[-\s]?executive|executive|trading|listed|other)?\s*director', context, re.IGNORECASE)
                    
                    if len(all_director_counts) >= 1:
                        # We found categories - the first one should be our independent count
                        # Sum ALL counts including the first (independent)
                        total = sum(int(c) for c in all_director_counts)
                        
                        # Verify independent is included in the breakdown
                        if int(all_director_counts[0]) == independent:
                            # First count matches our independent - good
                            pass
                        else:
                            # Mismatch - use the regex-found count
                            independent = int(all_director_counts[0])
                        
                        ratio = independent / total if total > 0 else 0
                        passes = ratio >= 0.333
                        
                        result = ExtractionResult(
                            section="S.41",
                            cg_code_requirement="At least one-third (33.3%) of board must be independent",
                            extracted_value={
                                "independent_count": independent,
                                "total_count": total,
                                "ratio": round(ratio, 3),
                                "ratio_percent": f"{ratio*100:.1f}%",
                                "breakdown": all_director_counts
                            },
                            passes_compliance=passes,
                            evidence_quote=match.group(0).strip(),
                            page_number=find_page_for_text(pdf_path, match.group(0)),
                            confidence_score=base_confidence + 0.05,  # Boost for finding breakdown
                            extraction_method=method
                        )
                        results.append(result)
                    else:
                        # Just report the independent count
                        result = ExtractionResult(
                            section="S.41",
                            cg_code_requirement="At least one-third (33.3%) of board must be independent",
                            extracted_value={
                                "independent_count": independent,
                                "total_count": None,
                                "ratio": None,
                                "note": "Independent count found but total board size not determinable from this pattern"
                            },
                            passes_compliance=None,
                            evidence_quote=match.group(0).strip(),
                            page_number=find_page_for_text(pdf_path, match.group(0)),
                            confidence_score=base_confidence * 0.6,
                            extraction_method=method
                        )
                        results.append(result)
                        
                elif method == "count_only":
                    # Low confidence - just a count, no ratio
                    independent = int(match.group(1))
                    
                    result = ExtractionResult(
                        section="S.41",
                        cg_code_requirement="At least one-third (33.3%) of board must be independent",
                        extracted_value={
                            "independent_count": independent,
                            "total_count": None,
                            "ratio": None,
                            "note": "Count only - total board size not found in this pattern"
                        },
                        passes_compliance=None,  # Cannot determine without total
                        evidence_quote=match.group(0).strip(),
                        page_number=find_page_for_text(pdf_path, match.group(0)),
                        confidence_score=base_confidence * 0.5,  # Downgrade confidence
                        extraction_method=method
                    )
                    results.append(result)
                    
            except (ValueError, ZeroDivisionError) as e:
                continue
    
    # Deduplicate: keep highest confidence result per unique value
    if results:
        results = deduplicate_results(results, key_func=lambda r: str(r.extracted_value))
    
    return results


# ============================================================================
# SECTION 45: TENURE BREACH (>9 years requires justification)
# ============================================================================

def extract_section_45(text: str, pdf_path: str, current_year: int = None) -> List[ExtractionResult]:
    """
    CG Code S.45: Independent directors serving >9 years require shareholder approval.
    Level 2: Extract appointment years and calculate tenure.
    Level 3: Cite exact page and quote with calculated tenure.
    """
    if current_year is None:
        current_year = datetime.now().year
    
    results = []
    
    # Pattern 1: "appointed in YYYY" or "appointed on DD Month YYYY"
    pattern_appointment = r"(?:appointed|joined\s+the\s+board|became\s+a\s+director)\s+(?:in|on)\s+(\d{4}|\d{1,2}\s+\w+\s+\d{4})"
    
    # Pattern 2: "has served for X years" 
    pattern_tenure = r"(?:has\s+served|serving|tenure\s+of)\s+(?:for\s+)?(\d+)\s+years?"
    
    # Pattern 3: Table with name and year: "John Doe ... 2015"
    pattern_table = r"([A-Z][a-z]+\s+[A-Z][a-z]+).*?(\d{4})"
    
    # Find all appointments
    for match in re.finditer(pattern_appointment, text, re.IGNORECASE):
        try:
            year_str = match.group(1)
            
            # Parse year
            if len(year_str) == 4:
                appointment_year = int(year_str)
            else:
                # Try to parse full date
                parsed_date = date_parser.parse(year_str)
                appointment_year = parsed_date.year
            
            tenure = current_year - appointment_year
            requires_approval = tenure > 9
            
            if tenure >= 5:  # Only report if tenure is significant (5+ years)
                result = ExtractionResult(
                    section="S.45",
                    cg_code_requirement=f"Directors serving >9 years require shareholder approval (current year: {current_year})",
                    extracted_value={
                        "appointment_year": appointment_year,
                        "tenure_years": tenure,
                        "requires_shareholder_approval": requires_approval,
                        "director_name": extract_nearby_name(text, match.start())
                    },
                    passes_compliance=not requires_approval,  # True if no approval needed
                    evidence_quote=match.group(0).strip(),
                    page_number=find_page_for_text(pdf_path, match.group(0)),
                    confidence_score=0.85,
                    extraction_method="appointment_year_extraction"
                )
                results.append(result)
                
        except (ValueError, OverflowError):
            continue
    
    # Find explicit tenure mentions
    for match in re.finditer(pattern_tenure, text, re.IGNORECASE):
        try:
            tenure_years = int(match.group(1))
            requires_approval = tenure_years > 9
            
            result = ExtractionResult(
                section="S.45",
                cg_code_requirement=f"Directors serving >9 years require shareholder approval",
                extracted_value={
                    "tenure_years": tenure_years,
                    "requires_shareholder_approval": requires_approval,
                    "director_name": extract_nearby_name(text, match.start())
                },
                passes_compliance=not requires_approval,
                evidence_quote=match.group(0).strip(),
                page_number=find_page_for_text(pdf_path, match.group(0)),
                confidence_score=0.80,
                extraction_method="explicit_tenure_extraction"
            )
            results.append(result)
            
        except ValueError:
            continue
    
    # Deduplicate
    if results:
        results = deduplicate_results(results, key_func=lambda r: f"{r.extracted_value.get('tenure_years', 0)}-{r.extracted_value.get('director_name', 'unknown')}")
    
    return results


# ============================================================================
# SECTION 48: RELATED PARTY TRANSACTIONS (Tunneling Detection)
# ============================================================================

def extract_section_48(text: str, pdf_path: str) -> List[ExtractionResult]:
    """
    CG Code S.48: Related party transactions must be disclosed with values and approval.
    Level 2: Extract transaction values, counterparties, and approval status.
    Level 3: Cite exact note number, page, and quote.
    """
    results = []
    
    # Look for "Note XX" sections about related parties
    note_pattern = r"(?:note|note\s+no\.?|note\s+#?)\s*(\d+)[.:]?\s*(related\s+party|related\s+parties|rpt|rpts)"
    
    # Transaction patterns
    transaction_patterns = [
        # Pattern 1: "Company X: KES Y million"
        r"([A-Za-z\s&]+(?:limited|ltd|plc|corporation|company|holdings))?[:\s-]+\s*(kes?|ksh|shilling|sh)\s*([\d,\.]+)\s*(million|billion|thousand)?",
        
        # Pattern 2: "Transactions with [Related Party] amounted to KES..."
        r"transactions?\s+with\s+([A-Za-z\s&]+)\s+(?:amounted\s+to|were|totaled?)\s+(kes?|ksh|shilling|sh)\s*([\d,\.]+)\s*(million|billion|thousand)?",
        
        # Pattern 3: "Due from/to [Related Party]: KES..."
        r"(?:due\s+(?:from|to)|payable\s+to|receivable\s+from)\s+([A-Za-z\s&]+)[:\s]+(?:kes?|ksh|shilling|sh)\s*([\d,\.]+)\s*(million|billion|thousand)?",
        
        # Pattern 4: Board approval mention
        r"(?:approved\s+by\s+the\s+board|board\s+approval|shareholder\s+approval|rpt\s+committee\s+approval)",
    ]
    
    # Find the related party note section
    note_matches = list(re.finditer(note_pattern, text, re.IGNORECASE))
    
    if not note_matches:
        # Fallback: search entire text for related party transactions
        search_text = text
        note_number = "Unknown"
    else:
        # Focus on the first related party note
        note_match = note_matches[0]
        note_number = note_match.group(1)
        start_pos = note_match.start()
        # Get ~2000 chars after the note header
        search_text = text[start_pos:start_pos + 3000]
    
    # Extract transactions
    transactions_found = []
    
    for pattern in transaction_patterns[:3]:  # Skip approval pattern for now
        for match in re.finditer(pattern, search_text, re.IGNORECASE):
            try:
                groups = match.groups()
                
                # Parse amount
                amount_str = None
                unit = ""
                counterparty = None
                
                if len(groups) >= 3:
                    if groups[0] and len(groups[0]) > 2:  # Counterparty
                        counterparty = groups[0].strip()
                    # Amount is usually in groups[2] or groups[1] depending on pattern
                    for g in groups[1:]:
                        if g and re.match(r'[\d,\.]+', g.replace(',', '')):
                            amount_str = g
                            break
                    for g in groups[3:]:
                        if g:
                            unit = g.lower()
                
                if amount_str:
                    # Normalize amount
                    amount_num = float(amount_str.replace(',', ''))
                    if unit == 'million':
                        amount_num *= 1_000_000
                    elif unit == 'billion':
                        amount_num *= 1_000_000_000
                    elif unit == 'thousand':
                        amount_num *= 1_000
                    
                    transactions_found.append({
                        'counterparty': counterparty or 'Not specified',
                        'amount': amount_num,
                        'amount_formatted': f"KES {amount_num:,.0f}",
                        'unit': unit,
                        'quote': match.group(0).strip()
                    })
                    
            except (ValueError, AttributeError):
                continue
    
    # Check for board approval
    approval_found = False
    for match in re.finditer(transaction_patterns[3], search_text, re.IGNORECASE):
        approval_found = True
        break
    
    # Create result if transactions found
    if transactions_found:
        total_amount = sum(t['amount'] for t in transactions_found)
        
        result = ExtractionResult(
            section="S.48",
            cg_code_requirement="All related party transactions must disclose values and have board/shareholder approval",
            extracted_value={
                "note_number": note_number,
                "transaction_count": len(transactions_found),
                "total_amount": total_amount,
                "total_amount_formatted": f"KES {total_amount:,.0f}",
                "transactions": transactions_found,
                "board_approval_disclosed": approval_found
            },
            passes_compliance=approval_found and len(transactions_found) > 0,
            evidence_quote=f"Found {len(transactions_found)} transactions in Note {note_number}. " + 
                          f"Approval mentioned: {'Yes' if approval_found else 'No'}",
            page_number=find_page_for_text(pdf_path, search_text[:500]),
            confidence_score=0.88 if approval_found else 0.65,
            extraction_method="related_party_note_extraction"
        )
        results.append(result)
    else:
        # Explicitly report no transactions found (could be compliance issue)
        result = ExtractionResult(
            section="S.48",
            cg_code_requirement="All related party transactions must disclose values and have board/shareholder approval",
            extracted_value={
                "note_number": None,
                "transaction_count": 0,
                "transactions": [],
                "board_approval_disclosed": False
            },
            passes_compliance=None,  # Unknown - might genuinely have no RPTs
            evidence_quote="No related party transaction note or disclosures found",
            page_number=None,
            confidence_score=0.50,
            extraction_method="no_rpt_found"
        )
        results.append(result)
    
    return results


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def find_page_for_text(pdf_path: str, target_text: str, context_chars: int = 100) -> Optional[int]:
    """Find which page contains the target text."""
    try:
        doc = fitz.open(pdf_path)
        target_lower = target_text.lower()[:50]  # Use first 50 chars for matching
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").lower()
            
            # Check if target appears in this page
            if target_lower in text:
                doc.close()
                return page_num + 1  # 1-indexed
            
            # Fuzzy match: check for substantial overlap
            words_target = set(target_lower.split())
            for i in range(0, len(text) - len(target_lower), 200):
                window = text[i:i+len(target_lower)+context_chars]
                words_window = set(window.split())
                overlap = len(words_target & words_window) / max(len(words_target), 1)
                if overlap > 0.6:
                    doc.close()
                    return page_num + 1
        
        doc.close()
        return None
        
    except Exception as e:
        return None


def extract_nearby_name(text: str, position: int, window: int = 100) -> Optional[str]:
    """Extract a person's name near the given position."""
    # Look backwards up to 100 chars
    start = max(0, position - window)
    snippet = text[start:position + 20]
    
    # Pattern for capitalized names
    name_pattern = r'([A-Z][a-z]+\s+[A-Z][a-z]+)'
    matches = list(re.finditer(name_pattern, snippet))
    
    if matches:
        # Return the last name found before the position
        return matches[-1].group(1)
    
    return None


def deduplicate_results(results: List[ExtractionResult], key_func) -> List[ExtractionResult]:
    """Keep only the highest-confidence result for each unique key."""
    seen = {}
    
    for result in results:
        key = key_func(result)
        if key not in seen or result.confidence_score > seen[key].confidence_score:
            seen[key] = result
    
    return list(seen.values())


def run_full_audit(pdf_path: str) -> Dict:
    """Run complete governance audit on a single PDF."""
    # Extract text
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text")
    doc.close()
    
    # Run all extractors
    s41_results = extract_section_41(full_text, pdf_path)
    s45_results = extract_section_45(full_text, pdf_path)
    s48_results = extract_section_48(full_text, pdf_path)
    
    # Compile report
    report = {
        "pdf_path": pdf_path,
        "extraction_timestamp": datetime.now().isoformat(),
        "sections": {
            "S.41": {
                "results": [vars(r) for r in s41_results],
                "compliant": any(r.passes_compliance for r in s41_results) if s41_results else None,
                "highest_confidence": max((r.confidence_score for r in s41_results), default=0)
            },
            "S.45": {
                "results": [vars(r) for r in s45_results],
                "compliant": all(r.passes_compliance for r in s45_results) if s45_results else None,
                "breaches_found": sum(1 for r in s45_results if r.extracted_value.get('requires_shareholder_approval'))
            },
            "S.48": {
                "results": [vars(r) for r in s48_results],
                "compliant": all(r.passes_compliance for r in s48_results) if s48_results else None,
                "total_rpt_amount": s48_results[0].extracted_value.get('total_amount_formatted') if s48_results else None
            }
        }
    }
    
    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python advanced_extractor.py <pdf_path>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    if not Path(pdf_file).exists():
        print(f"ERROR: File not found: {pdf_file}")
        sys.exit(1)
    
    print(f"Running advanced governance audit on: {pdf_file}")
    print("=" * 80)
    
    report = run_full_audit(pdf_file)
    
    # Print summary
    print("\n=== SECTION 41: BOARD INDEPENDENCE ===")
    for r in report["sections"]["S.41"]["results"]:
        print(f"  Confidence: {r['confidence_score']:.2f}")
        print(f"  Evidence: {r['evidence_quote'][:100]}...")
        print(f"  Value: {r['extracted_value']}")
        print(f"  Compliant: {r['passes_compliance']}")
        print(f"  Page: {r['page_number']}")
        print()
    
    print("\n=== SECTION 45: TENURE BREACHES ===")
    for r in report["sections"]["S.45"]["results"]:
        print(f"  Tenure: {r['extracted_value'].get('tenure_years', 'N/A')} years")
        print(f"  Requires Approval: {r['extracted_value'].get('requires_shareholder_approval')}")
        print(f"  Evidence: {r['evidence_quote'][:100]}...")
        print(f"  Page: {r['page_number']}")
        print()
    
    print("\n=== SECTION 48: RELATED PARTY TRANSACTIONS ===")
    for r in report["sections"]["S.48"]["results"]:
        print(f"  Transactions Found: {r['extracted_value'].get('transaction_count', 0)}")
        print(f"  Total Amount: {r['extracted_value'].get('total_amount_formatted', 'N/A')}")
        print(f"  Board Approval: {r['extracted_value'].get('board_approval_disclosed')}")
        print(f"  Compliant: {r['passes_compliance']}")
        print(f"  Page: {r['page_number']}")
        print()
    
    print("\n=== AUDIT COMPLETE ===")
