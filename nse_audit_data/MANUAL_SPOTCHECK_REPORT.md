# MANUAL SPOT-CHECK REPORT: Governance Extraction Validation

**Date:** 2026-03-21  
**Reviewer:** Automated Pipeline + Manual Verification Required  
**Corpus:** 2 highest-scoring NSE annual reports (from validated set of 8)

---

## Executive Summary

This report presents findings from automated text extraction for **Section 41 (Director Independence)** and **Section 48 (Board Evaluation)** of the NSE Corporate Governance Code. 

**CRITICAL:** These findings MUST be manually verified against the actual PDF documents before any compliance conclusions can be drawn.

---

## Files Subject to Spot-Check

### File 1: NSE-2021-ANNUAL-REPORT-AND-FINANCIAL-STATEMENTS-1.pdf.pdf
**Extracted Text File:** `nse_audit_data/processed_text/NSE-2021-ANNUAL-REPORT-AND-FINANCIAL-STATEMENTS-1.txt.txt`  
**Text Length:** 332,181 characters  
**Estimated Pages:** ~158 (based on table of contents)

### File 2: NSE-Annual-Report-2022-Integrated-Report.pdf.pdf
**Extracted Text File:** `nse_audit_data/processed_text/NSE-Annual-Report-2022-Integrated-Report.txt.txt`  
**Text Length:** 346,853 characters  
**Estimated Pages:** ~146 (based on table of contents)

---

## Section 41: Director Independence

### What Section 41 Requires (NSE CG Code)
Section 41 of the NSE Corporate Governance Code requires boards to:
- Establish and disclose **criteria for determining director independence**
- Assess each independent director against these criteria
- Disclose the results of the independence assessment

### Automated Extraction Findings

#### File 1 (NSE 2021 Annual Report)

**Finding 1:** Board Composition Table
- **Location:** Line ~2134, Estimated Page ~48
- **Extracted Text:**
```
Below is the current composition of the Board:
Mr. Kiprono Kittony
Board Chairman/ Independent Non-Executive Director
...
Ms. Isis Madison
Independent Non-Executive Director
```

**Finding 2:** Governance Fact Sheet
- **Location:** Line ~2606, Estimated Page ~58
- **Extracted Text:**
```
Nairobi Securities Exchange Corporate Governance Fact Sheet
Number of Board Members: 9
Number of Independent Non-Executive Directors: 3
...
Separate Chairman and CEO: Yes
Independent Audit Committee: Yes
```

**VERDICT FOR FILE 1 - S.41:** ⚠️ **PARTIAL COMPLIANCE**
- ✓ Discloses number of independent directors
- ✓ Lists which directors are independent
- ❌ Does NOT appear to disclose the **criteria** used to determine independence
- ❌ Does NOT show individual assessments against criteria

**What to verify in PDF:**
- Open PDF at page ~48 and ~58
- Check if there is a section titled "Director Independence Criteria" or similar
- Look for language like: "The Board considers a director independent if..." followed by specific criteria
- If only titles are listed without criteria → **S.41 NON-COMPLIANT**

---

#### File 2 (NSE 2022 Annual Report)

**Finding 1:** Director Profiles
- **Location:** Line ~1146, Estimated Page ~26
- **Extracted Text:**
```
Directors Profiles
Mr. Kiprono Kittony, EBS
Independent Non-Executive Director
Mr. Kiprono Kittony is the Chairman of the Nairobi Securities Exchange...
```

**Finding 2:** Governance Fact Sheet
- **Location:** Line ~3232, Estimated Page ~72
- **Extracted Text:**
```
NAIROBI SECURITIES EXCHANGE CORPORATE GOVERNANCE FACT SHEET
Number of Board Members: 10
Number of Independent Non-Executive Directors: 5
...
Separate Chairman and CEO: YES
Independent Audit Committee: YES
```

**VERDICT FOR FILE 2 - S.41:** ⚠️ **PARTIAL COMPLIANCE**
- ✓ Discloses number of independent directors (increased from 3 to 5)
- ✓ Provides detailed profiles of independent directors
- ❌ Does NOT appear to disclose the **criteria** used to determine independence
- ❌ Does NOT show individual assessments against criteria

**What to verify in PDF:**
- Open PDF at pages ~26 and ~72
- Search for "independence criteria", "determination of independence", or "assessment of independence"
- If only biographical information is present without explicit criteria → **S.41 NON-COMPLIANT**

---

## Section 48: Board Evaluation

### What Section 48 Requires (NSE CG Code)
Section 48 of the NSE Corporate Governance Code requires:
- **Annual evaluation** of the board, its committees, and individual directors
- Disclosure of the **process** used for evaluation
- Disclosure of **results** or summary of findings
- Use of external facilitator at least every 3 years

### Automated Extraction Findings

#### File 1 (NSE 2021 Annual Report)

**Finding:** Board Charter Reference
- **Location:** Line ~2862, Estimated Page ~64
- **Extracted Text:**
```
...the nomination of directors, training and evaluation of directors and members of Board committees.
Whilst the Board Charter includes references to minimum acceptable standards of conduct, the Board
embraces global best practices in this regard.
```

**VERDICT FOR FILE 1 - S.48:** ⚠️ **INSUFFICIENT DISCLOSURE**
- ✓ Mentions "evaluation of directors" exists in Board Charter
- ❌ Does NOT describe the evaluation **process**
- ❌ Does NOT disclose **when** evaluations were conducted
- ❌ Does NOT summarize **results** of evaluations
- ❌ Does NOT mention use of external facilitator

**What to verify in PDF:**
- Open PDF at page ~64
- Search for "board evaluation", "performance review", "effectiveness review"
- Look for: "The Board conducted an annual evaluation in 2021 using [method]..." 
- If only passing mention without process/results → **S.48 NON-COMPLIANT**

---

#### File 2 (NSE 2022 Annual Report)

**Finding:** Board Charter Reference (identical language)
- **Location:** Line ~1400, Estimated Page ~32
- **Extracted Text:**
```
...the nomination of directors, training and evaluation of directors and members of Board committees.
Whilst the Board Charter includes references to minimum acceptable standards of conduct, the
Board embraces global best practices in this regard.
```

**VERDICT FOR FILE 2 - S.48:** ⚠️ **INSUFFICIENT DISCLOSURE**
- ✓ Mentions "evaluation of directors" exists in Board Charter
- ❌ Does NOT describe the evaluation **process**
- ❌ Does NOT disclose **when** evaluations were conducted
- ❌ Does NOT summarize **results** of evaluations
- ❌ Does NOT mention use of external facilitator

**What to verify in PDF:**
- Open PDF at page ~32
- Search entire document for "evaluation", "performance review", "effectiveness"
- If no dedicated section on board evaluation → **S.48 NON-COMPLIANT**

---

## Manual Verification Checklist

**FOR EACH PDF ABOVE, COMPLETE THE FOLLOWING:**

### Section 41 Verification
- [ ] Open PDF in viewer (Adobe Acrobat, Preview, etc.)
- [ ] Navigate to estimated page numbers listed above
- [ ] Search PDF text for: "independence criteria", "determination of independence"
- [ ] **Question:** Does the document list specific criteria (e.g., "not employed by company in last 3 years", "no material business relationship")?
  - [ ] YES → Extractor found real data → **S.41 COMPLIANT**
  - [ ] NO → Extractor only found headers/titles → **S.41 NON-COMPLIANT**
- [ ] Record actual page number where criteria (or lack thereof) appears: _______

### Section 48 Verification
- [ ] Open PDF in viewer
- [ ] Navigate to estimated page numbers listed above
- [ ] Search PDF text for: "board evaluation", "performance evaluation", "effectiveness review"
- [ ] **Question:** Does the document describe the evaluation PROCESS (who, when, how)?
  - [ ] YES → Extractor found real data → **S.48 COMPLIANT**
  - [ ] NO → Extractor only found passing mention → **S.48 NON-COMPLIANT**
- [ ] **Question:** Does the document disclose RESULTS of the evaluation?
  - [ ] YES → Note key findings: _______________________
  - [ ] NO → **S.48 PARTIALLY NON-COMPLIANT**
- [ ] Record actual page number where evaluation details (or lack thereof) appears: _______

---

## Summary of Preliminary Findings (Pre-Verification)

| Company | Year | S.41 Status | S.48 Status | Overall |
|---------|------|-------------|-------------|---------|
| NSE PLC | 2021 | ⚠️ Partial (titles only, no criteria) | ⚠️ Insufficient (mention only, no process) | **Non-Compliant** |
| NSE PLC | 2022 | ⚠️ Partial (titles only, no criteria) | ⚠️ Insufficient (mention only, no process) | **Non-Compliant** |

**IF VERIFIED:** This would represent a **material governance gap** for NSE PLC itself—the market operator failing to comply with its own governance code.

---

## Next Steps

1. **IMMEDIATE:** Complete manual verification checklist above
2. **IF NON-COMPLIANCE CONFIRMED:**
   - Document exact page numbers and quotes (or absence thereof)
   - Prepare compliance gap report for ICPSK presentation
   - Consider whether this is a "comply or explain" situation or outright non-compliance
3. **PIPELINE IMPROVEMENT:**
   - Add page-level citation tracking to extractor
   - Enhance S.41 detection to distinguish between "listing titles" vs "disclosing criteria"
   - Enhance S.48 detection to require process description, not just keyword mention

---

## Critical Caveats

⚠️ **DO NOT PUBLISH OR PRESENT THESE FINDINGS UNTIL:**
- Manual verification is complete
- Actual PDF pages are reviewed
- Exact citations (page + paragraph) are recorded
- Context is confirmed (no column artifacts, OCR errors, or mis-extractions)

**This report is a WORKING DOCUMENT for validation purposes only.**

---

**Generated by:** NSE Governance Audit Pipeline v1.0  
**Timestamp:** 2026-03-21 11:00:00 EAT
